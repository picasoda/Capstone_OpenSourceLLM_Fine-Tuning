import csv
import json

# ============================================
# 설정
# ============================================
INPUT_PATH  = "./final_dataset.csv"
OUTPUT_PATH = "./dataset_chatml.jsonl"   # 학습용 최종 파일
VAL_RATIO   = 0.1                        # 10%를 검증용으로 분리
SEED        = 42

# ============================================
# 1. CSV 불러오기
# ============================================
data = []
with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        conversations = json.loads(row["conversations"])
        data.append(conversations)

print(f"불러온 데이터: {len(data)}개")


# ============================================
# 2. ChatML 형식으로 변환
# ============================================
def to_chatml(conversations):
    """대화 리스트를 ChatML 문자열로 변환"""
    chatml = ""
    for msg in conversations:
        role = msg["role"]
        content = msg["content"]
        chatml += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    return chatml.strip()


chatml_data = []
for conv in data:
    text = to_chatml(conv)
    chatml_data.append({"text": text})

# 변환 확인
print("\n=== 변환 샘플 ===")
print(chatml_data[0]["text"][:500])
print("...")


# ============================================
# 3. Train / Val 분리
# ============================================
import random
random.seed(SEED)
random.shuffle(chatml_data)

val_size = int(len(chatml_data) * VAL_RATIO)
train_data = chatml_data[val_size:]
val_data   = chatml_data[:val_size]

print(f"\nTrain: {len(train_data)}개")
print(f"Val:   {len(val_data)}개")


# ============================================
# 4. JSONL로 저장
# ============================================
train_path = OUTPUT_PATH.replace(".jsonl", "_train.jsonl")
val_path   = OUTPUT_PATH.replace(".jsonl", "_val.jsonl")

for path, dataset in [(train_path, train_data), (val_path, val_data)]:
    with open(path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"\n저장 완료:")
print(f"  Train: {train_path}")
print(f"  Val:   {val_path}")