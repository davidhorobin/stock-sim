from flask import Flask, render_template

import queries

app = Flask(__name__)


@app.route("/")
def homepage():
    top = queries.get_top_stocks(5)
    return render_template("homepage.html", top_stocks=top)


def run():
    app.run(debug=True)
