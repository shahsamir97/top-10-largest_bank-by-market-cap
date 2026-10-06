import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

url = "https://en.wikipedia.org/wiki/List_of_largest_banks"

headers = {
    'User-Agent': 'MyLearningProject/1.0'
}

sql_conn = sqlite3.connect('Banks.db')

table_name = "Largest_banks"

table_attributes = [
    'Name',
    'MC_USD_Billion'
]

log_file = "code_log.txt"
output_csv = "Largest_banks_data.csv"


def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.datetime.now()
    timestamp = now.strftime(timestamp_format)

    with open(log_file, "a") as f:
        f.write(timestamp + ' : ' + message + '\n')


def extract(url, table_attribs=None):

    if table_attribs is None:
        table_attribs = ['Name', 'MC_USD_Billion']

    df = pd.DataFrame(columns=table_attribs)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('tbody')
        target_table = tables[2]
        rows = target_table.find_all('tr')

        for row in rows:

            cols = row.find_all('td')

            if len(cols) != 0:

                data = {
                    'Name': cols[0].text.strip(),
                    'MC_USD_Billion': cols[2].text.strip()
                }

                df = pd.concat(
                    [df, pd.DataFrame([data])],
                    ignore_index=True
                )

    # Clean the Market Cap column
    df['MC_USD_Billion'] = (
        df['MC_USD_Billion']
        .str.replace(',', '', regex=False)
        .str.replace('$', '', regex=False)
    )

    # Convert Market Cap to numeric INSIDE extract()
    df['MC_USD_Billion'] = pd.to_numeric(
        df['MC_USD_Billion'],
        errors='coerce'
    )

    # Remove rows where Market Cap could not be converted
    df = df.dropna(subset=['MC_USD_Billion'])

    # Keep only top 10 banks
    df = df.head(10)

    return df


def transform(df, csv_path):

    rates_df = pd.read_csv(csv_path)

    eur_rate = rates_df.loc[
        rates_df['Currency'] == 'EUR',
        'Rate'
    ].iloc[0]

    gbp_rate = rates_df.loc[
        rates_df['Currency'] == 'GBP',
        'Rate'
    ].iloc[0]

    inr_rate = rates_df.loc[
        rates_df['Currency'] == 'INR',
        'Rate'
    ].iloc[0]

    df['MC_GBP_Billion'] = np.round(
        df['MC_USD_Billion'] * gbp_rate,
        2
    )

    df['MC_EUR_Billion'] = np.round(
        df['MC_USD_Billion'] * eur_rate,
        2
    )

    df['MC_INR_Billion'] = np.round(
        df['MC_USD_Billion'] * inr_rate,
        2
    )

    df['MC_USD_Billion'] = np.round(
        df['MC_USD_Billion'],
        2
    )

    return df


def load_to_csv(df, output_path):

    df.to_csv(output_path, index=False)

    # Required by feedback
    log_progress(
        f"Data saved to CSV file at {output_path}"
    )


def load_to_db(df, sql_connection, table_name):

    df.to_sql(
        table_name,
        sql_connection,
        if_exists='replace',
        index=False
    )

    # Required by feedback
    log_progress(
        f"Data loaded to database table {table_name}"
    )


def run_query(query, sql_conn):

    output = pd.read_sql(query, sql_conn)
    print(output)


# -----------------------
# ETL PROCESS
# -----------------------

log_progress(
    "Preliminaries complete. Initiating ETL process"
)

extracted_df = extract(
    url,
    table_attributes
)

log_progress(
    "Data extraction complete. Initiating Transformation process"
)

transformed_df = transform(
    extracted_df,
    'exchange_rate.csv'
)

log_progress(
    "Data transformation complete. Initiating Loading process"
)

load_to_csv(
    transformed_df,
    output_csv
)

load_to_db(
    transformed_df,
    sql_conn,
    table_name
)

log_progress(
    "Data loaded to Database as a table, Executing queries"
)

run_query(
    f"SELECT * FROM {table_name} LIMIT 5",
    sql_conn
)

run_query(
    f"SELECT AVG(MC_GBP_Billion) FROM {table_name}",
    sql_conn
)

run_query(
    f"SELECT Name FROM {table_name} LIMIT 5",
    sql_conn
)

log_progress("Process Complete")

sql_conn.close()

log_progress("Server Connection closed")