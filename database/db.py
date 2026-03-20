import sqlite3


def get_connection(db_name="shadowcomm.db"):
    db = sqlite3.connect(db_name)
    db.row_factory = sqlite3.Row
    return db


def create_users_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL
        )
        """
    )


def update_old_users_table(cursor):
    columns = cursor.execute("PRAGMA table_info(users)").fetchall()
    column_names = []

    for column in columns:
        column_names.append(column["name"])

    if "code_name" in column_names and "username" not in column_names:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        cursor.execute("UPDATE users SET username = code_name WHERE username IS NULL")
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS index_users_username ON users(username)"
        )


def create_messages_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id)
        )
        """
    )


def update_old_messages_table(cursor):
    columns = cursor.execute("PRAGMA table_info(messages)").fetchall()
    column_names = []

    for column in columns:
        column_names.append(column["name"])

    if column_names != []:
        if "sender_id" not in column_names or "content" not in column_names:
            cursor.execute("DROP TABLE IF EXISTS messages")
            create_messages_table(cursor)


def init_db(db_name="shadowcomm.db"):
    db = get_connection(db_name)
    cursor = db.cursor()

    create_users_table(cursor)
    update_old_users_table(cursor)
    create_messages_table(cursor)
    update_old_messages_table(cursor)

    db.commit()
    db.close()