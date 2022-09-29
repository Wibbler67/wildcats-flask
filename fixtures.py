from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from .auth import login_required
from .db import get_db

bp = Blueprint('fixtures', __name__)


@bp.route("/upcoming_fixtures")
def upcoming_fixtures():
    db = get_db()
    fixtures = db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location '
        ' FROM fixtures f JOIN user u on f.author_id = u.id '
        ' WHERE fixture_date > DATE() ORDER BY fixture_date ASC'
        ' LIMIT 5'
    ).fetchall()

    current_date = datetime.date(datetime.now())
    main_title = "Next 5 Fixtures"
    return render_template('fixtures/fixtures.html', fixtures=fixtures, current_date=current_date, main_title=main_title)


@bp.route("/all_fixtures")
def all_fixtures():
    db = get_db()

    fixtures = db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location, result'
        ' FROM fixtures f JOIN user u on f.author_id = u.id'
        ' JOIN results r on f.id = r.fixture_id'
        ' WHERE DATE() > fixture_date ORDER BY fixture_date ASC'
    ).fetchall()
    last_id = fixtures[-1]['id']

    fixtures += db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location'
        ' FROM fixtures f JOIN user u on f.author_id = u.id'
        ' WHERE f.id > ?'
        ' ORDER BY fixture_date ASC',
        (last_id,)
    ).fetchall()

    current_date = datetime.date(datetime.now())
    main_title = "All Fixtures"
    return render_template('fixtures/fixtures.html', fixtures=fixtures, current_date=current_date, main_title=main_title)


@bp.route("/all_results")
def all_results():
    db = get_db()
    fixtures = db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location, result'
        ' FROM fixtures f JOIN user u on f.author_id = u.id'
        ' JOIN results r on f.id = r.fixture_id'
        ' WHERE DATE() > fixture_date ORDER BY fixture_date ASC'
    ).fetchall()

    current_date = datetime.date(datetime.now())
    main_title = "All Results"
    return render_template('fixtures/fixtures.html', fixtures=fixtures, current_date=current_date, main_title=main_title)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        fixture_date = request.form['fixture_date']
        match_type = request.form['match_type']
        team = request.form['team']
        day = datetime.strptime(fixture_date, "%Y-%M-%d").strftime("%A")
        location = request.form['location']

        error = None

        if not team:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO fixtures (author_id, fixture_date, fixture_day, match_type, team, location)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (g.user['id'], fixture_date, day, match_type, team, location)
            )
            db.commit()
            return redirect(url_for('fixtures.fixtures'))

    return render_template('fixtures/create/fixture.html')


def get_fixture(id, check_author=True):
    fixture = get_db().execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location'
        ' FROM fixtures f JOIN user u ON f.author_id = u.id'
        ' WHERE f.id = ?',
        (id,)
    ).fetchone()

    if fixture is None:
        abort(404, f"Fixture id {id} doesn't exist.")

    if check_author and fixture['author_id'] != g.user['id']:
        abort(403)

    return fixture


@bp.route('/<int:id>/update/fixture', methods=['GET', 'POST'])
@login_required
def update_fixture(id):
    fixture = get_fixture(id)

    if request.method == 'POST':
        fixture_date = request.form['fixture_date']
        match_type = request.form['match_type']
        team = request.form['team']
        location = request.form['location']
        result = request.form['result']
        error = None

        if not fixture_date:
            error = 'Date of fixture is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE fixtures SET fixture_date = ?, match_type = ?, team = ?, location = ?'
                ' WHERE id = ?',
                (fixture_date, match_type, team, location, id)
            )
            db.commit()
            return redirect(url_for('fixtures.fixtures'))

    return render_template('fixtures/update/fixture.html', fixture=fixture)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_fixture(id)
    db = get_db()
    db.execute('DELETE FROM fixtures WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('fixtures.fixtures'))

