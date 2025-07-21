# QA Negative Testing Guide

## Overview
This guide covers all negative test scenarios that QA should test to ensure the API handles errors gracefully and securely.

## 🧪 Test Categories

### 1. **Authentication Endpoints**

#### **POST /api/v1/auth/register**

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty email**: `{"email": "", "password": "SecurePass123!", ...}`
- [ ] **Invalid email format**: `{"email": "invalid-email", "password": "SecurePass123!", ...}`
- [ ] **Empty password**: `{"email": "test@example.com", "password": "", ...}`
- [ ] **Password too short**: `{"email": "test@example.com", "password": "Abc1!", ...}`
- [ ] **Password missing uppercase**: `{"email": "test@example.com", "password": "securepass123!", ...}`
- [ ] **Password missing lowercase**: `{"email": "test@example.com", "password": "SECUREPASS123!", ...}`
- [ ] **Password missing digit**: `{"email": "test@example.com", "password": "SecurePass!", ...}`
- [ ] **Password missing special char**: `{"email": "test@example.com", "password": "SecurePass123", ...}`
- [ ] **Empty full_name**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": "", ...}`
- [ ] **Full name too short**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": "A", ...}`
- [ ] **Invalid phone**: `{"email": "test@example.com", "password": "SecurePass123!", "phone": "invalid", ...}`
- [ ] **Invalid user_type**: `{"email": "test@example.com", "password": "SecurePass123!", "user_type": "invalid", ...}`
- [ ] **Invalid language**: `{"email": "test@example.com", "password": "SecurePass123!", "language_preference": "invalid", ...}`
- [ ] **Invalid currency**: `{"email": "test@example.com", "password": "SecurePass123!", "currency_preference": "invalid", ...}`

**✅ Expected to PASS (422 Missing Field Errors):**
- [ ] **Missing email**: `{"password": "SecurePass123!", "full_name": "Test User", "phone": "+37412345678"}`
- [ ] **Missing password**: `{"email": "test@example.com", "full_name": "Test User", "phone": "+37412345678"}`
- [ ] **Missing full_name**: `{"email": "test@example.com", "password": "SecurePass123!", "phone": "+37412345678"}`
- [ ] **Missing phone**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": "Test User"}`
- [ ] **Only email**: `{"email": "test@example.com"}`
- [ ] **Only password**: `{"password": "SecurePass123!"}`
- [ ] **Empty request body**: `{}`

**✅ Expected to PASS (422 Null Value Errors):**
- [ ] **Null email**: `{"email": null, "password": "SecurePass123!", "full_name": "Test User", "phone": "+37412345678"}`
- [ ] **Null password**: `{"email": "test@example.com", "password": null, "full_name": "Test User", "phone": "+37412345678"}`
- [ ] **Null full_name**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": null, "phone": "+37412345678"}`
- [ ] **Null phone**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": "Test User", "phone": null}`
- [ ] **Null user_type**: `{"email": "test@example.com", "password": "SecurePass123!", "full_name": "Test User", "phone": "+37412345678", "user_type": null}`

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Duplicate email**: Register same email twice
- [ ] **Malformed JSON**: Send invalid JSON in request body

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors
- `500` for server errors

#### **POST /api/v1/auth/login**

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty email**: `{"email": "", "password": "SecurePass123!"}`
- [ ] **Invalid email format**: `{"email": "invalid-email", "password": "SecurePass123!"}`
- [ ] **Empty password**: `{"email": "test@example.com", "password": ""}`
- [ ] **Whitespace password**: `{"email": "test@example.com", "password": "   "}`

**✅ Expected to PASS (422 Missing Field Errors):**
- [ ] **Missing email**: `{"password": "SecurePass123!"}`
- [ ] **Missing password**: `{"email": "test@example.com"}`
- [ ] **Empty request body**: `{}`

**✅ Expected to PASS (422 Null Value Errors):**
- [ ] **Null email**: `{"email": null, "password": "SecurePass123!"}`
- [ ] **Null password**: `{"email": "test@example.com", "password": null}`

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **Wrong password**: `{"email": "test@example.com", "password": "WrongPass123!"}`
- [ ] **Non-existent email**: `{"email": "nonexistent@example.com", "password": "SecurePass123!"}`
- [ ] **Unverified email**: Login with user that hasn't verified email
- [ ] **Inactive account**: Login with suspended/disabled account

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `401` for authentication errors

#### **POST /api/v1/auth/refresh**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **Invalid refresh token**: `{"refresh_token": "invalid_token"}`
- [ ] **Expired refresh token**: Use expired refresh token
- [ ] **Already used refresh token**: Use refresh token that was already consumed
- [ ] **Malformed token**: `{"refresh_token": "not.a.valid.jwt"}`
- [ ] **Wrong token type**: Use access token instead of refresh token

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty refresh token**: `{"refresh_token": ""}`
- [ ] **Missing refresh token**: `{}`
- [ ] **Null refresh token**: `{"refresh_token": null}`
- [ ] **Malformed JSON**: Send invalid JSON

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `401` for authentication errors

#### **POST /api/v1/auth/logout**

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty refresh token**: `{"refresh_token": ""}`
- [ ] **Missing refresh token**: `{}`
- [ ] **Null refresh token**: `{"refresh_token": null}`
- [ ] **Malformed JSON**: Send invalid JSON

**✅ Expected to PASS (200 Success):**
- [ ] **Invalid refresh token**: Should still return success (security through obscurity)
- [ ] **Already logged out token**: Should still return success

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `200` for success (even with invalid tokens)

#### **POST /api/v1/auth/verify-email**

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty token**: `{"token": ""}`
- [ ] **Missing token**: `{}`
- [ ] **Null token**: `{"token": null}`
- [ ] **Malformed JSON**: Send invalid JSON

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Invalid token**: `{"token": "invalid-token"}`
- [ ] **Expired token**: Use expired verification token
- [ ] **Already verified**: Use token for already verified email

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors

#### **POST /api/v1/auth/resend-verification**

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty email**: `{"email": ""}`
- [ ] **Invalid email format**: `{"email": "invalid-email"}`
- [ ] **Missing email**: `{}`
- [ ] **Null email**: `{"email": null}`
- [ ] **Malformed JSON**: Send invalid JSON

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Non-existent email**: `{"email": "nonexistent@example.com"}`
- [ ] **Already verified email**: `{"email": "verified@example.com"}`

**Expected Response Codes:**
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors

### 2. **User Management Endpoints**

#### **GET /api/v1/users/profile**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token format**: `Authorization: Bearer invalid_token`
- [ ] **Expired access token**: Use expired access token
- [ ] **Wrong token type**: Use refresh token instead of access token
- [ ] **Malformed token**: `Authorization: Bearer not.a.valid.jwt`

**Expected Response Codes:**
- `401` for authentication errors

#### **PUT /api/v1/users/profile**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Invalid full_name**: `{"full_name": ""}` or `{"full_name": "A"}`
- [ ] **Invalid phone**: `{"phone": "invalid"}`
- [ ] **Invalid language**: `{"language_preference": "invalid"}`
- [ ] **Invalid currency**: `{"currency_preference": "invalid"}`

**✅ Expected to PASS (422 Null Value Errors):**
- [ ] **Null full_name**: `{"full_name": null}`
- [ ] **Null phone**: `{"phone": null}`
- [ ] **Null language**: `{"language_preference": null}`
- [ ] **Null currency**: `{"currency_preference": null}`

**Expected Response Codes:**
- `401` for authentication errors
- `422` for validation errors (invalid formats, null values)

### 3. **MFA Endpoints**

#### **POST /api/v1/mfa/totp/setup**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**Expected Response Codes:**
- `401` for authentication errors

#### **POST /api/v1/mfa/totp/verify**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty code**: `{"code": ""}`
- [ ] **Invalid code format**: `{"code": "12345"}` (too short)
- [ ] **Non-numeric code**: `{"code": "abcdef"}`
- [ ] **Missing code**: `{}`
- [ ] **Null code**: `{"code": null}`

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Invalid TOTP code**: `{"code": "123456"}` (wrong code)
- [ ] **TOTP not setup**: Try to verify without setting up TOTP

**Expected Response Codes:**
- `401` for authentication errors
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors

#### **POST /api/v1/mfa/email/setup**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**Expected Response Codes:**
- `401` for authentication errors

#### **POST /api/v1/mfa/email/verify**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty code**: `{"code": ""}`
- [ ] **Invalid code format**: `{"code": "12345"}` (too short)
- [ ] **Missing code**: `{}`
- [ ] **Null code**: `{"code": null}`

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Invalid email code**: `{"code": "123456"}` (wrong code)
- [ ] **Email MFA not setup**: Try to verify without setting up email MFA
- [ ] **Expired code**: Use expired email code

**Expected Response Codes:**
- `401` for authentication errors
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors

#### **POST /api/v1/mfa/backup/verify**

**✅ Expected to PASS (401 Authentication Errors):**
- [ ] **No Authorization header**: Request without Authorization
- [ ] **Invalid token**: Use invalid access token

**✅ Expected to PASS (422 Validation Errors):**
- [ ] **Empty code**: `{"code": ""}`
- [ ] **Invalid code format**: `{"code": "1234567"}` (wrong length)
- [ ] **Missing code**: `{}`
- [ ] **Null code**: `{"code": null}`

**✅ Expected to PASS (400 Business Logic Errors):**
- [ ] **Invalid backup code**: `{"code": "12345678"}` (wrong code)
- [ ] **Already used backup code**: Use backup code that was already consumed

**Expected Response Codes:**
- `401` for authentication errors
- `422` for validation errors (missing fields, null values, invalid formats)
- `400` for business logic errors

### 4. **General API Testing**

#### **Invalid Endpoints**
- [ ] **Non-existent endpoint**: `GET /api/v1/nonexistent`
- [ ] **Wrong HTTP method**: `GET /api/v1/auth/login` (should be POST)

#### **Malformed Requests**
- [ ] **Invalid JSON**: Send malformed JSON in request body
- [ ] **Wrong Content-Type**: Send JSON with `Content-Type: text/plain`
- [ ] **Empty request body**: Send empty body for endpoints expecting data
- [ ] **Extra fields**: Send unexpected fields in request body

#### **Missing Fields & Null Values Testing**
- [ ] **Partial data**: Send requests with only some required fields
- [ ] **Null values**: Send null for required string fields
- [ ] **Empty objects**: Send `{}` for endpoints requiring data
- [ ] **Mixed missing/null**: Combine missing fields with null values

#### **Rate Limiting (if implemented)**
- [ ] **Too many requests**: Send rapid requests to same endpoint
- [ ] **Concurrent requests**: Send multiple requests simultaneously

## 🎯 Test Execution Checklist

### **Pre-Test Setup**
- [ ] Ensure test database is clean
- [ ] Have valid test user accounts ready
- [ ] Have valid tokens ready for authenticated endpoints
- [ ] Document expected response codes and messages

### **Test Execution**
- [ ] Run each negative test scenario
- [ ] Verify correct HTTP status codes
- [ ] Verify appropriate error messages
- [ ] Check response format consistency
- [ ] Document any unexpected behavior

### **Post-Test Analysis**
- [ ] Review all test results
- [ ] Identify any security vulnerabilities
- [ ] Check for information disclosure in error messages
- [ ] Verify error handling doesn't crash the application

## 📊 Expected Results Summary

| Test Category | Expected Status Codes | Key Validations |
|---------------|---------------------|-----------------|
| **Validation Errors** | `422` | Proper field validation |
| **Missing Fields** | `422` | Required field validation |
| **Null Values** | `422` | Type validation |
| **Authentication Errors** | `401` | Secure error messages |
| **Business Logic Errors** | `400` | Appropriate error details |
| **Not Found** | `404` | Clean 404 responses |
| **Server Errors** | `500` | Graceful error handling |

## 🔒 Security Considerations

### **Information Disclosure**
- [ ] Error messages should not reveal sensitive information
- [ ] Database errors should not expose internal structure
- [ ] Stack traces should not be exposed in production

### **Input Validation**
- [ ] All inputs should be properly validated
- [ ] SQL injection attempts should be blocked
- [ ] XSS attempts should be sanitized
- [ ] Missing fields should be handled gracefully
- [ ] Null values should be rejected appropriately

### **Authentication Security**
- [ ] Invalid credentials should not reveal user existence
- [ ] Token validation should be strict
- [ ] Rate limiting should prevent brute force attacks

## 📝 Test Report Template

```
## Negative Test Results

### Endpoint: [ENDPOINT_NAME]
- **Test Case**: [DESCRIPTION]
- **Request**: [REQUEST_DETAILS]
- **Expected**: [EXPECTED_RESPONSE]
- **Actual**: [ACTUAL_RESPONSE]
- **Status**: ✅ PASS / ❌ FAIL
- **Notes**: [ADDITIONAL_NOTES]
```

## 🚀 Ready for QA Testing

All endpoints have comprehensive error handling and validation. The API should handle negative test scenarios gracefully and securely. Good luck with the testing! 🎉 