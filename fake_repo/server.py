
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
