import os
import time

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass

    app.add_url_rule('/', endpoint='index')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import fixtures
    app.register_blueprint(fixtures.bp)

    from . import attendance
    app.register_blueprint(attendance.bp)

    from . import account
    app.register_blueprint(account.bp)

    from . import results
    app.register_blueprint(results.bp)

    app.jinja_env.globals.update(get_result=results.get_result)

    @app.template_filter('ctime')
    def timectime(s):
        return time.ctime(s)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
