import datetime
import calendar


def is_operator_qualified(operator, task):
    return task.type in operator.qualified_tasks


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]
