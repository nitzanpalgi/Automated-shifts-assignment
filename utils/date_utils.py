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
    all_days_in_month = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
    if us_day_to_il_day(all_days_in_month[0].weekday()) == 6:
        all_days_in_month = all_days_in_month[1:]

    return all_days_in_month


def get_days_in_week_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    if NEXT_MONTH:
        month += 1
    weeks = calendar.monthcalendar(year, month)
    days_in_week = [count_nonzero(week) for week in weeks]
    return days_in_week


def us_day_to_il_day(day):
    return (day + 1) % 7


def is_first_day_of_the_month_saturday():
    return get_days_in_current_month()[0].day == 2


FIRST_DAY_OF_THE_MONTH_IS_SATURDAY = is_first_day_of_the_month_saturday()
