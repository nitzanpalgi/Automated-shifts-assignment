from mip import Model, xsum, BINARY, maximize
from functions import *
from Modules.dataImporter import get_tasks_type_df


def init_constraints(tasks_df, operators_df):
    shifts_model = Model()

    operators = [row for row in operators_df.iterrows()]
    tasks = [row for row in tasks_df.iterrows()]

    x_mat = add_vars(shifts_model, operators, tasks)

    shifts_model.objective = maximize(xsum(task for operator in x_mat for task in operator.values()))

    add_all_tasks_are_assigned_constrains(shifts_model, x_mat, operators, tasks)
    add_task_overlap_constrains(shifts_model, x_mat, operators, tasks)
    add_operator_capacity_constraint(shifts_model, x_mat, operators, tasks)
    add_operator_min_per_month_constraint(shifts_model, x_mat, operators, tasks)
    add_weekly_capactiy_constraint(shifts_model, x_mat, operators, tasks)
    return shifts_model


def get_var_if_qualified(shifts_model, operator, task, operator_id, task_id):
    if is_operator_qualified(operator, task):
        return shifts_model.add_var(f'x({operator_id},{task_id})', var_type=BINARY)
    return 1


def add_vars(shifts_model, operators, tasks):
    return [
        {task_id: shifts_model.add_var(f'x({operator_id},{task_id})', var_type=BINARY)
         for task_id, task in tasks
         if is_operator_capable(operator, task)}
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
                if is_operator_capable(operator, task)) <= 1, f'overlapping-({operator_id},{day}))'


def add_operator_capacity_constraint(model, x_mat, operators, tasks):
    for operator_id, operator in operators:
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks if
            is_operator_capable(operator, task)
        ) <= operator["MAX"] * 1.2, f'capacity-({operator_id})'


def add_operator_min_per_month_constraint(model, x_mat, operators, tasks):
    for operator_id, operator in operators:
        for _, taskType in get_tasks_type_df().iterrows():
            if is_operator_qualified(operator, taskType) and taskType["min_per_month"] > 0:
                model += xsum(x_mat[operator_id][task_id] for task_id, task in tasks
                              if (is_operator_capable(operator, task) and task["type"] == taskType['type'])) \
                         >= taskType["min_per_month"], f'keep form-({operator_id},{taskType["type"]})'


def add_weekly_capactiy_constraint(model, x_mat, operators, tasks):
    weeks = get_days_in_week_in_current_month()
    for week_id, days_in_week in enumerate(weeks):
        relevant_tasks = [(task_id, task) for task_id, task in tasks if is_task_in_week(week_id, task)]
        for operator_id, operator in operators:
            model += xsum(
                x_mat[operator_id][task_id] for task_id, task in relevant_tasks
                if is_operator_capable(operator, task)
            ) <= operator["MAX"], f'weekly-capacity-({operator_id},{week_id}))'
