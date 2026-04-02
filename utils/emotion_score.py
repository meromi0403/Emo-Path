def emotion_score(emotion):
    mapping = {
        "행복": 80,
        "불안": 40,
        "우울": 20,
        "분노": 30
    }
    return mapping.get(emotion, 50)