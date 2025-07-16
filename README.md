# Review Analyzer

A Python-based tool for analyzing customer return comments using OpenAI's GPT-4o model to extract customer sentiment and product feedback.

## Overview

This project processes customer return comments from various file formats, analyzes them using OpenAI's GPT models, and stores the results in DuckDB for further analysis. It extracts both product-related feedback and customer sentiment from return comments.

## Features

- Imports data from CSV, Excel, or Parquet files
- Processes data in batches to handle large datasets
- Analyzes comments using OpenAI GPT-4o for:
  - Product feedback themes and sentiment
  - Customer sentiment analysis
- Stores results in DuckDB for easy querying
- Exports analysis results to CSV files

## Requirements

- Python 3.8+
- DuckDB
- pandas
- openai
- duckdb
- openpyxl

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create an `apikey.py` file with your OpenAI API key:
   ```python
   def create_secret():
       import openai
       client = openai.OpenAI(api_key="your-api-key-here")
       return client
   ```

## Usage

The main workflow is in `main.ipynb` which:

1. Imports data from source files
2. Extracts relevant comments
3. Processes comments in batches through GPT-4o
4. Analyzes for product themes and customer sentiment
5. Stores results in DuckDB tables

## Prompt Files

The project uses three prompt files:
- `prompts/system_prompt.txt` - System context for GPT
- `prompts/product_prompt.txt` - Instructions for product feedback analysis
- `prompts/customer_sentiment_prompt.txt` - Instructions for customer sentiment analysis

## Data Processing

The tool processes data in these stages:
1. Import from source file to DuckDB
2. Extract comments with unique row IDs
3. Clean and sanitize comment text
4. Batch processing through OpenAI API
5. Parse and transform JSON responses
6. Store results in database and CSV files

## Limitations

- API costs will scale with dataset size
- Currently hardcoded for specific return comment schemas
- Error handling is basic, may need refinement for production

