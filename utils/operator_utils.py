import datetime

from Modules.dataImporter import get_task_types_df
from utils.task_utils import are_intervals_overlap


def is_operator_capable(operator, task):
    return is_operator_qualified(operator, task) and not is_operator_strong_no_task(operator, task)


def is_operator_qualified(operator, task):
    return task['type'] in operator['qualified tasks']


def is_operator_strong_no_task(operator, task):
    not_task_days = [int(num) for num in str(operator['Not task']).split(',') if num != 'nan']
    return task['start_time'].day in not_task_days


def dont_want_task(operator, task):
    if str(operator["Not evening"]) == 'nan':
        return False
    unwanted_evenings = str(operator["Not evening"]).split(',')
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month

    return any(
        are_intervals_overlap((task["start_time"], task["end_time"]), (
            datetime.datetime(year=year, month=month, day=int(evening), hour=18),
            datetime.datetime(year=year, month=month, day=int(evening), hour=23, minute=59)))
        for evening in unwanted_evenings)


def get_minimal_capacity_of_operator(operator):
    task_types = [task_type for task_type in get_task_types_df().iterrows()]
    return sum([taskType["min_per_month"] for _, taskType in task_types if is_operator_qualified(operator, taskType)])
