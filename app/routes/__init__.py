from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp
from app.routes.users import users_bp
from app.routes.tags import tags_bp

__all__ = [
    'health_bp',
    'auth_bp',
    'tasks_bp',
    'users_bp',
    'tags_bp'
]
