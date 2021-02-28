from mip import Model, xsum, BINARY, maximize
from functions import *

from pandas import DataFrame


def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)
    shifts_model = Model()
    x_mat = add_vars(shifts_model, operators, tasks)
    print(x_mat)
    # shifts_model.objective = maximize(xsum(x for x in x_mat))
    # shifts_model += all_tasks_are_assigned_constrains(x_mat, operators, tasks)


def add_vars(shifts_model, operators: DataFrame, tasks: DataFrame):
    return [shifts_model.add_var(f'x({operator_id},{task_id})', var_type=BINARY)
            for task_id, task in tasks.iterrows()
            for operator_id, operator in operators.iterrows()
            if is_operator_qualified(operator, task)]


def all_tasks_are_assigned_constrains(x_mat, operators, tasks):
    return [(xsum(x_mat[operator.id][task.id] for operator in operators
                  if is_operator_qualified(operator, task)) == 1, f'task({task})') for task in tasks]


def task_overlap_constrains(x_mat, operators, tasks):
    constrains = []
    for task in tasks():
        for operator in operators:
            constrains += xsum(
                x_mat[operator.id][task.id] for task_b in operators
                if (is_task_overlapping(task, task_b) and
                    task != task_b and
                    is_operator_qualified(operator, task))) <= 1, \
                          f'overlapping-({operator},{task}))'

    return constrains
