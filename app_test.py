import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_script(client):
    response = client.post('/execute', json={
        "script": "def main():\n    return {\"foo\": \"bar\"}"
    })
    assert response.status_code == 200
    assert response.get_json()["result"] == {"foo": "bar"}

def test_missing_main(client):
    response = client.post('/execute', json={
        "script": "def not_main():\n    return {\"foo\": \"bar\"}"
    })
    assert response.status_code == 400