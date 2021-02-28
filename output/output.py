import pandas as pd
import xlrd
import xlwt
import openpyxl
from mip import Model, xsum, BINARY
import datetime
from Modules import dataImporter
from functions import *

# dataframe for each operator as row
def create_operators_dataframe(operators):
    df = pd.DataFrame(columns=operators.name)
    for date in get_days_in_current_month():
        df = df.append({"Date": date}, ignore_index=True)
    print(df)
    return df


# dataframe for each task as a row
def create_task_dataframe(DB_path):
    data_df = pd.read_excel(DB_path, sheet_name='Tasks')
    df = pd.DataFrame(columns=data_df.name)
    for date in get_days_in_current_month():
        df = df.append({"Date": date}, ignore_index=True)
    print(df)
    return df


# converts binary matrix to dfs by operator and by task
def convert_to_readable_df(shifts_model, start_date, end_date, tasks, operators, DB_path):
    operators_df = create_operators_dataframe(operators)
    tasks_df = create_task_dataframe(DB_path)

    # needs to get the shifts model
    for i, v in enumerate(shifts_model.vars):
        # find the operator and the shift
        if v.x >= 0.99:
            cell = v.names[2:]
            cell = cell[:-1]
            # cell is x,y
            cell_x = cell.split(",")[0]
            cell_y = cell.split(",")[1]
            task_name = tasks.at[cell_x, "name"]
            task_start_time = tasks.at[cell_x, "start_time"]
            task_start_time = datetime.datetime.strptime(
                task_start_time, "%d/%m/%Y")
            operator_name = operators.at[cell_y, "name"]
            # find the persons and shift and assign them in the dfs
            operators_df.at[operator_name, task_start_time] = task_name
            tasks_df.at[task_name, task_start_time] = operator_name
    return operators_df, tasks_df


def main():
    shifts_model = {}
    DB_path = '../DATA/DB.xlsx'
    tasks, operators = dataImporter.CSV_importer(DB_path)
    operators_df, tasks_df = convert_to_readable_df(shifts_model, "1/3/2021", "31/3/2021", tasks, operators, DB_path)

    # by operator
    operators_df.to_excel("./operators_data.xlsx")
    # by task
    tasks_df.to_excel("./tasks_data.xlsx")


if __name__ == "__main__":
    main()
