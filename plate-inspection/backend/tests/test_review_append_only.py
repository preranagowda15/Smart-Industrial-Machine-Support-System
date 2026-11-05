import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.inspections.models import Inspection
from apps.reviews.models import Review


@pytest.mark.django_db
def test_review_is_append_only_and_prediction_immutable():
    """
    Test 5:
    - Review is append-only
    - Original prediction unchanged after reviews and after retry
    - Reviews cannot be updated or deleted
    """
    op = User.objects.create_user(username='op_app_test', password='pass', role=User.Role.OPERATOR)
    sup1 = User.objects.create_user(username='sup_app_1', password='pass', role=User.Role.SUPERVISOR)
    sup2 = User.objects.create_user(username='sup_app_2', password='pass', role=User.Role.SUPERVISOR)

    insp = Inspection.objects.create(
        user=op,
        image='uploads/sample_test.png',
        predicted_class=0,
        confidence=0.965,
        defect_probability=0.035,
        model_version='BIT-PLATE-CV-1.0',
        status=Inspection.Status.COMPLETED
    )

    client1 = APIClient()
    client1.force_authenticate(user=sup1)

    client2 = APIClient()
    client2.force_authenticate(user=sup2)

    # 1. First supervisor review: CONFIRMED
    res1 = client1.post(f'/api/inspections/{insp.id}/reviews/', {
        'decision': 'CONFIRMED',
        'comment': 'Initial check: Normal'
    }, format='json')
    assert res1.status_code == 201

    # 2. Second supervisor review: OVERRIDDEN
    res2 = client2.post(f'/api/inspections/{insp.id}/reviews/', {
        'decision': 'OVERRIDDEN',
        'comment': 'Discovered hairline crack: Marked Defective'
    }, format='json')
    assert res2.status_code == 201

    # 3. Verify reviews table has 2 records (append-only)
    reviews = Review.objects.filter(inspection=insp).order_by('created_at')
    assert reviews.count() == 2
    assert reviews[0].decision == 'CONFIRMED'
    assert reviews[1].decision == 'OVERRIDDEN'

    # 4. Verify original inspection prediction is completely UNCHANGED
    insp.refresh_from_db()
    assert insp.predicted_class == 0
    assert abs(insp.confidence - 0.965) < 1e-4
    assert abs(insp.defect_probability - 0.035) < 1e-4
    assert insp.model_version == 'BIT-PLATE-CV-1.0'

    # 5. Verify direct edit to inspection is blocked by immutability constraint
    insp.predicted_class = 1
    try:
        insp.save()
        pytest.fail("Expected ValidationError on modifying completed inspection prediction")
    except ValidationError:
        pass

    # 6. Verify review cannot be deleted or modified
    first_review = reviews.first()
    try:
        first_review.delete()
        pytest.fail("Expected ValidationError on attempting to delete review")
    except ValidationError:
        pass

    first_review.comment = "Modified comment"
    try:
        first_review.save()
        pytest.fail("Expected ValidationError on attempting to modify review")
    except ValidationError:
        pass

    # 7. Retry creates a NEW inspection attempt linked to original; original unchanged
    retry_insp = Inspection.objects.create(
        user=op,
        image='uploads/sample_retry.png',
        predicted_class=1,
        confidence=0.88,
        defect_probability=0.88,
        model_version='BIT-PLATE-CV-1.0',
        status=Inspection.Status.COMPLETED,
        parent_inspection=insp
    )

    # Original inspection remains intact with original reviews
    insp.refresh_from_db()
    assert insp.predicted_class == 0
    assert insp.reviews.count() == 2
    assert retry_insp.parent_inspection.id == insp.id

