# Guía de Pruebas de Accesibilidad con AXE

Esta guía explica cómo ejecutar y entender las pruebas de accesibilidad automatizadas para el Swagger UI de TaskForge API.

## ¿Qué es Accesibilidad Web?

La accesibilidad web significa que personas con discapacidades pueden usar la web. Específicamente:
- 👁️ **Personas ciegas** - Usan lectores de pantalla
- 🦻 **Personas sordas** - Necesitan subtítulos/transcripciones
- 🖱️ **Limitaciones motoras** - Navegación por teclado
- 🧠 **Discapacidades cognitivas** - Contenido claro y simple

### WCAG 2.1

Las **Web Content Accessibility Guidelines (WCAG) 2.1** son el estándar internacional.

**Niveles de conformidad:**
- **Nivel A** - Requisitos básicos
- **Nivel AA** - ⭐ Estándar recomendado (nuestro objetivo)
- **Nivel AAA** - Máximo nivel de accesibilidad

## ¿Qué es AXE?

AXE es una herramienta de testing de accesibilidad desarrollada por Deque Systems:
- 🤖 **Automatizada** - Detecta problemas sin intervención manual
- 🎯 **Precisa** - Muy pocos falsos positivos
- 📚 **Educativa** - Explica problemas y cómo corregirlos
- 🆓 **Open Source** - Gratis y de código abierto

**Cubre ~57% de issues WCAG** que pueden detectarse automáticamente.

## Ejecución Local

### Requisitos Previos

- Node.js 18+ instalado
- Python 3.11+ instalado
- API de TaskForge funcionando

### Paso 1: Verificar Requisitos

```powershell
# Verificar Node.js
node --version
# Debe mostrar v18.x.x o superior

# Verificar Python
python --version
# Debe mostrar 3.11.x
```

### Paso 2: Ejecutar Pruebas

```powershell
# Desde la raíz del proyecto
.\tests\accessibility\run-axe-local.ps1
```

El script automáticamente:
1. ✅ Instala dependencias NPM (primera vez)
2. ✅ Instala navegadores Playwright (primera vez)
3. ✅ Inicia la API Flask
4. ✅ Espera a que esté lista
5. ✅ Ejecuta análisis AXE
6. ✅ Genera reporte HTML
7. ✅ Abre el reporte en tu navegador
8. ✅ Detiene la API

### Paso 3: Revisar Resultados

El reporte HTML se abre automáticamente y muestra:

**Resumen en consola:**
```
AXE ACCESSIBILITY TEST RESULTS
=============================================================
✅ Passed rules: 45
⚠️  Incomplete rules: 3
❌ Violations found: 12

VIOLATIONS BY SEVERITY:
  🟠 Serious: 3
  🟡 Moderate: 6
  🔵 Minor: 3
```

**Reporte HTML completo:**
- Detalles de cada violación
- Elementos afectados
- Cómo corregir
- Enlaces a documentación

## Ejecución en GitHub Actions

Las pruebas AXE se ejecutan automáticamente en cada push/PR.

### Ver Resultados en GitHub

1. Ve a tu repositorio en GitHub
2. Click en pestaña **Actions**
3. Selecciona el workflow **"Code Quality Analysis"**
4. Click en la ejecución más reciente
5. Busca el job **"Accessibility Testing (AXE)"**

### Descargar Reporte

1. En la página del workflow, scroll hasta **Artifacts**
2. Descarga **"axe-accessibility-report"**
3. Descomprime y abre el archivo HTML

## Interpretación de Resultados

### Niveles de Severidad

#### 🔴 Critical
- **Impacto:** Bloqueador
- **Ejemplos:** 
  - Imágenes sin texto alternativo
  - Forms sin labels
  - Missing page title
- **Acción:** Corregir inmediatamente

#### 🟠 Serious
- **Impacto:** Alto
- **Ejemplos:**
  - Contraste de colores insuficiente
  - Missing ARIA labels
  - Estructura de headings incorrecta
- **Acción:** Corregir antes de producción

#### 🟡 Moderate
- **Impacto:** Medio
- **Ejemplos:**
  - Missing landmarks
  - Botones sin texto descriptivo
  - Links sin contexto claro
- **Acción:** Corregir cuando sea posible

#### 🔵 Minor
- **Impacto:** Bajo
- **Ejemplos:**
  - Mejoras de navegación por teclado
  - Orden de tab mejorable
  - Redundancia en ARIA
- **Acción:** Nice to have

### Reglas Comunes

#### color-contrast
**Qué detecta:** Texto con contraste insuficiente vs fondo

**Ejemplo de violación:**
```html
<!-- Texto gris claro sobre fondo blanco -->
<p style="color: #ccc; background: #fff">Texto difícil de leer</p>
```

**Cómo corregir:**
```html
<!-- Texto con contraste suficiente (>4.5:1 para texto normal) -->
<p style="color: #555; background: #fff">Texto legible</p>
```

**Tools:** [Contrast Checker](https://webaim.org/resources/contrastchecker/)

#### label
**Qué detecta:** Inputs sin labels asociados

**Ejemplo de violación:**
```html
<input type="text" name="username">
```

**Cómo corregir:**
```html
<label for="username">Usuario:</label>
<input type="text" id="username" name="username">
```

#### heading-order
**Qué detecta:** Jerarquía de headings incorrecta

**Ejemplo de violación:**
```html
<h1>Título Principal</h1>
<h3>Subtítulo</h3> <!-- Salta h2 -->
```

**Cómo corregir:**
```html
<h1>Título Principal</h1>
<h2>Subtítulo</h2>
<h3>Sub-subtítulo</h3>
```

#### image-alt
**Qué detecta:** Imágenes sin atributo alt

**Ejemplo de violación:**
```html
<img src="logo.png">
```

**Cómo corregir:**
```html
<img src="logo.png" alt="TaskForge Logo">
<!-- O si es decorativa: -->
<img src="decoration.png" alt="">
```

## Accesibilidad en APIs / Swagger

Aunque TaskForge es una API, el Swagger UI debe ser accesible:

### ✅ Buenas Prácticas

1. **Descripciones claras** en documentación Swagger
2. **Ejemplos comprensibles** en requests/responses
3. **Mensajes de error descriptivos** (ya implementado)
4. **Estructura semántica** en Swagger UI

### ⚠️ Limitaciones

- Swagger UI es un componente de terceros
- No podemos modificar completamente su HTML
- Algunas violaciones son inherentes a Flasgger/Swagger UI
- Enfocarse en violaciones **Critical** y **Serious**

### 📊 Métricas Esperadas para Swagger UI

Basado en experiencias con Flasgger:
- **Critical:** 0-2 (objetivo: 0)
- **Serious:** 2-5 (objetivo: <3)
- **Moderate:** 5-10 (aceptable)
- **Minor:** 10-20 (aceptable)

## Correcciones Comunes

### Para Swagger/Flasgger

La mayoría de issues de Swagger UI no los podemos corregir directamente, pero:

1. **Asegurar documentación clara:**
```python
@swag_from({
    'summary': 'Obtener todas las tareas',
    'description': 'Retorna una lista paginada de tareas del usuario autenticado',
    # ... más descripción
})
```

2. **Mensajes de error accesibles:**
```python
# Ya implementado en tu API
return jsonify({'mensaje': 'Usuario no encontrado'}), 404
```

3. **Estructura de respuestas consistente:**
```python
# Estructura clara y predecible
{
    "success": true,
    "data": {...},
    "pagination": {...}
}
```

## Testing Manual Adicional

AXE detecta ~57% de issues. Testing manual complementario:

### 1. Navegación por Teclado
- Tab para navegar entre elementos
- Enter/Space para activar botones
- Esc para cerrar modales

### 2. Lector de Pantalla
- Windows: NVDA (gratis)
- Mac: VoiceOver (integrado)
- Verificar que todo se lea correctamente

### 3. Zoom
- Probar con zoom 200%
- Todo debe ser usable

## Recursos Adicionales

### Herramientas
- [AXE DevTools](https://www.deque.com/axe/devtools/) - Extensión de Chrome/Firefox
- [WAVE](https://wave.webaim.org/) - Evaluador web
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Integrado en Chrome

### Documentación
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [AXE Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [WebAIM](https://webaim.org/) - Tutoriales y recursos

### Cursos
- [Web Accessibility by Google](https://www.udacity.com/course/web-accessibility--ud891) - Gratis
- [Microsoft Learn - Accessibility](https://learn.microsoft.com/en-us/training/paths/accessibility-fundamentals/)

## Para tu Presentación

### Talking Points

1. **"Implementé pruebas de accesibilidad automatizadas"**
   - Demuestra compromiso con inclusividad
   - No solo funcionalidad, también UX para todos

2. **"Uso AXE-core para cumplir WCAG 2.1 AA"**
   - Estándar internacional
   - Requerimiento legal en muchos países

3. **"Se ejecuta automáticamente en CI/CD"**
   - Catch issues antes de deployment
   - Parte del quality gate

### Mostrar Resultados

1. Ejecutar `.\tests\accessibility\run-axe-local.ps1`
2. Mostrar consola con resumen
3. Abrir reporte HTML
4. Explicar 2-3 violaciones encontradas
5. Mostrar cómo se corregirían

### Métricas para Destacar

- "X reglas pasadas de Y total"
- "Nivel de severidad más alto: Y"
- "Compatible con WCAG 2.1 nivel AA en Z%"

## Conclusión

La accesibilidad no es opcional - **es un derecho**.

Implementar testing automatizado con AXE:
- ✅ Demuestra profesionalismo
- ✅ Mejora UX para todos los usuarios
- ✅ Reduce riesgo legal
- ✅ Se ve genial en tu portafolio 😉
