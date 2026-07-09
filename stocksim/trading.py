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
