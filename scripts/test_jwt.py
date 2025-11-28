#!/usr/bin/env python3
"""Script de diagnóstico para verificar JWT"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from flask_jwt_extended import create_access_token, decode_token
import jwt

app = create_app()

with app.app_context():
    print("=" * 60)
    print("DIAGNÓSTICO DE JWT")
    print("=" * 60)

    # Verificar configuración
    print(f"\n1. JWT_SECRET_KEY configurado: {app.config['JWT_SECRET_KEY']}")
    print(f"2. JWT_HEADER_TYPE: {app.config['JWT_HEADER_TYPE']}")
    print(f"3. JWT_HEADER_NAME: {app.config['JWT_HEADER_NAME']}")

    # Crear un token de prueba
    print("\n" + "=" * 60)
    print("CREANDO TOKEN DE PRUEBA")
    print("=" * 60)

    test_user_id = "1"  # Ahora debe ser string
    token = create_access_token(identity=test_user_id)
    print(f"\nToken generado: {token[:50]}...")

    # Intentar decodificar el token
    print("\n" + "=" * 60)
    print("VERIFICANDO TOKEN")
    print("=" * 60)

    try:
        # Decodificar sin verificar
        decoded_unverified = jwt.decode(token, options={"verify_signature": False})
        print("\n[OK] Token decodificado (sin verificar firma):")
        print(f"   - sub (user_id): {decoded_unverified.get('sub')}")
        print(f"   - type: {decoded_unverified.get('type')}")
        print(f"   - iat: {decoded_unverified.get('iat')}")
        print(f"   - exp: {decoded_unverified.get('exp')}")

        # Intentar verificar firma
        decoded_verified = jwt.decode(
            token,
            app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        print("\n[OK] TOKEN VALIDO - Firma verificada correctamente!")

    except jwt.InvalidSignatureError:
        print("\n[ERROR] Firma invalida")
    except jwt.ExpiredSignatureError:
        print("\n[ERROR] Token expirado")
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {str(e)}")

    print("\n" + "=" * 60)
    print("Usa este token en Swagger:")
    print("=" * 60)
    print(f"\nBearer {token}")
    print("\n" + "=" * 60)
