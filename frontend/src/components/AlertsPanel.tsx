import React from 'react';
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

interface Alert {
  id: string;
  severity: 'warning' | 'critical' | 'resolved';
  message: string;
  timestamp: string;
  gpuIndex: number;
  metricName: string;
  value: number;
  threshold: number;
}

interface AlertsPanelProps {
  alerts: Alert[];
  onDismiss?: (alertId: string) => void;
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts, onDismiss }) => {
  const getSeverityIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'warning':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      case 'critical':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      case 'resolved':
        return <CheckCircleIcon sx={{ color: 'success.main' }} />;
    }
  };

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      case 'resolved':
        return 'success';
    }
  };

  return (
    <Paper sx={{ maxHeight: 400, overflow: 'auto', p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Alerts
      </Typography>
      <List>
        {alerts.map((alert) => (
          <ListItem
            key={alert.id}
            sx={{
              mb: 1,
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
            }}
            secondaryAction={
              onDismiss && (
                <IconButton
                  edge="end"
                  aria-label="dismiss"
                  onClick={() => onDismiss(alert.id)}
                >
                  <DeleteIcon />
                </IconButton>
              )
            }
          >
            <Box sx={{ mr: 2 }}>{getSeverityIcon(alert.severity)}</Box>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body1">{alert.message}</Typography>
                  <Chip
                    label={`GPU ${alert.gpuIndex}`}
                    size="small"
                    color={getSeverityColor(alert.severity)}
                    variant="outlined"
                  />
                </Box>
              }
              secondary={
                <>
                  <Typography variant="body2" color="text.secondary">
                    {format(new Date(alert.timestamp), 'MMM d, yyyy HH:mm:ss')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {alert.metricName}: {alert.value} (threshold: {alert.threshold})
                  </Typography>
                </>
              }
            />
          </ListItem>
        ))}
        {alerts.length === 0 && (
          <ListItem>
            <ListItemText
              primary={
                <Typography color="text.secondary">No active alerts</Typography>
              }
            />
          </ListItem>
        )}
      </List>
    </Paper>
  );
};

export default AlertsPanel;
