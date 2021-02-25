from mip import Model, xsum, BINARY


def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)

    shifts_model = Model()

    mat = add_vars(shifts_model, tasks, operators)

    # shifts_model += xsum()

    # all tasks are assigned
    for j, task in enumerate(tasks):
        shifts_model += xsum(mat[i][j] for i, operators in enumerate(operators)) == 1
        if is_shift_compatible(operators, task), f'task({task})'


def add_vars(shifts_model, tasks, operators):
    return [shifts_model.add_var(f'x({i},{j})')
            for j, task in enumerate(tasks)
            for i, operator in enumerate(operators)
            if is_shift_compatible(operators, task)]


def is_shift_compatible(operators, task):
    return True
