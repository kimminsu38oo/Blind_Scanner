import requests
import requests
import json

def get_product_info_by_barcode(barcode, api_key):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/C005/json/1/1/BAR_CD={barcode}"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.content)
        product_info = {
            "PRDLST_NM": data["C005"]["row"][0]["PRDLST_NM"],  # 제품명
            "PRDLST_REPORT_NO": data["C005"]["row"][0]["PRDLST_REPORT_NO"]
        }
        return product_info
    else:
        print("바코드 API 요청 실패:", response.status_code)
        return None



def get_nutrition_info_by_report_no(report_no, api_key):
    
    url = "http://apis.data.go.kr/B553748/CertImgListServiceV3/getCertImgListServiceV3"
    params = {
        'ServiceKey': api_key,
        'prdlstReportNo': report_no,
        'returnType' : 'json',
        'numOfRows' : '1'
    }
    response = requests.get(url, params=params)

    print("\n2. 요청 url: ", response.url)
    if response.status_code == 200:

        data = json.loads(response.content)

        item = data['body']['items']
        if item:
            product_info = {
                "nutrient": item[0]['item']['nutrient'],
                "allergy": item[0]['item']['allergy']
            }
            return product_info
        else:
            print(f"'{report_no}'에 대한 정보가 없습니다.")
            return None
    else:
        print("성분 정보 API 요청 실패:", response.status_code)
        return None
    
