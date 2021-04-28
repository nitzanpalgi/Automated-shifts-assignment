import math


def is_task_in_week(week_num, task):
    return math.floor(task["start_time"].day / 7) == week_num


def is_task_overlapping(task_a, task_b):
    return not all(task_a == task_b) and are_intervals_overlap((task_a['start_time'], task_a['end_time']),
                                                               (task_b['start_time'], task_b['end_time']))


def are_intervals_overlap(interval_a, interval_b):
    return interval_a[0] <= interval_b[0] <= interval_a[1] or interval_b[0] <= interval_a[0] <= interval_b[1]


def is_task_holiday(task):
    return task["is_weekend"] == 1


def is_task_night(task):
    return task["start_time"].hour > 19


def is_task_in_group(task, group):
    return task["compat_group"] == group["name"]


def is_task_in_a_day(task, day):
    return task["start_time"].date() == day
