import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.inspections.models import Inspection


@pytest.mark.django_db
def test_end_to_end_workflow():
    """
    Test 8: End-to-end: login -> upload -> result -> supervisor review -> evaluation page
    """
    # Create Operator and Supervisor
    op = User.objects.create_user(username='e2e_operator', password='OperatorPassword123!', role=User.Role.OPERATOR)
    sup = User.objects.create_user(username='e2e_supervisor', password='SupervisorPassword123!', role=User.Role.SUPERVISOR)

    client = APIClient()

    # Step 1: Login as Operator
    res = client.post('/api/auth/login/', {'username': 'e2e_operator', 'password': 'OperatorPassword123!'}, format='json')
    assert res.status_code == 200
    op_tokens = res.data
    assert 'access' in op_tokens
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {op_tokens['access']}")

    # Step 2: Upload plate image
    sample_path = 'Samples/images/inspection_035.png'
    with open(sample_path, 'rb') as f:
        upload = SimpleUploadedFile(name='inspection_035.png', content=f.read(), content_type='image/png')

    res = client.post('/api/inspections/', {'image': upload}, format='multipart')
    assert res.status_code == 201
    inspection_data = res.data
    insp_id = inspection_data['id']

    # Step 3: Check Result
    assert inspection_data['predicted_class'] == 1  # Defective
    assert inspection_data['predicted_label'] == 'Defective'
    assert inspection_data['confidence'] > 0.5
    assert inspection_data['defect_probability'] > 0.5
    assert inspection_data['model_version'] == 'BIT-PLATE-CV-1.0'
    assert 'limitations_notice' in inspection_data

    # Step 4: Login as Supervisor
    client.credentials()  # Clear operator auth
    res = client.post('/api/auth/login/', {'username': 'e2e_supervisor', 'password': 'SupervisorPassword123!'}, format='json')
    assert res.status_code == 200
    sup_tokens = res.data
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {sup_tokens['access']}")

    # Step 5: Supervisor Reviews Inspection
    res = client.post(f'/api/inspections/{insp_id}/reviews/', {
        'decision': 'CONFIRMED',
        'comment': 'Defect confirmed: surface pit detected.'
    }, format='json')
    assert res.status_code == 201
    review_data = res.data
    assert review_data['decision'] == 'CONFIRMED'
    assert review_data['reviewer_username'] == 'e2e_supervisor'

    # Verify inspection detail has review appended
    res = client.get(f'/api/inspections/{insp_id}/')
    assert res.status_code == 200
    assert len(res.data['reviews']) == 1
    assert res.data['reviews'][0]['decision'] == 'CONFIRMED'

    # Step 6: Supervisor accesses Evaluation Page & runs evaluation
    res = client.get('/api/evaluation/')
    assert res.status_code == 200
    eval_data = res.data
    assert eval_data['total_samples'] == 60
    assert eval_data['tp'] == 30
    assert eval_data['tn'] == 30
    assert eval_data['defect_recall'] == 1.0

    # Trigger fresh evaluation
    res = client.post('/api/evaluation/run/')
    assert res.status_code == 201
    fresh_eval = res.data
    assert fresh_eval['total_samples'] == 60
    assert fresh_eval['defect_recall'] == 1.0

