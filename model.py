from mip import Model, xsum, BINARY
import datetime, calendar


def init_constraints(tasks, operators):
    numTasks = len(tasks)
    numPeople = len(operators)

    shifts_model = Model()

    mat = add_vars(shifts_model, operators, tasks)

    # shifts_model += xsum()

    shifts_model += all_tasks_are_assigned_constrains(mat, operators, tasks)


def add_vars(shifts_model, operators, tasks):
    return [shifts_model.add_var(f'x({operator.id},{task.id})', var_type=BINARY)
            for task in tasks
            for operator in operators
            if is_operator_qualified(operators, task)]


def all_tasks_are_assigned_constrains(mat, operators, tasks):
    return [(xsum(mat[operator.id][task.id] for operator in operators
                  if is_operator_qualified(operator, task)) == 1, f'task({task})') for task in tasks]


def task_overlap_constrains(mat, operators, tasks):
    constrains = []
    for day in get_days_in_current_month():
        for operator in operators:
            constrains += xsum(
                mat[operator.id][task.id] for task in tasks
                if (task.start_time <= day <= task.end_time and
                    is_operator_qualified(operator,task))) <= 1, \
                          f'day-({day}) operator-({operator})'

    return constrains


def is_operator_qualified(operator, task):
    return True


def get_days_in_current_month():
    current_date = datetime.datetime.now()
    year, month = current_date.year, current_date.month
    num_days = calendar.monthrange(year, month)[1]
    return [datetime.date(year, month, day) for day in range(1, num_days + 1)]


if __name__ == "__main__":
    get_days_in_current_month()
