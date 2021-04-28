import datetime
import calendar
from numpy import count_nonzero

NEXT_MONTH = False


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    if NEXT_MONTH:
        month += 1
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]


def get_days_in_week_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    if NEXT_MONTH:
        month += 1
    weeks = calendar.monthcalendar(year, month)
    days_in_week = [count_nonzero(week) for week in weeks]
    return days_in_week
