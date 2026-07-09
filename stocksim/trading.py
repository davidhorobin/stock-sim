from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from stocksim.auth import login_required
from stocksim.db import get_db

bp = Blueprint('trading', __name__)


@bp.route('/portfolio')
@login_required
def portfolio():
    return render_template('trading/portfolio.html')
