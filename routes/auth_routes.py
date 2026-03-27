from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from database.db import get_niveaux, get_specialites
from models.User import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "" or password == "":
            flash("Remplis tous les champs.")
        else:
            user = User.login(username, password, current_app.config["DATABASE"])

            if user is None:
                flash("Identifiants incorrects.")
            else:
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("chat.chat"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    niveaux = get_niveaux(current_app.config["DATABASE"])
    specialites = get_specialites(current_app.config["DATABASE"])

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        accept_rules = request.form.get("accept_rules")
        nom = request.form.get("nom", "").strip()
        age_raw = request.form.get("age", "").strip()
        lieu_affectation = request.form.get("lieu_affectation", "").strip()

        try:
            niveau_id = int(request.form.get("niveau_id", 1))
            specialite_id = int(request.form.get("specialite_id", 1))
        except ValueError:
            flash("Choisis un niveau et une spécialité valides.")
            return render_template(
                "register.html",
                niveaux=niveaux,
                specialites=specialites,
            )

        if username == "" or password == "":
            flash("Remplis tous les champs obligatoires.")
        elif not accept_rules:
            flash("Tu dois accepter les règles de confidentialité.")
        elif age_raw and not age_raw.isdigit():
            flash("L'âge doit être un nombre.")
        else:
            user_created = User.create(
                username,
                password,
                current_app.config["DATABASE"],
                niveau_id=niveau_id,
                specialite_id=specialite_id,
                nom=nom,
                age=int(age_raw) if age_raw else None,
                lieu_affectation=lieu_affectation,
            )

            if user_created:
                flash("Compte créé. Tu peux te connecter.")
                return redirect(url_for("auth.login"))

            flash("Ce nom de code existe déjà.")

    return render_template("register.html", niveaux=niveaux, specialites=specialites)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Tu es déconnecté.")
    return redirect(url_for("main.home"))