import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint returns 200"""
        response = client.get('/api/health')

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json
        assert 'status' in response.json['data']
        assert 'database' in response.json['data']
        assert 'timestamp' in response.json['data']
        assert 'app_name' in response.json['data']
        assert 'version' in response.json['data']

    def test_health_check_status_healthy(self, client):
        """Test health check shows healthy status"""
        response = client.get('/api/health')

        assert response.json['data']['status'] in ['healthy', 'degraded']
        assert response.json['data']['database'] in ['connected', 'disconnected']

    def test_health_check_app_info(self, client):
        """Test health check includes app information"""
        response = client.get('/api/health')

        data = response.json['data']
        assert data['app_name'] == 'TaskForge API'
        assert data['version'] == '1.0.0'
