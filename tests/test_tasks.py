import pytest
from app.models.task import TaskStatus, TaskPriority


@pytest.mark.tasks
class TestTasksCreate:
    """Tests for creating tasks"""

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation"""
        response = client.post('/api/tasks', headers=auth_headers, json={
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high',
            'status': 'pending'
        })

        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['title'] == 'New Task'

    def test_create_task_missing_title(self, client, auth_headers):
        """Test creating task without title"""
        response = client.post('/api/tasks', headers=auth_headers, json={
            'description': 'Task description'
        })

        assert response.status_code == 400
        assert response.json['success'] is False

    def test_create_task_no_auth(self, client):
        """Test creating task without authentication"""
        response = client.post('/api/tasks', json={
            'title': 'New Task',
            'description': 'Task description'
        })

        assert response.status_code == 401

    def test_create_task_with_tags(self, client, auth_headers, sample_tag):
        """Test creating task with tags"""
        response = client.post('/api/tasks', headers=auth_headers, json={
            'title': 'Task with tags',
            'description': 'Description',
            'tags': [sample_tag.id]
        })

        assert response.status_code == 201
        assert len(response.json['data']['tags']) > 0

    def test_create_task_with_due_date(self, client, auth_headers):
        """Test creating task with due date"""
        response = client.post('/api/tasks', headers=auth_headers, json={
            'title': 'Task with due date',
            'due_date': '2025-12-31T23:59:59'
        })

        assert response.status_code == 201
        assert response.json['data']['due_date'] is not None


@pytest.mark.tasks
class TestTasksList:
    """Tests for listing tasks"""

    def test_list_tasks_success(self, client, auth_headers, sample_tasks):
        """Test listing tasks"""
        response = client.get('/api/tasks', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json
        assert len(response.json['data']) > 0

    def test_list_tasks_no_auth(self, client):
        """Test listing tasks without authentication"""
        response = client.get('/api/tasks')

        assert response.status_code == 401

    def test_list_tasks_with_filter_status(self, client, auth_headers, sample_tasks):
        """Test listing tasks with status filter"""
        response = client.get('/api/tasks?status=completed', headers=auth_headers)

        assert response.status_code == 200
        for task in response.json['data']['tasks']:
            assert task['status'] == 'completed'

    def test_list_tasks_with_filter_priority(self, client, auth_headers, sample_tasks):
        """Test listing tasks with priority filter"""
        response = client.get('/api/tasks?priority=high', headers=auth_headers)

        assert response.status_code == 200
        for task in response.json['data']['tasks']:
            assert task['priority'] == 'high'

    def test_list_tasks_pagination(self, client, auth_headers, sample_tasks):
        """Test tasks pagination"""
        response = client.get('/api/tasks?page=1&per_page=2', headers=auth_headers)

        assert response.status_code == 200
        assert 'pagination' in response.json['data']
        assert 'tasks' in response.json['data']
        assert response.json['data']['pagination']['per_page'] == 2


@pytest.mark.tasks
class TestTasksGetOne:
    """Tests for getting a single task"""

    def test_get_task_success(self, client, auth_headers, sample_task):
        """Test getting a task"""
        response = client.get(f'/api/tasks/{sample_task.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['id'] == sample_task.id

    def test_get_task_not_found(self, client, auth_headers):
        """Test getting non-existent task"""
        response = client.get('/api/tasks/99999', headers=auth_headers)

        assert response.status_code == 404

    def test_get_task_no_auth(self, client, sample_task):
        """Test getting task without authentication"""
        response = client.get(f'/api/tasks/{sample_task.id}')

        assert response.status_code == 401

    def test_get_other_user_task(self, app, client, auth_headers, another_user):
        """Test getting another user's task"""
        from app.models.task import Task
        from app import db

        with app.app_context():
            other_task = Task(
                title='Other user task',
                user_id=another_user.id
            )
            db.session.add(other_task)
            db.session.commit()
            task_id = other_task.id

        response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)

        assert response.status_code == 403


@pytest.mark.tasks
class TestTasksUpdate:
    """Tests for updating tasks"""

    def test_update_task_success(self, client, auth_headers, sample_task):
        """Test successful task update"""
        response = client.put(f'/api/tasks/{sample_task.id}',
            headers=auth_headers,
            json={
                'title': 'Updated Title',
                'description': 'Updated description'
            }
        )

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['title'] == 'Updated Title'

    def test_update_task_status(self, client, auth_headers, sample_task):
        """Test updating task status"""
        response = client.put(f'/api/tasks/{sample_task.id}',
            headers=auth_headers,
            json={'status': 'completed'}
        )

        assert response.status_code == 200
        assert response.json['data']['status'] == 'completed'

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating non-existent task"""
        response = client.put('/api/tasks/99999',
            headers=auth_headers,
            json={'title': 'Updated'}
        )

        assert response.status_code == 404

    def test_update_task_no_auth(self, client, sample_task):
        """Test updating task without authentication"""
        response = client.put(f'/api/tasks/{sample_task.id}',
            json={'title': 'Updated'}
        )

        assert response.status_code == 401


@pytest.mark.tasks
class TestTasksDelete:
    """Tests for deleting tasks"""

    def test_delete_task_success(self, client, auth_headers, sample_task):
        """Test successful task deletion"""
        response = client.delete(f'/api/tasks/{sample_task.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting non-existent task"""
        response = client.delete('/api/tasks/99999', headers=auth_headers)

        assert response.status_code == 404

    def test_delete_task_no_auth(self, client, sample_task):
        """Test deleting task without authentication"""
        response = client.delete(f'/api/tasks/{sample_task.id}')

        assert response.status_code == 401


@pytest.mark.tasks
class TestTasksStats:
    """Tests for task statistics"""

    def test_get_stats_success(self, client, auth_headers, sample_tasks):
        """Test getting task statistics"""
        response = client.get('/api/tasks/statistics', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'total_tasks' in response.json['data']
        assert 'completed_tasks' in response.json['data']
        assert 'pending_tasks' in response.json['data']
        assert 'by_priority' in response.json['data']

    def test_get_stats_no_auth(self, client):
        """Test getting statistics without authentication"""
        response = client.get('/api/tasks/statistics')

        assert response.status_code == 401
