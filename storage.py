from collections import defaultdict
import datetime

# Хранилище фидбеков
feedbacks = []

# Защита от спама
last_feedback_time = defaultdict(lambda: datetime.datetime.min)

def add_feedback(user, feedback_type, text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedbacks.append({
        "timestamp": timestamp,
        "user": user,
        "type": feedback_type,
        "text": text
    })
    print(f"[СОХРАНЕНО] {timestamp} | {user} | {feedback_type} | {text[:1000]}...", flush=True)
    return timestamp

def get_feedbacks(limit=50):
    return feedbacks[-limit:]

def is_spam(user_id):
    now = datetime.datetime.now()
    if (now - last_feedback_time[user_id]).total_seconds() < 30:
        return True, int(30 - (now - last_feedback_time[user_id]).total_seconds())
    return False, 0

def update_last_time(user_id):
    last_feedback_time[user_id] = datetime.datetime.now()