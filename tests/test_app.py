import os
import tempfile
import unittest

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

    def test_register_login_and_send_message(self):
        response = self.client.post(
            "/register",
            data={
                "username": "agent-test",
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

        self.assertIn("MINUIT", text)

        db = get_connection(self.db_path)
        cursor = db.cursor()
        cursor.execute("SELECT content FROM messages")
        row = cursor.fetchone()
        db.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["content"], "PLQXLW")


if __name__ == "__main__":
    unittest.main()