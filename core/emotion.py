import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("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"))

def analyze_emotion(text):
    prompt = f"""
    너는 감정을 매우 세밀하게 분석하는 전문가다.

    다음 문장을 분석해서 반드시 JSON으로만 답해.
    설명은 절대 하지 마.

    감정은 최대한 다양하고 구체적으로 표현해라.

    예시 감정:
    - 불안, 초조, 긴장, 압박감
    - 우울, 무기력, 공허함, 외로움
    - 분노, 짜증, 답답함, 억울함
    - 행복, 설렘, 안정감, 만족감

    형식:
    {{
    "primary_emotion": "",
    "secondary_emotion": "",
    "intensity": 0,
    "keywords": []
    }}

    문장: "{text}"
    """

    res = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},  # ⭐ 여기!
    messages=[{"role": "user", "content": prompt}]
)
    
    content = res.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "primary_emotion": "알 수 없음",
            "secondary_emotion": "",
            "intensity": 0,
            "keywords": []
        }