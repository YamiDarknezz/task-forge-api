from flask import Blueprint, request
from app.services.user_service import UserService
from app.middleware.auth import current_user_required
from app.middleware.rbac import admin_required
from app.utils.helpers import success_response, error_response, get_pagination_params, get_sort_params

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@admin_required
def get_all_users(current_user):
    """
    Obtener todos los usuarios (Solo admin)
    ---
    tags:
      - Usuarios
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
    responses:
      200:
        description: Lista de usuarios
      403:
        description: Prohibido - Acceso de administrador requerido
    """
    # Get pagination params
    page, per_page, _ = get_pagination_params()

    # Get sorting params
    allowed_sort_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
    sort_by, sort_order = get_sort_params(allowed_sort_fields)

    success, result, status_code = UserService.get_all_users(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result, status_code=status_code)


@users_bp.route('/<int:user_id>', methods=['GET'])
@current_user_required
def get_user(current_user, user_id):
    """
    Obtener un usuario individual (Solo admin)
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID de usuario
    responses:
      200:
        description: Detalles del usuario
      403:
        description: Prohibido
      404:
        description: Usuario no encontrado
    """
    # Check permissions
    if not current_user.is_admin and current_user.id != user_id:
        return error_response("Prohibido", status_code=403)

    success, result, status_code = UserService.get_user(user_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(data=result.to_dict(), status_code=status_code)


@users_bp.route('/<int:user_id>', methods=['PUT', 'PATCH'])
@current_user_required
def update_user(current_user, user_id):
    """
    Actualizar informacion de usuario (Solo admin)
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID de usuario
      - in: body
        name: body
        schema:
          type: object
          properties:
            first_name:
              type: string
              example: John
            last_name:
              type: string
              example: Doe
            is_active:
              type: boolean
              example: true
            role:
              type: string
              enum: [admin, user]
              example: user
    responses:
      200:
        description: Usuario actualizado con exito
      403:
        description: Prohibido
      404:
        description: Usuario no encontrado
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    # Check permissions
    if not current_user.is_admin and current_user.id != user_id:
        return error_response("Prohibido", status_code=403)

    # Filter sensitive fields for non-admins
    if not current_user.is_admin:
        if 'role' in data:
            del data['role']
        if 'is_active' in data:
            del data['is_active']

    success, result, status_code = UserService.update_user(user_id, data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Usuario actualizado con exito",
        status_code=status_code
    )


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """
    Eliminar un usuario (Solo admin)
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID de usuario
    responses:
      200:
        description: Usuario eliminado con exito
      403:
        description: Prohibido - No se pueden eliminar usuarios administradores
      404:
        description: Usuario no encontrado
    """
    success, result, status_code = UserService.delete_user(user_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(message=result, status_code=status_code)


@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(current_user, user_id):
    """
    Desactivar cuenta de usuario (Solo admin)
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID de usuario
    responses:
      200:
        description: Usuario desactivado con exito
      403:
        description: Prohibido
      404:
        description: Usuario no encontrado
    """
    success, result, status_code = UserService.deactivate_user(user_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Usuario desactivado con exito",
        status_code=status_code
    )


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(current_user, user_id):
    """
    Activar cuenta de usuario (Solo admin)
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID de usuario
    responses:
      200:
        description: Usuario activado con exito
      403:
        description: Prohibido
      404:
        description: Usuario no encontrado
    """
    success, result, status_code = UserService.activate_user(user_id)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Usuario activado con exito",
        status_code=status_code
    )
