# main4.py
from product_info import get_product_info_by_barcode, get_nutrition_info_by_report_no
import os
from dotenv import load_dotenv
import re
from db_utils import get_allergens_risk_levels
import sys

def main():
    # 환경 변수 로드
    load_dotenv()
    
    api_key_name = os.getenv('API_KEY_NAME')  # 식품안전나라 API 키
    api_key_detail = os.getenv('API_KEY_DETAIL')  # 성분 정보 API 키
    
    # 바코드 입력 받기
    barcode = input("바코드를 입력하세요: ").strip()
    
    # 바코드 검증 (숫자만 허용)
    if not barcode.isdigit():
        print("유효한 바코드를 입력해주세요. (숫자만 허용)")
        sys.exit(1)
    
    # 1. 바코드를 통해 제품 정보 가져오기
    product_info = get_product_info_by_barcode(barcode, api_key_name)
    if product_info:
        # 제품 정보에서 (이름 & 제품 번호) 추출
        product_name = product_info.get("PRDLST_NM", "이름 정보 없음")
        report_no = product_info.get("PRDLST_REPORT_NO", "번호 없음")
        
        # 콘솔에 제품 이름 및 번호 출력
        print("1. 제품 이름:", product_name)
        print("2. 제품 번호:", report_no)
        
        # 2. 제품 번호를 이용하여 (알러지 & 영양 정보) 가져오기
        detail_info = get_nutrition_info_by_report_no(report_no, api_key_detail)
        
        if detail_info:
            nutrient = detail_info.get("nutrient", {})
            allergy_info = detail_info.get("allergy", "알레르기 정보 없음")
            
            # 3. 영양 정보 출력
            print("\n3. 영양 정보:")
            print(f"   - 열량: {nutrient.get('energy_kcal', '정보 없음')} kcal")
            print(f"   - 탄수화물: {nutrient.get('carbohydrates', '정보 없음')} g")
            print(f"   - 단백질: {nutrient.get('proteins', '정보 없음')} g")
            print(f"   - 지방: {nutrient.get('fat', '정보 없음')} g")
            
            # 4. 알레르기 정보 분석 및 데이터베이스와 비교
            if allergy_info != "알레르기 정보 없음":
                # 알러지 정보가 문자열로 제공된다고 가정하고, 쉼표 또는 세미콜론으로 분리
                allergens = re.split(r'[;,]+', allergy_info)
                allergens = [allergen.strip() for allergen in allergens if allergen.strip()]
                
                if allergens:
                    # 데이터베이스에 등록된 알레르기 성분과 비교
                    risk_levels = get_allergens_risk_levels(allergens)
                    
                    # 등록된 알레르기 성분만 필터링
                    registered_allergens = {allergen: risk_levels[allergen] for allergen in allergens if allergen in risk_levels}
                    
                    if registered_allergens:
                        print("\n4. 알레르기 정보:")
                        for allergen, risk_level in registered_allergens.items():
                            if risk_level == "High Risk Group":
                                print(f" - {allergen}: 주의! 고위험 알레르기 성분이 포함되어 있습니다.")
                            elif risk_level == "Risk Group":
                                print(f" - {allergen}: 주의! 위험 알레르기 성분이 포함되어 있습니다.")
                            elif risk_level == "Caution Group":
                                print(f" - {allergen}: 주의! 주의가 필요한 알레르기 성분이 포함되어 있습니다.")
                            else:
                                print(f" - {allergen}: 알 수 없는 위험 수준.")
                    else:
                        print("\n4. 알레르기 정보: 데이터베이스에 등록된 알레르기 성분이 없습니다.")
                else:
                    print("\n4. 알레르기 정보: 알레르기 성분 정보가 없습니다.")
            else:
                print("\n4. 알레르기 정보: 알레르기 정보가 없습니다.")
        else:
            print("영양 성분 정보를 찾을 수 없습니다.")
    else:
        print("제품 정보를 찾을 수 없습니다. 바코드를 다시 확인해주세요.")

if __name__ == "__main__":
    main()
