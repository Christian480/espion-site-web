from flask import Blueprint, render_template, current_app

from database.db import get_connection

main_bp = Blueprint("main", __name__)


def _get_database_name():
    return current_app.config["DATABASE"]


def _get_agents_list():
    db = get_connection(_get_database_name())

    try:
        return db.execute(
            """
            SELECT
                users.id,
                users.code_name AS username,
                COALESCE(niveau.nom, '?') AS niveau,
                COALESCE(NULLIF(specialite.nom, ''), specialite.specialite, 'Non définie') AS specialite
            FROM users
            LEFT JOIN niveau ON users.niveau_id = niveau.id
            LEFT JOIN specialite ON users.specialite_id = specialite.id
            WHERE users.code_name IS NOT NULL AND users.code_name != ''
            ORDER BY users.id
            """
        ).fetchall()
    finally:
        db.close()


@main_bp.route("/")
def home():
    return render_template("interface.html")


@main_bp.route("/classification")
def classification():
    return render_template("niveauclass.html")


@main_bp.route("/agents")
def agents():
    agents_list = _get_agents_list()
    return render_template("listeagents.html", agents=agents_list)
