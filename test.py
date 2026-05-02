from openai import OpenAI

MODEL_NAME = "QuantTrio/Qwen3.5-4B-AWQ"

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy"   # 로컬 vLLM 서버는 형식상 값만 있으면 됨
)

messages = [
    {
        "role": "system",
        "content":(
            "당신은 친절한 AI입니다. "
            "사용자에게 항상 한국어로만 답하세요. "
            "답변은 자연스러운 구어체로, 짧고 간결하게 1~2문장으로 답하세요. "
        )
    }
]

print("로컬 Qwen3.5-4B-AWQ 채팅 시작. 종료하려면 quit 또는 exit 입력.\n")

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

    messages.append({"role": "assistant", "content": answer})
