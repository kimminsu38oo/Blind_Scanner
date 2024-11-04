from product_info import get_product_info_by_barcode, get_nutrition_info_by_name, extract_nutrition_info

def main():
    api_key_barcode = "b0db4232c70c49289cd0"  # 바코드 API 키
    api_key_nutrition = "CrOgKxzLcyAYCGAlCDoJfJM0LUej6T6uqJt1qAB4ATTuq3QDj0duWJORAJa2OZ7u2joSrqOoramsXby+41Ryzg=="  # 성분 API 키
    
    # 바코드 입력 받기
    barcode = input("바코드를 입력하세요: ")

    # 1. 바코드를 통해 제품 정보 가져오기
    product_info = get_product_info_by_barcode(barcode, api_key_barcode)
    if product_info:
        # 제품 정보에서 이름 추출
        product_name = product_info.get("PRDLST_NM", "이름 정보 없음")
        
        # 콘솔에 제품 이름 출력
        print("제품 이름:", product_name)

        # 2. 제품 이름을 이용하여 영양 성분 정보 가져오기
        nutrition_info = get_nutrition_info_by_name(product_name, api_key_nutrition)
        if nutrition_info:
            # 영양 성분 정보 추출 및 출력
            nutrition_details = extract_nutrition_info(nutrition_info)
            print("영양 성분 정보:", nutrition_details)
        else:
            print("영양 성분 정보를 찾을 수 없습니다.")
    else:
        print("제품 정보를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
