from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_calm_system_prompt():
    return """
너는 감각 민감 사용자와 자폐 성향 사용자를 돕는 안정형 감정 지원 AI다.

반드시 지켜야 할 규칙:
- 항상 짧게 말해
- 한 줄에 한 문장만 말해
- 어려운 말, 추상적인 말, 비유 금지
- 감정을 먼저 짚어줘
- 사용자를 다그치지 마
- 질문은 한 번에 하나만
- 출력 구조는 항상 같게 유지해

출력 구조:
1. 감정 확인
2. 짧은 안정 문장
3. 바로 할 수 있는 선택지 2개

출력 예시:
지금 불안해 보여.
괜찮아. 천천히 해도 돼.
1. 숨 쉬기
2. 잠깐 쉬기
""".strip()


def build_general_user_prompt(user_input, history="", stats="", emotion=""):
    return f"""
사용자의 감정 흐름:
{history if history else "기록 없음"}

감정 통계:
{stats if stats else "통계 없음"}

현재 추정 감정:
{emotion if emotion else "알 수 없음"}

입력:
{user_input}

위 정보를 참고해서 공감적으로 답해줘.
너무 차갑지 않게, 너무 길지 않게 답해줘.
""".strip()


def build_calm_user_prompt(user_input, emotion=""):
    return f"""
현재 감정:
{emotion if emotion else "알 수 없음"}

사용자 입력:
{user_input}

규칙에 맞춰 답해줘.
""".strip()


def generate_response(user_input, history="", stats="", emotion="", mode="일반 모드"):
    try:
        if mode == "자폐 친화 모드":
            system_prompt = build_calm_system_prompt()
            user_prompt = build_calm_user_prompt(
                user_input=user_input,
                emotion=emotion
            )
            temperature = 0.3
        else:
            system_prompt = SYSTEM_PROMPT
            user_prompt = build_general_user_prompt(
                user_input=user_input,
                history=history,
                stats=stats,
                emotion=emotion
            )
            temperature = 0.7

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=250
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        if mode == "자폐 친화 모드":
            return "지금 답변을 만들기 어려워.\n괜찮아.\n1. 잠깐 쉬기\n2. 다시 해보기"
        return f"응답 생성 중 오류가 발생했어: {e}"