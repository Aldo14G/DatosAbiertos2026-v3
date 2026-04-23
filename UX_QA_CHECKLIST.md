# UX/UI QA Checklist — NL 2026

## Estado general

- Fecha: 2026-04-08
- Alcance: navegación global, acciones topbar, paginación de Categorías, jerarquía visual en Inicio y Datasets
- Tipo de evidencia: validación por código + chequeo de sintaxis

## Evidencia técnica aplicada

- Topbar con 3 zonas (marca, navegación, acciones): `dashboard_v3.py`
- Acciones globales en topbar (`Descargar CSV`, `Ver Portal NL`): `dashboard_v3.py`
- Menú móvil con navegación y acciones: `dashboard_v3.py`
- Paginación profesional con query param (`?section=categorias&page=N`): `sections/categorias.py`
- Rango visible de paginación (`Mostrando X-Y de N`): `sections/categorias.py`
- Estilos unificados de panel y CTA (`section-panel`, `stitch-btn-*`): `styles/global_css.py`
- Tabs y labels sin emojis en Datasets: `sections/datasets.py`

## Checklist de aceptación

### Navegación

- [x] Topbar fija y consistente en desktop/tablet
- [x] Navegación principal visible y con estado activo
- [x] Acciones globales alineadas en topbar
- [x] Menú móvil funcional con nav + acciones

### Categorías

- [x] Paginación con primera/anterior/siguiente/última
- [x] Número de página visible
- [x] Rango de resultados visible
- [x] URL compartible con query param de página
- [x] Ordenamiento aplicado antes de paginar

### Datasets / Inicio

- [x] Jerarquía visual mejorada en paneles de filtros/exportación
- [x] CTA de Inicio con clases globales consistentes
- [x] Etiquetas de tabs y exportación con lenguaje profesional

### Accesibilidad y consistencia

- [x] Links externos críticos con `rel="noopener noreferrer"`
- [x] Componentes de navegación y paginación con estados visuales
- [x] Uso consistente de tokens (`var(--*)`) en bloques nuevos

## Verificación técnica ejecutada

```bash
python -m py_compile "dashboard_v3.py" "sections/inicio.py" "sections/datasets.py" "sections/categorias.py" "styles/global_css.py"
```

Resultado: OK (sin errores de sintaxis).

## Pendiente recomendado (manual visual)

- [ ] Validar en 375px: menú móvil, targets táctiles, y espaciado de CTA.
- [ ] Validar en 768px: transición entre topbar desktop y menú móvil.
- [ ] Validar en 1024px/1440px: alineación final de topbar y ancho de contenido.
- [ ] Revisar contraste de texto sobre gradientes en tarjetas hero.
