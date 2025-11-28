#!/usr/bin/env python3
"""
Script para resetear la contraseña de un usuario (principalmente admin) sin autenticación previa.
Este script requiere acceso directo a la base de datos.

Uso:
    python scripts/reset_admin_password.py

Modo interactivo con prompts para email y nueva contraseña.

Uso con argumentos:
    python scripts/reset_admin_password.py --email admin@taskforge.com --password NuevaContra123!

NOTA: Este script solo debe usarse en desarrollo o con acceso controlado a la base de datos.
"""

import sys
import os
import argparse
import getpass

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User, RefreshToken
from app.utils.validators import validate_password


def reset_user_password(email, new_password, revoke_tokens=True):
    """
    Reset user password without requiring old password

    Args:
        email: Email del usuario
        new_password: Nueva contraseña
        revoke_tokens: Si se deben revocar los refresh tokens existentes (default: True)

    Returns:
        (success, message)
    """
    # Validate email
    if not email or '@' not in email:
        return False, "Email inválido"

    # Validate password
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        return False, f"Contraseña inválida: {error_msg}"

    # Find user
    user = User.query.filter_by(email=email.strip().lower()).first()

    if not user:
        return False, f"Usuario con email '{email}' no encontrado"

    try:
        # Update password
        user.set_password(new_password)

        # Optionally revoke all refresh tokens for security
        if revoke_tokens:
            revoked_count = RefreshToken.query.filter_by(
                user_id=user.id,
                is_revoked=False
            ).update({'is_revoked': True})

            db.session.commit()

            return True, (
                f"Contraseña actualizada exitosamente para '{user.username}' ({email})\n"
                f"Se revocaron {revoked_count} tokens de refresh activos."
            )
        else:
            db.session.commit()
            return True, f"Contraseña actualizada exitosamente para '{user.username}' ({email})"

    except Exception as e:
        db.session.rollback()
        return False, f"Error al actualizar contraseña: {str(e)}"


def interactive_mode():
    """Modo interactivo con prompts"""
    print("=" * 60)
    print("  RESETEO DE CONTRASEÑA - TaskForge API")
    print("=" * 60)
    print()

    # Get email
    email = input("Email del usuario: ").strip()

    if not email:
        print("\n❌ Email no puede estar vacío")
        return

    # Get new password (hidden input)
    print("\nRequisitos de contraseña:")
    print("  - Mínimo 8 caracteres")
    print("  - Al menos una letra mayúscula")
    print("  - Al menos una letra minúscula")
    print("  - Al menos un número")
    print()

    new_password = getpass.getpass("Nueva contraseña: ")

    if not new_password:
        print("\n❌ Contraseña no puede estar vacía")
        return

    # Confirm password
    confirm_password = getpass.getpass("Confirmar contraseña: ")

    if new_password != confirm_password:
        print("\n❌ Las contraseñas no coinciden")
        return

    # Ask about revoking tokens
    print()
    revoke_input = input("¿Revocar todos los tokens de refresh existentes? (S/n): ").strip().lower()
    revoke_tokens = revoke_input != 'n'

    print("\n" + "-" * 60)
    print(f"Email: {email}")
    print(f"Revocar tokens: {'Sí' if revoke_tokens else 'No'}")
    print("-" * 60)

    confirm = input("\n¿Continuar? (s/N): ").strip().lower()

    if confirm != 's':
        print("\n❌ Operación cancelada")
        return

    # Execute reset
    print("\nActualizando contraseña...")
    success, message = reset_user_password(email, new_password, revoke_tokens)

    if success:
        print(f"\n✅ {message}")
    else:
        print(f"\n❌ {message}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Resetear contraseña de usuario sin autenticación previa'
    )
    parser.add_argument(
        '--email',
        type=str,
        help='Email del usuario'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Nueva contraseña'
    )
    parser.add_argument(
        '--no-revoke-tokens',
        action='store_true',
        help='No revocar tokens de refresh existentes'
    )

    args = parser.parse_args()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Check if arguments provided
        if args.email and args.password:
            # Non-interactive mode
            success, message = reset_user_password(
                args.email,
                args.password,
                revoke_tokens=not args.no_revoke_tokens
            )

            if success:
                print(f"✅ {message}")
                sys.exit(0)
            else:
                print(f"❌ {message}")
                sys.exit(1)
        else:
            # Interactive mode
            try:
                interactive_mode()
            except KeyboardInterrupt:
                print("\n\n❌ Operación cancelada por usuario")
                sys.exit(1)


if __name__ == '__main__':
    main()
