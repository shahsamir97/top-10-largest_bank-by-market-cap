import pandas as pd 
import numpy as np 
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

url = "https://en.wikipedia.org/wiki/List_of_largest_banks"
headers = {
    'User-Agent': 'MyLearningProject/1.0 (contact: mdshahsamir1997@gmail.com)'
}

sql_conn = sqlite3.connect('Banks.db')
table_name = "Largest_banks"
table_attributes = ['Name', 'MC_USD_Billion', 'MC_GBP_Billion', 'MC_EUR_Billion', 'MC_INR_Billion']
log_file = "code_log.txt"
output_csv = "Largest_banks_data.csv"

def log_progress(message): 
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.datetime.now()
    timestamp = now.strftime(timestamp_format) 
    with open(log_file, "a") as f: 
        f.write(timestamp + ' : ' + message + '\n')

def extract(url):
    df = pd.DataFrame(columns=['Name', 'MC_USD_Billion'])
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('tbody')
        target_table = table[2]
        rows = target_table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                data = {'Name': cols[0].text.strip(), 'MC_USD_Billion': cols[2].contents[0]}
                df = pd.concat([df, pd.DataFrame([data], index=[0])], ignore_index=True)
    return df

def transform(df, csv_path):

    with open(csv_path, 'r') as file:
        rates_df = pd.read_csv(file)

        eur_rate = rates_df.loc[rates_df['Currency'] == 'EUR', 'Rate'].iloc[0]
        gbp_rate = rates_df.loc[rates_df['Currency'] == 'GBP', 'Rate'].iloc[0]
        inr_rate = rates_df.loc[rates_df['Currency'] == 'INR', 'Rate'].iloc[0]

        df['MC_USD_Billion'] = df['MC_USD_Billion'].astype(float)

        df['MC_GBP_Billion'] = [np.round(x * gbp_rate, 2) for x in df['MC_USD_Billion']]
        df['MC_INR_Billion'] = [np.round(x * inr_rate, 2) for x in df['MC_USD_Billion']]
        df['MC_EUR_Billion'] = [np.round(x * eur_rate, 2) for x in df['MC_USD_Billion']]
        df['MC_USD_Billion'] = [np.round(x, 2) for x in df['MC_USD_Billion']]

        return df
     

def load_to_csv(df, output_csv):
    df.to_csv(output_csv, index=False)

def load_to_sqlite(df, sql_conn, table_name):
    df.to_sql(table_name, sql_conn, if_exists='replace', index=False)


def run_query(query, sql_conn):
    output = pd.read_sql(query, sql_conn)
    print(output)

log_progress("Preliminaries complete. Initiating ETL process")

extracted_df = extract(url)
log_progress("Data extraction complete. Initiating Transformation process")

transformed_df = transform(extracted_df, 'exchange_rate.csv')
log_progress("Data transformation complete. Initiating Loading process")

load_to_csv(transformed_df, output_csv)
log_progress("Data saved to CSV file")

log_progress("SQL Connection initiated")
load_to_sqlite(transformed_df, sql_conn, table_name)

log_progress("Data loaded to Database as a table, Executing queries")
run_query(f"SELECT * FROM {table_name} limit 5", sql_conn)
run_query(f"SELECT AVG(MC_GBP_Billion) FROM {table_name}", sql_conn)
run_query(f"SELECT Name from {table_name} LIMIT 5", sql_conn)
log_progress("Process Complete")

sql_conn.close()
log_progress("Server Connection closed")
