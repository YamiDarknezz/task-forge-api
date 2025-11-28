# Scripts de Administración - TaskForge API

## Credenciales de Administrador por Defecto

Después de ejecutar `init_db_azure.sql`, se crea automáticamente un usuario administrador:

- **Email:** `admin@taskforge.com`
- **Contraseña:** `Admin123!`
- **Username:** `admin`

> ⚠️ **IMPORTANTE:** Esta contraseña es solo para desarrollo. Cámbiala inmediatamente en producción.

## Script de Reset de Contraseña

El script `reset_admin_password.py` permite cambiar la contraseña de cualquier usuario (especialmente útil para el admin) sin necesidad de autenticación previa.

### Requisitos

- Acceso directo a la base de datos
- Variables de entorno configuradas correctamente (`.env`)
- Entorno virtual activado

### Uso

#### Modo Interactivo (Recomendado)

```bash
python scripts/reset_admin_password.py
```

El script te pedirá:
1. Email del usuario
2. Nueva contraseña (oculta)
3. Confirmación de contraseña
4. Si deseas revocar tokens de refresh existentes

#### Modo No-Interactivo (con argumentos)

```bash
python scripts/reset_admin_password.py --email admin@taskforge.com --password NuevaContra123!
```

#### No revocar tokens de refresh

```bash
python scripts/reset_admin_password.py --email admin@taskforge.com --password NuevaContra123! --no-revoke-tokens
```

### Requisitos de Contraseña

Las contraseñas deben cumplir con:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número

### Ejemplos de Uso

**Resetear contraseña del admin en desarrollo:**
```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Ejecutar script
python scripts/reset_admin_password.py

# Ingresar cuando se solicite:
# Email: admin@taskforge.com
# Nueva contraseña: MiNuevaContra123!
# Confirmar contraseña: MiNuevaContra123!
# Revocar tokens: S
```

**Resetear contraseña con argumentos:**
```bash
python scripts/reset_admin_password.py \
  --email admin@taskforge.com \
  --password DevPassword2024!
```

### Seguridad

- ✅ El script valida la contraseña antes de actualizarla
- ✅ Por defecto, revoca todos los tokens de refresh del usuario (fuerza re-login)
- ✅ Requiere acceso directo a la base de datos (no es un endpoint HTTP)
- ✅ Solo debe usarse en entornos de desarrollo o con acceso controlado

### Alternativas

Si tienes acceso al sistema y conoces la contraseña actual, puedes usar el endpoint de la API:

```bash
POST /auth/change-password
Authorization: Bearer <access_token>

{
  "old_password": "ContraseñaActual",
  "new_password": "NuevaContraseña123!"
}
```

## Inicialización de Base de Datos

### Azure SQL Server

```bash
# Ejecutar el script SQL en Azure
sqlcmd -S yamidarknezz.database.windows.net -d taskforge_db -U <usuario> -P <contraseña> -i scripts/init_db_azure.sql
```

O usando Azure Data Studio / SQL Server Management Studio.

### SQLite (Desarrollo Local)

La aplicación creará automáticamente `taskforge.db` si no hay configuración de Azure SQL en el `.env`.

---

## Troubleshooting

### "Usuario no encontrado"
Verifica que el email sea correcto. Los emails se almacenan en minúsculas.

### "Error al conectar a la base de datos"
Verifica que:
1. Las variables de entorno en `.env` estén correctamente configuradas
2. La base de datos esté accesible
3. El entorno virtual esté activado

### "Contraseña inválida"
Asegúrate de que la contraseña cumpla con todos los requisitos de validación.
