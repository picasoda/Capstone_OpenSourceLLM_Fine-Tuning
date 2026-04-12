import pandas as pd
import os
import re

def create_ultimate_character_dataset():
    # 1. 필터링 설정
    TARGET_TOPICS = [1, 4, 5]  # 1: 일상, 4: 태도/감정, 5: 인간관계
    MIN_EMOTION_TURNS = 2      # 한 대화 내 감정 표현 최소 2회
    MIN_LENGTH = 6             # 최소 발화 수
    MAX_LENGTH = 16            # 최대 발화 수

    # 2. 제외할 현대 IT/기기 키워드 (정규식 컴파일)
    MODERN_KEYWORDS = [
        "smartphone", "smart phone", "iphone", "ipad", "tablet", "laptop", "pc", "smartwatch",
        "wifi", "wi-fi", "bluetooth", "gps", "5g", "lte", "usb", "power bank", "charger",
        "earbuds", "airpods", "drone", "smart tv", "kiosk", "internet", "app", "apps", 
        "email", "e-mail", "online", "website", "download", "social media", "facebook", 
        "instagram", "twitter", "youtube", "netflix", "streaming", "podcast", 
        "text message", "texting", "qr code", "ai", "artificial intelligence", "vr", "virtual reality"
    ]
    pattern_str = r'\b(?:' + '|'.join(re.escape(kw) for kw in MODERN_KEYWORDS) + r')\b'
    modern_regex = re.compile(pattern_str, re.IGNORECASE)

    # 3. 레이블 매핑
    TOPIC_DICT = {1: 'Ordinary Life', 2: 'School Life', 3: 'Culture & Education',
                  4: 'Attitude & Emotion', 5: 'Relationship', 6: 'Tourism',
                  7: 'Health', 8: 'Work', 9: 'Politics', 10: 'Finance'}
    ACT_DICT = {'1': 'inform', '2': 'question', '3': 'directive', '4': 'commissive'}
    EMOTION_DICT = {'0': 'no emotion', '1': 'anger', '2': 'disgust', '3': 'fear',
                    '4': 'happiness', '5': 'sadness', '6': 'surprise'}

    # 4. 파일 경로 (반드시 원본 데이터가 있는 'data' 폴더 기준)
    base_dir = 'data'
    TEXT_FILE = os.path.join(base_dir, 'dialogues_text.txt')
    TOPIC_FILE = os.path.join(base_dir, 'dialogues_topic.txt')
    ACT_FILE = os.path.join(base_dir, 'dialogues_act.txt')
    EMOTION_FILE = os.path.join(base_dir, 'dialogues_emotion.txt')
    OUTPUT_FILE = 'npc_character_dialogues_final.csv'

    data_rows = []
    total_dialogs = 0
    filtered_out = 0

    print("🎭 완벽한 NPC 챗봇용 데이터 추출을 시작합니다... (전체 데이터 대상)")

    with open(TEXT_FILE, 'r', encoding='utf-8') as f_text, \
         open(TOPIC_FILE, 'r', encoding='utf-8') as f_topic, \
         open(ACT_FILE, 'r', encoding='utf-8') as f_act, \
         open(EMOTION_FILE, 'r', encoding='utf-8') as f_emotion:

        for dialog_id, (text_line, topic_line, act_line, emotion_line) in enumerate(zip(f_text, f_topic, f_act, f_emotion)):
            total_dialogs += 1
            
            # [필터 1] 주제 확인
            topic_val = int(topic_line.strip())
            if topic_val not in TARGET_TOPICS:
                filtered_out += 1
                continue
                
            # [필터 2] 현대적 키워드 배제
            if modern_regex.search(text_line):
                filtered_out += 1
                continue
                
            utterances = [u.strip() for u in text_line.split('__eou__') if u.strip()]
            
            # [필터 3] 대화 길이
            if not (MIN_LENGTH <= len(utterances) <= MAX_LENGTH):
                filtered_out += 1
                continue

            emotions = emotion_line.split()
            
            # [필터 4] 감정 밀도 (로봇 같은 대화 제거)
            emotion_count = sum(1 for e in emotions if e != '0')
            if emotion_count < MIN_EMOTION_TURNS:
                filtered_out += 1
                continue

            acts = act_line.split()
            
            # 무결성 검증 및 데이터 저장
            if len(utterances) == len(acts) == len(emotions):
                mapped_acts = [ACT_DICT.get(a, a) for a in acts]
                mapped_emotions = [EMOTION_DICT.get(e, e) for e in emotions]
                
                data_rows.append({
                    'Dialogue_ID': dialog_id,
                    'Topic': TOPIC_DICT.get(topic_val, str(topic_val)),
                    'Text': text_line.strip(),
                    'Acts': ', '.join(mapped_acts),
                    'Emotions': ', '.join(mapped_emotions)
                })

    # 5. CSV 저장
    df = pd.DataFrame(data_rows)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print(f"=== 추출 완료 ===")
    print(f"원본 전체 대화 수: {total_dialogs}개")
    print(f"조건 미달로 제외된 대화 수: {filtered_out}개")
    print(f"🎉 최종 확보된 고품질 NPC 대화(행) 개수: {len(df)}개")
    print(f"저장 위치: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_ultimate_character_dataset()