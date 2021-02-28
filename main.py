from model import init_constraints
from Modules.dataImporter import CSV_importer
from output.output import convert_to_readable_df

DATA_PATH = 'DATA/DB.xlsx'

if __name__ == "__main__":
    tasks, operators = CSV_importer(DATA_PATH)

    shifts_model = init_constraints(tasks, operators)
    shifts_model.optimize()
    if shifts_model.num_solutions:
        dfs = convert_to_readable_df(shifts_model, "1/3/2021", "31/3/2021", tasks, operators)
        dfs[0].to_excel("./By operator.xlsx")
        # by task
        dfs[1].to_excel("./By task.xlsx")

