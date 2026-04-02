import os
import sqlite3
import tempfile
import unittest

import bcrypt

from app import create_app
from database.db import get_connection


class ShadowCommTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key",
                "DATABASE": self.db_path,
                "AUTO_INIT_DB": True,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_home_page(self):
        response = self.client.get("/")
        text = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("ShadowComm", text)

    def test_classification_page(self):
        response = self.client.get("/classification")
        text = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Niveaux de classification", text)
        self.assertIn("Niveau S", text)

    def test_register_login_and_send_message(self):
        response = self.client.post(
            "/register",
            data={
                "username": "agent-test",
                "nom": "Agent Test",
                "age": "29",
                "lieu_affectation": "Paris",
                "niveau_id": "2",
                "specialite_id": "4",
                "password": "secret123",
                "accept_rules": "on",
            },
            follow_redirects=True,
        )
        self.assertIn("Connexion", response.get_data(as_text=True))

        response = self.client.post(
            "/login",
            data={"username": "agent-test", "password": "secret123"},
            follow_redirects=True,
        )
        self.assertIn("Chat ShadowComm", response.get_data(as_text=True))

        response = self.client.post(
            "/chat",
            data={"content": "MINUIT"},
            follow_redirects=True,
        )
        text = response.get_data(as_text=True)

        self.assertIn("PLQXLW", text)
        self.assertIn("Déchiffrer", text)

        db = get_connection(self.db_path)
        cursor = db.cursor()
        cursor.execute(
            "SELECT code_name, nom, age, lieu_affectation, niveau_id, specialite_id FROM users WHERE code_name = ?",
            ("agent-test",),
        )
        user_row = cursor.fetchone()
        cursor.execute("SELECT content FROM messages")
        row = cursor.fetchone()
        db.close()

        self.assertIsNotNone(user_row)
        self.assertEqual(user_row["nom"], "Agent Test")
        self.assertEqual(user_row["age"], 29)
        self.assertEqual(user_row["lieu_affectation"], "Paris")
        self.assertEqual(user_row["niveau_id"], 2)
        self.assertEqual(user_row["specialite_id"], 4)
        self.assertIsNotNone(row)
        self.assertEqual(row["content"], "PLQXLW")

    def test_user_can_decrypt_displayed_chat_message(self):
        self.client.post(
            "/register",
            data={
                "username": "field-agent",
                "niveau_id": "1",
                "specialite_id": "1",
                "password": "secret123",
                "accept_rules": "on",
            },
            follow_redirects=True,
        )

        self.client.post(
            "/login",
            data={"username": "field-agent", "password": "secret123"},
            follow_redirects=True,
        )

        self.client.post(
            "/chat",
            data={"content": "MINUIT"},
            follow_redirects=True,
        )

        db = get_connection(self.db_path)
        cursor = db.cursor()
        cursor.execute("SELECT id, content FROM messages ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        db.close()

        response = self.client.post(
            f"/chat/messages/{row['id']}/decrypt",
            follow_redirects=True,
        )
        text = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(row["content"], "PLQXLW")
        self.assertIn("PLQXLW", text)
        self.assertIn("MINUIT", text)
        self.assertIn("Message déchiffré", text)

    def test_chat_page_hides_manual_decrypt_and_agents_page_shows_classes(self):
        self.client.post(
            "/register",
            data={
                "username": "decrypt-agent",
                "niveau_id": "2",
                "specialite_id": "4",
                "password": "secret123",
                "accept_rules": "on",
            },
            follow_redirects=True,
        )

        self.client.post(
            "/login",
            data={"username": "decrypt-agent", "password": "secret123"},
            follow_redirects=True,
        )

        response = self.client.get("/chat")
        text = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Déchiffrer une transmission", text)

        response = self.client.get("/agents")
        text = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("decrypt-agent", text)
        self.assertIn("Classe A", text)
        self.assertIn("cyber-espion", text)

    def test_legacy_database_allows_register_and_login(self):
        legacy_fd, legacy_path = tempfile.mkstemp()

        try:
            db = sqlite3.connect(legacy_path)
            cursor = db.cursor()
            cursor.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password BLOB NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("legacy-agent", bcrypt.hashpw(b"legacy-pass", bcrypt.gensalt())),
            )
            db.commit()
            db.close()

            app = create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "legacy-test-key",
                    "DATABASE": legacy_path,
                    "AUTO_INIT_DB": True,
                }
            )
            client = app.test_client()

            response = client.post(
                "/register",
                data={
                    "username": "new-agent",
                    "password": "secret123",
                    "accept_rules": "on",
                },
                follow_redirects=True,
            )
            self.assertIn("Compte créé", response.get_data(as_text=True))

            response = client.post(
                "/login",
                data={"username": "legacy-agent", "password": "legacy-pass"},
                follow_redirects=True,
            )
            self.assertIn("Chat ShadowComm", response.get_data(as_text=True))
        finally:
            os.close(legacy_fd)
            os.unlink(legacy_path)

    def test_create_app_does_not_initialize_database_without_flag(self):
        db_fd, db_path = tempfile.mkstemp()

        try:
            app = create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "no-init-test-key",
                    "DATABASE": db_path,
                    "AUTO_INIT_DB": False,
                }
            )

            self.assertFalse(app.config["AUTO_INIT_DB"])

            db = sqlite3.connect(db_path)
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            tables = cursor.fetchall()
            db.close()

            self.assertEqual(tables, [])
        finally:
            os.close(db_fd)
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()