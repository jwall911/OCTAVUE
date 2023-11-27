import os
import subprocess
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, Date, Text, Integer, Float


def get_db_connection():
    server = os.environ.get('DB_SERVER', 'DESKTOP-671S80O\\SQLEXPRESS')
    database = os.environ.get('DB_DATABASE', 'UFCVUE')
    conn_string = f'mssql+pyodbc://{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'
    return create_engine(conn_string)


subprocess.run(['python', 'FighterScraper.py'])
file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "fighter-data-raw.csv"
data = pd.read_csv(file_name, encoding='ISO-8859-1')
dtype_dict = {
    'FighterID': Text(),
    'Name': Text(),
    'Height': Date(),
    'Weight': Integer(),
    'Reach': Integer(),
    'DOB': Integer(),
    'SSPM': Float(),
    'StrkACC': Float(),
    'SSAbsPM': Float(),
    'StrkDEF': Float(),
    'TDAVG': Float(),
    'TDACC': Float(),
    'TDDEF': Float(),
    'SUBAVG': Float(),
    'Wins': Integer(),
    'Losses': Integer(),
    'WLDiff': Float(),
    'Fire': Float()
    }
engine = get_db_connection()
data.to_sql('newAllFights', engine, if_exists='replace', index=False, dtype=dtype_dict)