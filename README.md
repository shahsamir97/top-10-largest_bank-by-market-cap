# Bank Market Cap ETL Pipeline

## Problem

A research organization needs a repeatable way to identify the **top 10 largest banks in the world by market capitalization** and report their values in multiple currencies.

The raw data is available in USD, but the final report also requires market capitalization values in **GBP, EUR, and INR**. The processed data must then be stored both as a **CSV file** and in a **database** so the same workflow can be reused every financial quarter.

## Solution

I built an automated **ETL pipeline in Python** that:

- Extracts bank market-cap data from the web
- Cleans and converts the market-cap values into numeric format
- Selects the top 10 banks
- Reads currency exchange rates from a CSV file
- Converts USD values into GBP, EUR, and INR
- Saves the processed dataset to CSV
- Loads the data into an SQLite database
- Runs SQL queries to validate the stored data
- Logs each major stage of the ETL process

## How It Works

```text
Web Data
   ↓
Extract
   ↓
Clean & Select Top 10
   ↓
Transform with Exchange Rates
   ↓
CSV + SQLite Database
   ↓
SQL Validation
```

## Tech Stack

**Python · Pandas · NumPy · BeautifulSoup · Requests · SQLite · SQL**

## Key Takeaway

This project demonstrates how I built a reusable **end-to-end ETL workflow** that transforms raw web data into structured, analysis-ready data that can be regenerated for recurring financial reports.
