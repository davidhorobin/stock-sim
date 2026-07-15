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
