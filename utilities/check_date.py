from datetime import datetime

def check_date(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        return None, "invalid date format."
    
    today = datetime.now().date()
    if date < today:
        return None, "Date is in the past."

    return date, "Date is valid."