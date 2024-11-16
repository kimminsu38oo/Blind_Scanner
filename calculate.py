
def calculate_bmr(weight, height, age, gender):
    """기초대사량(BMR) 계산 - 해리스-베네딕트 방정식 사용"""
    if gender.lower() == '남성':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:  # 여성
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)


def get_activity_multiplier(activity_level):
    """활동 수준에 따른 곱수 반환"""
    multipliers = {
        '비활동적': 1.2,    # 운동 안함
        '저활동적': 1.375,  # 주 1-3회 운동
        '활동적': 1.55,     # 주 3-5회 운동
        '매우활동적': 1.725,# 주 6-7회 운동
        '극도활동적': 1.9   # 매우 힘든 운동 또는 육체노동
    }
    return multipliers.get(activity_level, 1.2)


def calculate_daily_nutrients(weight, height, age, gender, activity_level):
    """일일 영양소 권장량 계산"""
    
    # 1. 기초대사량 계산
    bmr = calculate_bmr(weight, height, age, gender)
    
    # 2. 활동량 곱수 적용하여 일일 필요 칼로리 계산
    activity_multiplier = get_activity_multiplier(activity_level)
    energy_kcal = bmr * activity_multiplier
    
    # 3. 나트륨 계산 (나이와 활동량 고려)
    if age >= 65:
        sodium = 1500  # mg
    else:
        base_sodium = 2000
        if activity_level in ['매우활동적', '극도활동적']:
            sodium = base_sodium * 1.2
        else:
            sodium = base_sodium
    
    # 4. 당류 계산 (칼로리의 10% 기준)
    sugar = (energy_kcal * 0.10) / 4  # 탄수화물 1g = 4kcal
    
    # 5. 포화지방 계산 (칼로리의 10% 기준)
    saturated_fat = (energy_kcal * 0.10) / 9  # 지방 1g = 9kcal
    
    # 6. 트랜스지방 계산 (칼로리의 1% 미만)
    trans_fat = (energy_kcal * 0.01) / 9
    
    return {
        'energy_kcal': round(energy_kcal, 0),
        'sodium': round(sodium, 0),
        'sugar': round(sugar, 1),
        'saturated_fat': round(saturated_fat, 1),
        'trans_fat': round(trans_fat, 1)
    }




def calculate_daily_nutrient_ratio(selected_nutrients, daily_nutrients):
   """
   섭취한 영양소와 일일 권장 섭취량을 비교하여 비율(%)을 계산하는 함수

   Parameters:
   - selected_nutrients (dict): 섭취한 영양소 정보
   - daily_nutrients (dict): 일일 권장 섭취량 정보

   Returns:
   - dict: 각 영양소별 일일 권장량 대비 섭취 비율(%)
   """
   nutrient_ratios = {}
   
   # 각 영양소별 비율 계산
   for nutrient in ['energy_kcal', 'sodium', 'sugar', 'saturated_fat', 'trans_fat']:
       if selected_nutrients.get(nutrient, 0) == '정보 없음' or daily_nutrients.get(nutrient, 0) == 0:
           nutrient_ratios[nutrient] = 0
       else:
           ratio = (float(selected_nutrients[nutrient]) / float(daily_nutrients[nutrient])) * 100
           nutrient_ratios[nutrient] = round(ratio, 1)  # 소수점 첫째자리까지 반올림
   
   return nutrient_ratios

