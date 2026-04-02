from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from database.db import get_niveaux, get_specialites
from models.User import User

auth_bp = Blueprint("auth", __name__)


def _get_database_name():
    return current_app.config["DATABASE"]


def _get_register_options():
    db_name = _get_database_name()
    niveaux = get_niveaux(db_name)
    specialites = get_specialites(db_name)
    return niveaux, specialites


def _render_register_page(niveaux, specialites):
    return render_template("register.html", niveaux=niveaux, specialites=specialites)


def _save_user_in_session(user):
    session["user_id"] = user.id
    session["username"] = user.username


def _get_register_form_data():
    return {
        "username": request.form.get("username", "").strip(),
        "password": request.form.get("password", ""),
        "accept_rules": request.form.get("accept_rules"),
        "nom": request.form.get("nom", "").strip(),
        "age_raw": request.form.get("age", "").strip(),
        "lieu_affectation": request.form.get("lieu_affectation", "").strip(),
    }


def _read_register_ids():
    niveau_id = int(request.form.get("niveau_id", 1))
    specialite_id = int(request.form.get("specialite_id", 1))
    return niveau_id, specialite_id


def _register_form_has_error(form_data):
    if form_data["username"] == "" or form_data["password"] == "":
        flash("Remplis tous les champs obligatoires.")
        return True

    if not form_data["accept_rules"]:
        flash("Tu dois accepter les règles de confidentialité.")
        return True

    if form_data["age_raw"] and not form_data["age_raw"].isdigit():
        flash("L'âge doit être un nombre.")
        return True

    return False


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "" or password == "":
            flash("Remplis tous les champs.")
        else:
            user = User.login(username, password, _get_database_name())

            if user is None:
                flash("Identifiants incorrects.")
            else:
                _save_user_in_session(user)
                return redirect(url_for("chat.chat"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    niveaux, specialites = _get_register_options()

    if request.method == "POST":
        form_data = _get_register_form_data()

        try:
            niveau_id, specialite_id = _read_register_ids()
        except ValueError:
            flash("Choisis un niveau et une spécialité valides.")
            return _render_register_page(niveaux, specialites)

        if not _register_form_has_error(form_data):
            user_created = User.create(
                form_data["username"],
                form_data["password"],
                _get_database_name(),
                niveau_id=niveau_id,
                specialite_id=specialite_id,
                nom=form_data["nom"],
                age=int(form_data["age_raw"]) if form_data["age_raw"] else None,
                lieu_affectation=form_data["lieu_affectation"],
            )

            if user_created:
                flash("Compte créé. Tu peux te connecter.")
                return redirect(url_for("auth.login"))

            flash("Ce nom de code existe déjà.")

    return _render_register_page(niveaux, specialites)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Tu es déconnecté.")
    return redirect(url_for("main.home"))