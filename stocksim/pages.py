from flask import Blueprint, render_template
from . import queries

bp = Blueprint('pages', __name__)


@bp.route('/')
def index():
    top = queries.get_top_stocks(5)
    return render_template('pages/index.html', top_stocks=top)
