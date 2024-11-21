# GPU Sentinel Pro - Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA GPU with drivers installed
- Docker and Docker Compose
- VS Code (recommended)

### Initial Setup

1. **Clone and Configure**
```bash
# Clone repository
git clone https://github.com/jackccrawford/gpu-sentinel-pro.git
cd gpu-sentinel-pro

# Create Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

2. **Environment Configuration**
```bash
# Backend (.env)
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your-key
LOG_LEVEL=debug

# Frontend (.env)
VITE_API_URL=http://localhost:5500
VITE_UPDATE_INTERVAL=250
```

## Code Style Guidelines

### Python (Backend)

#### Style Guide
- Follow PEP 8
- Maximum line length: 100 characters
- Use type hints
- Use async/await for I/O operations

```python
# Good
async def get_gpu_metrics(gpu_id: int) -> Dict[str, Any]:
    """
    Fetch metrics for specific GPU.
    
    Args:
        gpu_id: ID of the GPU to monitor
        
    Returns:
        Dict containing GPU metrics
    """
    metrics = await nvidia_smi.get_metrics(gpu_id)
    return process_metrics(metrics)

# Bad
def get_gpu_metrics(id):
    metrics = nvidia_smi.get_metrics(id)
    return process_metrics(metrics)
```

#### Error Handling
```python
# Good
try:
    metrics = await nvidia_smi.get_metrics()
except NvidiaSMIError as e:
    logger.error(f"Failed to get GPU metrics: {e}")
    raise GPUError(str(e), "NVIDIA_SMI_ERROR")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Bad
try:
    metrics = nvidia_smi.get_metrics()
except:
    print("Error")
```

### TypeScript (Frontend)

#### Style Guide
- Use functional components
- Use TypeScript types/interfaces
- Use React Query for data fetching
- Maximum line length: 100 characters

```typescript
// Good
interface MetricsDisplayProps {
  gpuId: number;
  refreshInterval: number;
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({
  gpuId,
  refreshInterval,
}) => {
  const { data, error } = useQuery(['metrics', gpuId], fetchMetrics);
  
  if (error) return <ErrorDisplay error={error} />;
  if (!data) return <LoadingSpinner />;
  
  return <MetricsView data={data} />;
};

// Bad
function MetricsDisplay(props) {
  const [data, setData] = useState();
  useEffect(() => {
    fetch('/api/metrics').then(res => setData(res.data));
  }, []);
  return data ? <div>{data}</div> : null;
}
```

## Testing Standards

### Backend Testing

#### Unit Tests
```python
# test_metrics.py
import pytest
from unittest.mock import Mock, patch

class TestMetricsCollector:
    @pytest.fixture
    def collector(self):
        return MetricsCollector()
    
    @patch('nvidia_smi.get_metrics')
    async def test_collection(self, mock_get_metrics, collector):
        mock_get_metrics.return_value = {'temperature': 75}
        metrics = await collector.collect_metrics()
        assert metrics['temperature'] == 75
```

#### Integration Tests
```python
# test_api.py
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_metrics_endpoint():
    response = client.get("/api/gpu-stats")
    assert response.status_code == 200
    assert "gpus" in response.json()
```

### Frontend Testing

#### Component Tests
```typescript
// MetricsDisplay.test.tsx
import { render, screen } from '@testing-library/react';

describe('MetricsDisplay', () => {
  it('renders temperature correctly', () => {
    render(<MetricsDisplay gpuId={0} />);
    expect(screen.getByText(/Temperature/i)).toBeInTheDocument();
  });
});
```

#### Integration Tests
```typescript
// App.test.tsx
import { renderWithProviders } from '../test-utils';

test('full app rendering', async () => {
  const { container } = renderWithProviders(<App />);
  expect(container).toBeInTheDocument();
});
```

## Git Workflow

### Branch Naming
- Feature: `feature/description`
- Bug Fix: `fix/description`
- Documentation: `docs/description`
- Performance: `perf/description`

### Commit Messages
Follow conventional commits:
```bash
# Feature
git commit -m "feat: add temperature trend analysis"

# Bug fix
git commit -m "fix: correct memory usage calculation"

# Documentation
git commit -m "docs: update API documentation"

# Performance
git commit -m "perf: optimize metrics polling"
```

### Pull Request Process
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Create PR with description
6. Address review comments
7. Merge after approval

## Debugging Guide

### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug points
logger.debug(f"Metrics collected: {metrics}")

# Use VS Code debugger
# launch.json configuration provided
```

### Frontend Debugging
```typescript
// Use React DevTools
// Chrome DevTools Configuration
{
  "react-developer-tools": true,
  "redux-devtools": true
}

// Debug logging
console.debug('Metrics updated:', metrics);
```

## Performance Optimization

### Backend Optimization
- Use connection pooling
- Implement caching
- Optimize database queries
- Use async I/O

### Frontend Optimization
- Implement memoization
- Use React.memo for components
- Optimize re-renders
- Implement virtualization

## Security Best Practices

### Backend Security
- Input validation
- Rate limiting
- Authentication
- CORS configuration

### Frontend Security
- XSS prevention
- CSRF protection
- Secure storage
- API error handling

## Deployment Process

### Development
1. Run tests
2. Update documentation
3. Create PR
4. Code review
5. Merge to main

### Staging
1. Deploy to staging
2. Run integration tests
3. Performance testing
4. Security scanning

### Production
1. Create release
2. Deploy to production
3. Monitor metrics
4. Verify functionality

## Monitoring and Logging

### Logging Standards
```python
# Backend logging
logger.info("API request received", extra={
    "endpoint": "/api/metrics",
    "method": "GET",
    "user_id": user_id
})

# Frontend logging
console.info('Metrics updated', {
    timestamp: new Date(),
    metrics: metricsData
});
```

### Monitoring Metrics
- Response times
- Error rates
- Resource usage
- User activity

## Support and Maintenance

### Issue Resolution
1. Reproduce issue
2. Identify root cause
3. Implement fix
4. Add regression test
5. Deploy solution

### Regular Maintenance
- Dependency updates
- Security patches
- Performance optimization
- Documentation updates