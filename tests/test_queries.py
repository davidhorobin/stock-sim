import pytest
from yfinance.exceptions import YFRateLimitError
from requests.models import Response
from stocksim import queries


class FakeTicker:
    def __init__(self, info):
        self.info = info


def test_get_stock_success(app, monkeypatch):
    fake_aapl = FakeTicker({"symbol": "AAPL", "quoteType": "EQUITY"})
    monkeypatch.setattr("stocksim.queries.Ticker", lambda symbol: fake_aapl)

    result = queries.get_stock("AAPL")
    assert result == fake_aapl.info


@pytest.mark.parametrize(("symbol", "message"), (
        ("GOOG", "Invalid stock symbol"),
        ("VOO", "Invalid stock symbol"),
        ("", "Empty stock symbol"),
))
def test_get_stock_fail(monkeypatch, symbol, message):
    def fake_fetch(symbol):
        if symbol == "VOO":
            return FakeTicker({"symbol": "VOO", "quoteType": "ETF"})
        elif symbol != "":
            return FakeTicker({})
        else:
            raise ValueError

    monkeypatch.setattr("stocksim.queries.Ticker", fake_fetch)
    result = None
    with pytest.raises(queries.SymbolNotFoundError) as e:
        result = queries.get_stock(symbol)
    assert message in str(e)
    assert result is None


def test_get_stock_rate_limited(monkeypatch):
    def fake_fetch(symbol):
        raise YFRateLimitError()

    monkeypatch.setattr("stocksim.queries.Ticker", fake_fetch)
    result = None
    with pytest.raises(queries.SymbolNotFoundError) as e:
        result = queries.get_stock("AAPL")
    assert "Rate limit error" in str(e)
    assert result is None


@pytest.mark.parametrize(("top_cap", "top_win", "top_loss"), (
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
))
def test_top_stock_rate_limited(monkeypatch, top_cap, top_win, top_loss):
    def fake_rate_limited(symbol):
        raise YFRateLimitError()

    if top_cap:
        monkeypatch.setattr("stocksim.queries.get_top_cap", fake_rate_limited)
    if top_win:
        monkeypatch.setattr("stocksim.queries.get_top_win", fake_rate_limited)
    if top_loss:
        monkeypatch.setattr("stocksim.queries.get_top_loss", fake_rate_limited)

    result = None
    with pytest.raises(queries.SymbolNotFoundError) as e:
        result = queries.get_top_stocks(5)
    assert "Rate limit error" in str(e)
    assert result is None


@pytest.mark.parametrize("code", (
        408,
        403,
        404,
        308,
        307,
        301
))
def test_get_top_articles_no_response(monkeypatch, code):
    def fake_fetch(url):
        r = Response()
        r.status_code = code
        return r

    monkeypatch.setattr("stocksim.queries.get", fake_fetch)
    result = None
    with pytest.raises(queries.SymbolNotFoundError) as e:
        result = queries.get_top_articles()
    assert "No response from SeekingAlpha" in str(e)
    assert result is None
