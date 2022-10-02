from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db
from .fixtures import get_fixture

bp = Blueprint('results', __name__, url_prefix="/results")


def get_results(limit=None):

    limit_query = ""

    if limit is not None:
        limit_query = f"LIMIT {limit}"

    db = get_db()
    query = db.execute(
        "SELECT r.id, result, fixture_date "
        " FROM results r"
        " JOIN fixtures f on r.fixture_id = f.id"
        f" {limit_query}",
        ()
    ).fetchall()

    return query


def get_result(id):
    db = get_db()
    query = db.execute(
        "SELECT r.id, result, fixture_date "
        " FROM results r"
        " JOIN fixtures f on r.fixture_id = f.id"
        " WHERE fixture_id = ?",
        (id,)
    ).fetchone()

    return query


@bp.route('/<int:id>/create/result', methods=['GET', 'POST'])
@login_required
def create_result(id):
    fixture = get_fixture(id)

    if request.method == 'POST':

        wildcat_legs = request.form['wildcat_legs']
        opposition_legs = request.form['opposition_legs']
        result = "W" if wildcat_legs > opposition_legs else "L"

        error = None

        if wildcat_legs is None or opposition_legs is None:
            error = "Result needs to be present"

        if get_result(id) is not None:
            error = "Result already exists"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO results (fixture_id, wildcat_legs, opposition_legs, result) '
                ' values (?, ?, ?, ?)',
                (id, wildcat_legs, opposition_legs, result)
            )
            db.commit()
            return redirect(url_for('fixtures.all_fixtures'))

    return render_template('results/result.html', fixture=fixture)


@bp.route('/<int:id>/update/result', methods=['GET', 'POST'])
@login_required
def update_result(id):
    fixture = get_fixture(id)

    if request.method == 'POST':
        wildcat_legs = request.form['wildcat_legs']
        opposition_legs = request.form['opposition_legs']
        result = "W" if wildcat_legs > opposition_legs else "L"

        error = None

        if wildcat_legs is None or opposition_legs is None:
            error = "Result needs to be present"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE results SET wildcat_legs = ?, opposition_legs = ?, result = ?'
                ' WHERE fixture_id = ?',
                (wildcat_legs, opposition_legs, result, id)
            )
            db.commit()
            return redirect(url_for('fixtures.all_results'))

    return render_template('results/result.html', fixture=fixture)


@bp.route('/<int:id>/results/delete', methods=['POST'])
@login_required
def delete_result(id):
    result = get_result(id)
    db = get_db()
    db.execute('DELETE FROM results WHERE id = ?', (result['id'],))
    db.commit()
    return redirect(url_for('index'))
