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
table_attributes = ['Name', 'MC_USD_billion', 'MC_GBP_Billion', 'MC_INR_billion']
log_file = "code_log.txt"
output_csv = "Largest_banks_data.csv"

def log_progress(message): 
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.datetime.now()
    timestamp = now.strftime(timestamp_format) 
    with open(log_file, "a") as f: 
        f.write(timestamp + ' : ' + message + '\n')

def extract(url):
    df = pd.DataFrame(columns=['Name', 'MC_USD_billion'])
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('tbody')
        target_table = table[2]
        rows = target_table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                data = {'Name': cols[0].text.strip(), 'MC_USD_billion': cols[2].contents[0]}
                df = pd.concat([df, pd.DataFrame([data], index=[0])], ignore_index=True)
    return df

def transform(df, csv_path):

    with open(csv_path, 'r') as file:
        rates_df = pd.read_csv(file)
        eur_rate = rates_df.loc[rates_df['Currency'] == 'EUR', 'Rate'].iloc[0]
        gbp_rate = rates_df.loc[rates_df['Currency'] == 'GBP', 'Rate'].iloc[0]
        inr_rate = rates_df.loc[rates_df['Currency'] == 'INR', 'Rate'].iloc[0]

        df['MC_GBP_Billion'] = df['MC_USD_billion'].astype(float) * gbp_rate
        df['MC_INR_billion'] = df['MC_USD_billion'].astype(float) * inr_rate
        df['MC_EUR_Billion'] = df['MC_USD_billion'].astype(float) * eur_rate

        return df
     

def load_to_csv(df, output_csv):
    df.to_csv(output_csv)

def load_to_sqlite(df, sql_conn, table_name):
    df.to_sql(table_name, sql_conn, if_exists='replace', index=False)

def run_query(query, sql_conn):
    output = pd.read_sql(query, sql_conn)
    print(output)

log_progress("Starting ETL process")

log_progress("Extraction started")
extracted_df = extract(url)
log_progress("Extraction completed")

log_progress("Transformation started")
transformed_df = transform(extracted_df, 'exchange_rate.csv')
log_progress("Transformation completed")

log_progress("Loading data to CSV and SQLite")
load_to_csv(transformed_df, output_csv)
log_progress(f"Data loaded to CSV: {output_csv}")
load_to_sqlite(transformed_df, sql_conn, table_name)
log_progress(f"Data loaded to SQLite table: {table_name}")

log_progress("ETL process completed")

log_progress("running query")
run_query(f"SELECT * FROM {table_name}", sql_conn)
