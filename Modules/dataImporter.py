import pandas as pd
from pandas import DataFrame
from datetime import timedelta, datetime
from functions import get_days_in_current_month
from numpy import random, sum


# Turn tasks list into a task DataFrame
def format_tasks_list(tasks):
    start_time = [task[0] for task in tasks]
    end_time = [task[1] for task in tasks]
    name = [task[2] for task in tasks]
    cost = [task[3] for task in tasks]
    Compatible = [task[4] for task in tasks]
    min_per_month = [task[5] for task in tasks]
    ids = [task[6] for task in tasks]
    types = [task[7] for task in tasks]

    return pd.DataFrame({
        'id': ids,
        'start_time': start_time,
        'end_time': end_time,
        'name': name,
        'cost': cost,
        'Compatible': Compatible,
        'min_per_month': min_per_month,
        "type": types
    })


# Handle row and add to task_list
def distribute_tasks_in_day(row_data):
    tasks_in_day = []

    for day in get_days_in_current_month():
        if random.rand() <= row_data['probability']:
            date_time_str = f'{day} {row_data["start-hour"]}'
            start_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = start_time + timedelta(hours=row_data['time'])
            new_task = [start_time, end_time, row_data['name'], row_data['cost'], row_data['Compatible'], 1,
                        row_data['id'], row_data['type']]
            tasks_in_day.append(new_task)

    return tasks_in_day


# Spread tasks in month according to each task data
def distribute_tasks_in_month(tasks_data):
    tasks = []

    for index, row_data in tasks_data.iterrows():
        tasks += distribute_tasks_in_day(row_data)

    return tasks


def recalculate_operators_capacity(operators, tasks):
    capacity_sum = sum(operators["MAX"])
    tasks_cost_sum = sum(tasks["cost"])

    return operators["MAX"] * (tasks_cost_sum / capacity_sum)


# Gets the path of the DB and return (tasks_df, operators_df) - 2 dataFrames
def import_data_from_excel(path):
    tasks_data = pd.read_excel(path, sheet_name="Tasks")
    tasks = distribute_tasks_in_month(tasks_data)

    tasks_df = format_tasks_list(tasks)
    operators_df = pd.read_excel(path, sheet_name="Operators")

    operators_df["MAX"] = recalculate_operators_capacity(operators_df, tasks_df)

    calc_tasks_types(tasks_data)
    # temp_func(data, operators_df)
    return tasks_df, operators_df


def get_tasks_type_df():
    return tasks_type_df


def calc_tasks_types(data: DataFrame):
    global tasks_type_df
    tasks_type_df = data.drop_duplicates(subset=['type'])[['min_per_month', 'type']]
