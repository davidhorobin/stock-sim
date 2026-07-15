import pytest
from stocksim.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Log Out" in response.data
    assert b"test1" in response.data


def test_portfolio(client, auth):
    response = client.get('/portfolio')
    assert response.headers['Location'] == '/auth/login'

    auth.login()
    response = client.get('/portfolio')
    assert response.status_code == 200
    assert b"test1" in response.data
    assert b"portfolio" in response.data


def test_stockinfo(client):
    response = client.get('/stockinfo/')
    assert response.status_code == 200
    assert b"Name" not in response.data
    assert b"Symbol" in response.data


@pytest.mark.parametrize(('symbol', 'message'), (
        ('AAPL', b'AAPL'),
        ('GOOG', b'GOOG'),
        ('MSFT', b'MSFT'),
))
def test_stockinfo_validate_input(client, symbol, message):
    response = client.post('/stockinfo/', data={"symbol": symbol})
    assert response.status_code == 302
    assert response.headers['Location'] == '/stockinfo/' + symbol
    assert message in response.data
