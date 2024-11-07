# allergy_input.py
import streamlit as st
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

# 알레르기 정보를 데이터베이스에 저장하는 함수
def insert_allergy_info(user_name, allergen):
    dbConn = connect_to_database()
    cursor = dbConn.cursor()
    sql = "INSERT INTO allergy_info (user_name, allergen) VALUES (%s, %s)"
    cursor.execute(sql, (user_name, allergen))
    dbConn.commit()
    cursor.close()
    dbConn.close()

# Streamlit 앱 구성
st.title("알레르기 정보 입력")

# 사용자 이름과 알레르기 성분 입력받기
user_name = st.text_input("이름을 입력하세요")
allergen = st.text_input("알레르기 성분을 입력하세요 (예: 땅콩, 우유)")

# 데이터베이스에 저장 버튼
if st.button("알레르기 정보 저장"):
    if user_name and allergen:
        insert_allergy_info(user_name, allergen)
        st.success("알레르기 정보가 데이터베이스에 저장되었습니다!")
    else:
        st.error("이름과 알레르기 성분을 모두 입력해주세요.")
