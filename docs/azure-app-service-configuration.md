# Configuración de Azure App Service para TaskForge API

Esta guía te ayudará a configurar correctamente tu aplicación Flask en Azure App Service después del deployment automático con GitHub Actions.

## Problema Común: "Application Error"

Si ves este error al acceder a tu aplicación, es porque **faltan configuraciones críticas** en Azure App Service.

## Pasos de Configuración

### 1. Configurar el Startup Command

Azure necesita saber cómo iniciar tu aplicación Flask.

**Opción A: Usar startup.sh (Recomendado)**

1. Ve a Azure Portal → Tu App Service → **Configuration** → **General settings**
2. En **Startup Command**, ingresa:
   ```bash
   bash startup.sh
   ```
3. Haz clic en **Save**

**Opción B: Comando directo de Gunicorn**

Si prefieres no usar el script, puedes usar:
```bash
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=120 run:app
```

### 2. Configurar Variables de Entorno

Ve a Azure Portal → Tu App Service → **Configuration** → **Application settings**

Agrega las siguientes variables (haz clic en **New application setting** para cada una):

#### Variables Obligatorias

| Nombre | Valor | Descripción |
|--------|-------|-------------|
| `FLASK_ENV` | `production` | Entorno de ejecución |
| `SECRET_KEY` | `[genera-una-clave-segura]` | Clave secreta de Flask (usa un generador) |
| `JWT_SECRET_KEY` | `[genera-otra-clave-segura]` | Clave para tokens JWT |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Ya está configurado por defecto |

#### Variables de Base de Datos Azure SQL

Si usas Azure SQL Database:

| Nombre | Valor | Ejemplo |
|--------|-------|---------|
| `AZURE_SQL_SERVER` | `tu-servidor.database.windows.net` | `taskforge-server.database.windows.net` |
| `AZURE_SQL_DATABASE` | `nombre-de-tu-bd` | `taskforge_db` |
| `AZURE_SQL_USER` | `usuario-admin` | `sqladmin` |
| `AZURE_SQL_PASSWORD` | `tu-password-seguro` | `P@ssw0rd123!` |
| `AZURE_SQL_PORT` | `1433` | `1433` |

#### Variables Opcionales

| Nombre | Valor por Defecto | Descripción |
|--------|-------------------|-------------|
| `JWT_ACCESS_TOKEN_EXPIRES` | `3600` | Duración del token de acceso (segundos) |
| `RATELIMIT_ENABLED` | `true` | Habilitar rate limiting |
| `CORS_ORIGINS` | `https://tu-frontend.com` | Orígenes permitidos para CORS |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

### 3. Generar Claves Secretas Seguras

**IMPORTANTE**: NO uses las claves del `.env.example` en producción.

Para generar claves seguras, ejecuta en tu terminal local:

```bash
# Para SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Para JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia cada resultado y úsalo en las variables de Azure.

### 4. Configurar Azure SQL Database (Si aplica)

#### Opción A: Crear Azure SQL Database

1. Ve a Azure Portal → **Create a resource** → **SQL Database**
2. Llena la información:
   - Database name: `taskforge_db`
   - Server: Crea uno nuevo o usa uno existente
   - Compute + Storage: Elige el tier apropiado (Basic para desarrollo)
3. Una vez creado, ve a **Connection strings** y copia la información
4. Configura las variables de entorno con estos valores

#### Opción B: Permitir SQLite (Solo desarrollo)

Si quieres usar SQLite temporalmente:

1. En `app/config.py`, la aplicación ya maneja SQLite si no hay variables de Azure SQL
2. **ADVERTENCIA**: SQLite no es recomendado para producción en Azure
3. El archivo de base de datos se perderá si el contenedor se reinicia

### 5. Configurar el Firewall de Azure SQL

Si usas Azure SQL Database:

1. Ve a tu **SQL Server** (no la database) en Azure Portal
2. Ve a **Networking** → **Firewall rules**
3. Agrega una regla:
   - Name: `AllowAzureServices`
   - Start IP: `0.0.0.0`
   - End IP: `0.0.0.0`
   - O habilita: **Allow Azure services and resources to access this server**
4. Guarda los cambios

### 6. Reiniciar la Aplicación

Después de hacer todos los cambios:

1. Ve a **Overview** de tu App Service
2. Haz clic en **Restart**
3. Espera 1-2 minutos

### 7. Verificar que Funciona

Accede a tu aplicación:

```
https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs
```

Deberías ver la documentación Swagger de tu API.

## Solución de Problemas

### Ver Logs de la Aplicación

**Método 1: Azure Portal**
1. Ve a **Monitoring** → **Log stream**
2. Verás los logs en tiempo real

**Método 2: Kudu (Avanzado)**
1. Ve a `https://[tu-app].scm.azurewebsites.net/api/logs/docker`
2. Descarga y revisa los logs

**Método 3: SSH (Avanzado)**
1. Ve a **Development Tools** → **SSH**
2. Revisa los logs en `/home/site/wwwroot/logs/`

### Errores Comunes

#### Error: "Application Error"
- **Causa**: Falta el startup command o variables de entorno
- **Solución**: Completa los pasos 1 y 2 de esta guía

#### Error: "Cannot connect to database"
- **Causa**: Variables de base de datos incorrectas o firewall bloqueado
- **Solución**: Revisa los pasos 4 y 5

#### Error: "Token validation failed"
- **Causa**: `SECRET_KEY` o `JWT_SECRET_KEY` no configurados
- **Solución**: Configura estas variables (paso 2)

#### Error: "Module not found"
- **Causa**: Dependencias no instaladas correctamente
- **Solución**: Verifica que `SCM_DO_BUILD_DURING_DEPLOYMENT=true` esté configurado

### Verificar Variables de Entorno Configuradas

Puedes verificar las variables (sin mostrar sus valores) accediendo a:

```
https://[tu-app].scm.azurewebsites.net/Env
```

## Checklist de Configuración

Usa este checklist para asegurarte de que todo está configurado:

- [ ] Startup command configurado (`bash startup.sh`)
- [ ] `FLASK_ENV=production` configurado
- [ ] `SECRET_KEY` generado y configurado
- [ ] `JWT_SECRET_KEY` generado y configurado
- [ ] Variables de base de datos configuradas (o SQLite habilitado)
- [ ] Firewall de Azure SQL configurado (si aplica)
- [ ] Aplicación reiniciada
- [ ] `/api/docs` accesible

## Comandos Útiles

### Reiniciar la aplicación remotamente (con Azure CLI)

```bash
az webapp restart --name task-forge --resource-group [tu-resource-group]
```

### Ver logs en tiempo real (con Azure CLI)

```bash
az webapp log tail --name task-forge --resource-group [tu-resource-group]
```

### Ejecutar comandos en el contenedor (SSH)

```bash
az webapp ssh --name task-forge --resource-group [tu-resource-group]
```

## Próximos Pasos

Una vez que tu aplicación esté funcionando:

1. **Crear un usuario administrador**:
   ```bash
   # Conéctate por SSH y ejecuta:
   cd /home/site/wwwroot
   python scripts/reset_admin_password.py
   ```

2. **Configurar un dominio personalizado** (opcional)
3. **Habilitar HTTPS** (Azure lo hace automáticamente)
4. **Configurar CI/CD** (ya está con GitHub Actions)
5. **Configurar monitoreo** (Application Insights)

## Recursos Adicionales

- [Azure App Service Python Documentation](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Azure SQL Database Documentation](https://docs.microsoft.com/en-us/azure/azure-sql/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
