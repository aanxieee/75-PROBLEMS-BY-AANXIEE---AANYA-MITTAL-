"""
Cluster Analyzer
Groups images into visual clusters using KMeans on color histograms.
"""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def _image_to_histogram(img: Image.Image, bins: int = 32) -> np.ndarray:
    """Convert image to a normalized color histogram feature vector."""
    img_resized = img.resize((128, 128), Image.LANCZOS)
    arr = np.array(img_resized)

    # Compute histogram per channel and concatenate
    histograms = []
    for channel in range(3):
        hist, _ = np.histogram(arr[:, :, channel], bins=bins, range=(0, 256))
        hist = hist.astype(np.float32) / hist.sum()  # Normalize
        histograms.append(hist)

    return np.concatenate(histograms)


def cluster_images(images: dict, n_clusters: int = None) -> dict:
    """
    Cluster images using KMeans on color histograms.

    Args:
        images: dict of {filename: PIL.Image}
        n_clusters: number of clusters. Auto-calculated if None.

    Returns:
        dict with cluster assignments, cluster sizes, and feature vectors.
    """
    filenames = list(images.keys())

    if len(filenames) < 2:
        return {
            "clusters": {0: filenames},
            "labels": [0] * len(filenames),
            "filenames": filenames,
            "n_clusters": 1,
        }

    # Auto-determine cluster count: sqrt rule, capped
    if n_clusters is None:
        n_clusters = max(2, min(int(np.sqrt(len(filenames))), 10))

    # Can't have more clusters than images
    n_clusters = min(n_clusters, len(filenames))

    # Build feature matrix
    features = np.array([_image_to_histogram(images[f]) for f in filenames])

    # Run KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features)

    # Group filenames by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        label = int(label)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(filenames[idx])

    # Cluster sizes for summary
    cluster_sizes = {k: len(v) for k, v in sorted(clusters.items())}

    return {
        "clusters": clusters,
        "labels": labels.tolist(),
        "filenames": filenames,
        "n_clusters": n_clusters,
        "cluster_sizes": cluster_sizes,
    }
