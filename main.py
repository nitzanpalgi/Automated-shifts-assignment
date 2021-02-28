from model import init_constraints
from Modules.dataImporter import CSV_importer

DATA_PATH = 'DATA/DB.xlsx'

if __name__ == "__main__":
    tasks, operators = CSV_importer(DATA_PATH)
    init_constraints(tasks, operators)
