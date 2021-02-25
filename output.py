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
    data_df = pd.read_excel("DATA\db.xlsx")
    df = pd.DataFrame(columns=data_df.name)
    df.insert(0, "Date", [])
    start_date = datetime.datetime.strptime(start_date,"%d/%m/%Y")
    end_date = datetime.datetime.strptime(end_date,"%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    for i in range((end_date - start_date).days+1):
        df = df.append({"Date":start_date + i*delta},ignore_index=True)
    
    print(df)
    return df

# def create_task_dataframe():

# def final_print():
    # for i, v in enumerate(queens.vars):
    # stdout.write('O ' if v.x >= 0.99 else '. ')
    # find the operator and the shift
    # if v.x>= 0.99:

    # find gain

    # if i % n == n-1:
    # stdout.write('\n')


def main():
    create_operators_dataframe("1/3/2021", "31/3/2021")


if __name__ == "__main__":
    main()
