from openai import OpenAI
import json
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

ko_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="jhgan/ko-sroberta-multitask")

chroma_client = chromadb.Client() 
# 컬렉션을 만들 때 한국어 임베딩 함수를 명시적으로 주입합니다.
collection = chroma_client.get_or_create_collection(
    name="item_dict",
    embedding_function=ko_embedding
)
# ==========================================
# RAG용 아이템 데이터 준비 및 벡터 DB 구축
# ==========================================
# 실제 환경에서는 위에서 만든 items.json 파일을 읽어오면 됩니다.
# 여기서는 테스트를 위해 파이썬 리스트로 바로 넣었습니다.
ITEM_DATA = [
    {"name": "녹슨 철검", "price": "10골드", "effect": "공격력 +2"},
    {"name": "강철 대검", "price": "150골드", "effect": "공격력 +15"},
    {"name": "미스릴 단검", "price": "500골드", "effect": "공격력 +8"},
    {"name": "가죽 갑옷", "price": "30골드", "effect": "방어력 +5"},
    {"name": "사슬 갑옷", "price": "200골드", "effect": "방어력 +20"},
    {"name": "기사의 판금 갑옷", "price": "1200골드", "effect": "방어력 +50"},
    {"name": "나무 방패", "price": "15골드", "effect": "방어력 +2"},
    {"name": "강철 방패", "price": "180골드", "effect": "방어력 +15"},
    {"name": "숫돌", "price": "5골드", "effect": "무기 내구도 10 회복"},
    {"name": "대장장이의 땀방울", "price": "비매품", "effect": "장비 강화 성공률 +5%"}
]

print("벡터 DB(Chroma) 초기화 중...")
chroma_client = chromadb.Client() # 테스트용 메모리 DB (종료 시 초기화됨)
# 실서비스용: chromadb.PersistentClient(path="./my_vector_db") 
collection = chroma_client.get_or_create_collection(name="item_dictionary")

# DB에 데이터 인덱싱 (최초 1회만 실행됨)
if collection.count() == 0:
    docs, metadatas, ids = [], [], []
    for i, item in enumerate(ITEM_DATA):
        # AI가 검색하고 읽기 좋게 문장으로 풀어서 저장합니다.
        doc_str = f"아이템 이름: {item['name']}, 가격: {item['price']}, 효과: {item['effect']}"
        docs.append(doc_str)
        metadatas.append(item)
        ids.append(f"item_{i}")
    
    collection.add(documents=docs, metadatas=metadatas, ids=ids)
print("✅ 아이템 도감 RAG 구축 완료!\n")

# ==========================================
# 서버와 연결하여 챗봇 테스트하기
# ==========================================
# vLLM 서버 켤 때 등록한 LoRA 별명 혹은 모델 이름을 입력하세요.
MODEL_NAME = "QuantTrio/Qwen3.5-4B-AWQ"

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy"   # 로컬 vLLM 서버는 형식상 값만 있으면 됨
)

messages = [
    {
        "role": "system",
        "content": (
            "당신은 중세 판타지 마을의 대장장이 NPC입니다. "
            "성격: 매우 무뚝뚝하고 거칠며, 손님에게 반말과 가벼운 욕설을 섞어 씁니다. "
            "절대 친절하게 대답하지 말고, 무조건 1~2문장으로 짧게 쳐내세요. "
            "[중요] (일상 대화): 손님이 인사나 잡담을 하면 [창고]를 무시하고 대장장이 특유의 거친 성격으로 자연스럽게 대화를 이어가세요."
            "(상거래): 물건에대해 물어보면 [창고]를 확인하세요. 정보에 있는 물건이면 '가격'과 '효과'를 지어내지 마세요. "
        )
    }
]

print(f"로컬 RAG + 베이스 모델({MODEL_NAME}) 챗봇 시작. (종료: quit/exit)\n")

while True:
    user_input = input("You> ").strip()
    if user_input.lower() in {"quit", "exit"}:
        print("종료합니다.")
        break
    if not user_input:
        continue
    
    # 1. 벡터 DB에서 유저 질문과 관련된 아이템 정보 검색
    search_results = collection.query(
        query_texts=[user_input],
        n_results=1 
    )
    
    retrieved_info = "관련 정보 없음"
    if search_results['documents'] and search_results['documents'][0]:
        retrieved_info = "\n".join(search_results['documents'][0])

    # 2. [핵심] 베이스 모델이 헷갈리지 않도록 정보와 질문을 명확히 분리한 프롬프트 구성
    rag_prompt = f"""
    [창고]
    ---------------------
    {retrieved_info}
    ---------------------
    손님의 질문: {user_input}"""
    
    messages.append({"role": "user", "content": rag_prompt})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.5,
        max_tokens=80,
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