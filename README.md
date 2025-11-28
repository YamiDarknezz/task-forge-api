# TaskForge API

> Una API RESTful profesional para gestión de tareas construida con Flask, SQLAlchemy y Azure SQL Database.

## 📊 Badges

[![Build and Deploy](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/main_task-forge.yml/badge.svg)](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/main_task-forge.yml)
[![Code Quality](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/code-quality.yml/badge.svg)](https://github.com/YamiDarknezz/task-forge-api/actions/workflows/code-quality.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=bugs)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)

## 🌐 Demo en Vivo

**API en Producción:** [https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs](https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs)

Accede a la documentación interactiva Swagger UI y prueba los endpoints en tiempo real.

## 📋 Descripción

TaskForge API es un sistema completo de gestión de tareas que demuestra la implementación de **mejores prácticas en desarrollo backend con Flask**, incluyendo autenticación JWT, control de acceso basado en roles (RBAC), testing exhaustivo, análisis de calidad de código, pruebas de accesibilidad, y despliegue en Azure.

**Este proyecto fue desarrollado para demostrar conocimientos avanzados en:**
- ✅ Arquitectura de APIs RESTful con Flask
- ✅ Testing exhaustivo con pytest (268 tests, >73% cobertura)
- ✅ Análisis de calidad de código con SonarCloud
- ✅ Pruebas de accesibilidad con AXE (WCAG 2.1)
- ✅ Autenticación y autorización con JWT
- ✅ ORM con SQLAlchemy
- ✅ Integración con Azure SQL Database
- ✅ CI/CD con GitHub Actions
- ✅ Deployment en Azure App Service
- ✅ Documentación con Swagger/OpenAPI

## ✨ Características Principales

- 🔐 **Autenticación JWT** - Sistema completo con access y refresh tokens
- 👥 **RBAC (Control de Acceso Basado en Roles)** - Roles de Admin y Usuario con permisos específicos
- ✅ **CRUD Completo** - Gestión de tareas con título, descripción, prioridad, estado y fechas
- 🏷️ **Sistema de Etiquetas** - Organiza tareas con etiquetas personalizables y colores
- 🔍 **Filtrado Avanzado** - Filtra tareas por estado, prioridad, usuario, etiquetas y fechas
- 📄 **Paginación y Ordenamiento** - Paginación del lado del servidor con ordenamiento personalizable
- 📊 **Exportación de Datos** - Exporta tareas a formatos CSV o JSON
- 🚦 **Rate Limiting** - Protección contra abuso con Flask-Limiter
- 🌐 **Soporte CORS** - Configurado para peticiones cross-origin
- 📚 **Documentación Interactiva** - Swagger/OpenAPI UI
- 🧪 **Testing Completo** - 268 tests con pytest y >73% de cobertura de código
- 🚀 **CI/CD Pipeline** - Despliegue automatizado a Azure App Service
- 🐳 **Docker Support** - Aplicación containerizada con Docker Compose
- ☁️ **Producción en Azure** - Desplegado en Azure App Service con Azure SQL Database

## 🛠️ Stack Tecnológico

### Backend
- **Flask** 3.1.2 - Framework web
- **SQLAlchemy** 2.0.44 - ORM
- **Flask-JWT-Extended** 4.7.1 - Autenticación JWT
- **pyodbc** 5.3.0 - Conector para Azure SQL Server
- **Flask-CORS** 6.0.1 - Manejo de CORS
- **Flask-Limiter** 4.0.0 - Rate limiting
- **Flasgger** 0.9.7.1 - Documentación Swagger

### Base de Datos
- **Azure SQL Database** - Base de datos en producción
- **SQLite** - Fallback para desarrollo/testing

### Testing y Calidad
- **pytest** 9.0.1 - Framework de testing
- **pytest-cov** 7.0.0 - Cobertura de código
- **pytest-flask** 1.3.0 - Testing para Flask
- **pytest-mock** 3.15.1 - Mocking
- **Cobertura** >73% - Umbral de cobertura de código
- **SonarCloud** - Análisis de calidad de código (bugs, vulnerabilities, code smells)
- **AXE-core** (Playwright) - Pruebas de accesibilidad WCAG 2.1

### Despliegue
- **Gunicorn** 21.2.0 - Servidor WSGI
- **Docker** - Containerización
- **GitHub Actions** - Pipeline CI/CD
- **Azure App Service** - Hosting en la nube (Linux)
- **Azure SQL Database** - Base de datos gestionada

## 📁 Estructura del Proyecto

```
task-forge-api/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuración por entornos
│   ├── models/                  # Modelos de base de datos
│   │   ├── user.py              # User, Role, RefreshToken
│   │   ├── task.py              # Task, TaskStatus, TaskPriority
│   │   └── tag.py               # Tag
│   ├── services/                # Capa de lógica de negocio
│   │   ├── auth_service.py      # Autenticación y autorización
│   │   ├── task_service.py      # Gestión de tareas
│   │   ├── user_service.py      # Gestión de usuarios
│   │   └── tag_service.py       # Gestión de etiquetas
│   ├── routes/                  # Endpoints de la API
│   │   ├── health.py            # Health check
│   │   ├── auth.py              # Autenticación
│   │   ├── tasks.py             # CRUD de tareas
│   │   ├── users.py             # Gestión de usuarios
│   │   └── tags.py              # Gestión de etiquetas
│   ├── middleware/              # Decoradores de Auth y RBAC
│   │   ├── auth.py              # Middleware de autenticación
│   │   └── rbac.py              # Middleware de autorización
│   └── utils/                   # Funciones auxiliares
│       ├── helpers.py           # Paginación, respuestas
│       ├── validators.py        # Validación de inputs
│       └── export.py            # Exportación CSV/JSON
├── tests/                       # Suite de tests (268 tests)
│   ├── conftest.py              # Fixtures de pytest
│   ├── test_auth.py             # Tests de autenticación
│   ├── test_tasks.py            # Tests de tareas
│   ├── test_users.py            # Tests de usuarios
│   ├── test_tags.py             # Tests de etiquetas
│   ├── test_services.py         # Tests de servicios
│   ├── test_models.py           # Tests de modelos
│   ├── test_middleware.py       # Tests de middleware
│   ├── test_helpers.py          # Tests de helpers
│   └── test_validators.py       # Tests de validadores
├── scripts/                     # Scripts de utilidad
│   ├── init_db_azure.sql        # Schema para Azure SQL
│   └── reset_admin_password.py # Resetear contraseña admin
├── docs/                        # Documentación
│   ├── azure-app-service-configuration.md
│   ├── sonarcloud-setup.md
│   └── axe-accessibility.md
├── .github/workflows/           # Pipelines CI/CD
│   ├── code-quality.yml         # Análisis de calidad y accesibilidad
│   └── main_task-forge.yml      # Deployment a Azure
├── Dockerfile
├── docker-compose.yml
├── startup.sh                   # Script de inicio para Azure
├── requirements.txt
├── pytest.ini
├── run.py                       # Punto de entrada
└── README.md
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- Azure SQL Database (o SQLite para desarrollo local)
- Docker (opcional)

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/YamiDarknezz/task-forge-api.git
cd task-forge-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env  # Windows
# o
cp .env.example .env    # Linux/Mac

# Editar .env con tu configuración
```

5. **Inicializar base de datos**

Para Azure SQL:
```bash
# Ejecutar scripts/init_db_azure.sql en Azure Data Studio o SQL Server Management Studio
```

Para SQLite (desarrollo):
```bash
flask init-db
```

6. **Ejecutar la aplicación**
```bash
python run.py
```

La API estará disponible en `http://localhost:5000`

### Despliegue con Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# Acceder a la API en http://localhost:5000
```

## ⚙️ Variables de Entorno

Crear un archivo `.env` basado en `.env.example`:

```env
# Aplicación
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
JWT_SECRET_KEY=tu-clave-jwt-secreta-aqui-cambiar-en-produccion

# Azure SQL Database
AZURE_SQL_SERVER=tuservidor.database.windows.net
AZURE_SQL_DATABASE=taskforge_db
AZURE_SQL_USER=tuusuario
AZURE_SQL_PASSWORD=TuPassword123
AZURE_SQL_PORT=1433

# Configuración JWT
JWT_ACCESS_TOKEN_EXPIRES=3600        # 1 hora
JWT_REFRESH_TOKEN_EXPIRES=2592000    # 30 días

# Rate Limiting
RATELIMIT_ENABLED=true
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=200 per day;50 per hour

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Paginación
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Aplicación
APP_NAME=TaskForge API
APP_VERSION=1.0.0
```

## 📚 Documentación de la API

### Documentación Interactiva

**Producción:** [https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs](https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs)

**Local:** `http://localhost:5000/api/docs`

### Ejemplos de Uso

#### Autenticación

**Registro:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "usuario123",
  "email": "usuario@ejemplo.com",
  "password": "Password123!",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Login:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "Password123!"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "user": {
      "id": 1,
      "username": "usuario123",
      "email": "usuario@ejemplo.com",
      "role": "user"
    }
  }
}
```

**Refrescar Token:**
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Tareas

**Crear Tarea:**
```http
POST /api/tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Completar proyecto",
  "description": "Finalizar la API TaskForge",
  "priority": "high",
  "status": "in_progress",
  "due_date": "2024-12-31T23:59:59",
  "tags": [1, 2]
}
```

**Obtener Tareas (con filtros):**
```http
GET /api/tasks?status=pending&priority=high&page=1&per_page=10&sort_by=due_date&sort_order=asc
Authorization: Bearer <access_token>
```

**Exportar Tareas:**
```http
GET /api/tasks/export?format=csv
Authorization: Bearer <access_token>
```

**Estadísticas:**
```http
GET /api/tasks/statistics
Authorization: Bearer <access_token>
```

## 🧪 Testing

Ejecutar la suite de tests:

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Ejecutar tests específicos
pytest tests/test_auth.py

# Ejecutar con verbosidad
pytest -v

# Ver reporte de cobertura en navegador
# El reporte se genera en htmlcov/index.html
```

### Resultados de Testing

- **Total de Tests**: 268 ✅
- **Tests Pasando**: 268 ✅
- **Cobertura de Código**: >73%
- **Líneas Cubiertas**: 1,053+ / 1,441

### Categorías de Tests

- ✅ Tests de Autenticación (17 tests)
- ✅ Tests de Tareas (22 tests)
- ✅ Tests de Usuarios (18 tests)
- ✅ Tests de Etiquetas (18 tests)
- ✅ Tests de Servicios (72 tests)
- ✅ Tests de Modelos (23 tests)
- ✅ Tests de Middleware (11 tests)
- ✅ Tests de Helpers (29 tests)
- ✅ Tests de Validadores (58 tests)

## 📊 Calidad de Código y Accesibilidad

### SonarCloud - Análisis de Calidad

El proyecto utiliza **SonarCloud** para análisis automático de calidad de código en cada push/PR.

**Qué analiza:**
- 🐛 **Bugs** - Errores en el código
- 🔒 **Vulnerabilities** - Problemas de seguridad
- 💡 **Code Smells** - Código difícil de mantener
- 📊 **Coverage** - Cobertura de tests (>73%)
- 🔁 **Duplications** - Código duplicado

**Dashboard:** [Ver métricas en SonarCloud →](https://sonarcloud.io/summary/new_code?id=YamiDarknezz_task-forge-api)

**Ejecución:**
- Automática en GitHub Actions (cada push/PR)
- Ver workflow [`code-quality.yml`](.github/workflows/code-quality.yml)

Consulta la [guía de SonarCloud](docs/sonarcloud-setup.md) para más información.

---

### AXE - Pruebas de Accesibilidad

Pruebas automatizadas de accesibilidad para el Swagger UI usando **AXE-core** y **Playwright**.

**Qué verifica:**
- ♿ **WCAG 2.1 AA** - Estándares de accesibilidad
- 🎨 **Contraste de colores** - Legibilidad
- 🏷️ **Labels y ARIA** - Lectores de pantalla
- ⌨️ **Navegación por teclado** - Usabilidad

**Ejecución local:**
```powershell
.\tests\accessibility\run-axe-local.ps1
```

**Ejecución automática:**
- Se ejecuta en GitHub Actions
- Genera reporte HTML descargable
- Ver workflow [`code-quality.yml`](.github/workflows/code-quality.yml)

Consulta la [guía de AXE](docs/axe-accessibility.md) para más información.

---

## 🔄 Pipeline CI/CD

El proyecto incluye dos workflows de GitHub Actions separados:

### 1. Code Quality Analysis ([`code-quality.yml`](.github/workflows/code-quality.yml))
- **SonarCloud** - Análisis de calidad de código
- **AXE** - Pruebas de accesibilidad
- Se ejecuta en cada `push` y `pull_request`
- No bloquea el deployment

### 2. Azure Deployment ([`main_task-forge.yml`](.github/workflows/main_task-forge.yml))
- **Build** - Instalación de dependencias y creación de artefacto
- **Test** - Ejecución de pytest con requisito de cobertura (>70%)
- **Deploy** - Despliegue a Azure App Service con autenticación OIDC
- Se ejecuta en push a `main`/`master`

**Flujo de Deployment:**
```
Push → Build → Test → Deploy → Azure App Service
         ↓        ↓
    requirements pytest
         ↓     >70% coverage
    artifact.zip
```

### Secrets Requeridos en GitHub

**Para Azure Deployment:**
- `AZUREAPPSERVICE_CLIENTID_*` - Client ID de Azure
- `AZUREAPPSERVICE_TENANTID_*` - Tenant ID de Azure
- `AZUREAPPSERVICE_SUBSCRIPTIONID_*` - Subscription ID de Azure

**Para Code Quality:**
- `SONAR_TOKEN` - Token de SonarCloud (ver [guía de setup](docs/sonarcloud-setup.md))

## ☁️ Deployment en Azure

### Configuración en Azure App Service

El proyecto está configurado para desplegarse en **Azure App Service (Linux)** con las siguientes características:

**Stack:**
- Runtime: Python 3.11
- Startup Command: `bash startup.sh`
- Web Server: Gunicorn (4 workers)

**Variables de Entorno Configuradas:**
- `FLASK_ENV=production`
- `SECRET_KEY` - Clave secreta de la aplicación
- `JWT_SECRET_KEY` - Clave para tokens JWT
- `AZURE_SQL_*` - Credenciales de Azure SQL Database

**URL de Producción:**
[https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net](https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net)

**Documentación API:**
[https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs](https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs)

### Guía de Configuración

Para configurar tu propio deployment en Azure, consulta:
- [Azure App Service Configuration Guide](docs/azure-app-service-configuration.md)
- [Azure Quick Fix Guide](AZURE_QUICK_FIX.md)

## 🗄️ Esquema de Base de Datos

### Tablas

- **roles** - Roles de usuarios (admin, user)
- **users** - Cuentas de usuario con autenticación
- **refresh_tokens** - Tokens JWT de refresco
- **tasks** - Gestión de tareas
- **tags** - Categorización de tareas
- **task_tags** - Relación many-to-many entre tasks y tags

Ver `scripts/init_db_azure.sql` para el esquema completo.

### Diagrama ER

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    roles    │       │    users     │       │    tasks    │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ id (PK)      │───┐   │ id (PK)     │
│ name        │   └──<│ role_id (FK) │   └──<│ user_id (FK)│
│ description │       │ username     │       │ title       │
└─────────────┘       │ email        │       │ description │
                      │ password     │       │ status      │
                      └──────────────┘       │ priority    │
                                             │ due_date    │
                      ┌──────────────┐       └─────────────┘
                      │refresh_tokens│              │
                      ├──────────────┤              │
                      │ id (PK)      │              │
                      │ user_id (FK) │         ┌────┴────┐
                      │ token        │         │task_tags│
                      │ expires_at   │         ├─────────┤
                      └──────────────┘         │task_id  │
                                               │tag_id   │
                      ┌─────────────┐          └────┬────┘
                      │    tags     │               │
                      ├─────────────┤               │
                      │ id (PK)     │───────────────┘
                      │ name        │
                      │ color       │
                      │ user_id (FK)│
                      └─────────────┘
```

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT con expiración configurable
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Rate limiting en todos los endpoints
- ✅ Configuración CORS
- ✅ Protección contra inyección SQL vía SQLAlchemy ORM
- ✅ Validación de inputs
- ✅ Refresh tokens almacenados en base de datos con revocación
- ✅ HTTPS forzado en producción
- ✅ Debug mode desactivado en producción

## 📈 Rate Limiting

Límites por defecto:
- 200 peticiones por día
- 50 peticiones por hora

Personalizable en el archivo `.env` con la variable `RATELIMIT_DEFAULT`.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

**Requisitos para PRs:**
- ✅ Tests pasando (pytest)
- ✅ Cobertura >70%
- ✅ SonarCloud Quality Gate passing
- ✅ Sin vulnerabilidades de seguridad

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## 👤 Autor

**Erick (YamiDarknezz)**
- GitHub: [@YamiDarknezz](https://github.com/YamiDarknezz)
- Proyecto: [TaskForge API](https://github.com/YamiDarknezz/task-forge-api)
- Demo: [API en Producción](https://task-forge-gbd6h8gtg8hchve9.chilecentral-01.azurewebsites.net/api/docs)

## 🙏 Agradecimientos

- Documentación de Flask
- Documentación de SQLAlchemy
- Documentación de Azure
- Comunidad de pytest
- Documentación de GitHub Actions
- SonarCloud por el análisis de calidad de código
- AXE-core por las herramientas de accesibilidad

## 📊 Estadísticas del Proyecto

- **Líneas de Código**: ~1,500+ (app)
- **Tests**: 268
- **Cobertura**: >73%
- **Endpoints**: 30+
- **Modelos**: 6
- **Servicios**: 4
- **Tiempo de Build**: ~3 minutos
- **Tiempo de Deployment**: ~2 minutos

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub!**

🚀 **Desarrollado con Flask, Python y mucho ☕**
