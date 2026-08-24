import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Location, Prediction, Anomaly } from '../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TrendingUp, AlertOctagon, Cpu } from 'lucide-react';

export const PredictionsPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLoc, setSelectedLoc] = useState<string>('');
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [modelMetrics, setModelMetrics] = useState<any>(null);
  const [isTraining, setIsTraining] = useState(false);

  useEffect(() => {
    apiService.getLocations().then((locs) => {
      setLocations(locs);
      if (locs.length > 0) setSelectedLoc(locs[0].id);
    });
  }, []);

  const loadPredictions = async (locId: string) => {
    try {
      const res = await apiService.getPredictions(locId);
      setPredictions(res.predictions || []);
      setModelMetrics(res.model_metrics || null);
    } catch (e) {
      console.error(e);
    }
  };

  const loadAnomalies = async (locId: string) => {
    try {
      const res = await apiService.getAnomalies(locId);
      setAnomalies(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (selectedLoc) {
      loadPredictions(selectedLoc);
      loadAnomalies(selectedLoc);
    }
  }, [selectedLoc]);

  const handleTrain = async () => {
    if (!selectedLoc) return;
    setIsTraining(true);
    try {
      await apiService.trainModel(selectedLoc);
      await loadPredictions(selectedLoc);
    } catch (e) {
      console.error(e);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-emerald-400" />
            ML Predictions & Isolation Forest
          </h2>
          <p className="text-xs text-slate-400">RandomForest / GradientBoosting forecast horizons & anomaly detection</p>
        </div>

        <div className="flex gap-2">
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

          <button onClick={handleTrain} disabled={isTraining} className="btn btn-primary text-xs">
            {isTraining ? 'Training Model...' : 'Retrain Model'}
          </button>
        </div>
      </div>

      {/* Model Metrics */}
      {modelMetrics && (
        <div className="grid grid-cols-3 gap-4">
          <div className="kpi-card">
            <span className="kpi-label">MODEL MAE</span>
            <span className="kpi-value text-emerald-400">{modelMetrics.mae}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">MODEL RMSE</span>
            <span className="kpi-value text-cyan-400">{modelMetrics.rmse}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">R² ACCURACY SCORE</span>
            <span className="kpi-value text-purple-400">{modelMetrics.r2}</span>
          </div>
        </div>
      )}

      {/* Predictions Horizon Card */}
      <div className="card space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-slate-100">Forecast Horizons (PM2.5)</h3>
          <span className="badge badge-warning text-[10px]">PREDICTED - NOT OBSERVED</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {predictions.map((p, i) => (
            <div key={i} className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-2">
              <div className="text-xs text-slate-400 font-semibold">{p.horizon_hours} Hour Horizon</div>
              <div className="text-3xl font-black text-emerald-400">{p.predicted_value} {p.unit}</div>
              <div className="text-[10px] text-slate-500">
                Forecast Time: {new Date(p.forecast_time).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Anomalies Detected */}
      <div className="card space-y-4">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-amber-400" />
          <h3 className="font-bold text-slate-100">Isolation Forest Anomalies</h3>
        </div>

        <div className="space-y-3">
          {anomalies.length === 0 ? (
            <div className="text-xs text-slate-500 py-4 text-center">No statistical anomalies detected in the last 24h</div>
          ) : (
            anomalies.map((a, i) => (
              <div key={i} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between items-center">
                <div>
                  <div className="text-xs font-bold text-slate-200">
                    {a.parameter} Anomaly (+{a.change_percent}%)
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Current: {a.current_value} vs Baseline: {a.baseline_value}
                  </div>
                </div>
                <span className={`severity-${a.severity.toLowerCase()}`}>{a.severity}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
