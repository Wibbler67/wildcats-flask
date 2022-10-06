import operator
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g
)

from .auth import admin_login_required, login_required
from .subs import get_total_subs
from .results import get_results
from .availability import check_if_already_registered, get_availability, delete_availability
from .fixtures import get_fixture
from .db import get_db

bp = Blueprint('admin', __name__, url_prefix="/admin")


def get_user_id(username):
    db = get_db()

    user_row = db.execute(
        "SELECT id "
        " FROM user"
        " WHERE username == ?",
        (username,)
    ).fetchone()

    return user_row['id']


def get_all_subs(limit=None):
    db = get_db()

    limit_query = ""

    if limit is not None:
        limit_query = f"LIMIT {limit}"

    subs_of_fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location, sum(amount_paid) as total'
        ' FROM fixtures f '
        ' JOIN subs s on f.id = s.fixture_id'
        ' WHERE DATE() > fixture_date'
        ' GROUP BY f.id'
        ' ORDER BY fixture_date DESC'
        f' {limit_query}',
    ).fetchall()

    if subs_of_fixtures:
        ids = tuple(int(fixture['id']) for fixture in subs_of_fixtures)
        not_query = f"NOT IN {ids}"
        if len(ids) <= 1:
            not_query = f"!= {ids[0]}"
    else:
        not_query = "!= 0"

    subs_of_fixtures = db.execute(
        'SELECT f.id, fixture_date, match_type, team, location'
        ' FROM fixtures f '
        f' WHERE f.id {not_query} and DATE() > fixture_date'
        ' GROUP BY f.id'
        ' ORDER BY fixture_date DESC'
        f' {limit_query}',
    ).fetchall()

    subs_of_fixtures.sort(key=operator.itemgetter('fixture_date'))

    return subs_of_fixtures


def get_fixtures_and_attendance(limit=None):
    db = get_db()

    limit_query = ""

    if limit is not None:
        limit_query = f"LIMIT {limit}"

    fixtures = db.execute(
        'SELECT f.id, author_id, fixture_date, match_type, team, location, count(availability) as total'
        ' FROM fixtures f '
        ' JOIN availabilities a ON a.fixture_id = f.id '
        ' WHERE DATE() < fixture_date'
        ' GROUP BY f.id'
        f' {limit_query}',
        ()
    ).fetchall()

    if fixtures:
        ids = tuple(int(fixture['id']) for fixture in fixtures)
        not_query = f"NOT IN {ids}"
        if len(ids) <= 1:
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
    fixture = get_fixture(id)
    db = get_db()

    all_users = db.execute(
        "Select username "
        " FROM user"
    ).fetchall()

    user_availability = get_availability(id)

    if request.method == "POST":
        availability = request.form.getlist('availability[]')
        usernames = request.form.getlist('username[]')

        error = None

        if availability is None:
            error = "Attendance confirmation is required"

        attendees = [{"user": usernames[i], "availability": availability[i]} for i in range(len(availability))]

        for user in attendees:

            if user['availability'] == "1":
                user['availability'] = 1
            else:
                user['availability'] = 0

            user['id'] = get_user_id(user['user'])

            already_registered = check_if_already_registered(get_user_id(user['user']), fixture['id'])

            if already_registered is not None:
                error = f"Availability for user {user['user']} already confirmed"

        if error is not None:
            flash(error)
        else:
            for user in attendees:
                db = get_db()
                db.execute(
                    'INSERT INTO availabilities (attendee_id, fixture_id, availability)'
                    ' VALUES (?, ?, ?)',
                    (user['id'], fixture['id'], user['availability'])
                )
                db.commit()

            return redirect(url_for("admin.admin_home"))

    return render_template("admin/admin_attendance.html", all_users=all_users, fixture=fixture, user_availability=user_availability)


@bp.route("/subs/<int:id>/register", methods=["GET", "POST"])
@login_required
@admin_login_required
def add_player_subs(id):
    db = get_db()

    fixture = get_fixture(id)

    users_attending = get_availability(id)

    if request.method == "POST":
        username = request.form.getlist("username[]")
        subs_paid = request.form.getlist("subs_paid[]")
        user_subs = [{"user": username[i], "subs": subs_paid[i]} for i in range(len(username))]

        for user in user_subs:
            user['id'] = db.execute(
                'SELECT id FROM user where username = ?', (user['user'],)
            ).fetchone()['id']

        error = None

        if len(subs_paid) < 0:
            error = "Subs amount is required"

        if len(username) < 0:
            error = "A Username is required"

        if error is not None:
            flash(error)
        else:
            for user in user_subs:
                db = get_db()
                db.execute(
                    'INSERT INTO subs (attendee_id, fixture_id, amount_paid)'
                    ' VALUES (?, ?, ?)',
                    (user['id'], id, user['subs'])
                )
                db.commit()
        return redirect(url_for("admin.home", id=g.user['id']))

    return render_template("admin/admin-register-subs.html", users_attending=users_attending, fixture=fixture)


@bp.route("/userAttendance/delete")
@login_required
@admin_login_required
def remove_player_availability():
    username = request.args.get('username', None)
    fix_id = request.args.get('fix_id', None)

    user_id = get_user_id(username)

    delete_availability(user_id, fix_id)

    return redirect(url_for("admin.register_user_attendance", id=fix_id))
