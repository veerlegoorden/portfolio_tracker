#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26

@author: veerlegoorden

PnL toevoegen?
"""

import json
import os
import yfinance as yf

class Portfolio:
    def __init__(self, file_path='data/portfolio.json'):
        self.assets = []
        self.file_path = file_path
        self.load()

    def add_asset(self, ticker, sector, asset_class, quantity, price):
        asset = {
            'ticker': ticker,
            'sector': sector,
            'asset_class': asset_class,
            'quantity': quantity,
            'purchase_price': price,
            'transaction_value': quantity * price
        }
        self.assets.append(asset)
        self.save()
    
    
    def save(self):
        # Create the folder if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        # Save assets as JSON
        with open(self.file_path, 'w') as f:
            json.dump(self.assets, f)

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.assets = json.load(f)
        else:
            self.assets = []

    def get_current_price(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.history(period="1d")["Close"].iloc[-1]
            return round(current_price, 2)
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None
        
    def delete_asset(self, ticker):
        original_len = len(self.assets)
        self.assets = [a for a in self.assets if a['ticker'].upper() != ticker.upper()]
        self.save()
        print(f"Deleted {original_len - len(self.assets)} asset(s) with ticker '{ticker}'.")
        
    def clear_portfolio(self):
        self.assets = []
        self.save()
        print("Portfolio cleared.")
        
    
