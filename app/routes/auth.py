from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from app.models.user import User
from app.models.rbac import Role
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Enforce unique username/email
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("Username already taken.", "danger")
            return render_template("auth/register.html", form=form)
        if User.query.filter_by(email=form.email.data.strip().lower()).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register.html", form=form)
        user_role = Role.query.filter_by(name="user").first()

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role="user",
            role_id=(user_role.id if user_role else None),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created. You can log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        ident = form.username_or_email.data.strip()
        user = User.query.filter((User.username == ident) | (User.email == ident.lower())).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user)
        flash("Welcome back!", "success")

        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.home"))

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("main.home"))
