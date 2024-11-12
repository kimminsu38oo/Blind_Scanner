import requests

def get_raw_material(product_name, start_idx=1, end_idx=5):
    key_id = "b0db4232c70c49289cd0"  # 발급받은 유효한 인증키로 교체
    service_id = "C002"  # 실제 서비스명으로 설정
    data_type = "json"  # JSON 형식으로 요청
    base_url = f"http://openapi.foodsafetykorea.go.kr/api/{key_id}/{service_id}/{data_type}/{start_idx}/{end_idx}"

    # 요청 파라미터 설정
    params = {
        "PRDLST_NM": product_name  # 제품명으로 검색
    }

    # API 호출
    response = requests.get(base_url, params=params)

    # 응답 상태 코드 확인
    print("응답 상태 코드:", response.status_code)
    print("응답 내용:", response.text)  # 전체 응답 내용 출력

    if response.status_code == 200:
        try:
            data = response.json()
            
            # JSON 데이터 구조에 맞춰 'row' 키로 접근
            if service_id in data and 'row' in data[service_id]:
                items = data[service_id]['row']
                
                # 제품명과 일치하는 원재료 정보만 출력
                print(f"제품명 '{product_name}'의 원재료 목록:")
                for item in items:
                    if item.get("PRDLST_NM") == product_name:
                        raw_material = item.get("RAWMTRL_NM", "정보 없음")
                        print(raw_material)
                        break
                else:
                    print(f"'{product_name}'에 대한 원재료 정보를 찾을 수 없습니다.")
            else:
                print("데이터를 찾을 수 없습니다.")
        except ValueError:
            print("JSON 형식의 응답이 아닙니다.")
    else:
        print("API 요청 실패:", response.status_code)

# 예시 실행
get_raw_material("여자앤석류")  # 원하는 제품명을 넣어 실행

#get_raw_material("제품명", start_idx=21, end_idx=50)  # 최대 10개의 데이터 항목 요청
