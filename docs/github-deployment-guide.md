# Guía de Deployment a GitHub

Esta guía explica **paso a paso** cómo subir tu proyecto a GitHub con SonarCloud y AXE configurados, sin afectar el deployment a Azure.

## 📋 Checklist Pre-Push

Antes de hacer push a GitHub, asegúrate de tener:

- [x] Sincronizado GitHub con SonarCloud ✅ (Ya completado)
- [ ] `sonar-project.properties` actualizado con tu info real
- [ ] Badges en README actualizados con tu PROJECT_KEY
- [ ] `SONAR_TOKEN` listo para configurar en GitHub

---

## 🔧 Paso 1: Actualizar sonar-project.properties

Abre el archivo `sonar-project.properties` y actualiza estas líneas:

```properties
# Reemplaza con tu información real de SonarCloud
sonar.projectKey=TU_ORG_task-forge-api
sonar.organization=tu-organizacion
```

**¿Dónde encuentro estos valores?**

1. Ve a [SonarCloud.io](https://sonarcloud.io)
2. Click en tu proyecto **task-forge-api**
3. En el menú izquierdo, click en **Project Information**
4. Copia el **Project Key** y **Organization Key**

**Ejemplo real:**
```properties
sonar.projectKey=YamiDarknezz_task-forge-api
sonar.organization=yamidarknezz
```

---

## 🏷️ Paso 2: Actualizar Badges en README

Abre `README.md` y busca la sección de badges (línea ~7).

Reemplaza `YOUR_PROJECT_KEY` con tu `sonar.projectKey` real:

**Antes:**
```markdown
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=YOUR_PROJECT_KEY&metric=alert_status)]...
```

**Después:**
```markdown
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=YamiDarknezz_task-forge-api&metric=alert_status)]...
```

Haz esto para **TODOS** los badges (6 en total).

---

## 💾 Paso 3: Verificar Archivos Creados

Verifica que tengas todos estos archivos nuevos:

```
✅ .github/workflows/code-quality.yml
✅ sonar-project.properties
✅ package.json
✅ tests/accessibility/axe-swagger-test.js
✅ tests/accessibility/run-axe-local.ps1
✅ docs/sonarcloud-setup.md
✅ docs/axe-accessibility.md
✅ docs/presentation-guide.md
✅ .gitignore (actualizado)
✅ README.md (actualizado)
```

---

## 📤 Paso 4: Commit y Push a GitHub

### 4.1 Revisar Cambios

```powershell
# Ver archivos modificados/nuevos
git status
```

Deberías ver algo como:
```
modified:   .gitignore
modified:   README.md
new file:   .github/workflows/code-quality.yml
new file:   sonar-project.properties
new file:   package.json
new file:   tests/accessibility/axe-swagger-test.js
new file:   tests/accessibility/run-axe-local.ps1
new file:   docs/sonarcloud-setup.md
new file:   docs/axe-accessibility.md
new file:   docs/presentation-guide.md
```

### 4.2 Agregar Archivos

```powershell
# Agregar todos los archivos
git add .

# O agregar específicamente
git add .github/workflows/code-quality.yml
git add sonar-project.properties
git add package.json
git add tests/accessibility/
git add docs/
git add .gitignore
git add README.md
```

### 4.3 Commit

```powershell
git commit -m "feat: add SonarCloud and AXE accessibility analysis

- Configure SonarCloud integration via GitHub Actions
- Add AXE accessibility testing for Swagger UI
- Create comprehensive documentation guides
- Update README with badges and quality metrics
- Add separate code-quality workflow independent of Azure deployment"
```

### 4.4 Push a GitHub

```powershell
# Si es tu primer push
git push -u origin main

# O si ya existe
git push origin main
```

---

## 🔑 Paso 5: Configurar SONAR_TOKEN en GitHub

**IMPORTANTE:** Esto debe hacerse ANTES de que el workflow se ejecute.

### 5.1 Obtener Token de SonarCloud

1. Ve a [SonarCloud.io](https://sonarcloud.io)
2. Click en tu avatar (esquina superior derecha)
3. **My Account > Security**
4. En **Generate Tokens**:
   - Name: `GitHub Actions TaskForge`
   - Type: `User Token`
   - Expiration: `No expiration` (o 90 días)
   - Click **Generate**
5. **Copia el token** (solo se muestra una vez)

### 5.2 Configurar Secret en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (del repositorio)
3. En el menú izquierdo: **Secrets and variables > Actions**
4. Click en **"New repository secret"**
5. Configura:
   - **Name:** `SONAR_TOKEN`
   - **Secret:** Pega el token copiado
6. Click **"Add secret"**

---

## ✅ Paso 6: Verificar Workflows

### 6.1 Ir a GitHub Actions

1. En tu repositorio, click en pestaña **Actions**
2. Deberías ver dos workflows:
   - ✅ **Code Quality Analysis** (nuevo)
   - ✅ **Build, Test and Deploy Flask API to Azure Web App** (existente)

### 6.2 Ver Ejecución de Code Quality

1. Click en el workflow **"Code Quality Analysis"**
2. Click en la ejecución más reciente
3. Deberías ver dos jobs:
   - `sonarcloud` - Análisis de SonarCloud
   - `accessibility` - Pruebas AXE

**Primera ejecución puede tomar 3-5 minutos.**

### 6.3 Esperar Resultados

**Si pasa exitosamente ✅:**
- Ve a [SonarCloud.io](https://sonarcloud.io)
- Abre tu proyecto
- Verás las métricas actualizadas
- Los badges en el README mostrarán datos reales

**Si falla ❌:**
- Click en el job que falló
- Revisa los logs para ver el error
- Causas comunes:
  - `SONAR_TOKEN` no configurado o inválido
  - `sonar.projectKey` incorrecto en `sonar-project.properties`
  - Permisos insuficientes en SonarCloud

---

## 🚀 Paso 7: Verificar Azure Deployment (No Se Afecta)

### 7.1 Revisar Workflow de Azure

1. En **GitHub Actions**, busca el workflow:
   - **"Build, Test and Deploy Flask API to Azure Web App"**
2. Verifica que se ejecute normalmente
3. **Debe completarse sin errores**

### 7.2 Verificar Separación

Los workflows están **completamente separados**:

**Code Quality (`code-quality.yml`):**
- Se ejecuta en: `push` y `pull_request`
- Solo analiza código
- No toca Azure
- Trabaja con `SONAR_TOKEN`

**Azure Deployment (`azure-deploy.yml`):**
- Se ejecuta en: push a `main`/`master`
- Build, test, y deploy
- Usa secrets de Azure
- **No usa ni requiere** `SONAR_TOKEN`

**CONFIRMACIÓN:** Si Azure deployment sigue funcionando = ✅ Éxito

---

## 📊 Paso 8: Actualizar README Badges (Post-Primera Ejecución)

Después de que el primer análisis de SonarCloud complete:

### 8.1 Verificar Badges

1. Abre tu README en GitHub
2. Los badges deberían mostrar métricas reales:
   - Quality Gate: Passing/Failed
   - Coverage: 73%
   - Bugs: número real
   - Vulnerabilities: número real

### 8.2 Si los Badges No Cargan

Puede tomar algunos minutos. Verifica:
- El `projectKey` en los URLs de badges es correcto
- SonarCloud completó el análisis
- Refresca la página del README

---

## 🎯 Paso 9: Descargar Reportes de AXE

### 9.1 Acceder a Artifacts

1. En GitHub Actions, abre el workflow **"Code Quality Analysis"**
2. Click en la ejecución más reciente
3. Scroll hasta **Artifacts** (al final)
4. Descarga **"axe-accessibility-report"**

### 9.2 Ver Reporte

1. Descomprime el archivo
2. Abre el archivo HTML
3. Verás el reporte detallado de accesibilidad

**Guarda este reporte** para tu presentación de mañana.

---

## 📝 Paso 10: Preparar para Presentación

### 10.1 Capturar Screenshots

Toma screenshots de:

1. **README con badges** (GitHub)
2. **SonarCloud dashboard** (Overview)
3. **SonarCloud métricas detalladas** (Bugs, Vulnerabilities, Coverage)
4. **GitHub Actions** (ambos workflows passing)
5. **Reporte HTML de AXE** (Summary y 1-2 violaciones)

### 10.2 Revisar Documentación

Lee estas guías:
- [`docs/presentation-guide.md`](docs/presentation-guide.md) - Script completo
- [`docs/sonarcloud-setup.md`](docs/sonarcloud-setup.md) - Detalles técnicos
- [`docs/axe-accessibility.md`](docs/axe-accessibility.md) - Explicación de AXE

### 10.3 Practicar Demo

Practica mostrar:
1. Badges en README (30 seg)
2. SonarCloud dashboard (2 min)
3. Reporte de AXE (2 min)
4. GitHub Actions workflows (1 min)

**Total: 5-6 minutos de demo**

---

## ✅ Checklist Final

Antes de tu presentación, verifica:

- [ ] Push completo a GitHub
- [ ] Workflow "Code Quality Analysis" pasó ✅
- [ ] Workflow "Azure Deployment" pasó ✅ (sin afectarse)
- [ ] SonarCloud muestra métricas
- [ ] Badges en README funcionan
- [ ] Reporte de AXE descargado
- [ ] Screenshots capturados
- [ ] Guía de presentación revisada
- [ ] Tabs del navegador preparados
- [ ] Código en `sonar-project.properties` correcto

---

## 🆘 Troubleshooting

### "No module named 'playwright'"
El workflow de GitHub Actions instala automáticamente. Si pruebas localmente:
```powershell
npm install
npx playwright install chromium
```

### "SonarCloud analysis failed"
Verifica:
1. `SONAR_TOKEN` configurado en GitHub Secrets
2. `sonar.projectKey` correcto
3. Organización existe en SonarCloud

### "AXE job failed"
Revisa logs. Causas comunes:
- API no inició correctamente
- Timeout esperando API
- Navegación a Swagger falló

### "Azure deployment failed after code-quality changes"
**No debería pasar.** Los workflows son independientes. Si pasa:
1. Revisa cambios en `.github/workflows/azure-deploy.yml` (no debería haber)
2. Verifica secrets de Azure no se modified
3. Rollback si es necesario

---

## 🎉 ¡Listo!

Una vez completados todos los pasos:

✅ **SonarCloud** analiza tu código automáticamente  
✅ **AXE** verifica accesibilidad en cada push  
✅ **Badges** muestran métricas en tiempo real  
✅ **Azure deployment** funciona independientemente  
✅ **Documentación** completa para portfolio  

**Tu proyecto ahora demuestra:**
- Conocimiento de CI/CD
- Preocupación por calidad de código
- Awareness de accesibilidad
- Best practices de la industria
- Separación de concerns (CI vs CD)

---

## 📞 Soporte

Si tienes problemas:
1. Revisa esta guía paso a paso
2. Consulta los logs de GitHub Actions
3. Lee las guías en `/docs`
4. Busca el error en Google/StackOverflow
5. Verifica la configuración de SonarCloud

**Para tu presentación de mañana:**
- Revisa [`docs/presentation-guide.md`](docs/presentation-guide.md)
- Practica el script
- Prepara Plan B (screenshots)

---

**¡Mucha suerte con tu presentación! 🚀**
