from datetime import datetime

def check_date(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception as e:
        return None
    
    today = datetime.now()
    if date < today:
        return None

    return date