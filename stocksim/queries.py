import yfinance as yf
from yfinance import EquityQuery


# Top n stocks returned as list of symbol-value tuples
def get_top_stocks(n):
    q1 = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 4000000000])
    ])
    q2 = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 2000000000]),
        EquityQuery('gte', ['intradayprice', 5]),
        EquityQuery('gt', ['dayvolume', 15000]),
        EquityQuery('gt', ['percentchange', 3])
    ])
    q3 = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 2000000000]),
        EquityQuery('gte', ['intradayprice', 5]),
        EquityQuery('gt', ['dayvolume', 20000]),
        EquityQuery('lt', ['percentchange', -2.5])
    ])

    res = {}
    try:

        tmp = []
        response = yf.screen(q1, sortField='intradaymarketcap', sortAsc=False, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["marketCap"])]
        res["top_cap"] = tmp
    except yf.exceptions.RateLimitError:
        print("Rate limit error")
    try:
        tmp = []
        response = yf.screen(q2, sortField='percentchange', sortAsc=False, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
        res["top_win"] = tmp
    except yf.exceptions.RateLimitError:
        print("Rate limit error")
    try:
        tmp = []
        response = yf.screen(q3, sortField='percentchange', sortAsc=True, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
        res["top_loss"] = tmp
    except yf.exceptions.RateLimitError:
        print("Rate limit error")
    return res
