def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor
    if gender.lower() in ("male", "m"):
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

def calculate_tdee(bmr: float, activity: float) -> float:
    return bmr * activity

def calculate_macros(weight: float, height: float, age: int, gender: str, activity: float, goal: str):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)

    if goal == "lose":
        target_cal = tdee * 0.8
    elif goal == "gain":
        target_cal = tdee * 1.15
    else:
        target_cal = tdee

    protein_g = round(weight * 2)  # 2 g / kg
    fat_g = round(weight * 1)      # 1 g / kg
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    carbs_cal = max(0, target_cal - protein_cal - fat_cal)
    carbs_g = round(carbs_cal / 4) if carbs_cal > 0 else 0

    return {
        "calories": round(target_cal),
        "protein": protein_g,
        "fat": fat_g,
        "carbs": carbs_g,
    }
