import pandas as pd
from datetime import timedelta, datetime
from functions import get_days_in_current_month


tasks_list = []

# tasks_list ---> task_df
def format_tasks_list():
    start_time = [task[0] for task in tasks_list]
    end_time = [task[1] for task in tasks_list]
    name = [task[2] for task in tasks_list]
    cost = [task[3] for task in tasks_list]
    Compatible = [task[4] for task in tasks_list]
    min_per_month = [task[5] for task in tasks_list]
    tasks = pd.DataFrame({'start_time': start_time, 'end_time': end_time, 'name': name, 'cost': cost,
                          'Compatible': Compatible, 'min_per_month': min_per_month})
    return tasks

# Handle row and add to task_list
def Add_row_to_task_list(row_data):
    for day in get_days_in_current_month():
        date_time_str = f'{day} {row_data["start-hour"]}'
        start_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(hours=row_data['time'])
        new_task = [start_time, end_time, row_data['name'], row_data['cost'], row_data['Compatible'], 1]
        tasks_list.append(new_task)

# Gets the path of the DB and return (tasks_df, operators_df) - 2 dataFrames
def CSV_importer(path):
    data = pd.read_excel(path, sheet_name="Tasks")
    for index, row_data in data.iterrows():
        Add_row_to_task_list(row_data)

    tasks_df = format_tasks_list()
    operators_df = pd.read_excel(path, sheet_name="Operators")
    return tasks_df, operators_df


if __name__ == '__main__':
    DATA_PATH = '../data/DB.xlsx'
    tasks, operators = CSV_importer(DATA_PATH)
    print(tasks)
    print(operators)
