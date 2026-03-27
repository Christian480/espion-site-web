from database.db import get_connection
from services.caesar_cipher import decrypt_message, encrypt_message


class Message:
    def __init__(self, message_id, username, content, timestamp):
        self.id = message_id
        self.username = username
        self.content = content
        self.timestamp = timestamp

    @staticmethod
    def create(sender_id, content, db_name="shadowcomm.db", key=3):
        encrypted_content = encrypt_message(content, key)
        db = get_connection(db_name)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO messages (sender_id, content) VALUES (?, ?)",
            (sender_id, encrypted_content)
        )
        db.commit()
        db.close()

    @staticmethod
    def get_all(db_name="shadowcomm.db", key=3):
        db = get_connection(db_name)
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT messages.id, users.code_name AS username, messages.content, messages.timestamp
            FROM messages
            JOIN users ON users.id = messages.sender_id
            ORDER BY messages.timestamp ASC, messages.id ASC
            """
        )
        rows = cursor.fetchall()
        db.close()
        return [
            {
                "id": row["id"],
                "username": row["username"],
                "content": decrypt_message(row["content"], key),
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]