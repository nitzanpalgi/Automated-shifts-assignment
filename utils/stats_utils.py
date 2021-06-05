import numpy as np


def get_operator_filtered_tasks(oper_index, operator, taken_tasks_per_operator, tasks, filter_method):
    taken_tasks_by_operator = tasks.iloc[taken_tasks_per_operator[oper_index]]
    if taken_tasks_by_operator.empty:
        return taken_tasks_by_operator

    filtered_tasks_df = taken_tasks_by_operator.loc[
        taken_tasks_by_operator.apply(lambda task: filter_method(operator, task), axis=1)]
    return filtered_tasks_df


def get_permutation_by_name(assignment_mat, operators):
    operators_names = [oper['name'] for _, oper in operators]
    assignment_mat_names = list(assignment_mat.index)

    operators_sorted_perm = np.argsort(operators_names)
    assignment_mat_sorted_perm = np.argsort(np.argsort(assignment_mat_names))
    return operators_sorted_perm[assignment_mat_sorted_perm]


def calc_grade(top, bottom):
    if bottom == 0:
        return 1
    return top / bottom
