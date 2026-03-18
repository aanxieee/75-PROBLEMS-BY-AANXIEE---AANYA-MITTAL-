"""
Screenshot Detector
Identifies screenshots based on aspect ratio and common device resolutions.
"""

from PIL import Image

# Common screenshot resolutions (width x height) for popular devices
COMMON_SCREENSHOT_SIZES = {
    # iPhones
    (1170, 2532), (1284, 2778), (1125, 2436), (1242, 2688),
    (750, 1334), (1080, 1920), (1242, 2208), (828, 1792),
    (1179, 2556), (1290, 2796),
    # Android common
    (1080, 2400), (1080, 2340), (1440, 3200), (1440, 3120),
    (1440, 2960), (1080, 2160), (720, 1280), (1080, 1920),
    # iPads
    (2048, 2732), (1668, 2388), (1620, 2160), (2048, 2732),
    # Desktop common
    (1920, 1080), (2560, 1440), (1366, 768), (1440, 900),
    (3840, 2160), (2560, 1600), (1536, 864),
}

# Typical screenshot aspect ratios (as width/height)
SCREENSHOT_RATIOS = {
    9 / 19.5,   # Modern phones
    9 / 20,     # Newer phones
    9 / 16,     # Standard phones / desktop
    3 / 4,      # Tablets
    10 / 16,    # Some tablets
    16 / 9,     # Landscape desktop
}

RATIO_TOLERANCE = 0.03


def is_screenshot(image: Image.Image, filename: str = "") -> dict:
    """
    Detect if an image is likely a screenshot.

    Returns:
        dict with keys: is_screenshot (bool), confidence (str), reasons (list)
    """
    width, height = image.size
    reasons = []
    score = 0

    # --- Check 1: Exact resolution match ---
    if (width, height) in COMMON_SCREENSHOT_SIZES or (height, width) in COMMON_SCREENSHOT_SIZES:
        reasons.append(f"Exact device resolution match ({width}x{height})")
        score += 3

    # --- Check 2: Aspect ratio match ---
    ratio = min(width, height) / max(width, height)
    for sr in SCREENSHOT_RATIOS:
        if abs(ratio - sr) < RATIO_TOLERANCE:
            reasons.append(f"Aspect ratio {ratio:.3f} matches screenshot pattern")
            score += 2
            break

    # --- Check 3: Filename hints ---
    fname_lower = filename.lower()
    screenshot_keywords = ["screenshot", "screen shot", "screen_shot", "scr_", "capture", "snap"]
    if any(kw in fname_lower for kw in screenshot_keywords):
        reasons.append(f"Filename contains screenshot keyword")
        score += 3

    # --- Check 4: No EXIF camera data (screenshots lack camera info) ---
    exif = image.getexif()
    # Tag 271 = Make, Tag 272 = Model
    has_camera = exif.get(271) or exif.get(272)
    if not has_camera and exif:
        reasons.append("No camera make/model in EXIF (typical for screenshots)")
        score += 1
    elif not exif:
        reasons.append("No EXIF data at all")
        score += 1

    # --- Determine result ---
    is_ss = score >= 3
    if score >= 5:
        confidence = "high"
    elif score >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "is_screenshot": is_ss,
        "confidence": confidence,
        "reasons": reasons,
        "score": score,
        "resolution": f"{width}x{height}",
    }


def detect_screenshots(images: dict) -> dict:
    """
    Scan a dict of {filename: PIL.Image} and return screenshot detection results.

    Returns:
        dict with keys: screenshots (list), non_screenshots (list), summary (dict)
    """
    screenshots = []
    non_screenshots = []

    for filename, img in images.items():
        result = is_screenshot(img, filename)
        result["filename"] = filename
        if result["is_screenshot"]:
            screenshots.append(result)
        else:
            non_screenshots.append(result)

    return {
        "screenshots": screenshots,
        "non_screenshots": non_screenshots,
        "summary": {
            "total": len(images),
            "screenshots_found": len(screenshots),
            "percentage": round(len(screenshots) / max(len(images), 1) * 100, 1),
        },
    }
