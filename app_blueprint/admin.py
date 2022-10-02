from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required, admin_login_required
from ..db import get_db
from .fixtures import get_fixture
from .attendance import get_attending

bp = Blueprint('admin', __name__, url_prefix="/admin")


@bp.route("/admin", methods=["GET"])
@admin_login_required
def admin_home():

    return render_template("admin/index.html")