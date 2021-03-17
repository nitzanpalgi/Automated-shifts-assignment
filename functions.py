import datetime
import calendar
from numpy import count_nonzero
import math


def is_operator_capable(operator, task):
    return is_operator_qualified(operator, task) and is_operator_strong_no_task(operator, task)


def is_operator_qualified(operator, task):
    return task['type'] in operator['qualified tasks']


def is_operator_strong_no_task(operator, task):
    not_task_days = [int(num) for num in str(operator['Not task']).split(',') if num != 'nan']
    return not task['start_time'].day in not_task_days


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]


def get_days_in_week_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    month = month + 1
    weeks = calendar.monthcalendar(year, month)
    days_in_week = [count_nonzero(week) for week in weeks]
    return days_in_week


def is_task_in_week(week_num, task):
    return math.floor(task["start_time"].day / 7) == week_num


def is_task_overlapping(task_a, task_b):
    return not all(task_a == task_b) and \
           (task_a['start_time'] <= task_b['start_time'] <= task_a['end_time'] or
            task_b['start_time'] <= task_a['start_time'] <= task_b['end_time'])


def is_task_holiday(task):
    return task["is_weekend"] == 1
