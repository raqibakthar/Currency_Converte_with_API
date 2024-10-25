import requests
import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
DB = sqlite3.connect('currency_history.db')
CONNECTION = DB.cursor()
API_KEY = os.getenv('API_KEY')
API_URL = "https://v6.exchangerate-api.com/v6/"

CURRENCIES_AVAILABLE = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'AUD': 'Australian Dollar',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    'INR': 'Indian Rupee',
    'SGD': 'Singapore Dollar',
    'AED': 'UAE Dirham',
    'SAR': 'Saudi Riyal',
    'QAR': 'Qatari Riyal',
    'KWD': 'Kuwaiti Dinar',
    'BHD': 'Bahraini Dinar',
    'OMR': 'Omani Rial',
    'NZD': 'New Zealand Dollar',
}

def setup_database():
        CONNECTION.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_currency TEXT,
                to_currency TEXT,
                amount REAL,
                converted_amount REAL,
                rate REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        DB.commit()

def display_currencies():
    print("Code | Currency Name")
    print("-"*25)
    for code, name in sorted(CURRENCIES_AVAILABLE.items()):
        print(f"{code} | {name}")

def get_exchange_rate( from_currency, to_currency):    
        url = f"{API_URL}{API_KEY}/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        return float(data['conversion_rates'][to_currency])

def save_conversion( from_currency, to_currency, amount, converted_amount, rate):
        CONNECTION.execute('''
            INSERT INTO conversions 
            (from_currency, to_currency, amount, converted_amount, rate) 
            VALUES (?, ?, ?, ?, ?)
        ''', (from_currency, to_currency, amount, converted_amount, rate))
        DB.commit()

def get_conversion_history(limit=10):
        
        CONNECTION.execute('''
            SELECT * FROM conversions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return CONNECTION.fetchall()

def main():
        
    while True:
        print("\nCurrency Converter Menu:")
        print("1. List supported currencies")
        print("2. Convert currency")
        print("3. View conversion history")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            display_currencies()

        elif choice == '2':
            display_currencies()
            from_currency = input("\nEnter from currency code: ").upper()
            to_currency = input("Enter to currency code: ").upper()
            
            if from_currency not in CURRENCIES_AVAILABLE or to_currency not in CURRENCIES_AVAILABLE:
                print("Error: Please choose from supported currencies only.")
                continue
            
            try:
                amount = float(input("Enter amount: "))
            except ValueError:
                print("Error: Please enter a valid number.")
                continue

            rate = get_exchange_rate(from_currency, to_currency)
            if rate:
                converted_amount = amount * rate
                print(f"\nConversion Result:")
                print(f"{amount} {from_currency} = {converted_amount} {to_currency}")
                save_conversion(from_currency, to_currency, amount, converted_amount, rate)
                
        elif choice == '3':
                
                print('recent history\n')
                print("Date                | From  | To  | Amount   | Converted  | Rate")
                
                
                history = get_conversion_history(1)
                for record in history:
                    timestamp = record[6]
                    print(f"{timestamp:<19} | {record[1]:<5} | {record[2]:<5} | {record[3]:<11.2f} | {record[4]:<11.2f} | {record[5]:.4f}")

        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")


if __name__=='__main__':
        
        setup_database()
        main()
