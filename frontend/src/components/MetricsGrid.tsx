import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  LinearProgress,
  Box,
  IconButton,
} from '@mui/material';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Thermostat as ThermostatIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface GPUMetrics {
  index: number;
  name: string;
  utilization: number;
  memoryUsed: number;
  memoryTotal: number;
  temperature: number;
  fanSpeed: number;
  powerDraw: number;
  powerLimit: number;
}

interface MetricsGridProps {
  gpus: GPUMetrics[];
  onConfigureGPU?: (gpuIndex: number) => void;
}

const MetricsGrid: React.FC<MetricsGridProps> = ({ gpus, onConfigureGPU }) => {
  const getUtilizationColor = (value: number) => {
    if (value < 50) return 'success.main';
    if (value < 80) return 'warning.main';
    return 'error.main';
  };

  const getTemperatureColor = (value: number) => {
    if (value < 60) return 'success.main';
    if (value < 80) return 'warning.main';
    return 'error.main';
  };

  return (
    <Grid container spacing={3}>
      {gpus.map((gpu) => (
        <Grid item xs={12} md={6} lg={4} key={gpu.index}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">
                GPU {gpu.index}: {gpu.name}
              </Typography>
              {onConfigureGPU && (
                <IconButton
                  size="small"
                  onClick={() => onConfigureGPU(gpu.index)}
                >
                  <SettingsIcon />
                </IconButton>
              )}
            </Box>

            {/* Utilization */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SpeedIcon sx={{ mr: 1 }} />
                <Typography variant="body2">Utilization</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ flexGrow: 1, mr: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={gpu.utilization}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: 'action.hover',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getUtilizationColor(gpu.utilization),
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2">{gpu.utilization}%</Typography>
              </Box>
            </Box>

            {/* Memory */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <MemoryIcon sx={{ mr: 1 }} />
                <Typography variant="body2">Memory</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ flexGrow: 1, mr: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(gpu.memoryUsed / gpu.memoryTotal) * 100}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                    }}
                  />
                </Box>
                <Typography variant="body2">
                  {gpu.memoryUsed}/{gpu.memoryTotal} GB
                </Typography>
              </Box>
            </Box>

            {/* Temperature */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ThermostatIcon sx={{ mr: 1 }} />
                <Typography variant="body2">Temperature</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ flexGrow: 1, mr: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(gpu.temperature / 100) * 100}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: 'action.hover',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getTemperatureColor(gpu.temperature),
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2">{gpu.temperature}°C</Typography>
              </Box>
            </Box>

            {/* Power Usage */}
            <Box>
              <Typography variant="body2" color="text.secondary">
                Power: {gpu.powerDraw}W / {gpu.powerLimit}W
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Fan Speed: {gpu.fanSpeed}%
              </Typography>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};

export default MetricsGrid;
