# ============================================
# HuggingFace 데이터셋 → 중세 우선 보존 + 나머지 랜덤 추출
# ============================================

import csv
import json
import random
from datasets import load_dataset

# ============================================
# CONFIG (여기만 수정하면 됩니다)
# ============================================
CONFIG = {
    "output_path": "./final_dataset.csv",
    "target_count": 1298,
    "seed": 42,
    "priority_keywords": [
        "중세"
    ],
}
# ============================================

random.seed(CONFIG["seed"])

# ============================================
# 1. 데이터셋 로드
# ============================================
ds = load_dataset(
    "huggingface-KREW/korean-role-playing",
    "general-roleplay-data",
    split="train"
)

data = []
for row in ds:
    msgs = row["text"]
    data.append({
        "turn_count": len(msgs),
        "conversations": msgs,
    })

print(f"불러온 데이터: {len(data)}개")
print(f"목표 수량:     {CONFIG['target_count']}개")
print(f"우선 키워드:   {len(CONFIG['priority_keywords'])}개")

# ============================================
# 2. 우선 보존 vs 나머지 분리
# ============================================
def contains_priority_keyword(row):
    full_text = " ".join([m["content"] for m in row["conversations"]])
    for keyword in CONFIG["priority_keywords"]:
        if keyword in full_text:
            return True
    return False

priority_data = []
general_data = []

for row in data:
    if contains_priority_keyword(row):
        priority_data.append(row)
    else:
        general_data.append(row)

print(f"\n분류 결과:")
print(f"  우선 보존 (중세 등): {len(priority_data)}개")
print(f"  나머지 (랜덤 풀):   {len(general_data)}개")

# ============================================
# 3. 나머지에서 랜덤 추출
# ============================================
remaining_quota = CONFIG["target_count"] - len(priority_data)

if remaining_quota <= 0:
    print(f"\n우선 데이터만으로 이미 목표 초과! ({len(priority_data)}개)")
    final_data = priority_data
else:
    if remaining_quota > len(general_data):
        print(f"\n나머지 풀({len(general_data)}개)이 필요량({remaining_quota}개)보다 적습니다.")
        final_data = priority_data + general_data
    else:
        random.shuffle(general_data)
        sampled_general = general_data[:remaining_quota]
        final_data = priority_data + sampled_general

    random.shuffle(final_data)

print(f"\n최종 구성:")
print(f"  우선 보존: {len(priority_data)}개 ({len(priority_data)/len(final_data)*100:.1f}%)")
print(f"  랜덤 추출: {len(final_data) - len(priority_data)}개")
print(f"  합계:      {len(final_data)}개")

# ============================================
# 4. 매칭된 키워드 통계
# ============================================
keyword_counts = {}
for row in priority_data:
    full_text = " ".join([m["content"] for m in row["conversations"]])
    for keyword in CONFIG["priority_keywords"]:
        if keyword in full_text:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

print(f"\n우선 키워드별 매칭 수:")
for kw, cnt in sorted(keyword_counts.items(), key=lambda x: -x[1]):
    print(f"  {kw:10s}: {cnt}개")

# ============================================
# 5. CSV 저장
# ============================================
with open(CONFIG["output_path"], "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["index", "turn_count", "is_priority", "conversations"])
    for i, row in enumerate(final_data):
        is_priority = contains_priority_keyword(row)
        writer.writerow([
            i,
            row["turn_count"],
            is_priority,
            json.dumps(row["conversations"], ensure_ascii=False)
        ])

print(f"\n저장 완료: {CONFIG['output_path']}")
print(f"총 {len(final_data)}개")
