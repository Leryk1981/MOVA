# Webhook Support in MOVA SDK

## Overview

MOVA SDK provides comprehensive webhook support for external integrations, allowing you to receive real-time notifications about various events that occur within the SDK. This enables seamless integration with external systems, monitoring tools, and notification services.

## Features

- **Secure Signature Verification**: HMAC-SHA256/SHA1 signature validation
- **Multiple Event Types**: Support for validation, cache, Redis, LLM, and error events
- **Configurable Endpoints**: Multiple webhook endpoints with custom settings
- **Retry Logic**: Automatic retry with exponential backoff
- **Async Support**: Full async/await support for high performance
- **Event Filtering**: Subscribe to specific event types
- **Error Handling**: Comprehensive error handling and logging

## Event Types

### Validation Events
- `validation.started` - Validation process started
- `validation.completed` - Validation process completed successfully
- `validation.failed` - Validation process failed

### Cache Events
- `cache.updated` - Cache entry updated
- `cache.cleared` - Cache cleared

### Redis Events
- `redis.connected` - Redis connection established
- `redis.disconnected` - Redis connection lost

### LLM Events
- `llm.request.started` - LLM request started
- `llm.request.completed` - LLM request completed successfully
- `llm.request.failed` - LLM request failed

### System Events
- `config.updated` - Configuration updated
- `error.occurred` - Error occurred

## Quick Start

### 1. Basic Webhook Setup

```python
from src.mova.webhook import WebhookEndpoint, add_webhook_endpoint

# Create webhook endpoint
endpoint = WebhookEndpoint(
    url="https://your-webhook-url.com/webhook",
    secret="your-webhook-secret",
    timeout=30,
    retries=3
)

# Add endpoint to webhook manager
add_webhook_endpoint(endpoint)
```

### 2. Trigger Events

```python
from src.mova.webhook_integration import (
    trigger_validation_started,
    trigger_validation_completed,
    trigger_cache_updated
)

# Trigger validation events
trigger_validation_started({
    "schema": "user_schema",
    "data_size": 1024
})

trigger_validation_completed({
    "schema": "user_schema",
    "valid": True,
    "errors": []
})

# Trigger cache events
trigger_cache_updated({
    "key": "user_data_123",
    "size": 512
})
```

### 3. Receive Webhooks

```python
from src.mova.webhook import WebhookReceiver
import asyncio

# Create webhook receiver
receiver = WebhookReceiver(secret="your-webhook-secret")

# Define event handlers
def handle_validation_event(data):
    print(f"Validation event: {data}")

def handle_cache_event(data):
    print(f"Cache event: {data}")

# Add handlers
receiver.add_handler("validation.started", handle_validation_event)
receiver.add_handler("cache.updated", handle_cache_event)

# Handle incoming webhook (in your web framework)
async def handle_webhook_request(payload, signature):
    success = await receiver.handle_webhook(
        payload=payload,
        signature=signature
    )
    return success
```

## Configuration

### Environment Variables

```bash
# Enable/disable webhooks
MOVA_WEBHOOK_ENABLED=true

# Webhook timeout (seconds)
MOVA_WEBHOOK_TIMEOUT=30

# Webhook max retries
MOVA_WEBHOOK_MAX_RETRIES=3

# Default webhook secret
MOVA_WEBHOOK_SECRET=your-default-secret
```

### Configuration File

```yaml
# config.yaml
webhook:
  enabled: true
  timeout: 30
  max_retries: 3
  secret: your-webhook-secret
```

## Advanced Usage

### Multiple Endpoints

```python
from src.mova.webhook import WebhookEndpoint, add_webhook_endpoint

# Add multiple endpoints
endpoints = [
    WebhookEndpoint(
        url="https://monitoring.example.com/webhook",
        secret="monitoring-secret",
        event_types=["validation.started", "validation.completed", "error.occurred"]
    ),
    WebhookEndpoint(
        url="https://logging.example.com/webhook",
        secret="logging-secret",
        event_types=["cache.updated", "redis.connected", "redis.disconnected"]
    )
]

for endpoint in endpoints:
    add_webhook_endpoint(endpoint)
```

### Custom Event Handlers

```python
from src.mova.webhook import get_webhook_manager, WebhookEventType

manager = get_webhook_manager()

def custom_handler(payload):
    print(f"Custom handler: {payload.event_type} - {payload.data}")

# Add custom handler for specific event
manager.add_event_handler(WebhookEventType.VALIDATION_STARTED, custom_handler)
```

### Error Handling

```python
from src.mova.webhook_integration import trigger_error_occurred

try:
    # Your code that might raise an exception
    result = some_operation()
except Exception as e:
    # Trigger error event
    trigger_error_occurred(e, {
        "component": "validator",
        "operation": "validate_schema",
        "user_id": "12345"
    })
```

## Webhook Payload Structure

All webhook payloads follow this structure:

```json
{
    "event_type": "validation.started",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "schema": "user_schema",
        "data_size": 1024
    },
    "source": "mova_sdk",
    "version": "2.2"
}
```

### Headers

Webhook requests include the following headers:

- `Content-Type: application/json`
- `X-Mova-Signature: <hmac-signature>`
- `X-Mova-Event: <event-type>`
- `X-Mova-Timestamp: <unix-timestamp>`
- `User-Agent: MOVA-SDK/2.2`

## Security

### Signature Verification

Webhook signatures are generated using HMAC-SHA256:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Best Practices

1. **Use Strong Secrets**: Generate cryptographically secure secrets
2. **Verify Signatures**: Always verify webhook signatures
3. **Use HTTPS**: Only send webhooks to HTTPS endpoints
4. **Rate Limiting**: Implement rate limiting on your webhook endpoints
5. **Idempotency**: Make webhook handlers idempotent

## Testing

### Local Testing

```python
# Test webhook locally
from src.mova.webhook import WebhookReceiver
import json

receiver = WebhookReceiver(secret="test-secret")

# Simulate webhook
payload = json.dumps({
    "event_type": "validation.started",
    "data": {"test": "data"}
})

signature = receiver.generate_signature(payload, receiver.secret)
success = await receiver.handle_webhook(payload, signature)
```

### Using Webhook Testing Services

1. **Webhook.site**: Use for testing webhook delivery
2. **ngrok**: Expose local server for testing
3. **Postman**: Test webhook endpoints

## Integration Examples

### Flask Integration

```python
from flask import Flask, request
from src.mova.webhook import WebhookReceiver

app = Flask(__name__)
receiver = WebhookReceiver(secret="your-secret")

@app.route('/webhook', methods=['POST'])
async def webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('X-Mova-Signature')
    
    success = await receiver.handle_webhook(payload, signature)
    
    if success:
        return {'status': 'success'}, 200
    else:
        return {'status': 'error'}, 400
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException
from src.mova.webhook import WebhookReceiver

app = FastAPI()
receiver = WebhookReceiver(secret="your-secret")

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Mova-Signature")
    
    success = await receiver.handle_webhook(
        payload.decode(),
        signature
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    return {"status": "success"}
```

## Troubleshooting

### Common Issues

1. **Webhook Not Received**
   - Check endpoint URL is accessible
   - Verify webhook is enabled
   - Check network connectivity

2. **Invalid Signature**
   - Verify secret matches between sender and receiver
   - Check signature algorithm (SHA256/SHA1)
   - Ensure payload hasn't been modified

3. **Timeout Errors**
   - Increase timeout setting
   - Check endpoint response time
   - Verify endpoint is not blocking

4. **Retry Failures**
   - Check endpoint availability
   - Verify endpoint returns 2xx status codes
   - Review endpoint logs

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('src.mova.webhook').setLevel(logging.DEBUG)
```

## Performance Considerations

1. **Async Processing**: Webhook sending is async by default
2. **Connection Pooling**: aiohttp handles connection pooling
3. **Batch Processing**: Consider batching multiple events
4. **Rate Limiting**: Implement rate limiting for high-volume scenarios

## Migration Guide

### From v1.x to v2.x

1. Update import statements
2. Use new WebhookEventType enum
3. Update payload structure
4. Review signature verification

## API Reference

### WebhookEndpoint

```python
class WebhookEndpoint:
    def __init__(
        self,
        url: str,
        secret: str,
        headers: Dict[str, str] = None,
        timeout: int = 30,
        retries: int = 3,
        enabled: bool = True,
        event_types: List[WebhookEventType] = None
    )
```

### WebhookManager

```python
class WebhookManager:
    def add_endpoint(self, endpoint: WebhookEndpoint) -> None
    def remove_endpoint(self, url: str) -> bool
    def add_event_handler(self, event_type: WebhookEventType, handler: Callable) -> None
    def trigger_event(self, event_type: WebhookEventType, data: Dict[str, Any] = None) -> None
    def is_enabled(self) -> bool
    def set_enabled(self, enabled: bool) -> None
```

### WebhookReceiver

```python
class WebhookReceiver:
    def __init__(self, secret: str)
    def add_handler(self, event_type: str, handler: Callable) -> None
    def verify_signature(self, payload: str, signature: str) -> bool
    async def handle_webhook(self, payload: str, signature: str, event_type: str = None) -> bool
```

## Contributing

When contributing to webhook functionality:

1. Follow existing code style
2. Add comprehensive tests
3. Update documentation
4. Consider backward compatibility
5. Test with real webhook endpoints

## License

This webhook functionality is part of MOVA SDK and follows the same license terms. 