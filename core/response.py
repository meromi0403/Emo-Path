from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("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"))

def generate_response(user_input, history="", stats="", mode="일반 모드"):
    
    if mode == "단순 소통 모드":
        prompt = f"""
        너는 감각 민감 사용자를 돕는 AI야.

        규칙:
        - 짧게 말해
        - 한 문장씩
        - 어려운 말 금지
        - 감정을 명확하게 말해

        입력: {user_input}
        """

    else:
        prompt = f"""
        사용자의 감정 흐름:
        {history}

        감정 통계:
        {stats}

        공감적으로 답해줘.

        입력: {user_input}
        """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content