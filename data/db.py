import sqlite3

def init_db():
    conn = sqlite3.connect("emotion.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        text TEXT,
        emotion TEXT,
        intensity INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_log(text, emotion, intensity):
    conn = sqlite3.connect("emotion.db")
    c = conn.cursor()

    c.execute("INSERT INTO logs (text, emotion, intensity) VALUES (?, ?, ?)",
              (text, emotion, intensity))

    conn.commit()
    conn.close()


def load_logs():
    conn = sqlite3.connect("emotion.db")
    c = conn.cursor()

    c.execute("SELECT emotion, intensity FROM logs")
    data = c.fetchall()

    conn.close()
    return data

def get_emotion_stats():
    conn = sqlite3.connect("emotion.db")
    c = conn.cursor()

    c.execute("SELECT emotion FROM logs")
    data = c.fetchall()

    conn.close()

    emotions = [e[0] for e in data]

    stats = {}
    for e in emotions:
        stats[e] = stats.get(e, 0) + 1

    return stats