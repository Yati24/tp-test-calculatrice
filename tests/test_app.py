import os
import pytest

from app import app, init_db


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_history.db"
    monkeypatch.setattr('app.DB_PATH', str(db_file))
    init_db()
    yield
    if db_file.exists():
        os.remove(db_file)


def test_calc_and_history(client):
    res = client.post('/api/calc', json={'a': 2, 'b': 3, 'op': '+'})
    assert res.status_code == 200
    assert res.get_json()['result'] == 5

    res2 = client.get('/api/history')
    h = res2.get_json()
    assert isinstance(h, list)
    assert len(h) == 1


def test_division_by_zero(client):
    res = client.post('/api/calc', json={'a': 1, 'b': 0, 'op': '/'})
    assert res.status_code == 400
    assert 'error' in res.get_json()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
