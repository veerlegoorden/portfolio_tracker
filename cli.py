#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 

@author: veerlegoorden

ka hij twee keet dezelfde kopen?
"""

import click
from model.portfolio import Portfolio
from view.display import show_portfolio, show_summary_by, plot_tickers

portfolio = Portfolio()

@click.group()
def cli():
    pass

# add
@cli.command()
@click.option('--ticker', required=True)
@click.option('--sector', required=True)
@click.option('--class_', required=True, help="Asset class (e.g., Equity, Bond)")
@click.option('--quantity', required=True, type=float)
@click.option('--price', required=True, type=float)
def add(ticker, sector, class_, quantity, price):
    portfolio.add_asset(ticker, sector, class_, quantity, price)
    click.echo(f"Added {ticker} to portfolio.")


# view
@cli.command()
def view():
    show_portfolio(portfolio.assets, portfolio)
    

@cli.command()
@click.argument('ticker')
def delete(ticker):
    """Delete all entries of a given ticker."""
    portfolio.delete_asset(ticker)
    

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to delete your entire portfolio?')
def clear():
    """Delete all assets from the portfolio."""
    portfolio.clear_portfolio()
   
    
# summary
@cli.command()
@click.option('--by', type=click.Choice(['sector', 'asset_class']), required=True)
def summary(by):
    """Show total value and weights by sector or asset class."""
    import pandas as pd

    df = pd.DataFrame(portfolio.assets)
    if df.empty:
        print("Portfolio is empty.")
        return

    # Add current values
    df["current_price"] = df["ticker"].apply(portfolio.get_current_price)
    df["current_value"] = df["quantity"] * df["current_price"]

    show_summary_by(df, by)
 
    
# history
@cli.command()
@click.option('--ticker', required=True)
@click.option('--period', default="1mo", help="e.g. 5d, 1mo, 3mo, 6mo, 1y")
def history(ticker, period):
    """Show historical closing prices for a ticker."""
    from view.display import show_historical_prices
    show_historical_prices(ticker, period)
    

# graph (can do both 1 and multiple)    
@cli.command(name="graph")
@click.argument('tickers', nargs=-1)
@click.option('--period', default="1y")
@click.option('--normalize', is_flag=True, help="Normalize prices to start at 100")
def graph(tickers, period, normalize):
    """Plot one or more tickers on a price graph."""
    plot_tickers(tickers, period, normalize)
    
    
# simulation
@cli.command()
@click.option('--years', default=5, help='Years to simulate')
@click.option('--runs', default=500, help='Number of simulations')
def simulate(years, runs):
    """Run Monte Carlo simulation with mean and confidence intervals."""
    from view.display import simulate_portfolio
    results = simulate_portfolio(portfolio, years=years, n_simulations=runs)

    # Initial and final values
    initial_value = results["Mean"].iloc[0]
    final_mean = results["Mean"].iloc[-1]
    final_p10 = results["Percentile_10"].iloc[-1]
    final_p90 = results["Percentile_90"].iloc[-1]

    # Returns for each case
    def calc_return(initial, final):
        total = final / initial - 1
        annual = (final / initial) ** (1 / years) - 1
        return total, annual

    mean_total, mean_annual = calc_return(initial_value, final_mean)
    p10_total, p10_annual = calc_return(initial_value, final_p10)
    p90_total, p90_annual = calc_return(initial_value, final_p90)

    # Output
    print("\nFinal Portfolio Value Estimates:")
    print(f"  Mean: ${final_mean:,.0f}")
    print(f"  10th percentile: ${final_p10:,.0f}")
    print(f"  90th percentile: ${final_p90:,.0f}")

    print("\nEstimated Returns:")
    print(f"  Mean - Total return: {mean_total:.2%}, Annualized: {mean_annual:.2%}")
    print(f"  10th percentile - Total return: {p10_total:.2%}, Annualized: {p10_annual:.2%}")
    print(f"  90th percentile - Total return: {p90_total:.2%}, Annualized: {p90_annual:.2%}")
    
 
# compare with benchmark
@cli.command()
@click.option('--benchmark', default="SPY", help="Benchmark ticker (default: SPY)")
@click.option('--period', default="1y", help="Period to compare (e.g. 6mo, 1y, 2y)")
def benchmark(benchmark, period):
    """Compare portfolio vs benchmark like S&P 500."""
    from view.display import compare_with_benchmark
    compare_with_benchmark(portfolio, benchmark, period)
    
  
# statistics and risk metrics
@cli.command()
@click.option('--period', default="1y", help="Period for risk metrics (e.g. 6mo, 1y)")
def risk(period):
    """Show risk metrics: volatility, Sharpe ratio, VaR."""
    from view.display import calculate_risk_metrics
    calculate_risk_metrics(portfolio, period)