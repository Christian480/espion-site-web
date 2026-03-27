import bcrypt
import sqlite3

from database.db import get_connection, get_table_columns


class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def create(
        username,
        password,
        db_name="shadowcomm.db",
        niveau_id=1,
        specialite_id=1,
        nom="",
        age=None,
        lieu_affectation="",
    ):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        db = get_connection(db_name)
        cursor = db.cursor()
        user_columns = get_table_columns(db_name, "users")

        try:
            columns = ["code_name", "niveau_id", "specialite_id", "password"]
            values = [username, niveau_id, specialite_id, hashed_password]

            if "username" in user_columns:
                columns.insert(0, "username")
                values.insert(0, username)
            if "nom" in user_columns:
                columns.append("nom")
                values.append(nom.strip() or None)
            if "age" in user_columns:
                columns.append("age")
                values.append(age)
            if "lieu_affectation" in user_columns:
                columns.append("lieu_affectation")
                values.append(lieu_affectation.strip() or None)
            elif "Lieu_affectation" in user_columns:
                columns.append("Lieu_affectation")
                values.append(lieu_affectation.strip() or None)

            placeholders = ", ".join("?" for _ in columns)
            cursor.execute(
                f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})",
                tuple(values),
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
        user_columns = get_table_columns(db_name, "users")

        if "username" in user_columns:
            cursor.execute(
                """
                SELECT id, COALESCE(NULLIF(code_name, ''), username) AS code_name, password
                FROM users
                WHERE code_name = ? OR username = ?
                LIMIT 1
                """,
                (username, username),
            )
        else:
            cursor.execute("SELECT id, code_name, password FROM users WHERE code_name = ?", (username,))
        row = cursor.fetchone()
        db.close()

        if row is None:
            return None

        password_ok = bcrypt.checkpw(password.encode("utf-8"), row["password"])

        if password_ok:
            return User(row["id"], row["code_name"])

        return None

    @staticmethod
    def delete(user_id, db_name="shadowcomm.db"):
        db = get_connection(db_name)
        cursor = db.cursor()
        cursor.execute("DELETE FROM messages WHERE sender_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        db.close()