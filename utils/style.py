def get_emotion_color(emotion):
    mapping = {
        "불안": "#5DADE2",
        "초조": "#85C1E9",
        "압박감": "#3498DB",
        "우울": "#2C3E50",
        "무기력": "#34495E",
        "공허함": "#5D6D7E",
        "분노": "#E74C3C",
        "짜증": "#EC7063",
        "행복": "#F7DC6F",
        "설렘": "#F5B041"
    }
    return mapping.get(emotion, "#95A5A6")