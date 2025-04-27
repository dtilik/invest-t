#!/usr/bin/env python3
"""
Account Manager for Tinkoff Invest API
This script provides a simple CLI to create and list Tinkoff Invest accounts
"""
import argparse
from bot import TradingBot

def main():
    parser = argparse.ArgumentParser(description='Tinkoff Invest Account Manager')
    parser.add_argument('action', choices=['create', 'list'], 
                      help='Action to perform: create a new account or list existing accounts')
    
    args = parser.parse_args()
    
    # Initialize the trading bot (which has our account management methods)
    bot = TradingBot()
    
    if args.action == 'create':
        print("Creating new account...")
        account_id = bot.create_new_account()
        if account_id:
            print(f"Successfully created account with ID: {account_id}")
    elif args.action == 'list':
        print("Listing accounts...")
        accounts = bot.list_accounts()
        if not accounts:
            print("No accounts found or an error occurred.")

if __name__ == "__main__":
    main()
