from flask import Blueprint, request
from app import limiter
from app.services.tag_service import TagService
from app.middleware.auth import current_user_required
from app.middleware.rbac import admin_required
from app.utils.helpers import success_response, error_response, get_pagination_params, get_sort_params

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
@current_user_required
def get_all_tags(current_user):
    """
    Obtener todas las etiquetas
    ---
    tags:
      - Etiquetas
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
        default: 50
      - in: query
        name: sort_by
        type: string
        description: Campo de ordenamiento
        default: name
      - in: query
        name: sort_order
        type: string
        enum: [asc, desc]
        default: asc
    responses:
      200:
        description: Lista de etiquetas
      401:
        description: No autorizado
    """
    # Get pagination params
    page, per_page, _ = get_pagination_params()

    # Get sorting params
    allowed_sort_fields = ['id', 'name', 'created_at', 'updated_at']
    sort_by, sort_order = get_sort_params(allowed_sort_fields)

    success, result, status_code = TagService.get_all_tags(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result, status_code=status_code)


@tags_bp.route('/<int:tag_id>', methods=['GET'])
@current_user_required
def get_tag(current_user, tag_id):
    """
    Obtener una etiqueta individual
    ---
    tags:
      - Etiquetas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tag_id
        type: integer
        required: true
        description: ID de etiqueta
    responses:
      200:
        description: Detalles de la etiqueta
      404:
        description: Etiqueta no encontrada
    """
    success, result, status_code = TagService.get_tag(tag_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result.to_dict(), status_code=status_code)


@tags_bp.route('', methods=['POST'])
@current_user_required
@limiter.limit("20 per hour")
def create_tag(current_user):
    """
    Crear una nueva etiqueta
    ---
    tags:
      - Etiquetas
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Work
            color:
              type: string
              pattern: '^#[0-9A-Fa-f]{6}$'
              example: '#FF5733'
              default: '#808080'
            description:
              type: string
              example: Work-related tasks
    responses:
      201:
        description: Etiqueta creada con exito
      400:
        description: Error de validacion
      409:
        description: La etiqueta ya existe
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = TagService.create_tag(data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Etiqueta creada con exito",
        status_code=status_code
    )


@tags_bp.route('/<int:tag_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_tag(current_user, tag_id):
    """
    Actualizar una etiqueta (Solo admin)
    ---
    tags:
      - Etiquetas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tag_id
        type: integer
        required: true
        description: ID de etiqueta
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
              example: Work
            color:
              type: string
              pattern: '^#[0-9A-Fa-f]{6}$'
              example: '#FF5733'
            description:
              type: string
              example: Work-related tasks
    responses:
      200:
        description: Etiqueta actualizada con exito
      403:
        description: Prohibido
      404:
        description: Etiqueta no encontrada
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = TagService.update_tag(tag_id, data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Etiqueta actualizada con exito",
        status_code=status_code
    )


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@admin_required
def delete_tag(current_user, tag_id):
    """
    Eliminar una etiqueta (Solo admin)
    ---
    tags:
      - Etiquetas
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tag_id
        type: integer
        required: true
        description: ID de etiqueta
    responses:
      200:
        description: Etiqueta eliminada con exito
      403:
        description: Prohibido
      404:
        description: Etiqueta no encontrada
    """
    success, result, status_code = TagService.delete_tag(tag_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(message=result, status_code=status_code)
