import logging

import yfinance as yf
from yfinance import screen, Ticker, EquityQuery
from yfinance.exceptions import YFRateLimitError
from yfinance.utils import get_yf_logger

get_yf_logger().setLevel(logging.CRITICAL)


class SymbolNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


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
        response = screen(q1, sortField='intradaymarketcap', sortAsc=False, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["marketCap"])]
        res["top_cap"] = tmp

        tmp = []
        response = screen(q2, sortField='percentchange', sortAsc=False, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
        res["top_win"] = tmp

        tmp = []
        response = screen(q3, sortField='percentchange', sortAsc=True, size=n)
        for quote in response['quotes']:
            tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
        res["top_loss"] = tmp
    except YFRateLimitError:
        print("Rate limit error")
    return res


def get_stock(symbol):
    try:
        response = Ticker(symbol)
        if response.info.get("symbol") is None or response.info.get("quoteType") != "EQUITY":
            raise SymbolNotFoundError(f"Invalid stock symbol: {symbol}")
        else:
            return response.info
    except YFRateLimitError:
        raise SymbolNotFoundError(f"Rate limit error")
    except ValueError:
        raise SymbolNotFoundError(f"Empty stock symbol")
