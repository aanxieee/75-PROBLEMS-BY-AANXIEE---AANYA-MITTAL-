"""
Image Loader
Handles extracting images from uploaded zip files and loading them as PIL Images.
"""

import zipfile
import io
from PIL import Image
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def load_images_from_zip(zip_bytes: bytes) -> dict:
    """
    Extract images from a zip file's bytes.

    Args:
        zip_bytes: Raw bytes of the uploaded zip file.

    Returns:
        dict of {filename: PIL.Image}
    """
    images = {}

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for entry in zf.namelist():
            # Skip directories, hidden files, macOS resource forks
            if entry.endswith("/") or "/__MACOSX" in entry or entry.startswith("__MACOSX"):
                continue

            ext = Path(entry).suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            try:
                with zf.open(entry) as f:
                    img = Image.open(io.BytesIO(f.read()))
                    img = img.convert("RGB")  # Normalize to RGB
                    # Use just the filename, not full path inside zip
                    clean_name = Path(entry).name
                    # Handle duplicate filenames inside zip
                    if clean_name in images:
                        clean_name = f"{Path(entry).stem}_{hash(entry) % 10000}{ext}"
                    images[clean_name] = img
            except Exception:
                # Skip corrupted/unreadable images
                continue

    return images


def get_image_info(images: dict) -> list:
    """
    Get basic info for all loaded images.

    Returns:
        list of dicts with filename, width, height, mode, size_kb
    """
    info = []
    for filename, img in images.items():
        # Estimate size in KB from pixel data
        estimated_kb = (img.width * img.height * 3) / 1024
        info.append({
            "filename": filename,
            "width": img.width,
            "height": img.height,
            "resolution": f"{img.width}x{img.height}",
            "estimated_kb": round(estimated_kb, 1),
        })
    return info
