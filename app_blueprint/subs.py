from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required, admin_login_required
from ..db import get_db
from .attendance import get_attending

bp = Blueprint('subs', __name__, url_prefix="/subs")


@bp.route("/<int:id>/register", methods=["GET", "POST"])
@login_required
@admin_login_required
def add_player_subs(id):
    db = get_db()

    users_attending = get_attending(id)

    if request.method == "POST":
        subs_paid = request.form["subs_paid"]
        username = request.form["username"]

        print(username)

        user = db.execute(
            'SELECT id FROM user where username = ?', (username,)
        ).fetchone()

        error = None

        if subs_paid is None:
            error = "Subs amount is required"

        if username is None:
            error = "A Username is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO subs (attendee_id, fixture_id, amount_paid)'
                ' VALUES (?, ?, ?)',
                (user['id'], id, subs_paid)
            )
            db.commit()
        return redirect(url_for("account.account", id=g.user['id']))

    return render_template("subs/admin-register-subs.html", users_attending=users_attending)


@bp.route("/view_subs", methods=["GET"])
@admin_login_required
def view_subs():
    db = get_db()

    fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location, sum(amount_paid) as total'
        ' FROM fixtures f '
        ' JOIN subs s on f.id = s.fixture_id'
        ' GROUP BY fixture_date'
        ' ORDER BY fixture_date ASC'
    ).fetchall()

    total = db.execute(
        'SELECT sum(amount_paid) as total'
        ' FROM subs '
    ).fetchone()

    return render_template("subs/subs_index.html", fixtures=fixtures, total=total)
