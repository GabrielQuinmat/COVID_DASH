import time
import pandas as pd
import numpy as np
import sqlite3 as sql
import sqlalchemy as sa
import pyodbc
from glob import glob

path = "C:/Users/gquin/Downloads/HIST_PAINEL_COVIDBR_05set2022/"
files = glob(path + '*.csv', recursive=True)
df = pd.concat([pd.read_csv(file, delimiter=';') for file in files])

totalDF = df[df.regiao == 'Brasil']
stateDF = df[(df.regiao != 'Brasil') & (df.municipio.isna()) & (df.codmun.isna())]
granularDF = df[(df.regiao != 'Brasil') & (df.municipio.notna()) & (df.codmun.notna())]

conn = sql.connect('G:/Projects/Personal/Dash/COVID/covid.db')
totalDF.to_sql('global', conn, if_exists='replace', index=False)
stateDF.to_sql('state', conn, if_exists='replace', index=False)
granularDF.to_sql('granular', conn, if_exists='replace', index=False)
conn.close()


def timeit(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} took {end - start} seconds')
        return result
    return inner


totalDF = pd.read_sql_query('select * from global', conn)


@timeit
def getDF(table, conn, arraysize=1000):
    cursor = conn.cursor()
    cursor.arraysize = arraysize
    cursor.execute(f'SELECT * FROM {table}')
    names = [ x[0] for x in cursor.description]
    rows =   cursor.fetchall()
    result_opened = pd.DataFrame(rows, columns=names)
    return result_opened

totalDF = getDF('granular', conn)
totalDF = getDF('granular', conn, 5000)
totalDF = getDF('granular', conn, 10000) ## Mejor
totalDF = getDF('granular', conn, 50000)
totalDF = getDF('granular', conn, 100000)

engine = sa.create_engine('sqlite:///G:/Projects/Personal/Dash/COVID/covid.db', future=True)

@timeit
def getDF(table, engine):
    with engine.connect() as conn, conn.begin():
        query = conn.execute(f'SELECT * FROM {table}')         
        df = pd.DataFrame(query.fetchall())
        return df
    
totalDF = getDF('global', engine)


cnxn = pyodbc.connect("Driver=SQLite3;Database=G:/Projects/Personal/Dash/COVID/covid.db")
