from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from app.forms import ProfileForm
from app.models.user import User
from app.utils import permission_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/")
@login_required
def index():
    return redirect(url_for("user.profile"))


@user_bp.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for("user.profile"))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
@permission_required("edit_own_profile")
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        new_username = form.username.data.strip()
        username_changed = new_username != (current_user.username or "")
        changing_password = bool(form.new_password.data)
        requires_current_password = username_changed or changing_password

        if requires_current_password and not form.current_password.data:
            flash("Current password is required to change username or password.", "danger")
            return render_template("user/profile.html", form=form)
        if requires_current_password and not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return render_template("user/profile.html", form=form)

        # Unique checks (excluding myself)
        if User.query.filter(User.username == new_username, User.id != current_user.id).first():
            flash("Username already taken.", "danger")
            return render_template("user/profile.html", form=form)

        current_user.username = new_username

        # Optional password change
        if changing_password:
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/profile.html", form=form)
