def recommend_action(emotion):
    if "불안" in emotion:
        return "👉 1분 동안 천천히 호흡해봐 (4초 들이마시고 6초 내쉬기)"
    elif "우울" in emotion:
        return "👉 오늘 가장 작은 할 일 하나만 해보자"
    elif "분노" in emotion:
        return "👉 잠깐 자리에서 벗어나서 2분 정도 걸어보자"
    else:
        return "👉 물 한 잔 마시고 잠깐 쉬어도 괜찮아"
    
def robot_signal(emotion, intensity):
    if "불안" in emotion:
        return "BLUE_LED"
    elif "우울" in emotion:
        return "DIM_LIGHT"
    elif "행복" in emotion:
        return "YELLOW_LED"
    elif "분노" in emotion:
        return "RED_LED"
    else:
        return "NEUTRAL"