import bcrypt
import sqlite3

from database.db import get_connection


class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def create(username, password, db_name="shadowcomm.db"):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        db = get_connection(db_name)
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            db.commit()
            db.close()
            return True
        except sqlite3.IntegrityError:
            db.close()
            return False

    @staticmethod
    def login(username, password, db_name="shadowcomm.db"):
        db = get_connection(db_name)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        db.close()

        if row is None:
            return None

        password_ok = bcrypt.checkpw(password.encode("utf-8"), row["password"])

        if password_ok:
            return User(row["id"], row["username"])

        return None

    @staticmethod
    def delete(user_id, db_name="shadowcomm.db"):
        db = get_connection(db_name)
        cursor = db.cursor()
        cursor.execute("DELETE FROM messages WHERE sender_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        db.close()