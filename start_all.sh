#!/bin/bash

# vLLM 백그라운드 실행
vllm serve QuantTrio/Qwen3.5-4B-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 1024 \
  --max-num-seqs 1 \
  --dtype half \
  --gpu-memory-utilization 0.85 \
  --enforce-eager &

echo "vLLM 시작 대기중..."
sleep 120  # 모델 로딩 시간

# FastAPI 백그라운드 실행
python test.py &
sleep 3

# ngrok 실행 (고정 도메인)
ngrok http 8080 --url bullring-reactive-ensure.ngrok-free.dev