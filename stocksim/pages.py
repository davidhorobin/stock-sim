from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import queries
import yfinance as yf
from urllib.request import urlopen
import re
from datetime import *

bp = Blueprint('pages', __name__)


@bp.route('/')
def index():
    url = "https://seekingalpha.com/market_currents.xml"
    xml = urlopen(url).read().decode('utf-8')
    articles = re.findall(r"<title>.*</title>|<link>.*</link>|<pubDate>.*</pubDate>", xml)
    top_stories = []
    for i in range(5):
        article_time = datetime.strptime(strip_tags(articles[3 * i + 4]), "%a, %d %b %Y %H:%M:%S %z")
        difference = (datetime.utcnow() - article_time.astimezone(timezone.utc).replace(tzinfo=None)).seconds // 60
        top_stories += [
            (strip_tags(articles[3 * i + 2]), strip_tags(articles[3 * i + 3]), difference)]
    top_stocks = queries.get_top_stocks(5)
    return render_template('pages/index.html', top_stocks=top_stocks, articles=top_stories)


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
    return render_template('pages/stockinfo.html', symbol=symbol, info=info)


def strip_tags(s):
    return re.sub(r'<.*?>', '', s)
