from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("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"))

def generate_response(user_input, history="", stats=""):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
                사용자의 감정 통계:
                {stats}

                최근 감정 흐름:
                {history}

                현재 입력:
                {user_input}

                이 사용자를 이해한 상태에서 공감해줘.
                """
            }
        ]
    )

    return res.choices[0].message.content