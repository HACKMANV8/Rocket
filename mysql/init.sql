-- Create database
CREATE DATABASE IF NOT EXISTS mining_data;
USE mining_data;

-- Set flexible SQL mode
SET @@SESSION.sql_mode='';

-- Equipment Monitoring Table (WITHOUT UNIQUE constraint to avoid duplicates)
CREATE TABLE IF NOT EXISTS equipment_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(100),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    status ENUM('Operational', 'Maintenance', 'Critical', 'Offline') DEFAULT 'Operational',
    last_maintenance DATE,
    next_maintenance DATE,
    operating_hours INT DEFAULT 0,
    efficiency_score DECIMAL(5,2) DEFAULT 100.00,
    temperature_celsius DECIMAL(5,2),
    vibration_level DECIMAL(5,2),
    alerts TEXT,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_equipment_id (equipment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Mining Incidents Table
CREATE TABLE IF NOT EXISTS mining_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_date DATE NOT NULL,
    mine_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    incident_type VARCHAR(100),
    severity ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Low',
    description TEXT,
    casualties INT DEFAULT 0,
    injuries INT DEFAULT 0,
    cost_impact DECIMAL(15,2),
    response_time_minutes INT,
    status VARCHAR(50) DEFAULT 'Resolved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (incident_date),
    INDEX idx_severity (severity),
    INDEX idx_mine (mine_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Production Metrics Table
CREATE TABLE IF NOT EXISTS production_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metric_date DATE NOT NULL,
    site_name VARCHAR(255) NOT NULL,
    shift VARCHAR(20),
    material_type VARCHAR(100),
    quantity_tons DECIMAL(15,2) NOT NULL,
    target_tons DECIMAL(15,2),
    efficiency_percentage DECIMAL(5,2),
    downtime_hours DECIMAL(5,2) DEFAULT 0,
    workforce_count INT,
    energy_consumption_kwh DECIMAL(12,2),
    cost_per_ton DECIMAL(10,2),
    quality_grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (metric_date),
    INDEX idx_site (site_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Safety Compliance Table
CREATE TABLE IF NOT EXISTS safety_compliance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    audit_date DATE NOT NULL,
    site_name VARCHAR(255),
    compliance_score DECIMAL(5,2),
    violations INT DEFAULT 0,
    auditor_name VARCHAR(100),
    recommendations TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fuel Energy Table
CREATE TABLE IF NOT EXISTS fuel_energy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(100) NOT NULL,
    reading_date DATE NOT NULL,
    fuel_liters DECIMAL(10,2),
    energy_kwh DECIMAL(10,2),
    shift VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_equipment (equipment_id),
    INDEX idx_date (reading_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Maintenance Repairs Table
CREATE TABLE IF NOT EXISTS maintenance_repairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(100) NOT NULL,
    maintenance_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    cost DECIMAL(12,2),
    downtime_hours DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_equipment (equipment_id),
    INDEX idx_start_date (start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Quality Metrics Table
CREATE TABLE IF NOT EXISTS quality_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(255) NOT NULL,
    metric_date DATE NOT NULL,
    material_type VARCHAR(100),
    quality_grade ENUM('A','B','C','D') DEFAULT 'A',
    defects_found INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_site (site_name),
    INDEX idx_date (metric_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Load data from CSV files with flexible column mapping
-- Equipment Monitoring (using IGNORE to skip duplicates)
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/equipment_monitoring.csv'
IGNORE INTO TABLE equipment_monitoring
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5, @col6, @col7, @col8, @col9, @col10, @col11, @col12, @col13)
SET
    equipment_id = NULLIF(@col1, ''),
    equipment_type = NULLIF(@col2, ''),
    manufacturer = NULLIF(@col3, ''),
    model = NULLIF(@col4, ''),
    status = NULLIF(@col5, ''),
    last_maintenance = NULLIF(@col6, ''),
    next_maintenance = NULLIF(@col7, ''),
    operating_hours = NULLIF(@col8, ''),
    efficiency_score = NULLIF(@col9, ''),
    temperature_celsius = NULLIF(@col10, ''),
    vibration_level = NULLIF(@col11, ''),
    alerts = NULLIF(@col12, ''),
    location = NULLIF(@col13, '');

-- Mining Incidents
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/mining_incidents.csv'
INTO TABLE mining_incidents
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5, @col6, @col7, @col8, @col9, @col10, @col11)
SET
    incident_date = NULLIF(@col1, ''),
    mine_name = NULLIF(@col2, ''),
    location = NULLIF(@col3, ''),
    incident_type = NULLIF(@col4, ''),
    severity = NULLIF(@col5, ''),
    description = NULLIF(@col6, ''),
    casualties = NULLIF(@col7, ''),
    injuries = NULLIF(@col8, ''),
    cost_impact = NULLIF(@col9, ''),
    response_time_minutes = NULLIF(@col10, ''),
    status = NULLIF(@col11, '');

-- Production Metrics
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/production_metrics.csv'
INTO TABLE production_metrics
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5, @col6, @col7, @col8, @col9, @col10, @col11, @col12)
SET
    metric_date = NULLIF(@col1, ''),
    site_name = NULLIF(@col2, ''),
    shift = NULLIF(@col3, ''),
    material_type = NULLIF(@col4, ''),
    quantity_tons = NULLIF(@col5, ''),
    target_tons = NULLIF(@col6, ''),
    efficiency_percentage = NULLIF(@col7, ''),
    downtime_hours = NULLIF(@col8, ''),
    workforce_count = NULLIF(@col9, ''),
    energy_consumption_kwh = NULLIF(@col10, ''),
    cost_per_ton = NULLIF(@col11, ''),
    quality_grade = NULLIF(@col12, '');

-- Safety Compliance
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/safety_compliance.csv'
INTO TABLE safety_compliance
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5, @col6, @col7)
SET
    audit_date = NULLIF(@col1, ''),
    site_name = NULLIF(@col2, ''),
    compliance_score = NULLIF(@col3, ''),
    violations = NULLIF(@col4, ''),
    auditor_name = NULLIF(@col5, ''),
    recommendations = NULLIF(@col6, ''),
    follow_up_date = NULLIF(@col7, '');

-- Fuel Energy
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/fuel_energy.csv'
INTO TABLE fuel_energy
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5)
SET
    equipment_id = NULLIF(@col1, ''),
    reading_date = NULLIF(@col2, ''),
    fuel_liters = NULLIF(@col3, ''),
    energy_kwh = NULLIF(@col4, ''),
    shift = NULLIF(@col5, '');

-- Maintenance Repairs
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/maintenance_repairs.csv'
INTO TABLE maintenance_repairs
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5, @col6)
SET
    equipment_id = NULLIF(@col1, ''),
    maintenance_type = NULLIF(@col2, ''),
    start_date = NULLIF(@col3, ''),
    end_date = NULLIF(@col4, ''),
    cost = NULLIF(@col5, ''),
    downtime_hours = NULLIF(@col6, '');

-- Quality Metrics
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/quality_metrics.csv'
INTO TABLE quality_metrics
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@col1, @col2, @col3, @col4, @col5)
SET
    site_name = NULLIF(@col1, ''),
    metric_date = NULLIF(@col2, ''),
    material_type = NULLIF(@col3, ''),
    quality_grade = NULLIF(@col4, ''),
    defects_found = NULLIF(@col5, '');

-- Create user and grant permissions
CREATE USER IF NOT EXISTS 'mining_user'@'%' IDENTIFIED BY 'miningpass';
GRANT ALL PRIVILEGES ON mining_data.* TO 'mining_user'@'%';
FLUSH PRIVILEGES;

-- Create views for quick analytics
CREATE OR REPLACE VIEW incident_summary AS
SELECT 
    DATE_FORMAT(incident_date, '%Y-%m') as month,
    severity,
    COUNT(*) as incident_count,
    SUM(casualties) as total_casualties,
    AVG(cost_impact) as avg_cost
FROM mining_incidents
GROUP BY month, severity
ORDER BY month DESC;

CREATE OR REPLACE VIEW equipment_health AS
SELECT 
    status,
    COUNT(*) as equipment_count,
    AVG(efficiency_score) as avg_efficiency,
    SUM(CASE WHEN alerts IS NOT NULL THEN 1 ELSE 0 END) as alert_count
FROM equipment_monitoring
GROUP BY status;

CREATE OR REPLACE VIEW production_summary AS
SELECT 
    DATE_FORMAT(metric_date, '%Y-%m') as month,
    site_name,
    SUM(quantity_tons) as total_production,
    AVG(efficiency_percentage) as avg_efficiency,
    SUM(downtime_hours) as total_downtime
FROM production_metrics
GROUP BY month, site_name
ORDER BY month DESC;

-- Reset SQL mode
SET @@SESSION.sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));