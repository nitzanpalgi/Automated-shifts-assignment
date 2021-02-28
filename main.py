from model import *
from Modules.dataImporter import CSV_importer

DATA_PATH = '../data/DB.xlsx'

if __name__ == "__main__":
    tasks, operators = CSV_importer(DATA_PATH)

    init_constraints()
