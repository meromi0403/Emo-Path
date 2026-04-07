import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------
# fallback (강화 버전)
# ---------------------------------
def fallback_emotion(text):
    text = text.lower()

    if any(word in text for word in ["불안", "걱정", "긴장", "초조"]):
        return {
            "primary_emotion": "불안",
            "secondary_emotion": "걱정",
            "intensity": "보통",
            "cause": "불확실성"
        }

    if any(word in text for word in ["슬프", "슬픔", "우울", "눈물"]):
        return {
            "primary_emotion": "슬픔",
            "secondary_emotion": "우울",
            "intensity": "보통",
            "cause": "감정 저하"
        }

    if any(word in text for word in ["화", "짜증", "분노"]):
        return {
            "primary_emotion": "화남",
            "secondary_emotion": "짜증",
            "intensity": "보통",
            "cause": "스트레스"
        }

    if any(word in text for word in ["좋아", "행복", "기쁘"]):
        return {
            "primary_emotion": "기쁨",
            "secondary_emotion": "만족",
            "intensity": "보통",
            "cause": "긍정적 경험"
        }

    return {
        "primary_emotion": "모르겠음",
        "secondary_emotion": "혼란",
        "intensity": "보통",
        "cause": "불명확"
    }


# ---------------------------------
# 감정 분석 (고급 버전)
# ---------------------------------
def analyze_emotion(text):

    if not os.getenv("OPENAI_API_KEY"):
        return fallback_emotion(text)

    prompt = f"""
다음 문장의 감정을 분석하세요.

조건:
- 반드시 JSON으로만 답변
- 감정을 최대한 구체적으로 분석

형식:
{{
  "primary_emotion": "불안/슬픔/화남/기쁨/피곤함/괜찮음/모르겠음",
  "secondary_emotion": "구체적인 감정 (예: 상실감, 좌절, 외로움, 압박감 등)",
  "intensity": "약함/보통/강함",
  "cause": "감정의 원인 (예: 인간관계, 학업, 미래, 피로 등)"
}}

문장:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        content = res.choices[0].message.content

        try:
            result = json.loads(content)
            return result
        except:
            return fallback_emotion(text)

    except Exception as e:
        print("OpenAI error:", e)
        return fallback_emotion(text)