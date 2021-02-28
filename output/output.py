import pandas as pd
import xlrd
import xlwt
import openpyxl
from mip import Model, xsum, BINARY
import datetime
from Modules import dataImporter


# datadframe for each operator as row
def create_operators_dataframe(start_date, end_date):
    data_df = pd.read_excel("./DATA/DB.xlsx", sheet_name=0)
    df = pd.DataFrame(columns=data_df.name)
    df.insert(0, "Date", [])
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    for i in range((end_date - start_date).days + 1):
        df = df.append({"Date": start_date + i * delta}, ignore_index=True)
    return df, data_df


# dataframe for each task as a row
def create_task_dataframe(start_date, end_date):
    data_df = pd.read_excel("./DATA/DB.xlsx", sheet_name=1)
    df = pd.DataFrame(columns=data_df.name)
    df.insert(0, "Date", [])
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    for i in range((end_date - start_date).days + 1):
        df = df.append({"Date": start_date + i * delta}, ignore_index=True)
    return df, data_df


# converts binary mastix to dfs by operator and by task
def convert_to_readable_df(shifts_model, start_date, end_date, tasks, operators):
    op_df = create_operators_dataframe(start_date, end_date)
    # data_op_df = op_df[1]
    op_df = op_df[0]
    task_df = create_task_dataframe(start_date, end_date)
    # data_task_df = task_df[1]
    task_df = task_df[0]
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
            op_df.at[operator_name, task_start_time] = task_name
            task_df.at[task_name, task_start_time] = operator_name
            return (op_df, task_df)
    # find gain


def main():
    DB_path = './DATA/DB.xlsx'
    tasks, operators = dataImporter.CSV_importer(DB_path)
    dfs = convert_to_readable_df("1/3/2021", "31/3/2021", tasks, operators)
    # by operator
    dfs[0].to_excel("./By operator.xlsx")
    # by task
    dfs[1].to_excel("./By task.xlsx")


if __name__ == "__main__":
    main()