# 🚨 SOLUCIÓN RÁPIDA: Application Error en Azure

Tu deployment fue exitoso, pero **falta configurar Azure App Service**.

## Pasos Urgentes (5 minutos)

### 1️⃣ Configurar Startup Command

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca tu App Service: **task-forge**
3. Ve a **Configuration** → **Configuracion (vista preliminar)** → **Configuración de la pila**
4. En **Comando de inicio**, pega:
   ```bash
   gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=120 run:app
   ```
5. Haz clic en **Save** → **Continue**

### 2️⃣ Configurar Variables de Entorno Mínimas

1. Ve a **Configuration** → **Application settings**
2. Haz clic en **New application setting** para cada una:

   ```
   Nombre: FLASK_ENV
   Valor: production
   ```

   ```
   Nombre: SECRET_KEY
   Valor: [corre este comando en tu terminal local para generar una clave]
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   ```
   Nombre: JWT_SECRET_KEY
   Valor: [corre el comando de nuevo para otra clave diferente]
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Haz clic en **Save** → **Continue**

### 3️⃣ Reiniciar la Aplicación

1. Ve a **Overview**
2. Haz clic en **Restart**
3. Espera 1-2 minutos

### 4️⃣ Probar

Accede a: https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs

✅ Deberías ver la documentación Swagger de tu API

---

## Si necesitas Base de Datos (Opcional ahora)

Por defecto, la app usará SQLite si no configuras Azure SQL. Para producción, es mejor usar Azure SQL:

1. Crea un Azure SQL Database
2. Agrega estas variables en **Application settings**:
   ```
   AZURE_SQL_SERVER=tu-servidor.database.windows.net
   AZURE_SQL_DATABASE=taskforge_db
   AZURE_SQL_USER=tu-usuario
   AZURE_SQL_PASSWORD=tu-password
   ```
3. Configura el firewall del SQL Server para permitir Azure services

---

## ¿Sigue sin funcionar?

### Ver los logs:
1. Ve a **Monitoring** → **Log stream**
2. O accede a: https://task-forge-gbd6h8gtg8hchve9.scm.azurewebsites.net/api/logs/docker

### Guía completa:
Lee `docs/azure-app-service-configuration.md` para instrucciones detalladas.

---

## Commit los cambios nuevos

No olvides hacer commit del archivo `startup.sh`:

```bash
git add startup.sh AZURE_QUICK_FIX.md docs/azure-app-service-configuration.md
git commit -m "feat: Add Azure App Service configuration and startup script"
git push
```

El GitHub Actions redesplegará automáticamente.
