from pandas import DataFrame
import numpy as np
from utils.model_utils import get_taken_tasks_per_operator
from utils.stats_utils import calc_grade, get_operator_unwanted_tasks, get_permutation_by_name


def add_statistics(shifts_model, assignment_mat: DataFrame, operators_df: DataFrame, tasks: DataFrame):
    operators = [(oper_index, operator) for oper_index, operator in operators_df.iterrows()]
    add_capacity_stats(shifts_model, assignment_mat, operators, tasks)
    add_unwanted_tasks_stats(shifts_model, assignment_mat, operators, tasks)


def add_capacity_stats(shifts_model, assignment_mat: DataFrame, operators, tasks: DataFrame):
    capacities = []
    target_capacities = []
    grade_capacities = []
    weekend_capacities = []
    target_weekend_capacities = []
    grade_weekend_capacities = []
    total_grade = []

    taken_tasks_per_operator = get_taken_tasks_per_operator(shifts_model)

    for oper_index, operator in operators:
        taken_tasks_by_operator = tasks.iloc[taken_tasks_per_operator[oper_index]]
        taken_work_week_capacity = sum(taken_tasks_by_operator['cost'])
        taken_weekend_capacity = sum(taken_tasks_by_operator[taken_tasks_by_operator["is_weekend"] == 1]['cost'])

        capacities += [taken_work_week_capacity]
        target_capacities += [operator['MAX']]
        weekend_capacities += [taken_weekend_capacity]
        target_weekend_capacities += [operator['MAX_Sofashim']]
        grade_capacities += [calc_grade(taken_work_week_capacity, operator['MAX'])]
        grade_weekend_capacities += [calc_grade(taken_weekend_capacity, operator['MAX_Sofashim'])]
        total_grade += [((calc_grade(taken_work_week_capacity, operator['MAX'])) + (
            calc_grade(taken_weekend_capacity, operator['MAX_Sofashim']))) / 2]

    sorted_permutation = get_permutation_by_name(assignment_mat, operators)
    assignment_mat['capacities'] = np.array(capacities)[sorted_permutation]
    assignment_mat['target capacities'] = np.array(target_capacities)[sorted_permutation]
    assignment_mat['Weekend capacities'] = np.array(weekend_capacities)[sorted_permutation]
    assignment_mat['Target weekend capacities'] = np.array(target_weekend_capacities)[sorted_permutation]
    assignment_mat['capacities grade'] = np.array(grade_capacities)[sorted_permutation]
    assignment_mat['weekend capacities grade'] = np.array(grade_weekend_capacities)[sorted_permutation]
    assignment_mat['Total grades'] = np.array(total_grade)[sorted_permutation]


def add_unwanted_tasks_stats(shifts_model, assignment_mat: DataFrame, operators, tasks: DataFrame):
    unwanted_evenings_stats = []

    taken_tasks_per_operator = get_taken_tasks_per_operator(shifts_model)

    for oper_index, operator in operators:
        unwanted_tasks_df = get_operator_unwanted_tasks(oper_index, operator, taken_tasks_per_operator, tasks)
        string_to_print = '\n'.join(
            f'got unwanted evening: {unwanted_task["name"]} at {unwanted_task["start_time"]}' for _, unwanted_task in
            unwanted_tasks_df.iterrows())
        unwanted_evenings_stats += [string_to_print]

    sorted_permutation = get_permutation_by_name(assignment_mat, operators)
    assignment_mat['unwanted evenings'] = np.array(unwanted_evenings_stats)[sorted_permutation]
