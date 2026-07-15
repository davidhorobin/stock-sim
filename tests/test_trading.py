import pytest
from stocksim.db import get_db


def test_portfolio(client, auth):
    response = client.get('/portfolio')
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

    auth.login()
    response = client.get('/portfolio')
    assert response.status_code == 200
    assert b"test1" in response.data
    assert b"portfolio" in response.data


def test_buy(client, auth):
    response = client.get('/buy')
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'

    auth.login()
    response = client.get('/buy')
    assert response.status_code == 200
    assert b"Buy Stocks" in response.data
