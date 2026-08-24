import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { CurrentPollution } from '../types';
import { PollutionMap } from '../components/map/PollutionMap';

export const MapPage: React.FC = () => {
  const [locations, setLocations] = useState<CurrentPollution[]>([]);

  useEffect(() => {
    apiService.getCurrentPollution().then(setLocations);
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
