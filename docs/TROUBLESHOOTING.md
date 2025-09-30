# 🩺 Troubleshooting Guide

This guide provides solutions to common issues and explanations for error codes.

## Common Issues

### 1. `MainAPI` environment variable not set

**Error:** `MainAPI environment variable not set`

**Solution:** Make sure you have set your PropellerAds API key as an environment variable:

```bash
export MainAPI="your_propellerads_api_key"
```

### 2. `401 Unauthorized`

**Error:** `401 Unauthorized`

**Solution:** Your API key is incorrect. Please double-check your API key and make sure it is correct.

### 3. `429 Too Many Requests`

**Error:** `429 Too Many Requests`

**Solution:** You have exceeded the rate limit of the API. The client will automatically handle this by waiting for a short period of time before retrying the request. If you continue to see this error, you may need to reduce the number of requests you are making.

## Error Codes

| Code | Description | Solution |
|---|---|---|
| 400 | Bad Request | The request was malformed. Please check the API documentation for the correct request format. |
| 401 | Unauthorized | Your API key is incorrect. |
| 403 | Forbidden | You do not have permission to access this resource. |
| 404 | Not Found | The requested resource could not be found. |
| 429 | Too Many Requests | You have exceeded the rate limit of the API. |
| 500 | Internal Server Error | An error occurred on the server. Please try again later. |

