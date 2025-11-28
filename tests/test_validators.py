import pytest
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_required_fields,
    validate_string_length,
    validate_enum_value,
    validate_color_hex,
    validate_date_format
)
from app.models.task import TaskStatus


class TestValidateEmail:
    """Tests for email validation"""

    def test_valid_email(self):
        """Test valid email addresses"""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.co.uk',
            'test123@test-domain.com'
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is True
            assert error is None

    def test_invalid_email_format(self):
        """Test invalid email formats"""
        invalid_emails = [
            'invalid',
            'invalid@',
            '@example.com',
            'test@',
            'test@.com',
            'test..test@example.com'
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is False
            assert error is not None

    def test_empty_email(self):
        """Test empty email"""
        is_valid, error = validate_email('')
        assert is_valid is False
        assert 'el correo electronico es requerido' in error.lower()

    def test_none_email(self):
        """Test None email"""
        is_valid, error = validate_email(None)
        assert is_valid is False
        assert 'el correo electronico es requerido' in error.lower()

    def test_email_too_short(self):
        """Test email too short"""
        is_valid, error = validate_email('a@')
        assert is_valid is False
        assert 'el correo electronico es demasiado corto' in error.lower()

    def test_email_too_long(self):
        """Test email too long"""
        long_email = 'a' * 120 + '@example.com'
        is_valid, error = validate_email(long_email)
        assert is_valid is False
        assert 'el correo electronico es demasiado largo' in error.lower()


class TestValidatePassword:
    """Tests for password validation"""

    def test_valid_password(self):
        """Test valid passwords"""
        valid_passwords = [
            'Password123',
            'Test@Pass1',
            'MySecure1Pass',
            'Valid123Password'
        ]
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid is True
            assert error is None

    def test_password_too_short(self):
        """Test password too short"""
        is_valid, error = validate_password('Pass1')
        assert is_valid is False
        assert 'La contrasena debe tener al menos 8 caracteres' in error

    def test_password_too_long(self):
        """Test password too long"""
        long_password = 'A1' + 'a' * 130
        is_valid, error = validate_password(long_password)
        assert is_valid is False
        assert 'la contrasena es demasiado larga' in error.lower()

    def test_password_no_uppercase(self):
        """Test password without uppercase"""
        is_valid, error = validate_password('password123')
        assert is_valid is False
        assert 'la contrasena debe contener al menos una letra mayuscula' in error.lower()

    def test_password_no_lowercase(self):
        """Test password without lowercase"""
        is_valid, error = validate_password('PASSWORD123')
        assert is_valid is False
        assert 'la contrasena debe contener al menos una letra minuscula' in error.lower()

    def test_password_no_number(self):
        """Test password without number"""
        is_valid, error = validate_password('PasswordTest')
        assert is_valid is False
        assert 'la contrasena debe contener al menos un numero' in error.lower()

    def test_empty_password(self):
        """Test empty password"""
        is_valid, error = validate_password('')
        assert is_valid is False
        assert 'la contrasena es requerida' in error.lower()

    def test_none_password(self):
        """Test None password"""
        is_valid, error = validate_password(None)
        assert is_valid is False
        assert 'la contrasena es requerida' in error.lower()


class TestValidateUsername:
    """Tests for username validation"""

    def test_valid_username(self):
        """Test valid usernames"""
        valid_usernames = [
            'testuser',
            'user_name',
            'user-name',
            'Test123',
            'user_123-test'
        ]
        for username in valid_usernames:
            is_valid, error = validate_username(username)
            assert is_valid is True
            assert error is None

    def test_username_too_short(self):
        """Test username too short"""
        is_valid, error = validate_username('ab')
        assert is_valid is False
        assert 'El nombre de usuario debe tener al menos 3 caracteres' in error

    def test_username_too_long(self):
        """Test username too long"""
        long_username = 'a' * 81
        is_valid, error = validate_username(long_username)
        assert is_valid is False
        assert 'el nombre de usuario es demasiado largo' in error.lower()

    def test_username_invalid_characters(self):
        """Test username with invalid characters"""
        invalid_usernames = [
            'test@user',
            'test user',
            'test.user',
            'test!user'
        ]
        for username in invalid_usernames:
            is_valid, error = validate_username(username)
            assert is_valid is False
            assert 'El nombre de usuario solo puede contener letras, numeros, guiones bajos y guiones' in error

    def test_empty_username(self):
        """Test empty username"""
        is_valid, error = validate_username('')
        assert is_valid is False
        assert 'el nombre de usuario es requerido' in error.lower()

    def test_none_username(self):
        """Test None username"""
        is_valid, error = validate_username(None)
        assert is_valid is False
        assert 'el nombre de usuario es requerido' in error.lower()


class TestValidateRequiredFields:
    """Tests for required fields validation"""

    def test_all_fields_present(self):
        """Test when all required fields are present"""
        data = {'field1': 'value1', 'field2': 'value2', 'field3': 'value3'}
        required = ['field1', 'field2', 'field3']
        is_valid, missing = validate_required_fields(data, required)
        assert is_valid is True
        assert missing is None

    def test_missing_fields(self):
        """Test when some fields are missing"""
        data = {'field1': 'value1'}
        required = ['field1', 'field2', 'field3']
        is_valid, missing = validate_required_fields(data, required)
        assert is_valid is False
        assert missing == ['field2', 'field3']

    def test_empty_string_fields(self):
        """Test empty string fields"""
        data = {'field1': '', 'field2': 'value2'}
        required = ['field1', 'field2']
        is_valid, missing = validate_required_fields(data, required)
        assert is_valid is False
        assert 'field1' in missing

    def test_none_fields(self):
        """Test None fields"""
        data = {'field1': None, 'field2': 'value2'}
        required = ['field1', 'field2']
        is_valid, missing = validate_required_fields(data, required)
        assert is_valid is False
        assert 'field1' in missing


class TestValidateStringLength:
    """Tests for string length validation"""

    def test_valid_string_length(self):
        """Test valid string length"""
        is_valid, error = validate_string_length('test', min_length=2, max_length=10)
        assert is_valid is True
        assert error is None

    def test_string_too_short(self):
        """Test string too short"""
        is_valid, error = validate_string_length('ab', min_length=5, field_name='Title')
        assert is_valid is False
        assert 'Title debe tener al menos 5 caracteres' in error

    def test_string_too_long(self):
        """Test string too long"""
        is_valid, error = validate_string_length('toolong', max_length=5, field_name='Name')
        assert is_valid is False
        assert 'Name no debe exceder 5 caracteres' in error

    def test_non_string_value(self):
        """Test non-string value"""
        is_valid, error = validate_string_length(123, field_name='Field')
        assert is_valid is False
        assert 'Field debe ser una cadena' in error


class TestValidateEnumValue:
    """Tests for enum value validation"""

    def test_valid_enum_value(self):
        """Test valid enum value"""
        is_valid, error = validate_enum_value('pending', TaskStatus, 'Status')
        assert is_valid is True
        assert error is None

    def test_invalid_enum_value(self):
        """Test invalid enum value"""
        is_valid, error = validate_enum_value('invalid', TaskStatus, 'Status')
        assert is_valid is False
        assert 'Status debe ser uno de: pending, in_progress, completed, cancelled' in error

    def test_empty_enum_value(self):
        """Test empty enum value"""
        is_valid, error = validate_enum_value('', TaskStatus, 'Status')
        assert is_valid is False
        assert 'status es requerido' in error.lower()


class TestValidateColorHex:
    """Tests for hex color validation"""

    def test_valid_color_hex(self):
        """Test valid hex colors"""
        valid_colors = ['#FF0000', '#00ff00', '#0000FF', '#ABCDEF']
        for color in valid_colors:
            is_valid, error = validate_color_hex(color)
            assert is_valid is True
            assert error is None

    def test_invalid_color_hex(self):
        """Test invalid hex colors"""
        invalid_colors = ['FF0000', '#FF00', '#GGGGGG', 'red', '#12345']
        for color in invalid_colors:
            is_valid, error = validate_color_hex(color)
            assert is_valid is False
            assert 'El color debe ser un codigo hex valido (ej. #FF0000)' in error

    def test_empty_color(self):
        """Test empty color"""
        is_valid, error = validate_color_hex('')
        assert is_valid is True
        assert error is None


class TestValidateDateFormat:
    """Tests for date format validation"""

    def test_valid_date_formats(self):
        """Test valid date formats"""
        valid_dates = [
            '2024-01-15',
            '2024-01-15T10:30:00',
            '2024-01-15 10:30:00',
            '2024-01-15T10:30:00Z'
        ]
        for date_string in valid_dates:
            is_valid, error, parsed_date = validate_date_format(date_string)
            assert is_valid is True
            assert error is None
            assert parsed_date is not None

    def test_invalid_date_format(self):
        """Test invalid date formats"""
        invalid_dates = ['invalid', '2024-13-01', '15/01/2024', 'not-a-date']
        for date_string in invalid_dates:
            is_valid, error, parsed_date = validate_date_format(date_string)
            assert is_valid is False
            assert error is not None
            assert parsed_date is None

    def test_empty_date(self):
        """Test empty date"""
        is_valid, error, parsed_date = validate_date_format('')
        assert is_valid is True
        assert error is None
        assert parsed_date is None
