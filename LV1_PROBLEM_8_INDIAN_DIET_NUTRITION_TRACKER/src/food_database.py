"""
Indian Food Nutrition Database
Loads curated Indian foods and provides search/filter capabilities.
"""
import json
import os
from typing import List, Dict, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "indian_foods.json")

NUTRIENT_UNITS = {
    "calories": "kcal",
    "protein": "g",
    "carbs": "g",
    "fats": "g",
    "fiber": "g",
    "calcium": "mg",
    "iron": "mg",
    "zinc": "mg",
    "vitamin_a": "mcg",
    "vitamin_b12": "mcg",
    "vitamin_c": "mg",
    "vitamin_d": "mcg",
}

NUTRIENT_DISPLAY = {
    "calories": "Calories",
    "protein": "Protein",
    "carbs": "Carbs",
    "fats": "Fats",
    "fiber": "Fiber",
    "calcium": "Calcium",
    "iron": "Iron",
    "zinc": "Zinc",
    "vitamin_a": "Vitamin A",
    "vitamin_b12": "Vitamin B12",
    "vitamin_c": "Vitamin C",
    "vitamin_d": "Vitamin D",
}


def load_foods() -> List[Dict]:
    """Load all foods from the JSON database."""
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data["foods"]


def get_food_by_id(food_id: str) -> Optional[Dict]:
    """Get a specific food by its ID."""
    foods = load_foods()
    for food in foods:
        if food["id"] == food_id:
            return food
    return None


def search_foods(query: str) -> List[Dict]:
    """Search foods by name or category (case-insensitive)."""
    foods = load_foods()
    query_lower = query.lower().strip()
    if not query_lower:
        return foods

    results = []
    for food in foods:
        if (
            query_lower in food["name"].lower()
            or query_lower in food["category"].lower()
            or query_lower in food["id"].lower()
        ):
            results.append(food)
    return results


def get_categories() -> List[str]:
    """Get all unique food categories."""
    foods = load_foods()
    categories = sorted(set(food["category"] for food in foods))
    return categories


def get_foods_by_category(category: str) -> List[Dict]:
    """Get all foods in a specific category."""
    foods = load_foods()
    return [f for f in foods if f["category"] == category]


def get_top_foods_for_nutrient(nutrient: str, top_n: int = 5) -> List[Dict]:
    """Get top N foods highest in a specific nutrient (per serving)."""
    foods = load_foods()
    sorted_foods = sorted(
        foods, key=lambda f: f["nutrients"].get(nutrient, 0), reverse=True
    )
    return sorted_foods[:top_n]
