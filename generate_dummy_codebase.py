# generate_dummy_codebase.py
import os

os.makedirs("fake_repo", exist_ok=True)

files = {
    "fake_repo/auth.py": '''
import jwt
import datetime

class AuthenticationService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def generate_jwt(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_jwt(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def refresh_token(self, token: str) -> str:
        payload = self.validate_jwt(token)
        return self.generate_jwt(payload["user_id"])
''',

    "fake_repo/db.py": '''
import sqlite3
from typing import Optional

class DatabaseService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: tuple = ()) -> list:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute_write(self, query: str, params: tuple = ()) -> int:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.lastrowid
''',

    "fake_repo/server.py": '''
from flask import Flask, request, jsonify

class APIServer:
    def __init__(self, auth_service, db_service):
        self.app = Flask(__name__)
        self.auth = auth_service
        self.db = db_service
        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule("/login", "login", self.login, methods=["POST"])
        self.app.add_url_rule("/users", "get_users", self.get_users, methods=["GET"])
        self.app.add_url_rule("/refresh", "refresh", self.refresh_token, methods=["POST"])

    def login(self):
        data = request.get_json()
        token = self.auth.generate_jwt(data["user_id"])
        return jsonify({"token": token})

    def get_users(self):
        token = request.headers.get("Authorization")
        self.auth.validate_jwt(token)
        users = self.db.execute_query("SELECT * FROM users")
        return jsonify([dict(u) for u in users])

    def refresh_token(self):
        token = request.headers.get("Authorization")
        new_token = self.auth.refresh_token(token)
        return jsonify({"token": new_token})
''',

    "fake_repo/error.py": '''
class AppError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ErrorHandler:
    def handle_auth_error(self, error: Exception) -> dict:
        return {"error": "Authentication failed", "detail": str(error), "code": 401}

    def handle_db_error(self, error: Exception) -> dict:
        return {"error": "Database error", "detail": str(error), "code": 500}

    def handle_not_found(self, resource: str) -> dict:
        return {"error": f"{resource} not found", "code": 404}

    def handle_validation_error(self, field: str, message: str) -> dict:
        return {"error": "Validation failed", "field": field, "detail": message, "code": 400}
''',

    "fake_repo/main.py": '''
from auth import AuthenticationService
from db import DatabaseService
from server import APIServer
from error import ErrorHandler

class Application:
    def __init__(self):
        self.auth = AuthenticationService(secret_key="super-secret-key")
        self.db = DatabaseService(db_path="app.db")
        self.error_handler = ErrorHandler()
        self.server = APIServer(self.auth, self.db)

    def startup(self):
        self.db.connect()
        print("Database connected")

    def shutdown(self):
        self.db.disconnect()
        print("Database disconnected")

    def run(self):
        self.startup()
        self.server.app.run(debug=True)

if __name__ == "__main__":
    app = Application()
    app.run()
'''
}

for filepath, content in files.items():
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")

print("\nDummy codebase ready!")