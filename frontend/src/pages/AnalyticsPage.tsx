import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Location, AnalyticsSummary, TrendData, Correlation } from '../types';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line } from 'recharts';

export const AnalyticsPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLoc, setSelectedLoc] = useState<string>('');
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [correlations, setCorrelations] = useState<Correlation[]>([]);
  const [pollutant, setPollutant] = useState('pm25');

  useEffect(() => {
    apiService.getLocations().then((locs) => {
      setLocations(locs);
      if (locs.length > 0) setSelectedLoc(locs[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedLoc) {
      apiService.getAnalyticsSummary(selectedLoc).then(setSummary);
      apiService.getTrends(selectedLoc, pollutant, 'hourly', 7).then(setTrends);
      apiService.getCorrelation(selectedLoc).then((res) => setCorrelations(res.correlations || []));
    }
  }, [selectedLoc, pollutant]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-100 uppercase">Historical Analytics & Trends</h2>
          <p className="text-xs text-slate-400">Statistical breakdown, moving averages, and Pearson correlation coefficients</p>
        </div>

        <select
          value={selectedLoc}
          onChange={(e) => setSelectedLoc(e.target.value)}
          className="select text-sm w-48"
        >
          {locations.map((l) => (
            <option key={l.id} value={l.id}>
              {l.name} ({l.city})
            </option>
          ))}
        </select>
      </div>

      {/* Summary Cards */}
      {summary && summary[pollutant] && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="kpi-card">
            <span className="kpi-label">MEAN {pollutant.toUpperCase()}</span>
            <span className="kpi-value text-emerald-400">{summary[pollutant].mean}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">MAX {pollutant.toUpperCase()}</span>
            <span className="kpi-value text-red-400">{summary[pollutant].max}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">STD DEVIATION</span>
            <span className="kpi-value text-slate-200">{summary[pollutant].std_dev}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">P95 PERCENTILE</span>
            <span className="kpi-value text-amber-400">{summary[pollutant].p95 ?? 'N/A'}</span>
          </div>
        </div>
      )}

      {/* Historical Trend Chart */}
      <div className="card space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-slate-100">7-Day Aggregated Trend</h3>
          <select
            value={pollutant}
            onChange={(e) => setPollutant(e.target.value)}
            className="select text-xs py-1"
          >
            <option value="pm25">PM2.5</option>
            <option value="pm10">PM10</option>
            <option value="no2">NO2</option>
            <option value="so2">SO2</option>
            <option value="co">CO</option>
          </select>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="period" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '8px' }}
              />
              <Bar dataKey="mean" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Correlation Matrix */}
      <div className="card space-y-4">
        <h3 className="font-bold text-slate-100">Pearson Correlation Matrix</h3>
        <p className="text-xs text-slate-400">Statistical association between monitored environmental parameters</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {correlations.slice(0, 6).map((c, i) => (
            <div key={i} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between items-center">
              <div>
                <div className="text-xs font-bold text-slate-200">
                  {c.param1.toUpperCase()} vs {c.param2.toUpperCase()}
                </div>
                <div className="text-[10px] text-slate-500">{c.strength} association</div>
              </div>
              <span className={`text-sm font-black ${c.correlation > 0.5 ? 'text-emerald-400' : 'text-slate-300'}`}>
                r = {c.correlation}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
