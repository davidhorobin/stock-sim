import pytest

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


def test_get_stock_limited(app, monkeypatch):
    assert True
