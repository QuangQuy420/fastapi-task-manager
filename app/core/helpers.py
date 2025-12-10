import datetime
import math


def format_date_to_string(date):
    if isinstance(date, (datetime.date, datetime.datetime)):
        return date.isoformat()
    return date


def get_total_pages(total, page_size):
    return math.ceil(total / page_size) if total > 0 else 0
