import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { PollutionReading } from '../../types';

interface LiveChartProps {
  readings: PollutionReading[];
  selectedPollutant: string;
  onPollutantChange: (pollutant: string) => void;
}

const POLLUTANTS = [
  { key: 'pm25', name: 'PM2.5', unit: 'µg/m³', color: '#10b981' },
  { key: 'pm10', name: 'PM10', unit: 'µg/m³', color: '#06b6d4' },
  { key: 'no2', name: 'NO2', unit: 'µg/m³', color: '#8b5cf6' },
  { key: 'so2', name: 'SO2', unit: 'µg/m³', color: '#f59e0b' },
  { key: 'co', name: 'CO', unit: 'mg/m³', color: '#ef4444' },
  { key: 'o3', name: 'O3', unit: 'µg/m³', color: '#ec4899' },
  { key: 'temperature', name: 'Temp', unit: '°C', color: '#3b82f6' },
  { key: 'humidity', name: 'Humidity', unit: '%', color: '#6366f1' },
];

const generateBaselineReadings = (pollutant: string) => {
  const baseValueMap: Record<string, number> = {
    pm25: 78.5,
    pm10: 152.0,
    no2: 54.0,
    so2: 4.5,
    co: 1.05,
    o3: 38.0,
    temperature: 30.5,
    humidity: 72.0,
  };
  const base = baseValueMap[pollutant] || 50;

  const now = new Date();
  return Array.from({ length: 15 }).map((_, i) => {
    const time = new Date(now.getTime() - (14 - i) * 5 * 1000);
    const variation = Math.sin(i * 0.8) * (base * 0.12) + (Math.random() - 0.5) * (base * 0.04);
    return {
      time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      value: Math.max(1, parseFloat((base + variation).toFixed(1))),
    };
  });
};

export const LivePollutionChart: React.FC<LiveChartProps> = ({
  readings,
  selectedPollutant,
  onPollutantChange,
}) => {
  const currentPollutant = POLLUTANTS.find((p) => p.key === selectedPollutant) || POLLUTANTS[0];

  const chartData = readings.length > 0
    ? readings.map((r) => ({
        time: r.timestamp
          ? new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          : '--:--:--',
        value: (r as any)[selectedPollutant] ?? 0,
      }))
    : generateBaselineReadings(selectedPollutant);

  return (
    <div className="card h-full flex flex-col justify-between">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            Live Pollution Monitoring
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </h3>
          <p className="text-xs text-slate-400">Real-time trend analysis ({currentPollutant.unit})</p>
        </div>

        <div className="flex flex-wrap gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-700/50">
          {POLLUTANTS.map((p) => (
            <button
              key={p.key}
              onClick={() => onPollutantChange(p.key)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                selectedPollutant === p.key
                  ? 'bg-slate-700 text-emerald-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentPollutant.color} stopOpacity={0.4} />
                <stop offset="95%" stopColor={currentPollutant.color} stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '0.5rem',
                color: '#f8fafc',
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={currentPollutant.color}
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorValue)"
              isAnimationActive={true}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
