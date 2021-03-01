import datetime
import calendar


def is_operator_qualified(operator, task):
        return task['type'] in operator['qualified tasks']


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    month = month + 1
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]


def is_task_overlapping(task_a, task_b):
    return not all(task_a == task_b) and \
           (task_a['start_time'] <= task_b['start_time'] <= task_a['end_time'] or
            task_b['start_time'] <= task_a['start_time'] <= task_b['end_time'])
