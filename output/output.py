import pandas as pd
from Modules import dataImporter
from functions import *

# dataframe for each operator as row
def create_operators_dataframe(operators):
    df = pd.DataFrame(columns=operators.name)
    for date in get_days_in_current_month():
        df = df.append({"Date": date}, ignore_index=True)
    return df

# dataframe for each task as a row
def create_task_dataframe(DB_path):
    data_df = pd.read_excel(DB_path, sheet_name='Tasks')
    df = pd.DataFrame(columns=data_df.name)
    for date in get_days_in_current_month():
        df = df.append({"Date": date}, ignore_index=True)
    return df


counterZeros = 0
counterOnes = 0
counterElse = 0
# converts binary matrix to dfs by operator and by task
def convert_to_readable_df(shifts_model, tasks, operators, DB_path):
    operators_df = create_operators_dataframe(operators)
    tasks_df = create_task_dataframe(DB_path)

    df = pd.DataFrame()

    # needs to get the shifts model
    for i, v in enumerate(shifts_model.vars):

        if v.x >= 0.99:
            cell = v.name[2:]
            cell = cell[:-1]
            cell_x = int(cell.split(",")[0])
            cell_y = int(cell.split(",")[1])
            operator_name = operators['name'][cell_x]
            task_name = tasks['name'][cell_y]

            task_start_time = str(tasks['start_time'][cell_y]).split(' ')[0]

            df.at[operator_name, task_start_time] = task_name


    return df


def main():
    shifts_model = {}
    DB_path = '../DATA/DB.xlsx'
    tasks, operators = dataImporter.CSV_importer(DB_path)
    operators_df, tasks_df = convert_to_readable_df(shifts_model, tasks, operators, DB_path)

    # by operator
    operators_df.to_excel("./operators_data.xlsx")
    # by task
    tasks_df.to_excel("./tasks_data.xlsx")


if __name__ == "__main__":
    main()
