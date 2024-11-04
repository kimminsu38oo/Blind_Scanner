import requests
import xml.etree.ElementTree as ET

# 1. 바코드를 통해 제품 정보 가져오기
def get_product_info_by_barcode(barcode, api_key):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/C005/xml/1/1/BAR_CD={barcode}"
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        product_info = {
            "PRDLST_NM": root.find(".//PRDLST_NM").text if root.find(".//PRDLST_NM") is not None else None,
            "PRDLST_REPORT_NO": root.find(".//PRDLST_REPORT_NO").text if root.find(".//PRDLST_REPORT_NO") is not None else None,
        }
        return product_info
    else:
        print("바코드 API 요청 실패:", response.status_code)
        return None

# 2. 제품 이름으로 영양 성분 정보 가져오기
def get_nutrition_info_by_name(product_name, api_key):
    url = 'http://api.data.go.kr/openapi/tn_pubr_public_nutri_process_info_api'
    page_no = 1
    found_info = None

    while not found_info:
        params = {
            'serviceKey': api_key,
            'numOfRows': '100',
            'pageNo': str(page_no),
            'type': 'xml'
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # 각 페이지에서 모든 item을 탐색
            for item in root.findall(".//item"):
                food_name = item.find("foodNm").text
                if product_name in food_name:  # 부분 문자열로 제품 이름 일치 확인
                    found_info = {
                        "foodNm": food_name,
                        "enerc": item.find("enerc").text,
                        "prot": item.find("prot").text,
                        "fatce": item.find("fatce").text,
                        "chocdf": item.find("chocdf").text,
                        "nat": item.find("nat").text,
                    }
                    break

            # 데이터가 없으면 루프 종료
            if not root.findall(".//item"):
                print("해당 이름의 영양 성분 정보를 찾을 수 없습니다.")
                break

            page_no += 1  # 다음 페이지로 이동
        else:
            print("성분 정보 API 요청 실패:", response.status_code)
            break

    return found_info



# 3. 영양 성분 정보 형식화
def extract_nutrition_info(nutrition_info):
    return (f"상품명: {nutrition_info['foodNm']}\n"
            f"에너지: {nutrition_info['enerc']} kcal\n"
            f"단백질: {nutrition_info['prot']} g\n"
            f"지방: {nutrition_info['fatce']} g\n"
            f"탄수화물: {nutrition_info['chocdf']} g\n"
            f"나트륨: {nutrition_info['nat']} mg")
