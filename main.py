from model import *
from Modules import dataImporter

DB_PATH = './DATA/DB.xlsx'

if __name__ == "__main__":
    tasks, operators = dataImporter.CSV_importer(DB_PATH)
    init_constraints(tasks, operators)
