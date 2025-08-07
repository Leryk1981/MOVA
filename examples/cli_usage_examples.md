# MOVA CLI Usage Examples
# Приклади використання MOVA CLI

## Basic Usage / Базове використання

### Parse and validate MOVA file
```bash
# Parse JSON file
mova parse examples/basic_example.json

# Parse YAML file with validation
mova parse examples/config.yaml --validate

# Parse and export to different format
mova parse examples/basic_example.json --output examples/output.yaml
```

### Run MOVA protocols
```bash
# Basic run
mova run examples/basic_example.json

# Run with Redis and LLM
mova run examples/basic_example.json \
  --redis-url redis://localhost:6379 \
  --llm-api-key your-api-key \
  --llm-model openai/gpt-4

# Run with all integrations enabled
mova run examples/basic_example.json \
  --redis-url redis://localhost:6379 \
  --llm-api-key your-api-key \
  --webhook-enabled \
  --cache-enabled \
  --ml-enabled

# Run step by step
mova run examples/basic_example.json --step-by-step --verbose
```

### Validate MOVA files
```bash
# Basic validation
mova validate examples/basic_example.json

# Advanced validation with detailed report
mova validate examples/basic_example.json --advanced --detailed

# Save validation report
mova validate examples/basic_example.json --advanced --output validation_report.json
```

## Redis Management / Керування Redis

### View Redis sessions
```bash
# List all sessions
mova redis-sessions --redis-url redis://localhost:6379

# Show specific session
mova redis-sessions --redis-url redis://localhost:6379 --session-id my_session_123

# List sessions with custom pattern
mova redis-sessions --redis-url redis://localhost:6379 --pattern "mova:session:test*"
```

### Clear Redis sessions
```bash
# Clear all sessions (with confirmation)
mova redis-clear --redis-url redis://localhost:6379

# Delete specific session
mova redis-clear --redis-url redis://localhost:6379 --session-id my_session_123

# Clear without confirmation
mova redis-clear --redis-url redis://localhost:6379 --confirm
```

## Cache Management / Керування кешем

### View cache information
```bash
# Show cache statistics
mova cache-info --stats

# Show specific cache entry
mova cache-info --key "my_cache_key"
```

### Clear cache
```bash
# Clear all cache (with confirmation)
mova cache-clear

# Delete specific cache entry
mova cache-clear --key "my_cache_key"

# Clear without confirmation
mova cache-clear --confirm
```

## Webhook Management / Керування Webhook

### Test webhook endpoints
```bash
# Test validation event
mova webhook-test \
  --url "https://your-webhook-url.com/events" \
  --event-type "validation_started" \
  --data '{"protocol": "test_protocol", "session_id": "test_session"}'

# Test ML event
mova webhook-test \
  --url "https://your-webhook-url.com/events" \
  --event-type "ml_prediction_made" \
  --data '{"model_id": "intent_classifier", "confidence": 0.95}'

# Available event types:
# - validation_started, validation_completed, validation_failed
# - cache_updated, cache_cleared
# - redis_connected, redis_disconnected
# - llm_request_started, llm_request_completed, llm_request_failed
# - ml_intent_recognized, ml_entity_extracted, ml_prediction_made
```

### Check webhook status
```bash
mova webhook-status
```

## ML Integration / ML Інтеграція

### View ML models
```bash
# List all available models
mova ml-models --list-models

# Show specific model info
mova ml-models --model-id "intent_classifier"
```

### Evaluate ML models
```bash
# Evaluate model with test data
mova ml-evaluate \
  --model-id "intent_classifier" \
  --test-data test_data.json \
  --output evaluation_results.json
```

### Check ML system status
```bash
mova ml-status
```

## AI Analysis and Recommendations / AI Аналіз та рекомендації

### Analyze MOVA file
```bash
# Basic analysis
mova analyze examples/basic_example.json

# Detailed analysis with verbose output
mova analyze examples/basic_example.json --verbose

# Save recommendations to file
mova analyze examples/basic_example.json --output recommendations.json
```

### Diagnose errors
```bash
# Diagnose error and get recommendations
mova diagnose "Protocol execution failed: Invalid API endpoint" --verbose

# Save diagnosis results
mova diagnose "Connection timeout" --output diagnosis.json
```

### Get recommendations summary
```bash
# Show recommendations summary
mova recommendations-summary

# Save summary to file
mova recommendations-summary --output summary.json
```

## Testing / Тестування

### Test MOVA components
```bash
# Test all components
mova test examples/basic_example.json --verbose

# Test specific step
mova test examples/basic_example.json --step-id "step_1" --verbose

# Test specific API
mova test examples/basic_example.json --api-id "api_1" --verbose

# Dry run (show what would be executed)
mova test examples/basic_example.json --dry-run
```

## Async CLI Usage / Використання Async CLI

All the same commands are available in async CLI with `async-mova`:

```bash
# Async run with all integrations
async-mova run examples/basic_example.json \
  --redis-url redis://localhost:6379 \
  --llm-api-key your-api-key \
  --webhook-enabled \
  --cache-enabled \
  --ml-enabled \
  --verbose

# Async Redis management
async-mova redis-sessions --redis-url redis://localhost:6379

# Async ML evaluation
async-mova ml-evaluate --model-id "intent_classifier" --test-data test_data.json
```

## Configuration Examples / Приклади конфігурації

### Environment variables
```bash
export MOVA_REDIS_URL="redis://localhost:6379"
export MOVA_LLM_API_KEY="your-api-key"
export MOVA_LLM_MODEL="openai/gpt-4"
export MOVA_WEBHOOK_ENABLED="true"
export MOVA_CACHE_ENABLED="true"
export MOVA_ML_ENABLED="true"
```

### Configuration file
Create `mova_config.json`:
```json
{
  "redis_url": "redis://localhost:6379",
  "llm_api_key": "your-api-key",
  "llm_model": "openai/gpt-4",
  "webhook_enabled": true,
  "cache_enabled": true,
  "ml_enabled": true,
  "cache_ttl": 3600,
  "llm_temperature": 0.7,
  "llm_max_tokens": 1000
}
```

## Integration Workflow / Робочий процес інтеграції

### Complete workflow example
```bash
# 1. Parse and validate
mova parse my_protocol.json --validate

# 2. Run with all integrations
mova run my_protocol.json \
  --redis-url redis://localhost:6379 \
  --llm-api-key your-api-key \
  --webhook-enabled \
  --cache-enabled \
  --ml-enabled \
  --verbose

# 3. Analyze results
mova analyze my_protocol.json --output analysis.json

# 4. Check system status
mova redis-sessions --redis-url redis://localhost:6379
mova cache-info --stats
mova webhook-status
mova ml-status

# 5. Get recommendations
mova recommendations-summary --output summary.json
```

This workflow demonstrates the full integration capabilities of MOVA CLI with Redis, caching, webhooks, and ML components. 