-- Create alerts table
CREATE TABLE IF NOT EXISTS alert_thresholds (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name TEXT NOT NULL,
    warning_threshold FLOAT NOT NULL,
    critical_threshold FLOAT NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 60,
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create alerts history table
CREATE TABLE IF NOT EXISTS alert_history (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_threshold_id uuid REFERENCES alert_thresholds(id),
    gpu_index INTEGER NOT NULL,
    metric_value FLOAT NOT NULL,
    threshold_value FLOAT NOT NULL,
    severity TEXT NOT NULL,  -- 'warning' or 'critical'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for querying recent alerts
CREATE INDEX IF NOT EXISTS idx_alert_history_created_at 
ON alert_history(created_at);

-- Create function to cleanup old alert history
CREATE OR REPLACE FUNCTION cleanup_old_alerts(days_to_keep INTEGER)
RETURNS void AS $$
BEGIN
    DELETE FROM alert_history 
    WHERE created_at < NOW() - (days_to_keep || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Create function to update alert thresholds from config
CREATE OR REPLACE FUNCTION update_alert_thresholds_from_config(
    config jsonb
) RETURNS void AS $$
BEGIN
    -- Temperature alerts
    INSERT INTO alert_thresholds (
        metric_name, 
        warning_threshold, 
        critical_threshold, 
        duration_seconds
    ) VALUES (
        'temperature',
        (config->'alerts'->>'temperature_warning')::float,
        (config->'alerts'->>'temperature_critical')::float,
        (config->'alerts'->>'temperature_duration')::integer
    ) ON CONFLICT (metric_name) DO UPDATE SET
        warning_threshold = EXCLUDED.warning_threshold,
        critical_threshold = EXCLUDED.critical_threshold,
        duration_seconds = EXCLUDED.duration_seconds,
        updated_at = NOW();

    -- GPU utilization alerts
    INSERT INTO alert_thresholds (
        metric_name, 
        warning_threshold, 
        critical_threshold, 
        duration_seconds
    ) VALUES (
        'gpu_utilization',
        (config->'alerts'->>'gpu_utilization_warning')::float,
        (config->'alerts'->>'gpu_utilization_critical')::float,
        (config->'alerts'->>'gpu_utilization_duration')::integer
    ) ON CONFLICT (metric_name) DO UPDATE SET
        warning_threshold = EXCLUDED.warning_threshold,
        critical_threshold = EXCLUDED.critical_threshold,
        duration_seconds = EXCLUDED.duration_seconds,
        updated_at = NOW();

    -- Memory usage alerts
    INSERT INTO alert_thresholds (
        metric_name, 
        warning_threshold, 
        critical_threshold, 
        duration_seconds
    ) VALUES (
        'memory_usage',
        (config->'alerts'->>'memory_usage_warning')::float,
        (config->'alerts'->>'memory_usage_critical')::float,
        (config->'alerts'->>'memory_usage_duration')::integer
    ) ON CONFLICT (metric_name) DO UPDATE SET
        warning_threshold = EXCLUDED.warning_threshold,
        critical_threshold = EXCLUDED.critical_threshold,
        duration_seconds = EXCLUDED.duration_seconds,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Add unique constraint for metric_name
ALTER TABLE alert_thresholds 
ADD CONSTRAINT unique_metric_name UNIQUE (metric_name);

COMMENT ON TABLE alert_thresholds IS 'Stores configurable alert thresholds for GPU metrics';
COMMENT ON TABLE alert_history IS 'Stores history of triggered alerts';
