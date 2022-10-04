from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required, admin_login_required
from .db import get_db

bp = Blueprint('subs', __name__, url_prefix="/subs")


def get_total_subs():
    db = get_db()
    total = db.execute(
        'SELECT sum(amount_paid) as total'
        ' FROM subs '
    ).fetchone()

    return total


@bp.route("/view_subs", methods=["GET"])
@login_required
@admin_login_required
def view_subs():
    db = get_db()

    fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location, sum(amount_paid) as total'
        ' FROM fixtures f '
        ' JOIN subs s on f.id = s.fixture_id'
        ' GROUP BY f.id'
        ' ORDER BY f.id ASC'
    ).fetchall()

    total = get_total_subs()

    return render_template("subs/subs_index.html", fixtures=fixtures, total=total, main_title="Subs Overview")
