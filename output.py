import pandas as pd
import xlrd
import openpyxl
from sys import stdout
from mip import Model, xsum, BINARY
import datetime


def output_to_excel(shifts_model):
    for i, v in enumerate(queens.vars):
        stdout.write('O ' if v.x >= 0.99 else '. ')
        if i % n == n-1:
            stdout.write('\n')


# datadframe for each operator as row
def create_operators_dataframe(start_date, end_date):
    data_df = pd.read_excel("DATA\db.xlsx", sheet_name=0)
    df = pd.DataFrame(columns=data_df.name)
    df.insert(0, "Date", [])
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    for i in range((end_date - start_date).days+1):
        df = df.append({"Date": start_date + i*delta}, ignore_index=True)
    return df, data_df


def create_task_dataframe(start_date, end_date):
    data_df = pd.read_excel("DATA\db.xlsx", sheet_name=1)
    df = pd.DataFrame(columns=data_df.name)
    df.insert(0, "Date", [])
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    for i in range((end_date - start_date).days+1):
        df = df.append({"Date": start_date + i*delta}, ignore_index=True)
    return df, data_df


def final_print(start_date, end_date, big_task_df, big_names_df):
    op_df = create_operators_dataframe(start_date, end_date)
    data_op_df = op_df[1]
    op_df = op_df[0]
    task_df = create_task_dataframe(start_date, end_date)
    data_task_df = task_df[1]
    task_df = task_df[0]
    for i, v in enumerate(queens.vars):
        # stdout.write('O ' if v.x >= 0.99 else '. ')
        # find the operator and the shift
        if v.x >= 0.99:
            cell = v.names[2:]
            cell = cell[:-1]
            #cell is x,y
            cell_x = cell.split(",")[0]
            cell_y = cell.split(",")[1]
            task_name = big_task_df.at[cell_x,"name"]
            task_start_time= big_task_df.at[cell_x,"start_time"]
            task_start_time = datetime.datetime.strptime(task_start_time, "%d/%m/%Y")
            operator_name= big_names_df.at[cell_y,"name"]
            #find the persons and shift and assign them in the dfs
            op_df.at[operator_name,task_start_time]= task_name
            task_df.at[task_name,task_start_time]=operator_name
            #print to excel
            return (op_df,task_df)
    # find gain

    # if i % n == n-1:
    # stdout.write('\n')


def main():
    print(final_print("1/3/2021", "31/3/2021"))


if __name__ == "__main__":
    main()
