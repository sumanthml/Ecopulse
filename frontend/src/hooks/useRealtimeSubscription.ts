import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { ConnectionStatus } from '../types';

export function useRealtimeSubscription<T>(
  table: string,
  onInsert?: (payload: T) => void,
  onUpdate?: (payload: T) => void,
  onDelete?: (payload: T) => void
) {
  const [status, setStatus] = useState<ConnectionStatus>('OFFLINE');

  useEffect(() => {
    if (!supabase) {
      setStatus('OFFLINE');
      return;
    }

    setStatus('RECONNECTING');

    const channel = supabase.channel(`public:${table}`);

    if (onInsert) {
      channel.on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table },
        (payload) => onInsert(payload.new as T)
      );
    }
    if (onUpdate) {
      channel.on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table },
        (payload) => onUpdate(payload.new as T)
      );
    }
    if (onDelete) {
      channel.on(
        'postgres_changes',
        { event: 'DELETE', schema: 'public', table },
        (payload) => onDelete(payload.old as T)
      );
    }

    channel.subscribe((subscribeStatus) => {
      if (subscribeStatus === 'SUBSCRIBED') {
        setStatus('LIVE');
      } else if (subscribeStatus === 'CLOSED' || subscribeStatus === 'CHANNEL_ERROR') {
        setStatus('OFFLINE');
      } else {
        setStatus('RECONNECTING');
      }
    });

    return () => {
      supabase?.removeChannel(channel);
    };
  }, [table]);

  return { status };
}
