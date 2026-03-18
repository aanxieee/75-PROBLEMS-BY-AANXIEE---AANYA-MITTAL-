"""
Duplicate Finder
Finds duplicate/near-duplicate images using cosine similarity on resized thumbnails.
"""

import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

THUMBNAIL_SIZE = (64, 64)  # Resize all images to this for comparison
SIMILARITY_THRESHOLD = 0.95  # Cosine similarity above this = duplicate


def _image_to_vector(img: Image.Image) -> np.ndarray:
    """Resize image to thumbnail and flatten to 1D vector."""
    thumb = img.resize(THUMBNAIL_SIZE, Image.LANCZOS)
    return np.array(thumb, dtype=np.float32).flatten() / 255.0


def find_duplicates(images: dict, threshold: float = SIMILARITY_THRESHOLD) -> dict:
    """
    Find duplicate image pairs using cosine similarity.

    Args:
        images: dict of {filename: PIL.Image}
        threshold: similarity threshold (0-1), higher = stricter

    Returns:
        dict with keys: pairs (list of tuples), similarity_matrix, filenames
    """
    filenames = list(images.keys())
    if len(filenames) < 2:
        return {"pairs": [], "similarity_matrix": None, "filenames": filenames}

    # Convert all images to vectors
    vectors = np.array([_image_to_vector(images[f]) for f in filenames])

    # Compute pairwise cosine similarity
    sim_matrix = cosine_similarity(vectors)

    # Find pairs above threshold (upper triangle only to avoid duplicates)
    pairs = []
    seen = set()
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            if sim_matrix[i][j] >= threshold:
                pair = {
                    "file_a": filenames[i],
                    "file_b": filenames[j],
                    "similarity": round(float(sim_matrix[i][j]) * 100, 2),
                }
                pairs.append(pair)
                seen.add(filenames[j])  # Mark the second one as deletable

    # Sort by similarity descending
    pairs.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "pairs": pairs,
        "deletable": list(seen),  # Second image in each pair → safe to delete
        "similarity_matrix": sim_matrix,
        "filenames": filenames,
        "summary": {
            "total_pairs": len(pairs),
            "unique_deletable": len(seen),
        },
    }
