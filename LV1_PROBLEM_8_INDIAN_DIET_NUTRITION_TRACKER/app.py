"""
🍛 Indian Diet Nutrition Tracker
Day 08/75 — Healthcare Domain | Streamlit App
Track daily Indian food intake → see nutrition gaps → get smart dinner suggestions.
"""
import streamlit as st
from datetime import date, timedelta
from src.food_database import (
    load_foods, search_foods, get_categories, get_foods_by_category,
    NUTRIENT_DISPLAY, NUTRIENT_UNITS,
)
from src.tracker import (
    get_connection, get_profile, save_profile,
    add_food_entry, get_daily_log, get_daily_totals,
    get_meal_totals, remove_food_entry, get_log_dates,
)
from src.calculator import calculate_targets, nutrient_percentage, get_deficit
from src.recommender import get_recommendations, get_meal_suggestion

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="🍛 Indian Diet Tracker",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Mobile-Friendly CSS ─────────────────────────────────────
st.markdown("""
<style>
    /* Mobile-first responsive */
    .block-container { padding: 1rem 1rem !important; max-width: 900px !important; }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
    }
    .main-header h1 { font-size: 1.8rem; margin: 0; }
    .main-header p { color: #888; font-size: 0.9rem; margin: 0.2rem 0 0 0; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2a2a4a;
    }
    .metric-card h3 { margin: 0; font-size: 0.8rem; color: #aaa; }
    .metric-card .value { font-size: 1.6rem; font-weight: bold; margin: 0.3rem 0; }
    .metric-card .unit { font-size: 0.75rem; color: #888; }

    /* Progress bars */
    .nutrient-bar {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.4rem;
        border: 1px solid #2a2a4a;
    }
    .nutrient-bar .label {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 0.3rem;
    }
    .progress-outer {
        background: #2a2a4a;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
    }
    .progress-inner {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    /* Recommendation cards */
    .rec-card {
        background: #1a1a2e;
        border-left: 4px solid #ff6b6b;
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
    }
    .rec-card.good { border-left-color: #51cf66; }
    .rec-card.medium { border-left-color: #ffd43b; }

    /* Food log */
    .food-entry {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1a2e;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.3rem;
        border: 1px solid #2a2a4a;
        font-size: 0.85rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] { font-size: 0.9rem; padding: 0.5rem 0.8rem; }

    /* Hide Streamlit extras */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .block-container { padding: 0.5rem !important; }
        .main-header h1 { font-size: 1.4rem; }
    }
</style>
""", unsafe_allow_html=True)


# ── Database Connection ──────────────────────────────────────
@st.cache_resource
def init_db():
    return get_connection()

conn = init_db()

# ── Helper Functions ─────────────────────────────────────────

def render_progress_bar(label: str, consumed: float, target: float, unit: str, color: str = "#4dabf7"):
    """Render a custom progress bar for a nutrient."""
    pct = nutrient_percentage(consumed, target)
    bar_pct = min(pct, 100)

    if pct >= 90:
        color = "#51cf66"  # green
    elif pct >= 50:
        color = "#ffd43b"  # yellow
    else:
        color = "#ff6b6b"  # red

    st.markdown(f"""
    <div class="nutrient-bar">
        <div class="label">
            <span>{label}</span>
            <span>{consumed:.1f} / {target:.0f} {unit} ({pct:.0f}%)</span>
        </div>
        <div class="progress-outer">
            <div class="progress-inner" style="width: {bar_pct}%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_color_for_cal(consumed: float, target: float) -> str:
    """Get color based on calorie consumption."""
    pct = (consumed / target * 100) if target > 0 else 0
    if pct > 110:
        return "#ff6b6b"
    elif pct >= 80:
        return "#51cf66"
    elif pct >= 50:
        return "#ffd43b"
    return "#4dabf7"


# ── App Header ───────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🍛 Indian Diet Tracker</h1>
    <p>Track karo • Gaps dekho • Smart suggestions lo</p>
</div>
""", unsafe_allow_html=True)

# ── Profile Setup ────────────────────────────────────────────
profile = get_profile(conn)

if not profile:
    st.info("👋 Pehle apna profile set up karo — personalized targets ke liye!")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Name", value="User")
            p_age = st.number_input("Age", min_value=10, max_value=80, value=22)
            p_gender = st.selectbox("Gender", ["female", "male"])
        with col2:
            p_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=60.0, step=0.5)
            p_height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=160.0, step=0.5)
            p_activity = st.selectbox("Activity Level", [
                "sedentary", "light", "moderate", "active", "very_active"
            ], index=2, format_func=lambda x: {
                "sedentary": "🪑 Sedentary (desk job)",
                "light": "🚶 Light (1-3 days/week)",
                "moderate": "🏃 Moderate (3-5 days/week)",
                "active": "💪 Active (6-7 days/week)",
                "very_active": "🔥 Very Active (intense daily)",
            }.get(x, x))
        p_goal = st.selectbox("Goal", [
            "lose", "mild_lose", "maintain", "mild_gain", "gain"
        ], index=0, format_func=lambda x: {
            "lose": "⬇️ Lose Weight (-500 kcal)",
            "mild_lose": "↘️ Mild Loss (-250 kcal)",
            "maintain": "➡️ Maintain Weight",
            "mild_gain": "↗️ Mild Gain (+250 kcal)",
            "gain": "⬆️ Gain Weight (+500 kcal)",
        }.get(x, x))

        if st.form_submit_button("💾 Save Profile", use_container_width=True):
            profile = save_profile(conn, p_name, p_age, p_gender, p_weight, p_height, p_activity, p_goal)
            st.success(f"Profile saved! Welcome {p_name} 🎉")
            st.rerun()
    st.stop()

# ── Calculate Targets ────────────────────────────────────────
targets = calculate_targets(
    profile["weight_kg"], profile["height_cm"], profile["age"],
    profile["gender"], profile["activity_level"], profile["goal"]
)

# ── Date Selector ────────────────────────────────────────────
today = date.today()
selected_date = st.date_input("📅 Date", value=today, max_value=today,
                               min_value=today - timedelta(days=30))
date_str = selected_date.isoformat()

# ── Get Current Data ─────────────────────────────────────────
daily_totals = get_daily_totals(conn, date_str)
daily_log = get_daily_log(conn, date_str)
deficit = get_deficit(daily_totals, targets)

# ── Quick Stats Row ──────────────────────────────────────────
cal_color = get_color_for_cal(daily_totals["calories"], targets["calories"])
cols = st.columns(4)
with cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🔥 Calories</h3>
        <div class="value" style="color: {cal_color};">{daily_totals['calories']:.0f}</div>
        <div class="unit">/ {targets['calories']:.0f} kcal</div>
    </div>""", unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <h3>💪 Protein</h3>
        <div class="value" style="color: #4dabf7;">{daily_totals['protein']:.1f}</div>
        <div class="unit">/ {targets['protein']:.0f} g</div>
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🍚 Carbs</h3>
        <div class="value" style="color: #ffd43b;">{daily_totals['carbs']:.1f}</div>
        <div class="unit">/ {targets['carbs']:.0f} g</div>
    </div>""", unsafe_allow_html=True)
with cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🧈 Fats</h3>
        <div class="value" style="color: #ff922b;">{daily_totals['fats']:.1f}</div>
        <div class="unit">/ {targets['fats']:.0f} g</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Tabs ────────────────────────────────────────────────
tab_add, tab_summary, tab_suggest, tab_log, tab_profile = st.tabs([
    "➕ Add Food", "📊 Summary", "💡 Suggestions", "📋 Food Log", "👤 Profile"
])

# ── TAB 1: Add Food ─────────────────────────────────────────
with tab_add:
    st.subheader("Kya khaya? 🍽️")

    # Search or browse
    search_mode = st.radio("Find food:", ["🔍 Search", "📂 Browse Category"],
                           horizontal=True, label_visibility="collapsed")

    if search_mode == "🔍 Search":
        query = st.text_input("Food search karo...", placeholder="dal, paneer, roti, egg...")
        if query:
            results = search_foods(query)
        else:
            results = []
    else:
        categories = get_categories()
        selected_cat = st.selectbox("Category", categories)
        results = get_foods_by_category(selected_cat)

    if results:
        food_options = {f"{f['name']} ({f['serving_size']})": f for f in results}
        selected = st.selectbox("Select food:", list(food_options.keys()))
        food = food_options[selected]

        col1, col2 = st.columns(2)
        with col1:
            servings = st.number_input("Servings", min_value=0.25, max_value=10.0,
                                        value=1.0, step=0.25)
        with col2:
            meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Snack", "Dinner"])

        # Show nutrition preview
        n = food["nutrients"]
        st.caption(f"Per serving: {n['calories']:.0f} kcal | P: {n['protein']:.1f}g | "
                   f"C: {n['carbs']:.1f}g | F: {n['fats']:.1f}g")

        if servings != 1.0:
            st.caption(f"× {servings} servings = **{n['calories']*servings:.0f} kcal** | "
                       f"P: {n['protein']*servings:.1f}g | C: {n['carbs']*servings:.1f}g | "
                       f"F: {n['fats']*servings:.1f}g")

        if st.button("✅ Add to Log", use_container_width=True, type="primary"):
            entry_id = add_food_entry(conn, meal_type, food, servings, date_str)
            st.success(f"Added: {food['name']} × {servings} → {meal_type}")
            st.rerun()
    elif search_mode == "🔍 Search" and query:
        st.warning(f"'{query}' nahi mila database mein. Try different name.")

# ── TAB 2: Nutrition Summary ────────────────────────────────
with tab_summary:
    if not daily_log:
        st.info("Aaj kuch log nahi hua. ➕ Add Food tab se khaana add karo!")
    else:
        st.subheader("Macros")
        render_progress_bar("🔥 Calories", daily_totals["calories"], targets["calories"], "kcal")
        render_progress_bar("💪 Protein", daily_totals["protein"], targets["protein"], "g")
        render_progress_bar("🍚 Carbs", daily_totals["carbs"], targets["carbs"], "g")
        render_progress_bar("🧈 Fats", daily_totals["fats"], targets["fats"], "g")
        render_progress_bar("🌾 Fiber", daily_totals["fiber"], targets["fiber"], "g")

        st.subheader("Minerals")
        render_progress_bar("🦴 Calcium", daily_totals["calcium"], targets["calcium"], "mg")
        render_progress_bar("🩸 Iron", daily_totals["iron"], targets["iron"], "mg")
        render_progress_bar("⚡ Zinc", daily_totals["zinc"], targets["zinc"], "mg")

        st.subheader("Vitamins")
        render_progress_bar("👁️ Vitamin A", daily_totals["vitamin_a"], targets["vitamin_a"], "mcg")
        render_progress_bar("🧬 Vitamin B12", daily_totals["vitamin_b12"], targets["vitamin_b12"], "mcg")
        render_progress_bar("🍊 Vitamin C", daily_totals["vitamin_c"], targets["vitamin_c"], "mg")
        render_progress_bar("☀️ Vitamin D", daily_totals["vitamin_d"], targets["vitamin_d"], "mcg")

# ── TAB 3: Smart Suggestions ────────────────────────────────
with tab_suggest:
    st.subheader("Kya khana chahiye? 💡")

    if not daily_log:
        st.info("Pehle kuch food add karo, phir suggestions milenge!")
    else:
        # Determine next meal
        meal_totals = get_meal_totals(conn, date_str)
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 11:
            next_meal = "Lunch"
        elif hour < 16:
            next_meal = "Snack/Dinner"
        else:
            next_meal = "Dinner"

        # Get text suggestion
        suggestion_text = get_meal_suggestion(deficit, next_meal)
        st.markdown(suggestion_text)

        st.divider()

        # Detailed recommendations
        recs = get_recommendations(deficit, meal_totals)
        for rec in recs:
            border_class = "good" if rec["priority"] == "good" else ("medium" if rec["emoji"] == "🟡" else "")
            st.markdown(f"""
            <div class="rec-card {border_class}">
                <strong>{rec['emoji']} {rec['message']}</strong>
            </div>
            """, unsafe_allow_html=True)

            if rec.get("foods"):
                food_names = [f"**{f['name']}** ({f['amount']:.1f}{f['unit']}/{f['serving']})"
                              for f in rec["foods"][:3]]
                st.caption("Try: " + " • ".join(food_names))

# ── TAB 4: Food Log ─────────────────────────────────────────
with tab_log:
    st.subheader(f"📋 Food Log — {selected_date.strftime('%d %b %Y')}")

    if not daily_log:
        st.info("Aaj ka log empty hai. Khaana add karo! 🍽️")
    else:
        for meal in ["Breakfast", "Lunch", "Snack", "Dinner"]:
            entries = [e for e in daily_log if e["meal_type"] == meal]
            if entries:
                st.markdown(f"**{meal}**")
                for entry in entries:
                    col1, col2, col3 = st.columns([5, 3, 1])
                    with col1:
                        st.write(f"{entry['food_name']} × {entry['servings']:.1f}")
                    with col2:
                        st.caption(f"{entry['calories']:.0f} kcal | P:{entry['protein']:.1f}g")
                    with col3:
                        if st.button("🗑️", key=f"del_{entry['id']}", help="Remove"):
                            remove_food_entry(conn, entry["id"])
                            st.rerun()
                st.divider()

        # Daily total
        st.markdown(f"**Total: {daily_totals['calories']:.0f} kcal | "
                    f"P: {daily_totals['protein']:.1f}g | "
                    f"C: {daily_totals['carbs']:.1f}g | "
                    f"F: {daily_totals['fats']:.1f}g**")

# ── TAB 5: Profile ──────────────────────────────────────────
with tab_profile:
    st.subheader("👤 Your Profile")

    with st.form("edit_profile"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Name", value=profile["name"])
            p_age = st.number_input("Age", min_value=10, max_value=80, value=profile["age"])
            p_gender = st.selectbox("Gender", ["female", "male"],
                                     index=0 if profile["gender"] == "female" else 1)
        with col2:
            p_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0,
                                        value=float(profile["weight_kg"]), step=0.5)
            p_height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0,
                                        value=float(profile["height_cm"]), step=0.5)
            p_activity = st.selectbox("Activity Level", [
                "sedentary", "light", "moderate", "active", "very_active"
            ], index=["sedentary", "light", "moderate", "active", "very_active"].index(profile["activity_level"]),
            format_func=lambda x: {
                "sedentary": "🪑 Sedentary",
                "light": "🚶 Light",
                "moderate": "🏃 Moderate",
                "active": "💪 Active",
                "very_active": "🔥 Very Active",
            }.get(x, x))
        p_goal = st.selectbox("Goal", [
            "lose", "mild_lose", "maintain", "mild_gain", "gain"
        ], index=["lose", "mild_lose", "maintain", "mild_gain", "gain"].index(profile["goal"]),
        format_func=lambda x: {
            "lose": "⬇️ Lose Weight",
            "mild_lose": "↘️ Mild Loss",
            "maintain": "➡️ Maintain",
            "mild_gain": "↗️ Mild Gain",
            "gain": "⬆️ Gain Weight",
        }.get(x, x))

        if st.form_submit_button("💾 Update Profile", use_container_width=True):
            profile = save_profile(conn, p_name, p_age, p_gender, p_weight, p_height, p_activity, p_goal)
            st.success("Profile updated! ✅")
            st.rerun()

    # Show calculated targets
    st.divider()
    st.markdown("**📊 Your Daily Targets:**")
    st.caption(f"BMR: {targets['_bmr']:.0f} kcal → TDEE: {targets['_tdee']:.0f} kcal → "
               f"Target: {targets['calories']:.0f} kcal (adj: {targets['_calorie_adjustment']:+.0f})")

    target_cols = st.columns(3)
    display_targets = {k: v for k, v in targets.items() if not k.startswith("_")}
    items = list(display_targets.items())
    for i, (nutrient, value) in enumerate(items):
        with target_cols[i % 3]:
            unit = NUTRIENT_UNITS.get(nutrient, "")
            display = NUTRIENT_DISPLAY.get(nutrient, nutrient)
            st.metric(display, f"{value:.1f} {unit}")


# ── Footer ───────────────────────────────────────────────────
st.divider()
st.caption("🍛 Indian Diet Nutrition Tracker | Day 08/75 — Healthcare Domain | Built by aanxieee")
