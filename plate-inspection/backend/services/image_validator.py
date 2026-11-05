"""
backend/services/image_validator.py - Image validation prior to inference.
Enforces Section 6.1:
1. Extension / content type must be PNG or JPEG (UNSUPPORTED_TYPE)
2. File content check via Pillow (NOT_AN_IMAGE)
3. Full pixel decode with im.load() (CORRUPT_IMAGE)
4. Dimensions >= MIN_IMAGE_DIM (TOO_SMALL)
5. File size <= MAX_IMAGE_SIZE_MB (TOO_LARGE)
"""

import os
from io import BytesIO
from django.conf import settings
from PIL import Image, UnidentifiedImageError


class ImageValidationError(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


def validate_image_file(file_input, filename=None):
    """
    Validates an image file before model inference.
    
    Args:
        file_input: File path (str/Path), file-like object, or UploadedFile.
        filename (str, optional): File name if file_input is a stream.
    
    Returns:
        dict: {'is_valid': True, 'width': int, 'height': int, 'format': str}
        
    Raises:
        ImageValidationError with machine-readable error_code:
        - UNSUPPORTED_TYPE
        - NOT_AN_IMAGE
        - CORRUPT_IMAGE
        - TOO_SMALL
        - TOO_LARGE
    """
    min_dim = getattr(settings, 'MIN_IMAGE_DIM', 64)
    max_mb = getattr(settings, 'MAX_IMAGE_SIZE_MB', 10)
    max_bytes = max_mb * 1024 * 1024
    allowed_extensions = {'.png', '.jpg', '.jpeg'}
    allowed_formats = {'PNG', 'JPEG'}

    # 1. Determine filename and extension
    name = filename
    if not name:
        if isinstance(file_input, (str, os.PathLike)):
            name = str(file_input)
        elif hasattr(file_input, 'name'):
            name = file_input.name
        else:
            name = 'unknown.png'

    _, ext = os.path.splitext(name.lower())
    if ext not in allowed_extensions:
        raise ImageValidationError(
            error_code='UNSUPPORTED_TYPE',
            message=f"Unsupported file extension '{ext}'. Only PNG and JPEG images are allowed."
        )

    # 2. Check file size
    size = None
    if isinstance(file_input, (str, os.PathLike)):
        size = os.path.getsize(file_input)
    elif hasattr(file_input, 'size'):
        size = file_input.size
    elif hasattr(file_input, 'seek') and hasattr(file_input, 'tell'):
        pos = file_input.tell()
        file_input.seek(0, os.SEEK_END)
        size = file_input.tell()
        file_input.seek(pos)

    if size is not None and size > max_bytes:
        raise ImageValidationError(
            error_code='TOO_LARGE',
            message=f"File size exceeds maximum limit of {max_mb} MB."
        )

    # 3. Read image content
    try:
        if isinstance(file_input, (str, os.PathLike)):
            with open(file_input, 'rb') as f:
                content = f.read()
        elif hasattr(file_input, 'read'):
            if hasattr(file_input, 'seek'):
                file_input.seek(0)
            content = file_input.read()
            if hasattr(file_input, 'seek'):
                file_input.seek(0)
        else:
            content = file_input

        if not content:
            raise ImageValidationError(
                error_code='NOT_AN_IMAGE',
                message="Uploaded file is empty."
            )
    except ImageValidationError:
        raise
    except Exception as e:
        raise ImageValidationError(
            error_code='NOT_AN_IMAGE',
            message=f"Could not read uploaded file: {str(e)}"
        )

    # 4. Content check using Pillow (must catch not_an_image.jpg)
    try:
        buffer = BytesIO(content)
        img = Image.open(buffer)
    except (UnidentifiedImageError, ValueError, TypeError) as e:
        raise ImageValidationError(
            error_code='NOT_AN_IMAGE',
            message="File content is not a valid image format."
        )
    except Exception as e:
        raise ImageValidationError(
            error_code='NOT_AN_IMAGE',
            message=f"Image identification failed: {str(e)}"
        )

    # Format verification
    if img.format not in allowed_formats:
        raise ImageValidationError(
            error_code='UNSUPPORTED_TYPE',
            message=f"Detected image format '{img.format}' is not supported. Only PNG and JPEG are accepted."
        )

    # 5. Full decode check (im.load() catches truncated/corrupt PNG/JPG)
    try:
        img.load()
    except Exception as e:
        raise ImageValidationError(
            error_code='CORRUPT_IMAGE',
            message=f"Image file is corrupt or truncated: {str(e)}"
        )

    # 6. Dimension check (must catch too_small.png)
    width, height = img.size
    if width < min_dim or height < min_dim:
        raise ImageValidationError(
            error_code='TOO_SMALL',
            message=f"Image dimensions ({width}x{height}) are smaller than required minimum ({min_dim}x{min_dim})."
        )

    return {
        'is_valid': True,
        'width': width,
        'height': height,
        'format': img.format,
    }

