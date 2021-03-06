from mip import SearchEmphasis
from model import init_constraints
from output.output import convert_to_readable_df, color_cells
from output.tasks_sheets import add_tasks_sheets
from utils.model_utils import get_tasks_assignee
from Modules.dataImporter import import_data_from_excel
import time

DATA_PATH = 'DATA/DB.xlsx'
OUTPUT_PATH = './output/Butzi.xlsx'

if __name__ == "__main__":
    t = time.time()

    tasks, operators = import_data_from_excel(DATA_PATH)
    print(f'number of tasks {len(tasks)}')

    shifts_model = init_constraints(tasks, operators)

    shifts_model.emphasis = SearchEmphasis.OPTIMALITY

    shifts_model.optimize(max_seconds_same_incumbent=10)

    print(f"overall time: {time.time() - t}")

    if shifts_model.num_solutions:
        print(f'objective value {shifts_model.objective_value}')
        tasks['assignee'] = get_tasks_assignee(shifts_model, tasks)
        final_df_with_data = convert_to_readable_df(shifts_model, tasks, operators, DATA_PATH)
        final_df = final_df_with_data[0]
        color_dict = final_df_with_data[1]

        try:
            final_df.T.to_excel(OUTPUT_PATH)
        except:
            for x in range(30):
                print("Close output file!")
            x = input('press something')
            final_df.T.to_excel(OUTPUT_PATH)

        color_cells(OUTPUT_PATH, shifts_model, color_dict, operators, tasks)
        add_tasks_sheets(OUTPUT_PATH, tasks, operators)

    else:
        print("DAMN! no feasable solution found")
