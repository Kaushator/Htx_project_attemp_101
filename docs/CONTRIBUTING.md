# Contributing to HTX Trading Analytics Platform

Thank you for your interest in contributing to the HTX Trading Analytics Platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Environment Setup

1. **Clone the repository and switch to the active branch**:
   ```bash
   git clone https://github.com/Kaushator/Htx_project_attemp_101.git
   cd Htx_project_attemp_101
   git checkout copilot-refactor
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Frontend setup** (optional):
   ```bash
   cd frontend
   npm install
   ```

4. **Database setup**:
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Environment configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

### Development Commands

```bash
# Using Makefile (recommended)
make install      # Install all dependencies
make dev          # Start backend dev server
make test         # Run tests
make lint         # Run linting
make format       # Format code

# Manual commands
cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8004
cd frontend && npm run dev
```

## 📋 Branch Strategy

### Active Development
- **Main branch**: `copilot-refactor` - All active development happens here
- **Target base**: Always create PRs against `copilot-refactor`
- **Feature branches**: Create from `copilot-refactor`, name as `feature/description` or `fix/description`

### Historical Branches
- **Legacy branch**: `qoder-experience` - Archived as reference only
- **Do not**: Use or merge code from legacy branches without explicit approval

### Branch Naming Convention
```
feature/add-risk-metrics       # New features
fix/pnl-calculation-bug       # Bug fixes
docs/update-api-guide         # Documentation
chore/update-dependencies     # Maintenance
```

## 🎯 Contribution Types

### 1. Bug Reports
Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)

**Include**:
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or screenshots

### 2. Feature Requests
Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)

**Include**:
- Problem statement
- Proposed solution
- Alternative solutions considered
- Impact on existing functionality

### 3. Code Contributions
See [Development Guidelines](#-development-guidelines) below

### 4. Documentation
- API documentation in docstrings
- Architecture documentation in `/docs`
- README updates for new features
- Code comments for complex logic

## 💻 Development Guidelines

### Code Standards

#### Python (Backend)
- **Style**: [Black](https://black.readthedocs.io/) formatting (line length 88)
- **Import sorting**: [isort](https://pycqa.github.io/isort/) with Black compatibility
- **Linting**: [Ruff](https://docs.astral.sh/ruff/) for fast linting
- **Type hints**: Required for all public functions and class methods
- **Docstrings**: Google style for all public APIs

```python
# Example function with proper typing and docstrings
async def calculate_portfolio_pnl(
    trades: List[Trade], 
    deposits: List[Deposit]
) -> PnLReport:
    """Calculate portfolio profit and loss using FIFO method.
    
    Args:
        trades: List of trade records to analyze
        deposits: List of deposit records for cost basis
        
    Returns:
        PnLReport containing realized/unrealized PnL and metrics
        
    Raises:
        ValueError: If trades contain invalid data
        CalculationError: If PnL computation fails
    """
    # Implementation
```

#### JavaScript/React (Frontend)
- **Style**: [Prettier](https://prettier.io/) formatting
- **Linting**: [ESLint](https://eslint.org/) with React hooks rules
- **Components**: Functional components with hooks
- **State management**: React Context + useReducer or Redux Toolkit
- **Styling**: TailwindCSS utility classes

```jsx
// Example component with proper structure
import React, { useState, useEffect } from 'react';
import { usePnLData } from '../hooks/usePnLData';

export const PnLDashboard = ({ userId }) => {
  const { data, loading, error } = usePnLData(userId);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Component content */}
    </div>
  );
};
```

### Testing Requirements

#### Backend Tests
- **Unit tests**: For all service layer functions
- **Integration tests**: For API endpoints and database operations
- **Coverage target**: Minimum 80% code coverage
- **Framework**: pytest with async support

```python
# Example test structure
import pytest
from app.services.pnl import PnLService

@pytest.mark.asyncio
async def test_calculate_pnl_fifo():
    """Test FIFO PnL calculation with sample trades."""
    # Arrange
    service = PnLService(mock_db_service)
    trades = create_sample_trades()
    
    # Act
    result = await service.calculate_portfolio_pnl(trades)
    
    # Assert
    assert result.realized_pnl == Decimal('100.50')
    assert result.unrealized_pnl == Decimal('-25.30')
```

#### Frontend Tests
- **Component tests**: Using React Testing Library
- **Integration tests**: For user workflows
- **E2E tests**: For critical user paths (optional)

```jsx
// Example component test
import { render, screen, fireEvent } from '@testing-library/react';
import { PnLDashboard } from '../PnLDashboard';

test('displays PnL data when loaded', async () => {
  render(<PnLDashboard userId={1} />);
  
  expect(await screen.findByText('Portfolio PnL')).toBeInTheDocument();
  expect(screen.getByText('$1,234.56')).toBeInTheDocument();
});
```

### Performance Guidelines

#### Backend Performance
- **Async operations**: Use async/await for all I/O operations
- **Database queries**: Optimize with proper indexes and pagination
- **Caching**: Implement Redis caching for expensive calculations
- **Response times**: Target ≤ 200ms for cached endpoints

#### Frontend Performance
- **Bundle size**: Keep bundle size < 500KB (gzipped)
- **Code splitting**: Lazy load components for better initial load
- **Memoization**: Use React.memo and useMemo for expensive computations
- **API calls**: Implement proper loading states and error handling

## 🔄 Pull Request Process

### 1. Pre-submission Checklist
- [ ] Code follows style guidelines (run `make lint`)
- [ ] All tests pass (run `make test`)
- [ ] Documentation updated for new features
- [ ] Commit messages follow [Conventional Commits](#conventional-commits)
- [ ] PR targets `copilot-refactor` branch

### 2. Pull Request Template
Use the [PR Template](.github/PULL_REQUEST_TEMPLATE.md)

**Include**:
- Description of changes
- Type of change (feature, bugfix, docs, etc.)
- Testing performed
- Screenshots for UI changes
- Breaking changes (if any)

### 3. Review Process
- **Automatic checks**: CI pipeline must pass
- **Code review**: At least one approval required
- **Testing**: Reviewer should test functionality
- **Documentation**: Check that docs are updated

### 4. Merge Requirements
- All CI checks passing
- Code review approved
- No merge conflicts
- Branch up to date with target

## 📝 Conventional Commits

We use [Conventional Commits](https://conventionalcommits.org/) for consistent commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```bash
feat(api): add portfolio performance metrics endpoint

Add new endpoint to calculate and return portfolio performance
metrics including Sharpe ratio, maximum drawdown, and win rate.

Closes #123

fix(pnl): correct FIFO calculation for partial sells

The FIFO algorithm was incorrectly handling partial position
sales, leading to inaccurate unrealized PnL calculations.

Breaking change: PnL API response format updated

docs(readme): update installation instructions

chore(deps): update FastAPI to v0.104.0
```

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest                           # All tests
pytest tests/unit               # Unit tests only
pytest tests/integration       # Integration tests only
pytest --cov=app               # With coverage

# Frontend tests
cd frontend
npm test                       # Interactive mode
npm run test:ci               # CI mode
npm run test:coverage         # With coverage
```

### Test Structure

```
backend/tests/
├── unit/
│   ├── test_services/
│   │   ├── test_pnl_service.py
│   │   └── test_parser_service.py
│   └── test_models/
├── integration/
│   ├── test_api_endpoints.py
│   └── test_database.py
└── fixtures/
    ├── sample_data.py
    └── conftest.py

frontend/src/
├── __tests__/
│   ├── components/
│   └── hooks/
└── test-utils/
    └── render-with-providers.jsx
```

### Writing Good Tests

#### Unit Tests
- Test one unit of functionality
- Use mocks for external dependencies
- Cover both happy path and error cases
- Use descriptive test names

#### Integration Tests
- Test interaction between components
- Use real database for backend tests
- Test complete user workflows
- Verify error handling and edge cases

## 🚀 Deployment

### Development Deployment
```bash
# Local development
make dev

# Docker development environment
docker-compose up --build
```

### Production Considerations
- Environment variables properly configured
- Database migrations applied
- Static files served efficiently
- Security headers configured
- Monitoring and logging enabled

## 📖 Documentation

### API Documentation
- Use FastAPI automatic documentation
- Add comprehensive docstrings
- Include example requests/responses
- Document error conditions

### Code Documentation
- Comment complex business logic
- Explain non-obvious architectural decisions
- Update documentation with code changes
- Use type hints for better IDE support

### Architecture Documentation
- Keep `/docs/ARCHITECTURE.md` updated
- Document significant design decisions
- Explain trade-offs and alternatives
- Include diagrams for complex flows

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on what's best for the community
- Use welcoming and inclusive language
- Be collaborative and constructive

### Communication
- Use GitHub issues for bugs and features
- Use PR comments for code-specific discussions
- Be clear and concise in communication
- Provide constructive feedback

### Recognition
- Contributors will be recognized in releases
- Significant contributions may earn maintainer status
- Documentation improvements are highly valued
- Code reviews and testing are appreciated

## 🆘 Getting Help

### Resources
- [README.md](README.md) - Project overview and quick start
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Detailed development setup

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **PR Comments**: For code-specific questions

### Common Issues
- **Import errors**: Ensure virtual environment is activated
- **Database errors**: Run `alembic upgrade head`
- **Port conflicts**: Check if port 8004 is available
- **Dependency issues**: Try `pip install -r requirements-dev.txt`

---

Thank you for contributing to the HTX Trading Analytics Platform! 🚀

Your contributions help make this project better for everyone in the trading community.