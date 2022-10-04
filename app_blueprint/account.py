from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required, check_password_hash, generate_password_hash
from .db import get_db
from datetime import datetime

bp = Blueprint('account', __name__, url_prefix="/account")


@bp.route("<int:id>/", methods=["GET"])
@login_required
def account(id):

    if id != g.user['id']:
        abort(403)

    fixture_attendance = get_db().execute(
        "SELECT username, fixture_date, fixture_id, availability, match_type"
        ' FROM availabilities a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id '
        " WHERE u.id = ? and fixture_date > DATE()"
        " ORDER BY fixture_date asc",
        (id,)
    ).fetchall()
    current_date = datetime.date(datetime.now())

    return render_template("account/account.html", id=id, fixture_attendance=fixture_attendance, current_date=current_date)


@bp.route("<int:id>/attendance", methods=["GET"])
@login_required
def account_attendance(id):

    if id != g.user['id']:
        abort(403)

    fixture_attendance = get_db().execute(
        "SELECT username, fixture_date, fixture_id, availability, match_type"
        ' FROM availabilities a'
        ' JOIN user u ON u.id = a.attendee_id '
        ' JOIN fixtures f ON f.id = a.fixture_id '
        " WHERE u.id = ?"
        " ORDER BY fixture_date asc",
        (id,)
    ).fetchall()
    current_date = datetime.date(datetime.now())

    return render_template("account/account-attendance.html",
                           id=id, fixture_attendance=fixture_attendance, current_date=current_date)


@bp.route("<int:id>/edit_account", methods=["GET", "POST"])
@login_required
def edit_account(id):

    if id != g.user['id']:
        abort(403)

    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        db = get_db()

        error = None

        if error is None:
            try:
                db.execute(
                    "UPDATE user SET username = ?"
                    " WHERE id = ?",
                    (username, id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("account.get", id=g.user['id']))
        flash(error)

    return render_template("account/account.html", id=id)


@bp.route("<int:id>/change_password", methods=["GET", "POST"])
@login_required
def change_password(id):

    if id != g.user['id']:
        abort(403)

    if request.method == "POST":
        password = request.form['password']
        new_password = request.form['new_password']
        re_enter_new_password = request.form['re_enter_new_password']
        db = get_db()

        error = None

        user = get_db().execute(
            'SELECT * FROM user where id = ?', (id,)
        ).fetchone()

        if user is None:
            error = "Incorrect id."
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."

        if error is not None:
            flash(error)

        if new_password != re_enter_new_password:
            error = "Passwords don't match"

        if error is None:
            try:
                db.execute(
                    "UPDATE user SET password = ?"
                    " WHERE id = ?",
                    (generate_password_hash(new_password), id)
                )
                db.commit()
            except db.IntegrityError:
                error = "An error has occured"
            else:
                flash("Password changed successfully")
                return redirect(url_for("account.account", id=g.user['id']))

        flash(error)

    return render_template("account/edit_password.html", id=id)