"""
Simple test file for the Expense Tracker API
Run with: python -m pytest test_api.py -v
"""

import pytest
from app import app, expenses


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def token(client):
    """Get JWT token for testing"""
    response = client.post('/api/auth/login', json={
        'username': 'user1',
        'password': 'password123'
    })
    return response.json['access_token']


class TestAuth:
    def test_login_success(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'user1',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert response.json['user'] == 'user1'

    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'user1',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        assert response.json['message'] == 'Invalid credentials'


class TestExpenses:
    def test_get_expenses_no_auth(self, client):
        response = client.get('/api/expenses')
        assert response.status_code == 401

    def test_get_expenses_with_auth(self, client, token):
        response = client.get('/api/expenses', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
        assert 'expenses' in response.json

    def test_create_expense(self, client, token):
        response = client.post('/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'description': 'Test expense',
                'amount': 10.50,
                'category': 'Food'
            }
        )
        assert response.status_code == 201
        assert response.json['description'] == 'Test expense'
        assert response.json['amount'] == 10.50

    def test_get_expense_detail(self, client, token):
        # Create first
        create_resp = client.post('/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Test', 'amount': 5.00, 'category': 'Food'}
        )
        expense_id = create_resp.json['id']

        # Get detail
        response = client.get(f'/api/expenses/{expense_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert response.json['id'] == expense_id

    def test_update_expense(self, client, token):
        # Create first
        create_resp = client.post('/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Old', 'amount': 5.00, 'category': 'Food'}
        )
        expense_id = create_resp.json['id']

        # Update
        response = client.put(f'/api/expenses/{expense_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Updated', 'amount': 10.00}
        )
        assert response.status_code == 200
        assert response.json['description'] == 'Updated'
        assert response.json['amount'] == 10.00

    def test_delete_expense(self, client, token):
        # Create first
        create_resp = client.post('/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Test', 'amount': 5.00, 'category': 'Food'}
        )
        expense_id = create_resp.json['id']

        # Delete
        response = client.delete(f'/api/expenses/{expense_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert response.json['message'] == 'Expense deleted'


class TestHealth:
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
