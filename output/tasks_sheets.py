from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from utils.date_utils import get_days_in_current_month, us_day_to_il_day
from constants import WEEKDAYS_LIST


def add_tasks_sheets(file_path, tasks_df, operators_df):
    add_tahak_sheet(file_path, tasks_df, operators_df)
    add_equipment_sheet(file_path, tasks_df, operators_df)
    add_bakut_sheet(file_path, tasks_df, operators_df)
    add_production_sheet(file_path, tasks_df, operators_df)


def add_tahak_sheet(file_path, tasks_df, operators_df):
    output_workbook = load_workbook(file_path)
    output_workbook.create_sheet('cleaning the tahak')
    tahak_worksheet = output_workbook.get_sheet_by_name('cleaning the tahak')
    add_sheet_titles(tahak_worksheet, ['date', 'day', 'cleaning the tahak'])
    add_dates_column(tahak_worksheet, row_length=3)
    assign_operators_to_tasks_cells(tahak_worksheet, tasks_df.loc[tasks_df.name == 'CLEANING THE TAHAK'], operators_df,
                                    column_to_edit=3)
    blacken_empty_cells(tahak_worksheet)
    output_workbook.save(file_path)


def add_equipment_sheet(file_path, tasks_df, operators_df):
    output_workbook = load_workbook(file_path)
    output_workbook.create_sheet('equipment')
    equipment_worksheet = output_workbook.get_sheet_by_name('equipment')
    add_sheet_titles(equipment_worksheet,
                     ['date', 'day', 'equipment operator', 'equipment day', 'equipment night', 'WV operator'])
    add_dates_column(equipment_worksheet, row_length=6)

    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'equip operator'], operators_df,
                                    column_to_edit=3)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'equipment day'], operators_df,
                                    column_to_edit=4)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'Sofash Equip day'],
                                    operators_df, column_to_edit=4, is_weekend=True)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'equipment night'], operators_df,
                                    column_to_edit=5)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'Hamishi - equipment night'],
                                    operators_df, column_to_edit=5)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'Sofash Equip night'],
                                    operators_df, column_to_edit=5, is_weekend=True)
    assign_operators_to_tasks_cells(equipment_worksheet, tasks_df.loc[tasks_df.name == 'wv equipment'], operators_df,
                                    column_to_edit=6)
    blacken_empty_cells(equipment_worksheet)
    output_workbook.save(file_path)


def add_bakut_sheet(file_path, tasks_df, operators_df):
    output_workbook = load_workbook(file_path)
    output_workbook.create_sheet('bakut')
    bakut_worksheet = output_workbook.get_sheet_by_name('bakut')
    add_sheet_titles(bakut_worksheet,
                     ['date', 'day', 'bakut operator', 'bakut day 1', 'bakut day 2', 'bakut night 1', 'bakut night 2'])
    add_dates_column(bakut_worksheet, row_length=7)

    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'bakut operator'], operators_df,
                                    column_to_edit=3)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'bakut day 1'], operators_df,
                                    column_to_edit=4)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Sofash bakut day 1'],
                                    operators_df, column_to_edit=4, is_weekend=True)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'bakut day 2'], operators_df,
                                    column_to_edit=5)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Sofash bakut day 2'],
                                    operators_df, column_to_edit=5, is_weekend=True)

    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'bakut night 1'], operators_df,
                                    column_to_edit=6)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Hamishi - bakut night 1'],
                                    operators_df, column_to_edit=6)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Sofash bakut night 1'],
                                    operators_df, column_to_edit=6, is_weekend=True)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'bakut night 2'], operators_df,
                                    column_to_edit=7)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Hamishi - bakut night 2'],
                                    operators_df, column_to_edit=7)
    assign_operators_to_tasks_cells(bakut_worksheet, tasks_df.loc[tasks_df.name == 'Sofash bakut night 1'],
                                    operators_df, column_to_edit=7, is_weekend=True)

    blacken_empty_cells(bakut_worksheet)
    output_workbook.save(file_path)


def add_production_sheet(file_path, tasks_df, operators_df):
    output_workbook = load_workbook(file_path)
    output_workbook.create_sheet('production')
    production_worksheet = output_workbook.get_sheet_by_name('production')
    add_sheet_titles(production_worksheet,
                     ['date', 'day', 'eo production', 'sar production', 'eo production operator',
                      'sar production operator'])
    add_dates_column(production_worksheet, row_length=6)

    assign_operators_to_tasks_cells(production_worksheet, tasks_df.loc[tasks_df.name == 'eo production'], operators_df,
                                    column_to_edit=3)
    assign_operators_to_tasks_cells(production_worksheet, tasks_df.loc[tasks_df.name == 'Sofash production'],
                                    operators_df, column_to_edit=3, is_weekend=True)
    assign_operators_to_tasks_cells(production_worksheet, tasks_df.loc[tasks_df.name == 'sar production'], operators_df,
                                    column_to_edit=4)
    assign_operators_to_tasks_cells(production_worksheet, tasks_df.loc[tasks_df.name == 'eo production operator'], operators_df,
                                    column_to_edit=5)
    assign_operators_to_tasks_cells(production_worksheet, tasks_df.loc[tasks_df.name == 'sar production operator'], operators_df,
                                    column_to_edit=6)

    blacken_empty_cells(production_worksheet)
    output_workbook.save(file_path)


def add_sheet_titles(worksheet_to_edit, titles: list):
    for title_index, title in enumerate(titles):
        worksheet_to_edit.cell(row=1, column=title_index + 1).value = title


def add_dates_column(worksheet_to_edit, row_length):
    for date in get_days_in_current_month():
        day_name = WEEKDAYS_LIST[us_day_to_il_day(date.weekday())]
        add_weekend_color(worksheet_to_edit, date, row_length=row_length)
        worksheet_to_edit.cell(row=date.day + 1, column=1).value = str(date)
        worksheet_to_edit.cell(row=date.day + 1, column=2).value = day_name


def add_weekend_color(worksheet_to_edit, date, row_length):
    if us_day_to_il_day(date.weekday()) in [5, 6]:
        for column_index in range(1, row_length + 1):
            worksheet_to_edit.cell(row=date.day + 1, column=column_index).fill = \
                PatternFill(start_color="e4e4e4", end_color="e4e4e4", fill_type="solid")


def assign_operators_to_tasks_cells(worksheet_to_edit, tasks_df, operators_df, column_to_edit, is_weekend=False):
    for _, task in tasks_df.iterrows():
        worksheet_to_edit.cell(row=task['start_time'].day + 1, column=column_to_edit).value = \
            operators_df.iloc[task['assignee']]['name']
        if is_weekend:
            worksheet_to_edit.cell(row=task['start_time'].day + 2, column=column_to_edit).value = \
                operators_df.iloc[task['assignee']]['name']


def blacken_empty_cells(worksheet_to_edit):
    for col in worksheet_to_edit:
        for cell in col:
            if not cell.value:
                cell.fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
