import pytest
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.services.tag_service import TagService
from app.models.user import User, RefreshToken, RoleType
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.tag import Tag
from app import db


class TestAuthService:
    """Tests for AuthService"""

    def test_register_user_success(self, app, init_database):
        """Test successful user registration"""
        with app.app_context():
            success, user, status_code = AuthService.register_user({
                'username': 'newuser',
                'email': 'new@test.com',
                'password': 'Password123',
                'first_name': 'New',
                'last_name': 'User'
            })

            assert success is True
            assert user.username == 'newuser'
            assert status_code == 201

    def test_register_user_missing_fields(self, app, init_database):
        """Test registration with missing fields"""
        with app.app_context():
            success, error, status_code = AuthService.register_user({
                'username': 'newuser'
            })

            assert success is False
            assert status_code == 400

    def test_register_user_duplicate_username(self, app, regular_user):
        """Test registration with duplicate username"""
        with app.app_context():
            success, error, status_code = AuthService.register_user({
                'username': 'testuser',
                'email': 'different@test.com',
                'password': 'Password123'
            })

            assert success is False
            assert status_code == 409

    def test_login_user_success(self, app, regular_user):
        """Test successful login"""
        with app.app_context():
            success, tokens, status_code = AuthService.login_user({
                'email': 'user@test.com',
                'password': 'User123!'
            })

            assert success is True
            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
            assert status_code == 200

    def test_login_user_invalid_password(self, app, regular_user):
        """Test login with invalid password"""
        with app.app_context():
            success, error, status_code = AuthService.login_user({
                'email': 'user@test.com',
                'password': 'WrongPassword'
            })

            assert success is False
            assert status_code == 401

    def test_change_password_success(self, app, regular_user):
        """Test successful password change"""
        with app.app_context():
            success, message, status_code = AuthService.change_password(
                regular_user.id,
                {
                    'old_password': 'User123!',
                    'new_password': 'NewPassword123!'
                }
            )

            assert success is True
            assert status_code == 200

    def test_change_password_wrong_old(self, app, regular_user):
        """Test password change with wrong old password"""
        with app.app_context():
            success, error, status_code = AuthService.change_password(
                regular_user.id,
                {
                    'old_password': 'WrongPassword',
                    'new_password': 'NewPassword123!'
                }
            )

            assert success is False
            assert status_code == 401

    def test_get_current_user(self, app, regular_user):
        """Test getting current user"""
        with app.app_context():
            success, user, status_code = AuthService.get_current_user(regular_user.id)

            assert success is True
            assert user.id == regular_user.id
            assert status_code == 200

    def test_cleanup_expired_tokens(self, app, regular_user):
        """Test cleanup of expired tokens"""
        with app.app_context():
            # Create expired token
            expired_token = RefreshToken(
                token='expired_token',
                user_id=regular_user.id,
                expires_at=datetime.utcnow() - timedelta(days=1)
            )
            db.session.add(expired_token)
            db.session.commit()

            count = AuthService.cleanup_expired_tokens()
            assert count >= 1

    def test_get_current_user_not_found(self, app):
        """Test getting non-existent user"""
        with app.app_context():
            success, error, status_code = AuthService.get_current_user(99999)

            assert success is False
            assert status_code == 404

    def test_change_password_user_not_found(self, app):
        """Test changing password for non-existent user"""
        with app.app_context():
            success, error, status_code = AuthService.change_password(
                99999,
                {
                    'old_password': 'Old123!',
                    'new_password': 'New123!'
                }
            )

            assert success is False
            assert status_code == 404

    def test_change_password_missing_fields(self, app, regular_user):
        """Test changing password with missing fields"""
        with app.app_context():
            success, error, status_code = AuthService.change_password(
                regular_user.id,
                {'old_password': 'Old123!'}
            )

            assert success is False
            assert status_code == 400

    def test_change_password_weak_password(self, app, regular_user):
        """Test changing to weak password"""
        with app.app_context():
            success, error, status_code = AuthService.change_password(
                regular_user.id,
                {
                    'old_password': 'User123!',
                    'new_password': 'weak'
                }
            )

            assert success is False
            assert status_code == 400

    def test_register_user_invalid_username(self, app, init_database):
        """Test registration with invalid username"""
        with app.app_context():
            success, error, status_code = AuthService.register_user({
                'username': 'ab',  # Too short
                'email': 'test@test.com',
                'password': 'Password123'
            })

            assert success is False
            assert status_code == 400

    def test_login_user_missing_fields(self, app):
        """Test login with missing fields"""
        with app.app_context():
            success, error, status_code = AuthService.login_user({
                'email': 'test@test.com'
            })

            assert success is False
            assert status_code == 400

    def test_logout_user_no_token(self, app):
        """Test logout without token"""
        with app.app_context():
            success, error, status_code = AuthService.logout_user(None)

            assert success is False
            assert status_code == 400

    def test_logout_user_with_token(self, app, regular_user, user_refresh_token):
        """Test logout with valid token"""
        with app.app_context():
            success, message, status_code = AuthService.logout_user(user_refresh_token)

            assert success is True
            assert status_code == 200

    def test_refresh_token_invalid(self, app):
        """Test refreshing with invalid token"""
        with app.app_context():
            success, error, status_code = AuthService.refresh_access_token('invalid_token')

            assert success is False
            assert status_code == 401


class TestTaskService:
    """Tests for TaskService"""

    def test_create_task_success(self, app, regular_user):
        """Test successful task creation"""
        with app.app_context():
            success, task, status_code = TaskService.create_task(
                regular_user.id,
                {
                    'title': 'New Task',
                    'description': 'Task description',
                    'priority': 'high'
                }
            )

            assert success is True
            assert task.title == 'New Task'
            assert status_code == 201

    def test_create_task_missing_title(self, app, regular_user):
        """Test task creation without title"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {'description': 'Task description'}
            )

            assert success is False
            assert status_code == 400

    def test_create_task_title_too_long(self, app, regular_user):
        """Test task creation with title too long"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {'title': 'A' * 300}
            )

            assert success is False
            assert status_code == 400

    def test_create_task_invalid_status(self, app, regular_user):
        """Test task creation with invalid status"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {'title': 'Task', 'status': 'invalid'}
            )

            assert success is False
            assert status_code == 400

    def test_create_task_invalid_priority(self, app, regular_user):
        """Test task creation with invalid priority"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {'title': 'Task', 'priority': 'invalid'}
            )

            assert success is False
            assert status_code == 400

    def test_create_task_invalid_due_date(self, app, regular_user):
        """Test task creation with invalid due date"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {'title': 'Task', 'due_date': 'invalid-date'}
            )

            assert success is False
            assert status_code == 400

    def test_create_task_with_tags(self, app, regular_user, sample_tag):
        """Test task creation with tags"""
        with app.app_context():
            success, task, status_code = TaskService.create_task(
                regular_user.id,
                {
                    'title': 'Task with tags',
                    'tags': [sample_tag.id]
                }
            )

            assert success is True
            assert task.tags.count() > 0
            assert status_code == 201

    def test_create_task_with_description(self, app, regular_user):
        """Test creating task with description"""
        with app.app_context():
            success, task, status_code = TaskService.create_task(
                regular_user.id,
                {
                    'title': 'Task with description',
                    'description': 'This is a detailed description'
                }
            )

            assert success is True
            assert task.description == 'This is a detailed description'
            assert status_code == 201

    def test_create_task_description_too_long(self, app, regular_user):
        """Test creating task with description too long"""
        with app.app_context():
            success, error, status_code = TaskService.create_task(
                regular_user.id,
                {
                    'title': 'Task',
                    'description': 'A' * 6000
                }
            )

            assert success is False
            assert status_code == 400

    def test_get_user_tasks(self, app, regular_user, sample_tasks):
        """Test getting user tasks"""
        with app.app_context():
            success, result, status_code = TaskService.get_tasks(
                user_id=regular_user.id,
                is_admin=False
            )

            assert success is True
            assert status_code == 200
            assert len(result['tasks']) > 0
            assert result['pagination']['total'] >= 3

    def test_get_tasks_with_status_filter(self, app, regular_user, sample_tasks):
        """Test getting tasks with status filter"""
        with app.app_context():
            success, result, status_code = TaskService.get_tasks(
                regular_user.id,
                filters={'status': 'completed'}
            )

            assert success is True
            assert len(result['tasks']) >= 1

    def test_get_tasks_with_priority_filter(self, app, regular_user, sample_tasks):
        """Test getting tasks with priority filter"""
        with app.app_context():
            success, result, status_code = TaskService.get_tasks(
                regular_user.id,
                filters={'priority': 'high'}
            )

            assert success is True

    def test_get_tasks_with_search_filter(self, app, regular_user, sample_tasks):
        """Test getting tasks with search filter"""
        with app.app_context():
            success, result, status_code = TaskService.get_tasks(
                regular_user.id,
                filters={'search': 'Pending'}
            )

            assert success is True

    def test_get_tasks_as_admin(self, app, admin_user, sample_tasks):
        """Test getting all tasks as admin"""
        with app.app_context():
            success, result, status_code = TaskService.get_tasks(
                admin_user.id,
                is_admin=True
            )

            assert success is True
            assert len(result['tasks']) >= 0

    def test_get_task_by_id_success(self, app, regular_user, sample_task):
        """Test getting task by ID"""
        with app.app_context():
            success, task, status_code = TaskService.get_task(
                sample_task.id,
                regular_user.id
            )

            assert success is True
            assert task.id == sample_task.id
            assert status_code == 200

    def test_get_task_as_admin(self, app, admin_user, sample_task):
        """Test getting task as admin"""
        with app.app_context():
            success, task, status_code = TaskService.get_task(
                sample_task.id,
                admin_user.id,
                is_admin=True
            )

            assert success is True
            assert task.id == sample_task.id

    def test_get_task_permission_denied(self, app, regular_user, another_user):
        """Test getting another user's task"""
        with app.app_context():
            # Create task for another user
            from app.models.task import Task
            from app import db
            task = Task(title='Other task', user_id=another_user.id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

            success, error, status_code = TaskService.get_task(
                task_id,
                regular_user.id,
                is_admin=False
            )

            assert success is False
            assert status_code == 403

    def test_get_task_by_id_not_found(self, app, regular_user):
        """Test getting non-existent task"""
        with app.app_context():
            success, error, status_code = TaskService.get_task(99999, regular_user.id)

            assert success is False
            assert status_code == 404

    def test_update_task_success(self, app, regular_user, sample_task):
        """Test successful task update"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'title': 'Updated Title'}
            )

            assert success is True
            assert task.title == 'Updated Title'
            assert status_code == 200

    def test_update_task_not_found(self, app, regular_user):
        """Test updating non-existent task"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                99999,
                regular_user.id,
                {'title': 'Updated'}
            )

            assert success is False
            assert status_code == 404

    def test_update_task_invalid_title(self, app, regular_user, sample_task):
        """Test updating task with invalid title"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'title': 'A' * 300}
            )

            assert success is False
            assert status_code == 400

    def test_update_task_description(self, app, regular_user, sample_task):
        """Test updating task description"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'description': 'Updated description'}
            )

            assert success is True
            assert task.description == 'Updated description'
            assert status_code == 200

    def test_update_task_description_too_long(self, app, regular_user, sample_task):
        """Test updating with description too long"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'description': 'A' * 6000}
            )

            assert success is False
            assert status_code == 400

    def test_update_task_status(self, app, regular_user, sample_task):
        """Test updating task status"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'status': 'completed'}
            )

            assert success is True
            assert task.status == TaskStatus.COMPLETED.value
            assert task.completed_at is not None
            assert status_code == 200

    def test_update_task_status_invalid(self, app, regular_user, sample_task):
        """Test updating with invalid status"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'status': 'invalid'}
            )

            assert success is False
            assert status_code == 400

    def test_update_task_priority(self, app, regular_user, sample_task):
        """Test updating task priority"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'priority': 'urgent'}
            )

            assert success is True
            assert task.priority == TaskPriority.URGENT.value
            assert status_code == 200

    def test_update_task_priority_invalid(self, app, regular_user, sample_task):
        """Test updating with invalid priority"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'priority': 'invalid'}
            )

            assert success is False
            assert status_code == 400

    def test_update_task_due_date(self, app, regular_user, sample_task):
        """Test updating task due date"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'due_date': '2025-12-31T23:59:59'}
            )

            assert success is True
            assert task.due_date is not None
            assert status_code == 200

    def test_update_task_due_date_invalid(self, app, regular_user, sample_task):
        """Test updating with invalid due date"""
        with app.app_context():
            success, error, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'due_date': 'invalid-date'}
            )

            assert success is False
            assert status_code == 400

    def test_update_task_due_date_clear(self, app, regular_user, sample_task):
        """Test clearing task due date"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'due_date': None}
            )

            assert success is True
            assert task.due_date is None
            assert status_code == 200

    def test_update_task_tags(self, app, regular_user, sample_task, sample_tag):
        """Test updating task tags"""
        with app.app_context():
            success, task, status_code = TaskService.update_task(
                sample_task.id,
                regular_user.id,
                {'tags': [sample_tag.id]}
            )

            assert success is True
            assert status_code == 200

    def test_update_task_permission_denied(self, app, regular_user, another_user):
        """Test updating another user's task"""
        with app.app_context():
            from app.models.task import Task
            from app import db
            task = Task(title='Other task', user_id=another_user.id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

            success, error, status_code = TaskService.update_task(
                task_id,
                regular_user.id,
                {'title': 'Hacked'},
                is_admin=False
            )

            assert success is False
            assert status_code == 403

    def test_delete_task_success(self, app, regular_user, sample_task):
        """Test successful task deletion"""
        with app.app_context():
            success, message, status_code = TaskService.delete_task(
                sample_task.id,
                regular_user.id
            )

            assert success is True
            assert status_code == 200

    def test_delete_task_not_found(self, app, regular_user):
        """Test deleting non-existent task"""
        with app.app_context():
            success, error, status_code = TaskService.delete_task(99999, regular_user.id)

            assert success is False
            assert status_code == 404

    def test_get_task_statistics(self, app, regular_user, sample_tasks):
        """Test getting task statistics"""
        with app.app_context():
            success, stats, status_code = TaskService.get_user_task_statistics(regular_user.id)

            assert success is True
            assert status_code == 200
            assert 'total_tasks' in stats
            assert 'by_priority' in stats
            assert stats['total_tasks'] >= 3


class TestUserService:
    """Tests for UserService"""

    def test_get_all_users(self, app, regular_user, admin_user):
        """Test getting all users"""
        with app.app_context():
            success, result, status_code = UserService.get_all_users()

            assert success is True
            assert status_code == 200
            assert len(result['users']) >= 2
            assert result['pagination']['total'] >= 2

    def test_get_all_users_with_pagination(self, app, regular_user, admin_user):
        """Test getting all users with pagination"""
        with app.app_context():
            success, result, status_code = UserService.get_all_users(page=1, per_page=1)

            assert success is True
            assert status_code == 200
            assert len(result['users']) <= 1
            assert result['pagination']['total'] >= 2
            assert result['pagination']['per_page'] == 1

    def test_get_all_users_with_sorting(self, app, regular_user, admin_user):
        """Test getting all users with sorting"""
        with app.app_context():
            success, result, status_code = UserService.get_all_users(sort_by='username', sort_order='asc')

            assert success is True
            assert status_code == 200
            assert len(result['users']) >= 2

    def test_get_user_by_id_success(self, app, regular_user):
        """Test getting user by ID"""
        with app.app_context():
            success, user, status_code = UserService.get_user(regular_user.id)

            assert success is True
            assert user.id == regular_user.id
            assert status_code == 200

    def test_get_user_by_id_not_found(self, app):
        """Test getting non-existent user"""
        with app.app_context():
            success, error, status_code = UserService.get_user(99999)

            assert success is False
            assert status_code == 404

    def test_update_user_success(self, app, regular_user):
        """Test successful user update"""
        with app.app_context():
            success, user, status_code = UserService.update_user(
                regular_user.id,
                {'first_name': 'Updated'}
            )

            assert success is True
            assert user.first_name == 'Updated'
            assert status_code == 200

    def test_update_user_email(self, app, regular_user):
        """Test updating user email"""
        with app.app_context():
            success, user, status_code = UserService.update_user(
                regular_user.id,
                {'email': 'newemail@test.com'}
            )

            assert success is True
            assert user.email == 'newemail@test.com'
            assert status_code == 200

    def test_update_user_username(self, app, regular_user):
        """Test updating username"""
        with app.app_context():
            success, user, status_code = UserService.update_user(
                regular_user.id,
                {'username': 'newusername'}
            )

            assert success is True
            assert user.username == 'newusername'
            assert status_code == 200

    def test_update_user_invalid_username(self, app, regular_user):
        """Test updating with invalid username"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                regular_user.id,
                {'username': 'ab'}  # Too short
            )

            assert success is False
            assert status_code == 400

    def test_update_user_duplicate_email(self, app, regular_user, another_user):
        """Test updating with duplicate email"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                regular_user.id,
                {'email': another_user.email}
            )

            assert success is False
            assert status_code == 409

    def test_update_user_duplicate_username(self, app, regular_user, another_user):
        """Test updating with duplicate username"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                regular_user.id,
                {'username': another_user.username}
            )

            assert success is False
            assert status_code == 409

    def test_update_user_is_active(self, app, regular_user):
        """Test updating user is_active status"""
        with app.app_context():
            success, user, status_code = UserService.update_user(
                regular_user.id,
                {'is_active': False}
            )

            assert success is True
            assert user.is_active is False
            assert status_code == 200

    def test_delete_user_success(self, app, init_database):
        """Test successful user deletion"""
        with app.app_context():
            # Create a user to delete
            from app.models.user import Role, RoleType
            user_role = Role.query.filter_by(name=RoleType.USER.value).first()
            user = User(
                username='todelete',
                email='delete@test.com',
                role_id=user_role.id
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

            success, message, status_code = UserService.delete_user(user_id)

            assert success is True
            assert status_code == 200

    def test_delete_user_not_found(self, app, init_database):
        """Test deleting non-existent user"""
        with app.app_context():
            success, error, status_code = UserService.delete_user(99999)

            assert success is False
            assert status_code == 404

    def test_delete_admin_user(self, app, admin_user):
        """Test deleting admin user should fail"""
        with app.app_context():
            success, error, status_code = UserService.delete_user(admin_user.id)

            assert success is False
            assert status_code == 403
            assert 'admin' in error.lower()

    def test_update_user_role(self, app, regular_user):
        """Test updating user role"""
        with app.app_context():
            success, user, status_code = UserService.update_user(
                regular_user.id,
                {'role': 'admin'}
            )

            assert success is True
            assert user.role.name == RoleType.ADMIN.value
            assert status_code == 200

    def test_update_user_invalid_role(self, app, regular_user):
        """Test updating with invalid role"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                regular_user.id,
                {'role': 'invalid_role'}
            )

            assert success is False
            assert status_code == 400

    def test_update_user_not_found(self, app, init_database):
        """Test updating non-existent user"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                99999,
                {'first_name': 'Updated'}
            )

            assert success is False
            assert status_code == 404

    def test_update_user_invalid_email(self, app, regular_user):
        """Test updating user with invalid email"""
        with app.app_context():
            success, error, status_code = UserService.update_user(
                regular_user.id,
                {'email': 'invalid-email'}
            )

            assert success is False
            assert status_code == 400

    def test_get_user_statistics(self, app, regular_user, sample_tasks):
        """Test getting user task statistics"""
        with app.app_context():
            success, stats, status_code = TaskService.get_user_task_statistics(regular_user.id)

            assert success is True
            assert status_code == 200
            assert 'total_tasks' in stats


class TestTagService:
    """Tests for TagService"""

    def test_create_tag_success(self, app, init_database):
        """Test successful tag creation"""
        with app.app_context():
            success, tag, status_code = TagService.create_tag({
                'name': 'NewTag',
                'color': '#FF0000',
                'description': 'Test tag'
            })

            assert success is True
            assert tag.name == 'NewTag'
            assert status_code == 201

    def test_create_tag_missing_name(self, app, init_database):
        """Test tag creation without name"""
        with app.app_context():
            success, error, status_code = TagService.create_tag({
                'color': '#FF0000'
            })

            assert success is False
            assert status_code == 400

    def test_create_tag_duplicate_name(self, app, sample_tags):
        """Test tag creation with duplicate name"""
        with app.app_context():
            success, error, status_code = TagService.create_tag({
                'name': 'Work',
                'color': '#FF0000'
            })

            assert success is False
            assert status_code == 409

    def test_get_all_tags(self, app, sample_tags):
        """Test getting all tags"""
        with app.app_context():
            success, result, status_code = TagService.get_all_tags()

            assert success is True
            assert len(result['tags']) >= 3
            assert result['pagination']['total'] >= 3

    def test_get_tag_by_id_success(self, app, sample_tag):
        """Test getting tag by ID"""
        with app.app_context():
            success, tag, status_code = TagService.get_tag(sample_tag.id)

            assert success is True
            assert tag.id == sample_tag.id
            assert status_code == 200

    def test_get_tag_by_id_not_found(self, app, init_database):
        """Test getting non-existent tag"""
        with app.app_context():
            success, error, status_code = TagService.get_tag(99999)

            assert success is False
            assert status_code == 404

    def test_update_tag_success(self, app, sample_tag):
        """Test successful tag update"""
        with app.app_context():
            success, tag, status_code = TagService.update_tag(
                sample_tag.id,
                {'name': 'UpdatedTag', 'color': '#00FF00'}
            )

            assert success is True
            assert tag.name == 'UpdatedTag'
            assert status_code == 200

    def test_update_tag_not_found(self, app, init_database):
        """Test updating non-existent tag"""
        with app.app_context():
            success, error, status_code = TagService.update_tag(
                99999,
                {'name': 'Updated'}
            )

            assert success is False
            assert status_code == 404

    def test_update_tag_invalid_color(self, app, sample_tag):
        """Test updating tag with invalid color"""
        with app.app_context():
            success, error, status_code = TagService.update_tag(
                sample_tag.id,
                {'color': 'invalid-color'}
            )

            assert success is False
            assert status_code == 400

    def test_create_tag_invalid_color(self, app, init_database):
        """Test creating tag with invalid color"""
        with app.app_context():
            success, error, status_code = TagService.create_tag({
                'name': 'TestTag',
                'color': 'invalid'
            })

            assert success is False
            assert status_code == 400

    def test_delete_tag_success(self, app, sample_tag):
        """Test successful tag deletion"""
        with app.app_context():
            success, message, status_code = TagService.delete_tag(sample_tag.id)

            assert success is True
            assert status_code == 200

    def test_delete_tag_not_found(self, app, init_database):
        """Test deleting non-existent tag"""
        with app.app_context():
            success, error, status_code = TagService.delete_tag(99999)

            assert success is False
            assert status_code == 404
