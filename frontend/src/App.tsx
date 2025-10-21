import { useState, useEffect } from 'react'

const API_URL = 'http://localhost:5183'

/**
 * Represents comprehensive information about a single NVIDIA GPU
 * @interface GPUInfo
 */
interface GPUInfo {
  /** Unique index of the GPU in the system */
  index: number
  /** Full name/model of the GPU */
  name: string
  /** Current fan speed as a percentage (0-100) */
  fan_speed: number
  /** Current power consumption in watts */
  power_draw: number
  /** Maximum power limit in watts */
  power_limit: number
  /** Total GPU memory in megabytes */
  memory_total: number
  /** Currently used GPU memory in megabytes */
  memory_used: number
  /** Current GPU utilization as a percentage (0-100) */
  gpu_utilization: number
  /** Current GPU temperature in Celsius */
  temperature: number
  /** Highest recorded temperature in Celsius since last reset */
  peak_temperature: number
  /** Rate of temperature change in degrees Celsius per second */
  temp_change_rate: number
  /** Current compute mode of the GPU (e.g., 'Default', 'Exclusive Process') */
  compute_mode: string
}

/**
 * Metrics related to GPU stress testing/burn-in operations
 * @interface GPUBurnMetrics
 */
interface GPUBurnMetrics {
  /** Indicates if a GPU stress test is currently running */
  running: boolean
  /** Duration of the current/last stress test in seconds */
  duration: number
  /** Number of errors encountered during stress testing */
  errors: number
}

/**
 * Comprehensive GPU system information including all GPUs and system-wide metrics
 * @interface GPUData
 */
interface GPUData {
  /** Array of information for each GPU in the system */
  gpus: GPUInfo[]
  /** System-wide NVIDIA driver information */
  nvidia_info: {
    /** Installed NVIDIA driver version */
    driver_version: string
    /** Installed CUDA version */
    cuda_version: string
  }
  /** List of processes currently using GPU resources */
  processes: any[]
  /** Metrics from GPU stress testing */
  gpu_burn_metrics: GPUBurnMetrics
  /** Indicates if the data was retrieved successfully */
  success: boolean
}

/**
 * Theme configuration for the application's color scheme
 * @interface ThemeColors
 */
interface ThemeColors {
  /** Main background color of the application */
  background: string
  /** Background color for GPU info cards */
  cardBackground: string
  /** Primary text color */
  text: string
  /** Secondary/supplementary text color */
  subtext: string
  /** Border color for UI elements */
  border: string
  /** Background color for progress bar tracks */
  progressBackground: string
  /** Indicates if dark theme is active */
  isDark: boolean
}

const getColorScheme = (_isDark: boolean) => ({
  critical: {
    light: '#DC2626', // deep red (visible on white)
    dark: '#FF6B6B'   // lighter red (visible on dark)
  },
  warning: {
    light: '#EA580C', // deep orange
    dark: '#FFA94D'   // lighter orange
  },
  caution: {
    light: '#CA8A04', // deep yellow-orange
    dark: '#FFD43B'   // lighter yellow
  },
  good: {
    light: '#16A34A', // deep green
    dark: '#51CF66'   // lighter green
  },
  ideal: {
    light: '#2563EB', // deep blue
    dark: '#339AF0'   // lighter blue
  }
});

const POLLING_INTERVALS = [
  { label: '250ms', value: 250 },
  { label: '500ms', value: 500 },
  { label: '1 second', value: 1000 },
  { label: '2 seconds', value: 2000 },
  { label: '5 seconds', value: 5000 },
  { label: '10 seconds', value: 10000 }
]

function App() {
  const [data, setData] = useState<GPUData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : true
  })
  const [pollingInterval, setPollingInterval] = useState(() => {
    const saved = localStorage.getItem('pollingInterval')
    return saved ? parseInt(saved) : 1000
  })
  const [loggingEnabled, setLoggingEnabled] = useState(true)

  useEffect(() => {
    const fetchLoggingStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/logging/status`)
        if (!response.ok) throw new Error('Failed to fetch logging status')
        const data = await response.json()
        setLoggingEnabled(data.logging_enabled)
      } catch (error) {
        console.error('Error fetching logging status:', error)
      }
    }
    fetchLoggingStatus()
  }, [])

  const toggleLogging = async () => {
    try {
      const response = await fetch(`${API_URL}/api/logging/toggle`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to toggle logging')
      const data = await response.json()
      setLoggingEnabled(data.logging_enabled)
    } catch (error) {
      console.error('Error toggling logging:', error)
    }
  }

  const theme: ThemeColors = darkMode ? {
    background: '#1a1a1a',
    cardBackground: '#2d2d2d',
    text: '#e1e1e1',
    subtext: '#a0a0a0',
    border: '#404040',
    progressBackground: '#404040',
    isDark: true
  } : {
    background: '#f8f9fa',
    cardBackground: '#ffffff',
    text: '#2c3e50',
    subtext: '#666666',
    border: '#e1e4e8',
    progressBackground: '#e9ecef',
    isDark: false
  }

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  useEffect(() => {
    console.log('Polling interval set to:', pollingInterval);
    localStorage.setItem('pollingInterval', pollingInterval.toString())
  }, [pollingInterval])

  useEffect(() => {
    const fetchData = async () => {
      const startTime = Date.now();
      console.log('Starting fetch at:', new Date(startTime).toLocaleTimeString());
      try {
        console.log('Fetching from:', `${API_URL}/api/gpu-stats`);
        const response = await fetch(`${API_URL}/api/gpu-stats`)
        if (!response.ok) {
          console.error('Response not OK:', response.status, response.statusText);
          const errorData = await response.json()
          throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }
        const jsonData = await response.json()
        console.log('Response data:', jsonData);
        setData(jsonData)
        setError(null)
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error instanceof Error ? error.message : 'Failed to fetch GPU data')
      }
    }

    console.log('Setting up data fetch with interval:', pollingInterval);
    fetchData()
    const interval = setInterval(fetchData, pollingInterval)
    return () => clearInterval(interval)
  }, [pollingInterval])

  useEffect(() => {
    const pulseAnimation = `
      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
      }
    `

    const styleSheet = document.createElement('style')
    styleSheet.textContent = pulseAnimation
    document.head.appendChild(styleSheet)

    return () => {
      document.head.removeChild(styleSheet)
    }
  }, [])

  if (error) {
    return (
      <div style={{ 
        padding: '20px', 
        maxWidth: '800px', 
        margin: '40px auto',
        backgroundColor: theme.cardBackground,
        color: theme.text,
        borderRadius: '12px',
        border: `1px solid ${theme.border}`,
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          marginBottom: '24px'
        }}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill={getColorScheme(theme.isDark).warning[theme.isDark ? 'dark' : 'light']}>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <h2 style={{ margin: 0, color: theme.text }}>GPU Monitoring Unavailable</h2>
        </div>
        
        <div style={{
          backgroundColor: theme.background,
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px',
          fontFamily: 'monospace',
          fontSize: '14px',
          color: theme.subtext
        }}>
          {error}
        </div>

        <div style={{
          borderTop: `1px solid ${theme.border}`,
          paddingTop: '20px'
        }}>
          <h3 style={{ marginTop: 0, color: theme.text }}>Troubleshooting Steps:</h3>
          <ul style={{ color: theme.text, lineHeight: 1.6 }}>
            <li>Verify NVIDIA drivers are installed: <code style={{ backgroundColor: theme.background, padding: '2px 6px', borderRadius: '4px' }}>nvidia-smi</code></li>
            <li>Check GPU connection and power supply</li>
            <li>Ensure CUDA toolkit is properly installed</li>
            <li>Verify user permissions for GPU access</li>
            <li>Check system logs for driver errors</li>
          </ul>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              backgroundColor: getColorScheme(theme.isDark).good[theme.isDark ? 'dark' : 'light'],
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '16px'
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div style={{ 
        padding: '20px', 
        maxWidth: '800px', 
        margin: '40px auto',
        textAlign: 'center',
        color: theme.text
      }}>
        <div style={{
          display: 'inline-block',
          width: '40px',
          height: '40px',
          border: `4px solid ${theme.border}`,
          borderTopColor: getColorScheme(theme.isDark).good[theme.isDark ? 'dark' : 'light'],
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <style>
          {`
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}
        </style>
        <p style={{ marginTop: '16px' }}>Connecting to GPU Monitoring Service...</p>
      </div>
    )
  }

  const getMetricColor = (value: number, theme: ThemeColors): string => {
    const colors = getColorScheme(theme.isDark);
    if (value >= 90) return theme.isDark ? colors.critical.dark : colors.critical.light;
    if (value >= 75) return theme.isDark ? colors.warning.dark : colors.warning.light;
    if (value >= 50) return theme.isDark ? colors.caution.dark : colors.caution.light;
    if (value >= 25) return theme.isDark ? colors.good.dark : colors.good.light;
    return theme.isDark ? colors.ideal.dark : colors.ideal.light;
  }

  const getTemperatureColor = (temp: number): string => {
    const colors = getColorScheme(theme.isDark);
    if (temp >= 80) return theme.isDark ? colors.critical.dark : colors.critical.light;
    if (temp >= 70) return theme.isDark ? colors.warning.dark : colors.warning.light;
    if (temp >= 60) return theme.isDark ? colors.caution.dark : colors.caution.light;
    if (temp >= 50) return theme.isDark ? colors.good.dark : colors.good.light;
    return theme.isDark ? colors.ideal.dark : colors.ideal.light;
  }

  const getUtilizationColor = (utilization: number, theme: ThemeColors): string => {
    return getMetricColor(utilization, theme);
  }

  const getFanSpeedColor = (speed: number, theme: ThemeColors): string => {
    const colors = getColorScheme(theme.isDark);
    if (speed > 80) return theme.isDark ? colors.critical.dark : colors.critical.light;
    if (speed > 65) return theme.isDark ? colors.warning.dark : colors.warning.light;
    if (speed > 50) return theme.isDark ? colors.caution.dark : colors.caution.light;
    if (speed > 35) return theme.isDark ? colors.good.dark : colors.good.light;
    return theme.isDark ? colors.ideal.dark : colors.ideal.light;
  }

  const getTemperatureIcon = (rate: number): { icon: string; color: string } => {
    const colors = getColorScheme(theme.isDark);
    if (Math.abs(rate) < 1.0) return { icon: '', color: theme.text };
    return rate > 0 
      ? { icon: '⌃', color: theme.isDark ? colors.critical.dark : colors.critical.light }  // Rising temp
      : { icon: '⌄', color: theme.isDark ? colors.good.dark : colors.good.light };         // Falling temp
  }

  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '1200px', 
      margin: '0 auto', 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: theme.background,
      color: theme.text,
      minHeight: '100vh'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flexWrap: 'wrap' }}>
          <h1 style={{ margin: 0, color: theme.text }}>
            NVIDIA-SMI {data.nvidia_info.driver_version}
          </h1>
          <div style={{ 
            display: 'flex', 
            gap: '20px',
            color: theme.subtext,
            fontSize: '1rem',
            fontFamily: 'monospace',
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            <span style={{ 
              padding: '2px 6px',
              backgroundColor: theme.cardBackground,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              fontSize: '0.9em',
              display: 'flex',
              gap: '6px'
            }}>
              <span style={{ color: theme.subtext }}>Driver:</span>
              {data.nvidia_info.driver_version}
            </span>
            <span style={{ 
              padding: '2px 6px',
              backgroundColor: theme.cardBackground,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              fontSize: '0.9em',
              display: 'flex',
              gap: '6px'
            }}>
              <span style={{ color: theme.subtext }}>CUDA:</span>
              12.2
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select
            value={pollingInterval}
            onChange={(e) => setPollingInterval(parseInt(e.target.value))}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: `1px solid ${theme.border}`,
              backgroundColor: theme.cardBackground,
              color: theme.text,
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            {POLLING_INTERVALS.map(interval => (
              <option key={interval.value} value={interval.value}>
                Update every {interval.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: `1px solid ${theme.border}`,
              backgroundColor: theme.cardBackground,
              color: theme.text,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
          >
            {darkMode ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
              </svg>
            )}
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          <button
            onClick={toggleLogging}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: `1px solid ${theme.border}`,
              backgroundColor: theme.cardBackground,
              color: loggingEnabled ? getMetricColor(90, theme) : theme.subtext,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 12c0-1.1-.9-2-2-2s-2 .9-2 2 .9 2 2 2 2-.9 2-2zm-2-9c-4.97 0-9 4.03-9 9H0l4 4 4-4H5c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.51 0-2.91-.49-4.06-1.3l-1.42 1.44C8.04 20.3 9.94 21 12 21c4.97 0 9-4.03 9-9s-4.03-9-9-9z"/>
            </svg>
            {loggingEnabled ? 'Pause Logging' : 'Resume Logging'}
          </button>
        </div>
      </div>
      
      {/* GPU Cards */}
      {data.gpus.map(gpu => {
        return (
          <div key={gpu.index} style={{ 
            border: `1px solid ${theme.border}`,
            padding: '20px',
            margin: '20px 0',
            borderRadius: '8px',
            backgroundColor: theme.cardBackground,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '10px',
              marginBottom: '20px'
            }}>
              <h2 style={{ margin: 0, color: theme.text }}>{gpu.name}</h2>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <span style={{ 
                  fontSize: '0.9rem', 
                  padding: '3px 8px', 
                  backgroundColor: theme.cardBackground,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '4px',
                  color: theme.subtext
                }}>
                  GPU #{gpu.index}
                </span>
                <span style={{ 
                  fontSize: '0.9rem', 
                  padding: '3px 8px', 
                  backgroundColor: theme.cardBackground,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '4px',
                  color: theme.subtext
                }}>
                  {(gpu.memory_total / 1024).toFixed(1)} GB
                </span>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              {/* GPU Stats */}
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                <div style={{ flex: '1', minWidth: '150px' }}>
                  <div style={{ marginBottom: '8px', color: theme.subtext }}>GPU Utilization</div>
                  <div 
                    role="progressbar" 
                    aria-valuenow={gpu.gpu_utilization}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`GPU ${gpu.index} utilization: ${gpu.gpu_utilization}%`}
                    style={{ 
                      height: '24px', 
                      backgroundColor: theme.progressBackground,
                      borderRadius: '12px',
                      overflow: 'hidden',
                      position: 'relative'
                    }}
                  >
                    <div style={{
                      width: `${gpu.gpu_utilization}%`,
                      height: '100%',
                      backgroundColor: getUtilizationColor(gpu.gpu_utilization, theme),
                      transition: 'all 0.3s ease-in-out',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%)',
                        opacity: theme.isDark ? 0.1 : 0.2
                      }} />
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '4px', 
                    textAlign: 'right',
                    color: getUtilizationColor(gpu.gpu_utilization, theme)
                  }}>{gpu.gpu_utilization}%</div>
                </div>

                <div style={{ flex: '1', minWidth: '150px' }}>
                  <div style={{ marginBottom: '8px', color: theme.subtext }}>Memory Usage</div>
                  <div 
                    role="progressbar"
                    aria-valuenow={(gpu.memory_used / gpu.memory_total) * 100}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`GPU ${gpu.index} memory usage: ${(gpu.memory_used / gpu.memory_total * 100).toFixed(1)}%`}
                    style={{ 
                      height: '24px', 
                      backgroundColor: theme.progressBackground,
                      borderRadius: '12px',
                      overflow: 'hidden',
                      position: 'relative'
                    }}
                  >
                    <div style={{
                      width: `${(gpu.memory_used / gpu.memory_total) * 100}%`,
                      height: '100%',
                      backgroundColor: getUtilizationColor((gpu.memory_used / gpu.memory_total) * 100, theme),
                      transition: 'all 0.3s ease-in-out',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%)',
                        opacity: theme.isDark ? 0.1 : 0.2
                      }} />
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '4px', 
                    textAlign: 'right',
                    display: 'flex',
                    justifyContent: 'flex-end',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <span style={{
                      color: getUtilizationColor((gpu.memory_used / gpu.memory_total) * 100, theme)
                    }}>
                      {(gpu.memory_used / 1024).toFixed(1)}GB
                    </span>
                    <span style={{
                      color: theme.subtext
                    }}>
                      / {(gpu.memory_total / 1024).toFixed(1)}GB
                    </span>
                  </div>
                </div>

                <div style={{ flex: '1', minWidth: '150px' }}>
                  <div style={{ marginBottom: '8px', color: theme.subtext }}>Temperature</div>
                  <div 
                    role="progressbar"
                    aria-valuenow={gpu.temperature}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`GPU ${gpu.index} temperature: ${gpu.temperature}°C, ${Math.round(gpu.temperature * 9/5 + 32)}°F`}
                    style={{ 
                      height: '24px', 
                      backgroundColor: theme.progressBackground,
                      borderRadius: '12px',
                      overflow: 'hidden',
                      position: 'relative'
                    }}
                  >
                    <div style={{
                      width: `${Math.min((gpu.temperature / 100) * 100, 100)}%`,
                      height: '100%',
                      backgroundColor: getTemperatureColor(gpu.temperature),
                      transition: 'all 0.3s ease-in-out',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%)',
                        opacity: theme.isDark ? 0.1 : 0.2
                      }} />
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '4px', 
                    textAlign: 'right',
                    display: 'flex',
                    justifyContent: 'flex-end',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ 
                      color: getTemperatureColor(gpu.temperature),
                      fontSize: '1.1em',
                      fontWeight: 500,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      {Math.abs(gpu.temp_change_rate) >= 1.0 && (
                        <span style={{ 
                          color: getTemperatureIcon(gpu.temp_change_rate).color,
                          fontSize: '1.5em',
                          fontWeight: 'bold',
                          display: 'flex',
                          alignItems: 'center',
                          marginRight: '2px'
                        }}>
                          {getTemperatureIcon(gpu.temp_change_rate).icon}
                        </span>
                      )}
                      {Math.round(gpu.temperature)}°C
                    </span>
                    <span style={{ 
                      color: theme.subtext,
                      fontSize: '1.0em'
                    }}>
                      / {Math.round(gpu.temperature * 9/5 + 32)}°F
                    </span>
                    <div style={{ 
                      fontSize: '1.0rem', 
                      color: theme.subtext 
                    }}>
                      Peak: {gpu.peak_temperature}°C
                    </div>
                  </div>
                </div>

                <div style={{ flex: '1', minWidth: '150px' }}>
                  <div style={{ marginBottom: '8px', color: theme.subtext }}>Fan Speed</div>
                  <div 
                    role="progressbar"
                    aria-valuenow={gpu.fan_speed}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`GPU ${gpu.index} fan speed: ${gpu.fan_speed}%`}
                    style={{ 
                      height: '24px', 
                      backgroundColor: theme.progressBackground,
                      borderRadius: '12px',
                      overflow: 'hidden',
                      position: 'relative'
                    }}
                  >
                    <div style={{
                      width: `${gpu.fan_speed}%`,
                      height: '100%',
                      backgroundColor: getFanSpeedColor(gpu.fan_speed, theme),
                      transition: 'all 0.3s ease-in-out',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%)',
                        opacity: theme.isDark ? 0.1 : 0.2
                      }} />
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '4px', 
                    textAlign: 'right',
                    color: getFanSpeedColor(gpu.fan_speed, theme)
                  }}>{gpu.fan_speed}%</div>
                </div>
              </div>
            </div>
            
            {/* GPU Burn Status */}
            {data.gpu_burn_metrics.running && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: theme.cardBackground,
                borderRadius: '8px',
                border: `1px solid ${theme.border}`
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '10px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    <span style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      backgroundColor: '#ff4444',
                      animation: 'pulse 2s infinite'
                    }} />
                    <span style={{ fontWeight: 500 }}>GPU Burn Test Running</span>
                  </div>
                  <div style={{ color: theme.subtext }}>
                    Duration: {Math.floor(data.gpu_burn_metrics.duration / 60)}m {Math.round(data.gpu_burn_metrics.duration % 60)}s
                  </div>
                </div>
                {data.gpu_burn_metrics.errors > 0 && (
                  <div style={{ color: '#ff4444', marginTop: '10px' }}>
                    ⚠️ {data.gpu_burn_metrics.errors} computation errors detected
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}

      {/* Running Processes */}
      {data.processes.length > 0 && (
        <div style={{ 
          border: `1px solid ${theme.border}`,
          padding: '20px',
          marginTop: '20px',
          borderRadius: '8px',
          backgroundColor: theme.cardBackground,
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginTop: 0, color: theme.text }}>Running Processes</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '10px' 
          }}>
            {data.processes
              .filter(proc => proc.name.toLowerCase() !== 'unknown')
              .map((proc, idx) => (
                <div key={`${proc.pid}-${idx}`} style={{ 
                  padding: '10px',
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  backgroundColor: theme.cardBackground
                }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600', color: theme.text }}>{proc.name}</div>
                      <div style={{ fontSize: '12px', color: theme.subtext }}>PID: {proc.pid}</div>
                    </div>
                    <div style={{ color: theme.text }}>{proc.used_memory} MB</div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
