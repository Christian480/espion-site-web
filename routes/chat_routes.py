from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

from models.Message import Message
from models.User import User
from services.caesar_cipher import decrypt_message

chat_bp = Blueprint("chat", __name__)


def _user_is_logged_in():
    return "user_id" in session


def _get_database_name():
    return current_app.config["DATABASE"]


def _get_caesar_key():
    return current_app.config["CAESAR_KEY"]


def _save_message():
    content = request.form.get("content", "").strip()

    if content:
        Message.create(
            session["user_id"],
            content,
            _get_database_name(),
            _get_caesar_key(),
        )


def _get_messages():
    return Message.get_all(_get_database_name(), _get_caesar_key())


def _render_chat_page(decrypted_text=None, encrypted_input="", revealed_message_id=None):
    messages = _get_messages()
    return render_template(
        "centredecom.html",
        messages=messages,
        decrypted_text=decrypted_text,
        encrypted_input=encrypted_input,
        revealed_message_id=revealed_message_id,
    )


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if not _user_is_logged_in():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        _save_message()
        return redirect(url_for("chat.chat"))

    return _render_chat_page()


@chat_bp.route("/chat/decrypt", methods=["POST"])
def decrypt_transmission():
    if not _user_is_logged_in():
        return redirect(url_for("auth.login"))

    encrypted_input = request.form.get("encrypted_content", "").strip()
    decrypted_text = decrypt_message(encrypted_input, _get_caesar_key())

    return _render_chat_page(
        decrypted_text=decrypted_text,
        encrypted_input=encrypted_input,
    )


@chat_bp.route("/chat/messages/<int:message_id>/decrypt", methods=["POST"])
def decrypt_chat_message(message_id):
    if not _user_is_logged_in():
        return redirect(url_for("auth.login"))

    return _render_chat_page(revealed_message_id=message_id)


@chat_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if _user_is_logged_in():
        User.delete(session["user_id"], _get_database_name())

    session.clear()
    return redirect(url_for("main.home"))