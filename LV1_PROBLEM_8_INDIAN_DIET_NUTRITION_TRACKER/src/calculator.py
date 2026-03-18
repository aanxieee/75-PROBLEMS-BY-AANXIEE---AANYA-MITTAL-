"""
Nutrition Calculator
Personalized daily targets using Mifflin-St Jeor equation.
BMR → TDEE → Macro split → Micronutrient RDA.
"""
from typing import Dict

# Activity level multipliers for TDEE
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,        # Little/no exercise, desk job
    "light": 1.375,          # Light exercise 1-3 days/week
    "moderate": 1.55,        # Moderate exercise 3-5 days/week
    "active": 1.725,         # Hard exercise 6-7 days/week
    "very_active": 1.9,      # Very hard exercise, physical job
}

# Goal calorie adjustments
GOAL_ADJUSTMENTS = {
    "lose": -500,       # ~0.5 kg/week loss
    "mild_lose": -250,  # ~0.25 kg/week loss
    "maintain": 0,
    "mild_gain": 250,
    "gain": 500,
}

# RDA values by gender (daily recommended intake)
# Sources: ICMR-NIN 2020 RDA for Indians
MICRONUTRIENT_RDA = {
    "male": {
        "fiber": 38,          # g
        "calcium": 1000,      # mg
        "iron": 17,           # mg (ICMR for Indian males)
        "zinc": 12,           # mg
        "vitamin_a": 1000,    # mcg RAE
        "vitamin_b12": 2.4,   # mcg
        "vitamin_c": 80,      # mg
        "vitamin_d": 15,      # mcg (600 IU)
    },
    "female": {
        "fiber": 25,          # g
        "calcium": 1000,      # mg
        "iron": 21,           # mg (ICMR — higher for Indian females)
        "zinc": 10,           # mg
        "vitamin_a": 840,     # mcg RAE
        "vitamin_b12": 2.4,   # mcg
        "vitamin_c": 65,      # mg
        "vitamin_d": 15,      # mcg (600 IU)
    },
}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation for BMR.
    Male:   10 × weight(kg) + 6.25 × height(cm) - 5 × age - 5  (actually it's + 5 for males)
    Female: 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161
    """
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "male":
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_targets(weight_kg: float, height_cm: float, age: int,
                      gender: str, activity_level: str, goal: str) -> Dict:
    """
    Calculate all daily nutrient targets.
    Returns dict with target values for all 12 tracked nutrients.
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    # Apply goal adjustment
    calorie_target = tdee + GOAL_ADJUSTMENTS.get(goal, 0)
    calorie_target = max(calorie_target, 1200)  # Safety floor

    # Macro split based on goal
    if goal in ("lose", "mild_lose"):
        # Higher protein for satiety during deficit
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
    elif goal in ("gain", "mild_gain"):
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25
    else:
        protein_pct, carb_pct, fat_pct = 0.25, 0.50, 0.25

    # Convert to grams (protein & carbs = 4 cal/g, fats = 9 cal/g)
    protein_g = round((calorie_target * protein_pct) / 4, 1)
    carbs_g = round((calorie_target * carb_pct) / 4, 1)
    fats_g = round((calorie_target * fat_pct) / 9, 1)

    # Get micronutrient RDAs
    gender_key = "male" if gender == "male" else "female"
    micros = MICRONUTRIENT_RDA[gender_key]

    return {
        "calories": round(calorie_target, 0),
        "protein": protein_g,
        "carbs": carbs_g,
        "fats": fats_g,
        "fiber": micros["fiber"],
        "calcium": micros["calcium"],
        "iron": micros["iron"],
        "zinc": micros["zinc"],
        "vitamin_a": micros["vitamin_a"],
        "vitamin_b12": micros["vitamin_b12"],
        "vitamin_c": micros["vitamin_c"],
        "vitamin_d": micros["vitamin_d"],
        # Meta info
        "_bmr": bmr,
        "_tdee": tdee,
        "_calorie_adjustment": GOAL_ADJUSTMENTS.get(goal, 0),
    }


def nutrient_percentage(consumed: float, target: float) -> float:
    """Calculate percentage of target consumed."""
    if target <= 0:
        return 0
    return round(min((consumed / target) * 100, 150), 1)  # Cap at 150%


def get_deficit(consumed: Dict, targets: Dict) -> Dict:
    """
    Get deficit/surplus for each nutrient.
    Positive = still need more, Negative = exceeded target.
    """
    nutrients = ["calories", "protein", "carbs", "fats", "fiber",
                 "calcium", "iron", "zinc", "vitamin_a", "vitamin_b12",
                 "vitamin_c", "vitamin_d"]
    deficit = {}
    for n in nutrients:
        target = targets.get(n, 0)
        current = consumed.get(n, 0)
        deficit[n] = round(target - current, 1)
    return deficit
