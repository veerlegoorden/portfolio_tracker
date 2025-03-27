#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 

@author: veerlegoorden
"""

"""
Create a command-line interface (CLI) application to track a simple investment portfolio. The
application should at least allow users to:
    
1. Add assets to the portfolio, specifying the asset ticker (e.g.. AAPL, MSFT), the sector, asset
class, quantity, and purchase price.

2. Show the current and historical price of each asset ticker and be able to create a graph for
each ticker (or a combination of tickers).

3. View the current portfolio, displaying each asset's name, sector, asset class, quantity,
purchase price, transaction value and current value.

4. See calculations for the total portfolio value and the (relative) weights of each asset including
the option to see the same per asset class and sector.

5. Be able to perform a simulation over the upcoming five years for the portfolio,
demonstrating the impact of risk and uncertainty.

Use your own creativity to extend the functionality. You are allowed to use a LLM such as ChatGPT to
generate ideas.
"""

from controller.cli import cli

if __name__ == '__main__':
    cli()





