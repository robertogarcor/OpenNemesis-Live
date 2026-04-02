export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'OpenNemesis',
  pageTitle: 'OpenNemesis Live',
  pageDescription: 'Asistente de voz multimodal basado en LiveKit',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#6366f1',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#818cf8',
  startButtonText: 'Iniciar llamada',

  // optional: audio visualization configuration
  audioVisualizerType: 'bar',
  audioVisualizerColor: '#6366f1',
  audioVisualizerColorDark: '#818cf8',

  // agent dispatch configuration
  agentName: 'open-nemesis',

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
