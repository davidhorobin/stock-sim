from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

def run():
    app.run(debug=True)