from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

from models.Message import Message
from models.User import User

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            Message.create(
                session["user_id"],
                content,
                current_app.config["DATABASE"],
                current_app.config["CAESAR_KEY"],
            )
        return redirect(url_for("chat.chat"))

    messages = Message.get_all(
        current_app.config["DATABASE"],
        current_app.config["CAESAR_KEY"],
    )
    return render_template("centredecom.html", messages=messages)


@chat_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" in session:
        User.delete(session["user_id"], current_app.config["DATABASE"])
    session.clear()
    return redirect(url_for("main.home"))