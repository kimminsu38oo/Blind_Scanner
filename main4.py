from product_info import get_product_info_by_barcode, get_nutrition_info_by_report_no, get_nutrient_info
import os
from dotenv import load_dotenv
import re
from db_utils import get_allergens_risk_levels, get_user_info  # 사용자 정보 가져오는 함수 추가
import sys
from ttsAdvanced import speak_allergen_info, speak_product_info, speak_base_warning, speak_daily_nutrients
from calculate import calculate_daily_nutrients, calculate_daily_nutrient_ratio



def main():
    # 환경 변수 로드
    load_dotenv()
    
    api_key_name = os.getenv('API_KEY_NAME')  # 식품안전나라 API 키
    api_key_detail = os.getenv('API_KEY_DETAIL')  # 성분 정보 API 키
    
    # user 정보
    user_name = "나경훈"  # 고정된 사용자 이름

    # DB에서 사용자 정보 가져오기
    user_info = get_user_info(user_name)
    
    if user_info:
        weight = user_info['weight']
        height = user_info['height']
        age = user_info['age']
        gender = user_info['gender']
        activity_level = user_info['activity_level']
        
        # 일일 영양소 권장량 계산
        daily_nutrients = calculate_daily_nutrients(weight, height, age, gender, activity_level)
        
        # 결과 출력
        print(f"\n=== {user_name}의 일일 영양소 권장량 ===")
        print(f"칼로리: {daily_nutrients['energy_kcal']} kcal")
        print(f"나트륨: {daily_nutrients['sodium']} mg")
        print(f"첨가당: {daily_nutrients['sugar']} g")
        print(f"포화지방: {daily_nutrients['saturated_fat']} g")
        print(f"트랜스지방: {daily_nutrients['trans_fat']} g")
    else:
        print(f"{user_name}의 정보를 찾을 수 없습니다。")
    


        

    while True:
        # 바코드 입력 받기
        barcode = input("바코드를 입력하세요: ").strip()
        
        # 바코드 검증 (숫자만 허용)
        if not barcode.isdigit():
            print("유효한 바코드를 입력해주세요. (숫자만 허용)")
            sys.exit(1)
        
        # 1. 바코드를 통해 제품 정보 가져오기
        product_info = get_product_info_by_barcode(barcode, api_key_name)

        if product_info is None: # 1. 예외처리 : 바코드 정보를 찾지 못한 경우
            print("제품 정보를 찾을 수 없습니다. 바코드를 다시 확인해주세요.")
            sys.exit(1)

        # 제품 정보에서 (이름 & 제품 번호) 추출
        product_name = product_info.get("PRDLST_NM", "이름 정보 없음")
        report_no = product_info.get("PRDLST_REPORT_NO", "번호 없음")

        # 콘솔에 제품 이름 및 번호 출력
        print("1. 제품 이름:", product_name)
        print("2. 제품 번호:", report_no)
        


        # 2. 제품 번호를 이용하여 (알러지 & 영양 정보) 가져오기
        detail_info = get_nutrition_info_by_report_no(report_no, api_key_detail)

        if detail_info is None: # 2. 예외처리 : 바코드를 통해 영양 정보를 찾을 수 없음.
            print("영양 성분 정보를 찾을 수 없습니다.")
            sys.exit(1)

        nutrient = detail_info.get("nutrient", {})
        allergy_info = detail_info.get("allergy", "알레르기 정보 없음")
        

        # 제품명, 영양 정보 출력 --> 이부분 제품 명만 출력하도록 변경
        speak_product_info(barcode, product_name, nutrient) 

        # 열량, 나트륨, 포화지방, 당류, 트랜스지방 가져오는 함수
        selected_nutrients = get_nutrient_info(nutrient)

        print("=== 선택된 제품의 영양성분 ===")
        print(f"열량: {selected_nutrients['energy_kcal']}kcal")
        print(f"나트륨: {selected_nutrients['sodium']}mg")
        print(f"당류: {selected_nutrients['sugar']}g")
        print(f"포화지방: {selected_nutrients['saturated_fat']}g")
        print(f"트랜스지방: {selected_nutrients['trans_fat']}g")
        print("===========================")


        # 각각의 비율을 구하는 함수
        nutrient_ratios = calculate_daily_nutrient_ratio(selected_nutrients, daily_nutrients) # selected / daily * 100 = 비율
        

        
        print("=== 일일 영양성분 섭취 비율 ===")
        print(f"열량: {nutrient_ratios['energy_kcal']}%")
        print(f"나트륨: {nutrient_ratios['sodium']}%")
        print(f"당류: {nutrient_ratios['sugar']}%")
        print(f"포화지방: {nutrient_ratios['saturated_fat']}%")
        print(f"트랜스지방: {nutrient_ratios['trans_fat']}%")
        print("===========================")

        # 출력
        speak_daily_nutrients(nutrient_ratios)
        




        if allergy_info == "알레르기 정보 없음":
            print("\n4. 알레르기 정보: 알레르기 정보가 없습니다.")
            sys.exit(1)

        # 알러지 정보가 문자열로 제공된다고 가정하고, 쉼표 또는 세미콜론으로 분리
        allergens = re.split(r'[;,]+', allergy_info)
        allergens = [allergen.strip() for allergen in allergens if allergen.strip()]

        if allergens:
            # 데이터베이스에 등록된 알레르기 성분과 비교
            risk_levels = get_allergens_risk_levels(user_name, allergens)
            print(allergens)

            # 등록된 알레르기 성분만 필터링
            registered_allergens = {allergen: risk_levels[allergen] for allergen in allergens if allergen in risk_levels}
            
            if registered_allergens:
                print("\n4. 알레르기 성분이 포함되어 있습니다")
                speak_base_warning()

                allergy_comments = []
                for allergen, risk_level in registered_allergens.items():
                    if risk_level == "High Risk Group":
                        comment = f" - {allergen}: 섭취하지 마십시오."
                        allergy_comments.append(comment)
                    elif risk_level == "Risk Group":
                        comment = f" - {allergen}: 주의해 주십시오"
                        allergy_comments.append(comment)
                    elif risk_level == "Caution Group":
                        comment = f" - {allergen}: 참고해 주십시오"
                        allergy_comments.append(comment)
                    else:
                        comment = f" - {allergen}: 알 수 없는 위험 수준."
                        allergy_comments.append(comment)

                    speak_allergen_info(allergen, risk_level)

                for comment in allergy_comments:
                        print(comment)
            else:
                print("\n4. 알레르기 정보: 데이터베이스에 등록된 알레르기 성분이 없습니다.")
        else:
            print("\n4. 알레르기 정보: 알레르기 성분 정보가 없습니다.")


if __name__ == "__main__":
    main()
