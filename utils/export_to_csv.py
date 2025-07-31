import pymongo
import csv
import json
import os
from datetime import datetime

def export_symbol_to_csv(symbol, collection, start_date, end_date, output_dir="symbol_data"):
    # Define query for the symbol
    query = {
        "$and": [
            {
                "transaction_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            {
                "symbol": symbol
            }
        ]
    }

    # Fields to include in CSV
    csv_columns = [
        "transaction",
        "id",
        "symbol",
        "buyer",
        "seller",
        "quantity",
        "rate",
        "amount",
        "transaction_date"
    ]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Output CSV filename
    csv_file = f"{output_dir}/{symbol}_transactions.csv"

    try:
        # Open CSV file for writing
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            
            # Query MongoDB and write each document to CSV
            for doc in collection.find(query):
                # Prepare row data (excluding _id)
                row = {field: doc[field] for field in csv_columns}
                writer.writerow(row)
        
        count = collection.count_documents(query)
        print(f"Exported {count:4} records | {symbol}")
        return count
    
    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
        return 0

def main():
    # Load symbols from JSON file (assuming your provided data is in symbols.json)
    try:
        with open('symbol_sector.json', 'r') as f:
            symbols_data = json.load(f)
    except FileNotFoundError:
        print("Error: symbols.json file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in symbols.json")
        return

    # MongoDB connection setup
    client = pymongo.MongoClient("mongodb://admin:n3p53db53rv3raXios@157.245.110.154:34554/admin")  # Update with your connection string
    db = client["admin"]  # Update with your database name
    collection = db["scraped_data"]  # Update with your collection name

    # Date range
    start_date = "2025-05-01"
    end_date = "2025-07-30"

    print("\nExporting symbol data from MongoDB to CSV:")
    print("========================================")

    # Process each symbol
    total_documents = 0
    symbols_processed = 0
    
    # Extract just the symbol keys from your JSON (ignore the categories)
    symbols = list(symbols_data.keys())
    
    for symbol in symbols:
        count = export_symbol_to_csv(
            symbol, 
            collection, 
            start_date, 
            end_date
        )
        total_documents += count
        if count > 0:
            symbols_processed += 1

    print("========================================")
    print(f"\nSummary:")
    print(f"- Total symbols processed: {len(symbols)}")
    print(f"- Symbols with data exported: {symbols_processed}")
    print(f"- Total documents exported: {total_documents}")
    
    client.close()

if __name__ == "__main__":
    main()