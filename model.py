from mip import Model, xsum, BINARY 

def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)

    shifts_model = Model()

    mat = add_vars(shifts_model, tasks, operators)

    # shifts_model += xsum() 

def add_vars(shifts_model, tasks, operators):
    return [ [ 
        is_shift_compatible(
            shifts_model.add_var(f'x({i},{j})') 
        )
        for j in range(len(tasks)) ] 
    for i in range(len(operators)) ]
