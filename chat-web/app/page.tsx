'use client';

import * as React from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';
import { AnimatePresence, motion } from 'motion/react';
import {
  RoomAudioRenderer,
  RoomContext,
  StartAudio,
  VideoTrack,
  useTracks,
} from '@livekit/components-react';
import {
  ChatTextIcon,
  MicrophoneIcon,
  MicrophoneSlashIcon,
  MonitorArrowUpIcon,
  PhoneCallIcon,
  PhoneDisconnectIcon,
  VideoCameraIcon,
  VideoCameraSlashIcon,
  XIcon,
} from '@phosphor-icons/react/dist/ssr';

const STORAGE_KEY = 'openNemesisUserId';

type AgentUiState = 'disconnected' | 'connecting' | 'initializing' | 'listening' | 'speaking';

type UiMessage = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
};

function get_or_create_user_id(): string {
  if (typeof window === 'undefined') return 'default-user';
  const existing = localStorage.getItem(STORAGE_KEY);
  if (existing) return existing;
  const user_id = `user-${Math.random().toString(36).slice(2, 11)}`;
  localStorage.setItem(STORAGE_KEY, user_id);
  return user_id;
}

function is_secure_origin_for_media(): boolean {
  if (typeof window === 'undefined') return false;
  if (window.isSecureContext) return true;
  const host = window.location.hostname;
  return host === 'localhost' || host === '127.0.0.1';
}

function cn(...classes: Array<string | undefined | false | null>) {
  return classes.filter(Boolean).join(' ');
}

const AnimatedButton = motion.create('button');

function Trigger({
  error,
  popup_open,
  agent_state,
  on_toggle,
}: {
  error: string | null;
  popup_open: boolean;
  agent_state: AgentUiState;
  on_toggle: () => void;
}) {
  const is_agent_connecting = popup_open && (agent_state === 'connecting' || agent_state === 'initializing');
  const is_agent_connected = popup_open && agent_state !== 'disconnected' && !is_agent_connecting;

  return (
    <AnimatePresence>
      <AnimatedButton
        key="open-nemesis-trigger"
        type="button"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0 }}
        transition={{ type: 'spring', duration: 1, bounce: 0.2 }}
        onClick={on_toggle}
        className={cn(
          'fixed right-4 bottom-4 z-50 m-0 block size-12 p-0.5 drop-shadow-md',
          'scale-100 transition-[scale] duration-300 hover:scale-105 focus:scale-105'
        )}
      >
        <motion.div
          className={cn(
            'absolute inset-0 z-10 rounded-full transition-colors',
            !popup_open && 'bg-fgAccent',
            !error &&
              is_agent_connecting &&
              'bg-fgAccent/30 animate-spin [background-image:conic-gradient(from_0deg,transparent_0%,transparent_30%,var(--color-fgAccent)_50%,transparent_70%,transparent_100%)]',
            (is_agent_connected || (Boolean(error) && popup_open)) && 'bg-destructive-foreground'
          )}
        />

        <div
          className={cn(
            'relative z-20 grid size-11 place-items-center rounded-full transition-colors',
            !popup_open && 'bg-fgAccent',
            !error && is_agent_connecting && 'bg-bg1',
            (is_agent_connected || (Boolean(error) && popup_open)) && 'bg-destructive'
          )}
        >
          <AnimatePresence>
            {!popup_open && (
              <motion.div
                key="open"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: popup_open ? 20 : -20 }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              >
                <div className="grid place-items-center">
                  <span className="text-bg1 text-[18px] font-semibold">N</span>
                </div>
              </motion.div>
            )}
            {(is_agent_connecting || (Boolean(error) && popup_open)) && (
              <motion.div
                key="dismiss"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: popup_open ? -20 : 20 }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              >
                <XIcon
                  size={20}
                  weight="bold"
                  className={cn('text-fg0 size-5', error && 'text-destructive-foreground')}
                />
              </motion.div>
            )}
            {!error && is_agent_connected && (
              <motion.div
                key="disconnect"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: popup_open ? -20 : 20 }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              >
                <PhoneDisconnectIcon
                  size={20}
                  weight="bold"
                  className="text-destructive-foreground size-5"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </AnimatedButton>
    </AnimatePresence>
  );
}

function Transcript({ messages }: { messages: UiMessage[] }) {
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages]);

  return (
    <div
      ref={ref}
      className={cn(
        'scrollbar-on-hover flex grow flex-col overflow-x-hidden overflow-y-scroll py-3 pr-3 pl-1',
        '[mask-image:linear-gradient(0deg,rgba(0,0,0,0.2)_0%,rgba(0,0,0,1)_5%,rgba(0,0,0,1)_95%,rgba(0,0,0,0)_100%)]'
      )}
    >
      <div className="flex flex-1 flex-col justify-end gap-2 pt-12">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              'max-w-[85%] rounded-2xl px-3 py-2 text-[13px] leading-snug',
              m.role === 'user' && 'ml-auto bg-fgAccent text-bg1 rounded-br-md',
              m.role === 'assistant' && 'mr-auto bg-bg2 text-fg1 rounded-bl-md',
              m.role === 'system' && 'mx-auto max-w-full bg-bg1 text-fg3 text-[12px]'
            )}
          >
            {m.text}
          </div>
        ))}
      </div>
    </div>
  );
}

function ToggleButton({
  pressed,
  pending,
  on_click,
  children,
  label,
}: {
  pressed: boolean;
  pending?: boolean;
  on_click: () => void;
  children: React.ReactNode;
  label: string;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={on_click}
      disabled={pending}
      className={cn(
        'grid size-10 place-items-center rounded-xl border border-separator1 bg-bg2 text-fg1 drop-shadow-sm',
        'transition-colors hover:bg-bg3',
        !pressed && 'text-destructive-foreground',
        pending && 'opacity-70'
      )}
    >
      {children}
    </button>
  );
}

function ActionBar({
  can_chat,
  chat_open,
  on_chat_open_change,
  mic_enabled,
  cam_enabled,
  screen_enabled,
  pending,
  on_toggle_mic,
  on_toggle_cam,
  on_toggle_screen,
}: {
  can_chat: boolean;
  chat_open: boolean;
  on_chat_open_change: (open: boolean) => void;
  mic_enabled: boolean;
  cam_enabled: boolean;
  screen_enabled: boolean;
  pending: boolean;
  on_toggle_mic: () => Promise<void>;
  on_toggle_cam: () => Promise<void>;
  on_toggle_screen: () => Promise<void>;
}) {
  return (
    <div className="relative z-20 mx-2 mb-2 flex flex-col">
      <div className="flex flex-row justify-between gap-1">
        <div className="flex gap-1">
          <ToggleButton
            pressed={mic_enabled}
            pending={pending}
            on_click={() => void on_toggle_mic()}
            label="Microfono"
          >
            {(() => {
              const Icon = mic_enabled ? MicrophoneIcon : MicrophoneSlashIcon;
              return <Icon weight="bold" size={18} />;
            })()}
          </ToggleButton>

          <ToggleButton
            pressed={cam_enabled}
            pending={pending}
            on_click={() => void on_toggle_cam()}
            label="Camara"
          >
            {(() => {
              const Icon = cam_enabled ? VideoCameraIcon : VideoCameraSlashIcon;
              return <Icon weight="bold" size={18} />;
            })()}
          </ToggleButton>

          <ToggleButton
            pressed={screen_enabled}
            pending={pending}
            on_click={() => void on_toggle_screen()}
            label="Compartir pantalla"
          >
            <MonitorArrowUpIcon weight="bold" size={18} />
          </ToggleButton>
        </div>

        {can_chat && (
          <button
            type="button"
            aria-label="Chat"
            title="Chat"
            onClick={() => on_chat_open_change(!chat_open)}
            className={cn(
              'grid size-10 place-items-center rounded-xl border border-separator1 bg-bg2 text-fg1 drop-shadow-sm',
              'transition-colors hover:bg-bg3',
              chat_open && 'bg-bgAccentPrimary text-fgAccent'
            )}
          >
            <ChatTextIcon weight="bold" size={18} />
          </button>
        )}
      </div>
    </div>
  );
}

export default function Page() {
  const is_animating = React.useRef(false);
  const room = React.useMemo(() => new Room(), []);

  const [popup_open, set_popup_open] = React.useState(false);
  const [error, set_error] = React.useState<string | null>(null);
  const [agent_state, set_agent_state] = React.useState<AgentUiState>('disconnected');

  const [pending_toggle, set_pending_toggle] = React.useState(false);
  const [mic_enabled, set_mic_enabled] = React.useState(true);
  const [cam_enabled, set_cam_enabled] = React.useState(false);
  const [screen_enabled, set_screen_enabled] = React.useState(false);
  const [chat_open, set_chat_open] = React.useState(false);
  const [input_text, set_input_text] = React.useState('');

  const local_participant = room.localParticipant;
  const local_camera_track = React.useMemo(() => {
    if (!local_participant) return undefined;
    const publication = local_participant.getTrackPublication(Track.Source.Camera);
    if (!publication) return undefined;
    return { participant: local_participant, publication, source: Track.Source.Camera };
  }, [local_participant, cam_enabled]);
  const local_screen_track = React.useMemo(() => {
    if (!local_participant) return undefined;
    const publication = local_participant.getTrackPublication(Track.Source.ScreenShare);
    if (!publication) return undefined;
    return { participant: local_participant, publication, source: Track.Source.ScreenShare };
  }, [local_participant, screen_enabled]);

  const [messages, set_messages] = React.useState<UiMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'OpenNemesis listo. Pulsa para conectar.',
    },
  ]);

  const handle_toggle_popup = () => {
    if (is_animating.current) return;
    set_error(null);
    set_popup_open((open) => !open);
  };

  const handle_panel_animation_start = () => {
    is_animating.current = true;
  };

  const handle_panel_animation_complete = () => {
    is_animating.current = false;
    if (!popup_open && room.state !== 'disconnected') {
      room.disconnect();
    }
  };

  React.useEffect(() => {
    const on_disconnected = () => {
      set_agent_state('disconnected');
      set_popup_open(false);
      set_chat_open(false);
    };

    const on_connected = () => {
      set_agent_state('initializing');
      set_messages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'system', text: 'Conectado. Esperando al agente...' },
      ]);
    };

    const on_participant_connected = () => {
      // El SDK marca los agentes con isAgent en algunas integraciones,
      // pero como este cliente es "raw Room", usamos un mensaje generico.
      set_agent_state('listening');
      set_messages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'system', text: 'Agente en sala.' },
      ]);
    };

    const on_local_track_published = (publication: { source: Track.Source }) => {
      if (publication.source === Track.Source.Camera) {
        set_cam_enabled(true);
      }
      if (publication.source === Track.Source.ScreenShare) {
        set_screen_enabled(true);
      }
    };

    const on_local_track_unpublished = (publication: { source: Track.Source }) => {
      if (publication.source === Track.Source.Camera) {
        set_cam_enabled(false);
      }
      if (publication.source === Track.Source.ScreenShare) {
        set_screen_enabled(false);
      }
    };

    const on_connection_state_changed = (state: unknown) => {
      // livekit-client exposes an enum, but we keep this handler permissive.
      // Useful for debugging connection issues to LiveKit Cloud.
      // eslint-disable-next-line no-console
      console.log('[livekit] connectionStateChanged', state);
    };

    const on_signal_connected = () => {
      // eslint-disable-next-line no-console
      console.log('[livekit] signalConnected');
    };

    const on_reconnecting = () => {
      // eslint-disable-next-line no-console
      console.log('[livekit] reconnecting');
    };

    const on_signal_reconnecting = () => {
      // eslint-disable-next-line no-console
      console.log('[livekit] signalReconnecting');
    };

    const on_media_devices_error = (e: Error) => {
      const msg = `${e.name}: ${e.message}`;
      set_messages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'system',
          text: `Error de dispositivos de audio/video: ${msg}`,
        },
      ]);
    };

    const on_data = (payload: Uint8Array) => {
      try {
        const text = new TextDecoder().decode(payload);
        const msg = JSON.parse(text);
        if (msg && typeof msg === 'object' && msg.type === 'chat' && typeof msg.text === 'string') {
          set_messages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: msg.role === 'user' ? 'user' : msg.role === 'assistant' ? 'assistant' : 'system',
              text: msg.text,
            },
          ]);
        }
      } catch {
        // ignore
      }
    };

    room.on(RoomEvent.Connected, on_connected);
    room.on(RoomEvent.Disconnected, on_disconnected);
    room.on(RoomEvent.ParticipantConnected, on_participant_connected);
    room.on(RoomEvent.LocalTrackPublished, on_local_track_published as any);
    room.on(RoomEvent.LocalTrackUnpublished, on_local_track_unpublished as any);
    room.on(RoomEvent.ConnectionStateChanged, on_connection_state_changed as any);
    room.on(RoomEvent.SignalConnected, on_signal_connected as any);
    room.on(RoomEvent.Reconnecting, on_reconnecting as any);
    room.on(RoomEvent.SignalReconnecting, on_signal_reconnecting as any);
    room.on(RoomEvent.MediaDevicesError, on_media_devices_error as any);
    room.on(RoomEvent.DataReceived, on_data);

    return () => {
      room.off(RoomEvent.Connected, on_connected);
      room.off(RoomEvent.Disconnected, on_disconnected);
      room.off(RoomEvent.ParticipantConnected, on_participant_connected);
      room.off(RoomEvent.LocalTrackPublished, on_local_track_published as any);
      room.off(RoomEvent.LocalTrackUnpublished, on_local_track_unpublished as any);
      room.off(RoomEvent.ConnectionStateChanged, on_connection_state_changed as any);
      room.off(RoomEvent.SignalConnected, on_signal_connected as any);
      room.off(RoomEvent.Reconnecting, on_reconnecting as any);
      room.off(RoomEvent.SignalReconnecting, on_signal_reconnecting as any);
      room.off(RoomEvent.MediaDevicesError, on_media_devices_error as any);
      room.off(RoomEvent.DataReceived, on_data);
    };
  }, [room]);

  React.useEffect(() => {
    if (!popup_open) return;
    if (room.state !== 'disconnected') return;

    set_agent_state('connecting');

    const connect = async () => {
      try {
        const user_id = get_or_create_user_id();
        const secure_for_media = is_secure_origin_for_media();

        if (!secure_for_media) {
          set_messages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: 'system',
              text: 'Aviso: tu origen no es seguro (HTTPS). El microfono puede fallar. Usa localhost o HTTPS.',
            },
          ]);
        }

        const res = await fetch('/api/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId: user_id }),
        });
        if (!res.ok) throw new Error('No se pudo obtener token');

        const details = await res.json();

        const maybe_enable_mic = secure_for_media
          ? room.localParticipant
              .setMicrophoneEnabled(true, undefined, { preConnectBuffer: true })
              .catch((e: unknown) => {
                const msg = e instanceof Error ? `${e.name}: ${e.message}` : 'Permiso de microfono denegado';
                set_messages((prev) => [
                  ...prev,
                  {
                    id: crypto.randomUUID(),
                    role: 'system',
                    text: `Microfono no disponible: ${msg}`,
                  },
                ]);
              })
          : Promise.resolve();

        await Promise.all([room.connect(details.serverUrl, details.participantToken), maybe_enable_mic]);
      } catch (e) {
        const msg = e instanceof Error ? `${e.name}: ${e.message}` : 'Error conectando al agente';
        set_error(msg);
        set_agent_state('disconnected');
      }
    };

    void connect();
  }, [popup_open, room]);

  React.useEffect(() => {
    if (!popup_open) return;

    const timeout = window.setTimeout(() => {
      if (agent_state === 'connecting' || agent_state === 'initializing') {
        set_error('El agente no termino de iniciar. Reintenta.');
      }
    }, 12_000);

    return () => window.clearTimeout(timeout);
  }, [popup_open, agent_state]);

  async function toggle_mic() {
    set_pending_toggle(true);
    try {
      const next = !mic_enabled;
      await room.localParticipant.setMicrophoneEnabled(next);
      set_mic_enabled(next);
    } finally {
      set_pending_toggle(false);
    }
  }

  async function toggle_cam() {
    set_pending_toggle(true);
    try {
      if (cam_enabled) {
        const publication = room.localParticipant.getTrackPublication(Track.Source.Camera);
        if (publication?.track) {
          await room.localParticipant.unpublishTrack(publication.track, true);
        }
        await room.localParticipant.setCameraEnabled(false);
        set_cam_enabled(false);
      } else {
        const publication = await room.localParticipant.setCameraEnabled(true);
        set_cam_enabled(Boolean(publication));
      }
    } finally {
      set_pending_toggle(false);
    }
  }

  async function toggle_screen() {
    set_pending_toggle(true);
    try {
      if (screen_enabled) {
        const publication = room.localParticipant.getTrackPublication(Track.Source.ScreenShare);
        if (publication?.track) {
          await room.localParticipant.unpublishTrack(publication.track, true);
        }
        await room.localParticipant.setScreenShareEnabled(false);
        set_screen_enabled(false);
      } else {
        const publication = await room.localParticipant.setScreenShareEnabled(true);
        if (!publication) {
          set_messages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: 'system',
              text: 'No se pudo iniciar la pantalla compartida. Revisa permisos o el navegador.',
            },
          ]);
        }
        set_screen_enabled(Boolean(publication));
      }
    } finally {
      set_pending_toggle(false);
    }
  }

  async function send_text() {
    const text = input_text.trim();
    if (!text) return;

    set_messages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text }]);
    set_input_text('');

    try {
      await room.localParticipant.publishData(
        new TextEncoder().encode(JSON.stringify({ type: 'chat', role: 'user', text })),
        { reliable: true }
      );
    } catch {
      // ignore
    }
  }

  return (
    <RoomContext.Provider value={room}>
      <RoomAudioRenderer />
      <StartAudio label="Iniciar audio" />

      <Trigger
        error={error}
        popup_open={popup_open}
        agent_state={agent_state}
        on_toggle={handle_toggle_popup}
      />

      <motion.div
        inert={!popup_open}
        initial={{ opacity: 0, translateY: 8 }}
        animate={{ opacity: popup_open ? 1 : 0, translateY: popup_open ? 0 : 8 }}
        transition={{ type: 'spring', bounce: 0, duration: popup_open ? 1 : 0.2 }}
        onAnimationStart={handle_panel_animation_start}
        onAnimationComplete={handle_panel_animation_complete}
        className="fixed right-4 bottom-20 left-4 z-50 md:left-auto"
      >
        <div className="bg-bg1 border-separator1 ml-auto h-[500px] w-full rounded-[28px] border drop-shadow-md md:w-[380px] overflow-hidden">
          <div className="relative h-full w-full">
            {error && (
              <div className="absolute inset-0 grid place-items-center p-6">
                <div className="w-full rounded-2xl border border-separator1 bg-bg1 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-fg0 text-sm font-semibold">Sesion terminada</div>
                      <div className="text-fg2 mt-1 text-xs">{error}</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => set_error(null)}
                      className="grid size-9 place-items-center rounded-xl border border-separator1 bg-bg2 text-fg1 hover:bg-bg3"
                      aria-label="Cerrar"
                    >
                      <XIcon size={18} weight="bold" />
                    </button>
                  </div>
                  <div className="mt-3 flex justify-end">
                    <button
                      type="button"
                      className="rounded-xl bg-fgAccent px-4 py-2 text-bg1 text-sm font-semibold hover:opacity-90"
                      onClick={() => {
                        set_error(null);
                        room.disconnect();
                        set_popup_open(true);
                      }}
                    >
                      Reintentar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {!error && (
              <div className="flex h-full w-full flex-col overflow-hidden">
                <div className="relative flex shrink-0 items-center justify-between px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="size-9 rounded-2xl bg-bgAccentPrimary border border-separatorAccent grid place-items-center">
                      <span className="text-fgAccent text-sm font-semibold">ON</span>
                    </div>
                    <div>
                      <div className="text-fg0 text-sm font-semibold">OpenNemesis</div>
                      <div className="text-fg3 text-xs">
                        {agent_state === 'connecting'
                          ? 'Conectando...'
                          : agent_state === 'initializing'
                            ? 'Inicializando...'
                            : agent_state === 'speaking'
                              ? 'Hablando...'
                              : agent_state === 'listening'
                                ? 'Escuchando'
                                : 'Desconectado'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div
                      className="flex items-center gap-2 rounded-full border border-separator1 bg-bg2 px-3 py-1 text-[11px] text-fg2"
                      title="Sesion activa"
                    >
                      <PhoneCallIcon size={14} weight="bold" className="text-fgAccent" />
                      En llamada
                    </div>
                    <button
                      type="button"
                      className="grid size-10 place-items-center rounded-xl border border-separator1 bg-bg2 text-destructive-foreground hover:bg-destructive-hover"
                      onClick={() => room.disconnect()}
                      aria-label="Salir"
                      title="Salir"
                    >
                      <PhoneDisconnectIcon size={18} weight="bold" />
                    </button>
                  </div>
                </div>

                <div
                  className={cn(
                    'relative mx-2 mt-1 mb-2 h-[124px] overflow-hidden rounded-[14px] border border-separator1/70',
                    'bg-[radial-gradient(120%_120%_at_20%_0%,var(--color-bgAccentPrimary)_0%,transparent_50%),radial-gradient(90%_120%_at_100%_20%,rgba(11,95,255,0.18)_0%,transparent_60%),linear-gradient(180deg,var(--color-bg2)_0%,var(--color-bg1)_100%)]'
                  )}
                >
                  <div className="absolute inset-0 grid place-items-center">
                    <div className="text-fg2 text-xs">Voz en tiempo real</div>
                  </div>

                  <AnimatePresence>
                    {local_camera_track && (
                      <motion.div
                        key="local-camera"
                        initial={{ scale: 0.6, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.6, opacity: 0 }}
                        transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                        className="absolute right-3 bottom-3 border border-separator1 rounded-[12px] overflow-hidden shadow-lg"
                        title="Camara"
                      >
                        <VideoTrack
                          trackRef={local_camera_track}
                          className="h-[88px] w-[88px] object-cover"
                        />
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <AnimatePresence>
                    {local_screen_track && (
                      <motion.div
                        key="local-screen"
                        initial={{ scale: 0.6, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.6, opacity: 0 }}
                        transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                        className={cn(
                          'absolute bottom-3 border border-separator1 rounded-[12px] overflow-hidden shadow-lg',
                          local_camera_track ? 'right-[98px]' : 'right-3'
                        )}
                        title="Compartir pantalla"
                      >
                        <VideoTrack
                          trackRef={local_screen_track}
                          className="h-[88px] w-[88px] object-cover"
                        />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                <div className="relative flex h-full min-h-0 flex-1 flex-col">
                  <div className="flex min-h-0 flex-1 flex-col">
                    {chat_open && <Transcript messages={messages} />}

                    <div className={cn('px-2', chat_open && 'hidden')}>
                      <div className="rounded-[20px] border border-separator1 bg-bg2 p-4">
                        <div className="text-fg1 text-sm font-semibold">Habla o escribe</div>
                        <div className="text-fg3 mt-1 text-xs">
                          Este widget esta inspirado en el embed de LiveKit, con marca OpenNemesis.
                        </div>
                      </div>
                    </div>
                  </div>

                  <ActionBar
                    can_chat
                    chat_open={chat_open}
                    on_chat_open_change={set_chat_open}
                    mic_enabled={mic_enabled}
                    cam_enabled={cam_enabled}
                    screen_enabled={screen_enabled}
                    pending={pending_toggle}
                    on_toggle_mic={toggle_mic}
                    on_toggle_cam={toggle_cam}
                    on_toggle_screen={toggle_screen}
                  />

                  {chat_open && (
                    <div className="mx-2 mb-3 mt-1 flex gap-2">
                      <input
                        value={input_text}
                        onChange={(e) => set_input_text(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') void send_text();
                        }}
                        placeholder="Escribe aqui..."
                        className="h-11 w-full rounded-[18px] border border-separator1 bg-bg2 px-3 text-sm text-fg1 placeholder:text-fg4 outline-none focus:ring-2 focus:ring-fgAccent/30"
                      />
                      <button
                        type="button"
                        onClick={() => void send_text()}
                        className="h-11 shrink-0 rounded-[18px] bg-fgAccent px-4 text-sm font-semibold text-bg1 hover:opacity-90"
                      >
                        Enviar
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </RoomContext.Provider>
  );
}
