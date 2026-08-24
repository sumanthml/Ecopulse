import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Radio,
  Map,
  BarChart3,
  TrendingUp,
  Cpu,
  Bell,
  Sparkles,
  FileText,
  Settings,
  ShieldCheck,
  Activity,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Live Monitoring', path: '/live-monitoring', icon: Radio },
    { label: 'Pollution Map', path: '/map', icon: Map },
    { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Predictions', path: '/predictions', icon: TrendingUp },
    { label: 'Sensors', path: '/sensors', icon: Cpu },
    { label: 'Alerts', path: '/alerts', icon: Bell },
    { label: 'AI Insights', path: '/ai-insights', icon: Sparkles },
    { label: 'Reports', path: '/reports', icon: FileText },
    { label: 'Admin', path: '/admin', icon: ShieldCheck },
  ];

  return (
    <aside
      className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 transform ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      } transition-transform duration-200 ease-in-out flex flex-col justify-between`}
    >
      <div className="p-4 space-y-6">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-emerald-500/20">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-wider text-slate-100 uppercase">ECOPULSE</h1>
            <p className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest">
              ENV INTELLIGENCE
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex justify-between items-center">
        <span>v1.0.0</span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Online
        </span>
      </div>
    </aside>
  );
};
