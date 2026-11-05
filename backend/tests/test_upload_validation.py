import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.inspections.models import Inspection


@pytest.mark.django_db
def test_upload_rejects_invalid_images_with_error_codes():
    """
    Test 1: Upload rejects not_an_image.jpg, corrupt_image.png, too_small.png
    with correct error codes and creates no completed inspection.
    """
    user = User.objects.create_user(username='test_op_val', password='password123', role=User.Role.OPERATOR)
    client = APIClient()
    client.force_authenticate(user=user)

    cases = [
        ('Validation/not_an_image.jpg', 'NOT_AN_IMAGE'),
        ('Validation/corrupt_image.png', 'CORRUPT_IMAGE'),
        ('Validation/too_small.png', 'TOO_SMALL'),
    ]

    for filepath, expected_code in cases:
        assert os.path.exists(filepath), f"Validation fixture missing: {filepath}"
        with open(filepath, 'rb') as f:
            content = f.read()

        upload = SimpleUploadedFile(
            name=os.path.basename(filepath),
            content=content,
            content_type='image/png' if filepath.endswith('.png') else 'image/jpeg'
        )

        response = client.post('/api/inspections/', {'image': upload}, format='multipart')

        assert response.status_code == 400, f"Expected 400 for {filepath}, got {response.status_code}"
        assert response.data.get('error_code') == expected_code, (
            f"Expected error code '{expected_code}', got '{response.data.get('error_code')}' for {filepath}"
        )

    # Verify no completed inspections were created
    completed_count = Inspection.objects.filter(status=Inspection.Status.COMPLETED).count()
    assert completed_count == 0, f"Expected 0 completed inspections, found {completed_count}"

