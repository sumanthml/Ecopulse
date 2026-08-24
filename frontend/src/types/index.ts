/* EcoPulse TypeScript Type Definitions */

export interface Location {
  id: string;
  name: string;
  city: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  description?: string;
  created_at: string;
  sensor_count?: number;
  online_sensors?: number;
  current_aqi?: number;
  aqi_category?: string;
}

export interface Sensor {
  id: string;
  location_id: string;
  sensor_code: string;
  sensor_name: string;
  source: 'REAL' | 'SIMULATED' | 'API' | 'HISTORICAL';
  sensor_type: string;
  status: 'ONLINE' | 'OFFLINE' | 'WARNING' | 'MAINTENANCE';
  last_seen?: string;
  installation_date?: string;
  created_at: string;
  location_name?: string;
  city?: string;
  current_aqi?: number;
  health_score?: number;
}

export interface PollutionReading {
  id: string;
  sensor_id: string;
  location_id: string;
  timestamp: string;
  pm25?: number;
  pm10?: number;
  co?: number;
  co2?: number;
  no2?: number;
  so2?: number;
  o3?: number;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  wind_speed?: number;
  wind_direction?: number;
  noise_level?: number;
  source: string;
  created_at: string;
  aqi?: number;
  aqi_category?: string;
  dominant_pollutant?: string;
}

export interface CurrentPollution {
  location_id: string;
  location_name: string;
  city: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  aqi?: number;
  category?: string;
  dominant_pollutant?: string;
  pm25?: number;
  pm10?: number;
  co?: number;
  no2?: number;
  so2?: number;
  o3?: number;
  temperature?: number;
  humidity?: number;
  wind_speed?: number;
  pressure?: number;
  last_updated?: string;
  source?: string;
  sensor_count?: number;
  online_sensors?: number;
}

export interface AQIResult {
  aqi: number;
  category: string;
  dominant_pollutant?: string;
  sub_indices?: Record<string, { value: number; concentration: number; unit: string }>;
  color?: string;
}

export interface Alert {
  id: string;
  sensor_id?: string;
  location_id: string;
  parameter: string;
  value: number;
  threshold: number;
  severity: 'INFO' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  title: string;
  message?: string;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  location_name?: string;
  city?: string;
  sensor_code?: string;
}

export interface EnvironmentalInsight {
  id: string;
  location_id?: string;
  insight_type: string;
  title: string;
  content: string;
  severity?: string;
  generated_by: string;
  created_at: string;
  expires_at?: string;
  location_name?: string;
  city?: string;
}

export interface DashboardStats {
  total_locations: number;
  total_sensors: number;
  online_sensors: number;
  offline_sensors: number;
  total_readings: number;
  today_readings: number;
  active_alerts: number;
  critical_alerts: number;
}

export interface DashboardSummary {
  locations: CurrentPollution[];
  stats: DashboardStats;
  alerts: Alert[];
  insights: EnvironmentalInsight[];
  system: {
    collector: CollectorStatus;
    timestamp: string;
  };
}

export interface CollectorStatus {
  running: boolean;
  provider?: string;
  source_type?: string;
  last_fetch?: string;
  last_error?: string;
  fetch_count: number;
  error_count: number;
  interval_seconds: number;
}

export interface AnalyticsSummary {
  [key: string]: {
    mean: number;
    median: number;
    min: number;
    max: number;
    std_dev: number;
    variance?: number;
    p25?: number;
    p75?: number;
    p95?: number;
    count: number;
  };
}

export interface TrendData {
  period: string;
  mean: number;
  min: number;
  max: number;
  count: number;
}

export interface Correlation {
  param1: string;
  param2: string;
  correlation: number;
  strength: string;
  samples: number;
}

export interface Prediction {
  horizon_hours: number;
  predicted_value: number;
  target: string;
  unit: string;
  predicted_at: string;
  forecast_time: string;
}

export interface Anomaly {
  timestamp: string;
  parameter: string;
  parameter_key: string;
  current_value: number;
  baseline_value: number;
  change_percent: number;
  anomaly_score: number;
  severity: string;
  z_score: number;
  location_id: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
  };
}

export type ConnectionStatus = 'LIVE' | 'RECONNECTING' | 'OFFLINE';

export interface SystemHealth {
  status: string;
  database: string;
  provider: string;
  ai: string;
  version: string;
}
