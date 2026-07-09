from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import queries
import yfinance as yf

bp = Blueprint('pages', __name__)


@bp.route('/')
def index():
    top = queries.get_top_stocks(5)
    return render_template('pages/index.html', top_stocks=top)


@bp.route('/stockinfo/', methods=['GET', 'POST'])
@bp.route('/stockinfo/<symbol>', methods=['GET', 'POST'])
def stockinfo(symbol=None):
    if request.method == 'POST':
        symbol = request.form['symbol']
        error = None

        if symbol == '':
            error = "Please enter a stock symbol"

        if error is None:
            return redirect(url_for("pages.stockinfo", symbol=symbol))

        flash(error)
    if symbol is None:
        info = None
    else:
        info = yf.Ticker(symbol).info
        if len(info.keys()) <= 1 or info["quoteType"] != "EQUITY":
            flash("Invalid stock symbol")
            info = None
    return render_template('pages/stockinfo.html', info=info)
