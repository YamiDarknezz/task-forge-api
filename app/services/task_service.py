from datetime import datetime
from flask import current_app
from sqlalchemy import or_, and_
from app import db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.tag import Tag
from app.models.user import User
from app.utils.validators import (
    validate_required_fields,
    validate_string_length,
    validate_enum_value,
    validate_date_format
)
from app.utils.helpers import paginate, apply_sorting, parse_date


class TaskService:
    """Servicio para gestion de tareas"""

    @staticmethod
    def create_task(user_id, data):
        """
        Crear una nueva tarea
        Returns: (success, task_or_error_message, status_code)
        """
        # Validate required fields
        required_fields = ['title']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}", 400

        title = data.get('title')
        description = data.get('description', '')
        status = data.get('status', 'pending')
        priority = data.get('priority', 'medium')
        due_date_str = data.get('due_date')
        tag_ids = data.get('tags', [])

        # Validate title
        is_valid, error_msg = validate_string_length(title, min_length=1, max_length=200, field_name="Titulo")
        if not is_valid:
            return False, error_msg, 400

        # Validate description (optional)
        if description:
            is_valid, error_msg = validate_string_length(description, max_length=5000, field_name="Descripcion")
            if not is_valid:
                return False, error_msg, 400

        # Validate status
        is_valid, error_msg = validate_enum_value(status, TaskStatus, "Estado")
        if not is_valid:
            return False, error_msg, 400

        # Validate priority
        is_valid, error_msg = validate_enum_value(priority, TaskPriority, "Prioridad")
        if not is_valid:
            return False, error_msg, 400

        # Parse due date
        due_date = None
        if due_date_str:
            is_valid, error_msg, due_date = validate_date_format(due_date_str)
            if not is_valid:
                return False, error_msg, 400

        # Create task
        new_task = Task(
            title=title.strip(),
            description=description.strip() if description else None,
            status=status,
            priority=priority,
            due_date=due_date,
            user_id=user_id
        )

        try:
            # Add to session first so it's bound
            db.session.add(new_task)

            # Add tags if provided (after task is in session)
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in tags:
                    new_task.add_tag(tag)

            db.session.commit()
            return True, new_task, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating task: {str(e)}")
            return False, "Error al crear la tarea", 500

    @staticmethod
    def get_task(task_id, user_id, is_admin=False):
        """
        Obtener una tarea individual
        Returns: (success, task_or_error_message, status_code)
        """
        task = Task.query.get(task_id)

        if not task:
            return False, "Tarea no encontrada", 404

        # Check permissions
        if not is_admin and task.user_id != user_id:
            return False, "No tienes permiso para ver esta tarea", 403

        return True, task, 200

    @staticmethod
    def get_tasks(user_id, is_admin=False, filters=None, page=1, per_page=10, sort_by='created_at', sort_order='desc'):
        """
        Obtener tareas con filtrado, paginacion y ordenamiento
        Returns: (success, result_or_error_message, status_code)
        """
        # Build base query
        if is_admin:
            query = Task.query
        else:
            query = Task.query.filter_by(user_id=user_id)

        # Apply filters
        if filters:
            # Filter by status
            if 'status' in filters:
                query = query.filter(Task.status == filters['status'])

            # Filter by priority
            if 'priority' in filters:
                query = query.filter(Task.priority == filters['priority'])

            # Filter by user (admin only)
            if is_admin and 'user_id' in filters:
                query = query.filter(Task.user_id == int(filters['user_id']))

            # Filter by tag
            if 'tag_id' in filters:
                tag_id = int(filters['tag_id'])
                query = query.join(Task.tags).filter(Tag.id == tag_id)

            # Filter by tag name
            if 'tag_name' in filters:
                tag_name = filters['tag_name']
                query = query.join(Task.tags).filter(Tag.name.ilike(f'%{tag_name}%'))

            # Filter by overdue
            if 'overdue' in filters and filters['overdue'].lower() == 'true':
                query = query.filter(
                    and_(
                        Task.due_date < datetime.utcnow(),
                        Task.status != TaskStatus.COMPLETED.value
                    )
                )

            # Filter by date range
            if 'due_date_from' in filters:
                due_date_from = parse_date(filters['due_date_from'])
                if due_date_from:
                    query = query.filter(Task.due_date >= due_date_from)

            if 'due_date_to' in filters:
                due_date_to = parse_date(filters['due_date_to'])
                if due_date_to:
                    query = query.filter(Task.due_date <= due_date_to)

            # Search by title or description
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
                    )
                )

        # Apply sorting
        query = apply_sorting(query, Task, sort_by, sort_order)

        # Paginate
        tasks, pagination_meta = paginate(query, page, per_page)

        result = {
            'tasks': [task.to_dict() for task in tasks],
            'pagination': pagination_meta
        }

        return True, result, 200

    @staticmethod
    def update_task(task_id, user_id, data, is_admin=False):
        """
        Actualizar una tarea
        Returns: (success, task_or_error_message, status_code)
        """
        task = Task.query.get(task_id)

        if not task:
            return False, "Tarea no encontrada", 404

        # Check permissions
        if not is_admin and task.user_id != user_id:
            return False, "No tienes permiso para actualizar esta tarea", 403

        # Update fields
        if 'title' in data:
            is_valid, error_msg = validate_string_length(data['title'], min_length=1, max_length=200, field_name="Titulo")
            if not is_valid:
                return False, error_msg, 400
            task.title = data['title'].strip()

        if 'description' in data:
            description = data['description']
            if description:
                is_valid, error_msg = validate_string_length(description, max_length=5000, field_name="Descripcion")
                if not is_valid:
                    return False, error_msg, 400
            task.description = description.strip() if description else None

        if 'status' in data:
            is_valid, error_msg = validate_enum_value(data['status'], TaskStatus, "Estado")
            if not is_valid:
                return False, error_msg, 400
            task.status = data['status']

            # Auto-set completed_at when status changes to completed
            if task.status == TaskStatus.COMPLETED.value and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif task.status != TaskStatus.COMPLETED.value:
                task.completed_at = None

        if 'priority' in data:
            is_valid, error_msg = validate_enum_value(data['priority'], TaskPriority, "Prioridad")
            if not is_valid:
                return False, error_msg, 400
            task.priority = data['priority']

        if 'due_date' in data:
            due_date_str = data['due_date']
            if due_date_str:
                is_valid, error_msg, due_date = validate_date_format(due_date_str)
                if not is_valid:
                    return False, error_msg, 400
                task.due_date = due_date
            else:
                task.due_date = None

        # Update tags
        if 'tags' in data:
            tag_ids = data['tags']
            # Clear existing tags by directly deleting from association table
            from app.models.task import task_tags
            db.session.execute(
                task_tags.delete().where(task_tags.c.task_id == task_id)
            )
            # Add new tags
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in tags:
                    task.add_tag(tag)

        try:
            db.session.commit()
            return True, task, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating task: {str(e)}")
            return False, "Error al actualizar la tarea", 500

    @staticmethod
    def delete_task(task_id, user_id, is_admin=False):
        """
        Eliminar una tarea
        Returns: (success, message, status_code)
        """
        task = Task.query.get(task_id)

        if not task:
            return False, "Tarea no encontrada", 404

        # Check permissions
        if not is_admin and task.user_id != user_id:
            return False, "No tienes permiso para eliminar esta tarea", 403

        try:
            db.session.delete(task)
            db.session.commit()
            return True, "Tarea eliminada con exito", 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting task: {str(e)}")
            return False, "Error al eliminar la tarea", 500

    @staticmethod
    def mark_task_completed(task_id, user_id, is_admin=False):
        """
        Marcar una tarea como completada
        Returns: (success, task_or_error_message, status_code)
        """
        task = Task.query.get(task_id)

        if not task:
            return False, "Tarea no encontrada", 404

        # Check permissions
        if not is_admin and task.user_id != user_id:
            return False, "No tienes permiso para actualizar esta tarea", 403

        try:
            task.mark_completed()
            db.session.commit()
            return True, task, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error marking task as completed: {str(e)}")
            return False, "Error al marcar la tarea como completada", 500

    @staticmethod
    def get_user_task_statistics(user_id):
        """
        Obtener estadisticas de tareas para un usuario
        Returns: (success, stats_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        tasks = Task.query.filter_by(user_id=user_id).all()

        stats = {
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t.status == TaskStatus.COMPLETED.value]),
            'pending_tasks': len([t for t in tasks if t.status == TaskStatus.PENDING.value]),
            'in_progress_tasks': len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS.value]),
            'cancelled_tasks': len([t for t in tasks if t.status == TaskStatus.CANCELLED.value]),
            'overdue_tasks': len([t for t in tasks if t.is_overdue]),
            'by_priority': {
                'low': len([t for t in tasks if t.priority == TaskPriority.LOW.value]),
                'medium': len([t for t in tasks if t.priority == TaskPriority.MEDIUM.value]),
                'high': len([t for t in tasks if t.priority == TaskPriority.HIGH.value]),
                'urgent': len([t for t in tasks if t.priority == TaskPriority.URGENT.value])
            }
        }

        return True, stats, 200
