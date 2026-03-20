from flask import Blueprint, render_template, request, redirect, url_for, session

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html")


@chat_bp.route("/delete_account", methods=["POST"])
def delete_account():
    session.clear()
    return redirect(url_for("main.home"))
