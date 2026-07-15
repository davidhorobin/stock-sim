from instance.config import SECRET_KEY

# Stock Simulator

A Flask-based stock market trading simulator, simulating real stocks using
virtual cash and live market data.

## Features

- **Live stock data** - real-time prices via Yahoo Finance, using the
  [yfinance library](https://ranaroussi.github.io/yfinance/).
- **Real stocks trading** - trade stocks and shares using virtual cash,
  starting with $10,000.
- **Portfolio tracker** - keep all your holdings and profit/loss in one place.
- **Stock information** - easy access to live information on any stock given
  its ticker.
- **Summary homepage** - top stocks by market cap, daily winners, daily losers
  and latest market news all on one homepage.
- **Accounts and database integration** - create an account to save progress
  and check back any time.

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository
   ```
   git clone https://github.com/davidhorobin/stock-sim.git
   cd stock-sim
   ```
2. Create a venv
    ```
   python -m venv .venv
   ```
3. Activate venv \
   Windows Powershell
    ```
    .venv/Scripts/Activate.ps1
    ```
   Windows cmd
    ```
    .venv/Scripts/activate.bat
    ```
   Mac/Linux
    ```
    source .venv/bin/activate
    ```
4. Install requirements
    ```
    pip install -r requirements.txt
    ```
5. Set up configuration. Create an `instance/config.py` containing:
    ```python
    SECRET_KEY = "your-secret-key"
    ```
   (Optionally) Generate a secret key using Python
    ```python
    python -c 'import secrets; print(secrets.token_hex())'
    ```
6. Initialise the database
    ```
    flask --app stocksim init-db
    ```
7. Run tests
    ```
    pytest
    ```

## Help

For issues creating/activating virtual environment, check out the
[Python Docs](https://docs.python.org/3/library/venv.html).

## License

This project is licensed under the MIT License - see
[LICENSE.md](LICENSE.md) for details.

## Acknowledgements

- [Market news RSS feed by SeekingAlpha](https://seekingalpha.com/market_currents.xml)
- [Favicon by Vlad Szirka at Flaticon](https://www.flaticon.com/free-icons/forex)
- [Stock information by Yahoo Finance](https://finance.yahoo.com)