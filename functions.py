import datetime
import calendar


def is_operator_qualified(operator, task):
    if task['id'] is not None:
        return task['id'] in operator['tasks available']


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]


def is_task_overlapping(task_a, task_b):
    return task_a.start_time <= task_b.start_time <= task_a.end_time or \
           task_b.start_time <= task_a.start_time <= task_b.end_time
