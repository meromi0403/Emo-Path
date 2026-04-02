import streamlit as st
from data.db import init_db
init_db()
from core.emotion import analyze_emotion
from core.response import generate_response
from core.recommend import recommend_action
from data.db import save_log, load_logs
from utils.style import get_emotion_color
from data.db import load_logs
from data.db import get_emotion_stats
from core.recommend import robot_signal
from utils.emotion_score import emotion_score
from utils.style import get_emotion_color
import pandas as pd


if "mode" not in st.session_state:
    st.session_state.mode = "일반 모드"

if "logs" not in st.session_state:
    st.session_state.logs = []
 
if "step" not in st.session_state:
    st.session_state.step = 1

def recommend_intensity(text):
    if not text:
        return None

    if any(word in text for word in ["너무", "진짜", "완전", "미치겠"]):
        return "강함"
    elif any(word in text for word in ["조금", "약간"]):
        return "약함"

    return "보통"

def get_emotion_color(emotion):
    colors = {
        "불안": "#d4edda",
        "화남": "#cce5ff",
        "슬픔": "#e2e3e5",
        "피곤함": "#f8f9fa",
        "기쁨": "#fff3cd",
        "괜찮음": "#d1ecf1",
        "모르겠음": "#eeeeee"
    }
    return colors.get(emotion, "#ffffff")

def recommend_from_text(text):
    if not text:
        return None

    if any(word in text for word in ["시끄러", "소리", "떠들", "소음"]):
        return "소리"
    elif any(word in text for word in ["밝", "눈부", "빛"]):
        return "빛"
    elif any(word in text for word in ["복잡", "생각 많", "머리 아픔"]):
        return "복잡함"
    elif any(word in text for word in ["말하기", "대화", "대답"]):
        return "말하기"

    return None

def get_calm_actions(emotion):
    action_map = {
        "불안": ["숨 쉬기", "잠깐 쉬기"],
        "슬픔": ["조용히 있기", "따뜻한 말 보기"],
        "화남": ["잠깐 멈추기", "감정 다시 고르기"],
        "피곤함": ["눈 쉬기", "물 마시기"],
        "기쁨": ["기록 남기기", "좋은 이유 적기"],
        "괜찮음": ["지금 상태 유지하기", "감정 기록하기"],
        "모르겠음": ["천천히 생각하기", "다시 고르기"]
    }
    return action_map.get(emotion, ["잠깐 쉬기", "다시 해보기"])

def show_breathing_box():
    st.markdown("""
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
        50% { transform: scale(1.5); }
        100% { transform: scale(1); }
    }
    </style>

    <div style="text-align:center;">
        <h3>천천히 숨 쉬기</h3>
        <div class="breath-circle"></div>
        <p>원이 커질 때 들이마시고</p>
        <p>작아질 때 내쉬어</p>
    </div>
    """, unsafe_allow_html=True)

def show_calm_screen():
    st.markdown("""
    <div style="padding:40px;text-align:center;background:#f5f5f5;border-radius:20px;">
        <h2>괜찮아</h2>
        <p>지금은 쉬어도 돼</p>
    </div>
    """, unsafe_allow_html=True)

def emotion_card(emotion, intensity, color):
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}, #000000);
        padding:25px;
        border-radius:20px;
        color:white;
        text-align:center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
    ">
        <h2>{emotion}</h2>
        <p style="font-size:18px;">강도 {intensity}</p>
    </div>
    """

st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    button[kind="primary"] {
        background-color: black;
        color: white;
        border-radius: 10px;
        height: 50px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("정서로")
st.caption("감정을 기록하고, 이해하고, 천천히 정리하는 공간")
st.set_page_config(page_title="정서로", page_icon="🫧", layout="centered")
def show_step_progress():
    step = st.session_state.step
    total = 5

    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-weight:600;">진행 단계: {step} / {total}</div>
        <div style="
            height:10px;
            background:#eee;
            border-radius:10px;
            overflow:hidden;
        ">
            <div style="
                width:{(step/total)*100}%;
                height:100%;
                background:#6c9cff;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("모드 선택")

# ---------------------------
# 모드 선택
# ---------------------------
mode = st.radio("모드 선택", ["일반 모드", "자폐 친화 모드"])
st.session_state.mode = mode


# ===========================
# 🔵 일반 모드
# ===========================
if st.session_state.mode == "일반 모드":

    user_input = st.text_area("오늘 기분을 적어줘")

if st.button("분석하기"):
   
    danger_keywords = ["죽고싶", "자살", "사라지고싶", "힘들다", "끝내고싶다"]

    user_input = st.session_state.get("user_text", "") or st.session_state.get("emotion", "")

    if any(word in user_input for word in danger_keywords):
        st.warning("지금 많이 힘든 상태로 보여. 혼자 버티지 않아도 괜찮아.")
        st.write("👉 1393 자살 예방 상담 전화")

    if user_input.strip() == "":
        st.warning("조금만 적어줘 :)")
    else:
        emotion = analyze_emotion(user_input)
        logs = load_logs()

        history = ""
        stats = ""

        if "logs" not in st.session_state:
            st.session_state.logs = []

        if len(st.session_state.logs) > 0:
            recent = st.session_state.logs[-5:]
            history = " → ".join([log["emotion"] for log in recent])

            emotion_count = {}
            for log in st.session_state.logs:
                emo = log["emotion"]
                emotion_count[emo] = emotion_count.get(emo, 0) + 1

            stats = ", ".join([f"{k}: {v}회" for k, v in emotion_count.items()])
        response = generate_response(user_input, history, stats)
        action = recommend_action(emotion["primary_emotion"])
        signal = robot_signal(
            emotion["primary_emotion"],
            emotion["intensity"]
        )

        st.write("🤖 로봇 반응:", signal)
        
#저장        
        save_log(user_input, emotion["primary_emotion"], emotion["intensity"])

        st.divider()

       
#감정카드 
    color = get_emotion_color(emotion["primary_emotion"])

    st.markdown(emotion_card(
    emotion["primary_emotion"],
    emotion["intensity"],
    color
), unsafe_allow_html=True)
    
    if st.session_state.mode == "calm":
        st.markdown(f"""
        <div style='padding:16px; border-radius:12px; border:1px solid #ccc; background-color:#f7f7f7;'>
            <b>최근 감정 흐름</b><br>
            {' → '.join(emotion)}
        </div>
        """, unsafe_allow_html=True)   


# 공감
    st.subheader("💬 공감")
    st.write(response)

 # 행동
    st.subheader("🌿 추천")
    st.success(action)


# 그래프
    logs = load_logs()

    if logs:
        recent = logs[-5:]
        emotions = [e[0] for e in recent]

        colored_flow = " → ".join([
            f"<span style='color:{get_emotion_color(e)}'>{e}</span>"
            for e in emotions
         ])

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.08);
            padding:20px;
            border-radius:15px;
            border:1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            margin-top:20px;
        ">
            <h4 style="margin-bottom:10px;">🧠 감정 흐름</h4>
            <p style="font-size:18px; text-align:center;">
                {colored_flow}
            </p>
        </div>
        """, unsafe_allow_html=True)

    if logs:
        df = pd.DataFrame(logs, columns=["emotion", "intensity"])
        df["score"] = df["emotion"].apply(emotion_score)

        st.subheader("📊 감정 흐름 그래프")
        st.line_chart(df["score"])   

    if logs:
        emotions = [e[0] for e in logs]
   
        most_common = max(set(emotions), key=emotions.count)
        st.subheader("📌 최근 감정 패턴")
        st.info(f"요즘 가장 많이 느끼는 감정은 **{most_common}** 이야")

    if len(logs) >= 3:
        recent = [e[0] for e in logs[-3:]]

    if recent.count("불안") >= 2:
        st.warning("요즘 불안한 상태가 계속 이어지고 있어 보여")
   


# ===========================
# 🟢 자폐 친화 모드 (핵심🔥)
# ===========================
else:

    # 1단계: 감정
    if st.session_state.step == 1:
       st.subheader("지금 상태를 골라줘")

       st.selectbox(
            "감정",
            ["불안", "화남", "슬픔", "피곤함", "기쁨", "괜찮음", "모르겠음"],
            key="emotion"
        )

       st.text_input("말하기 (선택)", key="user_text")

       if st.button("다음", key="nextlevel1"):
           st.session_state.step = 2      

    # 2단계: 강도
    elif st.session_state.step == 2:

        user_text = st.session_state.get("user_text", "")

        recommended_intensity = recommend_intensity(user_text)

        intensity = st.radio(
            "강도",
            ["약함", "보통", "강함"],
            index=["약함", "보통", "강함"].index(recommended_intensity) if recommended_intensity else 1,
            key="intensity_radio"
        )

        if st.button("다음", key="step2_next"):
            st.session_state.intensity = intensity
            st.session_state.step = 3



    # 3단계: 감각 상태
    elif st.session_state.step == 3:

        user_text = st.session_state.get("user_text", "")
        recommended = recommend_from_text(user_text)

         # 🔥 자동 스킵
        if recommended:
            st.session_state.sensory = recommended
            st.session_state.step = 4
            st.rerun()

        st.subheader("지금 뭐가 힘들어?")

        if recommended:
            st.info(f"👉 '{recommended}' 때문일 가능성이 있어")

        sensory = st.selectbox(
            "선택",
            ["소리", "빛", "복잡함", "말하기", "없음"],
            index=["소리", "빛", "복잡함", "말하기", "없음"].index(recommended) if recommended else 0
         )
        

    # 4단계: 도움 선택
    elif st.session_state.step == 4:
        st.subheader("어떤 도움을 받을래?")

        choice = st.radio("선택", [
            "진정", "짧은 말", "조용한 화면"
        ])

        if st.button("시작"):
            st.session_state.choice = choice
            st.session_state.step = 5


    # 5단계: 결과
    elif st.session_state.step == 5:

        emotion = st.session_state.emotion("emotion", "모르겠음")
        bg_color = get_emotion_color(emotion)

        st.markdown(f"""
        <div style="
            padding:20px;
            border-radius:16px;
            background:{bg_color};
            margin-bottom:15px;
        ">
        """, unsafe_allow_html=True)

        st.subheader("결과")

        if st.session_state.choice == "진정":
            show_breathing_box()

        elif st.session_state.choice == "짧은 말":

            user_input = f"""
            감정: {st.session_state.emotion}
            강도: {st.session_state.intensity}
            감각: {st.session_state.sensory}
            추가 입력: {st.session_state.user_text}
            """

            response = generate_response(
               user_input=user_input,
               emotion=st.session_state.emotion,
               mode="자폐 친화 모드"
            )

            st.write(response)

        elif st.session_state.choice == "조용한 화면":
            show_calm_screen()
        st.markdown("</div>", unsafe_allow_html=True)

        # 기록 저장
        st.session_state.logs.append({
            "emotion": st.session_state.emotion,
            "intensity": st.session_state.intensity,
            "sensory": st.session_state.sensory
        })

        if st.button("다시 시작"):
            st.session_state.step = 1

