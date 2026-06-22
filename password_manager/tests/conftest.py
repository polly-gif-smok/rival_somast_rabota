import pytest
from app import app, get_db, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    init_db()
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    conn = get_db()
    yield conn
    conn.close()