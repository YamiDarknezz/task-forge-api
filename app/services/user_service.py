from flask import current_app
from app import db
from app.models.user import User, Role, RoleType
from app.utils.helpers import paginate, apply_sorting
from app.utils.validators import validate_email, validate_username


class UserService:
    """Servicio para gestion de usuarios (Solo admin)"""

    @staticmethod
    def get_all_users(page=1, per_page=10, sort_by='created_at', sort_order='desc'):
        """
        Obtener todos los usuarios con paginacion
        Returns: (success, result_or_error_message, status_code)
        """
        query = User.query

        # Apply sorting
        query = apply_sorting(query, User, sort_by, sort_order)

        # Paginate
        users, pagination_meta = paginate(query, page, per_page)

        result = {
            'users': [user.to_dict() for user in users],
            'pagination': pagination_meta
        }

        return True, result, 200

    @staticmethod
    def get_user(user_id):
        """
        Obtener un usuario individual
        Returns: (success, user_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        return True, user, 200

    @staticmethod
    def update_user(user_id, data):
        """
        Actualizar informacion de usuario (Solo admin)
        Returns: (success, user_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        # Update email
        if 'email' in data:
            email = data['email']
            is_valid, error_msg = validate_email(email)
            if not is_valid:
                return False, error_msg, 400

            # Check for duplicate email
            existing_user = User.query.filter_by(email=email.strip().lower()).first()
            if existing_user and existing_user.id != user_id:
                return False, "El correo electronico ya esta en uso", 409

            user.email = email.strip().lower()

        # Update username
        if 'username' in data:
            username = data['username']
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                return False, error_msg, 400

            # Check for duplicate username
            existing_user = User.query.filter_by(username=username.strip()).first()
            if existing_user and existing_user.id != user_id:
                return False, "El nombre de usuario ya esta en uso", 409

            user.username = username.strip()

        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()

        if 'last_name' in data:
            user.last_name = data['last_name'].strip()

        if 'is_active' in data:
            user.is_active = bool(data['is_active'])

        if 'role' in data:
            role_name = data['role']
            try:
                role_type = RoleType(role_name)
                role = Role.query.filter_by(name=role_type.value).first()
                if role:
                    user.role_id = role.id
                else:
                    return False, "Rol invalido", 400
            except ValueError:
                return False, "Rol invalido", 400

        try:
            db.session.commit()
            return True, user, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            return False, "Error al actualizar usuario", 500

    @staticmethod
    def delete_user(user_id):
        """
        Eliminar un usuario (Solo admin)
        Returns: (success, message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        if user.is_admin:
            return False, "No se pueden eliminar usuarios administradores", 403

        try:
            db.session.delete(user)
            db.session.commit()
            return True, "Usuario eliminado con exito", 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user: {str(e)}")
            return False, "Error al eliminar usuario", 500

    @staticmethod
    def deactivate_user(user_id):
        """
        Desactivar cuenta de usuario
        Returns: (success, user_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        if user.is_admin:
            return False, "No se pueden desactivar usuarios administradores", 403

        try:
            user.is_active = False
            db.session.commit()
            return True, user, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deactivating user: {str(e)}")
            return False, "Error al desactivar usuario", 500

    @staticmethod
    def activate_user(user_id):
        """
        Activar cuenta de usuario
        Returns: (success, user_or_error_message, status_code)
        """
        user = User.query.get(user_id)

        if not user:
            return False, "Usuario no encontrado", 404

        try:
            user.is_active = True
            db.session.commit()
            return True, user, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error activating user: {str(e)}")
            return False, "Error al activar usuario", 500
