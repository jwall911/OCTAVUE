import os
import subprocess
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, Date, Text


def get_db_connection():
    server = os.environ.get('DB_SERVER', 'DESKTOP-671S80O\\SQLEXPRESS')
    database = os.environ.get('DB_DATABASE', 'UFCVUE')
    conn_string = f'mssql+pyodbc://{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'
    return create_engine(conn_string)


subprocess.run(['python', 'UpcomingFightsScraper.py'])
file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "UpcomingEvents-data.csv"
data = pd.read_csv(file_name)
dtype_dict = {
    'EventID': Text(),
    'Name': Text(),
    'Date': Date(),
    'Location': Text()
}
engine = get_db_connection()
data.to_sql('UpcomingEvents', engine, if_exists='replace', index=False, dtype=dtype_dict)