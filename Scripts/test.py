from openai import OpenAI

# [수정됨] 기존 원본 모델 이름 대신, vLLM 서버 켤 때 등록한 LoRA 별명(my_npc)을 적어줍니다.
MODEL_NAME = "my_npc"

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy"   # 로컬 vLLM 서버는 형식상 값만 있으면 됨
)

messages = [
    {
        "role": "system",
        "content": (
            "You are a blacksmith. "
            "You are taciturn and a person of few words. "
            "Answer in a natural spoken tone, keeping it short and concise within 1 to 2 sentences. "
            "Stay immersed in your character and handle any anachronistic topics naturally."
        )
    }
]

print("로컬 Qwen3.5-4B-AWQ (NPC 파인튜닝 패치 적용됨) 채팅 시작. 종료하려면 quit 또는 exit 입력.\n")

while True:
    user_input = input("You> ").strip()
    if user_input.lower() in {"quit", "exit"}:
        print("종료합니다.")
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=50,
        top_p=0.9,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )

    answer = response.choices[0].message.content
    print(f"\nAI> {answer}\n")
    
    # AI의 답변도 대화 기록에 추가하여 문맥을 유지합니다.
    messages.append({"role": "assistant", "content": answer})