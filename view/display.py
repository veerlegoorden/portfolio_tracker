#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26

@author: veerlegoorden
"""

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np

    
def show_portfolio(assets, portfolio):
    if not assets:
        print("Portfolio is empty.")
        return

    df = pd.DataFrame(assets)
    
    # Add current prices
    df["current_price"] = df["ticker"].apply(portfolio.get_current_price)
    df["current_value"] = df["quantity"] * df["current_price"]
    
    # PnL
    df["gain"] = df["current_value"] - df["transaction_value"]
    df["gain_pct"] = df["gain"] / df["transaction_value"] * 100

    # Total portfolio value
    total_value = df["current_value"].sum()
    df["weight"] = df["current_value"] / total_value * 100

    # Round nicely
    df = df.round(2)

    print(df[[
        "ticker", "sector", "asset_class", "quantity",
        "purchase_price", "transaction_value",
        "current_price", "current_value", "weight"
    ]])
    
    print(f"\nTotal portfolio value: ${total_value:,.2f}")
    print(f"Total PnL: ${df['gain'].sum():,.2f} ({df['gain'].sum() / df['transaction_value'].sum():.2%})")
      

def show_historical_prices(ticker, period="1mo"):  # nog aanpassen 
    import yfinance as yf

    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        print(f"No historical data found for {ticker}")
        return

    print(f"\nHistorical prices for {ticker} ({period}):\n")
    print(history["Close"].round(2))    
    
    
def show_summary_by(df, column):
    if column not in ["sector", "asset_class"]:
        print("Can only summarize by 'sector' or 'asset_class'")
        return

    summary = df.groupby(column)["current_value"].sum().reset_index()
    total = summary["current_value"].sum()
    summary["weight (%)"] = summary["current_value"] / total * 100
    summary = summary.round(2)
    print(f"\nPortfolio breakdown by {column}:")
    print(summary)
    
    
def plot_tickers(tickers, period="6mo", normalize=False):
    """
    Plots one or more tickers with optional normalization.
    """
    if isinstance(tickers, str):
        tickers = [tickers]  # Convert single ticker to list

    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if not hist.empty:
            prices = hist["Close"]
            if normalize:
                prices = prices / prices.iloc[0] * 100
            data[ticker] = prices
        else:
            print(f"No data for {ticker}")

    if not data:
        print("No valid tickers to plot.")
        return

    df = pd.DataFrame(data)
    title = f"{'Normalized ' if normalize else ''}Price History ({period})"
    ylabel = "Normalized Price (Start = 100)" if normalize else "Price ($)"

    df.plot(title=title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend(title="Ticker")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    


import matplotlib.ticker as mticker

def simulate_portfolio(portfolio, years=5, n_simulations=500, show_plot=True):
    tickers = list(set([asset["ticker"] for asset in portfolio.assets]))
    weights = {}

    total_current_value = 0
    for asset in portfolio.assets:
        current_price = portfolio.get_current_price(asset["ticker"])
        value = current_price * asset["quantity"]
        weights[asset["ticker"]] = weights.get(asset["ticker"], 0) + value
        total_current_value += value

    for t in weights:
        weights[t] /= total_current_value

    trading_days = years * 252
    all_simulations = np.zeros((n_simulations, trading_days))

    for sim in range(n_simulations):
        total_value = np.zeros(trading_days)

        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5y")
            daily_returns = hist["Close"].pct_change().dropna()

            mu = daily_returns.mean()
            sigma = daily_returns.std()
            drift = mu - 0.5 * sigma ** 2

            S0 = portfolio.get_current_price(ticker)
            weighted_value = S0 * weights[ticker] * total_current_value

            rand_returns = np.random.normal(loc=drift, scale=sigma, size=trading_days)
            price_path = S0 * np.exp(np.cumsum(rand_returns))

            total_value += (price_path / S0) * weighted_value

        all_simulations[sim] = total_value

    # Compute statistics across simulations
    mean_path = all_simulations.mean(axis=0)
    percentile_10 = np.percentile(all_simulations, 10, axis=0)
    percentile_90 = np.percentile(all_simulations, 90, axis=0)

    # Date index for x-axis
    start_date = pd.Timestamp.today()
    date_range = pd.bdate_range(start=start_date, periods=trading_days)

    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.plot(date_range, mean_path, label="Mean Outcome", color="blue")
        plt.fill_between(date_range, percentile_10, percentile_90, color="lightblue", alpha=0.4, label="10th–90th Percentile")

        plt.title(f"5-Year Portfolio Simulation ({n_simulations} runs)")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        ax = plt.gca()
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    # Return a DataFrame with all values
    results = pd.DataFrame({
        "Date": date_range,
        "Mean": mean_path,
        "Percentile_10": percentile_10,
        "Percentile_90": percentile_90
    })

    return results


def compare_with_benchmark(portfolio, benchmark="SPY", period="1y"):
    import matplotlib.pyplot as plt
    import yfinance as yf

    df = pd.DataFrame(portfolio.assets)
    if df.empty:
        print("Portfolio is empty.")
        return

    # Build portfolio price series (equal or weighted allocation)
    prices = {}
    for ticker in df["ticker"].unique():
        hist = yf.Ticker(ticker).history(period=period)["Close"]
        prices[ticker] = hist

    portfolio_df = pd.DataFrame(prices).dropna()
    normalized = portfolio_df / portfolio_df.iloc[0]  # Start at 1.0
    weighted = normalized.multiply(
        df.groupby("ticker")["transaction_value"].sum() /
        df["transaction_value"].sum(), axis=1
    )
    portfolio_series = weighted.sum(axis=1)

    # Get benchmark (e.g. SPY)
    benchmark_series = yf.Ticker(benchmark).history(period=period)["Close"]
    benchmark_series = benchmark_series / benchmark_series.iloc[0]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(portfolio_series, label="Your Portfolio")
    plt.plot(benchmark_series, label=f"{benchmark}")
    plt.title("Portfolio vs Benchmark")
    plt.xlabel("Date")
    plt.ylabel("Normalized Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
def calculate_risk_metrics(portfolio, period="1y", risk_free_rate=0.02):
    import yfinance as yf
    df = pd.DataFrame(portfolio.assets)
    if df.empty:
        print("Portfolio is empty.")
        return

    prices = {}
    for ticker in df["ticker"].unique():
        hist = yf.Ticker(ticker).history(period=period)["Close"]
        prices[ticker] = hist

    portfolio_df = pd.DataFrame(prices).dropna()
    normalized = portfolio_df / portfolio_df.iloc[0]
    weighted = normalized.multiply(
        df.groupby("ticker")["transaction_value"].sum() /
        df["transaction_value"].sum(), axis=1
    )
    portfolio_series = weighted.sum(axis=1)
    daily_returns = portfolio_series.pct_change().dropna()

    # Risk metrics
    volatility = daily_returns.std() * np.sqrt(252)
    mean_return = daily_returns.mean() * 252
    sharpe = (mean_return - risk_free_rate) / volatility
    percentile_5 = np.percentile(daily_returns, 5)
    var_95 = -min(percentile_5, 0) * portfolio_series.iloc[-1]

    print("Risk Metrics:")
    print(f"  Annualized Volatility: {volatility:.2%}")
    print(f"  Annualized Return:     {mean_return:.2%}")
    print(f"  Sharpe Ratio:          {sharpe:.2f}")
    print(f"  Value-at-Risk (95%):   ${var_95:,.0f}")
