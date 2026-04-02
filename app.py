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
    <div style="
        padding: 20px;
        border-radius: 16px;
        background-color: #eef6ee;
        border: 1px solid #b7d3b7;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    ">
        <h3 style="margin-bottom: 10px;">천천히 숨 쉬기</h3>
        <p style="font-size: 18px;">4초 들이마시기</p>
        <p style="font-size: 18px;">4초 멈추기</p>
        <p style="font-size: 18px;">4초 내쉬기</p>
        <p style="margin-top: 10px;">천천히 따라 해봐.</p>
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

    if st.button("AI 응답 받기"):
        emotion = analyze_emotion(user_input)

        response = generate_response(
            user_input=user_input,
            emotion=emotion,
            mode="일반 모드"
        )

        st.session_state.logs.append({
            "emotion": emotion,
            "text": user_input
        })

        st.subheader("AI 응답")
        st.write(response)


# ===========================
# 🟢 자폐 친화 모드 (핵심🔥)
# ===========================
else:

    # 1단계: 감정
    if st.session_state.step == 1:
        st.subheader("지금 상태를 골라줘")

        emotion = st.selectbox("감정", [
            "불안", "화남", "슬픔", "피곤함", "기쁨", "괜찮음", "모르겠음"
        ])

        if st.button("다음"):
            st.session_state.emotion = emotion
            st.session_state.step = 2


    # 2단계: 강도
    elif st.session_state.step == 2:
        st.subheader("얼마나 강해?")

        intensity = st.radio("강도", ["약함", "보통", "강함"])

        if st.button("다음"):
            st.session_state.intensity = intensity
            st.session_state.step = 3


    # 3단계: 감각 상태
    elif st.session_state.step == 3:
        st.subheader("지금 뭐가 힘들어?")

        sensory = st.selectbox("선택", [
            "소리", "빛", "복잡함", "말하기", "없음"
        ])

        if st.button("다음"):
            st.session_state.sensory = sensory
            st.session_state.step = 4


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

        emotion = st.session_state.emotion

        st.subheader("결과")

        if st.session_state.choice == "진정":
            show_breathing_box()

        elif st.session_state.choice == "짧은 말":
            response = generate_response(
                user_input=emotion,
                emotion=emotion,
                mode="자폐 친화 모드"
            )
            st.write(response)

        elif st.session_state.choice == "조용한 화면":
            show_calm_screen()

        # 기록 저장
        st.session_state.logs.append({
            "emotion": st.session_state.emotion,
            "intensity": st.session_state.intensity,
            "sensory": st.session_state.sensory
        })

        if st.button("다시 시작"):
            st.session_state.step = 1

if st.button("분석하기"):
   
    danger_keywords = ["죽고 싶", "사라지고 싶", "힘들어 죽겠"]

    if any(word in user_input for word in danger_keywords):
        st.error("지금 많이 힘든 상태인 것 같아. 혼자 버티지 않아도 괜찮아.")
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
   