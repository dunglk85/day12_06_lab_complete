# Deployment Information

## Public URL
https://ai-agent-production-8kv9.onrender.com

## Platform
Render

## Test Commands

### Health Check
```bash
curl https://ai-agent-production-8kv9.onrender.com/health
# Expected: {"status": "ok", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://ai-agent-production-8kv9.onrender.com/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- PORT: 8000
- REDIS_URL: redis://...
- AGENT_API_KEY: dev-key-change-me-in-production
- ENVIRONMENT: production
- DEBUG: false

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
