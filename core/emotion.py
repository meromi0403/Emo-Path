import os
import json
from openai import OpenAI

# ---------------------------------
# OpenAI client
# ---------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------
# 기본 fallback
# ---------------------------------
def fallback_emotion(text):
    text = text.lower()

    if any(word in text for word in ["불안", "걱정", "긴장"]):
        return {"primary_emotion": "불안", "intensity": "보통"}

    if any(word in text for word in ["슬프", "우울", "눈물"]):
        return {"primary_emotion": "슬픔", "intensity": "보통"}

    if any(word in text for word in ["화나", "짜증", "분노"]):
        return {"primary_emotion": "화남", "intensity": "보통"}

    if any(word in text for word in ["좋아", "행복", "기쁘"]):
        return {"primary_emotion": "기쁨", "intensity": "보통"}

    return {"primary_emotion": "모르겠음", "intensity": "보통"}


# ---------------------------------
# 메인 분석 함수
# ---------------------------------
def analyze_emotion(text):

    # 1. API 키 없으면 fallback
    if not os.getenv("OPENAI_API_KEY"):
        return fallback_emotion(text)

    prompt = f"""
다음 문장을 읽고 감정을 분석하세요.

반드시 JSON 형식으로만 답하세요.

형식:
{{
    "primary_emotion": "불안/슬픔/화남/기쁨/피곤함/괜찮음/모르겠음",
    "intensity": "약함/보통/강함"
}}

문장:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = res.choices[0].message.content

        # JSON 파싱 시도
        try:
            result = json.loads(content)
            return result

        except:
            # JSON 깨졌으면 fallback
            return fallback_emotion(text)

    except Exception as e:
        # API 에러 → fallback
        print("OpenAI error:", e)
        return fallback_emotion(text)