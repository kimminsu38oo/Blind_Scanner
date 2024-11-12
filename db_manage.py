# db_manage.py
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from contextlib import contextmanager
from db_utils import get_db_cursor
import re

# 환경 변수 로드
load_dotenv()

# 알레르기 정보 삽입 함수
def insert_allergy_info(allergen, risk_level):
    with get_db_cursor() as cursor:
        sql = """
            INSERT INTO allergy_info (allergen, risk_level) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE risk_level = VALUES(risk_level)
        """
        cursor.execute(sql, (allergen, risk_level))

# 알레르기 정보 삭제 함수
def delete_allergy_info(allergen):
    with get_db_cursor() as cursor:
        sql = "DELETE FROM allergy_info WHERE allergen = %s"
        cursor.execute(sql, (allergen,))

# 알레르기 정보 그룹 조회 함수
def get_allergy_info_grouped():
    with get_db_cursor() as cursor:
        sql = "SELECT allergen, risk_level FROM allergy_info ORDER BY risk_level"
        cursor.execute(sql)
        result = cursor.fetchall()
    
    # DataFrame으로 변환하여 그룹별로 나눔
    df = pd.DataFrame(result)
    if not df.empty:
        grouped = {
            "High Risk Group": df[df['risk_level'] == 'High Risk Group'],
            "Risk Group": df[df['risk_level'] == 'Risk Group'],
            "Caution Group": df[df['risk_level'] == 'Caution Group']
        }
    else:
        grouped = {
            "High Risk Group": pd.DataFrame(),
            "Risk Group": pd.DataFrame(),
            "Caution Group": pd.DataFrame()
        }
    return grouped

# 입력값 검증 함수
def validate_allergen(allergen):
    # 허용할 문자 패턴 정의 (알파벳, 한글, 공백, 하이픈, 슬래시)
    pattern = re.compile(r'^[A-Za-z가-힣\s\-\/]+$')
    return bool(pattern.match(allergen))

# 페이지 새로고침을 위한 세션 상태 초기화
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# Streamlit 앱 구성
st.title("알레르기 정보 관리")

# **1. 알레르기 정보 입력 섹션**
st.subheader("알레르기 정보 입력")
allergen = st.text_input("알레르기 성분을 입력하세요 (예: 땅콩, 우유)")
risk_level = st.selectbox("위험 그룹을 선택하세요", ("High Risk Group", "Risk Group", "Caution Group"))

if st.button("알레르기 정보 추가"):
    if allergen and risk_level:
        if validate_allergen(allergen):
            insert_allergy_info(allergen, risk_level)
            st.success("알레르기 정보가 추가되었습니다!")
            # 데이터 업데이트를 위해 페이지 상태 변경
            st.session_state.refresh = not st.session_state.refresh
        else:
            st.error("알레르기 성분에 유효하지 않은 문자가 포함되어 있습니다.")
    else:
        st.error("알레르기 성분과 위험 그룹을 모두 입력해주세요.")

st.markdown("---")

# **2. 저장된 알레르기 정보 표시 및 그룹별 출력**
st.subheader("저장된 알레르기 정보 목록")

# 그룹별로 알레르기 정보 가져오기
allergy_data_grouped = get_allergy_info_grouped()

# 그룹별로 테이블 및 삭제 버튼 표시
for group, data in allergy_data_grouped.items():
    st.write(f"### {group}")
    if not data.empty:
        for index, row in data.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(row['allergen'])
            with col2:
                # 고유한 키를 생성하기 위해 그룹과 인덱스를 포함
                button_key = f"delete_{group}_{index}"
                if st.button("삭제", key=button_key):
                    delete_allergy_info(row['allergen'])
                    st.success(f"{row['allergen']} 항목이 삭제되었습니다!")
                    # 데이터 업데이트를 위해 페이지 상태 변경
                    st.session_state.refresh = not st.session_state.refresh
    else:
        st.write("해당 그룹에 저장된 알레르기 정보가 없습니다.")
