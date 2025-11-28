import pytest


@pytest.mark.users
class TestUsersList:
    """Tests for listing users"""

    def test_list_users_as_admin(self, client, admin_auth_headers, regular_user):
        """Test listing users as admin"""
        response = client.get('/api/users', headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert len(response.json['data']) > 0

    def test_list_users_as_regular_user(self, client, auth_headers):
        """Test listing users as regular user"""
        response = client.get('/api/users', headers=auth_headers)

        # Regular users should not be able to list all users
        assert response.status_code == 403

    def test_list_users_no_auth(self, client):
        """Test listing users without authentication"""
        response = client.get('/api/users')

        assert response.status_code == 401

    def test_list_users_pagination(self, client, admin_auth_headers):
        """Test user list pagination"""
        response = client.get('/api/users?page=1&per_page=10', headers=admin_auth_headers)

        assert response.status_code == 200
        assert 'pagination' in response.json['data']
        assert 'users' in response.json['data']


@pytest.mark.users
class TestUsersGetOne:
    """Tests for getting a single user"""

    def test_get_user_self(self, client, auth_headers, regular_user):
        """Test getting own user profile"""
        response = client.get(f'/api/users/{regular_user.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['id'] == regular_user.id

    def test_get_user_as_admin(self, client, admin_auth_headers, regular_user):
        """Test getting user as admin"""
        response = client.get(f'/api/users/{regular_user.id}', headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.json['data']['id'] == regular_user.id

    def test_get_other_user_as_regular_user(self, client, auth_headers, another_user):
        """Test getting another user as regular user"""
        response = client.get(f'/api/users/{another_user.id}', headers=auth_headers)

        # Regular users should not be able to view other users
        assert response.status_code == 403

    def test_get_user_not_found(self, client, admin_auth_headers):
        """Test getting non-existent user"""
        response = client.get('/api/users/99999', headers=admin_auth_headers)

        assert response.status_code == 404

    def test_get_user_no_auth(self, client, regular_user):
        """Test getting user without authentication"""
        response = client.get(f'/api/users/{regular_user.id}')

        assert response.status_code == 401


@pytest.mark.users
class TestUsersUpdate:
    """Tests for updating users"""

    def test_update_user_self(self, client, auth_headers, regular_user):
        """Test updating own profile"""
        response = client.put(f'/api/users/{regular_user.id}',
            headers=auth_headers,
            json={
                'first_name': 'Updated',
                'last_name': 'Name'
            }
        )

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['first_name'] == 'Updated'

    def test_update_user_as_admin(self, client, admin_auth_headers, regular_user):
        """Test updating user as admin"""
        response = client.put(f'/api/users/{regular_user.id}',
            headers=admin_auth_headers,
            json={
                'first_name': 'Admin Updated',
                'is_active': False
            }
        )

        assert response.status_code == 200

    def test_update_other_user_as_regular_user(self, client, auth_headers, another_user):
        """Test updating another user as regular user"""
        response = client.put(f'/api/users/{another_user.id}',
            headers=auth_headers,
            json={'first_name': 'Hacked'}
        )

        # Regular users should not be able to update other users
        assert response.status_code == 403

    def test_update_user_not_found(self, client, admin_auth_headers):
        """Test updating non-existent user"""
        response = client.put('/api/users/99999',
            headers=admin_auth_headers,
            json={'first_name': 'Updated'}
        )

        assert response.status_code == 404

    def test_update_user_no_auth(self, client, regular_user):
        """Test updating user without authentication"""
        response = client.put(f'/api/users/{regular_user.id}',
            json={'first_name': 'Updated'}
        )

        assert response.status_code == 401


@pytest.mark.users
class TestUsersDelete:
    """Tests for deleting users"""

    def test_delete_user_as_admin(self, app, client, admin_auth_headers, another_user):
        """Test deleting user as admin"""
        response = client.delete(f'/api/users/{another_user.id}', headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True

    def test_delete_user_as_regular_user(self, client, auth_headers, another_user):
        """Test deleting user as regular user"""
        response = client.delete(f'/api/users/{another_user.id}', headers=auth_headers)

        # Regular users should not be able to delete users
        assert response.status_code == 403

    def test_delete_user_not_found(self, client, admin_auth_headers):
        """Test deleting non-existent user"""
        response = client.delete('/api/users/99999', headers=admin_auth_headers)

        assert response.status_code == 404

    def test_delete_user_no_auth(self, client, regular_user):
        """Test deleting user without authentication"""
        response = client.delete(f'/api/users/{regular_user.id}')

        assert response.status_code == 401


@pytest.mark.users
class TestUsersStats:
    """Tests for user statistics"""

    def test_get_user_stats_self(self, client, auth_headers, sample_tasks):
        """Test getting own user statistics"""
        response = client.get('/api/tasks/statistics', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'total_tasks' in response.json['data']

    def test_get_user_stats_no_auth(self, client):
        """Test getting statistics without authentication"""
        response = client.get('/api/tasks/statistics')

        assert response.status_code == 401
