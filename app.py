import os

from flask import Flask


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

    from app_blueprint import db
    db.init_app(app)

    from app_blueprint import auth
    app.register_blueprint(auth.bp)

    from app_blueprint import fixtures
    app.register_blueprint(fixtures.bp)

    from app_blueprint import availability
    app.register_blueprint(availability.bp)

    from app_blueprint import account
    app.register_blueprint(account.bp)

    from app_blueprint import results
    app.register_blueprint(results.bp)

    from app_blueprint import posts
    app.register_blueprint(posts.bp)

    from app_blueprint import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from app_blueprint import subs
    app.register_blueprint(subs.bp)

    from app_blueprint import admin
    app.register_blueprint(admin.bp)

    app.jinja_env.globals.update(get_result=results.get_result)

    return app


create_app()
