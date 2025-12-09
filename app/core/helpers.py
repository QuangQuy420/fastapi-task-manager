import datetime

def format_date_to_string(date):
    if isinstance(date, (datetime.date, datetime.datetime)):
        return date.isoformat()
    return date
