"""
Image validation service for AI visual quality inspection.
Enforces:
1. File size <= 5 MiB
2. Decoded image format: JPEG or PNG only
3. Dimensions: 64x64 to 4096x4096 inclusive
4. Actual file integrity (not truncated or corrupt)
"""
import io
from typing import Tuple, Dict, Any
from PIL import Image

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MiB
MIN_DIMENSION = 64
MAX_DIMENSION = 4096
ALLOWED_FORMATS = {"JPEG", "PNG"}

class ImageValidationError(Exception):
    pass

class ImageValidator:
    @staticmethod
    def validate_file(file_obj, filename: str = "") -> Dict[str, Any]:
        """
        Validates uploaded file content, size, format, and dimensions.
        Returns a dict with dimensions and format if valid, or raises ImageValidationError.
        """
        # 1. Size check
        if hasattr(file_obj, "size"):
            size = file_obj.size
        elif hasattr(file_obj, "getbuffer"):
            size = file_obj.getbuffer().nbytes
        elif hasattr(file_obj, "seek") and hasattr(file_obj, "tell"):
            file_obj.seek(0, io.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(0)
        else:
            size = len(file_obj.read())
            file_obj.seek(0)

        if size <= 0:
            raise ImageValidationError("File is empty (0 bytes).")

        if size > MAX_FILE_SIZE_BYTES:
            size_mb = size / (1024 * 1024)
            raise ImageValidationError(f"File size ({size_mb:.2f} MiB) exceeds the 5 MiB limit.")

        # 2. Open and verify image content
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            img = Image.open(file_obj)
            fmt = img.format
            width, height = img.size

            # Verify integrity
            img.verify()
        except Exception as e:
            raise ImageValidationError(f"Invalid or corrupted image file: {str(e)}")

        # 3. Format check
        if fmt not in ALLOWED_FORMATS:
            raise ImageValidationError(
                f"Unsupported image format '{fmt}'. Only decoded JPEG and PNG images are accepted."
            )

        # 4. Dimensions check
        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height}) are smaller than the minimum allowable size of {MIN_DIMENSION}x{MIN_DIMENSION} pixels."
            )

        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height}) exceed the maximum allowable limit of {MAX_DIMENSION}x{MAX_DIMENSION} pixels."
            )

        # Rewind pointer for subsequent read/save
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        return {
            "format": fmt,
            "width": width,
            "height": height,
            "size_bytes": size,
        }

