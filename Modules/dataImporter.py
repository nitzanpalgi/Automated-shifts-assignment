import pandas as pd
from datetime import timedelta, datetime

MONTH_TO_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}
PATH = '../data/DB.xlsx'
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
def Add_row_to_task_list(row_data, num_of_days, month, year):
    for day in range(1, num_of_days + 1):
        date_time_str = f'{year}-{month}-{day} {row_data["start-hour"]}'
        start_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(hours=row_data['time'])
        new_task = [start_time, end_time, row_data['name'], row_data['cost'], row_data['Compatible'], 1]
        tasks_list.append(new_task)

# Gets the path of the DB and return (tasks_df, operators_df) - 2 dataFrames
def CSV_importer(path):
    current_month = (datetime.now().month + 1) % 12
    current_year = datetime.now().year
    current_year += 1 if current_month == 1 else 0
    NUM_OF_DAYS = MONTH_TO_DAYS[current_month]

    data = pd.read_excel(path, sheet_name="Tasks")
    for index, row_data in data.iterrows():
        Add_row_to_task_list(row_data, NUM_OF_DAYS, current_month, current_year)

    tasks_df = format_tasks_list()
    operators_df = pd.read_excel(path,  sheet_name="Operators")
    return tasks_df, operators_df


if __name__ == '__main__':
    tasks, operators = CSV_importer(PATH)
    print(tasks)
    print(operators)
