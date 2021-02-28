from mip import Model, xsum, BINARY, maximize
from functions import *


def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)
    shifts_model = Model()

    x_mat = add_vars(shifts_model, operators, tasks)

    shifts_model.objective = maximize(xsum(x for x in x_mat))

    # shifts_model += xsum()

    shifts_model += all_tasks_are_assigned_constrains(x_mat, operators, tasks)


def add_vars(shifts_model, operators, tasks):
    return [shifts_model.add_var(f'x({operator.id},{task.id})', var_type=BINARY)
            for t_index, task in tasks.iterrows()
            for o_index, operator in operators.iterrows()
            if is_operator_qualified(operators, task)]


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
