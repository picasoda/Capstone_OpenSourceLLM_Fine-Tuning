import pandas as pd
import json

def convert_text_to_json_overwrite():
    # 1. 입출력 파일명 설정 
    INPUT_FILE = 'npc_character_dialogues_final.csv'
    OUTPUT_FILE = 'npc_dialogues_message_format.csv'

    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"오류: {INPUT_FILE} 파일을 찾을 수 없습니다.")
        return

    json_messages_list = []

    print("CSV 내부 텍스트를 JSON 배열로 변환하여 'Text' 컬럼에 덮어쓰는 작업을 시작합니다...")

    for index, row in df.iterrows():
        # Text 컬럼의 데이터를 가져와 '__eou__' 기준으로 분리
        text = str(row['Text'])
        utterances = [u.strip() for u in text.split('__eou__') if u.strip()]
        
        messages = []
        
        # 대화 순서에 따라 역할(Role) 부여 (홀수: user, 짝수: assistant)
        for i, utterance in enumerate(utterances):
            role = "user" if i % 2 == 0 else "assistant"
            
            messages.append({
                "role": role,
                "content": utterance
            })
            
        # 리스트를 JSON 문자열로 변환 (ensure_ascii=False 로 한국어 등 다국어 깨짐 방지)
        json_string = json.dumps(messages, ensure_ascii=False)
        json_messages_list.append(json_string)

    # [수정된 핵심 로직] 새로운 컬럼을 만들지 않고 기존 'Text' 컬럼에 바로 덮어씌움
    df['Text'] = json_messages_list

    # 5. CSV 파일로 저장
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print("=== 작업 완료 ===")
    print(f"총 {len(df)}개의 대화가 JSON 형식으로 'Text' 컬럼에 성공적으로 덮어씌워졌습니다.")
    print(f"결과 파일: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_text_to_json_overwrite()