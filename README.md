# Top 10 Largest Banks by Market Capitalization — ETL Pipeline

## Problem
Bank market capitalization data is available online, but collecting, cleaning, and converting it into multiple currencies for financial analysis is time-consuming and repetitive.

## Solution
Built a Python-based ETL pipeline that:

- **Extracts:** Scrapes the top 10 largest banks by market capitalization from Wikipedia using BeautifulSoup.
- **Transforms:** Cleans financial data and converts USD values into GBP, EUR, and INR using exchange rates from a CSV file.
- **Loads:** Stores processed data in CSV and SQLite for querying and analysis.
- **Logs:** Tracks ETL execution stages with timestamps.
- **Analyzes:** Executes SQL queries to retrieve bank records and calculate market capitalization statistics.

## Tech Stack
Python, Pandas, NumPy, BeautifulSoup, Requests, SQLite, SQL, CSV, ETL
