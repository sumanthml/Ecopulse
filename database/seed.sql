-- ============================================================
-- EcoPulse Seed Data
-- Realistic demonstration data for Indian cities
-- ============================================================

-- ============================================================
-- LOCATIONS (5 Indian cities)
-- ============================================================
INSERT INTO locations (id, name, city, state, country, latitude, longitude, description) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567801', 'Chennai Central', 'Chennai', 'Tamil Nadu', 'India', 13.0827, 80.2707, 'Central monitoring station in Chennai covering the main commercial district'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567802', 'Hyderabad HITEC', 'Hyderabad', 'Telangana', 'India', 17.4435, 78.3772, 'HITEC City monitoring station near the IT corridor'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567803', 'Bengaluru Koramangala', 'Bengaluru', 'Karnataka', 'India', 12.9352, 77.6245, 'Koramangala residential and commercial area monitoring'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'Delhi Connaught Place', 'Delhi', 'Delhi', 'India', 28.6315, 77.2167, 'Connaught Place central Delhi monitoring station'),
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567805', 'Mumbai Bandra', 'Mumbai', 'Maharashtra', 'India', 19.0596, 72.8295, 'Bandra West monitoring station near Western Express Highway')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SENSORS (15 sensors, 3 per location)
-- ============================================================
INSERT INTO sensors (id, location_id, sensor_code, sensor_name, source, sensor_type, status, last_seen, installation_date) VALUES
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567801', 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', 'CHN-AQ-001', 'Chennai Air Quality Primary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-01-15'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567802', 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', 'CHN-MET-001', 'Chennai Meteorological', 'SIMULATED', 'meteorological', 'ONLINE', NOW(), '2024-01-15'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567803', 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', 'CHN-AQ-002', 'Chennai Air Quality Secondary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-03-20'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567804', 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', 'HYD-AQ-001', 'Hyderabad Air Quality Primary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-02-10'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567805', 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', 'HYD-MET-001', 'Hyderabad Meteorological', 'SIMULATED', 'meteorological', 'ONLINE', NOW(), '2024-02-10'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567806', 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', 'HYD-AQ-002', 'Hyderabad Air Quality Secondary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-04-05'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567807', 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', 'BLR-AQ-001', 'Bengaluru Air Quality Primary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-01-20'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567808', 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', 'BLR-MET-001', 'Bengaluru Meteorological', 'SIMULATED', 'meteorological', 'ONLINE', NOW(), '2024-01-20'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567809', 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', 'BLR-AQ-002', 'Bengaluru Air Quality Secondary', 'SIMULATED', 'multi-pollutant', 'WARNING', NOW(), '2024-05-12'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567810', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'DEL-AQ-001', 'Delhi Air Quality Primary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2023-11-01'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567811', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'DEL-MET-001', 'Delhi Meteorological', 'SIMULATED', 'meteorological', 'ONLINE', NOW(), '2023-11-01'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567812', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'DEL-AQ-002', 'Delhi Air Quality Secondary', 'SIMULATED', 'multi-pollutant', 'OFFLINE', NOW() - INTERVAL '2 hours', '2024-06-01'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567813', 'a1b2c3d4-e5f6-7890-abcd-ef1234567805', 'MUM-AQ-001', 'Mumbai Air Quality Primary', 'SIMULATED', 'multi-pollutant', 'ONLINE', NOW(), '2024-03-01'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567814', 'a1b2c3d4-e5f6-7890-abcd-ef1234567805', 'MUM-MET-001', 'Mumbai Meteorological', 'SIMULATED', 'meteorological', 'ONLINE', NOW(), '2024-03-01'),
    ('b1b2c3d4-e5f6-7890-abcd-ef1234567815', 'a1b2c3d4-e5f6-7890-abcd-ef1234567805', 'MUM-AQ-002', 'Mumbai Air Quality Secondary', 'SIMULATED', 'multi-pollutant', 'MAINTENANCE', NOW() - INTERVAL '1 day', '2024-07-15')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SAMPLE ALERTS
-- ============================================================
INSERT INTO alerts (id, sensor_id, location_id, parameter, value, threshold, severity, title, message, status, created_at) VALUES
    ('c1b2c3d4-e5f6-7890-abcd-ef1234567801', 'b1b2c3d4-e5f6-7890-abcd-ef1234567810', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'PM2.5', 156.3, 150, 'HIGH', 'PM2.5 exceeds unhealthy threshold', 'PM2.5 concentration at Delhi Connaught Place has exceeded 150 µg/m³. Current reading: 156.3 µg/m³. AQI category: Unhealthy.', 'ACTIVE', NOW() - INTERVAL '2 hours'),
    ('c1b2c3d4-e5f6-7890-abcd-ef1234567802', 'b1b2c3d4-e5f6-7890-abcd-ef1234567810', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'AQI', 198, 150, 'HIGH', 'AQI approaching Very Unhealthy', 'Air Quality Index at Delhi Connaught Place is 198, approaching Very Unhealthy levels.', 'ACTIVE', NOW() - INTERVAL '1 hour'),
    ('c1b2c3d4-e5f6-7890-abcd-ef1234567803', 'b1b2c3d4-e5f6-7890-abcd-ef1234567801', 'a1b2c3d4-e5f6-7890-abcd-ef1234567801', 'PM10', 185.7, 150, 'MODERATE', 'PM10 elevated at Chennai', 'PM10 levels at Chennai Central are elevated. Current: 185.7 µg/m³.', 'ACKNOWLEDGED', NOW() - INTERVAL '5 hours'),
    ('c1b2c3d4-e5f6-7890-abcd-ef1234567804', 'b1b2c3d4-e5f6-7890-abcd-ef1234567812', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'SENSOR', 0, 0, 'LOW', 'Sensor offline', 'Sensor DEL-AQ-002 at Delhi has gone offline. Last seen 2 hours ago.', 'ACTIVE', NOW() - INTERVAL '2 hours'),
    ('c1b2c3d4-e5f6-7890-abcd-ef1234567805', 'b1b2c3d4-e5f6-7890-abcd-ef1234567804', 'a1b2c3d4-e5f6-7890-abcd-ef1234567802', 'NO2', 92.4, 80, 'MODERATE', 'NO2 elevated at Hyderabad', 'Nitrogen Dioxide levels at Hyderabad HITEC are above recommended threshold.', 'RESOLVED', NOW() - INTERVAL '1 day')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SAMPLE AI INSIGHTS
-- ============================================================
INSERT INTO environmental_insights (id, location_id, insight_type, title, content, severity, generated_by, created_at, expires_at) VALUES
    ('d1b2c3d4-e5f6-7890-abcd-ef1234567801', 'a1b2c3d4-e5f6-7890-abcd-ef1234567804', 'daily_report', 'Delhi Daily Air Quality Report', 
     'Air quality in Delhi remained in the Unhealthy range for most of the day, with PM2.5 being the dominant pollutant. Peak pollution was observed between 19:00-21:00 IST, consistent with evening traffic patterns and reduced atmospheric dispersion. The average AQI was 168, with a maximum of 198 recorded at 20:30 IST. NO2 levels were also elevated, suggesting significant vehicular emissions contribution.', 
     'HIGH', 'groq', NOW() - INTERVAL '6 hours', NOW() + INTERVAL '18 hours'),
    
    ('d1b2c3d4-e5f6-7890-abcd-ef1234567802', 'a1b2c3d4-e5f6-7890-abcd-ef1234567803', 'recommendation', 'Bengaluru Air Quality Advisory',
     'Current air quality in Bengaluru is Moderate with an AQI of 89. PM2.5 levels are within acceptable limits. Outdoor activities are generally safe for most individuals. Those with respiratory sensitivities may want to monitor conditions during the evening peak period (18:00-21:00).', 
     'LOW', 'groq', NOW() - INTERVAL '3 hours', NOW() + INTERVAL '21 hours')
ON CONFLICT (id) DO NOTHING;
