import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { ShieldCheck, Activity, Database, Radio, Sparkles } from 'lucide-react';

export const AdminPage: React.FC = () => {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    apiService.getSystemStatus().then(setStatus);
  }, []);

  if (!status) return <div className="text-slate-400 text-xs">Loading system status...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          System Health & Administration
        </h2>
        <p className="text-xs text-slate-400">System infrastructure diagnostic dashboard and component statuses</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
            <Activity className="w-4 h-4 text-emerald-400" /> API SERVICE
          </div>
          <div className="text-2xl font-black text-emerald-400">{status.api.status}</div>
        </div>

        <div className="card space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
            <Database className="w-4 h-4 text-emerald-400" /> DATABASE
          </div>
          <div className="text-2xl font-black text-emerald-400">{status.database.status}</div>
        </div>

        <div className="card space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
            <Radio className="w-4 h-4 text-emerald-400" /> DATA COLLECTOR
          </div>
          <div className="text-2xl font-black text-emerald-400">
            {status.data_provider.running ? 'ONLINE' : 'OFFLINE'}
          </div>
          <div className="text-[10px] text-slate-500">Provider: {status.data_provider.provider}</div>
        </div>

        <div className="card space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
            <Sparkles className="w-4 h-4 text-emerald-400" /> GROQ AI
          </div>
          <div className="text-2xl font-black text-emerald-400">{status.ai.status}</div>
        </div>
      </div>
    </div>
  );
};
