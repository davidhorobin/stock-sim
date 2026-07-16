import logging
from re import findall
from requests import get

from yfinance import screen, Ticker, EquityQuery
from yfinance.exceptions import YFRateLimitError
from yfinance.utils import get_yf_logger
from .extensions import cache

get_yf_logger().setLevel(logging.CRITICAL)


class SymbolNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


# Top n stocks returned as list of symbol-value tuples
def get_top_stocks(n):
    res = {}
    try:
        res["top_cap"] = get_top_cap(n)
        res["top_win"] = get_top_win(n)
        res["top_loss"] = get_top_loss(n)
    except YFRateLimitError:
        raise SymbolNotFoundError(f"Rate limit error")
    return res


@cache.memoize(timeout=600)
def get_top_cap(n):
    q = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 4000000000])
    ])
    tmp = []
    response = screen(q, sortField='intradaymarketcap', sortAsc=False, size=n)
    for quote in response['quotes']:
        tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["marketCap"])]
    return tmp


@cache.memoize(timeout=120)
def get_top_win(n):
    q = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 2000000000]),
        EquityQuery('gte', ['intradayprice', 5]),
        EquityQuery('gt', ['dayvolume', 15000]),
        EquityQuery('gt', ['percentchange', 3])
    ])
    tmp = []
    response = screen(q, sortField='percentchange', sortAsc=False, size=n)
    for quote in response['quotes']:
        tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
    return tmp


@cache.memoize(timeout=120)
def get_top_loss(n):
    q = EquityQuery('and', [
        EquityQuery('eq', ['region', 'us']),
        EquityQuery('gte', ['intradaymarketcap', 2000000000]),
        EquityQuery('gte', ['intradayprice', 5]),
        EquityQuery('gt', ['dayvolume', 20000]),
        EquityQuery('lt', ['percentchange', -2.5])
    ])
    tmp = []
    response = screen(q, sortField='percentchange', sortAsc=True, size=n)
    for quote in response['quotes']:
        tmp += [(quote['symbol'], quote["regularMarketPrice"], quote["regularMarketChangePercent"])]
    return tmp


@cache.memoize(timeout=15)
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


@cache.memoize(timeout=120)
def get_top_articles():
    url = "https://seekingalpha.com/market_currents.xml"
    response = get(url)
    if response.status_code != 200:
        raise SymbolNotFoundError(f"No response from SeekingAlpha.")
    articles = findall(r"<title>.*</title>|<link>.*</link>|<pubDate>.*</pubDate>", response.text)
    return articles
