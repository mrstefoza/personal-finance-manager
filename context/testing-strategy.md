# Testing Strategy

## Overview
Comprehensive testing approach with automated test execution on every code change to ensure code quality and prevent regressions.

## Testing Philosophy

### **Quality First**
- **Test-Driven Development**: Write tests before or alongside code
- **Automated Execution**: Tests run automatically after every code change
- **Immediate Feedback**: Get test results instantly to catch issues early
- **Comprehensive Coverage**: Test all critical paths and edge cases

### **Development Workflow**
1. **Write Code** → **Write Tests** → **Run Tests** → **Verify Results**
2. **Every Code Change** triggers automatic test execution
3. **No Broken Code** gets committed without test verification
4. **Continuous Quality** through automated testing

## Test Execution Strategy

### **Automated Test Execution**
- **On Every Code Change**: Tests run automatically when files are modified
- **Immediate Feedback**: Get test results within seconds
- **Fail Fast**: Catch issues before they propagate
- **Quality Gate**: Code changes are validated by tests

### **Manual Test Execution**
```bash
# Run all tests
./scripts/dev.sh test

# Run specific test categories
./scripts/dev.sh test tests/test_api/          # API tests only
./scripts/dev.sh test tests/test_services/     # Service tests only
./scripts/dev.sh test -k "auth"                # Auth-related tests only

# Run with different options
./scripts/dev.sh test -v                       # Verbose output
./scripts/dev.sh test --cov=app                # With coverage
./scripts/dev.sh test --cov=app --cov-report=html  # HTML coverage report
```

## Test Categories

### **1. Unit Tests**
**Purpose**: Test individual functions and components in isolation

**Coverage**:
- Database operations (CRUD)
- Authentication logic (JWT, password hashing)
- MFA utilities (TOTP, email codes)
- Validation functions
- Utility functions

**Example**:
```python
def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePass123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
```

### **2. Integration Tests**
**Purpose**: Test how components work together

**Coverage**:
- API endpoints with database
- Authentication flows
- MFA setup and verification
- User management operations

**Example**:
```python
async def test_user_registration_flow(client, db):
    """Test complete user registration flow"""
    # Register user
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Verify database record
    user = await db.fetchrow("SELECT * FROM users WHERE email = $1", user_data["email"])
    assert user is not None
    assert user["email_verified"] is False
```

### **3. End-to-End Tests**
**Purpose**: Test complete user workflows

**Coverage**:
- Registration → Login → MFA → Profile Update
- Password reset flow
- Account management
- Session management

**Example**:
```python
async def test_complete_auth_flow(client, db):
    """Test complete authentication workflow"""
    # 1. Register user
    # 2. Verify email
    # 3. Login
    # 4. Setup MFA
    # 5. Login with MFA
    # 6. Update profile
    # 7. Logout
```

### **4. Security Tests**
**Purpose**: Ensure security measures work correctly

**Coverage**:
- Password strength validation
- Account lockout mechanisms
- Rate limiting
- Token security
- Input validation

**Example**:
```python
def test_account_lockout_after_failed_attempts(client):
    """Test account lockout after multiple failed login attempts"""
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json=invalid_credentials)
        assert response.status_code == 401
    
    # 6th attempt should be locked
    response = client.post("/api/v1/auth/login", json=valid_credentials)
    assert response.status_code == 423  # Locked
```

## Test Structure

### **File Organization**
```
tests/
├── conftest.py              # Test configuration & fixtures
├── test_basic.py            # Basic app functionality
├── test_api/                # API endpoint tests
│   ├── test_auth.py         # Authentication endpoints
│   ├── test_users.py        # User management endpoints
│   └── test_mfa.py          # MFA endpoints
├── test_services/           # Business logic tests
│   ├── test_auth_service.py # Authentication service
│   ├── test_user_service.py # User management service
│   └── test_mfa_service.py  # MFA service
├── test_utils/              # Utility function tests
│   ├── test_encryption.py   # Encryption utilities
│   └── test_validators.py   # Validation functions
└── test_integration/        # Integration tests
    ├── test_auth_flow.py    # Complete auth flows
    └── test_mfa_flow.py     # Complete MFA flows
```

### **Test Naming Convention**
- **Unit Tests**: `test_function_name`
- **Integration Tests**: `test_component_integration`
- **E2E Tests**: `test_complete_workflow`
- **Security Tests**: `test_security_feature`

## Test Data Management

### **Fixtures**
```python
@pytest.fixture
async def test_user(db):
    """Create a test user for testing"""
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual"
    }
    # Create user in test database
    user_id = await create_test_user(db, user_data)
    yield user_id
    # Cleanup after test
    await cleanup_test_user(db, user_id)
```

### **Test Database**
- **Separate Test Database**: Isolated from development data
- **Automatic Setup/Teardown**: Clean state for each test
- **Transaction Rollback**: Tests don't affect each other
- **Realistic Data**: Factory-generated test data

## Coverage Requirements

### **Minimum Coverage Targets**
- **Overall Coverage**: 90%+
- **Critical Paths**: 100%
- **Security Features**: 100%
- **API Endpoints**: 100%
- **Database Operations**: 95%+

### **Coverage Reports**
```bash
# Generate coverage report
./scripts/dev.sh test --cov=app --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Automated Test Execution

### **Development Workflow**
1. **Code Change** → **Automatic Test Execution** → **Results Display**
2. **Passing Tests** → **Continue Development**
3. **Failing Tests** → **Fix Issues** → **Re-run Tests**

### **Test Execution Triggers**
- **File Save**: Tests run when .py files are modified
- **Git Commit**: Tests run before commit (pre-commit hook)
- **Manual Trigger**: Tests run on demand via script

### **Test Results Display**
```
🧪 Running tests...
✅ test_health_check PASSED
✅ test_user_registration PASSED
✅ test_login_flow PASSED
❌ test_mfa_setup FAILED
   AssertionError: Expected status code 201, got 400

📊 Test Summary:
   - Total: 15 tests
   - Passed: 14
   - Failed: 1
   - Coverage: 87%
```

## Performance Testing

### **Database Performance**
- **Query Optimization**: Test database query performance
- **Connection Pooling**: Verify connection management
- **Index Usage**: Ensure proper index utilization

### **API Performance**
- **Response Times**: Measure endpoint response times
- **Concurrent Requests**: Test under load
- **Memory Usage**: Monitor resource consumption

## Continuous Integration

### **Pre-commit Hooks**
```bash
# Automatic execution before commit
git commit -m "Add new feature"
# → Format code
# → Lint code
# → Run tests
# → Check coverage
# → Commit if all pass
```

### **Quality Gates**
- **All Tests Pass**: No failing tests
- **Coverage Threshold**: Minimum 90% coverage
- **Code Quality**: No linting errors
- **Type Safety**: No type errors

## Test Maintenance

### **Regular Updates**
- **Update Tests**: When features change
- **Add New Tests**: For new functionality
- **Remove Obsolete Tests**: For removed features
- **Performance Monitoring**: Track test execution time

### **Test Documentation**
- **Clear Descriptions**: What each test verifies
- **Setup Instructions**: How to run tests
- **Troubleshooting**: Common test issues and solutions

## Tools and Frameworks

### **Testing Tools**
- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for API testing
- **factory-boy**: Test data generation
- **pytest-mock**: Mocking external services

### **Quality Tools**
- **Black**: Code formatting
- **Flake8**: Code linting
- **MyPy**: Type checking
- **pre-commit**: Git hooks

## Best Practices

### **Test Writing**
- **Arrange-Act-Assert**: Clear test structure
- **Descriptive Names**: Tests explain what they verify
- **Single Responsibility**: Each test verifies one thing
- **Independent**: Tests don't depend on each other

### **Test Data**
- **Realistic Data**: Use realistic test data
- **Edge Cases**: Test boundary conditions
- **Error Scenarios**: Test failure modes
- **Security Cases**: Test security vulnerabilities

### **Maintenance**
- **Keep Tests Fast**: Optimize test execution time
- **Regular Updates**: Update tests with code changes
- **Documentation**: Document test purpose and setup
- **Monitoring**: Track test performance and reliability 