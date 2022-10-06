from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .fixtures import get_fixture

bp = Blueprint('availability', __name__, url_prefix="/availability")


def get_available(fixture_id):

    attendees = get_db().execute(
        'SELECT count(*) as total'
        ' FROM availabilities a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id '
        ' WHERE a.availability = 1 and f.id = ?'
        ' GROUP BY f.id',
        (fixture_id,)
    ).fetchall()

    return attendees


def get_availability(fixture_id):

    attendees = get_db().execute(
        'SELECT username, availability'
        ' FROM availabilities a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id '
        ' WHERE f.id = ? ',
        (fixture_id,)
    ).fetchall()

    return attendees


def check_if_already_registered(user_id, fixture_id):
    db = get_db()
    already_registered = db.execute(
        'SELECT username, fixture_date, availability '
        ' FROM availabilities a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id'
        ' WHERE u.id = ? and f.id = ? ',
        (user_id, fixture_id,)
    ).fetchone()

    return already_registered


@bp.route("/<int:id>/total_attendance", methods=["GET"])
@login_required
def get_fixture_availability(id):
    fixture = get_fixture(id)

    attendees = get_availability(id)

    count = get_db().execute(
        'SELECT count(*) as total '
        ' FROM availabilities a'
        ' JOIN fixtures f ON f.id = a.fixture_id '
        ' WHERE f.id = ? and a.availability = 1 ',
        (id,)
    ).fetchall()

    if attendees is None:
        abort(404, f"Attendance for fixture id {id} doesn't exist.")

    return render_template("/attendance/attending.html", fixture=fixture, attendees=attendees, count=count)


@bp.route("/<int:id>/add_availability", methods=["GET", "POST"])
@login_required
def create_availability(id):
    fixture = get_fixture(id, False)

    if request.method == "POST":
        attendance = request.form['confirmation']

        error = None

        if attendance is None:
            error = "Availability confirmation is required"

        if attendance == "yes":
            availability = 1
        else:
            availability = 0

        already_registered = check_if_already_registered(g.user['id'], fixture['id'])

        if already_registered is not None:
            error = "Attendance already confirmed"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO availabilities (attendee_id, fixture_id, availability)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], fixture['id'], availability)

            )
            db.commit()
        return redirect(url_for("fixtures.all_fixtures", id=g.user['id']))

    return render_template("attendance/edit.html", fixture=fixture)


@bp.route("/<int:id>/edit_availability", methods=["POST", "GET"])
@login_required
def update_availability(id):
    fixture = get_fixture(id, False)

    if request.method == "POST":
        attendance = request.form['confirmation']

        error = None

        if attendance is None:
            error = "Attendance confirmation is required"

        if attendance == "yes":
            availability = 1
        else:
            availability = 0

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE availabilities SET availability = ?'
                ' WHERE id = ? and fixture_id = ?',
                (availability, g.user['id'], fixture['id'])
            )
            db.commit()
        return redirect(url_for("account.account", id=g.user['id']))

    return render_template("attendance/edit.html", fixture=fixture)


@bp.route('/<int:fixture_id>/<int:user_id>/delete', methods=['POST'])
def delete_availability(user_id, fixture_id):
    db = get_db()

    db.execute(
        'DELETE FROM availabilities WHERE attendee_id = ? and fixture_id = ?',
        (user_id, fixture_id)
        )
    db.commit()

    return redirect(url_for("account.account_attendance", id=g.user['id']))