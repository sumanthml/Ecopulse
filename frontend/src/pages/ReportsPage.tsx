import React from 'react';
import { FileText, Download } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-slate-100 uppercase flex items-center gap-2">
          <FileText className="w-6 h-6 text-emerald-400" />
          Environmental Compliance Reports
        </h2>
        <p className="text-xs text-slate-400">Export PDF and CSV reports for academic, regulatory, and municipal analysis</p>
      </div>

      <div className="card space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-slate-400 font-semibold block mb-1">Location</label>
            <select className="select text-xs">
              <option>All Locations</option>
              <option>Chennai Central</option>
              <option>Delhi Connaught Place</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-400 font-semibold block mb-1">Timeframe</label>
            <select className="select text-xs">
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-400 font-semibold block mb-1">Format</label>
            <select className="select text-xs">
              <option>PDF Executive Summary</option>
              <option>Raw CSV Data</option>
            </select>
          </div>
        </div>

        <button className="btn btn-primary text-xs flex items-center gap-2">
          <Download className="w-4 h-4" />
          Generate and Export Report
        </button>
      </div>
    </div>
  );
};
