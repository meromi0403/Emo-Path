def get_emotion_color(emotion):
    if "불안" in emotion:
        return "#5DADE2"  # 파랑
    elif "우울" in emotion:
        return "#2C3E50"  # 어두운
    elif "행복" in emotion:
        return "#F7DC6F"  # 노랑
    elif "분노" in emotion:
        return "#E74C3C"  # 빨강
    else:
        return "#95A5A6"  # 회색