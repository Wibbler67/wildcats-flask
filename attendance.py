from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .fixtures import get_fixture

bp = Blueprint('attendance', __name__, url_prefix="/attendance")


def check_if_already_registered(user_id, fixture_id):
    db = get_db()
    already_registered = db.execute(
        'SELECT username, fixture_date, attending '
        ' FROM attendance a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id'
        ' WHERE u.id = ? and f.id = ? ',
        (user_id, fixture_id,)
    ).fetchone()

    return already_registered


@bp.route("/<int:id>/total_attendance", methods=["GET"])
@login_required
def get_fixture_attendance(id):
    fixture = get_fixture(id)

    attendees = get_db().execute(
        'SELECT username'
        ' FROM attendance a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id '
        ' WHERE f.id = ? and a.attending = 1 ',
        (id,)
    ).fetchall()

    count = get_db().execute(
        'SELECT count(*) as total '
        ' FROM attendance a'
        ' JOIN fixtures f ON f.id = a.fixture_id '
        ' WHERE f.id = ? and a.attending = 1 ',
        (id,)
    ).fetchall()

    if attendees is None:
        abort(404, f"Attendance for fixture id {id} doesn't exist.")

    return render_template("/attendance/attending.html", fixture=fixture, attendees=attendees, count=count)


@bp.route("/<int:id>/add_attendance", methods=["GET", "POST"])
@login_required
def create_confirm_attendance(id):
    fixture = get_fixture(id, False)

    if request.method == "POST":
        attendance = request.form['confirmation']

        error = None

        if attendance is None:
            error = "Attendance confirmation is required"

        if attendance == "yes":
            attendance = 1
        else:
            attendance = 0

        already_registered = check_if_already_registered(g.user['id'], fixture['id'])

        if already_registered is not None:
            error = "Attendance already confirmed"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO attendance (attendee_id, fixture_id, attending)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], fixture['id'], attendance)

            )
            db.commit()
        return redirect(url_for("account.home", id=g.user['id']))

    return render_template("attendance/edit.html", fixture=fixture)


@bp.route("/<int:id>/edit_attendance", methods=["POST", "GET"])
@login_required
def update_attendance(id):
    fixture = get_fixture(id, False)

    if request.method == "POST":
        attendance = request.form['confirmation']

        error = None

        if attendance is None:
            error = "Attendance confirmation is required"

        if attendance == "yes":
            attendance = 1
        else:
            attendance = 0

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE attendance SET attending = ?'
                ' WHERE id = ? and fixture_id = ?',
                (attendance, g.user['id'], fixture['id'])
            )
            db.commit()
        return redirect(url_for("account.home", id=g.user['id']))

    return render_template("attendance/edit.html", fixture=fixture)
