# Seraaj API Testing Suite

This comprehensive testing suite ensures the reliability, performance, and security of the Seraaj v2 API.

## 📁 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Test configuration and fixtures
├── test_auth.py             # Authentication & authorization tests
├── test_opportunities.py    # Opportunities API tests
├── test_applications.py     # Applications API tests
├── test_verification.py     # Skill & organization verification tests
├── test_websocket.py        # Real-time WebSocket tests
├── test_integration.py      # End-to-end integration tests
└── test_performance.py      # Performance & load tests
```

## 🚀 Quick Start

### 1. Setup Test Environment

```bash
python test_runner.py setup
```

### 2. Run All Tests

```bash
python test_runner.py test
```

### 3. Run Specific Test Types

```bash
# Unit tests only
python test_runner.py test --type unit

# Integration tests
python test_runner.py test --type integration

# Performance tests
python test_runner.py test --type performance

# Authentication tests
python test_runner.py test --type auth
```

## 🧪 Test Categories

### Unit Tests
Test individual components and functions in isolation.

```bash
python test_runner.py test --type unit --verbose --coverage
```

**Coverage:**
- Authentication endpoints
- CRUD operations
- Data validation
- Business logic
- Error handling

### Integration Tests
Test complete workflows and system interactions.

```bash
python test_runner.py test --type integration
```

**Scenarios:**
- Complete volunteer journey (registration → profile → application)
- Organization workflow (registration → opportunity creation → application management)
- Application lifecycle (submission → review → approval/rejection)
- Review and rating system
- File upload integration

### Performance Tests
Test system performance under various load conditions.

```bash
python test_runner.py test --type performance
```

**Metrics:**
- Response times
- Concurrent user handling
- Database query performance
- Memory usage
- Throughput under load

### WebSocket Tests
Test real-time messaging and notification features.

```bash
python test_runner.py test --type websocket
```

**Features:**
- Connection management
- Message delivery
- Presence indicators
- Typing indicators
- Real-time notifications

## 📊 Test Reporting

### Generate Comprehensive Report

```bash
python test_runner.py report
```

This generates:
- HTML coverage report (`htmlcov/index.html`)
- XML coverage report (`coverage.xml`)
- JUnit XML report (`test-results.xml`)

### Coverage Requirements

- **Minimum Coverage:** 70%
- **Target Coverage:** 85%
- **Critical Paths:** 95%

## 🔧 Test Configuration

### Environment Variables

```bash
# Test database (uses in-memory SQLite by default)
TEST_DATABASE_URL=sqlite:///:memory:

# Test file uploads directory
TEST_UPLOAD_DIR=tests/temp/uploads

# Mock external services
MOCK_EMAIL_SERVICE=true
MOCK_PAYMENT_SERVICE=true
```

### pytest.ini Settings

Key configuration in `pytest.ini`:
- Minimum version requirements
- Test discovery patterns
- Coverage thresholds
- Warning filters
- Custom markers

## 🏃‍♂️ Running Tests

### Basic Commands

```bash
# All tests with coverage
pytest tests/ --cov=. --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Tests matching pattern
pytest tests/ -k "test_authentication"

# Tests with specific marker
pytest tests/ -m "not slow"

# Parallel execution
pytest tests/ -n auto
```

### Using Test Runner

```bash
# Fast tests only (excluding slow/performance tests)
python test_runner.py test --type fast

# Verbose output with coverage
python test_runner.py test --verbose --coverage

# Parallel execution
python test_runner.py test --parallel

# Watch mode (re-run on file changes)
python test_runner.py test --watch
```

## 🧩 Test Fixtures

### User Fixtures
- `test_user_volunteer`: Volunteer user with complete profile
- `test_user_organization`: Organization user with profile
- `test_admin_user`: Admin user for testing admin endpoints

### Data Fixtures
- `test_opportunity`: Sample opportunity for testing
- `sample_application_data`: Complete application data
- `sample_review_data`: Review and rating data

### Authentication Fixtures
- `auth_headers_volunteer`: Authorization headers for volunteer
- `auth_headers_organization`: Authorization headers for organization
- `auth_headers_admin`: Authorization headers for admin

### Utility Fixtures
- `performance_timer`: Timer for performance measurements
- `TestDataFactory`: Factory for creating bulk test data

## 🎯 Test Markers

Use pytest markers to categorize and select tests:

```bash
# Performance tests
pytest -m performance

# Slow tests
pytest -m slow

# Integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# API tests only
pytest -m api
```

Available markers:
- `slow`: Time-consuming tests
- `integration`: End-to-end tests
- `unit`: Unit tests
- `api`: API endpoint tests
- `websocket`: WebSocket tests
- `auth`: Authentication tests
- `performance`: Performance tests

## 🔍 Debugging Tests

### Verbose Output

```bash
pytest tests/test_auth.py -v -s
```

### Debug Specific Test

```bash
pytest tests/test_auth.py::TestAuthenticationEndpoints::test_user_login_success -v -s
```

### Print Debug Information

```python
def test_example(client, test_user):
    response = client.get("/v1/auth/me")
    print(f"Response: {response.json()}")  # Will show with -s flag
    assert response.status_code == 200
```

## 🚨 Continuous Integration

### GitHub Actions Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
- name: Run Tests
  run: |
    python test_runner.py setup
    python test_runner.py test --coverage
    python test_runner.py quality
```

### Pre-commit Hooks

Run tests before committing:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Performance Testing

### Load Testing Scenarios

1. **Concurrent Users**: 20 users browsing opportunities
2. **Bulk Operations**: Creating 50+ opportunities
3. **Large Datasets**: Querying 1000+ records
4. **File Uploads**: Large file handling
5. **WebSocket Connections**: Multiple concurrent connections

### Performance Benchmarks

| Operation | Target Response Time | Max Response Time |
|-----------|---------------------|-------------------|
| User Login | < 1s | < 2s |
| Opportunity List | < 2s | < 5s |
| Search Query | < 3s | < 5s |
| File Upload (1MB) | < 10s | < 30s |
| WebSocket Message | < 100ms | < 500ms |

## 🛡️ Security Testing

### Authentication Tests
- Token validation
- Role-based access control
- Password security
- Rate limiting
- Session management

### Input Validation Tests
- SQL injection prevention
- XSS prevention
- File upload security
- Data sanitization

### Authorization Tests
- Endpoint access control
- Resource ownership validation
- Admin privilege verification

## 🤝 Contributing to Tests

### Writing New Tests

1. **Follow naming conventions**: `test_feature_scenario`
2. **Use appropriate fixtures**: Leverage existing test fixtures
3. **Add docstrings**: Describe what the test validates
4. **Include edge cases**: Test both success and failure scenarios
5. **Performance considerations**: Mark slow tests appropriately

### Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should be descriptive
3. **Coverage**: Aim for high code coverage
4. **Reliability**: Tests should be deterministic
5. **Speed**: Keep tests as fast as possible

### Example Test Structure

```python
class TestFeatureEndpoints:
    """Test feature-specific endpoints"""
    
    def test_feature_success_scenario(self, client, auth_headers, test_data):
        """Test successful feature operation"""
        # Arrange
        request_data = {"key": "value"}
        
        # Act
        response = client.post("/v1/feature", json=request_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["key"] == "value"
    
    def test_feature_validation_error(self, client, auth_headers):
        """Test feature validation error handling"""
        # Test with invalid data
        response = client.post("/v1/feature", json={}, headers=auth_headers)
        assert response.status_code == 422
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection**: Ensure test database is properly configured
2. **File Permissions**: Check test file upload permissions
3. **Port Conflicts**: Ensure test ports are available
4. **Memory Usage**: Large datasets may require more memory
5. **Network Issues**: WebSocket tests may fail in restricted networks

### Debug Commands

```bash
# Check test collection
pytest --collect-only

# Run with maximum verbosity
pytest tests/ -vvv

# Show local variables on failure
pytest tests/ -l

# Enter debugger on failure
pytest tests/ --pdb
```

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🎉 Test Success Criteria

A successful test run should show:
- ✅ All critical path tests passing
- ✅ Coverage above 70%
- ✅ No security vulnerabilities
- ✅ Performance benchmarks met
- ✅ All integration scenarios working
- ✅ WebSocket functionality operational

---

**Happy Testing! 🧪✨**

For questions or issues with the test suite, please check the test documentation or create an issue in the repository.