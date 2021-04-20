from mip import Model, xsum, BINARY, CONTINUOUS, minimize
from functions import *
from Modules.dataImporter import get_tasks_type_df
from constants import *
import math
import numpy as np


def init_constraints(tasks_df, operators_df):
    shifts_model = Model()

    operators = [row for row in operators_df.iterrows()]
    tasks = [row for row in tasks_df.iterrows()]

    x_mat = add_vars(shifts_model, operators, tasks)
    s_weekly_capacity = add_weekly_capacity_slack_vars(shifts_model, operators)
    s_variety = add_variety_slack_vars(shifts_model, operators)

    shifts_model.objective = minimize(
        xsum(task_x * get_operator_task_cost(operators[operator_id][1], tasks[task_id][1])
             for operator_id, operator in enumerate(x_mat)
             for task_id, task_x in operator.items()
             ) +
        xsum(100 * s_variety[operator_id] / operator["pazam"] for operator_id, operator in operators) +

        xsum(10 * s_weekly_capacity[operator_id][week_id]
             for operator_id, operator in operators
             for week_id, days_in_week in enumerate(get_days_in_week_in_current_month())
             )
    )

    add_all_tasks_are_assigned_constrains(shifts_model, x_mat, operators, tasks)
    add_task_overlap_constrains(shifts_model, x_mat, operators, tasks)
    add_operator_capacity_constraint_not_weekend(shifts_model, x_mat, operators, tasks, MAX_CAPACITY_NOT_WEEKEND,
                                                MIN_CAPACITY_NOT_WEEKEND)
    add_operator_capacity_constraint_weekend(shifts_model, x_mat, operators, tasks, INCREASE_MAX_SOFASHIM)
    add_operator_min_per_month_constraint(shifts_model, x_mat, operators, tasks)
    add_weekly_capacity_constraint(shifts_model, x_mat, s_weekly_capacity, operators, tasks, MAX_WEEKLY_CAPACITY)
    add_variety_constraint(shifts_model, x_mat, s_variety, operators, tasks)
    add_operator_capacity_constraint_nights(shifts_model, x_mat, operators, tasks, MAX_NIGHT_CAPACITY)

    return shifts_model


def get_operator_task_cost(operator, task):
    if dont_want_task(operator, task):
        return (operator["pazam"] ** 2) * (task["cost"] + 10)
    else:
        return (operator["pazam"] ** 2) * task["cost"]


def add_vars(shifts_model, operators, tasks):
    return [
        {task_id: shifts_model.add_var(f'x({operator_id},{task_id})', var_type=BINARY)
         for task_id, task in tasks
         if is_operator_capable(operator, task)}
        for operator_id, operator in operators
    ]


def add_variety_slack_vars(shifts_model, operators):
    return [
        shifts_model.add_var(f's_variety({operator_id})', var_type=CONTINUOUS)
        for operator_id, operator in operators
    ]


def add_weekly_capacity_slack_vars(shifts_model, operators):
    return [
        [shifts_model.add_var(f'weekly capacity({operator_id},{week_id})', var_type=CONTINUOUS)
         for week_id, days_in_week in enumerate(get_days_in_week_in_current_month())]
        for operator_id, operator in operators
    ]


def add_all_tasks_are_assigned_constrains(model, x_mat, operators, tasks):
    for task_id, task in tasks:
        model += xsum(x_mat[operator_id][task_id] for operator_id, operator in operators
                      if is_operator_capable(operator, task)) == 1, f'task({task_id})'


def add_task_overlap_constrains(model, x_mat, operators, tasks):
    for day in get_days_in_current_month():
        relevant_tasks = [(task_id, task) for task_id, task in tasks if task["start_time"] <= day <= task["end_time"]]
        for operator_id, operator in operators:
            model += xsum(
                x_mat[operator_id][task_id] for task_id, task in relevant_tasks
                if is_operator_capable(operator, task)) <= 1, f'overlapping-({operator_id},{day.day}))'


def add_operator_capacity_constraint_not_weekend(model, x_mat, operators, tasks, max_config, min_config):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task) and not is_task_holiday(task)
        ) <= operator["MAX"] * max_config, f'max capacity-({operator_id})'

    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task) and not is_task_holiday(task)
        ) >= operator["MAX"] * min_config, f'min capacity-({operator_id})'


def add_operator_capacity_constraint_weekend(model, x_mat, operators, tasks, INCREASE_MAX_SOFASHIM):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task) and is_task_holiday(task)
        ) <= operator["MAX_Sofashim"] * INCREASE_MAX_SOFASHIM, f'capacity-weekend-({operator_id})'


def add_operator_capacity_constraint_nights(model, x_mat, operators, tasks, max_config):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task) and is_task_night(task) and not is_task_holiday(task)
        ) <= operator["MAX_nights"] * max_config, f'capacity-nights-({operator_id})'


def add_operator_min_per_month_constraint(model, x_mat, operators, tasks):
    for operator_id, operator in operators:
        for _, taskType in get_tasks_type_df().iterrows():
            if is_operator_qualified(operator, taskType) and taskType["min_per_month"] > 0:
                model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks
                              if (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                         >= taskType["min_per_month"], f'keep form-({operator_id},{taskType["type"]})'


def add_variety_constraint(model, x_mat, slack_variables, operators, tasks):
    for operator_id, operator in operators:
        relevant_tasks = [taskType for _, taskType in get_tasks_type_df().iterrows()
                          if is_operator_qualified(operator, taskType)]

        # target_number_of_tasks_per_type = 3 # operator["MAX"] / sum([task["cost"] for task in relevant_tasks])
        target_number_of_tasks = operator["MAX"] / np.mean([task["cost"] for task in relevant_tasks])
        task_freq_modifier = sum(task['freq'] for task in relevant_tasks)

        for taskType in relevant_tasks:
            target_number_of_tasks_per_type = target_number_of_tasks * taskType['freq'] / task_freq_modifier
            model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks if
                          (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                     >= target_number_of_tasks_per_type - 1 - slack_variables[operator_id] \
                , f'variety min-({operator_id},{taskType["type"]})'

            model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks if
                          (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                     <= target_number_of_tasks_per_type + 1 + slack_variables[operator_id] \
                , f'variety max-({operator_id},{taskType["type"]})'


def add_weekly_capacity_constraint(model, x_mat, slack_variables, operators, tasks, max_config):
    weeks = get_days_in_week_in_current_month()
    for week_id, days_in_week in enumerate(weeks):
        relevant_tasks = [(task_id, task) for task_id, task in tasks if is_task_in_week(week_id, task)]
        for operator_id, operator in operators:
            model += xsum(
                task["cost"] * x_mat[operator_id][task_id] for task_id, task in relevant_tasks
                if is_operator_capable(operator, task) and not is_task_holiday(task)
            ) >= math.floor(operator["MAX"] * max_config) - slack_variables[operator_id][
                         week_id], f'weekly-capacity-({operator_id},{week_id}))'


def add_operator_capacity_constraint_nights(model, x_mat, operators, tasks, max_config):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task) and is_task_night(task) and not is_task_holiday(task)
        ) <= operator["MAX_nights"] * max_config, f'capacity-nights-({operator_id})'

