---
name: skill-creator
description: Guía al agente en la creación de nuevas habilidades (skills) para Antigravity en español, siguiendo los estándares oficiales.
---

# Creador de Habilidades

Esta habilidad te permite crear y estructurar nuevas habilidades (skills) de manera consistente dentro del espacio de trabajo. Las habilidades son paquetes de conocimiento que extienden tus capacidades.

## Cuándo usar esta habilidad
- Cuando el usuario te pida crear una nueva habilidad.
- Cuando necesites estructurar conocimientos específicos o flujos de trabajo repetitivos.
- Cuando quieras mejorar la documentación de cómo realizas ciertas tareas.

## Estructura de una Habilidad
Una habilidad se organiza en una carpeta dentro de `.agents/skills/` con la siguiente estructura:
- `SKILL.md`: El archivo principal con instrucciones y frontmatter YAML.
- `scripts/`: (Opcional) Scripts de automatización o ayuda.
- `examples/`: (Opcional) Ejemplos de uso o implementaciones de referencia.
- `resources/`: (Opcional) Plantillas, imágenes o activos necesarios.

## Instrucciones para crear una nueva habilidad
1. **Definir el propósito**: Asegúrate de que la habilidad tenga un enfoque único y claro.
2. **Crear la carpeta**: `mkdir .agents/skills/<nombre-de-la-habilidad>`
3. **Escribir el SKILL.md**:
    - Incluye el frontmatter con `name` y `description` (obligatorio).
    - Usa Markdown para detallar las instrucciones.
    - Sé específico sobre cuándo y cómo el agente debe usar la habilidad.
4. **Agregar recursos**: Si la habilidad requiere scripts (ej. Python, JavaScript, PowerShell), colócalos en `scripts/`.
5. **Validar**: Asegúrate de que la estructura sea correcta y los enlaces de archivos funcionen.

## Ejemplo de Frontmatter en SKILL.md
```yaml
---
name: mi-nueva-habilidad
description: Breve descripción de lo que hace (en tercera persona).
---
```

## Herramientas de ayuda
- Puedes usar el script `scripts/scaffold_skill.ps1` incluido en esta habilidad para generar la estructura básica.
