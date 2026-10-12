import os
import tempfile

import pytest

from webapp_v1.aime import create_app
from webapp_v1.aime.extensions import db
from webapp_v1.aime.models import EmotionAnalysis


@pytest.fixture()
def client():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{path}',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()
    if os.path.exists(path):
        os.remove(path)


def register_and_login(client, email='user@example.com', password='TestPass123', name='User One'):
    res = client.post('/api/v1/auth/register', json={'fullName': name, 'email': email, 'password': password})
    assert res.status_code == 201


def test_register_login_and_me(client):
    register_and_login(client)
    me = client.get('/api/v1/auth/me')
    assert me.status_code == 200
    assert me.get_json()['user']['email'] == 'user@example.com'


def test_invalid_login(client):
    register_and_login(client)
    bad = client.post('/api/v1/auth/login', json={'email': 'user@example.com', 'password': 'wrong'})
    assert bad.status_code == 401


def test_protected_history_requires_auth(client):
    res = client.get('/api/v1/history')
    assert res.status_code == 401


def test_save_and_delete_analysis(client):
    register_and_login(client)
    save = client.post('/api/v1/analysis/save', json={
        'modality': 'audio',
        'predictedEmotion': 'happy',
        'confidenceScore': 0.88,
        'classProbabilities': {'happy': 0.88}
    })
    assert save.status_code == 201
    analysis_id = save.get_json()['analysis']['id']

    get_one = client.get(f'/api/v1/analysis/{analysis_id}')
    assert get_one.status_code == 200

    delete = client.delete(f'/api/v1/analysis/{analysis_id}')
    assert delete.status_code == 200

    missing = client.get(f'/api/v1/analysis/{analysis_id}')
    assert missing.status_code == 404


def test_user_data_isolation(client):
    register_and_login(client, email='u1@example.com', name='U1')
    save = client.post('/api/v1/analysis/save', json={
        'modality': 'video',
        'predictedEmotion': 'sad',
        'confidenceScore': 0.55,
    })
    analysis_id = save.get_json()['analysis']['id']

    client.post('/api/v1/auth/logout')
    register_and_login(client, email='u2@example.com', name='U2')

    access = client.get(f'/api/v1/analysis/{analysis_id}')
    assert access.status_code == 404

    with client.application.app_context():
        assert EmotionAnalysis.query.count() == 1
