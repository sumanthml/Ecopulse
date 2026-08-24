import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Sensor } from '../types';
import { Cpu, CheckCircle, AlertTriangle, XCircle, Wrench } from 'lucide-react';

const FALLBACK_SENSORS: Sensor[] = [
  { id: '1', location_id: 'l1', sensor_code: 'SN-CHE-001', sensor_name: 'Central Optical Particle Counter', source: 'SIMULATED', sensor_type: 'PM2.5 / PM10 Optical', status: 'ONLINE', city: 'Chennai', health_score: 98, last_seen: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: '2', location_id: 'l2', sensor_code: 'SN-HYD-001', sensor_name: 'HITEC Laser Aerosol Monitor', source: 'SIMULATED', sensor_type: 'Multi-Gas electrochemical', status: 'ONLINE', city: 'Hyderabad', health_score: 100, last_seen: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: '3', location_id: 'l3', sensor_code: 'SN-BLR-001', sensor_name: 'Koramangala Environmental Station', source: 'SIMULATED', sensor_type: 'AQI Integrated Telemetry', status: 'ONLINE', city: 'Bengaluru', health_score: 95, last_seen: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: '4', location_id: 'l4', sensor_code: 'SN-DEL-001', sensor_name: 'CP High-Precision Telemetry Node', source: 'SIMULATED', sensor_type: 'Beta Attenuation Monitor', status: 'ONLINE', city: 'Delhi', health_score: 92, last_seen: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: '5', location_id: 'l5', sensor_code: 'SN-BOM-001', sensor_name: 'Bandra Coastal Telemetry Monitor', source: 'SIMULATED', sensor_type: 'Optical & Electrochemical', status: 'ONLINE', city: 'Mumbai', health_score: 97, last_seen: new Date().toISOString(), created_at: new Date().toISOString() },
];

export const SensorsPage: React.FC = () => {
  const [sensors, setSensors] = useState<Sensor[]>(FALLBACK_SENSORS);

  useEffect(() => {
    apiService.getSensors().then((data) => {
      if (data && data.length > 0) setSensors(data);
    }).catch(console.warn);
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
