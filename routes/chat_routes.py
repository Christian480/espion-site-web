from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from models.Message import Message
from models.User import User


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        flash("Connecte-toi d'abord.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if content != "":
            Message.create(
                session["user_id"],
                content,
                current_app.config["DATABASE"],
                current_app.config["CAESAR_KEY"],
            )
            return redirect(url_for("chat.chat"))

        flash("Écris un message avant d'envoyer.")

    messages = Message.get_all(
        current_app.config["DATABASE"],
        current_app.config["CAESAR_KEY"],
    )
    return render_template("chat.html", messages=messages)


@chat_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    User.delete(session["user_id"], current_app.config["DATABASE"])
    session.clear()
    flash("Ton compte et tes messages ont été supprimés.")
    return redirect(url_for("main.home"))
