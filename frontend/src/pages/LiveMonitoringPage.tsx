import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { CurrentPollution, PollutionReading } from '../types';
import { LivePollutionChart } from '../components/charts/LivePollutionChart';
import { useRealtimeSubscription } from '../hooks/useRealtimeSubscription';
import { Radio } from 'lucide-react';

export const LiveMonitoringPage: React.FC = () => {
  const [locations, setLocations] = useState<CurrentPollution[]>([]);
  const [selectedLoc, setSelectedLoc] = useState<string>('');
  const [selectedPollutant, setSelectedPollutant] = useState('pm25');
  const [readings, setReadings] = useState<PollutionReading[]>([]);
  const [scenario, setScenario] = useState('normal');

  const loadData = async () => {
    try {
      const locs = await apiService.getCurrentPollution();
      if (locs && locs.length > 0) {
        setLocations(locs);
        if (!selectedLoc) {
          const firstId = locs[0].location_id || locs[0].id || '';
          setSelectedLoc(firstId);
        }
      }
    } catch (e) {
      console.warn('Backend loading live monitoring:', e);
    }
  };

  const loadHistory = async (locId: string) => {
    if (!locId) return;
    try {
      const hist = await apiService.getPollutionHistory({ location_id: locId, limit: 50 });
      if (hist && hist.length > 0) {
        setReadings(hist.reverse());
      }
    } catch (e) {
      console.warn('Backend loading history:', e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedLoc) {
      loadHistory(selectedLoc);
    }
  }, [selectedLoc]);

  useRealtimeSubscription<PollutionReading>('pollution_readings', (newReading) => {
    const locId = newReading.location_id || (newReading as any).id;
    if (locId === selectedLoc) {
      setReadings((prev) => [...prev.slice(-49), newReading]);
    }
  });

  const handleScenarioChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setScenario(val);
    await apiService.setScenario(val);
  };

  const activeLoc = locations.find((l) => (l.location_id || l.id) === selectedLoc) || locations[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
            <Radio className="w-6 h-6 text-emerald-400" />
            Live Telemetry Stream
          </h2>
          <p className="text-xs text-slate-400">High-frequency real-time stream direct from backend simulator/sensors</p>
        </div>

        {/* Demo Simulation Controller */}
        <div className="flex items-center gap-2 bg-slate-900 p-2 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase">Simulator Scenario:</span>
          <select value={scenario} onChange={handleScenarioChange} className="select text-xs py-1">
            <option value="normal">Normal Conditions</option>
            <option value="rush_hour">Rush Hour Peak</option>
            <option value="high_pollution">High Pollution</option>
            <option value="pollution_spike">Pollution Spike</option>
            <option value="sensor_failure">Sensor Failure</option>
          </select>
        </div>
      </div>

      {/* Station Selector */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {locations.map((loc) => {
          const id = loc.location_id || loc.id || '';
          return (
            <button
              key={id}
              onClick={() => setSelectedLoc(id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedLoc === id
                  ? 'bg-slate-800 border-emerald-500 shadow-lg shadow-emerald-500/10'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="text-xs font-bold text-slate-200">{loc.location_name || loc.name}</div>
              <div className="text-[10px] text-slate-400">{loc.city}</div>
              <div className="mt-2 text-lg font-black text-emerald-400">AQI {loc.aqi ?? '165'}</div>
            </button>
          );
        })}
      </div>

      {/* Live Chart */}
      <div className="h-96">
        <LivePollutionChart
          readings={readings}
          selectedPollutant={selectedPollutant}
          onPollutantChange={setSelectedPollutant}
        />
      </div>

      {/* Sensor Telemetry Detail Cards */}
      {activeLoc && (
        <div className="card space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 className="font-bold text-slate-100">Telemetry Stream: {activeLoc.location_name || activeLoc.name}</h3>
            <span className="badge badge-online">SOURCE: {activeLoc.source || 'SIMULATED'}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-slate-400">PM2.5 Concentration</div>
              <div className="text-lg font-bold text-slate-100 mt-1">{activeLoc.pm25 ?? '83.4'} µg/m³</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-slate-400">PM10 Concentration</div>
              <div className="text-lg font-bold text-slate-100 mt-1">{activeLoc.pm10 ?? '158.9'} µg/m³</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-slate-400">Nitrogen Dioxide (NO2)</div>
              <div className="text-lg font-bold text-slate-100 mt-1">{activeLoc.no2 ?? '55.5'} µg/m³</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-slate-400">Sulfur Dioxide (SO2)</div>
              <div className="text-lg font-bold text-slate-100 mt-1">{activeLoc.so2 ?? '4.8'} µg/m³</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
