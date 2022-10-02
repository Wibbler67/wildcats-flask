from flask import (
    Blueprint, render_template
)

from .auth import admin_login_required
from .subs import get_total_subs
from .results import get_results
from.db import get_db

bp = Blueprint('admin', __name__, url_prefix="/admin")


def get_fixtures_and_attendance(limit=None):
    db = get_db()

    limit_query = ""

    if limit is not None:
        limit_query = f"LIMIT {limit}"

    fixtures = db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location, sum(attending) as total'
        ' FROM fixtures f '
        ' JOIN attendance a ON a.fixture_id = f.id '
        ' WHERE DATE() < fixture_date and attending = 1'
        ' GROUP BY f.id'
        f' {limit_query}',
        ()
    ).fetchall()

    if fixtures:
        ids = tuple(int(fixture['id']) for fixture in fixtures)
        not_query = f"NOT IN {ids}"
        if len(ids) <= 1:
            print(ids)
            not_query = f"!= {ids[0]}"
    else:
        not_query = "!= 0"

    fixtures += db.execute(
        'SELECT f.id, fixture_date, match_type, team, location'
        ' FROM fixtures f '
        f' WHERE DATE() < fixture_date and f.id {not_query}'
        ' GROUP BY f.id'
        f' {limit_query}',
        ()
    ).fetchall()

    print(fixtures)

    return fixtures[:limit]


@bp.route("/", methods=["GET"])
@admin_login_required
def admin_home():

    fixtures = get_fixtures_and_attendance(5)

    total_subs = get_total_subs()

    results = get_results(5)

    main_title = "Admin Home"

    return render_template("admin/index.html", fixtures=fixtures, total_subs=total_subs,
                           results=results, main_title=main_title)


@bp.route("/admin/<int:id>/user_attendance", methods=["GET", "POST"])
@admin_login_required
def register_user_attendance(id):

    return render_template("admin/admin_attendance.html")
