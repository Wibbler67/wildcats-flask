from flask import (
    Blueprint, render_template
)

from .db import get_db

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    main_header = "Welcome Wildcats"
    return render_template('index.html', posts=posts, main_header=main_header)