-- Olympic Operational Dashboard Database Setup
-- This script creates tables and inserts fake data for operational monitoring

-- 1. Venues Table
CREATE TABLE IF NOT EXISTS operational_venues (
    venue_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL,
    current_occupancy INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Operational',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Staff Deployment Table
CREATE TABLE IF NOT EXISTS operational_staff (
    staff_id SERIAL PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    active_count INTEGER NOT NULL,
    total_assigned INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Transportation Data Table
CREATE TABLE IF NOT EXISTS operational_transport (
    transport_id SERIAL PRIMARY KEY,
    time_slot VARCHAR(10) NOT NULL,
    passenger_count INTEGER NOT NULL,
    on_time_percentage DECIMAL(5,2) NOT NULL,
    date_recorded DATE DEFAULT CURRENT_DATE
);

-- 4. Event Schedule Performance Table
CREATE TABLE IF NOT EXISTS operational_schedule (
    schedule_id SERIAL PRIMARY KEY,
    day_of_week VARCHAR(10) NOT NULL,
    on_time_events INTEGER NOT NULL,
    minor_delays INTEGER NOT NULL,
    major_delays INTEGER NOT NULL,
    week_number INTEGER DEFAULT 1
);

-- 5. Resource Utilization Table
CREATE TABLE IF NOT EXISTS operational_resources (
    resource_id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL,
    utilization_percentage DECIMAL(5,2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. System Status Table
CREATE TABLE IF NOT EXISTS operational_status (
    status_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value VARCHAR(100) NOT NULL,
    status_level VARCHAR(20) DEFAULT 'Normal',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Priority Alerts Table
CREATE TABLE IF NOT EXISTS operational_alerts (
    alert_id SERIAL PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    priority_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL
);

-- 8. Operational Intelligence Table
CREATE TABLE IF NOT EXISTS operational_intelligence (
    intelligence_id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    time_frame VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clear existing data (if any)
TRUNCATE TABLE operational_venues, operational_staff, operational_transport, 
                operational_schedule, operational_resources, operational_status, 
                operational_alerts, operational_intelligence RESTART IDENTITY CASCADE;

-- Insert Venue Data
INSERT INTO operational_venues (venue_name, capacity, current_occupancy, status) VALUES
('Olympic Stadium', 80000, 76000, 'Operational'),
('Aquatics Center', 15000, 13050, 'Operational'),
('Gymnastics Arena', 12000, 11040, 'Operational'),
('Basketball Arena', 18000, 14040, 'Operational'),
('Tennis Courts', 10000, 6500, 'Operational'),
('Cycling Velodrome', 6000, 5280, 'Operational'),
('Wrestling Arena', 8000, 6560, 'Operational'),
('Boxing Arena', 9000, 8190, 'Operational');

-- Insert Staff Deployment Data
INSERT INTO operational_staff (department, active_count, total_assigned) VALUES
('Security', 485, 520),
('Medical', 127, 140),
('Technical', 298, 320),
('Volunteers', 1247, 1300),
('Catering', 189, 200),
('Transport', 156, 170),
('Media', 345, 360);

-- Insert Transportation Data
INSERT INTO operational_transport (time_slot, passenger_count, on_time_percentage) VALUES
('06:00', 1200, 98.0),
('08:00', 3400, 94.0),
('10:00', 2800, 96.0),
('12:00', 2200, 92.0),
('14:00', 3800, 89.0),
('16:00', 4200, 91.0),
('18:00', 3600, 95.0),
('20:00', 2400, 97.0),
('22:00', 1800, 99.0);

-- Insert Schedule Performance Data
INSERT INTO operational_schedule (day_of_week, on_time_events, minor_delays, major_delays) VALUES
('Monday', 45, 2, 0),
('Tuesday', 52, 3, 1),
('Wednesday', 48, 1, 0),
('Thursday', 61, 4, 1),
('Friday', 58, 2, 0),
('Saturday', 67, 3, 0),
('Sunday', 43, 1, 1);

-- Insert Resource Utilization Data
INSERT INTO operational_resources (resource_type, utilization_percentage) VALUES
('Staff', 87.0),
('Venues', 92.0),
('Equipment', 78.0),
('Transport', 94.0),
('Security', 85.0);

-- Insert System Status Data
INSERT INTO operational_status (metric_name, metric_value, status_level) VALUES
('System Status', 'All Systems Operational', 'Normal'),
('Active Events', '12', 'Normal'),
('Total Attendees', '89,432', 'Normal'),
('Active Staff', '2,847', 'Normal'),
('Weather Temperature', '24°C', 'Normal'),
('Venue Capacity', '87%', 'Normal'),
('Transportation On-Time', '94%', 'Normal'),
('Security Level', 'Normal', 'Normal'),
('Active Incidents', '3', 'Low');

-- Insert Priority Alerts Data
INSERT INTO operational_alerts (venue_name, alert_type, description, priority_level, status, created_at) VALUES
('Aquatics Center', 'Maintenance', 'Pool temperature adjustment needed', 'Medium', 'Active', CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
('Olympic Stadium', 'Security', 'Security sweep completed', 'Low', 'Resolved', CURRENT_TIMESTAMP - INTERVAL '12 minutes'),
('Transport Hub', 'Monitoring', 'Increased passenger flow detected', 'Low', 'Monitoring', CURRENT_TIMESTAMP - INTERVAL '18 minutes');

-- Insert Operational Intelligence Data
INSERT INTO operational_intelligence (insight_type, title, description, recommendation, priority, time_frame) VALUES
('Crowd Flow Prediction', 'Peak Expected at Olympic Stadium', 'Olympic Stadium - 15:30, +23% above normal capacity', 'Deploy 3 additional security teams and activate overflow parking', 'High', 'Next 2 Hours'),
('Weather Impact Analysis', 'Light Rain Expected', 'Light Rain - 16:00, affecting 3 outdoor events', 'Prepare covered areas and distribute rain gear to spectators', 'Medium', 'Today'),
('Maintenance Optimization', 'Gymnastics Arena HVAC Priority', 'Gymnastics Arena HVAC needs attention, optimal window tonight 22:00-06:00', 'Schedule maintenance team for 6-hour window between events', 'Medium', 'Tonight');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_venues_status ON operational_venues(status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON operational_alerts(priority_level, status);
CREATE INDEX IF NOT EXISTS idx_transport_time ON operational_transport(time_slot);
CREATE INDEX IF NOT EXISTS idx_schedule_day ON operational_schedule(day_of_week);
CREATE INDEX IF NOT EXISTS idx_status_updated ON operational_status(last_updated);

-- Create views for easier data access
CREATE OR REPLACE VIEW operational_dashboard_summary AS
SELECT 
    (SELECT COUNT(*) FROM operational_venues WHERE status = 'Operational') as operational_venues,
    (SELECT COUNT(*) FROM operational_venues WHERE status = 'Maintenance') as maintenance_venues,
    (SELECT COUNT(*) FROM operational_venues WHERE status = 'Preparing') as preparing_venues,
    (SELECT SUM(active_count) FROM operational_staff) as total_active_staff,
    (SELECT COUNT(*) FROM operational_alerts WHERE status = 'Active') as active_alerts,
    (SELECT AVG(utilization_percentage) FROM operational_resources) as avg_resource_utilization;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

COMMIT; 