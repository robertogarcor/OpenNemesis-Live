'use client';

import { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';

const STORAGE_KEY = 'openNemesisUserId';

function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return 'default-user';
  
  let userId = localStorage.getItem(STORAGE_KEY);
  if (!userId) {
    userId = 'user-' + Math.random().toString(36).substring(2, 11);
    localStorage.setItem(STORAGE_KEY, userId);
  }
  return userId;
}

export default function ChatWidget() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [inputText, setInputText] = useState('');
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');
  
  const roomRef = useRef<Room | null>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const screenStreamRef = useRef<MediaStream | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      roomRef.current?.disconnect();
    };
  }, []);

  const connect = async () => {
    setConnecting(true);
    setError('');
    
    try {
      const userId = getOrCreateUserId();
      
      const res = await fetch('/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
      });
      
      if (!res.ok) throw new Error('Failed to get token');
      
      const { serverUrl, roomName, participantToken } = await res.json();
      
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });
      
      room.on(RoomEvent.ParticipantConnected, (participant) => {
        setMessages(prev => [...prev, { role: 'system', text: 'Conectado al asistente de voz' }]);
      });
      
      room.on(RoomEvent.ParticipantDisconnected, () => {
        setMessages(prev => [...prev, { role: 'system', text: 'Asistente desconectado' }]);
      });
      
      room.on(RoomEvent.TrackSubscribed, (track, _publication, _participant) => {
        if (track.kind === 'audio') {
          track.attach();
        } else if (track.kind === 'video') {
          if (remoteVideoRef.current) {
            const el = track.attach();
            el.style.width = '100%';
            el.style.height = '100%';
            el.style.objectFit = 'cover';
            remoteVideoRef.current.appendChild(el);
          }
        }
      });
      
      // Listen for agent transcription/audio
      room.on(RoomEvent.AudioPlaybackStarted, () => {
        console.log('Agent audio started');
      });
      
      // Listen for data messages (text from agent)
      room.on(RoomEvent.DataReceived, (payload, _participant) => {
        try {
          const data = JSON.parse(new TextDecoder().decode(payload));
          if (data.text) {
            setMessages(prev => [...prev, { role: 'agent', text: data.text }]);
          }
        } catch {}
      });
      
      await room.connect(serverUrl, participantToken);
      roomRef.current = room;
      
      // Get available devices and create tracks
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: true, 
          video: true 
        });
        streamRef.current = stream;
        
        // Audio
        const audioTrack = stream.getAudioTracks()[0];
        if (audioTrack) {
          const track = await room.localParticipant.createAudioTrack({ name: 'microphone' }, audioTrack);
          await room.localParticipant.publishTrack(track);
        }
        
        // Video
        const videoTrack = stream.getVideoTracks()[0];
        if (videoTrack && localVideoRef.current) {
          const track = await room.localParticipant.createVideoTrack({ name: 'camera' }, videoTrack);
          await room.localParticipant.publishTrack(track);
          track.attach(localVideoRef.current);
        }
      } catch (e) {
        console.warn('Could not get media devices:', e);
      }
      
      setConnected(true);
      setIsExpanded(true);
      setMessages(prev => [...prev, { role: 'system', text: 'Conectado. ¡Habla conmigo!' }]);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setConnecting(false);
    }
  };

  const disconnect = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    roomRef.current?.disconnect();
    roomRef.current = null;
    setConnected(false);
    setIsExpanded(false);
    setMessages([]);
  };

  const toggleMute = async () => {
    if (!streamRef.current) return;
    
    const audioTrack = streamRef.current.getAudioTracks()[0];
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled;
      setIsMuted(!audioTrack.enabled);
    }
  };

  const toggleVideo = async () => {
    if (!streamRef.current) return;
    
    const videoTrack = streamRef.current.getVideoTracks()[0];
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled;
      setIsVideoOn(videoTrack.enabled);
    }
  };

  const toggleScreenShare = async () => {
    if (!roomRef.current) return;
    
    if (isScreenSharing) {
      // Stop screen sharing
      if (screenStreamRef.current) {
        screenStreamRef.current.getTracks().forEach(track => track.stop());
        screenStreamRef.current = null;
      }
      setIsScreenSharing(false);
    } else {
      // Start screen sharing
      try {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({ 
          video: true 
        });
        screenStreamRef.current = screenStream;
        
        const screenTrack = screenStream.getVideoTracks()[0];
        if (screenTrack) {
          const track = await roomRef.current.localParticipant.createVideoTrack({ name: 'screen' }, screenTrack);
          await roomRef.current.localParticipant.publishTrack(track);
          
          screenTrack.onended = () => {
            setIsScreenSharing(false);
            screenStreamRef.current = null;
          };
        }
        
        setIsScreenSharing(true);
      } catch (e) {
        console.warn('Could not share screen:', e);
      }
    }
  };

  const sendText = async () => {
    if (!inputText.trim() || !roomRef.current) return;
    
    setMessages(prev => [...prev, { role: 'user', text: inputText }]);
    
    await roomRef.current.localParticipant.publishData(
      new TextEncoder().encode(JSON.stringify({ type: 'text', text: inputText })),
      'data'
    );
    
    setInputText('');
  };

  // Bubble widget UI
  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 }}>
      {isExpanded && connected && (
        <div style={{
          position: 'absolute',
          bottom: '70px',
          right: '0',
          width: '380px',
          height: '500px',
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}>
          {/* Header */}
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#6366f1', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px'
              }}>
                🤖
              </div>
              <div>
                <div style={{ fontWeight: '600' }}>OpenNemesis</div>
                <div style={{ fontSize: '12px', opacity: 0.8 }}>Asistente de voz</div>
              </div>
            </div>
            <button 
              onClick={() => setIsExpanded(false)}
              style={{ background: 'none', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer' }}
            >
              −
            </button>
          </div>
          
          {/* Video area */}
          <div style={{ 
            height: '180px', 
            backgroundColor: '#1a1a1a',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div ref={remoteVideoRef} style={{ width: '100%', height: '100%' }} />
            <video 
              ref={localVideoRef} 
              autoPlay 
              muted 
              playsInline 
              style={{ 
                width: '80px', 
                height: '60px',
                position: 'absolute',
                bottom: '10px',
                right: '10px',
                borderRadius: '8px',
                border: '2px solid white',
                objectFit: 'cover',
              }} 
            />
          </div>
          
          {/* Controls */}
          <div style={{ padding: '10px', display: 'flex', gap: '10px', borderBottom: '1px solid #eee' }}>
            <button
              onClick={toggleMute}
              style={{
                flex: 1,
                padding: '8px',
                backgroundColor: isMuted ? '#ef4444' : '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '18px',
              }}
            >
              {isMuted ? '🔇' : '🎤'}
            </button>
            <button
              onClick={toggleVideo}
              style={{
                flex: 1,
                padding: '8px',
                backgroundColor: !isVideoOn ? '#ef4444' : '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '18px',
              }}
            >
              {isVideoOn ? '📹' : '📷'}
            </button>
            <button
              onClick={toggleScreenShare}
              style={{
                flex: 1,
                padding: '8px',
                backgroundColor: isScreenSharing ? '#22c55e' : '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '18px',
              }}
            >
              {isScreenSharing ? '🖥️' : '📺'}
            </button>
            <button
              onClick={disconnect}
              style={{
                flex: 1,
                padding: '8px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              Salir
            </button>
          </div>
          
          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '15px' }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  marginBottom: '10px',
                  padding: '10px 14px',
                  borderRadius: '16px',
                  maxWidth: '80%',
                  backgroundColor: msg.role === 'user' ? '#6366f1' : msg.role === 'agent' ? '#e0e7ff' : '#f3f4f6',
                  color: msg.role === 'user' ? 'white' : '#333',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  marginLeft: msg.role === 'user' ? 'auto' : '0',
                }}
              >
                {msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input */}
          <div style={{ padding: '15px', borderTop: '1px solid #eee', display: 'flex', gap: '10px' }}>
            <input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendText()}
              placeholder="Escribe un mensaje..."
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '24px',
                outline: 'none',
              }}
            />
            <button
              onClick={sendText}
              disabled={!inputText.trim()}
              style={{
                width: '44px',
                height: '44px',
                backgroundColor: '#6366f1',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              ➤
            </button>
          </div>
        </div>
      )}
      
      {/* Floating button */}
      <button
        onClick={connected ? () => setIsExpanded(!isExpanded) : connect}
        disabled={connecting}
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: connected ? '#6366f1' : '#22c55e',
          border: 'none',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
          cursor: connecting ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
        }}
      >
        {connecting ? '...' : connected ? '💬' : '🎤'}
      </button>
    </div>
  );
}