import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Sensor } from '../types';
import { Cpu, CheckCircle, AlertTriangle, XCircle, Wrench } from 'lucide-react';

export const SensorsPage: React.FC = () => {
  const [sensors, setSensors] = useState<Sensor[]>([]);

  useEffect(() => {
    apiService.getSensors().then(setSensors);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ONLINE': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case 'WARNING': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'OFFLINE': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'MAINTENANCE': return <Wrench className="w-4 h-4 text-slate-400" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
          <Cpu className="w-6 h-6 text-emerald-400" />
          Sensor Registry & Health
        </h2>
        <p className="text-xs text-slate-400">Inventory of all active physical, virtual, and simulated hardware sensors</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors.map((s) => (
          <div key={s.id} className="card space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-slate-100">{s.sensor_name}</h3>
                <span className="text-xs font-mono text-slate-400">{s.sensor_code}</span>
              </div>
              <div className="flex items-center gap-1.5">
                {getStatusIcon(s.status)}
                <span className={`badge badge-${s.status.toLowerCase()}`}>{s.status}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-2.5 rounded-lg">
              <div>
                <span className="text-slate-500">Location:</span>{' '}
                <span className="font-semibold text-slate-300">{s.city}</span>
              </div>
              <div>
                <span className="text-slate-500">Type:</span>{' '}
                <span className="font-semibold text-slate-300">{s.sensor_type}</span>
              </div>
              <div>
                <span className="text-slate-500">Source:</span>{' '}
                <span className="font-semibold text-emerald-400">{s.source}</span>
              </div>
              <div>
                <span className="text-slate-500">Health:</span>{' '}
                <span className="font-semibold text-slate-200">{s.health_score ?? 100}%</span>
              </div>
            </div>

            <div className="text-[10px] text-slate-500">
              Last Ping: {s.last_seen ? new Date(s.last_seen).toLocaleString() : 'Never'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
