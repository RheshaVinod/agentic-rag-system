
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
