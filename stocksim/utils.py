from re import sub
from .queries import get_stock


def strip_tags(s):
    return sub(r'<.*?>', '', s)


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
        unrealised_profit_loss = (get_stock(symbol)["regularMarketPrice"] - avg_cost) * running_shares

    return realised_profit_loss + unrealised_profit_loss, running_cost
