import pytest
from datetime import datetime, timedelta
from app.models.user import User, Role, RoleType, RefreshToken
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.tag import Tag
from app import db


class TestUserModel:
    """Tests for User model"""

    def test_user_creation(self, app, init_database):
        """Test creating a user"""
        with app.app_context():
            user_role = Role.query.filter_by(name=RoleType.USER.value).first()
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role_id=user_role.id
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'

    def test_user_password_hashing(self, app, init_database):
        """Test password is hashed"""
        with app.app_context():
            user_role = Role.query.filter_by(name=RoleType.USER.value).first()
            user = User(
                username='testuser',
                email='test@example.com',
                role_id=user_role.id
            )
            user.set_password('Password123')

            assert user.password_hash != 'Password123'
            assert user.check_password('Password123') is True
            assert user.check_password('WrongPassword') is False

    def test_user_is_admin_property(self, app, admin_user, regular_user):
        """Test is_admin property"""
        with app.app_context():
            admin = User.query.get(admin_user.id)
            user = User.query.get(regular_user.id)

            assert admin.is_admin is True
            assert user.is_admin is False

    def test_user_full_name_property(self, app, regular_user):
        """Test full_name property"""
        with app.app_context():
            user = User.query.get(regular_user.id)
            assert user.full_name == 'Test User'

    def test_user_full_name_fallback(self, app, init_database):
        """Test full_name falls back to username"""
        with app.app_context():
            user_role = Role.query.filter_by(name=RoleType.USER.value).first()
            user = User(
                username='testuser',
                email='test@example.com',
                role_id=user_role.id
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.commit()

            assert user.full_name == 'testuser'

    def test_user_to_dict(self, app, regular_user):
        """Test user to_dict method"""
        with app.app_context():
            user = User.query.get(regular_user.id)
            data = user.to_dict()

            assert data['id'] == user.id
            assert data['username'] == 'testuser'
            assert data['email'] == 'user@test.com'
            assert 'role' in data

    def test_user_to_dict_without_role(self, app, regular_user):
        """Test user to_dict without role"""
        with app.app_context():
            user = User.query.get(regular_user.id)
            data = user.to_dict(include_role=False)

            assert 'role' not in data


class TestRoleModel:
    """Tests for Role model"""

    def test_role_creation(self, app):
        """Test role exists"""
        with app.app_context():
            user_role = Role.query.filter_by(name=RoleType.USER.value).first()
            admin_role = Role.query.filter_by(name=RoleType.ADMIN.value).first()

            assert user_role is not None
            assert admin_role is not None

    def test_role_to_dict(self, app):
        """Test role to_dict method"""
        with app.app_context():
            role = Role.query.filter_by(name=RoleType.USER.value).first()
            data = role.to_dict()

            assert data['name'] == 'user'
            assert 'description' in data


class TestRefreshTokenModel:
    """Tests for RefreshToken model"""

    def test_refresh_token_creation(self, app, regular_user):
        """Test creating a refresh token"""
        with app.app_context():
            expires_at = datetime.utcnow() + timedelta(days=30)
            token = RefreshToken(
                token='test_token_123',
                user_id=regular_user.id,
                expires_at=expires_at
            )
            db.session.add(token)
            db.session.commit()

            assert token.id is not None
            assert token.is_revoked is False

    def test_refresh_token_is_expired(self, app, regular_user):
        """Test is_expired property"""
        with app.app_context():
            # Expired token
            expired_token = RefreshToken(
                token='expired_token',
                user_id=regular_user.id,
                expires_at=datetime.utcnow() - timedelta(days=1)
            )
            db.session.add(expired_token)

            # Valid token
            valid_token = RefreshToken(
                token='valid_token',
                user_id=regular_user.id,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(valid_token)
            db.session.commit()

            assert expired_token.is_expired is True
            assert valid_token.is_expired is False

    def test_refresh_token_is_valid(self, app, regular_user):
        """Test is_valid property"""
        with app.app_context():
            token = RefreshToken(
                token='test_token',
                user_id=regular_user.id,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(token)
            db.session.commit()

            assert token.is_valid is True

            token.revoke()
            assert token.is_valid is False


class TestTaskModel:
    """Tests for Task model"""

    def test_task_creation(self, app, regular_user):
        """Test creating a task"""
        with app.app_context():
            task = Task(
                title='Test Task',
                description='Test description',
                user_id=regular_user.id
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.status == TaskStatus.PENDING.value
            assert task.priority == TaskPriority.MEDIUM.value

    def test_task_is_overdue(self, app, regular_user):
        """Test is_overdue property"""
        with app.app_context():
            # Overdue task
            overdue_task = Task(
                title='Overdue Task',
                user_id=regular_user.id,
                due_date=datetime.utcnow() - timedelta(days=1)
            )
            db.session.add(overdue_task)

            # Not overdue task
            future_task = Task(
                title='Future Task',
                user_id=regular_user.id,
                due_date=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(future_task)
            db.session.commit()

            assert overdue_task.is_overdue is True
            assert future_task.is_overdue is False

    def test_task_is_completed(self, app, regular_user):
        """Test is_completed property"""
        with app.app_context():
            task = Task(
                title='Test Task',
                user_id=regular_user.id,
                status=TaskStatus.COMPLETED.value
            )
            db.session.add(task)
            db.session.commit()

            assert task.is_completed is True

    def test_task_mark_completed(self, app, regular_user):
        """Test marking task as completed"""
        with app.app_context():
            task = Task(
                title='Test Task',
                user_id=regular_user.id
            )
            db.session.add(task)
            db.session.commit()

            task.mark_completed()
            assert task.status == TaskStatus.COMPLETED.value
            assert task.completed_at is not None

    def test_task_add_tag(self, app, regular_user, sample_tag):
        """Test adding tag to task"""
        with app.app_context():
            task = Task(
                title='Test Task',
                user_id=regular_user.id
            )
            db.session.add(task)
            db.session.commit()

            tag = Tag.query.get(sample_tag.id)
            task.add_tag(tag)
            db.session.commit()

            assert task.has_tag(tag) is True

    def test_task_remove_tag(self, app, regular_user, sample_tag):
        """Test removing tag from task"""
        with app.app_context():
            task = Task(
                title='Test Task',
                user_id=regular_user.id
            )
            db.session.add(task)
            db.session.commit()

            tag = Tag.query.get(sample_tag.id)
            task.add_tag(tag)
            db.session.commit()

            task.remove_tag(tag)
            db.session.commit()

            assert task.has_tag(tag) is False

    def test_task_to_dict(self, app, sample_task):
        """Test task to_dict method"""
        with app.app_context():
            task = Task.query.get(sample_task.id)
            data = task.to_dict()

            assert data['id'] == task.id
            assert data['title'] == task.title
            assert data['status'] == task.status
            assert data['priority'] == task.priority


class TestTagModel:
    """Tests for Tag model"""

    def test_tag_creation(self, app, init_database):
        """Test creating a tag"""
        with app.app_context():
            tag = Tag(
                name='TestTag',
                color='#FF0000',
                description='Test description'
            )
            db.session.add(tag)
            db.session.commit()

            assert tag.id is not None
            assert tag.name == 'TestTag'

    def test_tag_task_count(self, app, regular_user, sample_tag):
        """Test tag task_count property"""
        with app.app_context():
            tag = Tag.query.get(sample_tag.id)

            # Create tasks with this tag
            task1 = Task(title='Task 1', user_id=regular_user.id)
            task2 = Task(title='Task 2', user_id=regular_user.id)
            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()

            task1.add_tag(tag)
            task2.add_tag(tag)
            db.session.commit()

            assert tag.task_count == 2

    def test_tag_to_dict(self, app, sample_tag):
        """Test tag to_dict method"""
        with app.app_context():
            tag = Tag.query.get(sample_tag.id)
            data = tag.to_dict()

            assert data['id'] == tag.id
            assert data['name'] == tag.name
            assert data['color'] == tag.color
            assert 'task_count' in data
