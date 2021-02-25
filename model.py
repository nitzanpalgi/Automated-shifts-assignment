from mip import Model, xsum, BINARY


def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)

    shifts_model = Model()

    mat = add_vars(shifts_model, operators, tasks)

    # shifts_model += xsum()

    shifts_model += all_tasks_are_assigned_constrains(mat, operators, tasks)


def add_vars(shifts_model, operators, tasks):
    return [shifts_model.add_var(f'x({i},{j})')
            for j, task in enumerate(tasks)
            for i, operator in enumerate(operators)
            if is_operator_qualified(operators, task)]


def all_tasks_are_assigned_constrains(mat, operators, tasks):
    return [(xsum(mat[i][j] for i, operators in enumerate(operators)
             if is_operator_qualified(operators, task)) == 1,
             f'task({task})') for j, task in enumerate(tasks)]


def is_operator_qualified(operators, task):
    return True
