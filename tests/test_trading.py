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


@pytest.mark.parametrize(('symbol', 'value'), (
        ('AAPL', 2000),
        ('GOOG', 10000),
        ('VOD.L', 0.01),
))
def test_buy_success(app, client, auth, monkeypatch, symbol, value):
    monkeypatch.setattr("stocksim.trading.get_stock", lambda symbol: {"regularMarketPrice": 100})

    auth.login()
    response = client.post(f'/buy/{symbol}', data={'value': value}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your portfolio' in response.data
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


@pytest.mark.parametrize(('buy_symbol', 'buy_value', 'sell_price', 'sell_symbol', 'sell_amount'), (
        ('AAPL', 1000, 120, 'AAPL', 1200),
        ('AAPL', 1000, 50, 'AAPL', 500),
        ('AAPL', 1000, 100, 'AAPL', 1000),
        ('AAPL', 1000, 120, 'AAPL', 1100),
        ('AAPL', 1000, 50, 'AAPL', 400),
        ('AAPL', 1000, 1000, 'AAPL', 0.01),
        ('AAPL', 1000, 100, 'AAPL', 999.99),
))
def test_sell_success(app, client, auth, monkeypatch, buy_symbol, buy_value, sell_price, sell_symbol, sell_amount):
    monkeypatch.setattr("stocksim.trading.get_stock", lambda symbol: {"regularMarketPrice": 100})
    auth.login()
    client.post(f'/buy/{buy_symbol}', data={'value': buy_value})
    monkeypatch.setattr("stocksim.trading.get_stock", lambda symbol: {"regularMarketPrice": sell_price})
    response = client.post('/sell', data={"symbol": sell_symbol, "sellamount": sell_amount}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your portfolio' in response.data
    assert response.history[0].status_code == 302
    assert response.history[0].location == '/portfolio'

    with app.app_context():
        db = get_db()
        ledger = db.execute('SELECT * FROM ledger WHERE user_id=1').fetchall()
        assert len(ledger) == 2
        assert ledger[0]['type'] == 'buy'
        assert ledger[1]['type'] == 'sell'
        assert ledger[1]['shares'] * ledger[1]['price'] == sell_amount
        cash = float(db.execute('SELECT cash FROM users WHERE id=1').fetchone()['cash'])
        assert cash == 9000 + sell_amount
        holding = db.execute('SELECT symbol, shares FROM holding WHERE user_id=1').fetchall()
        if ledger[0]['shares'] * sell_price == sell_amount:
            assert len(holding) == 0
        else:
            assert len(holding) == 1


@pytest.mark.parametrize(('buy_symbol', 'buy_value', 'sell_price', 'sell_symbol', 'sell_amount', 'message'), (
        ('AAPL', 1000, 100, 'AAPL', 1200, "Sell value exceeds held value"),
        ('AAPL', 1000, 100, 'AAPL', 0, "Value must be"),
        ('AAPL', 1000, 100, 'AAPL', 0.0001),
))
def test_sell_fail(app, client, auth, monkeypatch, buy_symbol, buy_value, sell_price, sell_symbol, sell_amount,
                   message):
    monkeypatch.setattr("stocksim.trading.get_stock", lambda symbol: {"regularMarketPrice": 100})
    auth.login()
    client.post(f'/buy/{buy_symbol}', data={'value': buy_value})
    db = get_db()
    cash = db.execute('SELECT cash FROM users WHERE id=1').fetchone()['cash']
    holdings = db.execute('SELECT symbol, shares FROM holding WHERE user_id=1').fetchall()
    monkeypatch.setattr("stocksim.trading.get_stock", lambda symbol: {"regularMarketPrice": sell_price})
    response = client.post('/sell', data={"symbol": sell_symbol, "sellamount": sell_amount}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data
    assert response.request.path == '/sell'

    with app.app_context():
        ledger = db.execute('SELECT * FROM ledger WHERE user_id=1').fetchall()
        assert len(ledger) == 1
        assert ledger[0]['type'] == 'buy'
        assert cash == db.execute('SELECT cash FROM users WHERE id=1').fetchone()['cash']
        assert holdings == db.execute('Select symbol, shares FROM holding WHERE user_id=1').fetchall()
