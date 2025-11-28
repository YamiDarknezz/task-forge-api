from flask import Blueprint, current_app
from app.utils.helpers import success_response
from app import db
from datetime import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificacion de salud
    ---
    tags:
      - Salud
    responses:
      200:
        description: La API esta saludable
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
                timestamp:
                  type: string
                  example: 2024-01-15T10:30:00
                app_name:
                  type: string
                  example: TaskForge API
                version:
                  type: string
                  example: 1.0.0
                database:
                  type: string
                  example: connected
    """
    # Check database connection
    db_status = "connected"
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_status = "disconnected"

    data = {
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'app_name': current_app.config.get('APP_NAME', 'TaskForge API'),
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'database': db_status
    }

    return success_response(data=data)
