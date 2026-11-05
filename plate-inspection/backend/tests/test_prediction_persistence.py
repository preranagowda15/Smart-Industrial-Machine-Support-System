import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.inspections.models import Inspection


@pytest.mark.django_db
def test_valid_upload_persists_prediction_and_model_version():
    """
    Test 2: Valid sample image returns a prediction with all four fields
    (predicted_class, confidence, defect_probability, model_version) and persists model_version.
    """
    user = User.objects.create_user(username='test_op_pred', password='password123', role=User.Role.OPERATOR)
    client = APIClient()
    client.force_authenticate(user=user)

    sample_path = 'Samples/images/inspection_001.png'
    assert os.path.exists(sample_path), f"Sample image missing: {sample_path}"

    with open(sample_path, 'rb') as f:
        upload = SimpleUploadedFile(name='inspection_001.png', content=f.read(), content_type='image/png')

    response = client.post('/api/inspections/', {'image': upload}, format='multipart')

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.data}"
    data = response.data

    # Check all four fields returned
    assert 'predicted_class' in data and data['predicted_class'] in (0, 1)
    assert 'confidence' in data and 0.0 <= data['confidence'] <= 1.0
    assert 'defect_probability' in data and 0.0 <= data['defect_probability'] <= 1.0
    assert data['model_version'] == 'BIT-PLATE-CV-1.0'

    # Check database persistence
    inspection = Inspection.objects.get(id=data['id'])
    assert inspection.status == Inspection.Status.COMPLETED
    assert inspection.model_version == 'BIT-PLATE-CV-1.0'
    assert inspection.predicted_class == data['predicted_class']
    assert abs(inspection.confidence - data['confidence']) < 1e-4
    assert abs(inspection.defect_probability - data['defect_probability']) < 1e-4

