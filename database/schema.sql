-- ============================================================
-- EcoPulse Database Schema
-- Environmental Pollution Monitoring and Analysis System
-- 
-- Run this in Supabase SQL Editor to create all tables.
-- AQI Standard: US EPA (United States Environmental Protection Agency)
-- ============================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'analyst', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_role ON profiles(role);

-- ============================================================
-- 2. LOCATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT,
    country TEXT NOT NULL DEFAULT 'India',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_locations_city ON locations(city);
CREATE INDEX idx_locations_country ON locations(country);
CREATE INDEX idx_locations_coords ON locations(latitude, longitude);

-- ============================================================
-- 3. SENSORS
-- ============================================================
CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    sensor_code TEXT UNIQUE NOT NULL,
    sensor_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'SIMULATED' CHECK (source IN ('REAL', 'SIMULATED', 'API', 'HISTORICAL')),
    sensor_type TEXT NOT NULL DEFAULT 'multi-pollutant',
    status TEXT NOT NULL DEFAULT 'ONLINE' CHECK (status IN ('ONLINE', 'OFFLINE', 'WARNING', 'MAINTENANCE')),
    last_seen TIMESTAMPTZ,
    installation_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sensors_location ON sensors(location_id);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_sensors_source ON sensors(source);
CREATE INDEX idx_sensors_code ON sensors(sensor_code);

-- ============================================================
-- 4. POLLUTION READINGS
-- All numerical fields support NULL (provider may not supply all pollutants)
-- ============================================================
CREATE TABLE IF NOT EXISTS pollution_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Air pollutants (µg/m³ unless noted)
    pm25 DOUBLE PRECISION,          -- PM2.5 (µg/m³)
    pm10 DOUBLE PRECISION,          -- PM10 (µg/m³)
    co DOUBLE PRECISION,            -- Carbon Monoxide (mg/m³)
    co2 DOUBLE PRECISION,           -- Carbon Dioxide (ppm)
    no2 DOUBLE PRECISION,           -- Nitrogen Dioxide (µg/m³)
    so2 DOUBLE PRECISION,           -- Sulfur Dioxide (µg/m³)
    o3 DOUBLE PRECISION,            -- Ozone (µg/m³)

    -- Meteorological
    temperature DOUBLE PRECISION,    -- °C
    humidity DOUBLE PRECISION,       -- %
    pressure DOUBLE PRECISION,       -- hPa
    wind_speed DOUBLE PRECISION,     -- m/s
    wind_direction DOUBLE PRECISION, -- degrees
    noise_level DOUBLE PRECISION,    -- dB

    -- Metadata
    source TEXT NOT NULL DEFAULT 'SIMULATED' CHECK (source IN ('REAL', 'SIMULATED', 'API', 'HISTORICAL')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Critical performance indexes
CREATE INDEX idx_readings_sensor_time ON pollution_readings(sensor_id, timestamp DESC);
CREATE INDEX idx_readings_location_time ON pollution_readings(location_id, timestamp DESC);
CREATE INDEX idx_readings_timestamp ON pollution_readings(timestamp DESC);
CREATE INDEX idx_readings_created ON pollution_readings(created_at DESC);
CREATE INDEX idx_readings_source ON pollution_readings(source);

-- ============================================================
-- 5. AQI RECORDS
-- ============================================================
CREATE TABLE IF NOT EXISTS aqi_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reading_id UUID REFERENCES pollution_readings(id) ON DELETE CASCADE,
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    aqi INTEGER NOT NULL,
    category TEXT NOT NULL,
    dominant_pollutant TEXT,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_aqi_location_time ON aqi_records(location_id, calculated_at DESC);
CREATE INDEX idx_aqi_reading ON aqi_records(reading_id);
CREATE INDEX idx_aqi_calculated ON aqi_records(calculated_at DESC);

-- ============================================================
-- 6. ALERTS
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID REFERENCES sensors(id) ON DELETE SET NULL,
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    parameter TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    severity TEXT NOT NULL DEFAULT 'LOW' CHECK (severity IN ('INFO', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    title TEXT NOT NULL,
    message TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_location ON alerts(location_id);
CREATE INDEX idx_alerts_sensor ON alerts(sensor_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- ============================================================
-- 7. ENVIRONMENTAL INSIGHTS (AI-generated)
-- ============================================================
CREATE TABLE IF NOT EXISTS environmental_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL DEFAULT 'general' CHECK (insight_type IN ('general', 'anomaly', 'daily_report', 'weekly_report', 'recommendation', 'trend', 'alert_explanation')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    severity TEXT DEFAULT 'INFO' CHECK (severity IN ('INFO', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    generated_by TEXT NOT NULL DEFAULT 'groq',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_insights_location ON environmental_insights(location_id);
CREATE INDEX idx_insights_type ON environmental_insights(insight_type);
CREATE INDEX idx_insights_created ON environmental_insights(created_at DESC);

-- ============================================================
-- Enable Supabase Realtime for key tables
-- ============================================================
ALTER PUBLICATION supabase_realtime ADD TABLE pollution_readings;
ALTER PUBLICATION supabase_realtime ADD TABLE aqi_records;
ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE environmental_insights;
ALTER PUBLICATION supabase_realtime ADD TABLE sensors;

-- ============================================================
-- Row Level Security (basic - allow authenticated access)
-- ============================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE pollution_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE aqi_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE environmental_insights ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users
CREATE POLICY "Allow read access for all authenticated users" ON profiles FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON locations FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON sensors FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON pollution_readings FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON aqi_records FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON alerts FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow read access for all authenticated users" ON environmental_insights FOR SELECT TO authenticated USING (true);

-- Allow anon read access (for public dashboard)
CREATE POLICY "Allow anon read" ON locations FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON sensors FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON pollution_readings FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON aqi_records FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON alerts FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon read" ON environmental_insights FOR SELECT TO anon USING (true);

-- Allow service role full access (backend uses service role key)
CREATE POLICY "Allow service role full access" ON profiles FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON locations FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON sensors FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON pollution_readings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON aqi_records FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON alerts FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Allow service role full access" ON environmental_insights FOR ALL TO service_role USING (true) WITH CHECK (true);
