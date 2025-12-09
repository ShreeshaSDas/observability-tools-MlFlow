# LiteLLM Quick Reference - In-Memory Mode

## ⚠️ Important: You're Running in In-Memory Mode

Your LiteLLM setup does NOT use a database. This means certain endpoints (like `/sso/key/generate`) won't work because they require database mode.

**This is normal and expected!**

## ✅ What You CAN Use

### 1. API Endpoints (The Main Use Case)

#### Chat Completions
```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

#### Health Check
```bash
curl http://localhost:4000/health
```

### 2. Web Interfaces

| URL | Purpose | Works in In-Memory Mode? |
|-----|---------|-------------------------|
| http://localhost:4000/docs | Swagger API Documentation | ✅ Yes |
| http://localhost:4000/ui | LiteLLM UI (Models page) | ✅ Yes (limited) |
| http://localhost:4000/health | Health check | ✅ Yes |
| http://localhost:4000/sso/key/generate | Generate API keys | ❌ No (requires database) |

### 3. Your Authentication Key

You already have your master key configured:
```
LITELLM_MASTER_KEY="sk-1234"
```

**Use this key for all API calls!** You don't need to generate additional keys.

## ❌ What You CANNOT Use (Database Mode Only)

These features require `DATABASE_URL` to be set:

- ❌ `/sso/key/generate` - Generate API keys
- ❌ `/user/new` - Create users
- ❌ `/key/generate` - Generate team keys
- ❌ Dynamic model management via UI
- ❌ User management features

**You don't need these for basic LiteLLM usage!**

## 🎯 Recommended Workflow

### For API Calls (Python)

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-1234",  # Your LITELLM_MASTER_KEY
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### For API Calls (curl)

```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [{"role": "user", "content": "Your question here"}]
  }'
```

### For Viewing Traces

Use MLflow UI instead:
```
http://localhost:5001
```

Click "Traces" in the left sidebar to see all your API calls.

## 🔧 If You Really Need Database Mode

If you absolutely need the `/sso/key/generate` endpoint and other database features:

1. **Stop services**:
   ```bash
   ./stop.sh
   ```

2. **Update `.env`**:
   ```bash
   DATABASE_URL="postgresql://litellm:litellm_password@localhost:5433/litellm"
   STORE_MODEL_IN_DB="True"
   ```

3. **Run migrations**:
   ```bash
   # You'll need to set up LiteLLM's database schema
   # This is more complex and not recommended for simple use cases
   ```

4. **Restart**:
   ```bash
   ./start.sh
   ```

**But honestly, you don't need this!** The in-memory mode is simpler and works great for most use cases.

## 📝 Summary

- ✅ Use `sk-1234` as your API key
- ✅ Make API calls to http://localhost:4000/chat/completions
- ✅ View traces at http://localhost:5001
- ✅ Check API docs at http://localhost:4000/docs
- ❌ Don't try to use `/sso/key/generate` (requires database mode)
- ❌ Don't worry about the "Missing DATABASE_URL" message (it's just info)

## 🎉 You're All Set!

Your LiteLLM is working correctly. Just use the master key `sk-1234` for all your API calls!
