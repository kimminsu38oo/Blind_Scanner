"""
Directory Structure:
sound_cache/
├── daily_ratio/          # 일일 섭취 비율 음성 캐시 (숫자는 섭취 비율을 나타냄)
│   └── *.mp3            # 예: 167805400.mp3 - 167% 섭취 비율을 의미
│
├── ingredients/          # 알레르기 성분 음성 캐시
│   └── *.mp3            # 알레르기 성분명 (예: chicken.mp3)
│
├── product/             # 제품 정보 음성 캐시
│   └── *.mp3            # 제품 바코드 기반 파일명
│
└── warnings/            # 위험 수준 경고 음성
   ├── base_warning.mp3 # 기본 경고
   ├── caution.mp3      # 주의 
   ├── high_risk.mp3    # 고위험
   └── risk.mp3         # 위험

참고: daily_ratio의 파일명에서 숫자는 백분율을 나타냄 (소수점 제외)
예시) 167805400.mp3 = 167% 섭취 비율
"""

import boto3
import os
from playsound import playsound

import subprocess
import platform


aws_access_key: str = os.getenv('AWS_ACCESS_KEY')
aws_secret_key: str = os.getenv('AWS_SECRET_KEY')



def play_audio(file_path):
    """
    플랫폼에 따라 적절한 오디오 플레이어를 사용하여 음성 파일을 재생합니다.
    """
    system = platform.system().lower()
    
    if system == 'linux':
        if file_path.lower().endswith('.mp3'):
            # MP3 파일은 mpg123로 재생
            try:
                subprocess.run(['mpg123', '-q', file_path], check=True)
            except subprocess.SubprocessError as e:
                print(f"mpg123 재생 실패: {str(e)}")
                print("mpg123가 설치되어 있는지 확인하세요: sudo apt-get install mpg123")
        else:
            # 그 외 파일은 aplay로 재생
            try:
                subprocess.run(['aplay', '-q', file_path], check=True)
            except subprocess.SubprocessError as e:
                print(f"aplay 재생 실패: {str(e)}")
                print("ALSA가 설치되어 있는지 확인하세요: sudo apt-get install alsa-utils")
    else:
        # 윈도우 환경에서는 기존 playsound 사용
        from playsound import playsound
        playsound(file_path)

def text_to_speak_adv(audio_file_name, text, category):
    """
    텍스트를 음성으로 변환하고 캐시하여 재생하는 함수
    """
    # 카테고리별 캐시 디렉토리 설정
    cache_dir = "sound_cache"
    category_dir = os.path.join(cache_dir, category)
    
    # 디렉토리가 없으면 생성 (권한 설정 포함)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, mode=0o755)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir, mode=0o755)
    
    # 캐시된 파일의 전체 경로
    output = os.path.join(category_dir, audio_file_name)
    
    try:
        # 캐시된 파일이 있는지 확인
        if os.path.exists(output):
            print(f"캐시된 파일 {audio_file_name} 사용")
            play_audio(output)
            return
        
        # 캐시된 파일이 없는 경우 API 호출
        print(f"새로운 음성 파일 생성: {audio_file_name}")
        polly_client = boto3.Session(
            aws_access_key_id=aws_access_key,                     
            aws_secret_access_key=aws_secret_key,
            region_name='us-east-1').client('polly')

        response = polly_client.synthesize_speech(
            VoiceId='Seoyeon',
            OutputFormat='mp3', 
            Text = text,
            Engine = 'neural',
            LanguageCode='ko-KR'
        )

        # 새로운 파일 저장 (권한 설정 포함)
        with open(output, 'wb') as file:
            file.write(response['AudioStream'].read())
        os.chmod(output, 0o644)  # 파일 권한 설정
        
        # 생성된 파일 재생
        play_audio(output)
        
    except Exception as e:
        print(f"음성 생성 또는 재생 중 오류 발생: {str(e)}")
        # 에러 발생 시 캐시 파일 정리
        if os.path.exists(output) and os.path.getsize(output) == 0:
            os.remove(output)



def speak_product_info(barcode, product_name, nutrient):
    # 기본 제품 정보 구성
    product_text = f"제품 이름 {product_name}"

    # product 디렉토리에 저장하고 재생
    audio_file_name = f"{barcode}_product.mp3"

    text_to_speak_adv(audio_file_name, product_text, "product")


def speak_daily_nutrients(nutrient_ratios):
    """
    일일 영양소 섭취 비율을 음성으로 변환하는 함수
    
    Parameters:
    - nutrient_ratios: 각 영양소의 일일 섭취 비율(%)을 담은 딕셔너리
    
    """
    # 영양소 비율 텍스트 구성
    daily_text = "일일 권장 섭취 비율은 "

    # 각 영양소 비율 추출 (소수점 제거를 위해 정수 변환)
    energy_ratio = int(nutrient_ratios.get('energy_kcal', 0))
    sodium_ratio = int(nutrient_ratios.get('sodium', 0))
    sugar_ratio = int(nutrient_ratios.get('sugar', 0))
    saturated_ratio = int(nutrient_ratios.get('saturated_fat', 0))
    trans_ratio = int(nutrient_ratios.get('trans_fat', 0))

    # 모든 값이 0인지 체크
    if energy_ratio == 0 and sodium_ratio == 0 and sugar_ratio == 0 and saturated_ratio == 0 and trans_ratio == 0:
        daily_text = "0 칼로리입니다"
        file_name = "0000000000.mp3"
    else:
        # 파일명 구성 (비율을 2자리 숫자로 변환)
        file_name = f"{energy_ratio:02d}{sodium_ratio:02d}{sugar_ratio:02d}{saturated_ratio:02d}{trans_ratio:02d}.mp3"

        # 텍스트 구성
        if energy_ratio > 0:
            daily_text += f"열량 {energy_ratio}%, "
        if sodium_ratio > 0:
            daily_text += f"나트륨 {sodium_ratio}%, "
        if sugar_ratio > 0:
            daily_text += f"당류 {sugar_ratio}%, "
        if saturated_ratio > 0:
            daily_text += f"포화지방 {saturated_ratio}%, "
        if trans_ratio > 0:
            daily_text += f"트랜스지방 {trans_ratio}% 입니다."

    # 음성 파일 생성 및 저장
    text_to_speak_adv(file_name, daily_text, "daily_ratio")





def get_allergen_filename(allergen):
    # 알레르겐 한글-영어 매핑
    allergen_mapping = {
        "우유": "milk",
        "대두": "soybean",
        "밀": "wheat",
        "땅콩": "peanut",
        "견과류": "nuts",
        "갑각류": "crustacean",
        "계란": "egg",
        "생선": "fish",
        "조개류": "shellfish",
        "닭고기" : "chicken"
        # 필요한 매핑 추가
    }
    return allergen_mapping.get(allergen, f"allergen_{hash(allergen)}")



def speak_allergen_info(allergen, risk_level):

    # 알레르겐 파일명을 영어로 변환
    allergen_filename = f"{get_allergen_filename(allergen)}.mp3"
    
    
    # 알레르겐 음성 파일 생성/재생
    text_to_speak_adv(allergen_filename, allergen, "ingredients")
    

    # 위험도 메시지 파일명도 영어로
    risk_filename_mapping = {
        "High Risk Group": "high_risk.mp3",
        "Risk Group": "risk.mp3",
        "Caution Group": "caution.mp3"
    }

    # 위험도 메시지 음성 파일 생성/재생
    risk_message = ""
    if risk_level == "High Risk Group":
        risk_message = "고위험. 섭취하지 마십시오"
    elif risk_level == "Risk Group":
        risk_message = "위험. 주의해 주십시오"
    elif risk_level == "Caution Group":
        risk_message = "참고해 주십시오"
    else:
        risk_message = "알 수 없는 위험 수준."
    
    risk_filename = risk_filename_mapping.get(risk_level, "unknown_risk.mp3")
    category = "warnings"

    text_to_speak_adv(risk_filename, risk_message, category)



def speak_base_warning():
    audio_file_name = "base_warning.mp3"
    text = "알레르기 성분이 포함되어 있습니다"
    category = "warnings" 

    text_to_speak_adv(audio_file_name, text, category)
