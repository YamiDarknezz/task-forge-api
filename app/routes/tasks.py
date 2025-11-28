from flask import Blueprint, request
from app import limiter
from app.services.task_service import TaskService
from app.middleware.auth import current_user_required
from app.middleware.rbac import admin_required
from app.utils.helpers import success_response, error_response, get_pagination_params, get_sort_params, get_filter_params
from app.utils.export import export_to_csv, export_to_json, prepare_tasks_for_export

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@current_user_required
def get_tasks(current_user):
    """
    Obtener todas las tareas con filtros, paginacion y ordenamiento
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        description: Numero de pagina
        default: 1
      - in: query
        name: per_page
        type: integer
        description: Items por pagina
        default: 10
      - in: query
        name: sort_by
        type: string
        description: Campo de ordenamiento
        default: created_at
      - in: query
        name: sort_order
        type: string
        enum: [asc, desc]
        default: desc
      - in: query
        name: status
        type: string
        description: Filtrar por estado
      - in: query
        name: priority
        type: string
        description: Filtrar por prioridad
      - in: query
        name: tag_id
        type: integer
        description: Filtrar por ID de etiqueta
      - in: query
        name: tag_name
        type: string
        description: Filtrar por nombre de etiqueta
      - in: query
        name: search
        type: string
        description: Buscar en titulo y descripcion
      - in: query
        name: overdue
        type: boolean
        description: Filtrar tareas vencidas
      - in: query
        name: due_date_from
        type: string
        description: Filtrar por fecha de vencimiento desde (ISO format, e.g., 2024-01-01T00:00:00)
      - in: query
        name: due_date_to
        type: string
        description: Filtrar por fecha de vencimiento hasta (ISO format, e.g., 2024-12-31T23:59:59)
    responses:
      200:
        description: Lista de tareas
      401:
        description: No autorizado
    """
    # Get pagination params
    page, per_page, _ = get_pagination_params()

    # Get sorting params
    allowed_sort_fields = ['id', 'title', 'status', 'priority', 'due_date', 'created_at', 'updated_at']
    sort_by, sort_order = get_sort_params(allowed_sort_fields)

    # Get filters
    allowed_filters = ['status', 'priority', 'user_id', 'tag_id', 'tag_name', 'search', 'overdue', 'due_date_from', 'due_date_to']
    filters = get_filter_params(allowed_filters)

    # Get tasks
    success, result, status_code = TaskService.get_tasks(
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        filters=filters,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result, status_code=status_code)


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@current_user_required
def get_task(current_user, task_id):
    """
    Obtener una tarea individual
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
        description: ID de tarea
    responses:
      200:
        description: Detalles de la tarea
      403:
        description: Prohibido
      404:
        description: Tarea no encontrada
    """
    success, result, status_code = TaskService.get_task(
        task_id=task_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result.to_dict(), status_code=status_code)


@tasks_bp.route('', methods=['POST'])
@current_user_required
@limiter.limit("50 per hour")
def create_task(current_user):
    """
    Crear una nueva tarea
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Complete project documentation
            description:
              type: string
              example: Write comprehensive API documentation
            status:
              type: string
              enum: [pending, in_progress, completed, cancelled]
              default: pending
            priority:
              type: string
              enum: [low, medium, high, urgent]
              default: medium
            due_date:
              type: string
              format: date-time
              description: Due date in ISO format (e.g., 2024-12-31T23:59:59 or 2024-12-31T23:59:59Z)
              example: "2024-12-31T23:59:59"
            tags:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
    responses:
      201:
        description: Tarea creada con exito
      400:
        description: Error de validacion
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = TaskService.create_task(
        user_id=current_user.id,
        data=data
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Tarea creada con exito",
        status_code=status_code
    )


@tasks_bp.route('/<int:task_id>', methods=['PUT', 'PATCH'])
@current_user_required
def update_task(current_user, task_id):
    """
    Actualizar una tarea
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
        description: ID de tarea
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [pending, in_progress, completed, cancelled]
            priority:
              type: string
              enum: [low, medium, high, urgent]
            due_date:
              type: string
              format: date-time
              description: Due date in ISO format (e.g., 2024-12-31T23:59:59 or 2024-12-31T23:59:59Z)
              example: "2024-12-31T23:59:59"
            tags:
              type: array
              items:
                type: integer
    responses:
      200:
        description: Tarea actualizada con exito
      403:
        description: Prohibido
      404:
        description: Tarea no encontrada
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = TaskService.update_task(
        task_id=task_id,
        user_id=current_user.id,
        data=data,
        is_admin=current_user.is_admin
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Tarea actualizada con exito",
        status_code=status_code
    )


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@current_user_required
def delete_task(current_user, task_id):
    """
    Eliminar una tarea
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
        description: ID de tarea
    responses:
      200:
        description: Tarea eliminada con exito
      403:
        description: Prohibido
      404:
        description: Tarea no encontrada
    """
    success, result, status_code = TaskService.delete_task(
        task_id=task_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(message=result, status_code=status_code)


@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@current_user_required
def mark_task_completed(current_user, task_id):
    """
    Marcar tarea como completada
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
        description: ID de tarea
    responses:
      200:
        description: Tarea marcada como completada
      403:
        description: Prohibido
      404:
        description: Tarea no encontrada
    """
    success, result, status_code = TaskService.mark_task_completed(
        task_id=task_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Tarea marcada como completada",
        status_code=status_code
    )


@tasks_bp.route('/statistics', methods=['GET'])
@current_user_required
def get_task_statistics(current_user):
    """
    Obtener estadisticas de tareas para el usuario actual
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    responses:
      200:
        description: Estadisticas de tareas
      404:
        description: Usuario no encontrado
    """
    success, result, status_code = TaskService.get_user_task_statistics(current_user.id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result, status_code=status_code)


@tasks_bp.route('/export', methods=['GET'])
@current_user_required
def export_tasks(current_user):
    """
    Exportar tareas a CSV o JSON
    ---
    tags:
      - Tareas
    security:
      - Bearer: []
    parameters:
      - in: query
        name: format
        type: string
        enum: [csv, json]
        default: csv
        description: Formato de exportacion
      - in: query
        name: status
        type: string
        description: Filtrar por estado
      - in: query
        name: priority
        type: string
        description: Filtrar por prioridad
    responses:
      200:
        description: Archivo exportado
      401:
        description: No autorizado
    """
    export_format = request.args.get('format', 'csv').lower()

    # Get filters
    allowed_filters = ['status', 'priority', 'tag_id', 'overdue']
    filters = get_filter_params(allowed_filters)

    # Get all tasks (no pagination for export)
    success, result, status_code = TaskService.get_tasks(
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        filters=filters,
        page=1,
        per_page=10000  # Get all tasks
    )

    if not success:
        return error_response(result, status_code=status_code)

    tasks = [task for task in result['tasks']]

    if not tasks:
        return error_response("No hay tareas para exportar", status_code=404)

    # Convert task dicts back to objects for export preparation
    from app.models.task import Task
    task_objects = Task.query.filter(Task.id.in_([t['id'] for t in tasks])).all()

    # Prepare data for export
    export_data = prepare_tasks_for_export(task_objects)

    # Export based on format
    if export_format == 'json':
        return export_to_json(export_data, filename='tasks.json')
    else:
        return export_to_csv(export_data, filename='tasks.csv')
