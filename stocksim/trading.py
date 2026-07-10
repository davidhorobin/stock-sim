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
    cash = db.execute('SELECT * FROM users WHERE id=?', (g.user["id"],)).fetchone()['cash']
    assets = db.execute('SELECT * FROM holding WHERE user_id=?', (g.user["id"],)).fetchall()
    asset_rows = []
    asset_total = 0
    profit_total = cash - 10000
    for asset in assets:
        tmp = {"symbol": asset["symbol"], "shares": asset["shares"]}
        price = yf.Ticker(tmp["symbol"]).info["regularMarketPrice"]
        tmp["price"] = price
        tmp["total"] = price * tmp["shares"]
        if tmp["total"] < 0.005:
            db.execute("DELETE FROM holding WHERE user_id=? AND symbol=?", (g.user["id"], asset["symbol"]))
            db.commit()
            continue
        profit_calculations = calculate_profit(db, tmp["symbol"], g.user["id"])
        tmp["profitloss"] = profit_calculations[0]
        tmp["avgcost"] = profit_calculations[1]
        profit_total += tmp["total"]
        asset_rows.append(tmp)
        asset_total += tmp["total"]
    return render_template('trading/portfolio.html', profit=profit_total, assettotal=asset_total, balance=cash,
                           assets=sorted(asset_rows, key=lambda x: x['total'], reverse=True))


def calculate_profit(db, symbol, user_id):
    running_shares = 0
    running_cost = 0
    realised_profit_loss = 0
    unrealised_profit_loss = 0

    transactions = db.execute('SELECT * FROM ledger WHERE symbol=? AND user_id=? ORDER BY created',
                              (symbol, user_id)).fetchall()
    for t in transactions:
        if t['type'] == "buy":
            running_shares += t['shares']
            running_cost += t['price'] * t['shares']
        else:
            avg_cost = running_cost / running_shares
            sell_price = t['shares'] * t['price']
            cost_basis = avg_cost * t['shares']
            running_shares -= t['shares']
            realised_profit_loss += sell_price - cost_basis
            running_cost -= cost_basis

    if running_shares > 0:
        avg_cost = running_cost / running_shares
        unrealised_profit_loss = (yf.Ticker(symbol).info["regularMarketPrice"] - avg_cost) * running_shares
    else:
        unrealised_profit_loss = 0

    return (realised_profit_loss + unrealised_profit_loss, running_cost)


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
                    db.execute('UPDATE holding SET shares=shares+? WHERE user_id=?', (shares, g.user['id']))
                    db.commit()
                return redirect(url_for('trading.portfolio'))

        flash(error)
    if symbol is None:
        info = None
    else:
        info = yf.Ticker(symbol).info

    return render_template('trading/buy.html', balance=cash, info=info)


@bp.route('/sell', methods=['GET', 'POST'])
@login_required
def sell(symbol=None):
    db = get_db()
    cash = db.execute('SELECT * FROM users WHERE id=?', (g.user['id'],)).fetchone()['cash']

    if request.method == 'POST':
        error = None
        symbol = request.form['symbol']
        sell_amount = float(request.form['sellamount'])
        price = yf.Ticker(symbol).info["regularMarketPrice"]
        shares = sell_amount / price
        db.execute("INSERT INTO ledger (user_id, symbol, shares, price, type) VALUES (?,?,?,?,?)",
                   (g.user['id'], symbol, shares, price, 'sell',))
        db.execute("UPDATE holding SET shares=shares-? WHERE user_id=? AND symbol=?", (shares, g.user['id'], symbol))
        db.execute(
            "UPDATE users SET cash=cash+? WHERE id=?", (sell_amount, g.user['id']))
        db.commit()
        return redirect(url_for('trading.portfolio'))

    assets = db.execute('SELECT * FROM holding WHERE user_id=?', (g.user["id"],)).fetchall()
    asset_rows = []
    for asset in assets:
        market_price = yf.Ticker(asset['symbol']).info["regularMarketPrice"]
        tmp = {"symbol": asset['symbol']}
        tmp['market_price'] = market_price
        tmp['value'] = asset['shares'] * market_price
        if tmp["value"] < 0.005:
            db.execute("DELETE FROM holding WHERE user_id=? AND symbol=?", (g.user["id"], asset["symbol"]))
            db.commit()
            continue
        tmp['purchase_price'] = (calculate_profit(db, tmp["symbol"], g.user["id"]))[1]
        tmp['avg_price'] = tmp['purchase_price'] / asset['shares']
        tmp['shares'] = asset['shares']
        asset_rows.append(tmp)

    return render_template('trading/sell.html', assets=asset_rows)
