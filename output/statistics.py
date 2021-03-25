from pandas import DataFrame
import numpy as np
from collections import defaultdict
from functions import dont_want_task


def add_statistics(shifts_model, assignment_mat: DataFrame, operators_df: DataFrame, tasks: DataFrame):
    operators = [(oper_index, operator) for oper_index, operator in operators_df.iterrows()]
    add_capacity_stats(shifts_model, assignment_mat, operators, tasks)
    add_unwanted_tasks_stats(shifts_model, assignment_mat, operators, tasks)


def add_capacity_stats(shifts_model, assignment_mat: DataFrame, operators, tasks: DataFrame):
    capacities = []

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
        capacities += [f"taken work week capacity: {taken_work_week_capacity}, target capacity {operator['MAX']}\n"
                       f"taken weekend capacity: {taken_weekend_capacity}, target capacity {operator['MAX_Sofashim']}"]
    assignment_mat['capacities'] = capacities


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
