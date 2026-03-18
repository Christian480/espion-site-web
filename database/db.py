import sqlite3
import bcrypt

def create_user(code_name, niveau_id, specialite_id, password):
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
        "INSERT OR IGNORE INTO users (code_name, niveau_id, specialite_id, password) VALUES (?,?,?,?)",
        (code_name, niveau_id, specialite_id, hashed_password)
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