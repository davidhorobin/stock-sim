import os

from flask import Flask
from .extensions import cache


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'stocksim.sqlite'),
        CACHE_TYPE='SimpleCache',
        CACHE_DEFAULT_TIMEOUT=120,
    )
    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    cache.init_app(app)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import pages
    app.register_blueprint(pages.bp)

    from . import trading
    app.register_blueprint(trading.bp)

    return app
