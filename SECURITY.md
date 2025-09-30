# Security Policy

## Supported Versions

We actively support the following versions of the PropellerAds Python SDK:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in the PropellerAds Python SDK, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@propellerads.com**

Include the following information in your report:
- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: Within 48 hours of receiving your report
- **Status Update**: Within 7 days with a more detailed response
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### What to Expect

1. **Acknowledgment**: We'll acknowledge receipt of your vulnerability report
2. **Investigation**: We'll investigate and validate the reported vulnerability
3. **Fix Development**: We'll develop and test a fix for the vulnerability
4. **Disclosure**: We'll coordinate disclosure of the vulnerability with you
5. **Credit**: We'll credit you for the discovery (unless you prefer to remain anonymous)

## Security Best Practices

When using the PropellerAds Python SDK:

### API Key Security
- **Never commit API keys** to version control
- Store API keys in environment variables or secure configuration files
- Use different API keys for different environments (dev, staging, production)
- Rotate API keys regularly

### Network Security
- Always use HTTPS endpoints (default in the SDK)
- Implement proper certificate validation
- Use rate limiting to prevent abuse
- Monitor API usage for unusual patterns

### Data Protection
- Validate all input data before sending to the API
- Sanitize any user-provided data
- Implement proper error handling to avoid information leakage
- Log security events appropriately

### Code Security
```python
# Good: Using environment variables
import os
from propellerads import EnhancedPropellerAdsClient

api_key = os.environ.get('PROPELLERADS_API_KEY')
if not api_key:
    raise ValueError("API key not found in environment variables")

client = EnhancedPropellerAdsClient(api_key)

# Bad: Hardcoded API key
# client = EnhancedPropellerAdsClient('your-api-key-here')  # DON'T DO THIS
```

### Dependency Security
- Keep the SDK and its dependencies updated
- Regularly audit dependencies for known vulnerabilities
- Use tools like `pip-audit` or `safety` to check for security issues

## Security Features

The PropellerAds Python SDK includes several security features:

- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Request Validation**: Input validation using Pydantic schemas
- **Secure Defaults**: HTTPS-only communication by default
- **Error Handling**: Secure error handling that doesn't leak sensitive information
- **Logging**: Security-conscious logging that doesn't expose sensitive data

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Private Disclosure**: Security issues are first reported privately
2. **Investigation**: We investigate and develop fixes
3. **Coordinated Disclosure**: We coordinate public disclosure with the reporter
4. **Public Disclosure**: After fixes are available, we may publish security advisories

## Contact

For security-related questions or concerns:
- **Email**: security@propellerads.com
- **General Support**: support@propellerads.com

## Acknowledgments

We thank the security research community for helping keep the PropellerAds Python SDK secure. Security researchers who responsibly disclose vulnerabilities will be acknowledged in our security advisories (unless they prefer to remain anonymous).
