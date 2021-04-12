import pandas as pd
from pandas import DataFrame
from datetime import timedelta, datetime
from functions import get_days_in_current_month
from numpy import random, sum, ceil


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
    is_weekends = [task[8] for task in tasks]
    compat_groups = [task[9] for task in tasks]

    return pd.DataFrame({
        'id': ids,
        'start_time': start_time,
        'end_time': end_time,
        'name': name,
        'cost': cost,
        'Compatible': Compatible,
        'min_per_month': min_per_month,
        "type": types,
        "is_weekend": is_weekends,
        "compat_group": compat_groups
    })


def US_day_to_IL_day(day):
    return ((day + 1) % 7) + 1

def create_task(row_data, day):
    date_time_str = f'{day} {row_data["start-hour"]}'
    start_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(hours=row_data['time'])
    new_task = [start_time, end_time, row_data['name'], row_data['cost'], row_data['Compatible'],
                row_data['min_per_month'], row_data['id'], row_data['type'], 
                row_data['is_sofash'], row_data['compat_group']]

    return new_task

# Handle row and add to task_list
def distribute_tasks_in_day(row_data):
    tasks_in_day = []
    for day in get_days_in_current_month():
        # if random.rand() <= row_data['probability']:
        if row_data['is_autofill']:
            if str(US_day_to_IL_day(day.weekday())) in str(row_data['days_in_week']):
                new_task = create_task(row_data, day)
                tasks_in_day.append(new_task)
            else:
                # print(f'task {row_data["name"]} cannot be at {day}')
                pass

    return tasks_in_day

def distribute_tasks_manual(row_data, specific_tasks_data):
    task_name = row_data['name']
    new_manual_tasks = []
    manual_tasks = list(specific_tasks_data.columns.values)
    if task_name in manual_tasks:
        days_in_month = str(specific_tasks_data[task_name][0]).split(',')
        days_in_month = list(map(lambda x: int(x), days_in_month))
        for day in get_days_in_current_month():
            if day.day in days_in_month:
                new_task = create_task(row_data, day)
                new_manual_tasks.append(new_task)
    return new_manual_tasks

# Spread tasks in month according to each task data
def distribute_tasks_in_month(tasks_data, specific_tasks_data):
    tasks = []
    for index, row_data in tasks_data.iterrows():
        tasks += distribute_tasks_in_day(row_data)
        tasks += distribute_tasks_manual(row_data, specific_tasks_data)
    return tasks


def recalculate_operators_capacity(operators, tasks):
    capacity_sum = sum(operators["MAX"])
    tasks_cost_sum = sum(tasks[tasks["is_weekend"] == 0]["cost"])

    return operators["MAX"] * (tasks_cost_sum / capacity_sum)


# Gets the path of the DB and return (tasks_df, operators_df) - 2 dataFrames
def import_data_from_excel(path):
    task_definition_df = pd.read_excel(path, sheet_name="Tasks")
    specific_tasks_data = pd.read_excel(path, sheet_name="Mishmarot")
    tasks = distribute_tasks_in_month(task_definition_df, specific_tasks_data)

    print(len(tasks))

    tasks_df = format_tasks_list(tasks)

    operators_df = pd.read_excel(path, sheet_name="Operators")

    # Temp remove recalculation of capacity
    # operators_df["MAX"] = recalculate_operators_capacity(operators_df, tasks_df)

    global task_types_df, compatible_tasks_groups_df
    calc_task_types_df(task_definition_df, tasks_df)

    compatible_tasks_groups_df = pd.read_excel(path, sheet_name="Task Groups")
    task_types_df = calc_task_types_df(task_definition_df, tasks_df)

    return tasks_df, operators_df


def get_task_types_df():
    return task_types_df
    

def get_compatible_tasks_groups_df():
    return compatible_tasks_groups_df

def calc_task_types_df(data: DataFrame, all_tasks):
    task_types_df = data.drop_duplicates(subset=['type'])[['min_per_month', 'type', 'cost']]

    task_types_df['freq'] = 0
    for task_type, task_frequency in (all_tasks['type'].value_counts() / len(all_tasks)).items():
        task_types_df.loc[task_types_df.type == task_type, 'freq'] = task_frequency

    return task_types_df


def main():
    DB_path = '../DATA/DB.xlsx'
    import_data_from_excel(DB_path)


if __name__ == "__main__":
    main()
