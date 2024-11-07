import pymysql

# MySQL 연결 함수
def connect_to_database():
    return pymysql.connect(
        user='root',
        passwd='Alsrb0315!',
        host='192.168.127.128',
        db='TESTDB',
        charset='utf8'
    )

# 사용자 이름을 기준으로 알레르기 정보를 삭제하는 함수
def delete_user_by_name(user_name):
    dbConn = connect_to_database()
    cursor = dbConn.cursor()
    
    # DELETE 쿼리
    sql = "DELETE FROM allergy_info WHERE user_name = %s"
    cursor.execute(sql, (user_name,))
    
    dbConn.commit()  # 변경 사항을 저장
    cursor.close()
    dbConn.close()
    
    print(f"{user_name} 님의 알레르기 정보가 삭제되었습니다.")

# 예시 사용
user_name = input("삭제할 사용자 이름을 입력하세요: ")
delete_user_by_name(user_name)
