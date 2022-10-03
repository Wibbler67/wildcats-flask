from flask import (
    Blueprint, render_template
)

from .auth import admin_login_required
from .subs import get_total_subs
from .results import get_results
from.db import get_db
import operator

bp = Blueprint('admin', __name__, url_prefix="/admin")


def get_all_subs(limit=None):
    db = get_db()

    limit_query = ""

    if limit is not None:
        limit_query = f"LIMIT {limit}"

    subs_of_fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location, sum(amount_paid) as total'
        ' FROM fixtures f '
        ' JOIN subs s on f.id = s.fixture_id'
        ' GROUP BY f.id'
        ' ORDER BY fixture_date ASC'
        f' {limit_query}',
    ).fetchall()

    if subs_of_fixtures:
        ids = tuple(int(fixture['id']) for fixture in subs_of_fixtures)
        not_query = f"NOT IN {ids}"
        if len(ids) <= 1:
            print(ids)
            not_query = f"!= {ids[0]}"
    else:
        not_query = "!= 0"

    subs_of_fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location'
        ' FROM fixtures f '
        f' WHERE f.id {not_query}'
        ' GROUP BY f.id'
        ' ORDER BY fixture_date ASC'
        f' {limit_query}',
    ).fetchall()

    return subs_of_fixtures


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

    fixtures.sort(key=operator.itemgetter('fixture_date'))

    return fixtures[:limit]


@bp.route("/", methods=["GET"])
@admin_login_required
def admin_home():

    fixtures = get_fixtures_and_attendance(5)

    all_subs = get_all_subs(5)
    total_subs = get_total_subs()

    results = get_results(5)

    main_title = "Admin Home"

    return render_template("admin/index.html", fixtures=fixtures, total_subs=total_subs,
                           all_subs=all_subs, results=results, main_title=main_title)


@bp.route("/admin/<int:id>/user_attendance", methods=["GET", "POST"])
@admin_login_required
def register_user_attendance(id):

    return render_template("admin/admin_attendance.html")
