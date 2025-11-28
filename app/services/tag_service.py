from flask import current_app
from app import db
from app.models.tag import Tag
from app.utils.validators import validate_required_fields, validate_string_length, validate_color_hex
from app.utils.helpers import paginate, apply_sorting


class TagService:
    """Servicio para gestion de etiquetas"""

    @staticmethod
    def create_tag(data):
        """
        Crear una nueva etiqueta
        Returns: (success, tag_or_error_message, status_code)
        """
        # Validate required fields
        required_fields = ['name']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return False, f"Faltan campos requeridos: {', '.join(missing_fields)}", 400

        name = data.get('name')
        color = data.get('color', '#808080')
        description = data.get('description', '')

        # Validate name
        is_valid, error_msg = validate_string_length(name, min_length=1, max_length=50, field_name="Nombre")
        if not is_valid:
            return False, error_msg, 400

        # Validate color
        is_valid, error_msg = validate_color_hex(color)
        if not is_valid:
            return False, error_msg, 400

        # Check if tag already exists
        if Tag.query.filter_by(name=name.strip()).first():
            return False, "La etiqueta ya existe", 409

        # Create tag
        new_tag = Tag(
            name=name.strip(),
            color=color,
            description=description.strip() if description else None
        )

        try:
            db.session.add(new_tag)
            db.session.commit()
            return True, new_tag, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating tag: {str(e)}")
            return False, "Error al crear la etiqueta", 500

    @staticmethod
    def get_all_tags(page=1, per_page=50, sort_by='name', sort_order='asc'):
        """
        Obtener todas las etiquetas con paginacion
        Returns: (success, result_or_error_message, status_code)
        """
        query = Tag.query

        # Apply sorting
        query = apply_sorting(query, Tag, sort_by, sort_order)

        # Paginate
        tags, pagination_meta = paginate(query, page, per_page)

        result = {
            'tags': [tag.to_dict() for tag in tags],
            'pagination': pagination_meta
        }

        return True, result, 200

    @staticmethod
    def get_tag(tag_id):
        """
        Obtener una etiqueta individual
        Returns: (success, tag_or_error_message, status_code)
        """
        tag = Tag.query.get(tag_id)

        if not tag:
            return False, "Etiqueta no encontrada", 404

        return True, tag, 200

    @staticmethod
    def update_tag(tag_id, data):
        """
        Actualizar una etiqueta
        Returns: (success, tag_or_error_message, status_code)
        """
        tag = Tag.query.get(tag_id)

        if not tag:
            return False, "Etiqueta no encontrada", 404

        # Update fields
        if 'name' in data:
            name = data['name']
            is_valid, error_msg = validate_string_length(name, min_length=1, max_length=50, field_name="Nombre")
            if not is_valid:
                return False, error_msg, 400

            # Check if name already exists (excluding current tag)
            existing_tag = Tag.query.filter_by(name=name.strip()).first()
            if existing_tag and existing_tag.id != tag_id:
                return False, "La etiqueta ya existe", 409

            tag.name = name.strip()

        if 'color' in data:
            color = data['color']
            is_valid, error_msg = validate_color_hex(color)
            if not is_valid:
                return False, error_msg, 400
            tag.color = color

        if 'description' in data:
            description = data['description']
            tag.description = description.strip() if description else None

        try:
            db.session.commit()
            return True, tag, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating tag: {str(e)}")
            return False, "Error al actualizar la etiqueta", 500

    @staticmethod
    def delete_tag(tag_id):
        """
        Eliminar una etiqueta
        Returns: (success, message, status_code)
        """
        tag = Tag.query.get(tag_id)

        if not tag:
            return False, "Etiqueta no encontrada", 404

        try:
            db.session.delete(tag)
            db.session.commit()
            return True, "Etiqueta eliminada con exito", 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting tag: {str(e)}")
            return False, "Error al eliminar la etiqueta", 500
