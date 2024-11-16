# product_info.py
import requests
import json
import re

def get_product_info_by_barcode(barcode, api_key):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/C005/json/1/1/BAR_CD={barcode}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 데이터 구조 확인
            if "C005" in data and "row" in data["C005"] and len(data["C005"]["row"]) > 0:
                product_info = {
                    "PRDLST_NM": data["C005"]["row"][0].get("PRDLST_NM", "이름 정보 없음"),  # 제품명
                    "PRDLST_REPORT_NO": data["C005"]["row"][0].get("PRDLST_REPORT_NO", "번호 없음")
                }
                return product_info
            else:
                print("API 응답에 제품 정보가 없습니다.")
                return None
        else:
            print("바코드 API 요청 실패:", response.status_code)
            return None
    except requests.Timeout:
        print("바코드 API 요청 시간이 초과되었습니다.")
        return None
    except requests.ConnectionError:
        print("바코드 API 서버에 연결할 수 없습니다.")
        return None
    except requests.RequestException as e:
        print(f"바코드 API 요청 중 오류 발생: {e}")
        return None


def get_nutrition_info_by_report_no(report_no, api_key):
    url = "http://apis.data.go.kr/B553748/CertImgListServiceV3/getCertImgListServiceV3"
    params = {
        'ServiceKey': api_key,
        'prdlstReportNo': report_no,
        'returnType' : 'json',
        'numOfRows' : '1'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'body' in data and 'items' in data['body'] and len(data['body']['items']) > 0:
                item = data['body']['items'][0]['item']
                # 'nutrient' 필드가 문자열인지 확인
                nutrient_str = item.get('nutrient', "알레르기 정보 없음")
                allergy = item.get('allergy', "알레르기 정보 없음")
                
                # 'nutrient'가 JSON 문자열인지 확인 후 파싱
                if isinstance(nutrient_str, str):
                    nutrient = parse_nutrient_string(nutrient_str)
                else:
                    nutrient = nutrient_str
                
                product_info = {
                    "nutrient": nutrient,
                    "allergy": allergy
                }
                return product_info
            else:
                print(f"'{report_no}'에 대한 정보가 없습니다.")
                return None
        else:
            print("성분 정보 API 요청 실패:", response.status_code)
            return None
    except requests.Timeout:
        print("성분 정보 API 요청 시간이 초과되었습니다.")
        return None
    except requests.ConnectionError:
        print("성분 정보 API 서버에 연결할 수 없습니다.")
        return None
    except requests.RequestException as e:
        print(f"성분 정보 API 요청 중 오류 발생: {e}")
        return None


def parse_nutrient_string(nutrient_str):
    """
    'nutrient' 문자열을 파싱하여 숫자값만 딕셔너리로 변환하는 함수
    필요한 영양성분: 열량, 탄수화물, 단백질, 지방, 나트륨, 포화지방, 당류, 트랜스지방
    """
    nutrient_dict = {}
    key_mapping = {
        "열량": "energy_kcal",
        "탄수화물": "carbohydrates",
        "단백질": "proteins",
        "지방": "fat",
        "나트륨": "sodium",
        "포화지방": "saturated_fat",
        "당류": "sugar",
        "트랜스지방": "trans_fat"
    }
    
    for korean, english in key_mapping.items():
        # 숫자만 추출 (정수 또는 소수점)
        pattern = rf"{korean}\s+([\d,]+(?:\.\d+)?)"
        match = re.search(pattern, nutrient_str)
        if match:
            # 쉼표 제거하고 실수형으로 변환
            value = float(match.group(1).replace(',', ''))
            nutrient_dict[english] = value
        else:
            nutrient_dict[english] = 0  # 또는 'None' 또는 '정보 없음' 선택 가능
    
    return nutrient_dict


def get_nutrient_info(nutrient):
    """
    주요 영양소 정보를 수집하여 하나의 딕셔너리로 반환하는 함수
    
    Parameters:
    - nutrient (dict): 원본 영양소 정보를 담고 있는 딕셔너리
    
    Returns:
    - dict: 주요 영양소 정보만 선별하여 담은 딕셔너리
    """
    return {
        'energy_kcal': nutrient.get('energy_kcal', '정보 없음'),
        'sodium': nutrient.get('sodium', '정보 없음'),
        'saturated_fat': nutrient.get('saturated_fat', '정보 없음'),
        'trans_fat': nutrient.get('trans_fat', '정보 없음'),
        'sugar': nutrient.get('sugar', '정보 없음')
    }