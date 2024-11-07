import pymysql
from product_info import get_product_info_by_barcode, get_nutrition_info_by_report_no

# MySQL 연결 함수
def connect_to_database():
    return pymysql.connect(
        user='root',
        passwd='Alsrb0315!',
        host='192.168.127.128',
        db='TESTDB',
        charset='utf8'
    )

# 사용자의 알레르기 정보를 가져오는 함수
def get_user_allergens(user_name):
    dbConn = connect_to_database()
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT allergen FROM allergy_info WHERE user_name = %s"
    cursor.execute(sql, (user_name,))
    result = cursor.fetchall()
    cursor.close()
    dbConn.close()
    
    return [item['allergen'] for item in result]

# 알레르기 성분 비교 함수
def check_allergens_in_product(user_allergens, product_allergens):
    # 제품의 알레르기 성분을 콤마(,)로 분리하여 리스트로 변환
    product_allergens_list = [allergen.strip() for allergen in product_allergens.split(',')]
    
    # 사용자 알레르기 성분과 제품의 알레르기 성분을 비교
    matched_allergens = set(user_allergens) & set(product_allergens_list)
    
    if matched_allergens:
        print(f"경고: 제품에 알레르기 성분이 포함되어 있습니다! {', '.join(matched_allergens)}")
    else:
        print("알레르기 성분이 포함되지 않았습니다. 안전하게 섭취할 수 있습니다.")

def main():
    # 사용자 이름 입력받기 (Streamlit에서 입력받았다고 가정)
    user_name = input("사용자 이름을 입력하세요: ")
    
    # 사용자의 알레르기 정보 가져오기
    user_allergens = get_user_allergens(user_name)
    if not user_allergens:
        print(f"{user_name} 님의 알레르기 정보가 데이터베이스에 없습니다.")
        return

    # 바코드 입력받기
    barcode = input("바코드를 입력하세요: ")

    # API 키 설정
    api_key_name = "b0db4232c70c49289cd0"
    api_key_detail = "oqdC/qEnEV/uF3Vy2pVZd4qFqZQTJkEVnv4wvLJIP/adzKf/BOn5/zQSQ/g0mEV5s53E7bSwXJ5wz0V8UNbGlw=="

    # 제품 정보 가져오기
    product_info = get_product_info_by_barcode(barcode, api_key_name)
    if product_info:
        product_name = product_info.get("PRDLST_NM", "이름 정보 없음")
        report_no = product_info.get("PRDLST_REPORT_NO", "번호 없음")
        
        print("제품 이름:", product_name)

        detail_info = get_nutrition_info_by_report_no(report_no, api_key_detail)
        
        if detail_info:
            product_allergens = detail_info.get("allergy", "알러지 정보 없음")
            check_allergens_in_product(user_allergens, product_allergens)
        else:
            print("영양 성분 정보를 찾을 수 없습니다.")
    else:
        print("제품 정보를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
