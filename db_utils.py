import os
from dotenv import load_dotenv
from contextlib import contextmanager
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 환경 변수 로드
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_info(name: str):
    """DB에서 사용자 정보를 가져오는 함수 (예: 체중, 신장, 나이, 성별, 활동 수준)"""
    try:
        # name에 해당하는 사용자 정보 가져오기
        result = supabase.table('user_info').select('weight, height, age, gender, activity_level').eq('name', name).execute()
        user_data = result.data
        print(f"DB에서 조회된 사용자 정보: {user_data}")  # 디버그 출력
        
        if user_data:
            return user_data[0]  # 첫 번째 사용자 데이터 반환
        else:
            print(f"사용자 {name}을 찾을 수 없습니다.")  # 디버그 출력
            return None  # 사용자가 없으면 None 반환
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None
    
# Supabase 클라이언트 초기화
def init_supabase():
    url: str = os.getenv('SUPABASE_URL')
    key: str = os.getenv('SUPABASE_KEY')
    return create_client(url, key)

@contextmanager
def get_db_connection():
    supabase = init_supabase()
    try:
        yield supabase
    except Exception as e:
        st.error(f"데이터베이스 오류: {e}")
        raise e

def get_allergen_risk_level(name, allergen):
    """
    주어진 알레르기 성분의 위험 수준을 반환합니다.
    알레르기 정보가 없으면 None을 반환합니다.
    """
    with get_db_connection() as supabase:
        result = supabase.table('allergy_info')\
            .select('risk_level')\
            .eq('name', name) \
            .eq('allergen', allergen)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['risk_level']
        return None

def get_allergens_risk_levels(name, allergens):
    """
    특정 이름의 여러 알레르기 성분의 위험 수준을 반환하는 함수
    name: 사용자 이름
    allergens: 리스트 형태의 알레르기 성분
    반환: 딕셔너리 {allergen: risk_level}
    """
    if not allergens:
        return {}
    
    with get_db_connection() as supabase:
        result = supabase.table('allergy_info')\
            .select('allergen, risk_level')\
            .eq('name', name)\
            .in_('allergen', allergens)\
            .execute()
        
        return {row['allergen']: row['risk_level'] for row in result.data}

def insert_allergy_info(name, allergen, risk_level):
    """
    알레르기 정보를 데이터베이스에 삽입하거나 업데이트하는 함수
    name: 사용자 이름
    allergen: 알레르기 성분
    risk_level: 위험 수준
    특정 이름과 알레르기 성분이 이미 존재하면 위험 수준만 업데이트됨
    """
    with get_db_connection() as supabase:
        # 기존 데이터 확인
        existing = supabase.table('allergy_info')\
            .select('id')\
            .eq('name', name)\
            .eq('allergen', allergen)\
            .execute()
        
        if existing.data:
            # 기존 데이터가 있으면 업데이트
            result = supabase.table('allergy_info')\
                .update({'risk_level': risk_level})\
                .eq('id', existing.data[0]['id'])\
                .execute()
        else:
            # 새로운 데이터 삽입
            result = supabase.table('allergy_info')\
                .insert({
                    'name': name,
                    'allergen': allergen,
                    'risk_level': risk_level
                })\
                .execute()
        
        return result

    
def delete_allergy_info(name, allergen):
   """
   특정 사용자의 특정 알레르기 정보를 데이터베이스에서 삭제하는 함수
   name: 사용자 이름
   allergen: 삭제할 알레르기 성분
   """
   with get_db_connection() as supabase:
       result = supabase.table('allergy_info')\
           .delete()\
           .eq('name', name)\
           .eq('allergen', allergen)\
           .execute()
       return result


def get_allergy_info_grouped(name):
   """
   특정 사용자의 알레르기 정보를 위험도 그룹별로 분류하여 조회하는 함수
   name: 사용자 이름
   """
   with get_db_connection() as supabase:
       result = supabase.table('allergy_info')\
           .select('allergen, risk_level')\
           .eq('name', name)\
           .order('risk_level')\
           .execute()
       
       # DataFrame으로 변환
       df = pd.DataFrame(result.data)
       
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
   

def insert_user_info(name, weight, height, age, gender, activity_level):
    """
    사용자 정보를 데이터베이스에 삽입하거나 업데이트하는 함수
    동일한 이름이 있다면 정보를 업데이트하고, 없다면 새로 생성합니다.
    
    Parameters:
    - name (str): 사용자 이름
    - weight (int): 체중(kg)
    - height (int): 신장(cm)
    - age (int): 나이
    - gender (str): 성별
    - activity_level (str): 활동 수준
    """
    with get_db_connection() as supabase:
        # 기존 사용자 확인
        existing = supabase.table('user_info')\
            .select('id')\
            .eq('name', name)\
            .execute()
        
        # 업데이트할 데이터 정의
        user_data = {
            'weight': weight,
            'height': height,
            'age': age,
            'gender': gender,
            'activity_level': activity_level
        }
        
        if existing.data:
            # 기존 사용자가 있으면 정보 업데이트
            result = supabase.table('user_info')\
                .update(user_data)\
                .eq('id', existing.data[0]['id'])\
                .execute()
        else:
            # 새로운 사용자면 정보 삽입
            user_data['name'] = name  # 새 사용자 생성 시에만 이름 추가
            result = supabase.table('user_info')\
                .insert(user_data)\
                .execute()
        
        return result