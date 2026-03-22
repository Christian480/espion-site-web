from flask import Blueprint, render_template, current_app

from database.db import get_connection

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("interface.html")


@main_bp.route("/agents")
def agents():
    db = get_connection(current_app.config["DATABASE"])
    agents_list = db.execute("SELECT id, username FROM users ORDER BY id").fetchall()
    db.close()
    return render_template("listeagents.html", agents=agents_list)

