
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
