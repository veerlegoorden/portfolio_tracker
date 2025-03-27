# Investment Portfolio Tracker - CLI Application

This is a Python command-line application to manage and analyze a portfolio.

Note: Everything with ‘Extra’ is an addition to the described project.  

---

### 1. Add Assets to the Portfolio

Users can add assets by specifying:
- Ticker
- Sector
- Asset class
- Quantity
- Purchase price

Implemented in:
- File: model/portfolio.py  


Example command:
python main.py add –ticker AAPL –sector Tech –class_ Equity –quantity 10 –price 150


---

### 2. Show Current and Historical Prices + Graphs

View historical and current prices and create price graphs for one or more tickers.

Implemented in:
- File: view/display.py

Example commands:
python main.py history –ticker AAPL –period 1mo
python main.py graph AAPL MSFT XOM –period 6mo –normalize

EXTRA:
- Normalize prices across tickers using `--normalize` to compare relative performance over time.

---

### 3. View the Current Portfolio

Displays for each asset:
- Ticker
- Sector
- Asset class
- Quantity
- Purchase price
- Transaction value
- Current value

Displays for portfolio:
- PnL (based on purchase price) (Extra)
- Total portfolio value

Example command:
python main.py view

---

### 4. Show Portfolio Value and Asset Weights (by asset, sector, class)

Calculates:
- Total portfolio value (see 3.)
- Relative weights of assets (individual asset value / total value) (see 3.)

Example commands:
python main.py view
python main.py summary —by asset_class

---

### 5. Portfolio Simulation (5-Year Horizon)

Simulates portfolio value over 5 years based on historical data. Uses log-normal return simulation and returns results for:
- 90th percentile returns
- Base case
- 10th percentile returns

Also calculates:
- Final values for each scenario
- Total and annualized return

Command:
python main.py simulate –years 5 –runs 100

---

### Additions (Extra)
- PnL 
- Annualized volatility
- Annualized return
- Sharpe ratio
- Value at Risk (VaR)
- Benchmark (S&P500) comparison





