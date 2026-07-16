from flask import Blueprint, render_template, request, flash, redirect, url_for

from .queries import get_top_stocks, get_stock, SymbolNotFoundError, get_top_articles
from .utils import format_articles

bp = Blueprint('pages', __name__)


@bp.route('/')
def index():
    top_stories = get_top_articles()
    top_stories = format_articles(top_stories)[:5]
    top_stocks = get_top_stocks(5)
    return render_template('pages/index.html', top_stocks=top_stocks, articles=top_stories)


@bp.route('/stockinfo/', methods=['GET', 'POST'])
@bp.route('/stockinfo/<symbol>', methods=['GET', 'POST'])
def stockinfo(symbol=None):
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()

        if symbol == '':
            flash('Please enter a stock symbol.')

        return redirect(url_for("pages.stockinfo", symbol=symbol))

    if symbol is None:
        info = None
    else:
        try:
            info = get_stock(symbol)
        except SymbolNotFoundError as e:
            flash(str(e))
            info = None
    return render_template('pages/stockinfo.html', symbol=symbol, info=info)
