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

def updaterecords():
    subprocess.run(['python', 'UfcRecordScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "ufcRecords-data.csv"
    data = pd.read_csv(file_name)
    dtype_dict = {
        'RecordType': Text(),
        'RecordHolder': Text(),
        'Record': Text(),
        'Date': Date(),
        'Event': Text()
    }
    engine = get_db_connection()
    data.to_sql('RecordBook', engine, if_exists='replace', index=False, dtype=dtype_dict)


def updateupcoming():
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


def updatepastevents():
    subprocess.run(['python', 'CompletedEventScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "CompletedEvents-data.csv"
    data = pd.read_csv(file_name, encoding='ISO-8859-1')
    dtype_dict = {
        'EventID': Text(),
        'Name': Text(),
        'Date': Date(),
        'Location': Text()
    }
    engine = get_db_connection()
    data.to_sql('CompletedEvents', engine, if_exists='replace', index=False, dtype=dtype_dict)

def updatefights():
    subprocess.run(['python', 'FightScraper.py'])
    file_name = "C:/Users/Josh/Desktop/" + str(date.today()) + "-" + "fight-data-raw.csv"
    data = pd.read_csv(file_name, encoding='ISO-8859-1')
    dtype_dict = {
        'EventID': Text(),
        'EventName': Text(),
        'Fighter1ID': Text(),
        'Fighter1Name': Text(),
        'Fighter2ID': Text(),
        'Fighter2Name': Text(),
        'WinnerID': Text()
    }
    engine = get_db_connection()
    data.to_sql('AllFights', engine, if_exists='replace', index=False, dtype=dtype_dict)


