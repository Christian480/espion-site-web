from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

from database.db import get_connection

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    db = get_connection(current_app.config["DATABASE"])

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            user = db.execute(
                "SELECT id FROM users WHERE username = ?", (session["username"],)
            ).fetchone()
            if user:
                db.execute(
                    "INSERT INTO messages (sender_id, content) VALUES (?, ?)",
                    (user["id"], content),
                )
                db.commit()
        db.close()
        return redirect(url_for("chat.chat"))

    messages = db.execute(
        """SELECT messages.id, users.username, messages.content, messages.timestamp
           FROM messages
           JOIN users ON messages.sender_id = users.id
           ORDER BY messages.timestamp ASC"""
    ).fetchall()
    db.close()
    return render_template("centredecom.html", messages=messages)


@chat_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if "username" in session:
        db = get_connection(current_app.config["DATABASE"])
        user = db.execute(
            "SELECT id FROM users WHERE username = ?", (session["username"],)
        ).fetchone()
        if user:
            db.execute("DELETE FROM messages WHERE sender_id = ?", (user["id"],))
            db.execute("DELETE FROM users WHERE id = ?", (user["id"],))
            db.commit()
        db.close()
    session.clear()
    return redirect(url_for("main.home"))
