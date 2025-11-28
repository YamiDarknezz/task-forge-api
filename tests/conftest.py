import pytest
from app import create_app, db
from app.models.user import User, Role, RoleType
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.tag import Tag
from flask_jwt_extended import create_access_token, create_refresh_token


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        # Create roles
        admin_role = Role(name=RoleType.ADMIN.value, description='Administrator')
        user_role = Role(name=RoleType.USER.value, description='Regular user')

        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database for each test"""
    with app.app_context():
        yield db

        # Clean up after each test
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            if table.name != 'roles':  # Keep roles
                db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def admin_user(app, init_database):
    """Create admin user"""
    with app.app_context():
        admin_role = Role.query.filter_by(name=RoleType.ADMIN.value).first()

        admin = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role_id=admin_role.id
        )
        admin.set_password('Admin123!')

        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

        # Refresh to avoid detached instance errors
        db.session.refresh(admin)

    # Return admin from new context
    with app.app_context():
        return User.query.get(admin_id)


@pytest.fixture
def regular_user(app, init_database):
    """Create regular user"""
    with app.app_context():
        user_role = Role.query.filter_by(name=RoleType.USER.value).first()

        user = User(
            username='testuser',
            email='user@test.com',
            first_name='Test',
            last_name='User',
            role_id=user_role.id
        )
        user.set_password('User123!')

        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Refresh to avoid detached instance errors
        db.session.refresh(user)

    # Return user from new context
    with app.app_context():
        return User.query.get(user_id)


@pytest.fixture
def another_user(app, init_database):
    """Create another regular user"""
    with app.app_context():
        user_role = Role.query.filter_by(name=RoleType.USER.value).first()

        user = User(
            username='anotheruser',
            email='another@test.com',
            first_name='Another',
            last_name='User',
            role_id=user_role.id
        )
        user.set_password('Another123!')

        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Refresh to avoid detached instance errors
        db.session.refresh(user)

    # Return user from new context
    with app.app_context():
        return User.query.get(user_id)


@pytest.fixture
def admin_token(app, admin_user):
    """Create admin access token"""
    with app.app_context():
        return create_access_token(identity=str(admin_user.id))


@pytest.fixture
def admin_refresh_token(app, admin_user):
    """Create admin refresh token"""
    from datetime import datetime, timedelta
    from app.models.user import RefreshToken
    
    with app.app_context():
        refresh_token_jwt = create_refresh_token(identity=str(admin_user.id))
        
        # Store in database
        expires_at = datetime.utcnow() + timedelta(days=30)
        refresh_token = RefreshToken(
            token=refresh_token_jwt,
            user_id=admin_user.id,
            expires_at=expires_at
        )
        db.session.add(refresh_token)
        db.session.commit()
        
        return refresh_token_jwt


@pytest.fixture
def user_token(app, regular_user):
    """Create user access token"""
    with app.app_context():
        return create_access_token(identity=str(regular_user.id))


@pytest.fixture
def user_refresh_token(app, regular_user):
    """Create user refresh token"""
    from datetime import datetime, timedelta
    from app.models.user import RefreshToken
    
    with app.app_context():
        refresh_token_jwt = create_refresh_token(identity=str(regular_user.id))
        
        # Store in database
        expires_at = datetime.utcnow() + timedelta(days=30)
        refresh_token = RefreshToken(
            token=refresh_token_jwt,
            user_id=regular_user.id,
            expires_at=expires_at
        )
        db.session.add(refresh_token)
        db.session.commit()
        
        return refresh_token_jwt


@pytest.fixture
def sample_task(app, regular_user):
    """Create sample task"""
    with app.app_context():
        task = Task(
            title='Test Task',
            description='This is a test task',
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.MEDIUM.value,
            user_id=regular_user.id
        )

        db.session.add(task)
        db.session.commit()
        task_id = task.id
        db.session.refresh(task)

    with app.app_context():
        return Task.query.get(task_id)


@pytest.fixture
def sample_tasks(app, regular_user):
    """Create multiple sample tasks"""
    with app.app_context():
        tasks = []

        # Create tasks with different statuses and priorities
        tasks.append(Task(
            title='Task 1 - Pending',
            description='Pending task',
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.HIGH.value,
            user_id=regular_user.id
        ))

        tasks.append(Task(
            title='Task 2 - In Progress',
            description='In progress task',
            status=TaskStatus.IN_PROGRESS.value,
            priority=TaskPriority.MEDIUM.value,
            user_id=regular_user.id
        ))

        tasks.append(Task(
            title='Task 3 - Completed',
            description='Completed task',
            status=TaskStatus.COMPLETED.value,
            priority=TaskPriority.LOW.value,
            user_id=regular_user.id
        ))

        for task in tasks:
            db.session.add(task)

        db.session.commit()

        return tasks


@pytest.fixture
def sample_tag(app, init_database):
    """Create sample tag"""
    with app.app_context():
        tag = Tag(
            name='TestTag',
            color='#FF5733',
            description='Test tag for individual tests'
        )

        db.session.add(tag)
        db.session.commit()
        tag_id = tag.id
        db.session.refresh(tag)

    with app.app_context():
        return Tag.query.get(tag_id)


@pytest.fixture
def sample_tags(app, init_database):
    """Create multiple sample tags"""
    with app.app_context():
        tags = []

        tags.append(Tag(name='Work', color='#FF5733', description='Work tasks'))
        tags.append(Tag(name='Personal', color='#33FF57', description='Personal tasks'))
        tags.append(Tag(name='Urgent', color='#FF3333', description='Urgent tasks'))

        for tag in tags:
            db.session.add(tag)

        db.session.commit()

        return tags


@pytest.fixture
def auth_headers(user_token):
    """Get authorization headers with user token"""
    return {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_auth_headers(admin_token):
    """Get authorization headers with admin token"""
    return {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
