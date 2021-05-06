from collections import defaultdict

import numpy as np


def get_tasks_assignee(shifts_model, tasks_df):
    tasks_assignee = np.zeros(len(tasks_df), dtype=int)-1
    for v in shifts_model.vars:
        if v.name[0] == 'x' and v.x > 0:
            oper_id = int(v.name.split(',')[0][2:])
            task_id = int(v.name.split(',')[1][:-1])
            tasks_assignee[task_id] = oper_id
    return tasks_assignee


def get_taken_tasks_per_operator(shifts_model):
    taken_tasks_per_operator = defaultdict(list)
    for v in shifts_model.vars:
        if v.name[0] == 'x' and v.x > 0:
            oper_id = int(v.name.split(',')[0][2:])
            task_id = int(v.name.split(',')[1][:-1])
            taken_tasks_per_operator[oper_id].append(task_id)
    return taken_tasks_per_operator
