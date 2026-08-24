import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { CurrentPollution } from '../../types';

interface PollutionMapProps {
  locations: CurrentPollution[];
  onSelectLocation?: (location: CurrentPollution) => void;
}

// Custom AQI colored SVG markers
const createAqiIcon = (aqi?: number) => {
  let color = '#999999'; // Default gray
  if (aqi !== undefined && aqi !== null) {
    if (aqi <= 50) color = '#00c853';
    else if (aqi <= 100) color = '#ffd600';
    else if (aqi <= 150) color = '#ff9100';
    else if (aqi <= 200) color = '#ff1744';
    else if (aqi <= 300) color = '#8e24aa';
    else color = '#b71c1c';
  }

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
      <path fill="${color}" stroke="#0f172a" stroke-width="2" d="M16 0C7.164 0 0 7.164 0 16c0 12 16 26 16 26s16-14 16-26C32 7.164 24.836 0 16 0z"/>
      <circle cx="16" cy="16" r="10" fill="#0f172a"/>
      <text x="16" y="20" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">${aqi ?? 'N/A'}</text>
    </svg>
  `;

  return L.divIcon({
    className: 'custom-aqi-marker',
    html: svg,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -38],
  });
};

export const PollutionMap: React.FC<PollutionMapProps> = ({ locations, onSelectLocation }) => {
  const center: [number, number] = locations.length > 0
    ? [locations[0].latitude, locations[0].longitude]
    : [20.5937, 78.9629]; // Default India center

  return (
    <div className="card h-full flex flex-col justify-between overflow-hidden p-0 relative min-h-[380px]">
      <MapContainer
        center={center}
        zoom={5}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', borderRadius: '0.75rem' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {locations.map((loc) => (
          <Marker
            key={loc.location_id}
            position={[loc.latitude, loc.longitude]}
            icon={createAqiIcon(loc.aqi)}
            eventHandlers={{
              click: () => onSelectLocation && onSelectLocation(loc),
            }}
          >
            <Popup>
              <div className="p-2 space-y-2 min-w-[200px]">
                <div className="flex justify-between items-start border-b border-slate-700 pb-1">
                  <div>
                    <h4 className="font-bold text-slate-100">{loc.location_name}</h4>
                    <p className="text-xs text-slate-400">{loc.city}, {loc.country}</p>
                  </div>
                  <span className="badge badge-online text-[10px]">
                    {loc.source || 'SIMULATED'}
                  </span>
                </div>

                <div className="flex justify-between items-center py-1">
                  <span className="text-xs text-slate-400">AQI Index</span>
                  <span className="text-lg font-black text-emerald-400">{loc.aqi ?? 'N/A'}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-2 rounded">
                  <div>
                    <span className="text-slate-400">PM2.5:</span>{' '}
                    <span className="font-semibold text-slate-200">{loc.pm25 ? `${loc.pm25} µg/m³` : 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">PM10:</span>{' '}
                    <span className="font-semibold text-slate-200">{loc.pm10 ? `${loc.pm10} µg/m³` : 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Temp:</span>{' '}
                    <span className="font-semibold text-slate-200">{loc.temperature ? `${loc.temperature} °C` : 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Humidity:</span>{' '}
                    <span className="font-semibold text-slate-200">{loc.humidity ? `${loc.humidity} %` : 'N/A'}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-slate-900/90 backdrop-blur-md p-2.5 rounded-lg border border-slate-700/60 text-xs text-slate-300 shadow-xl flex flex-wrap gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#00c853]"></span> Good (0-50)
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#ffd600]"></span> Moderate (51-100)
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#ff9100]"></span> Unhealthy SG (101-150)
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#ff1744]"></span> Unhealthy (151-200)
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#8e24aa]"></span> Very Unhealthy (201-300)
        </div>
      </div>
    </div>
  );
};
