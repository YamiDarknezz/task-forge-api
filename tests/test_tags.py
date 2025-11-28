import pytest


@pytest.mark.tags
class TestTagsCreate:
    """Tests for creating tags"""

    def test_create_tag_success(self, client, auth_headers):
        """Test successful tag creation"""
        response = client.post('/api/tags', headers=auth_headers, json={
            'name': 'NewTag',
            'color': '#FF0000',
            'description': 'A new tag'
        })

        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['name'] == 'NewTag'

    def test_create_tag_missing_name(self, client, auth_headers):
        """Test creating tag without name"""
        response = client.post('/api/tags', headers=auth_headers, json={
            'color': '#FF0000'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_create_tag_invalid_color(self, client, auth_headers):
        """Test creating tag with invalid color"""
        response = client.post('/api/tags', headers=auth_headers, json={
            'name': 'NewTag',
            'color': 'invalid'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_create_tag_duplicate_name(self, client, auth_headers, sample_tags):
        """Test creating tag with duplicate name"""
        response = client.post('/api/tags', headers=auth_headers, json={
            'name': 'Work',
            'color': '#FF0000'
        })

        assert response.status_code == 409
        assert response.json['success'] is False

    def test_create_tag_no_auth(self, client):
        """Test creating tag without authentication"""
        response = client.post('/api/tags', json={
            'name': 'NewTag'
        })

        assert response.status_code == 401


@pytest.mark.tags
class TestTagsList:
    """Tests for listing tags"""

    def test_list_tags_success(self, client, auth_headers, sample_tags):
        """Test listing tags"""
        response = client.get('/api/tags', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert len(response.json['data']) > 0

    def test_list_tags_no_auth(self, client):
        """Test listing tags without authentication"""
        response = client.get('/api/tags')

        assert response.status_code == 401

    def test_list_tags_pagination(self, client, auth_headers, sample_tags):
        """Test tags pagination"""
        response = client.get('/api/tags?page=1&per_page=2', headers=auth_headers)

        assert response.status_code == 200
        assert 'pagination' in response.json['data']
        assert 'tags' in response.json['data']


@pytest.mark.tags
class TestTagsGetOne:
    """Tests for getting a single tag"""

    def test_get_tag_success(self, client, auth_headers, sample_tag):
        """Test getting a tag"""
        response = client.get(f'/api/tags/{sample_tag.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['id'] == sample_tag.id

    def test_get_tag_not_found(self, client, auth_headers):
        """Test getting non-existent tag"""
        response = client.get('/api/tags/99999', headers=auth_headers)

        assert response.status_code == 404

    def test_get_tag_no_auth(self, client, sample_tag):
        """Test getting tag without authentication"""
        response = client.get(f'/api/tags/{sample_tag.id}')

        assert response.status_code == 401


@pytest.mark.tags
class TestTagsUpdate:
    """Tests for updating tags"""

    def test_update_tag_success(self, client, admin_auth_headers, sample_tag):
        """Test successful tag update"""
        response = client.put(f'/api/tags/{sample_tag.id}',
            headers=admin_auth_headers,
            json={
                'name': 'UpdatedTag',
                'color': '#00FF00',
                'description': 'Updated description'
            }
        )

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['name'] == 'UpdatedTag'

    def test_update_tag_not_found(self, client, admin_auth_headers):
        """Test updating non-existent tag"""
        response = client.put('/api/tags/99999',
            headers=admin_auth_headers,
            json={'name': 'Updated'}
        )

        assert response.status_code == 404

    def test_update_tag_invalid_color(self, client, admin_auth_headers, sample_tag):
        """Test updating tag with invalid color"""
        response = client.put(f'/api/tags/{sample_tag.id}',
            headers=admin_auth_headers,
            json={'color': 'invalid'}
        )

        assert response.status_code == 400

    def test_update_tag_no_auth(self, client, sample_tag):
        """Test updating tag without authentication"""
        response = client.put(f'/api/tags/{sample_tag.id}',
            json={'name': 'Updated'}
        )

        assert response.status_code == 401


@pytest.mark.tags
class TestTagsDelete:
    """Tests for deleting tags"""

    def test_delete_tag_success(self, client, admin_auth_headers, sample_tag):
        """Test successful tag deletion"""
        response = client.delete(f'/api/tags/{sample_tag.id}', headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True

    def test_delete_tag_not_found(self, client, admin_auth_headers):
        """Test deleting non-existent tag"""
        response = client.delete('/api/tags/99999', headers=admin_auth_headers)

        assert response.status_code == 404

    def test_delete_tag_no_auth(self, client, sample_tag):
        """Test deleting tag without authentication"""
        response = client.delete(f'/api/tags/{sample_tag.id}')

        assert response.status_code == 401
