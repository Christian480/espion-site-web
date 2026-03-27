import sqlite3

import bcrypt 


DEFAULT_USERS = [
    ("agent007", 1, 4, "agent007@2026", "James Bond", 30, "Londres"),
    ("agentX", 2, 1, "motdepasse123", "Agent X", 25, "New York"),
    ("ghost", 3, 2, "secret456", "The Ghost", 35, "Tokyo"),
    ("shadow", 2, 3, "shadow@2026", "Shadow", 28, "Paris"),
    ("viper", 1, 2, "viperSecure", "Viper", 32, "Berlin"),
    ("falcon", 1, 1, "falcon123", "Falcon", 27, "Rome"),
    ("neo", 3, 4, "matrixNeo", "Neo", 29, "Zion"),
    ("hunter", 2, 2, "hunt3r!", "Hunter", 31, "Los Angeles"),
    ("zeus", 3, 3, "thunderBolt", "Zeus", 33, "Olympus"),
    ("phantom", 2, 1, "phantomX", "Phantom", 26, "London"),
]


def get_connection(db_name="shadowcomm.db"):
    db = sqlite3.connect(db_name)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def _table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _get_columns(cursor, table_name):
    if not _table_exists(cursor, table_name):
        return set()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def get_table_columns(db_name, table_name):
    db = get_connection(db_name)
    columns = _get_columns(db.cursor(), table_name)
    db.close()
    return columns


def _ensure_specialite_table(cursor):
    if not _table_exists(cursor, "specialite"):
        cursor.execute(
            """
            CREATE TABLE specialite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                specialite TEXT
            )
            """
        )
    else:
        columns = _get_columns(cursor, "specialite")
        if "nom" not in columns:
            cursor.execute("ALTER TABLE specialite ADD COLUMN nom TEXT")
        if "specialite" not in columns:
            cursor.execute("ALTER TABLE specialite ADD COLUMN specialite TEXT")

    cursor.execute("UPDATE specialite SET nom = COALESCE(NULLIF(nom, ''), specialite)")
    cursor.execute("UPDATE specialite SET specialite = COALESCE(NULLIF(specialite, ''), nom)")


def _ensure_users_table(cursor):
    if not _table_exists(cursor, "users"):
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_name TEXT NOT NULL UNIQUE,
                niveau_id INTEGER NOT NULL DEFAULT 1,
                specialite_id INTEGER NOT NULL DEFAULT 1,
                password BLOB NOT NULL,
                nom TEXT,
                age INTEGER,
                lieu_affectation TEXT,
                FOREIGN KEY (niveau_id) REFERENCES niveau(id),
                FOREIGN KEY (specialite_id) REFERENCES specialite(id)
            )
            """
        )
        return

    columns = _get_columns(cursor, "users")
    if "code_name" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN code_name TEXT")
    if "niveau_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN niveau_id INTEGER NOT NULL DEFAULT 1")
    if "specialite_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN specialite_id INTEGER NOT NULL DEFAULT 1")
    if "nom" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN nom TEXT")
    if "age" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER")
    if "lieu_affectation" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN lieu_affectation TEXT")

    refreshed_columns = _get_columns(cursor, "users")
    if "Lieu_affectation" in refreshed_columns:
        cursor.execute(
            """
            UPDATE users
            SET lieu_affectation = COALESCE(NULLIF(lieu_affectation, ''), Lieu_affectation)
            WHERE Lieu_affectation IS NOT NULL
            """
        )

    if "username" in refreshed_columns:
        rows = cursor.execute("SELECT id, username, code_name FROM users").fetchall()
    else:
        rows = cursor.execute("SELECT id, code_name FROM users").fetchall()

    for row in rows:
        current_code_name = row["code_name"] if "code_name" in row.keys() else None
        if current_code_name is not None and str(current_code_name).strip() != "":
            continue

        fallback = None
        if "username" in row.keys():
            username = row["username"]
            if username is not None and str(username).strip() != "":
                fallback = str(username).strip()

        if fallback is None:
            fallback = f"agent_{row['id']}"

        cursor.execute("UPDATE users SET code_name = ? WHERE id = ?", (fallback, row["id"]))

    cursor.execute("UPDATE users SET niveau_id = COALESCE(niveau_id, 1)")
    cursor.execute("UPDATE users SET specialite_id = COALESCE(specialite_id, 1)")
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_code_name ON users(code_name)"
    )


def _ensure_messages_table(cursor):
    legacy_message_exists = _table_exists(cursor, "message")

    if not _table_exists(cursor, "messages"):
        cursor.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER,
                content TEXT NOT NULL,
                status INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
            """
        )
    else:
        columns = _get_columns(cursor, "messages")
        if "receiver_id" not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN receiver_id INTEGER")
        if "status" not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN status INTEGER")
        if "timestamp" not in columns:
            cursor.execute(
                "ALTER TABLE messages ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
            )

    if legacy_message_exists:
        legacy_columns = _get_columns(cursor, "message")
        receiver_sql = "receiver_id" if "receiver_id" in legacy_columns else "NULL"
        status_sql = "status" if "status" in legacy_columns else "NULL"
        timestamp_sql = "timestamp" if "timestamp" in legacy_columns else "CURRENT_TIMESTAMP"
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO messages (id, sender_id, receiver_id, content, status, timestamp)
            SELECT id, sender_id, {receiver_sql}, content, {status_sql}, {timestamp_sql}
            FROM message
            """
        )
        cursor.execute("DROP TABLE IF EXISTS message")


def init_db(db_name="shadowcomm.db"):
    db = get_connection(db_name)
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS niveau (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL
        )
        """
    )
    _ensure_specialite_table(cursor)
    _ensure_users_table(cursor)
    _ensure_messages_table(cursor)

    cursor.execute("INSERT OR IGNORE INTO niveau (id, nom) VALUES (1, 'S'), (2, 'A'), (3, 'C')")
    cursor.execute(
        """
        INSERT OR IGNORE INTO specialite (id, nom, specialite) VALUES
        (1, 'agent-double', 'agent-double'),
        (2, 'agent-infiltré', 'agent-infiltré'),
        (3, 'agent-informateur', 'agent-informateur'),
        (4, 'cyber-espion', 'cyber-espion')
        """
    )

    db.commit()
    db.close()


def create_user(
    code_name,
    niveau_id,
    specialite_id,
    password,
    nom="",
    age=None,
    lieu_affectation="",
    db_name="shadowcomm.db",
):
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    db = get_connection(db_name)
    cursor = db.cursor()
    columns = get_table_columns(db_name, "users")

    cursor.execute("SELECT id FROM users WHERE code_name = ?", (code_name,))
    if cursor.fetchone():
        db.close()
        return False

    insert_columns = ["code_name", "niveau_id", "specialite_id", "password"]
    values = [code_name, niveau_id, specialite_id, hashed_password]

    if "username" in columns:
        insert_columns.insert(0, "username")
        values.insert(0, code_name)
    if "nom" in columns:
        insert_columns.append("nom")
        values.append(nom or None)
    if "age" in columns:
        insert_columns.append("age")
        values.append(age)
    if "lieu_affectation" in columns:
        insert_columns.append("lieu_affectation")
        values.append(lieu_affectation or None)

    placeholders = ", ".join("?" for _ in insert_columns)
    cursor.execute(
        f"INSERT INTO users ({', '.join(insert_columns)}) VALUES ({placeholders})",
        tuple(values),
    )
    db.commit()
    db.close()
    return True


def seed_default_users(db_name="shadowcomm.db"):
    for user in DEFAULT_USERS:
        create_user(*user, db_name=db_name)


def get_niveaux(db_name="shadowcomm.db"):
    db = get_connection(db_name)
    niveaux = db.execute("SELECT id, nom FROM niveau ORDER BY id").fetchall()
    db.close()
    return niveaux


def get_specialites(db_name="shadowcomm.db"):
    db = get_connection(db_name)
    specialites = db.execute(
        """
        SELECT id, COALESCE(NULLIF(nom, ''), specialite) AS nom
        FROM specialite
        ORDER BY id
        """
    ).fetchall()
    db.close()
    return specialites


if __name__ == "__main__":
    init_db()
    seed_default_users()
    print("Base de données ShadowComm initialisée avec succès !")