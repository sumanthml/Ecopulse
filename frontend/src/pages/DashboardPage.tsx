import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { DashboardSummary, PollutionReading } from '../types';
import { AQIGauge } from '../components/dashboard/AQIGauge';
import { LivePollutionChart } from '../components/charts/LivePollutionChart';
import { PollutionMap } from '../components/map/PollutionMap';
import { useRealtimeSubscription } from '../hooks/useRealtimeSubscription';
import { AlertTriangle, Sparkles, Wind, Thermometer, Droplets } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPollutant, setSelectedPollutant] = useState('pm25');
  const [liveReadings, setLiveReadings] = useState<PollutionReading[]>([]);

  const loadData = async () => {
    try {
      const data = await apiService.getDashboardSummary();
      if (data && data.locations) {
        setSummary(data);

        if (data.locations.length > 0) {
          try {
            const locId = data.locations[0].location_id || (data.locations[0] as any).id;
            const history = await apiService.getPollutionHistory({
              location_id: locId,
              limit: 30,
            });
            if (history && history.length > 0) {
              setLiveReadings(history.reverse());
            }
          } catch (histErr) {
            console.warn('History load error:', histErr);
          }
        }
      }
    } catch (e) {
      console.warn('Backend loading dashboard summary:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  useRealtimeSubscription<PollutionReading>('pollution_readings', (newReading) => {
    setLiveReadings((prev) => [...prev.slice(-29), newReading]);
    loadData();
  });

  if (loading && !summary) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-800 rounded w-1/4"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-24 bg-slate-800 rounded-xl"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="h-80 bg-slate-800 rounded-xl"></div>
          <div className="lg:col-span-2 h-80 bg-slate-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  const primaryLoc = summary?.locations[0] || {} as any;

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
          <span className="kpi-value text-emerald-400">{primaryLoc.aqi ?? 'N/A'}</span>
          <span className="kpi-trend text-slate-400">{primaryLoc.category || 'Good'}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            PM2.5 <Wind className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.pm25 ?? 'N/A'}</span>
          <span className="text-xs text-slate-500">µg/m³</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            PM10 <Wind className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.pm10 ?? 'N/A'}</span>
          <span className="text-xs text-slate-500">µg/m³</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            TEMPERATURE <Thermometer className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.temperature ?? 'N/A'}</span>
          <span className="text-xs text-slate-500">°C</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label flex items-center justify-between">
            HUMIDITY <Droplets className="w-3.5 h-3.5 text-slate-500" />
          </span>
          <span className="kpi-value text-slate-100">{primaryLoc.humidity ?? 'N/A'}</span>
          <span className="text-xs text-slate-500">%</span>
        </div>
        <div className="kpi-card border-red-500/30 bg-red-950/20">
          <span className="kpi-label text-red-400">ACTIVE ALERTS</span>
          <span className="kpi-value text-red-400">{summary?.stats.active_alerts ?? 0}</span>
          <span className="text-xs text-red-400/80">{summary?.stats.critical_alerts ?? 0} Critical</span>
        </div>
      </div>

      {/* Main Grid: Gauge + Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card flex flex-col items-center justify-center">
          <AQIGauge
            aqi={primaryLoc.aqi ?? 0}
            category={primaryLoc.category ?? 'Good'}
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
          <PollutionMap locations={summary?.locations || []} />
        </div>

        {/* Active Alerts Panel */}
        <div className="card flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Active Alerts
            </h3>
            <span className="badge badge-warning">{summary?.alerts.length ?? 0}</span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-72 pr-1">
            {!summary || summary.alerts.length === 0 ? (
              <div className="text-xs text-slate-500 text-center py-8">No active alerts reported</div>
            ) : (
              summary.alerts.map((alert) => (
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
              ))
            )}
          </div>
        </div>
      </div>

      {/* AI Intelligence Section */}
      <div className="card bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-emerald-500/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <h3 className="font-bold text-slate-100">AI Environmental Intelligence</h3>
        </div>
        {summary && summary.insights.length > 0 ? (
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
