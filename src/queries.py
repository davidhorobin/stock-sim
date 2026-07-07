import yfinance as yf
from yfinance import EquityQuery


# Top n stocks returned as list of symbol-value tuples
def get_top_stocks(n):
    q = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 4000000000])
    ])
    response = yf.screen(q, sortField='intradaymarketcap', sortAsc=False, size=n)

    res = []
    for quote in response['quotes']:
        res += [(quote['symbol'], quote["regularMarketPrice"])]

    return res
