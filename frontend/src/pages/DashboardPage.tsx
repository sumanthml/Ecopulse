import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { DashboardSummary, PollutionReading, CurrentPollution } from '../types';
import { AQIGauge } from '../components/dashboard/AQIGauge';
import { LivePollutionChart } from '../components/charts/LivePollutionChart';
import { PollutionMap } from '../components/map/PollutionMap';
import { useRealtimeSubscription } from '../hooks/useRealtimeSubscription';
import { AlertTriangle, Sparkles, Wind, Thermometer, Droplets } from 'lucide-react';

const INITIAL_LOCATIONS: CurrentPollution[] = [
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', location_name: 'Bengaluru Koramangala', city: 'Bengaluru', state: 'Karnataka', country: 'India', latitude: 12.9352, longitude: 77.6245, aqi: 164, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 81.1, pm10: 108.2, co: 1.22, no2: 54.6, so2: 7.7, o3: 37.9, temperature: 26.2, humidity: 74.0, wind_speed: 2.5, pressure: 1013.8 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', location_name: 'Chennai Central', city: 'Chennai', state: 'Tamil Nadu', country: 'India', latitude: 13.0827, longitude: 80.2707, aqi: 174, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 100.2, pm10: 151.8, co: 1.79, no2: 79.0, so2: 8.1, o3: 34.9, temperature: 30.4, humidity: 75.8, wind_speed: 3.0, pressure: 1013.3 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', location_name: 'Delhi Connaught Place', city: 'Delhi', state: 'Delhi', country: 'India', latitude: 28.6315, longitude: 77.2167, aqi: 240, category: 'Very Unhealthy', dominant_pollutant: 'PM10', pm25: 183.0, pm10: 381.9, co: 3.1, no2: 107.5, so2: 14.8, o3: 45.8, temperature: 32.1, humidity: 59.0, wind_speed: 2.4, pressure: 1013.4 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', location_name: 'Hyderabad HITEC', city: 'Hyderabad', state: 'Telangana', country: 'India', latitude: 17.4435, longitude: 78.3772, aqi: 177, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 105.8, pm10: 161.7, co: 1.35, no2: 64.5, so2: 4.6, o3: 44.6, temperature: 32.5, humidity: 60.3, wind_speed: 1.5, pressure: 1013.5 },
  { location_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567805', location_name: 'Mumbai Bandra', city: 'Mumbai', state: 'Maharashtra', country: 'India', latitude: 19.0596, longitude: 72.8295, aqi: 175, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 102.5, pm10: 179.3, co: 1.46, no2: 72.2, so2: 10.6, o3: 44.1, temperature: 29.8, humidity: 78.0, wind_speed: 1.7, pressure: 1014.4 },
];

const INITIAL_SUMMARY: DashboardSummary = {
  locations: INITIAL_LOCATIONS,
  stats: { total_locations: 5, total_sensors: 15, online_sensors: 14, offline_sensors: 0, total_readings: 785, today_readings: 785, active_alerts: 4, critical_alerts: 1 },
  alerts: [
    { id: '1', location_id: 'loc1', title: 'PM10 very unhealthy level', severity: 'CRITICAL', parameter: 'PM10', value: 381.9, threshold: 250.0, status: 'ACTIVE', created_at: new Date().toISOString() },
    { id: '2', location_id: 'loc2', title: 'PM2.5 unhealthy level', severity: 'HIGH', parameter: 'PM25', value: 100.2, threshold: 75.0, status: 'ACTIVE', created_at: new Date().toISOString() },
  ],
  insights: [
    { id: '1', location_id: 'loc1', title: 'Bengaluru Air Quality Assessment', content: 'Air quality in Koramangala is Unhealthy with AQI of 164. PM2.5 levels are elevated. Outdoor exercise should be reduced.', severity: 'MODERATE', insight_type: 'daily_report', generated_by: 'GROQ_AI', created_at: new Date().toISOString() },
  ],
  system: { collector: { running: true, provider: 'Demo Sensor Simulator', source_type: 'SIMULATED', fetch_count: 100, error_count: 0, interval_seconds: 30 }, timestamp: new Date().toISOString() },
};

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary>(INITIAL_SUMMARY);
  const [selectedPollutant, setSelectedPollutant] = useState('pm25');
  const [liveReadings, setLiveReadings] = useState<PollutionReading[]>([]);

  const loadData = async () => {
    try {
      const data = await apiService.getDashboardSummary();
      if (data && data.locations && data.locations.length > 0) {
        setSummary(data);
        const locId = data.locations[0].location_id || (data.locations[0] as any).id;
        try {
          const history = await apiService.getPollutionHistory({ location_id: locId, limit: 30 });
          if (history && history.length > 0) {
            setLiveReadings(history.reverse());
          }
        } catch (hErr) {
          console.warn('Pollution history error:', hErr);
        }
      }
    } catch (e) {
      console.warn('Live API connection pending:', e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  useRealtimeSubscription<PollutionReading>('pollution_readings', (newReading) => {
    setLiveReadings((prev) => [...prev.slice(-29), newReading]);
    loadData();
  });

  const primaryLoc = summary.locations[0] || INITIAL_LOCATIONS[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-black tracking-tight text-slate-100 uppercase">System Overview</h2>
        <p className="text-xs text-slate-400">Real-time environmental telemetry across active monitoring stations</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="kpi-card">
          <span className="kpi-label">AQI INDEX</span>
          <span className="kpi-value text-emerald-400">{primaryLoc.aqi ?? 164}</span>
          <span className="kpi-trend text-slate-400">{primaryLoc.category || 'Unhealthy'}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            PM2.5 <Wind className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.pm25 ?? 81.1}</span>
          <span className="text-xs text-slate-500">µg/m³</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            PM10 <Wind className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.pm10 ?? 108.2}</span>
          <span className="text-xs text-slate-500">µg/m³</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            TEMPERATURE <Thermometer className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.temperature ?? 26.2}</span>
          <span className="text-xs text-slate-500">°C</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            HUMIDITY <Droplets className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.humidity ?? 74.0}</span>
          <span className="text-xs text-slate-500">%</span>
        </div>
        <div className="kpi-card border-red-500/30 bg-red-950/20">
          <span className="kpi-label text-red-400">ACTIVE ALERTS</span>
          <span className="kpi-value text-red-400">{summary.stats.active_alerts}</span>
          <span className="text-xs text-red-400/80">{summary.stats.critical_alerts} Critical</span>
        </div>
      </div>

      {/* Main Grid: Gauge + Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card flex flex-col items-center justify-center">
          <AQIGauge
            aqi={primaryLoc.aqi ?? 164}
            category={primaryLoc.category || 'Unhealthy'}
            dominantPollutant={primaryLoc.dominant_pollutant || 'PM2.5'}
            size="lg"
          />
        </div>

        <div className="lg:col-span-2">
          <LivePollutionChart
            readings={liveReadings}
            selectedPollutant={selectedPollutant}
            onPollutantChange={setSelectedPollutant}
          />
        </div>
      </div>

      {/* Second Grid: Map + Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-96">
          <PollutionMap locations={summary.locations} />
        </div>

        {/* Active Alerts Panel */}
        <div className="card flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Active Alerts
            </h3>
            <span className="badge badge-warning">{summary.alerts.length}</span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-72 pr-1">
            {summary.alerts.map((alert) => (
              <div
                key={alert.id}
                className="p-3 bg-slate-900/60 rounded-lg border border-slate-700/50 space-y-1"
              >
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold text-slate-200">{alert.title}</span>
                  <span className={`severity-${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                </div>
                <p className="text-xs text-slate-400">
                  {alert.parameter}: {alert.value} (Threshold: {alert.threshold})
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Intelligence Section */}
      <div className="card bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-emerald-500/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <h3 className="font-bold text-slate-100">AI Environmental Intelligence</h3>
        </div>
        {summary.insights.length > 0 ? (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-emerald-400">{summary.insights[0].title}</h4>
            <p className="text-xs text-slate-300 leading-relaxed">{summary.insights[0].content}</p>
          </div>
        ) : (
          <p className="text-xs text-slate-400">
            No AI environmental summary generated yet. Analyzes automated trends when critical events trigger.
          </p>
        )}
      </div>
    </div>
  );
};
