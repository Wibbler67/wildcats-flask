from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db
from .fixtures import get_fixture

bp = Blueprint('subs', __name__, url_prefix="/subs")


@bp.route("/<int:id>/register", methods=["GET", "POST"])
@login_required
def register_subs(id):
    fixture = get_fixture(id)

    if request.method == "POST":
        subs_paid = request.form["subs_paid"]

        error = None

        if subs_paid is None:
            error = "Attendance confirmation is required"

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

    return render_template("attendance/subs.html", fixture=fixture)
