import pytest
from flask import g, session
from stocksim.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post('/auth/register', data={'username': '1', 'password': '1'})
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute('SELECT * FROM users WHERE username = 1').fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '1', b'Username is required.'),
        ('', '', b'Username is required.'),
        ('1', '', b'Password is required.'),
        ('test1', '123', b'already exists.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post('/auth/register', data={'username': username, 'password': password})
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test1'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('test1', 'xxx', b'Incorrect username or password.'),
        ('xxxxx', '123', b'Incorrect username or password.'),
        ('test1', '321', b'Incorrect username or password.'),
        ('test2', '123', b'Incorrect username or password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
