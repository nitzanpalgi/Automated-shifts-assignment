from mip import Model, xsum, BINARY, minimize
from functions import *
from Modules.dataImporter import get_tasks_type_df
from datetime import datetime


def init_constraints(tasks_df, operators_df):
    shifts_model = Model()

    operators = [row for row in operators_df.iterrows()]
    tasks = [row for row in tasks_df.iterrows()]

    x_mat = add_vars(shifts_model, operators, tasks)

    shifts_model.objective = minimize(
        xsum(task_x * get_operator_task_cost(operators[operator_xs_id][1], tasks[task_xs_id][1])
            for operator_xs_id, operator_xs in enumerate(x_mat)
            for task_xs_id, task_x in operator_xs.items()
        )
    )

    add_all_tasks_are_assigned_constrains(shifts_model, x_mat, operators, tasks)
    add_task_overlap_constrains(shifts_model, x_mat, operators, tasks)
    add_operator_capacity_constraint(shifts_model, x_mat, operators, tasks)
    add_operator_min_per_month_constraint(shifts_model, x_mat, operators, tasks)
    add_weekly_capactiy_constraint(shifts_model, x_mat, operators, tasks)
    return shifts_model


def get_operator_task_cost(operator, task):
    if dont_want_task(operator, task):
        return operator["pazam"] * (task["cost"] + 10)
    else:
        return operator["pazam"] * task["cost"]


def dont_want_task(operator, task):
    if str(operator["Not evening"]) == 'nan':
        return False
    unwanted_evenings = str(operator["Not evening"]).split(',')
    current_date = datetime.now()
    year, month = current_date.year, current_date.month

    return any(task["start_time"] <= datetime(year=year, month=month, day=int(evening), hour=18) <= task["end_time"]
               for evening in unwanted_evenings)


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
