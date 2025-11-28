from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from app import db
from app.models.user import User, Role, RoleType, RefreshToken
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_required_fields
)


class AuthService:
    """Servicio de autenticacion para gestion de usuarios"""

    @staticmethod
    def register_user(data):
        """
        Registrar un nuevo usuario
        Returns: (success, user_or_error_message, status_code)
        """
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}", 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return False, error_msg, 400

        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return False, error_msg, 400

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return False, error_msg, 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return False, "El nombre de usuario ya existe", 409

        if User.query.filter_by(email=email).first():
            return False, "El correo electronico ya existe", 409

        # Get user role (default)
        user_role = Role.query.filter_by(name=RoleType.USER.value).first()
        if not user_role:
            return False, "Error del sistema: Rol de usuario no encontrado", 500

        # Create new user
        new_user = User(
            username=username.strip(),
            email=email.strip().lower(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role_id=user_role.id
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return True, new_user, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error registering user: {str(e)}")
            return False, "Error al crear la cuenta de usuario", 500

    @staticmethod
    def login_user(data):
        """
        Autenticar usuario y generar tokens
        Returns: (success, tokens_or_error_message, status_code)
        """
        # Validate required fields
        required_fields = ['email', 'password']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}", 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return False, "Correo electronico o contrasena invalidos", 401

        if not user.is_active:
            return False, "La cuenta esta inactiva", 403

        # Generate tokens (convert user.id to string for JWT compliance)
        access_token = create_access_token(identity=str(user.id))
        refresh_token_jwt = create_refresh_token(identity=str(user.id))

        # Store refresh token in database
        expires_at = datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        refresh_token = RefreshToken(
            token=refresh_token_jwt,
            user_id=user.id,
            expires_at=expires_at
        )

        try:
            db.session.add(refresh_token)
            db.session.commit()

            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token_jwt,
                'user': user.to_dict()
            }

            return True, tokens, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error storing refresh token: {str(e)}")
            return False, "Error al generar tokens", 500

    @staticmethod
    def refresh_access_token(refresh_token_jwt):
        """
        Generar nuevo token de acceso desde token de refresco
        Returns: (success, token_or_error_message, status_code)
        """
        # Find refresh token in database
        refresh_token = RefreshToken.query.filter_by(token=refresh_token_jwt).first()

        if not refresh_token:
            return False, "Token de refresco invalido", 401

        if not refresh_token.is_valid:
            return False, "Token de refresco expirado o revocado", 401

        # Get user
        user = User.query.get(refresh_token.user_id)

        if not user or not user.is_active:
            return False, "Usuario no encontrado o inactivo", 401

        # Generate new access token (convert user.id to string for JWT compliance)
        access_token = create_access_token(identity=str(user.id))

        return True, {'access_token': access_token}, 200

    @staticmethod
    def logout_user(refresh_token_jwt):
        """
        Revocar token de refresco
        Returns: (success, message, status_code)
        """
        if not refresh_token_jwt:
            return False, "Se requiere token de refresco", 400

        # Find and revoke refresh token
        refresh_token = RefreshToken.query.filter_by(token=refresh_token_jwt).first()

        if refresh_token:
            try:
                refresh_token.revoke()
                return True, "Sesion cerrada con exito", 200
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error revoking token: {str(e)}")
                return False, "Error al cerrar sesion", 500

        return True, "Sesion cerrada con exito", 200

    @staticmethod
    def get_current_user(user_id):
        """
        Obtener usuario autenticado actual
        Returns: (success, user_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        if not user.is_active:
            return False, "La cuenta esta inactiva", 403

        return True, user, 200

    @staticmethod
    def change_password(user_id, data):
        """
        Cambiar contrasena de usuario
        Returns: (success, message, status_code)
        """
        required_fields = ['old_password', 'new_password']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}", 400

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        # Get user
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        # Verify old password
        if not user.check_password(old_password):
            return False, "La contrasena actual es incorrecta", 401

        # Validate new password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return False, error_msg, 400

        # Update password
        try:
            user.set_password(new_password)

            # Revoke all existing refresh tokens for security
            RefreshToken.query.filter_by(user_id=user.id, is_revoked=False).update({'is_revoked': True})

            db.session.commit()
            return True, "Contrasena cambiada con exito", 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error changing password: {str(e)}")
            return False, "Error al cambiar la contrasena", 500

    @staticmethod
    def cleanup_expired_tokens():
        """
        Eliminar tokens de refresco expirados de la base de datos
        Returns: number of tokens deleted
        """
        try:
            expired_tokens = RefreshToken.query.filter(
                RefreshToken.expires_at < datetime.utcnow()
            ).all()

            count = len(expired_tokens)

            for token in expired_tokens:
                db.session.delete(token)

            db.session.commit()
            return count
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error cleaning up tokens: {str(e)}")
            return 0
