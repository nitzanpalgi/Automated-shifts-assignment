from mip import Model, xsum, BINARY, CONTINUOUS, minimize
from utils.task_utils import *
from utils.operator_utils import *
from Modules.dataImporter import get_compatible_tasks_groups_df, get_task_types_df
from utils.date_utils import get_days_in_current_month, get_days_in_week_in_current_month
from utils.date_utils import FIRST_DAY_OF_THE_MONTH_IS_SATURDAY
from constants import *
import math
import numpy as np


def init_constraints(tasks_df, operators_df):
    shifts_model = Model()

    operators = [row for row in operators_df.iterrows()]
    tasks = [row for row in tasks_df.iterrows()]
    compatible_groups = [group for group in get_compatible_tasks_groups_df().iterrows()]
    task_types = [task_type for task_type in get_task_types_df().iterrows()]

    x_mat = add_vars(shifts_model, operators, tasks)
    s_weekly_capacity = add_weekly_capacity_slack_vars(shifts_model, operators)
    s_parallel_tasks_groups = add_parallel_tasks_group_slack_vars(shifts_model, operators, compatible_groups)
    s_variety = add_variety_slack_vars(shifts_model, operators)
    s_working_days = add_working_days_slack_vars(shifts_model, operators)
    shifts_model.objective = minimize(
        xsum(task_x * get_operator_task_cost(operators[operator_id][1], tasks[task_id][1])
             for operator_id, operator in enumerate(x_mat)
             for task_id, task_x in operator.items()
             ) +
        100 * xsum(s_variety[operator_id] / operator["pazam"] for operator_id, operator in operators) +

        10 * xsum(s_weekly_capacity[operator_id][week_id]
                  for operator_id, operator in operators
                  for week_id, days_in_week in enumerate(get_days_in_week_in_current_month())
                  ) +
        3 * xsum(s_working_days[operator_id][day.day - 1 - int(FIRST_DAY_OF_THE_MONTH_IS_SATURDAY)]
                 for operator_id, operator in operators for day in get_days_in_current_month())
    )

    add_all_tasks_are_assigned_constrains(shifts_model, x_mat, operators, tasks)
    add_task_overlap_constrains(shifts_model, x_mat, s_parallel_tasks_groups, operators, tasks, compatible_groups,
                                task_types)
    add_operator_capacity_constraint_not_weekend(shifts_model, x_mat, operators, tasks, MAX_CAPACITY_NOT_WEEKEND,
                                                 MIN_CAPACITY_NOT_WEEKEND)
    add_operator_capacity_constraint_weekend(shifts_model, x_mat, operators, tasks, INCREASE_MAX_SOFASHIM)
    add_operator_min_per_month_constraint(shifts_model, x_mat, operators, tasks)
    add_weekly_capacity_constraint(shifts_model, x_mat, s_weekly_capacity, operators, tasks, MAX_WEEKLY_CAPACITY)
    add_variety_constraint(shifts_model, x_mat, s_variety, operators, tasks, task_types)
    add_operator_capacity_constraint_nights(shifts_model, x_mat, operators, tasks, MAX_NIGHT_CAPACITY)
    add_working_days_int(shifts_model, x_mat, s_working_days, operators, tasks)

    return shifts_model


def get_operator_task_cost(operator, task):
    if dont_want_task(operator, task):
        return (operator["pazam"] ** 2) * (task["cost"] + 100)
    elif want_task(operator, task):
        return -100 * (operator["pazam"] ** 2) * task["cost"]
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
        shifts_model.add_var(f's_variety({operator_id})', var_type=CONTINUOUS, ub=4)
        for operator_id, operator in operators
    ]


def add_working_days_slack_vars(shifts_model, operators):
    return [
        [shifts_model.add_var(f's_working_days({operator_id},{day})', var_type=BINARY)
         for day in get_days_in_current_month()] for operator_id, operator in operators
    ]


def add_weekly_capacity_slack_vars(shifts_model, operators):
    return [
        [shifts_model.add_var(f'weekly capacity({operator_id},{week_id})', var_type=CONTINUOUS)
         for week_id, days_in_week in enumerate(get_days_in_week_in_current_month())]
        for operator_id, operator in operators
    ]


def add_parallel_tasks_group_slack_vars(shifts_model, operators, compatible_groups):
    return [
        [
            [
                shifts_model.add_var(f'parallel tasks group({day.day},{operator_id},{group_id})', var_type=BINARY)
                for group_id, group in compatible_groups
            ] for operator_id, operator in operators
        ] for day in get_days_in_current_month()
    ]


def add_all_tasks_are_assigned_constrains(model, x_mat, operators, tasks):
    for task_id, task in tasks:
        model += xsum(x_mat[operator_id][task_id] for operator_id, operator in operators
                      if is_operator_capable(operator, task)) == 1, f'task({task_id})'


def add_task_overlap_constrains(model, x_mat, s_groups, operators, tasks, compatible_groups, task_types):
    for day_id, day in enumerate(get_days_in_current_month()):
        relevant_tasks = [(task_id, task) for task_id, task in tasks if task["start_time"] <= day <= task["end_time"]]

        for operator_id, operator in operators:
            operator_relevant_tasks = [(task_id, task) for (task_id, task) in relevant_tasks
                                       if is_operator_capable(operator, task)]

            # Make sure only one from each type is given to each operator in same day
            for _, taskType in task_types:
                model += xsum(x_mat[operator_id][task_id]
                              for task_id, task in operator_relevant_tasks
                              if (is_operator_capable(operator, task) and task["type"] == taskType['type'])) <= 1 \
                    , f'max-of-task-type-({operator_id},{day.day},{taskType["type"]})'

            model += xsum(s_groups[day_id][operator_id][group_id] for group_id, _ in compatible_groups) <= 1 \
                , f'max group-({day.day},{operator_id})'

            for group_id, group in compatible_groups:
                in_group_xsum = xsum(x_mat[operator_id][task_id]
                                     for task_id, task in operator_relevant_tasks if is_task_in_group(task, group))

                model += in_group_xsum <= s_groups[day_id][operator_id][group_id] * group["max_per_day"] \
                    , f'group max per day-({operator_id},{day.day},{group["name"]}))'


def add_operator_capacity_constraint_not_weekend(model, x_mat, operators, tasks, max_config, min_config):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task)
        ) <= max(operator["MAX"] + max_config,
                 get_minimal_capacity_of_operator(operator)), f'max capacity-({operator_id})'

    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task)
        ) >= operator["MAX"] - min_config, f'min capacity-({operator_id})'


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
            is_operator_capable(operator, task) and is_task_night(
                task) and not is_task_holiday(task)
        ) <= operator["MAX_nights"] * max_config, f'capacity-nights-({operator_id})'


def add_operator_min_per_month_constraint(model, x_mat, operators, tasks):
    task_types = [task_type for task_type in get_task_types_df().iterrows()]

    for operator_id, operator in operators:
        for _, taskType in task_types:
            if is_operator_qualified(operator, taskType) and taskType["min_per_month"] > 0:
                model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks
                              if (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                         >= taskType["min_per_month"], f'keep form-({operator_id},{taskType["type"]})'


def add_variety_constraint(model, x_mat, slack_variables, operators, tasks, task_types):
    for operator_id, operator in operators:
        relevant_tasks = [taskType for _, taskType in task_types if is_operator_qualified(operator, taskType)]

        target_number_of_tasks = (operator["MAX"] - operator["MAX_Sofashim"]) / np.mean(
            [task["cost"] for task in relevant_tasks])
        task_freq_modifier = sum(task['freq'] for task in relevant_tasks)

        for taskType in relevant_tasks:
            target_number_of_tasks_per_type = target_number_of_tasks * taskType['freq'] / task_freq_modifier
            model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks if
                          (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                     >= target_number_of_tasks_per_type - 1 - slack_variables[
                         operator_id], f'variety min-({operator_id},{taskType["type"]})'

            model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks if
                          (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                     <= target_number_of_tasks_per_type + 1 + slack_variables[
                         operator_id], f'variety max-({operator_id},{taskType["type"]})'


def add_weekly_capacity_constraint(model, x_mat, slack_variables, operators, tasks, max_config):
    weeks = get_days_in_week_in_current_month()
    for week_id, days_in_week in enumerate(weeks):
        relevant_tasks = [(task_id, task) for task_id,
                                              task in tasks if is_task_in_week(week_id, task)]
        for operator_id, operator in operators:
            model += xsum(
                task["cost"] * x_mat[operator_id][task_id] for task_id, task in relevant_tasks
                if is_operator_capable(operator, task)
            ) >= math.floor(operator["MAX"] * max_config) - slack_variables[operator_id][
                         week_id], f'weekly-capacity-({operator_id},{week_id}))'


def add_working_days_int(model, x_mat, slack_variables, operators, tasks):
    for day_id, day in enumerate(get_days_in_current_month()):
        relevant_tasks = [(task_id, task) for task_id,
                                              task in tasks if task["start_time"] <= day <= task["end_time"]]
        for operator_id, operator in operators:
            operator_relevant_tasks = [(task_id, task) for (task_id, task) in relevant_tasks
                                       if is_operator_capable(operator, task)]
            tasks_in_day = xsum(x_mat[operator_id][task_id]
                                for task_id, task in operator_relevant_tasks)
            model += tasks_in_day <= 3 * slack_variables[operator_id][
                day_id], f'working-days-({operator_id},{day.day}))'
