import pytest
from stocksim.db import get_db


@pytest.mark.parametrize('path', (
        '/portfolio',
        '/buy/',
        '/sell'
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'


def test_portfolio(client, auth):
    auth.login()
    response = client.get('/portfolio')
    assert response.status_code == 200
    assert b"test1" in response.data
    assert b"portfolio" in response.data


def test_buy(client, auth):
    auth.login()
    response = client.get('/buy/')
    assert response.status_code == 200
    assert b"Buy Stocks" in response.data


@pytest.mark.parametrize(('symbol', 'message'), (
        ('AAPL', b'Price'),
        ('GOOG', b'GOOG'),
        ('WRONGSYMBOL', b'Invalid stock symbol: WRONGSYMBOL'),
        ('VOO', b'Invalid stock symbol: VOO'),
        ('', b'Please enter a stock symbol.')
))
def test_buy_validate_lookup(client, auth, symbol, message):
    auth.login()
    response = client.post('/buy/', data={'symbol': symbol}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data
    assert response.history[0].status_code == 302
    assert response.history[0].location == f'/buy/{symbol}'


@pytest.mark.parametrize(('symbol', 'value', 'message'), (
        ('AAPL', 2000, b'Your portfolio'),
        ('GOOG', 10000, b'Your portfolio'),
        ('VOD.L', 0.01, b'Your portfolio'),
))
def test_buy_success(app, client, auth, monkeypatch, symbol, value, message):
    def fake_get_stock(symbol):
        return {"regularMarketPrice": 100}

    monkeypatch.setattr("stocksim.trading.get_stock", fake_get_stock)

    auth.login()
    response = client.post(f'/buy/{symbol}', data={'value': value}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data
    assert response.history[0].status_code == 302
    assert response.history[0].location == '/portfolio'
    with app.app_context():
        db = get_db()
        cash = float(db.execute('SELECT cash FROM users WHERE id=1').fetchone()['cash'])
        assert cash == 10000 - value
        holdings = db.execute('SELECT symbol, shares FROM holding WHERE user_id=1').fetchone()
        assert holdings['symbol'] == symbol
        assert holdings['shares'] == value / 100
        ledger = db.execute('SELECT * FROM ledger WHERE user_id=1').fetchall()
        assert len(ledger) == 1
        ledger = ledger[0]
        assert ledger['symbol'] == symbol
        assert ledger['shares'] == value / 100
        assert ledger['price'] == 100
        assert ledger['type'] == 'buy'


@pytest.mark.parametrize(('symbol', 'value', 'message'), (
        ('AAPL', 20000, b'Value of the stock exceeds account balance.'),
        ('AAPL', 0, b'Please enter a positive value.'),
        ('AAPL', -500, b'Please enter a positive value.'),
        ('AAPL', -50000, b'Please enter a positive value.'),
        ('AAPL', 0.0001, b'Value must be at least $0.01')
))
def test_buy_fail(app, client, auth, symbol, value, message):
    auth.login()
    response = client.post(f'/buy/{symbol}', data={'value': value}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data
    assert response.request.path == f'/buy/{symbol}'

    with app.app_context():
        db = get_db()
        cash = float(db.execute('SELECT cash FROM users WHERE id=1').fetchone()['cash'])
        assert cash == 10000
        holdings = db.execute('SELECT symbol, shares FROM holding WHERE user_id=1').fetchall()
        assert len(holdings) == 0
        ledger = db.execute('SELECT * FROM ledger WHERE user_id=1').fetchall()
        assert len(ledger) == 0


def test_sell(client, auth):
    auth.login()
    response = client.get('/sell')
    assert response.status_code == 200
    assert b"Sell" in response.data
    assert b"No holdings to sell" in response.data


@pytest.mark.parametrize(('symbol', 'value', 'message'), ())
def test_sell_success(client, auth):
    auth.login()
    response = client.get('/sell')
