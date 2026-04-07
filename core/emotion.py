import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------
# fallback
# ---------------------------------
def fallback_emotion(text):
    text = text.lower()

    if any(word in text for word in ["불안", "걱정", "긴장", "초조"]):
        return {"primary_emotion": "불안", "intensity": "보통"}

    if any(word in text for word in ["슬프", "슬픔", "슬퍼", "우울", "눈물"]):
        return {"primary_emotion": "슬픔", "intensity": "보통"}

    if any(word in text for word in ["화", "짜증", "분노", "열받"]):
        return {"primary_emotion": "화남", "intensity": "보통"}

    if any(word in text for word in ["좋아", "행복", "기쁘", "신남"]):
        return {"primary_emotion": "기쁨", "intensity": "보통"}

    return {"primary_emotion": "모르겠음", "intensity": "보통"}


# ---------------------------------
# emotion 분석
# ---------------------------------
def analyze_emotion(text):

    if not os.getenv("OPENAI_API_KEY"):
        return fallback_emotion(text)

    prompt = f"""
다음 문장의 감정을 분석하세요.

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

        try:
            return json.loads(content)
        except:
            return fallback_emotion(text)

    except Exception as e:
        print("OpenAI error:", e)
        return fallback_emotion(text)