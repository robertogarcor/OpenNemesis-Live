# OpenNemesis-Live Frontend

Cliente web para el asistente de voz multimodal basado en LiveKit.

## Tech Stack

- **Framework:** Next.js 15
- **LiveKit:** JavaScript Client SDK
- **UI:** Componentes personalizados con LiveKit UI

## Setup

```bash
# Instalar dependencias
npm install

# Desarrollo local
npm run dev
```

Abre http://localhost:3000 para ver las demos de embed.

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env.local` y configura:

```env
LIVEKIT_URL=wss://tu-proyecto.livekit.cloud
LIVEKIT_API_KEY=tu_api_key
LIVEKIT_API_SECRET=tu_api_secret
NEXT_PUBLIC_CONN_DETAILS_ENDPOINT=http://localhost:3000/api/connection-details
```

### Configuración de App

Edita `app-config.ts` para personalizar:

- `agentName`: Nombre del agente
- `supportsChatInput`: Habilitar entrada de texto
- `supportsVideoInput`: Habilitar cámara
- `supportsScreenShare`: Habilitar compartir pantalla

## Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Build del script embed
npm run build-embed-popup-script
```

## Más Información

- [SPEC.md](../SPEC.md) - Especificación del proyecto
- [AGENTS.md](../AGENTS.md) - Instrucciones para agentes
