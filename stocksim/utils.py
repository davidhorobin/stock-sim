from re import sub
from datetime import datetime, timezone


def strip_tags(s):
    return sub(r'<.*?>', '', s)


def calculate_profit(db, symbol, price, user_id):
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
        unrealised_profit_loss = (price - avg_cost) * running_shares

    return realised_profit_loss + unrealised_profit_loss, running_cost


def format_articles(articles):
    articles = articles[2:]
    for i in range(len(articles) // 3):
        title = strip_tags(articles.pop(0))
        link = strip_tags(articles.pop(0))
        article_time = datetime.strptime(strip_tags(articles.pop(0)), "%a, %d %b %Y %H:%M:%S %z")
        difference = (datetime.utcnow() - article_time.astimezone(timezone.utc).replace(tzinfo=None)).seconds // 60
        articles.append((title, link, difference))
    return articles
