import pytest
from app.models.user import User


@pytest.mark.auth
class TestAuthRegister:
    """Tests for user registration"""

    def test_register_success(self, client, init_database):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'Password123',
            'first_name': 'New',
            'last_name': 'User'
        })

        assert response.status_code == 201
        assert response.json['success'] is True
        assert 'data' in response.json
        assert response.json['data']['username'] == 'newuser'

    def test_register_missing_fields(self, client, init_database):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_register_invalid_email(self, client, init_database):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'Password123'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_register_weak_password(self, client, init_database):
        """Test registration with weak password"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'weak'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_register_duplicate_username(self, client, regular_user):
        """Test registration with duplicate username"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'different@test.com',
            'password': 'Password123'
        })

        assert response.status_code == 409
        assert response.json['success'] is False

    def test_register_duplicate_email(self, client, regular_user):
        """Test registration with duplicate email"""
        response = client.post('/api/auth/register', json={
            'username': 'differentuser',
            'email': 'user@test.com',
            'password': 'Password123'
        })

        assert response.status_code == 409
        assert response.json['success'] is False

    def test_register_no_data(self, client, init_database):
        """Test registration with no data"""
        response = client.post(
            '/api/auth/register',
            json={},
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 400
        assert response.json['success'] is False


@pytest.mark.auth
class TestAuthLogin:
    """Tests for user login"""

    def test_login_success(self, client, regular_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'User123!'
        })

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json
        assert 'access_token' in response.json['data']
        assert 'refresh_token' in response.json['data']

    def test_login_invalid_email(self, client, regular_user):
        """Test login with invalid email"""
        response = client.post('/api/auth/login', json={
            'email': 'wrong@test.com',
            'password': 'User123!'
        })

        assert response.status_code == 401
        assert response.json['success'] is False

    def test_login_invalid_password(self, client, regular_user):
        """Test login with invalid password"""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'WrongPassword123'
        })

        assert response.status_code == 401
        assert response.json['success'] is False

    def test_login_missing_fields(self, client, init_database):
        """Test login with missing fields"""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_login_inactive_user(self, app, client, regular_user):
        """Test login with inactive user"""
        with app.app_context():
            user = User.query.get(regular_user.id)
            user.is_active = False
            from app import db
            db.session.commit()

        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'User123!'
        })

        assert response.status_code == 403
        assert response.json['success'] is False


@pytest.mark.auth
class TestAuthMe:
    """Tests for getting current user"""

    def test_me_success(self, client, auth_headers):
        """Test getting current user"""
        response = client.get('/api/auth/me', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json

    def test_me_no_token(self, client):
        """Test getting current user without token"""
        response = client.get('/api/auth/me')

        assert response.status_code == 401


@pytest.mark.auth
class TestAuthRefresh:
    """Tests for token refresh"""

    def test_refresh_token_success(self, client, user_refresh_token):
        """Test refreshing access token"""
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {user_refresh_token}'
        })

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'access_token' in response.json['data']

    def test_refresh_token_no_token(self, client):
        """Test refreshing without token"""
        response = client.post('/api/auth/refresh')

        assert response.status_code == 401


@pytest.mark.auth
class TestAuthLogout:
    """Tests for logout"""

    def test_logout_success(self, client, user_refresh_token, auth_headers):
        """Test logout"""
        response = client.post('/api/auth/logout',
            headers=auth_headers,
            json={'refresh_token': user_refresh_token}
        )

        assert response.status_code == 200
        assert response.json['success'] is True

    def test_logout_no_token(self, client, auth_headers):
        """Test logout without refresh token"""
        response = client.post('/api/auth/logout',
            headers=auth_headers,
            json={}
        )

        assert response.status_code == 400


@pytest.mark.auth
class TestAuthChangePassword:
    """Tests for password change"""

    def test_change_password_success(self, client, auth_headers):
        """Test successful password change"""
        response = client.post('/api/auth/change-password',
            headers=auth_headers,
            json={
                'old_password': 'User123!',
                'new_password': 'NewPassword123!'
            }
        )

        assert response.status_code == 200
        assert response.json['success'] is True

    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test password change with wrong old password"""
        response = client.post('/api/auth/change-password',
            headers=auth_headers,
            json={
                'old_password': 'WrongPassword123',
                'new_password': 'NewPassword123!'
            }
        )

        assert response.status_code == 401
        assert response.json['success'] is False

    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test password change with weak new password"""
        response = client.post('/api/auth/change-password',
            headers=auth_headers,
            json={
                'old_password': 'User123!',
                'new_password': 'weak'
            }
        )

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_change_password_missing_fields(self, client, auth_headers):
        """Test password change with missing fields"""
        response = client.post('/api/auth/change-password',
            headers=auth_headers,
            json={
                'old_password': 'User123!'
            }
        )

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_change_password_no_auth(self, client):
        """Test password change without authentication"""
        response = client.post('/api/auth/change-password',
            json={
                'old_password': 'User123!',
                'new_password': 'NewPassword123!'
            }
        )

        assert response.status_code == 401
