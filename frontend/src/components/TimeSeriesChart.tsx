import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { Box, Typography, useTheme } from '@mui/material';

interface TimeSeriesProps {
  data: Array<{
    timestamp: string;
    value: number;
  }>;
  title: string;
  dataKey: string;
  color?: string;
  unit?: string;
}

const TimeSeriesChart: React.FC<TimeSeriesProps> = ({
  data,
  title,
  dataKey,
  color = '#8884d8',
  unit = '',
}) => {
  const theme = useTheme();

  const formatXAxis = (tickItem: string) => {
    return format(new Date(tickItem), 'HH:mm:ss');
  };

  const formatTooltip = (value: number) => {
    return `${value}${unit}`;
  };

  return (
    <Box sx={{ width: '100%', height: 300, p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <ResponsiveContainer>
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatXAxis}
            stroke={theme.palette.text.primary}
          />
          <YAxis stroke={theme.palette.text.primary} />
          <Tooltip
            labelFormatter={(label: string) => format(new Date(label), 'HH:mm:ss')}
            formatter={(value: number) => [formatTooltip(value), title]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            dot={false}
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default TimeSeriesChart;
