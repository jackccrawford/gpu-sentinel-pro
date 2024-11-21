-- Create an extension for generating UUIDs if not exists
create extension if not exists "uuid-ossp";

-- Create the gpu_metrics table
create table if not exists gpu_metrics (
    id uuid primary key default uuid_generate_v4(),
    timestamp timestamptz not null default now(),
    
    -- GPU Burn Metrics
    duration integer not null,
    errors integer not null,
    running boolean not null,
    
    -- Nvidia Info
    cuda_version text not null,
    driver_version text not null,
    
    -- GPU Metrics Array (stored as JSONB)
    gpus jsonb not null,
    
    -- Additional fields
    processes jsonb default '[]'::jsonb,
    success boolean not null,
    
    -- Indexes for common queries
    created_at timestamptz not null default now()
);

-- Create indexes for better query performance
create index if not exists idx_gpu_metrics_timestamp on gpu_metrics(timestamp);
create index if not exists idx_gpu_metrics_created_at on gpu_metrics(created_at);

-- Add a comment to the table
comment on table gpu_metrics is 'Stores GPU metrics data collected from NVIDIA GPUs';