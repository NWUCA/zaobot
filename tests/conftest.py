import pytest
import os
from server import create_app
from db import init_database

@pytest.fixture(scope='session')
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': 'test.db'
    })

    with app.app_context():
        init_database()

    yield app

    os.remove('test.db')

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()