import sqlite3

import click
from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
import os


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def seed_db():
    db = get_db()

    admin_account = ["admin@example.com", "admin", generate_password_hash("password")]
    db.execute("INSERT INTO user (email, username, password) VALUES (?, ?, ?)", admin_account)
    db.commit()

    admin_id = db.execute(
        "SELECT id from USER where username = 'admin'"
    ).fetchone()

    lst = []

    try:
        with open(f"{os.path.abspath(os.getcwd())}/Fixture/fixture_list.csv") as csv:
            for line in csv:
                lst.append(line.strip("\n").split(","))
    except FileNotFoundError:
        with open(f"{os.path.abspath(os.getcwd())}/Flaskr/Fixture/fixture_list_seed.csv") as csv:
            for line in csv:
                lst.append(line.strip("\n").split(","))

    for fixtures in lst:
        fixtures.append(admin_id['id'])

    db.executemany("INSERT INTO fixtures (fixture_date, fixture_day, match_type, location, team, author_id)"
                   " VALUES (?, ?, ?, ?, ?, ?)", lst[1:])
    db.commit()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    seed_db()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
