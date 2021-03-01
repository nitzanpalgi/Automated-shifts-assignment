import pandas as pd
from Modules import dataImporter
from functions import *
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.styles import Color, PatternFill,Fill, Font, Border
from openpyxl.cell import Cell
import datetime
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
    return df, data_df


counterZeros = 0
counterOnes = 0
counterElse = 0


# converts binary matrix to dfs by operator and by task
def convert_to_readable_df(shifts_model, tasks, operators, DB_path):
    operators_df = create_operators_dataframe(operators)
    tasks_df_multiple = create_task_dataframe(DB_path)
    tasks_df = tasks_df_multiple[0]
    tasks_df_colors = tasks_df_multiple[1]


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
    colors_dict= create_colors_dict(tasks_df_colors)
    df =df.sort_index(1)
    return df,colors_dict

def create_colors_dict(color_df):
    colors_dict_from_df = color_df.to_dict()
    colors_dict ={}
    for i in range(len(colors_dict_from_df["name"])):
        colors_dict[colors_dict_from_df["name"][i]]=colors_dict_from_df["color"][i][1:]
    return colors_dict

def color_cells(file_path,color_dict):
    new_book= Workbook()
    new_sheet = new_book.active
    book = load_workbook(file_path)
    ws = book.worksheets[0]
    min_row = int(ws.min_row)
    max_row = int(ws.max_row)
    for col in ws:
        for cell in col:
            new_cell=new_sheet.cell(row = cell.row,column=cell.column,value =cell.value)
            # color by task
            if cell.value in color_dict:
                new_cell.fill= PatternFill(start_color= color_dict[cell.value],end_color= color_dict[cell.value],fill_type="solid")
            #add weekend colors
            elif datetime.datetime(ws.cell(column=1,row=cell).value).weekday()==4 or datetime.datetime(ws.cell(column=1,row=cell).value).weekday()==5 :
                new_cell.fill=PatternFill(start_color="e4e4e4" ,end_color="e4e4e4" ,fill_type="solid")
                new_cell.font = Font(bold=True) 
            #bold for titles
            else:
                new_cell.font = Font(bold=True) 
    return new_book.save('./output/Butzi.xlsx')

    

def main():
    shifts_model = {}
    DB_path = '../DATA/DB.xlsx'

    tasks, operators = dataImporter.import_data_from_excel(DB_path)
    operators_df, tasks_df = convert_to_readable_df(shifts_model, tasks, operators, DB_path)

    # by operator
    operators_df.to_excel("./operators_data.xlsx")
    # by task
    tasks_df.to_excel("./tasks_data.xlsx")


if __name__ == "__main__":
    main()
