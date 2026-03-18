"""
Smart Food Recommender
Rule-based recommendations: what to eat next based on current deficits.
"""
from typing import Dict, List, Tuple
from src.food_database import load_foods, get_top_foods_for_nutrient, NUTRIENT_DISPLAY, NUTRIENT_UNITS


def get_recommendations(deficit: Dict, meal_totals: Dict) -> List[Dict]:
    """
    Generate meal recommendations based on current nutrient deficits.
    Returns list of recommendation dicts with priority, message, and suggested foods.
    """
    recommendations = []
    foods = load_foods()

    # Identify critical deficits (nutrients where less than 50% consumed by lunch)
    critical_nutrients = _find_critical_deficits(deficit)

    if not critical_nutrients:
        recommendations.append({
            "priority": "good",
            "emoji": "✅",
            "message": "Badhiya! Aaj ka nutrition on track hai!",
            "foods": [],
        })
        return recommendations

    # Generate recommendations for top 3 critical nutrients
    for nutrient, remaining in critical_nutrients[:3]:
        display_name = NUTRIENT_DISPLAY.get(nutrient, nutrient)
        unit = NUTRIENT_UNITS.get(nutrient, "")

        # Find best foods for this nutrient
        best_foods = _get_best_foods_for_deficit(nutrient, remaining, foods)

        if remaining > 0:
            msg = f"{display_name} {remaining:.0f}{unit} aur chahiye"
            recommendations.append({
                "priority": "high" if remaining > 0 else "low",
                "emoji": "🔴" if nutrient in ("protein", "calories", "iron", "calcium") else "🟡",
                "nutrient": nutrient,
                "message": msg,
                "foods": best_foods[:3],
            })

    return recommendations


def _find_critical_deficits(deficit: Dict) -> List[Tuple[str, float]]:
    """
    Find nutrients with significant deficits.
    Returns sorted list of (nutrient, remaining_amount) tuples.
    """
    # Priority weights — protein and iron are more critical in Indian diets
    priority_weights = {
        "protein": 3.0,
        "iron": 2.5,
        "calcium": 2.0,
        "vitamin_b12": 2.0,
        "vitamin_d": 2.0,
        "calories": 1.5,
        "fiber": 1.5,
        "zinc": 1.5,
        "vitamin_a": 1.0,
        "vitamin_c": 1.0,
        "carbs": 0.8,
        "fats": 0.8,
    }

    deficits = []
    for nutrient, remaining in deficit.items():
        if remaining > 0 and nutrient in priority_weights:
            # Score = deficit percentage × priority weight
            deficits.append((nutrient, remaining, priority_weights.get(nutrient, 1.0)))

    # Sort by weighted priority (highest deficit × weight first)
    deficits.sort(key=lambda x: x[2], reverse=True)
    return [(n, r) for n, r, _ in deficits]


def _get_best_foods_for_deficit(nutrient: str, deficit_amount: float,
                                 foods: List[Dict]) -> List[Dict]:
    """Get best food suggestions to fill a specific nutrient deficit."""
    # Sort foods by this nutrient content (per serving)
    scored = []
    for food in foods:
        value = food["nutrients"].get(nutrient, 0)
        if value > 0:
            scored.append({
                "name": food["name"],
                "id": food["id"],
                "serving": food["serving_size"],
                "amount": value,
                "unit": NUTRIENT_UNITS.get(nutrient, ""),
            })

    scored.sort(key=lambda x: x["amount"], reverse=True)
    return scored[:5]


def get_meal_suggestion(deficit: Dict, current_meal: str) -> str:
    """
    Get a simple text suggestion for the next meal.
    Hinglish style messaging.
    """
    suggestions = []

    if deficit.get("protein", 0) > 15:
        suggestions.append("Protein kam hai — paneer, dal, eggs, ya soya chunks lo 💪")

    if deficit.get("calcium", 0) > 300:
        suggestions.append("Calcium ki zaroorat hai — dahi ya milk le lo 🥛")

    if deficit.get("iron", 0) > 5:
        suggestions.append("Iron low hai — palak, chana, ya rajma kha lo 🥬")

    if deficit.get("vitamin_c", 0) > 30:
        suggestions.append("Vitamin C chahiye — guava, orange ya nimbu pani pi lo 🍊")

    if deficit.get("vitamin_b12", 0) > 1:
        suggestions.append("B12 bohot kam — dahi, milk, ya eggs zaroor lo ⚡")

    if deficit.get("fiber", 0) > 10:
        suggestions.append("Fiber badhao — sabzi, salad, ya sprouts add karo 🥗")

    if deficit.get("calories", 0) > 500:
        suggestions.append(f"Abhi {deficit['calories']:.0f} kcal aur chahiye — proper meal lo 🍽️")

    if not suggestions:
        return "Aaj ka nutrition almost complete hai — great job! 🎉"

    header = f"📋 **{current_meal} ke liye suggestions:**\n"
    return header + "\n".join(f"  • {s}" for s in suggestions)
