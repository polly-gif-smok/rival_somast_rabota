import pytest
from app import app, get_db, generate_password

def test_index_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Генератор паролей' in response.data

def test_generate_password(client):
    """Тест генерации пароля"""
    response = client.post('/generate', data={
        'length': 12,
        'use_digits': 'on',
        'use_special': 'on'
    })
    assert response.status_code == 200
    assert b'Сгенерированный пароль' in response.data

def test_add_password(client):
    """Тест добавления пароля"""
    response = client.post('/add', data={
        'site': 'test.com',
        'login': 'testuser',
        'password': 'testpass123',
        'notes': 'test notes'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Пароль успешно сохранён' in response.data

def test_search_passwords(client):
    """Тест поиска паролей"""
    # Сначала добавим пароль
    client.post('/add', data={
        'site': 'github.com',
        'login': 'user1',
        'password': 'pass123',
        'notes': ''
    })
    
    response = client.get('/search?q=github')
    assert response.status_code == 200
    assert b'github.com' in response.data

def test_404_error(client):
    """Тест обработки ошибки 404"""
    response = client.get('/password/99999')
    assert response.status_code == 302  # Редирект на список

def test_validation_empty_fields(client):
    """Тест валидации - пустые поля"""
    response = client.post('/add', data={
        'site': '',
        'login': '',
        'password': '',
        'notes': ''
    })
    assert response.status_code == 200
    assert b'Все поля' in response.data