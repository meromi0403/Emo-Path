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
def generate_response(user_input, history="", stats="", emotion=None, mode="일반 모드"):

    # API 키 없으면 fallback
    if not os.getenv("OPENAI_API_KEY"):
        return fallback_response(emotion or "모르겠음")

    prompt = f"""
너는 사용자의 감정을 이해하고 공감하는 시스템이다.

조건:
- 너무 길지 않게
- 해결책보다 공감 중심
- 부드럽고 자연스럽게

사용자 입력:
{user_input}

최근 감정 흐름:
{history}

감정 통계:
{stats}

현재 감정:
{emotion}

모드:
{mode}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("OpenAI error:", e)
        return fallback_response(emotion or "모르겠음")