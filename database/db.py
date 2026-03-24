import sqlite3
import bcrypt

def create_user(code_name, niveau_id, specialite_id, password, nom, age, lieu_affectation):
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    db = sqlite3.connect("shadowcomm.db")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE code_name = ?", (code_name,))
    if cursor.fetchone():
        print(f"{code_name} existe déjà dans la base de données.")
        db.close()
        return
    cursor.execute(
        "INSERT OR IGNORE INTO users (code_name, niveau_id, specialite_id, password, nom, age, lieu_affectation) VALUES (?,?,?,?,?,?,?)",
        (code_name, niveau_id, specialite_id, hashed_password, nom, age, lieu_affectation)
    )

    db.commit()
    db.close()


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
        FOREIGN KEY (sender_id) REFERENCES users(id) );

    INSERT OR IGNORE INTO niveau (id, nom) VALUES (1,'S'), (2,'A'), (3,'C');

    INSERT OR IGNORE INTO specialite (id, nom) VALUES
    (1,'agent-double'),
    (2,'agent-infiltré'),
    (3,'agent-informateur'),
    (4,'cyber-espion');
    """)

    cursor.execute("ALTER TABLE users ADD IF NOT EXISTS COLUMN nom TEXT")
    cursor.execute("ALTER TABLE users ADD IF NOT EXISTS COLUMN age INTEGER")
    cursor.execute("ALTER TABLE users ADD IF NOT EXISTS COLUMN Lieu_affectation TEXT")
    cursor.execute("ALTER TABLE message ADD IF NOT EXISTS COLUMN timestamp DATETIME")
    cursor.execute("ALTER TABLE message ADD IF NOT EXISTS FOREIGN KEY (receiver_id) REFERENCES users(id)")
    cursor.execute("ALTER TABLE message ADD IF NOT EXISTS COLUMN status INTEGER")
    cursor.execute("ALTER TABLE message ADD IF NOT EXISTS COLUMN receiver_id INTEGER")
    cursor.execute("DROP TABLE IF EXISTS messages")

    db.commit()
    db.close()


init_db()


create_user("agent007", 1, 4, "agent007@2026", "James Bond", 30, "Londres")
create_user("agentX", 2, 1, "motdepasse123", "Agent X", 25, "New York")
create_user("ghost", 3, 2, "secret456", "The Ghost", 35, "Tokyo")
create_user("shadow", 2, 3, "shadow@2026", "Shadow", 28, "Paris")
create_user("viper", 1, 2, "viperSecure", "Viper", 32, "Berlin")
create_user("falcon", 1, 1, "falcon123", "Falcon", 27, "Rome")
create_user("neo", 3, 4, "matrixNeo", "Neo", 29, "Zion")
create_user("hunter", 2, 2, "hunt3r!", "Hunter", 31, "Los Angeles")
create_user("zeus", 3, 3, "thunderBolt", "Zeus", 33, "Olympus")
create_user("phantom", 2, 1, "phantomX", "Phantom", 26, "London")

print("Base de données Shadowcomm initialisée avec succès !")
