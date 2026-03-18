"""
Gallery Storage Optimizer — Day 04/75
Scan your photos, detect screenshots, find duplicates, and free up space.
100% offline. No cloud. No API.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.image_loader import load_images_from_zip, get_image_info
from src.screenshot_detector import detect_screenshots
from src.duplicate_finder import find_duplicates
from src.cluster_analyzer import cluster_images

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Gallery Storage Optimizer",
    page_icon="🗂️",
    layout="wide",
)

st.title("🗂️ Gallery Storage Optimizer")
st.caption("Day 04/75 — #75DayAIChallenge | 100% Local. No Cloud. No API.")

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    similarity_threshold = st.slider(
        "Duplicate Similarity Threshold",
        min_value=0.80,
        max_value=1.00,
        value=0.95,
        step=0.01,
        help="Higher = stricter matching. 0.95 catches near-identical images.",
    )
    n_clusters = st.number_input(
        "Number of Clusters (0 = auto)",
        min_value=0,
        max_value=20,
        value=0,
        help="How many groups to sort images into. 0 lets the app decide.",
    )
    st.divider()
    st.markdown("**Built by [aanxiee](https://github.com/aanxieee)**")
    st.markdown("#75DayAIChallenge")

# ── Upload ───────────────────────────────────────────────────
uploaded_zip = st.file_uploader(
    "Upload a ZIP folder of images",
    type=["zip"],
    help="Put your photos in a zip file and upload here.",
)

if uploaded_zip is None:
    st.info("👆 Upload a zip file with your images to get started.")
    st.stop()

# ── Process ──────────────────────────────────────────────────
with st.spinner("Extracting and loading images..."):
    images = load_images_from_zip(uploaded_zip.read())

if not images:
    st.error("No valid images found in the zip file. Supported: JPG, PNG, WEBP, BMP, GIF.")
    st.stop()

st.success(f"Loaded **{len(images)}** images from `{uploaded_zip.name}`")

# ── Analysis ─────────────────────────────────────────────────
with st.spinner("Analyzing images..."):
    image_info = get_image_info(images)
    ss_results = detect_screenshots(images)
    dup_results = find_duplicates(images, threshold=similarity_threshold)
    cluster_n = n_clusters if n_clusters > 0 else None
    cluster_results = cluster_images(images, n_clusters=cluster_n)

# ── Summary Metrics ──────────────────────────────────────────
st.header("📊 Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Images", len(images))
with col2:
    st.metric("Screenshots", ss_results["summary"]["screenshots_found"])
with col3:
    st.metric("Duplicate Pairs", dup_results["summary"]["total_pairs"])
with col4:
    safe_to_delete = set()
    for s in ss_results["screenshots"]:
        safe_to_delete.add(s["filename"])
    for d in dup_results["deletable"]:
        safe_to_delete.add(d)
    st.metric("Safe to Delete", len(safe_to_delete))

# ── Tab Layout ───────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📱 Screenshots", "🔁 Duplicates", "🗂️ Clusters", "🗑️ Delete List"]
)

# ── Tab 1: Screenshots ──────────────────────────────────────
with tab1:
    st.subheader("Screenshots Detected")

    if not ss_results["screenshots"]:
        st.info("No screenshots detected!")
    else:
        for item in ss_results["screenshots"]:
            fname = item["filename"]
            with st.expander(f"📱 {fname} — {item['confidence']} confidence"):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    st.image(images[fname], width=200)
                with col_info:
                    st.write(f"**Resolution:** {item['resolution']}")
                    st.write(f"**Score:** {item['score']}")
                    st.write("**Reasons:**")
                    for r in item["reasons"]:
                        st.write(f"  - {r}")

# ── Tab 2: Duplicates ───────────────────────────────────────
with tab2:
    st.subheader("Duplicate Pairs")

    if not dup_results["pairs"]:
        st.info("No duplicates found at the current threshold!")
    else:
        for pair in dup_results["pairs"]:
            st.markdown(f"**Similarity: {pair['similarity']}%**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.image(images[pair["file_a"]], caption=pair["file_a"], use_container_width=True)
            with col_b:
                st.image(images[pair["file_b"]], caption=pair["file_b"], use_container_width=True)
            st.divider()

    # Heatmap if enough images
    if dup_results["similarity_matrix"] is not None and len(dup_results["filenames"]) <= 30:
        st.subheader("Similarity Heatmap")
        fig = px.imshow(
            dup_results["similarity_matrix"],
            x=dup_results["filenames"],
            y=dup_results["filenames"],
            color_continuous_scale="RdYlGn",
            zmin=0.5,
            zmax=1.0,
            labels=dict(color="Similarity"),
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Clusters ─────────────────────────────────────────
with tab3:
    st.subheader(f"Image Clusters ({cluster_results['n_clusters']} groups)")

    # Cluster size bar chart
    sizes_df = pd.DataFrame(
        list(cluster_results["cluster_sizes"].items()),
        columns=["Cluster", "Count"],
    )
    sizes_df["Cluster"] = sizes_df["Cluster"].apply(lambda x: f"Group {x + 1}")

    fig_bar = px.bar(
        sizes_df,
        x="Cluster",
        y="Count",
        color="Count",
        color_continuous_scale="teal",
        title="Images per Cluster",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Show each cluster
    for cluster_id, members in sorted(cluster_results["clusters"].items()):
        with st.expander(f"🗂️ Group {cluster_id + 1} — {len(members)} images"):
            cols = st.columns(min(len(members), 4))
            for idx, fname in enumerate(members):
                with cols[idx % 4]:
                    st.image(images[fname], caption=fname, use_container_width=True)

# ── Tab 4: Safe to Delete ───────────────────────────────────
with tab4:
    st.subheader("🗑️ Safe to Delete")
    st.caption("Screenshots + duplicate copies (keeping one from each pair)")

    if not safe_to_delete:
        st.success("Your gallery looks clean! Nothing flagged for deletion.")
    else:
        # Storage savings estimate
        total_kb = sum(
            info["estimated_kb"]
            for info in image_info
            if info["filename"] in safe_to_delete
        )
        st.metric(
            "Estimated Space Savings",
            f"{total_kb / 1024:.1f} MB" if total_kb > 1024 else f"{total_kb:.0f} KB",
        )

        # Pie chart
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=["Keep", "Delete"],
                    values=[
                        len(images) - len(safe_to_delete),
                        len(safe_to_delete),
                    ],
                    marker_colors=["#2ecc71", "#e74c3c"],
                    hole=0.4,
                )
            ]
        )
        fig_pie.update_layout(title="Keep vs Delete")
        st.plotly_chart(fig_pie, use_container_width=True)

        # File list
        st.markdown("**Files flagged for deletion:**")
        for fname in sorted(safe_to_delete):
            reason = []
            if any(s["filename"] == fname for s in ss_results["screenshots"]):
                reason.append("Screenshot")
            if fname in dup_results["deletable"]:
                reason.append("Duplicate")
            tag = " + ".join(reason)
            st.write(f"- `{fname}` — _{tag}_")
