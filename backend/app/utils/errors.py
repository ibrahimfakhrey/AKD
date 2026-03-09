"""Custom error handlers and exception classes."""
from flask import jsonify


class APIError(Exception):
    """Base API error."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv['error'] = self.message
        return rv


class NotFoundError(APIError):
    def __init__(self, message='Resource not found'):
        super().__init__(message, status_code=404)


class ForbiddenError(APIError):
    def __init__(self, message='Forbidden'):
        super().__init__(message, status_code=403)


class ConflictError(APIError):
    def __init__(self, message='Conflict'):
        super().__init__(message, status_code=409)


class InsufficientFundsError(APIError):
    def __init__(self, currency='points'):
        super().__init__(f'Insufficient {currency}', status_code=400)


def register_error_handlers(app):
    """Register JSON error handlers on the Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({'error': 'Internal server error'}), 500
