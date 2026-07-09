from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import yfinance as yf
from stocksim.auth import login_required
from stocksim.db import get_db

bp = Blueprint('trading', __name__)


@bp.route('/portfolio')
@login_required
def portfolio():
    db = get_db()
    cash = db.execute('SELECT * FROM users WHERE id=?', (g.user[0],)).fetchone()['cash']
    assets = db.execute('SELECT * FROM holding WHERE id=?', (g.user[0],)).fetchall()
    asset_rows = []
    for asset in assets:
        tmp = {"symbol": asset["symbol"], "shares": asset["shares"]}
        price = yf.Ticker(tmp["symbol"]).info["regularMarketPrice"]
        tmp["price"] = price
        tmp["total"] = price * tmp["shares"]
        asset_rows.append(tmp)
    return render_template('trading/portfolio.html', balance=cash, assets=asset_rows)


@bp.route('/buy', methods=['GET', 'POST'])
@bp.route('/buy/<symbol>', methods=['GET', 'POST'])
@login_required
def buy(symbol=None):
    db = get_db()
    cash = db.execute('SELECT * FROM users WHERE id=?', (g.user['id'],)).fetchone()['cash']
    if request.method == 'POST':
        error = None
        if "symbol" in request.form.keys():
            symbol = request.form['symbol']

            if symbol == '':
                error = "Please enter a stock symbol"

            if error is None:
                return redirect(url_for('trading.buy', symbol=symbol))


        else:
            value = request.form['value']
            price = yf.Ticker(symbol).info["regularMarketPrice"]
            shares = float(value) / price
            if float(value) > cash:
                error = "Value of the stock exceeds account balance. Please try again."

            if error is None:
                db.execute('INSERT INTO ledger (user_id, symbol, shares, price, type) VALUES (?,?,?,?,?)',
                           (g.user['id'], symbol, shares, price, 'buy'))
                db.execute('UPDATE users SET cash=? WHERE id=?', (cash - float(value), g.user['id']))
                db.commit()
                try:
                    db.execute('INSERT INTO holding (user_id, symbol, shares) VALUES (?,?,?)',
                               (g.user['id'], symbol, shares))
                    db.commit()
                except db.IntegrityError:
                    db.execute('UPDATE holding SET shares=shares+? WHERE id=?', (shares, g.user['id']))
                    db.commit()
                return redirect(url_for('trading.portfolio'))

        flash(error)
    if symbol is None:
        info = None
    else:
        info = yf.Ticker(symbol).info

    return render_template('trading/buy.html', balance=cash, info=info)
