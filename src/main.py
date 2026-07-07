import yfinance as yf

def main():
    dat = yf.Ticker("MSFT")
    print(dat.fast_info["last_price"])

if __name__ == '__main__':
    main()