# db_utils.py
import pymysql
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import streamlit as st

# 환경 변수 로드
load_dotenv()

def connect_to_database():
    return pymysql.connect(
        user=os.getenv('DB_USER'),
        passwd=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        db=os.getenv('DB_NAME'),
        charset=os.getenv('DB_CHARSET')
    )

@contextmanager
def get_db_cursor(cursor_type=pymysql.cursors.DictCursor):
    connection = connect_to_database()
    try:
        cursor = connection.cursor(cursor_type)
        yield cursor
        connection.commit()
    except pymysql.MySQLError as e:
        st.error(f"데이터베이스 오류: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def get_allergen_risk_level(allergen):
    """
    주어진 알레르기 성분의 위험 수준을 반환합니다.
    알레르기 정보가 없으면 None을 반환합니다.
    """
    with get_db_cursor() as cursor:
        sql = "SELECT risk_level FROM allergy_info WHERE allergen = %s"
        cursor.execute(sql, (allergen,))
        result = cursor.fetchone()
        if result:
            return result['risk_level']
        else:
            return None

def get_allergens_risk_levels(allergens):
    """
    여러 알레르기 성분의 위험 수준을 반환하는 함수
    allergens: 리스트 형태의 알레르기 성분
    반환: 딕셔너리 {allergen: risk_level}
    """
    if not allergens:
        return {}
    
    with get_db_cursor() as cursor:
        # SQL IN 절을 위해 포맷 문자열 생성
        format_strings = ','.join(['%s'] * len(allergens))
        sql = f"SELECT allergen, risk_level FROM allergy_info WHERE allergen IN ({format_strings})"
        cursor.execute(sql, tuple(allergens))
        results = cursor.fetchall()
        risk_levels = {row['allergen']: row['risk_level'] for row in results}
        return risk_levels
