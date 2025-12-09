# Accessing LiteLLM Dashboard - Your Options

## Current Situation

The LiteLLM **interactive dashboard** (UI for managing keys, users, models) **requires database mode**. 

When running in in-memory mode, the dashboard redirects to the setup page.

![LiteLLM Setup Page](file:///Users/shreesha.dasthoughtworks.com/.gemini/antigravity/brain/54a8f780-19ad-4e89-98c1-33f73ed88a3c/litellm_setup_page_1765103076798.png)

## ✅ Option 1: Use What's Available Now (Recommended)

You have several interfaces available in in-memory mode:

### 1. Swagger API Documentation
**URL**: http://localhost:4000/docs

This provides:
- Interactive API testing
- All available endpoints
- Request/response examples
- Try out API calls directly in the browser

### 2. MLflow Dashboard  
**URL**: http://localhost:5001

This provides:
- View all API call traces
- Request/response details
- Performance metrics
- Token usage statistics
- Error tracking

### 3. Direct API Access
Use curl or Python to interact with LiteLLM:

```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-2.0-flash", "messages": [{"role": "user", "content": "Hello"}]}'
```

## 🔧 Option 2: Enable Database Mode (For Full Dashboard)

If you really want the full LiteLLM dashboard with UI for key/user management:

### Step 1: Update Configuration

Edit `.env`:
```bash
# Add these lines
DATABASE_URL="postgresql://litellm:litellm_password@localhost:5433/litellm"
STORE_MODEL_IN_DB="True"
```

### Step 2: Initialize Database

```bash
# Stop services
./stop.sh

# Run LiteLLM database migrations
docker exec -i litellm_postgres psql -U litellm -d litellm << 'EOF'
-- LiteLLM will create tables on first startup
EOF
```

### Step 3: Update start.sh

Remove the `unset DATABASE_URL` lines from `start.sh` and `start_litellm_clean.sh`.

### Step 4: Restart

```bash
./start.sh
```

### What You'll Get

With database mode enabled:
- ✅ Full LiteLLM dashboard UI
- ✅ User management
- ✅ API key generation
- ✅ Team management
- ✅ Dynamic model configuration via UI
- ✅ Usage tracking per key

### Trade-offs

**Pros:**
- Full-featured dashboard
- Multi-user support
- Fine-grained access control

**Cons:**
- More complex setup
- Requires database maintenance
- Models stored in DB instead of config.yaml
- More moving parts

## 📊 Comparison

| Feature | In-Memory Mode | Database Mode |
|---------|----------------|---------------|
| API Access | ✅ | ✅ |
| Swagger Docs | ✅ | ✅ |
| MLflow Traces | ✅ | ✅ |
| Dashboard UI | ❌ | ✅ |
| User Management | ❌ | ✅ |
| Key Generation | ❌ | ✅ |
| Setup Complexity | Simple | Complex |
| Best For | Development, Simple deployments | Production, Multi-user |

## 🎯 My Recommendation

**For your use case, stick with Option 1:**

1. Use **Swagger docs** (http://localhost:4000/docs) for API exploration
2. Use **MLflow** (http://localhost:5001) for viewing traces and monitoring
3. Use **direct API calls** for actual usage

This gives you everything you need without the complexity of database mode.

## 🚀 Quick Links

- **Swagger API Docs**: http://localhost:4000/docs
- **MLflow Dashboard**: http://localhost:5001
- **Health Check**: http://localhost:4000/health

Try opening http://localhost:4000/docs in your browser right now!
