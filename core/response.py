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

    # 🔥 API 키 없으면 fallback
    if not os.getenv("OPENAI_API_KEY"):
        return fallback_response(emotion)

    messages = []

    # 🔥 system 프롬프트 (핵심)
    system_prompt = f"""
너는 감정을 공감해주는 AI다.

현재 사용자 감정: {emotion}
모드: {mode}

규칙:
- 공감 중심으로 말해
- 너무 길게 말하지 마
- 부드럽고 안정적으로 말해
- 반드시 이 감정을 기반으로 공감해라.
- 절대 '모르겠음' 같은 애매한 표현 쓰지 마.
"""

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    # 🔥 기존 대화 추가
    if chat_history:
        messages.extend(chat_history)

    # 🔥 현재 입력 추가
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 🔥 메시지 정리 (에러 방지 핵심)
    clean_messages = []
    for msg in messages:
        if (
            isinstance(msg, dict)
            and "role" in msg
            and "content" in msg
            and msg["content"] is not None
        ):
            clean_messages.append({
                "role": msg["role"],
                "content": str(msg["content"])
            })

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=clean_messages
        )

        content = res.choices[0].message.content

        # 🔥 None 방지
        if content is None:
            return fallback_response(emotion)

        return content

    except Exception as e:
        print("OpenAI error:", e)
        return fallback_response(emotion)