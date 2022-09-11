import pandas as pd
import numpy as np
import sqlite3 as sql

def queryDB(query):
    conn = sql.connect('COVID/covid.db')
    cursor = conn.cursor()
    cursor.arraysize = 10000
    cursor.execute(query)
    names = [ x[0] for x in cursor.description]
    rows =   cursor.fetchall()
    result_opened = pd.DataFrame(rows, columns=names)
    conn.close()
    return result_opened

def casesFormat(row):
    if((np.isnan(row['cases_DIFF'])) | (np.isinf(row['cases_DIFF']))):
        pct = '0%'
    else: 
        pct = format(row.cases_DIFF, ',.1%')
    return f"""<span>{format(row.casosAcumulado_current, ",")}</span><span class="extra">{pct}</span>"""

def defuncFormat(row):
    if((np.isnan(row['defunc_DIFF'])) | (np.isinf(row['defunc_DIFF']))):
        pct = '0%'
    else: 
        pct = format(row.defunc_DIFF, ',.1%')
    return f"""<span>{format(row.obitosAcumulado_current, ",")}</span><span class="extra">{pct}</span>"""

def estadoFormat(row):
    return f"""<i class='fi {'fi-sr-angle-circle-up up' if row.growing else 'fi-sr-angle-circle-down down'} data-icon'></i><span>{row.estado}</span>"""

def assignGeoData(geo, df):
    ufs = geo['features']
    for uf in ufs:
        uf['properties']['cases'] = df[df.estado == uf['properties']['UF_05']]['casosAcumulado_current'].values[0]
    return geo