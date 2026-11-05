import pytest
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.inspections.models import Inspection


@pytest.mark.django_db
def test_role_permissions_and_operator_isolation():
    """
    Test 4:
    - Operator cannot read other operators' inspections (403/404)
    - Operator cannot review (403)
    - Unauthenticated -> 401
    """
    op1 = User.objects.create_user(username='op_perm_1', password='pass', role=User.Role.OPERATOR)
    op2 = User.objects.create_user(username='op_perm_2', password='pass', role=User.Role.OPERATOR)
    sup = User.objects.create_user(username='sup_perm', password='pass', role=User.Role.SUPERVISOR)

    # Create inspection for Operator 1
    insp1 = Inspection.objects.create(
        user=op1,
        image='uploads/test1.png',
        predicted_class=0,
        confidence=0.98,
        defect_probability=0.02,
        model_version='BIT-PLATE-CV-1.0',
        status=Inspection.Status.COMPLETED
    )

    unauth_client = APIClient()
    op1_client = APIClient()
    op1_client.force_authenticate(user=op1)

    op2_client = APIClient()
    op2_client.force_authenticate(user=op2)

    sup_client = APIClient()
    sup_client.force_authenticate(user=sup)

    # 1. Unauthenticated -> 401
    res = unauth_client.get(f'/api/inspections/{insp1.id}/')
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"

    res = unauth_client.post(f'/api/inspections/{insp1.id}/reviews/', {'decision': 'CONFIRMED'}, format='json')
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"

    # 2. Operator 1 can view own inspection -> 200
    res = op1_client.get(f'/api/inspections/{insp1.id}/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    # 3. Operator 2 cannot read Operator 1's inspection -> 403
    res = op2_client.get(f'/api/inspections/{insp1.id}/')
    assert res.status_code in (403, 404), f"Expected 403 or 404, got {res.status_code}"

    # 4. Operator 2 list should not contain Operator 1's inspection
    res = op2_client.get('/api/inspections/')
    assert res.status_code == 200
    ids = [item['id'] for item in res.data]
    assert insp1.id not in ids, "Operator 2 saw Operator 1's inspection in list"

    # 5. Operator 1 attempting to review -> 403
    res = op1_client.post(f'/api/inspections/{insp1.id}/reviews/', {'decision': 'CONFIRMED'}, format='json')
    assert res.status_code == 403, f"Expected 403 for operator review attempt, got {res.status_code}"

    # 6. Supervisor can view Operator 1's inspection and review -> 200 / 201
    res = sup_client.get(f'/api/inspections/{insp1.id}/')
    assert res.status_code == 200

    res = sup_client.post(f'/api/inspections/{insp1.id}/reviews/', {'decision': 'CONFIRMED', 'comment': 'Supervisor approved'}, format='json')
    assert res.status_code == 201

