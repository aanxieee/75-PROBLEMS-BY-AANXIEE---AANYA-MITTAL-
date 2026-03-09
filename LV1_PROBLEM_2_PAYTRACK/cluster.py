"""
model/cluster.py
Core logic for UPI Spend Analyzer:
- PhonePe PDF parsing (real format: Date | Transaction Details | Type | Amount)
- Paytm PDF parsing  (real format: Date & Time | Details | Notes & Tags | Account | Amount)
- Auto-detection of PDF source
- Data cleaning, category tagging, KMeans clustering
- Spending personality detection
"""

import re
import os
import pandas as pd
import pdfplumber
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Optional


# ── Category keyword map ──────────────────────────────────────────────────────
CATEGORY_MAP: dict[str, list[str]] = {
    "Food":           ["zomato", "swiggy", "dominos", "mcdonalds", "kfc",
                       "subway", "blinkit", "zepto", "burger", "pizza", "cafe",
                       "zomatofood", "food"],
    "Travel":         ["uber", "ola", "rapido", "irctc", "redbus", "makemytrip",
                       "goibibo", "metro", "petrol", "fuel", "ixigo"],
    "Shopping":       ["amazon", "flipkart", "myntra", "ajio", "meesho",
                       "nykaa", "snapdeal", "reliance", "tata cliq"],
    "Groceries":      ["bigbasket", "dmart", "grofers", "jiomart",
                       "nature basket", "supermarket", "kirana", "groceries"],
    "Entertainment":  ["netflix", "spotify", "prime", "hotstar", "bookmyshow",
                       "pvr", "inox", "youtube", "disney", "kukufm", "kuku fm"],
    "Utilities":      ["airtel", "jio", "vodafone", "bsnl", "electricity",
                       "water", "gas", "wifi", "broadband", "recharge",
                       "bharti hexacom", "tata power"],
    "Health":         ["pharmacy", "medplus", "apollo", "1mg", "netmeds",
                       "hospital", "clinic", "doctor", "lab"],
    "Money Transfer": ["sent to", "transfer", "money transfer"],
}


def tag_category(merchant: str) -> str:
    """Assign a spending category based on merchant name keywords."""
    merchant_lower = str(merchant).lower()
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in merchant_lower for kw in keywords):
            return category
    return "Other"


# ── PDF format auto-detection ─────────────────────────────────────────────────

def detect_pdf_source(text: str) -> str:
    """
    Detect whether a PDF is from PhonePe or Paytm.
    Returns: 'phonepe' | 'paytm' | 'unknown'
    """
    text_lower = text.lower()
    if "transaction statement for" in text_lower or "phonepe" in text_lower:
        return "phonepe"
    if "paytm" in text_lower or "passbook payments history" in text_lower:
        return "paytm"
    return "unknown"


# ── PhonePe Parser ────────────────────────────────────────────────────────────

def parse_phonepe_pdf(pdf_path: str) -> Optional[pd.DataFrame]:
    """
    Parse a PhonePe transaction statement PDF.

    PhonePe PDF real structure:
      Col 0 - Date:    'Mar 05, 2026\n10:28 pm'
      Col 1 - Details: 'Paid to ZOMATO LIMITED\nTransaction ID...\nUTR No...\nPaid by XXXXXX6573'
      Col 2 - Type:    'DEBIT' or 'CREDIT'
      Col 3 - Amount:  '962.9'
    """
    rows = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 4:
                            continue
                        # Skip header rows
                        if any(h in str(row[0]).lower()
                               for h in ["date", "transaction"]):
                            continue
                        rows.append(row)
    except Exception as e:
        print(f"[PhonePe] Table parse error: {e}")

    if not rows:
        return _parse_phonepe_text_fallback(pdf_path)

    records = []
    for row in rows:
        try:
            # Col 0: date — take first line only (ignore time)
            raw_date = str(row[0]).strip().split("\n")[0]

            # Col 1: first line is merchant description
            raw_detail = str(row[1]).strip().split("\n")[0]
            merchant = _clean_phonepe_merchant(raw_detail)

            # Col 2: DEBIT or CREDIT
            txn_type = str(row[2]).strip().upper()
            if txn_type not in ("DEBIT", "CREDIT"):
                continue

            # Col 3: amount
            amount = _parse_amount(str(row[3]))
            if amount is None:
                continue

            records.append({"Date": raw_date, "Merchant": merchant,
                             "Type": txn_type, "Amount": amount})
        except Exception:
            continue

    if not records:
        return None

    return _finalize_dataframe(pd.DataFrame(records))


def _parse_phonepe_text_fallback(pdf_path: str) -> Optional[pd.DataFrame]:
    """Text-based fallback for PhonePe when table extraction fails."""
    records = []
    date_re   = re.compile(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}"
    )
    amount_re = re.compile(r"(?:₹|Rs\.?)\s*([\d,]+\.?\d*)")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                lines = (page.extract_text() or "").split("\n")
                for i, line in enumerate(lines):
                    if not date_re.search(line):
                        continue
                    date_str = date_re.search(line).group()
                    merchant, amount, txn_type = "", None, "DEBIT"
                    for j in range(i + 1, min(i + 6, len(lines))):
                        if any(kw in lines[j].lower()
                               for kw in ["paid to", "payment to",
                                          "received from", "refund"]):
                            merchant = _clean_phonepe_merchant(lines[j])
                        if "DEBIT"  in lines[j]: txn_type = "DEBIT"
                        if "CREDIT" in lines[j]: txn_type = "CREDIT"
                        m = amount_re.search(lines[j])
                        if m and "transaction id" not in lines[j].lower():
                            amount = float(m.group(1).replace(",", ""))
                    if merchant and amount:
                        records.append({"Date": date_str, "Merchant": merchant,
                                        "Type": txn_type, "Amount": amount})
    except Exception as e:
        print(f"[PhonePe text] {e}")
        return None

    return _finalize_dataframe(pd.DataFrame(records)) if records else None


def _clean_phonepe_merchant(raw: str) -> str:
    """
    'Paid to ZOMATO LIMITED'  → 'Zomato'
    'Payment to SPOTIFY'      → 'Spotify'
    'Refund from KukuFM'      → 'Kukufm'
    """
    prefixes = ["paid to ", "payment to ", "refund from ",
                 "received from ", "paid by "]
    cleaned = raw.strip()
    for p in prefixes:
        if cleaned.lower().startswith(p):
            cleaned = cleaned[len(p):]
            break
    cleaned = re.sub(
        r"\s+(LIMITED|PRIVATE LIMITED|LTD\.?|PVT\.?\s*LTD\.?)$",
        "", cleaned, flags=re.IGNORECASE
    ).strip()
    return cleaned.title()


# ── Paytm Parser ──────────────────────────────────────────────────────────────

def parse_paytm_pdf(pdf_path: str) -> Optional[pd.DataFrame]:
    """
    Parse a Paytm UPI statement PDF.

    Paytm PDF real structure:
      Col 0 - Date & Time:  '07 Mar\n11:09 PM'
      Col 1 - Details:      'Money sent to Richa Kumari\nUPI ID: ...\nUPI Ref No: ...'
      Col 2 - Notes & Tags: 'Tag: #Money Transfer'
      Col 3 - Your Account: 'HDFC Bank - 73'
      Col 4 - Amount:       '- Rs.988'  or  '+ Rs.500'
    """
    rows = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 3:
                            continue
                        if any(h in str(row[0]).lower()
                               for h in ["date", "time", "account", "note"]):
                            continue
                        rows.append(row)
    except Exception as e:
        print(f"[Paytm] Table parse error: {e}")

    if not rows:
        return _parse_paytm_text_fallback(pdf_path)

    records = []
    for row in rows:
        try:
            raw_date   = str(row[0]).strip().split("\n")[0]
            raw_detail = str(row[1]).strip().split("\n")[0]
            merchant   = _clean_paytm_merchant(raw_detail)
            tag_col    = str(row[2]) if len(row) > 2 else ""
            raw_amount = str(row[-1]).strip()

            txn_type, amount = _parse_paytm_amount(raw_amount)
            if amount is None:
                continue

            hint = _extract_paytm_tag(tag_col)
            records.append({"Date": raw_date, "Merchant": merchant,
                             "Type": txn_type, "Amount": amount,
                             "_hint": hint})
        except Exception:
            continue

    if not records:
        return None

    return _finalize_dataframe(pd.DataFrame(records))


def _parse_paytm_text_fallback(pdf_path: str) -> Optional[pd.DataFrame]:
    """Text-based fallback for Paytm."""
    records = []
    date_re   = re.compile(r"\d{2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)")
    amount_re = re.compile(r"([+\-])\s*Rs\.?\s*([\d,]+\.?\d*)")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                lines = (page.extract_text() or "").split("\n")
                for i, line in enumerate(lines):
                    m = amount_re.search(line)
                    if not m:
                        continue
                    txn_type = "DEBIT" if m.group(1) == "-" else "CREDIT"
                    amount   = float(m.group(2).replace(",", ""))
                    date_str, merchant = "", "Unknown"
                    for j in range(max(0, i - 4), i):
                        dm = date_re.search(lines[j])
                        if dm:
                            date_str = lines[j].strip()
                        if any(kw in lines[j].lower()
                               for kw in ["paid to", "money sent",
                                          "payment to", "received from"]):
                            merchant = _clean_paytm_merchant(lines[j])
                    if date_str:
                        records.append({"Date": date_str, "Merchant": merchant,
                                        "Type": txn_type, "Amount": amount,
                                        "_hint": ""})
    except Exception as e:
        print(f"[Paytm text] {e}")
        return None

    return _finalize_dataframe(pd.DataFrame(records)) if records else None


def _clean_paytm_merchant(raw: str) -> str:
    """
    'Money sent to Richa Kumari' → 'Richa Kumari'
    'Paid to Zomatofood'         → 'Zomatofood'
    """
    prefixes = ["money sent to ", "paid to ", "payment to ",
                 "received from ", "refund from "]
    cleaned = raw.strip()
    for p in prefixes:
        if cleaned.lower().startswith(p):
            cleaned = cleaned[len(p):]
            break
    return cleaned.title().strip()


def _parse_paytm_amount(raw: str):
    """
    '- Rs.988'    → ('DEBIT',  988.0)
    '+ Rs.500'    → ('CREDIT', 500.0)
    '-Rs.4,000'   → ('DEBIT',  4000.0)
    """
    raw = raw.replace(",", "").strip()
    m = re.search(r"([+\-])\s*(?:Rs\.?|₹)?\s*([\d]+\.?\d*)", raw)
    if m:
        return ("DEBIT" if m.group(1) == "-" else "CREDIT"), float(m.group(2))
    m2 = re.search(r"(?:Rs\.?|₹)\s*([\d]+\.?\d*)", raw)
    if m2:
        return "DEBIT", float(m2.group(1))
    return "DEBIT", None


def _extract_paytm_tag(tag_col: str) -> str:
    """'Tag: #Food' → 'Food'"""
    m = re.search(r"#(\w[\w\s]*)", tag_col)
    return m.group(1).strip() if m else ""


# ── Main entry point ──────────────────────────────────────────────────────────

def parse_upi_pdf(pdf_path: str) -> Optional[pd.DataFrame]:
    """
    Auto-detect PDF source (PhonePe / Paytm) and parse accordingly.
    Returns a cleaned DataFrame or None if parsing fails.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_text = pdf.pages[0].extract_text() or ""
    except Exception:
        return None

    source = detect_pdf_source(first_text)

    if source == "phonepe":
        return parse_phonepe_pdf(pdf_path)
    elif source == "paytm":
        return parse_paytm_pdf(pdf_path)
    else:
        # Try both; return whichever gives more rows
        df_pp = parse_phonepe_pdf(pdf_path)
        df_pt = parse_paytm_pdf(pdf_path)
        if df_pp is not None and df_pt is not None:
            return df_pp if len(df_pp) >= len(df_pt) else df_pt
        return df_pp or df_pt


def load_csv(file_path: str) -> Optional[pd.DataFrame]:
    """Load transactions from a CSV file (demo/testing)."""
    try:
        return _finalize_dataframe(pd.read_csv(file_path))
    except Exception as e:
        print(f"CSV error: {e}")
        return None


# ── Shared finalization ───────────────────────────────────────────────────────

def _parse_amount(raw: str) -> Optional[float]:
    """Remove ₹/Rs/commas and convert to float."""
    cleaned = re.sub(r"[₹Rs\.,\s]", "", str(raw))
    try:
        return float(cleaned)
    except ValueError:
        return None


def _finalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize columns, parse dates, clean amounts,
    add time features and categories. Works on all sources.
    """
    df.columns = [str(c).strip().lower() for c in df.columns]

    col_map = {
        "date": "Date", "date & time": "Date",
        "merchant": "Merchant", "description": "Merchant",
        "transaction details": "Merchant",
        "amount": "Amount",
        "type": "Type",
        "_hint": "_hint",
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns},
              inplace=True)

    for col in ["Date", "Merchant", "Amount", "Type"]:
        if col not in df.columns:
            df[col] = "Unknown" if col != "Amount" else 0

    # Clean Amount
    if df["Amount"].dtype == object:
        df["Amount"] = (
            df["Amount"].astype(str)
            .str.replace(r"[₹Rs,\+\-\s]", "", regex=True)
            .str.extract(r"(\d+\.?\d*)")[0]
        )
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount"])

    # Only Debit transactions
    df["Type"] = df["Type"].astype(str).str.strip().str.upper()
    df = df[df["Type"] == "DEBIT"].copy()

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], infer_datetime_format=True,
                                errors="coerce")
    df = df.dropna(subset=["Date"])

    # Time features
    df["DayOfWeek"]  = df["Date"].dt.day_name()
    df["WeekOfMonth"] = df["Date"].dt.day.apply(lambda d: (d - 1) // 7 + 1)
    df["Month"]      = df["Date"].dt.strftime("%b %Y")

    # Category — prefer Paytm's own tag, else auto-tag
    if "_hint" in df.columns:
        df["Category"] = df.apply(
            lambda r: r["_hint"] if r["_hint"] else tag_category(r["Merchant"]),
            axis=1
        )
        df.drop(columns=["_hint"], inplace=True)
    else:
        df["Category"] = df["Merchant"].apply(tag_category)

    keep = ["Date", "Merchant", "Amount", "Type",
            "Category", "DayOfWeek", "WeekOfMonth", "Month"]
    return df[keep].reset_index(drop=True)


# ── KMeans Clustering ─────────────────────────────────────────────────────────

def run_clustering(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """
    KMeans on Amount + DayOfWeek + Category.
    Adds 'Cluster' and 'ClusterLabel' columns.
    """
    if len(df) < n_clusters:
        df["Cluster"] = 0
        df["ClusterLabel"] = "General Spending"
        return df

    df_enc = df.copy()
    df_enc["DayNum"] = pd.Categorical(df_enc["DayOfWeek"]).codes
    df_enc["CatNum"] = pd.Categorical(df_enc["Category"]).codes

    features = df_enc[["Amount", "DayNum", "CatNum"]].fillna(0)
    scaled   = StandardScaler().fit_transform(features)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["Cluster"] = km.fit_predict(scaled)
    df["ClusterLabel"] = df["Cluster"].apply(
        lambda c: _label_cluster(df[df["Cluster"] == c])
    )
    return df


def _label_cluster(cluster_df: pd.DataFrame) -> str:
    """Human label based on dominant category + avg amount."""
    if cluster_df.empty:
        return "Misc"
    dominant = cluster_df["Category"].mode()[0]
    avg      = cluster_df["Amount"].mean()
    label_map = {
        "Food":           "🍔 Foodie Days",
        "Travel":         "🚗 On-The-Move",
        "Shopping":       "🛍️ Impulse Buys",
        "Groceries":      "🛒 Essentials Run",
        "Entertainment":  "🎬 Fun Splurge",
        "Utilities":      "💡 Bills & Basics",
        "Health":         "💊 Health First",
        "Money Transfer": "💸 Money Sent",
        "Other":          "❓ Misc Spends",
    }
    base = label_map.get(dominant, "❓ Misc Spends")
    if avg > 1000:  return f"{base} (Big Ticket)"
    if avg < 200:   return f"{base} (Small & Often)"
    return base


# ── Personality & Top Merchants ───────────────────────────────────────────────

def get_spending_personality(df: pd.DataFrame) -> dict:
    """Spending personality from category distribution."""
    if df.empty:
        return {"name": "Unknown", "emoji": "❓",
                "description": "No data", "top_pct": 0}

    cat   = df.groupby("Category")["Amount"].sum()
    total = cat.sum()

    pcts = {c: cat.get(c, 0) / total * 100
            for c in ["Food", "Shopping", "Travel", "Money Transfer"]}
    top_cat = cat.idxmax()
    top_pct = cat.max() / total * 100

    if pcts["Food"] > 35:
        return {"name": "The Foodie", "emoji": "🍕",
                "description": "Food is your love language. Zomato knows you by name.",
                "top_pct": round(pcts["Food"], 1)}
    elif pcts["Shopping"] > 30:
        return {"name": "The Impulse Buyer", "emoji": "🛍️",
                "description": "Your cart is always full. Sale notifications are your weakness.",
                "top_pct": round(pcts["Shopping"], 1)}
    elif pcts["Travel"] > 25:
        return {"name": "The Commuter", "emoji": "🚗",
                "description": "Always on the move. Uber surge pricing is your nemesis.",
                "top_pct": round(pcts["Travel"], 1)}
    elif pcts["Money Transfer"] > 30:
        return {"name": "The Generous One", "emoji": "💸",
                "description": "You send money more than you spend it. Everyone's favourite person.",
                "top_pct": round(pcts["Money Transfer"], 1)}
    elif top_pct < 25:
        return {"name": "The Balanced Spender", "emoji": "⚖️",
                "description": "Spread across categories — actually pretty disciplined.",
                "top_pct": round(top_pct, 1)}
    else:
        return {"name": "The Practical Spender", "emoji": "🧾",
                "description": f"Most money goes to {top_cat}. Needs-first mindset.",
                "top_pct": round(top_pct, 1)}


def get_top_merchants(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Top N merchants by total spend."""
    return (
        df.groupby("Merchant")["Amount"].sum()
        .sort_values(ascending=False).head(n)
        .reset_index()
        .rename(columns={"Amount": "Total Spent (₹)"})
    )
