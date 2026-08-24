import React, { useState, useEffect } from 'react';
import { Bell, User, Menu, X } from 'lucide-react';
import { ConnectionStatus } from '../types';

interface HeaderProps {
  status: ConnectionStatus;
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ status, onToggleSidebar }) => {
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      setTime(new Date().toLocaleTimeString());
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden text-slate-400 hover:text-slate-200 p-1"
        >
          <Menu className="w-6 h-6" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            STATUS:
          </span>
          {status === 'LIVE' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="live-dot"></span> LIVE
            </span>
          )}
          {status === 'RECONNECTING' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
              <span className="reconnecting-dot"></span> RECONNECTING
            </span>
          )}
          {status === 'OFFLINE' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/30">
              <span className="offline-dot"></span> OFFLINE
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <div className="text-xs font-mono text-slate-400 tabular-nums bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/50">
          {time || '10:42:31 PM'}
        </div>

        <button className="relative text-slate-400 hover:text-slate-200 transition-colors p-1.5 rounded-lg hover:bg-slate-800">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full animate-ping"></span>
        </button>

        <div className="flex items-center gap-2 border-l border-slate-800 pl-4 sm:pl-6">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-xs">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden md:block text-left text-xs">
            <div className="font-semibold text-slate-200">Operator</div>
            <div className="text-slate-500">Admin</div>
          </div>
        </div>
      </div>
    </header>
  );
};
