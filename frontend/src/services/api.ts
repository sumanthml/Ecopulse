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

// Dynamically use environment variable VITE_API_BASE_URL, or fall back to Render backend URL on Vercel
const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    return 'https://ecopulse-backend-46fv.onrender.com';
  }
  return ''; // Default to relative URL for local development proxy
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health & System
  getHealth: async (): Promise<SystemHealth> => {
    const res = await api.get<SystemHealth>('/health');
    return res.data;
  },

  getSystemStatus: async () => {
    const res = await api.get<ApiResponse<any>>('/api/system/status');
    return res.data.data;
  },

  setScenario: async (scenario: string) => {
    const res = await api.post<ApiResponse<any>>(`/api/system/scenario?scenario=${scenario}`);
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get<ApiResponse<DashboardSummary>>('/api/dashboard/summary');
    return res.data.data;
  },

  // Pollution
  getCurrentPollution: async (locationId?: string): Promise<CurrentPollution[]> => {
    const url = locationId ? `/api/pollution/current?location_id=${locationId}` : '/api/pollution/current';
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
    const res = await api.get<ApiResponse<PollutionReading[]>>('/api/pollution/history', { params });
    return res.data.data;
  },

  // Locations & Sensors
  getLocations: async (): Promise<Location[]> => {
    const res = await api.get<ApiResponse<Location[]>>('/api/locations');
    return res.data.data;
  },

  getLocation: async (id: string): Promise<Location> => {
    const res = await api.get<ApiResponse<Location>>(`/api/locations/${id}`);
    return res.data.data;
  },

  getSensors: async (params?: { location_id?: string; status?: string }): Promise<Sensor[]> => {
    const res = await api.get<ApiResponse<Sensor[]>>('/api/sensors', { params });
    return res.data.data;
  },

  getSensor: async (id: string): Promise<Sensor> => {
    const res = await api.get<ApiResponse<Sensor>>(`/api/sensors/${id}`);
    return res.data.data;
  },

  // Alerts
  getAlerts: async (params?: {
    status?: string;
    severity?: string;
    location_id?: string;
    limit?: number;
  }): Promise<Alert[]> => {
    const res = await api.get<ApiResponse<Alert[]>>('/api/alerts', { params });
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
      params: { location_id: locationId, start_date: startDate, end_date: endDate },
    });
    return res.data.data;
  },

  getTrends: async (locationId: string, pollutant = 'pm25', aggregation = 'hourly', days = 7): Promise<TrendData[]> => {
    const res = await api.get<ApiResponse<TrendData[]>>('/api/analytics/trends', {
      params: { location_id: locationId, pollutant, aggregation, days },
    });
    return res.data.data;
  },

  getCorrelation: async (locationId: string, days = 7): Promise<{ correlations: Correlation[]; note: string }> => {
    const res = await api.get<ApiResponse<{ correlations: Correlation[]; note: string }>>('/api/analytics/correlation', {
      params: { location_id: locationId, days },
    });
    return res.data.data;
  },

  getHeatmap: async (locationId: string, days = 7): Promise<any> => {
    const res = await api.get<ApiResponse<any>>('/api/analytics/heatmap', {
      params: { location_id: locationId, days },
    });
    return res.data.data;
  },

  // Predictions & Anomalies
  getPredictions: async (locationId: string, target = 'pm25'): Promise<{ predictions: Prediction[]; model_metrics: any }> => {
    const res = await api.get<ApiResponse<any>>('/api/predictions', {
      params: { location_id: locationId, target },
    });
    return res.data.data;
  },

  trainModel: async (locationId: string, target = 'pm25'): Promise<any> => {
    const res = await api.post<ApiResponse<any>>(`/api/predictions/train?location_id=${locationId}&target=${target}`);
    return res.data.data;
  },

  getAnomalies: async (locationId: string, hours = 24): Promise<Anomaly[]> => {
    const res = await api.get<ApiResponse<Anomaly[]>>('/api/predictions/anomalies', {
      params: { location_id: locationId, hours },
    });
    return res.data.data;
  },

  // AI Insights
  getInsights: async (params?: { location_id?: string; insight_type?: string; limit?: number }): Promise<EnvironmentalInsight[]> => {
    const res = await api.get<ApiResponse<EnvironmentalInsight[]>>('/api/ai-insights', { params });
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
