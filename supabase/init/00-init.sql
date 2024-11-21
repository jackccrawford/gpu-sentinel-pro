-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the gpu_metrics table
CREATE TABLE IF NOT EXISTS gpu_metrics (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp timestamptz NOT NULL DEFAULT now(),
    
    -- GPU Burn Metrics
    duration integer NOT NULL,
    errors integer NOT NULL,
    running boolean NOT NULL,
    
    -- Nvidia Info
    cuda_version text NOT NULL,
    driver_version text NOT NULL,
    
    -- GPU Metrics Array (stored as JSONB)
    gpus jsonb NOT NULL,
    
    -- Additional fields
    processes jsonb DEFAULT '[]'::jsonb,
    success boolean NOT NULL,
    
    -- Indexes for common queries
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_gpu_metrics_timestamp ON gpu_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_gpu_metrics_created_at ON gpu_metrics(created_at);

-- Set up row level security (RLS)
ALTER TABLE gpu_metrics ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for now (we can restrict this later)
CREATE POLICY "Allow all operations on gpu_metrics" 
    ON gpu_metrics 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- Add a comment to the table
COMMENT ON TABLE gpu_metrics IS 'Stores GPU metrics data collected from NVIDIA GPUs';