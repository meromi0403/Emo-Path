import streamlit as st
import pandas as pd
from datetime import datetime

from data.db import init_db, save_log, load_logs
from core.emotion import analyze_emotion
from core.response import generate_response
from core.recommend import recommend_action
if "page" not in st.session_state:
    st.session_state.page = "intro"
    
import time

if st.button("시작하기"):
    with st.spinner("넘어가는 중..."):
        time.sleep(0.6)
        st.session_state.page = "meaning"
        st.rerun()
        
def show_intro():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.image("assets/start.png", use_container_width=True)

    if st.button("시작하기"):
        st.session_state.page = "meaning"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
# ---------------------------------
# 기본 설정
# ---------------------------------
st.set_page_config(page_title="정서로", page_icon="🫧", layout="centered")
init_db()

st.markdown("""
<style>
.fade {
    animation: fadeIn 0.6s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# 상수 / 유틸
# ---------------------------------
EMOTION_BG_COLORS = {
    "불안": "#d4edda",
    "화남": "#cce5ff",
    "슬픔": "#e2e3e5",
    "피곤함": "#f8f9fa",
    "기쁨": "#fff3cd",
    "괜찮음": "#d1ecf1",
    "모르겠음": "#eeeeee",
}

EMOTION_TEXT_COLORS = {
    "불안": "#dc3545",
    "화남": "#0d6efd",
    "슬픔": "#6c757d",
    "피곤함": "#868e96",
    "기쁨": "#f59f00",
    "괜찮음": "#17a2b8",
    "모르겠음": "#999999",
}

EMOTION_SCORE_MAP = {
    "약함": 1,
    "보통": 2,
    "강함": 3,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
}

DANGER_KEYWORDS = ["죽고싶", "자살", "사라지고싶", "끝내고싶", "없어지고싶"]

def detectss_state(logs):
    recent = logs[-5:]

    emotions = [l["emotion"] for l in recent]

    if emotions.count("불안") >= 3:
        return "긴장 상태"

    if emotions.count("슬픔") >= 3:
        return "우울 상태"

    if len(set(emotions)) >= 3:
        return "감정 불안정 상태"

    if emotions.count("기쁨") >= 3:
        return "안정 상태"

    return "일반 상태"


def show_meaning():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.title("정서로 의미")

    st.markdown("""
    우리는 감정을 단순한 상태가 아닌  
    시간 속에서 변화하는 흐름으로 바라봅니다.

    이 시스템은 감정을 기록하고,  
    패턴을 통해 상태를 이해하고,  
    사용자에게 맞는 반응을 제공합니다.
    """)

    if st.button("다음"):
        st.session_state.page = "guide"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_guide():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.title("사용 방법")

    st.markdown("""
    1. 현재 감정을 선택하세요  
    2. 감정의 강도를 선택하세요  
    3. 필요한 경우 추가 입력을 하세요  
    4. 시스템이 상태를 분석하고 반응합니다  

    👉 감정은 기록되고 흐름으로 분석됩니다.
    """)

    if st.button("시작"):
        st.session_state.page = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_mode_select():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.title("모드 선택")

    st.markdown("""
    사용 방식을 선택해주세요.

    - 일반 모드: 자유롭게 감정을 기록하고 대화합니다  
    - 자폐 친화 모드: 단계별 선택 기반으로 진행됩니다  
    """)

    mode = st.radio("선택", ["일반 모드", "자폐 친화 모드"], key="mode_select")

    if st.button("시작"):
        st.session_state.mode = mode
        st.session_state.page = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def get_bg_color(emotion: str) -> str:
    return EMOTION_BG_COLORS.get(emotion, "#ffffff")


def get_text_color(emotion: str) -> str:
    return EMOTION_TEXT_COLORS.get(emotion, "#666666")


def intensity_to_score(value):
    return EMOTION_SCORE_MAP.get(value, 2)

def detects_state(logs):
    recent = logs[-5:]

    emotions = [l["emotion"] for l in recent]

    if emotions.count("불안") >= 3:
        return "긴장 상태"

    if emotions.count("슬픔") >= 3:
        return "우울 상태"

    if len(set(emotions)) >= 3:
        return "감정 불안정 상태"

    if emotions.count("기쁨") >= 3:
        return "안정 상태"

    return "일반 상태"

def detect_state(logs: list[dict]) -> str:
    if len(logs) < 3:
        return "분석 중"

    recent = logs[-3:]
    emotions = [log.get("emotion", "모르겠음") for log in recent]
    intensities = [intensity_to_score(log.get("intensity", "보통")) for log in recent]

    if emotions.count("불안") >= 2 and intensities[-1] >= intensities[0]:
        return "불안 축적 상태"

    if len(set(emotions)) >= 3:
        return "감정 변동 상태"

    if max(intensities) <= 2 and len(set(emotions)) <= 2:
        return "안정 상태"

    return "관찰 중"


def recommend_intensity(text: str):
    if not text:
        return None
    if any(word in text for word in ["너무", "진짜", "완전", "미치겠", "숨막", "폭발"]):
        return "강함"
    if any(word in text for word in ["조금", "약간", "살짝"]):
        return "약함"
    return "보통"


def recommend_from_text(text: str):
    if not text:
        return None

    if any(word in text for word in ["시끄러", "소리", "떠들", "소음"]):
        return "소리"
    if any(word in text for word in ["밝", "눈부", "빛"]):
        return "빛"
    if any(word in text for word in ["복잡", "머리 아픔", "생각 많", "정신없"]):
        return "복잡함"
    if any(word in text for word in ["말하기", "대화", "대답", "말하기 싫"]):
        return "말하기"
    return None


def show_breathing_box():
    st.markdown(
        """
        <style>
        .breath-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background-color: #a8e6cf;
            margin: 20px auto;
            animation: breathe 4s infinite;
        }

        @keyframes breathe {
            0% { transform: scale(1); }
            50% { transform: scale(1.45); }
            100% { transform: scale(1); }
        }
        </style>

        <div style="text-align:center;">
            <h3>천천히 숨 쉬기</h3>
            <div class="breath-circle"></div>
            <p>원이 커질 때 들이마시고</p>
            <p>작아질 때 내쉬어</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_calm_screen():
    st.markdown(
        """
        <div style="padding:40px;text-align:center;background:#f5f5f5;border-radius:20px;">
            <h2>괜찮아</h2>
            <p>지금은 쉬어도 돼</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def emotion_card(emotion: str, intensity, state: str):
    bg = get_bg_color(emotion)
    text_color = "#222222"
    return f"""
    <div style="
        background:{bg};
        padding:24px;
        border-radius:20px;
        color:{text_color};
        text-align:center;
        box-shadow: 0px 10px 24px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        margin-top: 12px;
        margin-bottom: 12px;
    ">
        <h2 style="margin:0 0 8px 0;">{emotion}</h2>
        <p style="font-size:17px; margin:0 0 6px 0;">강도 {intensity}</p>
        <p style="font-size:15px; margin:0; color:#555;">현재 상태: {state}</p>
    </div>
    """


def show_state_badge(emotion: str, state: str):
    color = get_text_color(emotion)
    st.markdown(
        f"""
        <div style="
            padding:14px 16px;
            border-radius:14px;
            background:#ffffff;
            border:1px solid #e9ecef;
            text-align:center;
            margin-top:10px;
            margin-bottom:10px;
        ">
            <span style="font-size:15px; color:#666;">상태 분석</span><br>
            <span style="font-size:20px; font-weight:700; color:{color};">{state}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("최근 감정 패턴을 기반으로 상태를 분석했습니다")
    

def build_history_and_stats(logs: list[dict]):
    if not logs:
        return "", ""

    recent = logs[-5:]
    history = " → ".join(log["emotion"] for log in recent)

    emotion_count = {}
    for log in logs:
        emo = log["emotion"]
        emotion_count[emo] = emotion_count.get(emo, 0) + 1

    stats = ", ".join(f"{k}: {v}회" for k, v in emotion_count.items())
    return history, stats


def render_time_chart(logs: list[dict]):
    if not logs:
        return

    chart_logs = []
    for log in logs:
        if "time" not in log:
            continue
        chart_logs.append(
            {
                "time": pd.to_datetime(log["time"]),
                "intensity_score": intensity_to_score(log.get("intensity", "보통")),
            }
        )

    if not chart_logs:
        return

    df = pd.DataFrame(chart_logs).sort_values("time")
    st.subheader("📈 감정 강도 흐름")
    st.line_chart(df.set_index("time")["intensity_score"])


def render_emotion_flow(logs: list[dict]):
    if not logs:
        return

    recent = logs[-5:]
    colored_flow = " → ".join(
        [
            f"<span style='color:{get_text_color(log['emotion'])}; font-weight:600;'>{log['emotion']}</span>"
            for log in recent
        ]
    )

    st.markdown(
        f"""
        <div style="
            background: #fafafa;
            padding:20px;
            border-radius:15px;
            border:1px solid #eeeeee;
            margin-top:20px;
        ">
            <h4 style="margin-bottom:10px;">🧠 최근 감정 흐름</h4>
            <p style="font-size:18px; text-align:center; margin:0;">
                {colored_flow}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if st.session_state.page == "intro":
    show_intro()

elif st.session_state.page == "meaning":
    show_meaning()

elif st.session_state.page == "guide":
    show_guide()

elif st.session_state.page == "mode":
    show_mode_select()

elif st.session_state.page == "main":
    if st.session_state.mode == "일반 모드":
        show_general_mode()
    else:
        show_autism_mode()
        
def show_general_mode():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.subheader("오늘 기분 기록하기")

    user_input = st.text_area("오늘 기분을 적어줘", key="general_user_input")

    if st.button("기록하기", key="general_save_btn"):
        if not user_input.strip():
            st.warning("조금만 적어줘 :)")
            return

        
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        if any(word in user_input for word in DANGER_KEYWORDS):
            st.warning("지금 많이 힘든 상태로 보여. 혼자 버티지 않아도 괜찮아.")
            st.write("👉 109 / 1588-9191 / 1393 등 긴급 상담 도움을 바로 받아봐.")

        emotion_result = analyze_emotion(user_input)

        primary_emotion = emotion_result.get("primary_emotion", "모르겠음")
        secondary_emotion = emotion_result.get("secondary_emotion", "")
        cause = emotion_result.get("cause", "")
        intensity = emotion_result.get("intensity", "보통")

        current_log = {
            "emotion": primary_emotion,
            "secondary": secondary_emotion,
            "cause": cause,
            "intensity": intensity,
            "time": datetime.now(),
            "text": user_input,
        }
        st.session_state.logs.append(current_log)

        try:
            save_log(user_input, primary_emotion, intensity)
        except Exception:
            pass

        history, stats = build_history_and_stats(st.session_state.logs)
        
        with st.spinner("정서 흐름으로 이동 중..."):
            response = generate_response(
        
                user_input=user_input,
                chat_history=st.session_state.chat_history,
                emotion=primary_emotion
        )
        action = recommend_action(primary_emotion)
        state = detect_state(st.session_state.logs)
        # 상태 기반 UI 변화
        if state == "불안 축적 상태":
            st.markdown("""
                <style>
                .stApp {
                    background-color: #fff5f5;
                }
                </style>
            """, unsafe_allow_html=True)
            st.warning("지금 불안이 계속 쌓이고 있어요. 잠깐 쉬는 게 좋아요.")
            st.write("👉 입력을 줄이고 간단한 선택을 추천해요")

        elif state == "감정 변동 상태":
            st.markdown("""
                <style>
                .stApp {
                    background-color: #f0f8ff;
                }
                </style>
            """, unsafe_allow_html=True)
            st.info("감정 변화가 큰 상태예요. 천천히 정리해볼까요?")

        elif state == "안정 상태":
            st.markdown("""
                <style>
                .stApp {
                    background-color: #f6fff5;
                }
                </style>
            """, unsafe_allow_html=True)
            st.success("지금은 안정된 상태예요 👍")

        st.markdown(emotion_card(primary_emotion, intensity, state), unsafe_allow_html=True)
        show_state_badge(primary_emotion, state)
       
        if secondary_emotion or cause:
            st.caption(f"{secondary_emotion} • 원인: {cause}")
        
        

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": str(response)
        })
        st.subheader("💬 공감")
        st.write(response)

        st.subheader("🌿 추천")
        st.success(action)

    if st.session_state.logs:
        render_emotion_flow(st.session_state.logs)
        render_time_chart(st.session_state.logs)

        emotions = [log["emotion"] for log in st.session_state.logs]
        most_common = max(set(emotions), key=emotions.count)
        st.subheader("📌 최근 감정 패턴")
        st.info(f"요즘 가장 많이 느끼는 감정은 **{most_common}** 이야")

        recent = emotions[-3:]
        if recent.count("불안") >= 2:
            st.warning("요즘 불안한 상태가 계속 이어지고 있어 보여")

    st.markdown('</div>', unsafe_allow_html=True)
def show_step_progress():
    step = st.session_state.step
    total = 5
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <div style="font-weight:600;">진행 단계: {step} / {total}</div>
            <div style="
                height:10px;
                background:#eee;
                border-radius:10px;
                overflow:hidden;
            ">
                <div style="
                    width:{(step / total) * 100}%;
                    height:100%;
                    background:#6c9cff;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_autism_mode_log_once():
    if st.session_state.get("autism_result_saved", False):
        return

    log = {
        "emotion": st.session_state.get("emotion", "모르겠음"),
        "secondary": "선택 기반",
        "cause": st.session_state.get("sensory", "없음"),
        "intensity": st.session_state.get("intensity", "보통"),
        "time": datetime.now(),
        "text": st.session_state.get("user_text", ""),
    }
    st.session_state.logs.append(log)

    state = detect_state(st.session_state.logs)


    if state == "긴장 상태":
        st.warning("지금 긴장이 지속되고 있어요")

    elif state == "우울 상태":
        st.info("마음이 많이 가라앉은 상태입니다")

    elif state == "감정 불안정 상태":
        st.error("감정 변화가 크게 나타나고 있어요")

    elif state == "안정 상태":
        st.success("현재 안정된 상태입니다")

    try:
        save_log(
            st.session_state.get("user_text", ""),
            st.session_state.get("emotion", "모르겠음"),
            st.session_state.get("intensity", "보통"),
        )
    except Exception:
        pass

    st.session_state.autism_result_saved = True


def reset_autism_mode():
    st.session_state.step = 1
    st.session_state.emotion = "모르겠음"
    st.session_state.intensity = "보통"
    st.session_state.sensory = "없음"
    st.session_state.user_text = ""
    st.session_state.choice = "진정"
    st.session_state.autism_result_saved = False


def show_autism_mode():
    st.markdown('<div class="fade">', unsafe_allow_html=True)
    st.subheader("자폐 친화 모드")
    show_step_progress()

    if st.session_state.step == 1:
        st.subheader("지금 상태를 골라줘")
        selected_emotion = st.selectbox(
           "감정",
           ["불안", "화남", "슬픔", "피곤함", "기쁨", "괜찮음", "모르겠음"],
        )
        emotion = st.session_state.get("emotion")

        st.text_input("말하기 (선택)", key="user_text")

        if st.button("다음", key="step1_next"):
           st.session_state.emotion = selected_emotion
           st.session_state.step = 2
           st.rerun()

    elif st.session_state.step == 2:
        user_text = st.session_state.get("user_text", "")
        recommended_intensity = recommend_intensity(user_text)

        intensity = st.radio(
            "강도",
            ["약함", "보통", "강함"],
            index=["약함", "보통", "강함"].index(recommended_intensity) if recommended_intensity else 1,
            key="intensity_radio",
            horizontal=True,
        )

        if st.button("다음", key="step2_next"):
            st.session_state.intensity = intensity
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        user_text = st.session_state.get("user_text", "")
        recommended = recommend_from_text(user_text)

        st.subheader("지금 뭐가 힘들어?")
        if recommended:
            st.info(f"👉 '{recommended}' 때문일 가능성이 있어")

        sensory_options = ["소리", "빛", "복잡함", "말하기", "없음"]
        sensory = st.selectbox(
            "선택",
            sensory_options,
            index=sensory_options.index(recommended) if recommended in sensory_options else sensory_options.index("없음"),
            key="sensory_select",
        )

        if st.button("다음", key="step3_next"):
            st.session_state.sensory = sensory
            st.session_state.step = 4
            st.rerun()

    elif st.session_state.step == 4:
        st.subheader("어떤 도움을 받을래?")
        choice = st.radio("선택", ["진정", "짧은 말", "조용한 화면"], key="choice_radio", horizontal=True)

        if st.button("시작", key="step4_start"):
            st.session_state.choice = choice
            st.session_state.step = 5
            st.session_state.autism_result_saved = False
            st.rerun()

    elif st.session_state.step == 5:
       
       

        st.subheader("감정 흐름")

        st.line_chart(df.set_index("time")["emotion"])

        emotion = st.session_state.get("emotion")
        if not emotion:
            emotion = "모르겠음"

        intensity = st.session_state.get("intensity", "보통")
        secondary_emotion = "선택 기반"
        cause = st.session_state.get("sensory", "없음")
        bg_color = get_bg_color(emotion)

        st.markdown(
            f"""
            <div style="
                padding:20px;
                border-radius:16px;
                background:{bg_color};
                margin-bottom:15px;
                border:1px solid rgba(0,0,0,0.05);
            ">
            """,
            unsafe_allow_html=True,
        )

        st.subheader("결과")

        if st.session_state.choice == "진정":
            show_breathing_box()

        elif st.session_state.choice == "짧은 말":
            user_input = f"""
        감정: {emotion}
        강도: {intensity}
        감각: {st.session_state.get("sensory", "없음")}
        추가 입력: {st.session_state.get("user_text", "")}
            """.strip()

            with st.spinner("생각하는 중..."):
                response = generate_response(
                    user_input=user_input,
                    chat_history=st.session_state.chat_history[-3:],
                    emotion=emotion,
                    mode="자폐 친화 모드",
               )

          st.write(response)

      elif st.session_state.choice == "조용한 화면":
          show_calm_screen()

        st.markdown("</div>", unsafe_allow_html=True)

        current_log = {
            "emotion": emotion,
            "intensity": intensity,
            "time": datetime.now(),
            "text": st.session_state.get("user_text", ""),
        }
        preview_state = detect_state(st.session_state.logs + [current_log])

        st.markdown(emotion_card(emotion, intensity, preview_state), unsafe_allow_html=True)
        show_state_badge(emotion, preview_state)
        st.caption(f"{secondary_emotion} • 원인: {cause}")
        save_autism_mode_log_once()

        if st.button("다시 시작", key="autism_restart"):
            reset_autism_mode()
            st.rerun()

    if st.session_state.logs:
        render_emotion_flow(st.session_state.logs)
        render_time_chart(st.session_state.logs)

    if len(st.session_state.logs) > 1:
           df = pd.DataFrame(st.session_state.logs)

    st.markdown('</div>', unsafe_allow_html=True)
# ---------------------------------
# 세션 상태 초기화
# ---------------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "일반 모드"

if "logs" not in st.session_state:
    st.session_state.logs = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  

if "step" not in st.session_state:
    st.session_state.step = 1

if "emotion" not in st.session_state:
    st.session_state.emotion = "모르겠음"

if "intensity" not in st.session_state:
    st.session_state.intensity = "보통"

if "sensory" not in st.session_state:
    st.session_state.sensory = "없음"

if "user_text" not in st.session_state:
    st.session_state.user_text = ""

if "choice" not in st.session_state:
    st.session_state.choice = "진정"

if "autism_result_saved" not in st.session_state:
    st.session_state.autism_result_saved = False
   
# ---------------------------------
# 스타일
# ---------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2rem;
        max-width: 760px;
    }
    button[kind="primary"] {
        background-color: black;
        color: white;
        border-radius: 10px;
        height: 48px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------
# 상단 UI
# ---------------------------------
st.title("정서로")
st.caption("감정을 기록하고, 이해하고, 천천히 정리하는 공간")

st.subheader("모드 선택")
mode = st.radio("모드 선택", ["일반 모드", "자폐 친화 모드"], horizontal=True)
st.session_state.mode = mode

# ---------------------------------
# 본문
# ---------------------------------
if st.session_state.mode == "일반 모드":
    show_general_mode()
else:
    show_autism_mode()
