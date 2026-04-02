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

TABLES = (
    "CREATE TABLE IF NOT EXISTS niveau (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS specialite (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, specialite TEXT)",
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, code_name TEXT NOT NULL UNIQUE, niveau_id INTEGER NOT NULL DEFAULT 1, specialite_id INTEGER NOT NULL DEFAULT 1, password BLOB NOT NULL, nom TEXT, age INTEGER, lieu_affectation TEXT, FOREIGN KEY (niveau_id) REFERENCES niveau(id), FOREIGN KEY (specialite_id) REFERENCES specialite(id))",
    "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL, content TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (sender_id) REFERENCES users(id))",
)
USER_COLUMNS = (
    ("code_name", "TEXT"),
    ("niveau_id", "INTEGER DEFAULT 1"),
    ("specialite_id", "INTEGER DEFAULT 1"),
    ("nom", "TEXT"),
    ("age", "INTEGER"),
    ("lieu_affectation", "TEXT"),
)
DEFAULT_NIVEAUX = ((1, "S"), (2, "A"), (3, "C"))
DEFAULT_SPECIALITES = (
    (1, "agent-double", "agent-double"),
    (2, "agent-infiltré", "agent-infiltré"),
    (3, "agent-informateur", "agent-informateur"),
    (4, "cyber-espion", "cyber-espion"),
)


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
    try:
        return _get_columns(db.cursor(), table_name)
    finally:
        db.close()


def _add_missing_columns(cursor, table_name, columns):
    existing = _get_columns(cursor, table_name)
    for name, definition in columns:
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}")
    return _get_columns(cursor, table_name)


def _fetchall(db_name, sql):
    db = get_connection(db_name)
    try:
        return db.execute(sql).fetchall()
    finally:
        db.close()


def init_db(db_name="shadowcomm.db"):
    db = get_connection(db_name)

    try:
        cursor = db.cursor()
        for sql in TABLES:
            cursor.execute(sql)

        user_columns = _add_missing_columns(cursor, "users", USER_COLUMNS)
        if "username" in user_columns:
            cursor.execute(
                "UPDATE users SET code_name = username WHERE (code_name IS NULL OR code_name = '') AND username IS NOT NULL"
            )
        cursor.execute("UPDATE users SET niveau_id = 1 WHERE niveau_id IS NULL")
        cursor.execute("UPDATE users SET specialite_id = 1 WHERE specialite_id IS NULL")

        if "nom" not in _get_columns(cursor, "specialite"):
            cursor.execute("ALTER TABLE specialite ADD COLUMN nom TEXT")
        cursor.execute("UPDATE specialite SET nom = specialite WHERE nom IS NULL OR nom = ''")

        if _table_exists(cursor, "message"):
            timestamp_sql = "timestamp" if "timestamp" in _get_columns(cursor, "message") else "CURRENT_TIMESTAMP"
            cursor.execute(
                f"INSERT OR IGNORE INTO messages (id, sender_id, content, timestamp) SELECT id, sender_id, content, {timestamp_sql} FROM message"
            )
            cursor.execute("DROP TABLE IF EXISTS message")

        cursor.executemany("INSERT OR IGNORE INTO niveau (id, nom) VALUES (?, ?)", DEFAULT_NIVEAUX)
        cursor.executemany(
            "INSERT OR IGNORE INTO specialite (id, nom, specialite) VALUES (?, ?, ?)",
            DEFAULT_SPECIALITES,
        )
        db.commit()
    finally:
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
    db = get_connection(db_name)
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM users WHERE code_name = ?", (code_name,))
        if cursor.fetchone() is not None:
            return False
        cursor.execute(
            "INSERT INTO users (code_name, niveau_id, specialite_id, password, nom, age, lieu_affectation) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (code_name, niveau_id, specialite_id, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), nom, age, lieu_affectation),
        )
        db.commit()
        return True
    finally:
        db.close()


def seed_default_users(db_name="shadowcomm.db"):
    for user in DEFAULT_USERS:
        create_user(*user, db_name=db_name)


def get_niveaux(db_name="shadowcomm.db"):
    return _fetchall(db_name, "SELECT id, nom FROM niveau ORDER BY id")


def get_specialites(db_name="shadowcomm.db"):
    return _fetchall(
        db_name,
        "SELECT id, COALESCE(NULLIF(nom, ''), specialite) AS nom FROM specialite ORDER BY id",
    )


<<<<<<< HEAD

def init_db():
    db = sqlite3.connect("shadowcomm.db")
    cursor = db.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS niveau (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS specialite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        specialite TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        code_name TEXT NOT NULL UNIQUE,
        niveau_id INTEGER NOT NULL,
        specialite_id INTEGER NOT NULL,
        password BLOB NOT NULL,
        FOREIGN KEY (niveau_id) REFERENCES niveau(id),
        FOREIGN KEY (specialite_id) REFERENCES specialite(id)
    );
                         
    CREATE TABLE IF NOT EXISTS message ( 
         id INTEGER PRIMARY KEY AUTOINCREMENT, 
         sender_id INTEGER NOT NULL, 
         content TEXT NOT NULL, 
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
         FOREIGN KEY (sender_id) REFERENCES users(id)
     );

    INSERT OR IGNORE INTO niveau (id, nom) VALUES (1,'S'), (2,'A'), (3,'C');

    INSERT OR IGNORE INTO specialite (id, nom) VALUES
    (1,'agent-double'),
    (2,'agent-infiltré'),
    (3,'agent-informateur'),
    (4,'cyber-espion');
    """)

    cursor.execute("DROP TABLE IF EXISTS messages")

    db.commit()
    db.close()


init_db()


create_user("agent007", 1, 4, "agent007@2026")
create_user("agentX", 2, 1, "motdepasse123")
create_user("ghost", 3, 2, "secret456")

print("Base de données Shadowcomm initialisée avec succès !")
=======
if __name__ == "__main__":
    init_db()
    seed_default_users()
    print("Base de données ShadowComm initialisée avec succès !")
>>>>>>> christian
