import pytest
import json

from server import create_app
from db import init_database

import sys
import os
# 不添加path会导致ModuleNotFoundError
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))


@pytest.fixture(scope='session')
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': 'test.db'
    })

    init_database(app)

    yield app

    os.remove('test.db')


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def data():
    # TODO 为什么要这么写 直接open json在coverage下报错找不到文件
    with open(os.path.join(os.path.dirname(__file__), 'test_data.json'), 'r') as f:
        yield json.load(f)


