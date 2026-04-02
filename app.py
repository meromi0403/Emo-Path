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

st.set_page_config(layout="centered")

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

st.markdown("""
<h1 style='text-align: center;'>💚 정서로 💚</h1>
<p style='text-align: center; color: gray;'>너의 감정을 이해하는 AI</p>
""", unsafe_allow_html=True)


mode = st.radio(
    "모드 선택",
    ["일반 모드", "단순 소통 모드"]
)

user_input = st.text_area("오늘 마음을 조금만 들려줄래?", height=150)

if mode == "단순 소통 모드":
    quick_choice = st.radio(
        "지금 기분 선택",
        ["좋아", "별로야", "모르겠어"]
    )

    if quick_choice:
        user_input = quick_choice

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
        if logs:
            history = ", ".join([e[0] for e in logs[-3:]])

        stats = get_emotion_stats()
        response = generate_response(user_input, history, stats, mode)
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


# 공감
    st.subheader("💬 공감")
    st.write(response)

 # 행동
    st.subheader("🌿 추천")
    st.success(action)

#단순 모드 UI
    if mode == "단순 소통 모드":
        st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
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
   