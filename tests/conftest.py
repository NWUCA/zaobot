import pytest
import os
from bot.server import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': 'test.db'
    })

    yield app

    os.remove('test.db')


@pytest.fixture(autouse=True)
def mock_send_to_tg(requests_mock, app):
    requests_mock.post(f"{app.config['TELEGRAM_API_ADDRESS']}/"
                       f"{app.config['TELEGRAM_API_TOKEN']}/sendMessage")


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def config(app):
    return app.config
