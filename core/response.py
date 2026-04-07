import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------
# fallback 응답 (API 없을 때)
# ---------------------------------
def fallback_response(emotion):

    responses = {
        "불안": "지금 많이 불안한 상태 같아. 잠깐 쉬어도 괜찮아.",
        "슬픔": "마음이 많이 무거워 보이네. 괜찮아, 그런 날도 있어.",
        "화남": "지금 많이 답답하거나 화가 난 상태 같아.",
        "기쁨": "좋은 기분이 느껴진다 😊",
        "피곤함": "지금 많이 지쳐 보이네. 조금 쉬어도 괜찮아.",
        "괜찮음": "지금은 비교적 안정된 상태인 것 같아.",
        "모르겠음": "지금 감정이 조금 복잡한 것 같아."
    }

    return responses.get(emotion, "지금 감정을 천천히 느껴봐도 괜찮아.")


# ---------------------------------
# 메인 응답 함수
# ---------------------------------
def generate_response(user_input, chat_history=None, emotion=None, mode="일반 모드"):

    messages = []

    if chat_history:
        messages.extend(chat_history)

    # 🔥 감정 기반 시스템 프롬프트
    system_prompt = f"""
너는 감정을 공감해주는 AI다.
현재 사용자 감정: {emotion}

- 너무 길게 말하지 마
- 자연스럽게 공감해
"""

    messages.insert(0, {
        "role": "system",
        "content": system_prompt
    })

    messages.append({
        "role": "user",
        "content": user_input
    })

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return res.choices[0].message.content