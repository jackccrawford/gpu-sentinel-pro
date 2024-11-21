# Contributing to GPU Sentinel Pro

Thank you for your interest in contributing to GPU Sentinel Pro! This document provides guidelines and workflows for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the problem, not the person
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/gpu-sentinel-pro.git
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/jackccrawford/gpu-sentinel-pro.git
   ```
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Development
```bash
cd frontend
npm install
```

### Database Setup
```bash
cd supabase
docker-compose up -d
```

## Development Workflow

1. Check TODO.md for planned features
2. Create an issue for new features/bugs
3. Write code and tests
4. Update documentation
5. Submit pull request

### Commit Messages

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test updates
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add temperature trend analysis"
```

### Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Document functions and classes
- Maximum line length: 100 characters

Example:
```python
def calculate_temperature_trend(
    temperatures: List[float],
    window_size: int = 10
) -> float:
    """
    Calculate temperature trend over time window.

    Args:
        temperatures: List of temperature readings
        window_size: Size of rolling window

    Returns:
        float: Temperature change rate
    """
    # Implementation
```

#### TypeScript (Frontend)
- Use ESLint configuration
- Document components and functions
- Use functional components
- Type all props and state

Example:
```typescript
interface TemperatureGraphProps {
  data: Temperature[];
  timeRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
}

const TemperatureGraph: React.FC<TemperatureGraphProps> = ({
  data,
  timeRange,
  onRangeChange,
}) => {
  // Implementation
};
```

### Testing

#### Backend Tests
```bash
cd backend
pytest
```

#### Frontend Tests
```bash
cd frontend
npm test
```

### Documentation

- Update API.md for endpoint changes
- Update INSTALLATION.md for setup changes
- Add JSDoc comments for frontend components
- Add docstrings for Python functions

## Feature Requests

1. Check existing issues and TODO.md
2. Create detailed issue with:
   - Use case
   - Expected behavior
   - Technical approach
   - Acceptance criteria

## Bug Reports

Include:
1. Description
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. System information:
   - OS version
   - GPU model
   - Driver version
   - Software version

## Review Process

1. Code review by maintainers
2. CI/CD checks
3. Documentation review
4. Testing verification
5. Final approval

## Release Process

1. Version bump
2. Update CHANGELOG.md
3. Create release branch
4. Run test suite
5. Create GitHub release
6. Deploy to production

## Getting Help

- Check documentation
- Search existing issues
- Join discussions
- Ask questions in issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to GPU Sentinel Pro!