import re
from datetime import datetime


def validate_email(email):
    """
    Validar formato de correo electronico
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "El correo electronico es requerido"

    email = email.strip()

    if len(email) < 3:
        return False, "El correo electronico es demasiado corto"

    if len(email) > 120:
        return False, "El correo electronico es demasiado largo"

    # More strict email pattern that doesn't allow consecutive dots
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Formato de correo electronico invalido"

    # Check for consecutive dots
    if '..' in email:
        return False, "Formato de correo electronico invalido"

    return True, None


def validate_password(password):
    """
    Validar fortaleza de la contrasena
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "La contrasena es requerida"

    if len(password) < 8:
        return False, "La contrasena debe tener al menos 8 caracteres"

    if len(password) > 128:
        return False, "La contrasena es demasiado larga"

    if not re.search(r'[A-Z]', password):
        return False, "La contrasena debe contener al menos una letra mayuscula"

    if not re.search(r'[a-z]', password):
        return False, "La contrasena debe contener al menos una letra minuscula"

    if not re.search(r'[0-9]', password):
        return False, "La contrasena debe contener al menos un numero"

    return True, None


def validate_username(username):
    """
    Validar formato de nombre de usuario
    Requirements:
    - 3-80 characters
    - Only alphanumeric, underscore, and hyphen
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "El nombre de usuario es requerido"

    username = username.strip()

    if len(username) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"

    if len(username) > 80:
        return False, "El nombre de usuario es demasiado largo"

    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return False, "El nombre de usuario solo puede contener letras, numeros, guiones bajos y guiones"

    return True, None


def validate_required_fields(data, required_fields):
    """
    Validar que todos los campos requeridos esten presentes en los datos
    Returns: (is_valid, missing_fields)
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)

    if missing_fields:
        return False, missing_fields

    return True, None


def validate_string_length(value, min_length=None, max_length=None, field_name="Field"):
    """
    Validar longitud de cadena
    Returns: (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} debe ser una cadena"

    length = len(value.strip())

    if min_length is not None and length < min_length:
        return False, f"{field_name} debe tener al menos {min_length} caracteres"

    if max_length is not None and length > max_length:
        return False, f"{field_name} no debe exceder {max_length} caracteres"

    return True, None


def validate_enum_value(value, enum_class, field_name="Field"):
    """
    Validar que el valor este en la enumeracion
    Returns: (is_valid, error_message)
    """
    if not value:
        return False, f"{field_name} es requerido"

    valid_values = [e.value for e in enum_class]

    if value not in valid_values:
        return False, f"{field_name} debe ser uno de: {', '.join(valid_values)}"

    return True, None


def validate_color_hex(color):
    """
    Validar codigo de color hex
    Returns: (is_valid, error_message)
    """
    if not color:
        return True, None

    pattern = r'^#[0-9A-Fa-f]{6}$'
    if not re.match(pattern, color):
        return False, "El color debe ser un codigo hex valido (ej. #FF0000)"

    return True, None


def validate_date_format(date_string):
    """
    Validar formato de fecha ISO
    Returns: (is_valid, error_message, parsed_date)
    """
    if not date_string:
        return True, None, None

    try:
        # Try strict ISO format first (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        parsed_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True, None, parsed_date
    except (ValueError, TypeError):
        # Fallback: Try dateutil for more flexible parsing, but check for ISO-like format
        try:
            # Only accept if it looks like ISO format
            if not (date_string[0].isdigit() and ('-' in date_string or 'T' in date_string)):
                return False, "Formato de fecha invalido. Use formato ISO (ej. 2024-01-15T10:30:00)", None

            from dateutil import parser
            parsed_date = parser.isoparse(date_string)  # More strict than parse()
            return True, None, parsed_date
        except:
            return False, "Formato de fecha invalido. Use formato ISO (ej. 2024-01-15T10:30:00)", None
