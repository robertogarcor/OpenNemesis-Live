# OpenNemesis-Live Frontend

Cliente web para el asistente de voz multimodal basado en LiveKit.

## Tech Stack

- **Framework:** Next.js 15
- **LiveKit:** JavaScript Client SDK + Agents UI
- **UI:** Componentes personalizados con shadcn/ui

## Setup

```bash
# Instalar dependencias
npm install

# Desarrollo local
npm run dev
```

Abre http://localhost:3000 para ver la aplicación.

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env.local` y configura:

```env
LIVEKIT_URL=wss://tu-proyecto.livekit.cloud
LIVEKIT_API_KEY=tu_api_key
LIVEKIT_API_SECRET=tu_api_secret
```

### Configuración de App

Edita `app-config.ts` para personalizar:

- `companyName`: Nombre de la empresa
- `pageTitle`: Título de la página
- `accent`: Color principal (hex)
- `startButtonText`: Texto del botón
- `audioVisualizerType`: Tipo de visualizador (bar, wave, grid, radial, aura)

## Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Build de producción
npm run build
```

## Más Información

- [SPEC.md](../SPEC.md) - Especificación del proyecto
- [AGENTS.md](../AGENTS.md) - Instrucciones para agentes