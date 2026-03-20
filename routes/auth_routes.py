from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from models.User import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        accept_rules = request.form.get("accept_rules")

        if username == "" or password == "":
            flash("Remplis tous les champs.")
        elif not accept_rules:
            flash("Tu dois accepter les règles de confidentialité.")
        else:
            user_created = User.create(username, password, current_app.config["DATABASE"])

            if user_created:
                flash("Compte créé. Tu peux te connecter.")
                return redirect(url_for("auth.login"))

            flash("Ce nom de code existe déjà.")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.login(username, password, current_app.config["DATABASE"])

        if user is None:
            flash("Identifiants incorrects.")
        else:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("chat.chat"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Tu es déconnecté.")
    return redirect(url_for("auth.login"))
