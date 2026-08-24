import React from 'react';

interface AQIGaugeProps {
  aqi: number;
  category: string;
  dominantPollutant?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const AQIGauge: React.FC<AQIGaugeProps> = ({
  aqi,
  category,
  dominantPollutant,
  size = 'md',
}) => {
  const getCategoryColor = (aqiValue: number) => {
    if (aqiValue <= 50) return { bg: 'bg-emerald-500', text: 'text-emerald-400', border: 'border-emerald-500' };
    if (aqiValue <= 100) return { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' };
    if (aqiValue <= 150) return { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' };
    if (aqiValue <= 200) return { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' };
    if (aqiValue <= 300) return { bg: 'bg-purple-600', text: 'text-purple-400', border: 'border-purple-600' };
    return { bg: 'bg-rose-900', text: 'text-rose-400', border: 'border-rose-900' };
  };

  const colors = getCategoryColor(aqi);

  const dimensions = {
    sm: { container: 'w-32 h-32', number: 'text-3xl', label: 'text-xs' },
    md: { container: 'w-48 h-48', number: 'text-5xl', label: 'text-sm' },
    lg: { container: 'w-64 h-64', number: 'text-6xl', label: 'text-base' },
  }[size];

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div
        className={`relative ${dimensions.container} rounded-full border-4 ${colors.border} bg-slate-900/60 backdrop-blur-md flex flex-col items-center justify-center shadow-xl transition-all duration-300`}
      >
        <span className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-1">AQI</span>
        <span className={`${dimensions.number} font-black text-slate-100 tabular-nums`}>{aqi}</span>
        <span className={`mt-2 px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${colors.bg} text-slate-950`}>
          {category}
        </span>
      </div>
      {dominantPollutant && (
        <div className="mt-3 text-xs text-slate-400 font-medium">
          Dominant Pollutant: <span className="text-slate-200 font-semibold">{dominantPollutant}</span>
        </div>
      )}
    </div>
  );
};
