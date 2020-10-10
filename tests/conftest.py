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
    def callback(request, context):
        res = {"message_id": -1, "date": "fake", "chat": None}
        if request.path.split('/')[-1] == 'sendmediagroup':
            res = [res]
        return {"ok": True, "result": res}

    requests_mock.post(
        app.config['TELEGRAM_API_ADDRESS'].format(app.config['TELEGRAM_API_TOKEN'], "sendMessage"),
        json=callback
    )
    requests_mock.get(
        app.config['TELEGRAM_API_ADDRESS'].format(app.config['TELEGRAM_API_TOKEN'], "sendMediaGroup"),
        json=callback
    )


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def config(app):
    return app.config
