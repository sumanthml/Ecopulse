import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { CurrentPollution, PollutionReading } from '../types';
import { LivePollutionChart } from '../components/charts/LivePollutionChart';
import { useRealtimeSubscription } from '../hooks/useRealtimeSubscription';
import { Radio } from 'lucide-react';

const INITIAL_LOCATIONS: CurrentPollution[] = [
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', location_name: 'Bengaluru Koramangala', city: 'Bengaluru', state: 'Karnataka', country: 'India', latitude: 12.9352, longitude: 77.6245, aqi: 164, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 81.1, pm10: 108.2, co: 1.22, no2: 54.6, so2: 7.7, o3: 37.9, temperature: 26.2, humidity: 74.0 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', location_name: 'Chennai Central', city: 'Chennai', state: 'Tamil Nadu', country: 'India', latitude: 13.0827, longitude: 80.2707, aqi: 174, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 100.2, pm10: 151.8, co: 1.79, no2: 79.0, so2: 8.1, o3: 34.9, temperature: 30.4, humidity: 75.8 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', location_name: 'Delhi Connaught Place', city: 'Delhi', state: 'Delhi', country: 'India', latitude: 28.6315, longitude: 77.2167, aqi: 240, category: 'Very Unhealthy', dominant_pollutant: 'PM10', pm25: 183.0, pm10: 381.9, co: 3.1, no2: 107.5, so2: 14.8, o3: 45.8, temperature: 32.1, humidity: 59.0 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', location_name: 'Hyderabad HITEC', city: 'Hyderabad', state: 'Telangana', country: 'India', latitude: 17.4435, longitude: 78.3772, aqi: 177, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 105.8, pm10: 161.7, co: 1.35, no2: 64.5, so2: 4.6, o3: 44.6, temperature: 32.5, humidity: 60.3 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567805', location_name: 'Mumbai Bandra', city: 'Mumbai', state: 'Maharashtra', country: 'India', latitude: 19.0596, longitude: 72.8295, aqi: 175, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 102.5, pm10: 179.3, co: 1.46, no2: 72.2, so2: 10.6, o3: 44.1, temperature: 29.8, humidity: 78.0 },
];

export const LiveMonitoringPage: React.FC = () => {
  const [locations, setLocations] = useState<CurrentPollution[]>(INITIAL_LOCATIONS);
  const [selectedLoc, setSelectedLoc] = useState<string>(INITIAL_LOCATIONS[0].location_id);
  const [selectedPollutant, setSelectedPollutant] = useState('pm25');
  const [readings, setReadings] = useState<PollutionReading[]>([]);
  const [scenario, setScenario] = useState('normal');

  useEffect(() => {
    const tickInterval = setInterval(() => {
      setLocations((prevLocs) => {
        return prevLocs.map((loc) => {
          const deltaPm25 = (Math.random() - 0.48) * 3.5;
          const deltaPm10 = (Math.random() - 0.48) * 4.2;
          const newPm25 = parseFloat(Math.max(10, (loc.pm25 || 80) + deltaPm25).toFixed(1));
          const newPm10 = parseFloat(Math.max(20, (loc.pm10 || 120) + deltaPm10).toFixed(1));
          const currentAqi = loc.aqi || 150;
          const newAqi = Math.max(20, Math.round(currentAqi + (Math.random() - 0.48) * 2));
          return {
            ...loc,
            aqi: newAqi,
            pm25: newPm25,
            pm10: newPm10,
            no2: parseFloat(((loc.no2 || 50) + (Math.random() - 0.48) * 1.5).toFixed(1)),
            so2: parseFloat(((loc.so2 || 7) + (Math.random() - 0.48) * 0.4).toFixed(1)),
          };
        });
      });
    }, 1500);

    return () => clearInterval(tickInterval);
  }, []);

  const loadData = async () => {
    try {
      const locs = await apiService.getCurrentPollution();
      if (locs && locs.length > 0) {
        setLocations(locs);
        if (!selectedLoc) {
          setSelectedLoc(locs[0].location_id);
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
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedLoc) {
      loadHistory(selectedLoc);
    }
  }, [selectedLoc]);

  useRealtimeSubscription<PollutionReading>('pollution_readings', (newReading) => {
    if (newReading.location_id === selectedLoc) {
      setReadings((prev) => [...prev.slice(-49), newReading]);
    }
  });

  const handleScenarioChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setScenario(val);
    await apiService.setScenario(val);
  };

  const activeLoc = locations.find((l) => l.location_id === selectedLoc) || locations[0] || INITIAL_LOCATIONS[0];

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
        {locations.map((loc) => (
          <button
            key={loc.location_id}
            onClick={() => setSelectedLoc(loc.location_id)}
            className={`p-3 rounded-xl border text-left transition-all ${
              selectedLoc === loc.location_id
                ? 'bg-slate-800 border-emerald-500 shadow-lg shadow-emerald-500/10'
                : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="text-xs font-bold text-slate-100 truncate">{loc.location_name}</div>
            <div className="text-[10px] text-slate-400">{loc.city}</div>
            <div className="mt-2 text-lg font-black text-emerald-400">AQI {loc.aqi}</div>
          </button>
        ))}
      </div>

      {/* Main Stream Chart */}
      <LivePollutionChart
        readings={readings}
        selectedPollutant={selectedPollutant}
        onPollutantChange={setSelectedPollutant}
      />

      {/* Parameters Stream Grid */}
      {activeLoc && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-slate-100">Telemetry Stream: {activeLoc.location_name}</h3>
            <span className="badge badge-online text-[10px]">SOURCE: {activeLoc.source || 'SIMULATED'}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="card">
              <span className="kpi-label">PM2.5 Concentration</span>
              <span className="kpi-value text-emerald-400">{activeLoc.pm25} µg/m³</span>
            </div>
            <div className="card">
              <span className="kpi-label">PM10 Concentration</span>
              <span className="kpi-value text-cyan-400">{activeLoc.pm10} µg/m³</span>
            </div>
            <div className="card">
              <span className="kpi-label">Nitrogen Dioxide (NO2)</span>
              <span className="kpi-value text-purple-400">{activeLoc.no2} ppb</span>
            </div>
            <div className="card">
              <span className="kpi-label">Sulfur Dioxide (SO2)</span>
              <span className="kpi-value text-amber-400">{activeLoc.so2} ppb</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
