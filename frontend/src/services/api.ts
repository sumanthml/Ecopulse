import axios from 'axios';
import type {
  ApiResponse,
  DashboardSummary,
  CurrentPollution,
  PollutionReading,
  Location,
  Sensor,
  Alert,
  EnvironmentalInsight,
  AnalyticsSummary,
  TrendData,
  Correlation,
  Prediction,
  Anomaly,
  SystemHealth,
} from '../types';

const RENDER_BACKEND_URL = 'https://ecopulse-backend-46fv.onrender.com';

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (import.meta.env.PROD) {
    return RENDER_BACKEND_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return RENDER_BACKEND_URL;
  }
  return '';
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
});

export const apiService = {
  // Health & System
  getHealth: async (): Promise<SystemHealth> => {
    const res = await api.get<SystemHealth>(`/health?_t=${Date.now()}`);
    return res.data;
  },

  getSystemStatus: async () => {
    const res = await api.get<ApiResponse<any>>(`/api/system/status?_t=${Date.now()}`);
    return res.data.data;
  },

  setScenario: async (scenario: string) => {
    const res = await api.post<ApiResponse<any>>(`/api/system/scenario?scenario=${scenario}&_t=${Date.now()}`);
    return res.data;
  },

  // Dashboard — cache-busted for real-time telemetry updates
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get<ApiResponse<DashboardSummary>>(`/api/dashboard/summary?_t=${Date.now()}`);
    return res.data.data;
  },

  // Pollution — cache-busted
  getCurrentPollution: async (locationId?: string): Promise<CurrentPollution[]> => {
    const url = locationId
      ? `/api/pollution/current?location_id=${locationId}&_t=${Date.now()}`
      : `/api/pollution/current?_t=${Date.now()}`;
    const res = await api.get<ApiResponse<CurrentPollution[]>>(url);
    return res.data.data;
  },

  getPollutionHistory: async (params: {
    location_id?: string;
    sensor_id?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<PollutionReading[]> => {
    const queryParams = { ...params, _t: Date.now() };
    const res = await api.get<ApiResponse<PollutionReading[]>>('/api/pollution/history', { params: queryParams });
    return res.data.data;
  },

  // Locations & Sensors
  getLocations: async (): Promise<Location[]> => {
    const res = await api.get<ApiResponse<Location[]>>(`/api/locations?_t=${Date.now()}`);
    return res.data.data;
  },

  getLocation: async (id: string): Promise<Location> => {
    const res = await api.get<ApiResponse<Location>>(`/api/locations/${id}?_t=${Date.now()}`);
    return res.data.data;
  },

  getSensors: async (params?: { location_id?: string; status?: string }): Promise<Sensor[]> => {
    const queryParams = { ...(params || {}), _t: Date.now() };
    const res = await api.get<ApiResponse<Sensor[]>>('/api/sensors', { params: queryParams });
    return res.data.data;
  },

  getSensor: async (id: string): Promise<Sensor> => {
    const res = await api.get<ApiResponse<Sensor>>(`/api/sensors/${id}?_t=${Date.now()}`);
    return res.data.data;
  },

  // Alerts
  getAlerts: async (params?: {
    status?: string;
    severity?: string;
    location_id?: string;
    limit?: number;
  }): Promise<Alert[]> => {
    const queryParams = { ...(params || {}), _t: Date.now() };
    const res = await api.get<ApiResponse<Alert[]>>('/api/alerts', { params: queryParams });
    return res.data.data;
  },

  acknowledgeAlert: async (id: string): Promise<any> => {
    const res = await api.put<ApiResponse<any>>(`/api/alerts/${id}/acknowledge`);
    return res.data.data;
  },

  resolveAlert: async (id: string): Promise<any> => {
    const res = await api.put<ApiResponse<any>>(`/api/alerts/${id}/resolve`);
    return res.data.data;
  },

  // Analytics
  getAnalyticsSummary: async (locationId: string, startDate?: string, endDate?: string): Promise<AnalyticsSummary> => {
    const res = await api.get<ApiResponse<AnalyticsSummary>>('/api/analytics/summary', {
      params: { location_id: locationId, start_date: startDate, end_date: endDate, _t: Date.now() },
    });
    return res.data.data;
  },

  getTrends: async (locationId: string, pollutant = 'pm25', aggregation = 'hourly', days = 7): Promise<TrendData[]> => {
    const res = await api.get<ApiResponse<TrendData[]>>('/api/analytics/trends', {
      params: { location_id: locationId, pollutant, aggregation, days, _t: Date.now() },
    });
    return res.data.data;
  },

  getCorrelation: async (locationId: string, days = 7): Promise<{ correlations: Correlation[]; note: string }> => {
    const res = await api.get<ApiResponse<{ correlations: Correlation[]; note: string }>>('/api/analytics/correlation', {
      params: { location_id: locationId, days, _t: Date.now() },
    });
    return res.data.data;
  },

  getHeatmap: async (locationId: string, days = 7): Promise<any> => {
    const res = await api.get<ApiResponse<any>>('/api/analytics/heatmap', {
      params: { location_id: locationId, days, _t: Date.now() },
    });
    return res.data.data;
  },

  // Predictions & Anomalies
  getPredictions: async (locationId: string, target = 'pm25'): Promise<{ predictions: Prediction[]; model_metrics: any }> => {
    const res = await api.get<ApiResponse<any>>('/api/predictions', {
      params: { location_id: locationId, target, _t: Date.now() },
    });
    return res.data.data;
  },

  trainModel: async (locationId: string, target = 'pm25'): Promise<any> => {
    const res = await api.post<ApiResponse<any>>(`/api/predictions/train?location_id=${locationId}&target=${target}`);
    return res.data.data;
  },

  getAnomalies: async (locationId: string, hours = 24): Promise<Anomaly[]> => {
    const res = await api.get<ApiResponse<Anomaly[]>>('/api/predictions/anomalies', {
      params: { location_id: locationId, hours, _t: Date.now() },
    });
    return res.data.data;
  },

  // AI Insights
  getInsights: async (params?: { location_id?: string; insight_type?: string; limit?: number }): Promise<EnvironmentalInsight[]> => {
    const queryParams = { ...(params || {}), _t: Date.now() };
    const res = await api.get<ApiResponse<EnvironmentalInsight[]>>('/api/ai-insights', { params: queryParams });
    return res.data.data;
  },

  generateInsight: async (locationId: string, insightType = 'general', force = false): Promise<any> => {
    const res = await api.post<ApiResponse<any>>('/api/ai-insights/generate', {
      location_id: locationId,
      insight_type: insightType,
      force,
    });
    return res.data;
  },
};
