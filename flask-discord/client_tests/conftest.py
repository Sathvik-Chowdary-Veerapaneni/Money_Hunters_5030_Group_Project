import os
import tempfile

import pytest
from flaskd import create_app
from flaskd.db import get_db, init_db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        })
    yield app
    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


