from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app import limiter
from app.services.auth_service import AuthService
from app.middleware.auth import current_user_required, refresh_token_required
from app.utils.helpers import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
      - Autenticacion
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: johndoe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecurePass123
            first_name:
              type: string
              example: John
            last_name:
              type: string
              example: Doe
    responses:
      201:
        description: Usuario registrado con exito
      400:
        description: Error de validacion
      409:
        description: El usuario ya existe
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = AuthService.register_user(data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result.to_dict(),
        message="Usuario registrado con exito",
        status_code=status_code
    )


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """
    Iniciar sesion y obtener token de acceso
    ---
    tags:
      - Autenticacion
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecurePass123
    responses:
      200:
        description: Inicio de sesion exitoso
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
                user:
                  type: object
      401:
        description: Credenciales invalidas
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = AuthService.login_user(data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result,
        message="Inicio de sesion exitoso",
        status_code=status_code
    )


@auth_bp.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh():
    """
    Refrescar token de acceso
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    responses:
      200:
        description: Token refrescado con exito
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                access_token:
                  type: string
      401:
        description: Token de refresco invalido o expirado
    """
    # Get refresh token from Authorization header
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return error_response("Encabezado de autorizacion invalido", status_code=401)

    refresh_token = auth_header.replace('Bearer ', '')

    success, result, status_code = AuthService.refresh_access_token(refresh_token)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        data=result,
        message="Token refrescado con exito",
        status_code=status_code
    )


@auth_bp.route('/logout', methods=['POST'])
@current_user_required
def logout(current_user):
    """
    Cerrar sesion y revocar token de refresco
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            refresh_token:
              type: string
              description: Token de refresco a revocar
    responses:
      200:
        description: Sesion cerrada con exito
      401:
        description: No autorizado
    """
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token')

    success, result, status_code = AuthService.logout_user(refresh_token)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        message=result,
        status_code=status_code
    )


@auth_bp.route('/me', methods=['GET'])
@current_user_required
def get_current_user(current_user):
    """
    Obtener perfil del usuario actual
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil del usuario actual
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
      401:
        description: No autorizado
    """
    return success_response(data=current_user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@current_user_required
@limiter.limit("3 per hour")
def change_password(current_user):
    """
    Cambiar contrasena de usuario
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
              example: OldPass123
            new_password:
              type: string
              example: NewPass123
    responses:
      200:
        description: Contrasena cambiada con exito
      401:
        description: Contrasena anterior invalida
    """
    data = request.get_json()

    if not data:
        return error_response("No se proporcionaron datos", status_code=400)

    success, result, status_code = AuthService.change_password(current_user.id, data)

    if not success:
        return error_response(result, status_code=status_code)

    return success_response(
        message=result,
        status_code=status_code
    )
