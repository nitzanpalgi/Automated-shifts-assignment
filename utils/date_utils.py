import datetime
import calendar
import numpy as np

NEXT_MONTH = False
HOLIDAY_ARRAY = []


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
    # TODO use IL weeks not US weeks
    weeks = calendar.monthcalendar(year, month)
    days_in_week = [np.count_nonzero(week) for week in weeks]
    return days_in_week


def us_day_to_il_day(day):
    return (day + 1) % 7


def is_first_day_of_the_month_saturday():
    return get_days_in_current_month()[0].day == 2


def get_holiday_array():
    return HOLIDAY_ARRAY


def update_holiday_array(holiday_df):
    global HOLIDAY_ARRAY
    HOLIDAY_ARRAY = np.array(holiday_df['dates'][0].split(','), dtype=int)


FIRST_DAY_OF_THE_MONTH_IS_SATURDAY = is_first_day_of_the_month_saturday()
