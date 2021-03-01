from model import init_constraints
from Modules.dataImporter import CSV_importer
from output.output import convert_to_readable_df
import time

DATA_PATH = 'DATA/DB.xlsx'

if __name__ == "__main__":
    t = time.time()

    tasks, operators = CSV_importer(DATA_PATH)
    print(f'number of tasks {len(tasks)}')

    shifts_model = init_constraints(tasks, operators)

    shifts_model.optimize()

    print(time.time() - t)

    if shifts_model.num_solutions:
        print(f'objective value {shifts_model.objective_value}')
        final_df = convert_to_readable_df(shifts_model, tasks, operators, DATA_PATH)
        final_df.T.to_excel('./output/dani.xlsx')
