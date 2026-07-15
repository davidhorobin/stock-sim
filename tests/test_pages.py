import pytest


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


def test_stockinfo(client):
    response = client.get('/stockinfo/')
    assert response.status_code == 200
    assert b"Name" not in response.data
    assert b"Symbol" in response.data


@pytest.mark.parametrize(('symbol', 'message'), (
        ('AAPL', b'Apple Inc.'),
        ('GOOG', b'Price'),
        ('WRONGSYMBOL', b'Invalid stock symbol'),
        ('', b'Please enter a stock symbol.'),
))
def test_stockinfo_validate_input(client, symbol, message):
    response = client.post('/stockinfo/', data={"symbol": symbol}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data
    assert response.history[0].status_code == 302
    assert response.history[0].location == f'/stockinfo/{symbol}'
