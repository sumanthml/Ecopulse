import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { CurrentPollution } from '../types';
import { PollutionMap } from '../components/map/PollutionMap';

const FALLBACK_MAP_LOCATIONS: CurrentPollution[] = [
  { location_id: '1', location_name: 'Chennai Central', city: 'Chennai', state: 'Tamil Nadu', country: 'India', latitude: 13.0827, longitude: 80.2707, aqi: 165, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 83.4, pm10: 158.9, temperature: 31.0, humidity: 75.9 },
  { location_id: '2', location_name: 'Hyderabad HITEC', city: 'Hyderabad', state: 'Telangana', country: 'India', latitude: 17.4435, longitude: 78.3772, aqi: 168, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 88.1, pm10: 162.3, temperature: 32.5, humidity: 68.0 },
  { location_id: '3', location_name: 'Bengaluru Koramangala', city: 'Bengaluru', state: 'Karnataka', country: 'India', latitude: 12.9352, longitude: 77.6245, aqi: 161, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 74.5, pm10: 94.4, temperature: 24.6, humidity: 67.7 },
  { location_id: '4', location_name: 'Delhi Connaught Place', city: 'Delhi', state: 'Delhi', country: 'India', latitude: 28.6315, longitude: 77.2167, aqi: 228, category: 'Very Unhealthy', dominant_pollutant: 'PM2.5', pm25: 142.0, pm10: 210.0, temperature: 28.0, humidity: 62.0 },
  { location_id: '5', location_name: 'Mumbai Bandra', city: 'Mumbai', state: 'Maharashtra', country: 'India', latitude: 19.0596, longitude: 72.8295, aqi: 172, category: 'Unhealthy', dominant_pollutant: 'PM2.5', pm25: 89.0, pm10: 168.0, temperature: 30.0, humidity: 78.0 },
];

export const MapPage: React.FC = () => {
  const [locations, setLocations] = useState<CurrentPollution[]>(FALLBACK_MAP_LOCATIONS);

  useEffect(() => {
    apiService.getCurrentPollution().then((data) => {
      if (data && data.length > 0) setLocations(data);
    }).catch(console.warn);
  }, []);

  return (
    <div className="h-[calc(100vh-7rem)] flex flex-col space-y-4">
      <div>
        <h2 className="text-2xl font-black text-slate-100 uppercase">Geospatial Pollution Map</h2>
        <p className="text-xs text-slate-400">Interactive OpenStreetMap view of all active monitoring stations</p>
      </div>
      <div className="flex-1">
        <PollutionMap locations={locations} />
      </div>
    </div>
  );
};
