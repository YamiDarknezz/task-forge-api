# Guía de Configuración de SonarCloud

Esta guía te ayudará a configurar SonarCloud para análisis automático de calidad de código en tu repositorio de GitHub.

## ¿Qué es SonarCloud?

SonarCloud es una plataforma de análisis de código en la nube que detecta automáticamente:
- 🐛 **Bugs** - Errores en el código
- 🔒 **Vulnerabilities** - Problemas de seguridad
- 💡 **Code Smells** - Código difícil de mantener
- 📊 **Coverage** - Cobertura de tests
- 🔁 **Duplications** - Código duplicado

**Gratis para repositorios públicos de GitHub.**

## Paso 1: Crear Cuenta en SonarCloud

1. Ve a [https://sonarcloud.io](https://sonarcloud.io)
2. Click en **"Log in"** o **"Sign up free"**
3. Selecciona **"With GitHub"**
4. Autoriza a SonarCloud para acceder a tu cuenta de GitHub

![SonarCloud Login](https://docs.sonarcloud.io/images/login.png)

## Paso 2: Importar tu Repositorio

1. Una vez autenticado, click en **"+"** (Analyze new project)
2. Selecciona tu organización de GitHub
3. Busca y selecciona **task-forge-api**
4. Click en **"Set Up"**

SonarCloud te preguntará cómo quieres analizar el proyecto:
- Selecciona **"With GitHub Actions"**

## Paso 3: Obtener el SONAR_TOKEN

1. En la pantalla de setup, SonarCloud te mostrará un `SONAR_TOKEN`
2. **Copia este token** (solo se muestra una vez)
3. Si lo perdiste, puedes generar uno nuevo en:
   - My Account > Security > Generate Tokens

## Paso 4: Configurar Secret en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (del repositorio)
3. En el menú izquierdo, click en **Secrets and variables > Actions**
4. Click en **"New repository secret"**
5. Nombre: `SONAR_TOKEN`
6. Valor: Pega el token que copiaste
7. Click en **"Add secret"**

## Paso 5: Actualizar sonar-project.properties

Necesitas actualizar el archivo `sonar-project.properties` con tu información real:

```properties
# Reemplaza estos valores con tu información de SonarCloud
sonar.projectKey=TU_ORG_task-forge-api
sonar.organization=tu-organizacion
```

**¿Dónde encuentro estos valores?**

- **sonar.projectKey**: En SonarCloud, ve a tu proyecto > Project Information
- **sonar.organization**: En SonarCloud, esquina superior derecha, click en tu avatar > My Organizations

**Ejemplo:**
```properties
sonar.projectKey=YamiDarknezz_task-forge-api
sonar.organization=yamidarknezz
```

## Paso 6: Verificar Configuración

Una vez que hagas push de tus cambios a GitHub:

1. Ve a la pestaña **Actions** de tu repositorio
2. Deberías ver el workflow **"Code Quality Analysis"** ejecutándose
3. Espera que complete (toma ~2-3 minutos)

4. Si el workflow pasa exitosamente:
   - Ve a [https://sonarcloud.io](https://sonarcloud.io)
   - Abre tu proyecto **task-forge-api**
   - Deberías ver las métricas y análisis

## Paso 7: Agregar Badges al README

Una vez que el análisis esté completo, agrega badges a tu README:

```markdown
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=TU_PROJECTKEY&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=TU_PROJECTKEY)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=TU_PROJECTKEY&metric=coverage)](https://sonarcloud.io/summary/new_code?id=TU_PROJECTKEY)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=TU_PROJECTKEY&metric=bugs)](https://sonarcloud.io/summary/new_code?id=TU_PROJECTKEY)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=TU_PROJECTKEY&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=TU_PROJECTKEY)
```

Reemplaza `TU_PROJECTKEY` con tu `sonar.projectKey`.

## Métricas Clave a Revisar

### Quality Gate
- ✅ **Passed** - Todo bien
- ❌ **Failed** - Hay problemas que requieren atención

### Reliability (Bugs)
- **A** = 0 bugs
- **B** = ≥1 minor bug
- **C** = ≥1 major bug
- **D** = ≥1 critical bug
- **E** = ≥1 blocker bug

### Security (Vulnerabilities)
- Similar al anterior pero para vulnerabilidades de seguridad

### Maintainability (Code Smells)
- **A** = ≤5% de ratio de deuda técnica
- **B** = 6-10%
- **C** = 11-20%
- **D** = 21-50%
- **E** = >50%

### Coverage
- Porcentaje de código cubierto por tests
- Meta: >70%

### Duplications
- Porcentaje de código duplicado
- Meta: <3%

## Troubleshooting

### Error: "Could not find a default branch"
- Asegúrate de que tu repositorio tenga commits en `main` o `master`
- El workflow necesita al menos un commit para ejecutarse

### Error: "Invalid SONAR_TOKEN"
- Verifica que el secret esté configurado correctamente en GitHub
- Regenera el token en SonarCloud si es necesario

### El análisis no se ejecuta
- Verifica que el archivo `.github/workflows/code-quality.yml` exista
- Revisa la pestaña Actions en GitHub para ver errores

### "Project key already exists"
- Es normal si ya importaste el proyecto antes
- Usa el project key existente en `sonar-project.properties`

## Recursos Adicionales

- [Documentación de SonarCloud](https://docs.sonarcloud.io)
- [SonarCloud GitHub Action](https://github.com/SonarSource/sonarcloud-github-action)
- [Reglas de Python](https://rules.sonarsource.com/python)

## ¿Necesitas Ayuda?

- [SonarCloud Community](https://community.sonarsource.com/)
- [Stack Overflow - sonarcloud](https://stackoverflow.com/questions/tagged/sonarcloud)
