import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Alert } from '../types';
import { Bell, Check, ShieldAlert } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const loadAlerts = () => {
    apiService.getAlerts({ limit: 100 }).then(setAlerts);
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleAcknowledge = async (id: string) => {
    await apiService.acknowledgeAlert(id);
    loadAlerts();
  };

  const handleResolve = async (id: string) => {
    await apiService.resolveAlert(id);
    loadAlerts();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
          <Bell className="w-6 h-6 text-amber-400" />
          Threshold Alerts Log
        </h2>
        <p className="text-xs text-slate-400">Real-time alert engine log with severity classification and operational workflows</p>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/60">
              <th className="table-header">Time</th>
              <th className="table-header">Location</th>
              <th className="table-header">Parameter</th>
              <th className="table-header">Value / Threshold</th>
              <th className="table-header">Severity</th>
              <th className="table-header">Status</th>
              <th className="table-header text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id} className="table-row">
                <td className="table-cell font-mono text-xs text-slate-400">
                  {new Date(a.created_at).toLocaleString()}
                </td>
                <td className="table-cell font-semibold text-slate-200">
                  {a.location_name} ({a.city})
                </td>
                <td className="table-cell font-bold text-emerald-400">{a.parameter}</td>
                <td className="table-cell font-mono text-xs text-slate-300">
                  {a.value} / {a.threshold}
                </td>
                <td className="table-cell">
                  <span className={`severity-${a.severity.toLowerCase()}`}>{a.severity}</span>
                </td>
                <td className="table-cell">
                  <span className="text-xs font-bold uppercase text-slate-400">{a.status}</span>
                </td>
                <td className="table-cell text-right space-x-2">
                  {a.status === 'ACTIVE' && (
                    <button
                      onClick={() => handleAcknowledge(a.id)}
                      className="btn btn-secondary text-xs py-1 px-2"
                    >
                      Acknowledge
                    </button>
                  )}
                  {a.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleResolve(a.id)}
                      className="btn btn-primary text-xs py-1 px-2"
                    >
                      Resolve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
