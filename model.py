from mip import Model, xsum, BINARY, maximize
from functions import *

from pandas import DataFrame


def init_constraints(tasks, operators):
    shifts_model = Model()

    x_mat = add_vars(shifts_model, operators, tasks)

    shifts_model.objective = maximize(xsum(task for operator in x_mat for task in operator.values()))

    add_all_tasks_are_assigned_constrains(shifts_model, x_mat, operators, tasks)

    # add_task_overlap_constrains(shifts_model, x_mat, operators, tasks)

    add_operator_capacity_constraint(shifts_model, x_mat, operators, tasks)

    return shifts_model


def add_vars(shifts_model, operators: DataFrame, tasks: DataFrame):
    return [
        {task_id: shifts_model.add_var(f'x({operator_id},{task_id})', var_type=BINARY)
         for task_id, task in tasks.iterrows()
         if is_operator_qualified(operator, task)}
        for operator_id, operator in operators.iterrows()
    ]


def add_all_tasks_are_assigned_constrains(model, x_mat, operators: DataFrame, tasks: DataFrame):
    for task_id, task in tasks.iterrows():
        model += xsum(x_mat[operator_id][task_id] for operator_id, operator in operators.iterrows()
                      if is_operator_qualified(operator, task)) == 1, f'task({task_id})'


def add_task_overlap_constrains(model, x_mat, operators: DataFrame, tasks: DataFrame):
    for task_id, task in tasks.iterrows():
        for operator_id, operator in operators.iterrows():
            model += xsum(
                x_mat[operator_id][task_id] for task_b_id, task_b in tasks.iterrows()
                if (is_task_overlapping(task, task_b) and
                    is_operator_qualified(operator, task))) <= 1, \
                     f'overlapping-({operator_id},{task_id}))'


def add_operator_capacity_constraint(model, x_mat, operators: DataFrame, tasks: DataFrame):
    for operator_id, operator in operators.iterrows():
        model += xsum(
            task["cost"] * x_mat[operator_id][task_id] for task_id, task in tasks.iterrows() if
            is_operator_qualified(operator, task)
        ) <= operator["MAX"], f'capacity-({operator_id})'
