from pandas import DataFrame
import numpy as np
from collections import defaultdict
from functions import dont_want_task
import time

def add_statistics(shifts_model, assignment_mat: DataFrame, operators_df: DataFrame, tasks: DataFrame):
    assign_empty_values(assignment_mat)
    operators = [(oper_index, operator) for oper_index, operator in operators_df.iterrows()]
    add_capacity_stats(shifts_model, assignment_mat, operators, tasks)
    add_unwanted_tasks_stats(shifts_model, assignment_mat, operators, tasks)

def assign_empty_values(assignment_mat):
    assignment_mat['capacities'] = ''
    assignment_mat['target capacities'] = ''


def add_capacity_stats(shifts_model, assignment_mat: DataFrame, operators, tasks: DataFrame):
    capacities = []
    target_capacities = []
    grade_capacities = []
    weekend_capacities = []
    target_weekend_capacities = []
    grade_weekend_capacities = []
    total_grade = []

    taken_tasks_per_operator = defaultdict(list)
    for v in shifts_model.vars:
        if v.name[0] == 'x' and v.x > 0:
            oper_id = int(v.name.split(',')[0][2:])
            task_id = int(v.name.split(',')[1][:-1])
            taken_tasks_per_operator[oper_id].append(task_id)

    for oper_index, operator in operators:
        taken_tasks_by_operator = tasks.iloc[taken_tasks_per_operator[oper_index]]
        taken_work_week_capacity = sum(taken_tasks_by_operator[taken_tasks_by_operator["is_weekend"] == 0]['cost'])
        taken_weekend_capacity = sum(taken_tasks_by_operator[taken_tasks_by_operator["is_weekend"] == 1]['cost'])
        # capacities += [f"taken work week capacity: {taken_work_week_capacity}, target capacity {operator['MAX']}\n"
        #                f"taken weekend capacity: {taken_weekend_capacity}, target capacity {operator['MAX_Sofashim']}"]

        capacities += [taken_work_week_capacity]
        target_capacities += [operator['MAX']]
        weekend_capacities += [taken_weekend_capacity]
        target_weekend_capacities += [operator['MAX_Sofashim']]
        grade_capacities += [calc_grade(taken_work_week_capacity,operator['MAX'])]
        grade_weekend_capacities += [calc_grade(taken_weekend_capacity,operator['MAX_Sofashim'])]
        total_grade += [((calc_grade(taken_work_week_capacity,operator['MAX'])) + (calc_grade(taken_weekend_capacity,operator['MAX_Sofashim'])))/2]

    assignment_mat['capacities'] = capacities
    assignment_mat['target capacities'] = target_capacities
    assignment_mat['Weekend capacities'] = weekend_capacities
    assignment_mat['Target weekend capacities'] = target_weekend_capacities
    assignment_mat['capacities grade'] = grade_capacities
    assignment_mat['weekend capacities grade'] = grade_weekend_capacities
    assignment_mat['Total grades'] = total_grade


def calc_grade(top, bottom):
    if bottom == 0:
        return 1
    return top/bottom


def add_unwanted_tasks_stats(shifts_model, assignment_mat: DataFrame, operators, tasks: DataFrame):
    unwanted_evenings_stats = []

    taken_tasks_per_operator = defaultdict(list)
    for v in shifts_model.vars:
        if v.name[0] == 'x' and v.x > 0:
            oper_id = int(v.name.split(',')[0][2:])
            task_id = int(v.name.split(',')[1][:-1])
            taken_tasks_per_operator[oper_id].append(task_id)

    for oper_index, operator in operators:
        taken_tasks_by_operator = tasks.iloc[taken_tasks_per_operator[oper_index]]
        unwanted_tasks_df = taken_tasks_by_operator.loc[
            taken_tasks_by_operator.apply(lambda task: dont_want_task(operator, task), axis=1)]
        string_to_print = '\n'.join(
            f'got unwanted evening: {unwanted_task["name"]} at {unwanted_task["start_time"]}' for _, unwanted_task in
            unwanted_tasks_df.iterrows())
        unwanted_evenings_stats += [string_to_print]

    assignment_mat['unwanted evenings'] = unwanted_evenings_stats
