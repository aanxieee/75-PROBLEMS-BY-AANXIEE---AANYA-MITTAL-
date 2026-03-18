# 🗂️ Gallery Storage Optimizer — Day 04/75

> **#75DayAIChallenge** | Problem 4 of 75

## 🧠 The Problem

Phone storage full? Yeah, mine too. 80% of it was screenshots I'll never look at again and 15 copies of the same sunset. I needed something that scans my gallery, spots the junk, and tells me what's safe to delete — without uploading anything to the cloud.

## 💡 The Solution

**Gallery Storage Optimizer** — a Streamlit app that:
- Accepts a zip folder of images
- Detects screenshots using aspect ratio, resolution matching, EXIF analysis, and filename hints
- Finds near-duplicate images using cosine similarity on flattened pixel vectors
- Clusters images into visual groups using KMeans on color histograms
- Generates a "Safe to Delete" list with estimated space savings

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core language |
| **Streamlit** | UI framework |
| **Pillow** | Image loading & processing |
| **scikit-learn** | KMeans clustering + cosine similarity |
| **NumPy** | Vector operations |
| **Plotly** | Charts (heatmap, bar chart, pie chart) |
| **Pandas** | Data wrangling for charts |

## 📂 Project Structure

```
day-04-gallery-optimizer/
├── app.py                      # Main Streamlit app
├── src/
│   ├── image_loader.py         # Zip extraction + image loading
│   ├── screenshot_detector.py  # Screenshot detection engine
│   ├── duplicate_finder.py     # Cosine similarity duplicate finder
│   └── cluster_analyzer.py     # KMeans image clustering
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 How to Run

```bash
# Clone the repo
git clone https://github.com/aanxieee/75-day-ai-challenge.git
cd 75-day-ai-challenge/day-04-gallery-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

## 🔒 Privacy

**100% local processing.** No images leave your machine. No cloud API. No external calls.

## ✨ Features

- **Screenshot Detection:** Checks device resolutions, aspect ratios, EXIF data, and filenames
- **Duplicate Finder:** Cosine similarity with adjustable threshold (sidebar slider)
- **Visual Clusters:** KMeans grouping with auto or manual cluster count
- **Similarity Heatmap:** See which images look alike at a glance
- **Delete List:** Combined screenshots + duplicates with estimated space savings

## 👩‍💻 About

Built by **Aanya** as part of the **75 Problems. 75 Real-World AI Solutions** challenge.

- GitHub: [@aanxieee](https://github.com/aanxieee)
- Instagram: [@aanxiee](https://instagram.com/aanxiee)
- Website: [aanxiee.com](https://aanxiee.com)

---

*Day 04/75 — #75DayAIChallenge #aanxiee75*
