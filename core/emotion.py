import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("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"))

def analyze_emotion(text):
    prompt = f"""
    다음 문장의 감정을 JSON으로 분석해:

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