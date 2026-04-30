'use client';

import * as React from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';
import { AnimatePresence, motion } from 'motion/react';
import {
  RoomAudioRenderer,
  RoomContext,
  StartAudio,
  BarVisualizer,
  VideoTrack,
  useVoiceAssistant,
} from '@livekit/components-react';
import {
  ChatTextIcon,
  MicrophoneIcon,
  MicrophoneSlashIcon,
  MonitorArrowUpIcon,
  InfoIcon,
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

function AudioVisualizer({
  agentState,
  audioTrack,
  size,
}: {
  agentState: string;
  audioTrack?: any;
  size: 'small' | 'medium' | 'large';
}) {
  const options =
    size === 'large'
      ? { minHeight: 24, maxHeight: 210 }
      : size === 'medium'
        ? { minHeight: 10, maxHeight: 80 }
        : { minHeight: 12, maxHeight: 100 };
  const barClass =
    size === 'large'
      ? 'flex h-36 min-h-[144px] w-auto items-end gap-2.5'
      : size === 'medium'
        ? 'flex h-11 min-h-[44px] w-auto items-end gap-1.5'
        : 'flex h-12 min-h-[48px] w-auto items-end gap-1.5';
  const barCount = size === 'large' ? 7 : size === 'medium' ? 5 : 5;
  const barTemplateClass =
    size === 'large'
      ? 'lk-audio-bar min-h-9 w-4 rounded-full'
      : size === 'medium'
        ? 'lk-audio-bar min-h-4 w-2 rounded-full'
        : 'lk-audio-bar min-h-5 w-2 rounded-full';
  return (
    <BarVisualizer
      barCount={barCount}
      state={agentState as any}
      trackRef={audioTrack}
      options={options}
      className={barClass}
    >
      <span className={barTemplateClass} />
    </BarVisualizer>
  );
}

function VoiceBar({
  agentState,
  variant,
  className,
}: {
  agentState: string;
  variant: 'small' | 'large';
  className?: string;
}) {
  const { audioTrack, state } = useVoiceAssistant();
  if (!audioTrack) return null;
  return (
    <div
      className={cn(
        'absolute z-10',
        className,
        variant === 'small'
          ? 'left-3 bottom-3'
          : 'left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2'
      )}
    >
      <AudioVisualizer
        agentState={(state as string) ?? agentState}
        audioTrack={audioTrack}
        size={variant}
      />
    </div>
  );
}

function InlineVoiceBar({ agentState }: { agentState: string }) {
  const { audioTrack, state } = useVoiceAssistant();
  if (!audioTrack) return null;
  return <AudioVisualizer agentState={(state as string) ?? agentState} audioTrack={audioTrack} size="medium" />;
}

function Transcript({ messages }: { messages: UiMessage[] }) {
  const ref = React.useRef<HTMLDivElement>(null);
  const is_near_bottom_ref = React.useRef(true);

  const update_scroll_anchor = React.useCallback(() => {
    const el = ref.current;
    if (!el) return;
    const distance_to_bottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    is_near_bottom_ref.current = distance_to_bottom < 64;
  }, []);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const id = window.requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
      is_near_bottom_ref.current = true;
    });
    return () => window.cancelAnimationFrame(id);
  }, []);

  React.useEffect(() => {
    const el = ref.current;
    if (!el || !is_near_bottom_ref.current) return;
    const id = window.requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
    return () => window.cancelAnimationFrame(id);
  }, [messages]);

  return (
    <div
      ref={ref}
      onScroll={update_scroll_anchor}
      onWheel={(event) => event.stopPropagation()}
      onTouchMove={(event) => event.stopPropagation()}
      className="scrollbar-on-hover relative z-20 h-full min-h-0 overflow-x-hidden overflow-y-auto overscroll-contain py-3 pr-3 pl-1 touch-pan-y"
    >
      <div className="flex flex-col gap-2 pt-12 pb-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              'max-w-[85%] rounded-2xl px-3 py-2 text-[13px] leading-snug',
              m.role === 'user' && 'ml-auto bg-fgAccent text-bg1 rounded-br-md',
              m.role === 'assistant' && 'mr-auto border border-separator1/40 bg-bg2/70 text-fg1 rounded-bl-md',
              m.role === 'system' && 'mx-auto max-w-full border border-separator1/50 bg-bg1/40 text-fg3 text-[12px]'
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
        'grid size-10 place-items-center rounded-xl border border-separator1 bg-bg1 text-fg0 drop-shadow-sm',
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
  about_open,
  on_about_toggle,
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
  about_open: boolean;
  on_about_toggle: () => void;
  on_toggle_mic: () => Promise<void>;
  on_toggle_cam: () => Promise<void>;
  on_toggle_screen: () => Promise<void>;
}) {
  return (
    <div className="z-50 mx-2 mb-2 flex shrink-0 flex-col bg-bg1/95">
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
              return <Icon weight="bold" size={18} color={mic_enabled ? '#1f2937' : '#c62828'} />;
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
              return <Icon weight="bold" size={18} color={cam_enabled ? '#1f2937' : '#c62828'} />;
            })()}
          </ToggleButton>

          <ToggleButton
            pressed={screen_enabled}
            pending={pending}
            on_click={() => void on_toggle_screen()}
            label="Compartir pantalla"
          >
            <MonitorArrowUpIcon
              weight="bold"
              size={18}
              color={screen_enabled ? '#1f2937' : '#c62828'}
            />
          </ToggleButton>
        </div>

        {can_chat && (
          <div className="relative flex gap-1">
            {about_open && (
              <div className="absolute bottom-12 right-0 w-[220px] rounded-xl border border-separator1 bg-bg1 p-3 text-xs text-fg2 shadow-lg">
                Este widget esta inspirado en el embed de LiveKit, con marca OpenNemesis.
              </div>
            )}
            <button
              type="button"
              aria-label="Chat"
              title="Chat"
              onClick={() => on_chat_open_change(!chat_open)}
              className={cn(
                'grid size-10 place-items-center rounded-xl border border-separator1 bg-bg1 text-fg0 drop-shadow-sm',
                'transition-colors hover:bg-bg3',
                chat_open && 'bg-bgAccentPrimary text-fgAccent'
              )}
            >
              <ChatTextIcon weight="bold" size={18} />
            </button>
            <button
              type="button"
              aria-label="About"
              title="About"
              onClick={on_about_toggle}
              className={cn(
                'grid size-10 place-items-center rounded-xl border border-separator1 bg-bg1 text-fg0 drop-shadow-sm',
                'transition-colors hover:bg-bg3',
                about_open && 'bg-bgAccentPrimary text-fgAccent'
              )}
            >
              <InfoIcon weight="bold" size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Page() {
  const room = React.useMemo(() => new Room(), []);

  const [error, set_error] = React.useState<string | null>(null);
  const [agent_state, set_agent_state] = React.useState<AgentUiState>('disconnected');

  const [pending_toggle, set_pending_toggle] = React.useState(false);
  const [mic_enabled, set_mic_enabled] = React.useState(true);
  const [cam_enabled, set_cam_enabled] = React.useState(false);
  const [screen_enabled, set_screen_enabled] = React.useState(false);
  const [chat_open, set_chat_open] = React.useState(false);
  const [about_open, set_about_open] = React.useState(false);
  const [input_text, set_input_text] = React.useState('');
  const [ui_notice, set_ui_notice] = React.useState<string | null>(null);
  const notice_timeout_ref = React.useRef<number | null>(null);

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
  const active_local_visual_track = React.useMemo(() => {
    if (screen_enabled && local_screen_track) {
      return { trackRef: local_screen_track, title: 'Compartir pantalla' };
    }
    if (cam_enabled && local_camera_track) {
      return { trackRef: local_camera_track, title: 'Camara' };
    }
    return null;
  }, [screen_enabled, cam_enabled, local_screen_track, local_camera_track]);

  const [messages, set_messages] = React.useState<UiMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'OpenNemesis listo. Conectando automaticamente...',
    },
  ]);

  const push_system_message = React.useCallback((text: string) => {
    set_messages((prev) => [...prev, { id: crypto.randomUUID(), role: 'system', text }]);
  }, []);

  const show_notice = React.useCallback((text: string) => {
    if (notice_timeout_ref.current) {
      window.clearTimeout(notice_timeout_ref.current);
    }
    set_ui_notice(text);
    notice_timeout_ref.current = window.setTimeout(() => {
      set_ui_notice(null);
      notice_timeout_ref.current = null;
    }, 3500);
  }, []);

  const connect_room = React.useCallback(async () => {
    if (room.state !== 'disconnected') return;

    set_agent_state('connecting');
    set_error(null);

    try {
      const user_id = get_or_create_user_id();
      const secure_for_media = is_secure_origin_for_media();

      if (!secure_for_media) {
        push_system_message(
          'Aviso: tu origen no es seguro (HTTPS). El microfono puede fallar. Usa localhost o HTTPS.'
        );
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
              push_system_message(`Microfono no disponible: ${msg}`);
            })
        : Promise.resolve();

      await Promise.all([room.connect(details.serverUrl, details.participantToken), maybe_enable_mic]);
      set_agent_state('listening');
    } catch (e) {
      const msg = e instanceof Error ? `${e.name}: ${e.message}` : 'Error conectando al agente';
      set_error(msg);
      set_agent_state('disconnected');
    }
  }, [room, push_system_message]);

  React.useEffect(() => {
    const on_disconnected = () => {
      set_agent_state('disconnected');
      show_notice('Se perdio la conexion con la sala.');
      push_system_message('Se perdio la conexion con la sala. Reintenta.');
      set_chat_open(false);
      set_about_open(false);
    };

    const on_connected = () => {
      set_agent_state('initializing');
      push_system_message('Conectado. Esperando al agente...');
    };

    const on_participant_connected = () => {
      set_agent_state('listening');
      push_system_message('Agente en sala.');
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

    const on_media_devices_error = (e: Error) => {
      const msg = `${e.name}: ${e.message}`;
      push_system_message(`Error de dispositivos de audio/video: ${msg}`);
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
    room.on(RoomEvent.MediaDevicesError, on_media_devices_error as any);
    room.on(RoomEvent.DataReceived, on_data);

    return () => {
      if (notice_timeout_ref.current) {
        window.clearTimeout(notice_timeout_ref.current);
      }
      room.off(RoomEvent.Connected, on_connected);
      room.off(RoomEvent.Disconnected, on_disconnected);
      room.off(RoomEvent.ParticipantConnected, on_participant_connected);
      room.off(RoomEvent.LocalTrackPublished, on_local_track_published as any);
      room.off(RoomEvent.LocalTrackUnpublished, on_local_track_unpublished as any);
      room.off(RoomEvent.MediaDevicesError, on_media_devices_error as any);
      room.off(RoomEvent.DataReceived, on_data);
    };
  }, [room, push_system_message, show_notice]);

  React.useEffect(() => {
    void connect_room();
  }, [connect_room]);

  React.useEffect(() => {
    const timeout = window.setTimeout(() => {
      if (agent_state === 'connecting' || agent_state === 'initializing') {
        set_error('El agente no termino de iniciar. Reintenta.');
      }
    }, 12_000);

    return () => window.clearTimeout(timeout);
  }, [agent_state]);

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
        await room.localParticipant.setCameraEnabled(false);
        set_cam_enabled(false);
      } else {
        if (screen_enabled) {
          await room.localParticipant.setScreenShareEnabled(false);
          set_screen_enabled(false);
          const msg = 'Se desactivo pantalla para activar camara.';
          push_system_message(msg);
          show_notice(msg);
        }

        const publication = await room.localParticipant.setCameraEnabled(true);
        set_cam_enabled(Boolean(publication));
      }
    } catch (e) {
      const msg = e instanceof Error ? `Camara: ${e.message}` : 'No se pudo cambiar camara.';
      push_system_message(msg);
      show_notice(msg);
    } finally {
      set_pending_toggle(false);
    }
  }

  async function toggle_screen() {
    set_pending_toggle(true);
    try {
      if (screen_enabled) {
        await room.localParticipant.setScreenShareEnabled(false);
        set_screen_enabled(false);
      } else {
        if (cam_enabled) {
          await room.localParticipant.setCameraEnabled(false);
          set_cam_enabled(false);
          const msg = 'Se desactivo camara para compartir pantalla.';
          push_system_message(msg);
          show_notice(msg);
        }

        const publication = await room.localParticipant.setScreenShareEnabled(true);
        if (!publication) {
          const msg = 'No se pudo iniciar la pantalla compartida. Revisa permisos o el navegador.';
          push_system_message(msg);
          show_notice(msg);
        }
        set_screen_enabled(Boolean(publication));
      }
    } catch (e) {
      const msg = e instanceof Error ? `Pantalla: ${e.message}` : 'No se pudo cambiar pantalla.';
      push_system_message(msg);
      show_notice(msg);
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

  const is_disconnected = agent_state === 'disconnected';

  return (
    <RoomContext.Provider value={room}>
      <RoomAudioRenderer />
      <StartAudio label="Iniciar audio" />

      <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(120%_120%_at_10%_0%,rgba(11,95,255,0.14)_0%,transparent_55%),radial-gradient(100%_120%_at_100%_0%,rgba(11,95,255,0.09)_0%,transparent_60%),linear-gradient(180deg,#fbfbfa_0%,#f4f5f7_100%)] px-4 py-6 md:px-8 md:py-8">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-[-80px] top-[120px] h-56 w-56 rounded-full bg-fgAccent/10 blur-3xl" />
          <div className="absolute right-[-60px] top-[40px] h-44 w-44 rounded-full bg-fgAccent/10 blur-3xl" />
        </div>

        <section className="relative mx-auto w-full max-w-5xl">
          <div className="h-[88vh] min-h-[560px] w-full overflow-hidden">
            <div className="relative h-full w-full">
              {error && (
                <div className="absolute inset-0 grid place-items-center p-6">
                  <div className="w-full max-w-[560px] rounded-2xl border border-separator1 bg-bg1 p-4">
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
                          void connect_room();
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
                        title={is_disconnected ? 'Sesion desconectada' : 'Sesion activa'}
                      >
                        <PhoneCallIcon size={14} weight="bold" className="text-fgAccent" />
                        {is_disconnected ? 'Desconectado' : 'En llamada'}
                      </div>

                      {is_disconnected ? (
                        <button
                          type="button"
                          className="rounded-xl bg-fgAccent px-3 py-2 text-xs font-semibold text-bg1 hover:opacity-90"
                          onClick={() => {
                            set_error(null);
                            void connect_room();
                          }}
                          aria-label="Reconectar"
                          title="Reconectar"
                        >
                          Conectar
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="grid size-10 place-items-center rounded-xl border border-separator1 bg-bg2 text-destructive-foreground hover:bg-destructive-hover"
                          onClick={() => room.disconnect()}
                          aria-label="Salir"
                          title="Salir"
                        >
                          <PhoneDisconnectIcon size={18} weight="bold" />
                        </button>
                      )}
                    </div>
                  </div>

                  {ui_notice && (
                    <div className="mx-3 mb-1 rounded-xl border border-separator1 bg-bg2/90 px-3 py-2 text-xs text-fg2">
                      {ui_notice}
                    </div>
                  )}

                  {chat_open && !error && (
                    <div className="mx-2 mt-1 mb-1 flex shrink-0 justify-center">
                      <div className="inline-flex h-[72px] w-fit items-center gap-2.5 rounded-2xl border border-separator1/40 px-3 md:h-[78px]">
                        <div className="flex h-[54px] w-[64px] items-end justify-center pb-[3px] md:h-[62px] md:w-[72px] md:pb-[4px]">
                          <InlineVoiceBar agentState={agent_state} />
                        </div>
                        <AnimatePresence>
                          {active_local_visual_track && (
                            <motion.div
                              key={`floating-${active_local_visual_track.title}`}
                              initial={{ scale: 0.7, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              exit={{ scale: 0.7, opacity: 0 }}
                              transition={{ type: 'spring', bounce: 0.2, duration: 0.3 }}
                              className="overflow-hidden rounded-xl"
                              title={active_local_visual_track.title}
                            >
                              <VideoTrack
                                trackRef={active_local_visual_track.trackRef}
                                className="h-[54px] w-[54px] object-cover md:h-[62px] md:w-[62px]"
                              />
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  )}

                  {!chat_open && (
                    <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center">
                      <VoiceBar agentState={agent_state} variant="large" className="-translate-y-20" />
                    </div>
                  )}

                  {!chat_open && active_local_visual_track && (
                    <div className="pointer-events-none absolute right-3 bottom-[64px] z-20">
                      <AnimatePresence>
                        <motion.div
                          key={`closed-${active_local_visual_track.title}`}
                          initial={{ scale: 0.6, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          exit={{ scale: 0.6, opacity: 0 }}
                          transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                          className="overflow-hidden rounded-[12px]"
                          title={active_local_visual_track.title}
                        >
                          <VideoTrack
                            trackRef={active_local_visual_track.trackRef}
                            className="h-[112px] w-[112px] object-cover"
                          />
                        </motion.div>
                      </AnimatePresence>
                    </div>
                  )}

                  <div className="grid min-h-0 flex-1 grid-rows-[minmax(0,1fr)_auto]">
                    <div className="min-h-0 overflow-hidden">
                      {chat_open && <Transcript messages={messages} />}
                    </div>

                    {chat_open && (
                      <div className="shrink-0 pb-1">
                        <div className="mx-2 mt-1 mb-2 flex gap-2">
                          <textarea
                            value={input_text}
                            onChange={(e) => set_input_text(e.target.value)}
                            onInput={(e) => {
                              const el = e.currentTarget;
                              el.style.height = 'auto';
                              el.style.height = `${Math.min(el.scrollHeight, 144)}px`;
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                void send_text();
                              }
                            }}
                            placeholder="Escribe aqui..."
                            rows={1}
                            className="min-h-11 max-h-36 w-full resize-none overflow-y-auto rounded-[18px] border border-separator1/80 bg-transparent px-3 py-2 text-sm text-fg1 placeholder:text-fg4 outline-none focus:ring-2 focus:ring-fgAccent/30"
                          />
                          <button
                            type="button"
                            onClick={() => void send_text()}
                            className="h-11 shrink-0 rounded-[18px] bg-fgAccent px-4 text-sm font-semibold text-bg1 opacity-100 transition-[filter] hover:opacity-100 hover:brightness-95"
                          >
                            Enviar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="relative z-50 shrink-0 px-2 pb-1">
                    <div className="rounded-2xl border border-separator1/80 bg-bg1/45 pt-1 backdrop-blur-sm">
                      <ActionBar
                        can_chat
                        chat_open={chat_open}
                        on_chat_open_change={set_chat_open}
                        mic_enabled={mic_enabled}
                        cam_enabled={cam_enabled}
                        screen_enabled={screen_enabled}
                        pending={pending_toggle}
                        about_open={about_open}
                        on_about_toggle={() => set_about_open((prev) => !prev)}
                        on_toggle_mic={toggle_mic}
                        on_toggle_cam={toggle_cam}
                        on_toggle_screen={toggle_screen}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </RoomContext.Provider>
  );
}
