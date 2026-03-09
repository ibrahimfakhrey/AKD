"""Pytest configuration and fixtures."""
import sys
import os
import pytest

# Ensure the backend directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__) + '/..')

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    flask_app = create_app('testing')
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db
