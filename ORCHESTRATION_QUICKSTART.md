# Master AI Orchestration System - Quick Start Guide

Get your AI orchestration system up and running in 5 minutes!

## Prerequisites

- Python 3.11 or later
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- Google AI API key ([Get one here](https://makersuite.google.com/app/apikey)) - Optional, for image/video generation

## Quick Start (Linux/Mac)

```bash
# 1. Clone or navigate to the repository
cd Aliexpress-scraper

# 2. Run the startup script
./start_orchestration.sh
```

That's it! The server will start on `http://localhost:8000`

## Quick Start (Windows)

```cmd
# 1. Navigate to the repository
cd Aliexpress-scraper

# 2. Run the startup script
start_orchestration.bat
```

## First API Call

Once the server is running, open a new terminal and try:

```bash
# Test with curl
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the benefits of renewable energy?"}'
```

Or use Python:

```python
import httpx

response = httpx.post("http://localhost:8000/chat", json={
    "message": "What are the benefits of renewable energy?"
})

print(response.json())
```

## Interactive Testing

Run the test client for an interactive experience:

```bash
python test_client.py
```

Select option 7 for interactive chat mode!

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Common Examples

### 1. Simple Question (Category M)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing in simple terms"}'
```

### 2. Complex Task (Category H)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a marketing plan for an eco-friendly product"}'
```

### 3. Code Generation (Category L)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a Python function to calculate fibonacci numbers"}'
```

### 4. Execute Workflow Template
```bash
curl -X POST http://localhost:8000/template/research_report \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence", "audience": "business leaders"}'
```

### 5. Custom Workflow
```bash
curl -X POST http://localhost:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {
        "type": "inline",
        "tasks": [
          {
            "model": "thinking_ai",
            "prompt": "List 5 benefits of {topic}",
            "output_variable": "benefits",
            "config": {"temperature": 0.7}
          }
        ]
      }
    ],
    "variables": {"topic": "cloud computing"}
  }'
```

## Monitoring

Check system health:
```bash
curl http://localhost:8000/health
```

Get statistics:
```bash
curl http://localhost:8000/stats
```

List available models:
```bash
curl http://localhost:8000/models
```

## Deploy to Railway

1. **Create Railway Account**: Go to [railway.app](https://railway.app)

2. **New Project**: Click "New Project" → "Deploy from GitHub repo"

3. **Connect Repository**: Select your repository

4. **Automatic Detection**: Railway will automatically detect the configuration

5. **Environment Variables** (Optional): Add any custom environment variables

6. **Deploy**: Click "Deploy"

Your API will be live at: `https://your-project.railway.app`

## Configuration

All configuration is in `orchestration_config.json`. Key sections:

```json
{
  "api_keys": {
    "openrouter": "your-key-here",
    "google_ai": "your-key-here"
  },
  "orchestration": {
    "maxConcurrentWorkflows": 1000,
    "defaultTimeoutSeconds": 300
  },
  "ai_models": {
    // AI model configurations
  },
  "prompt_addons": {
    // 50 specialized prompt addons
  }
}
```

## Workflow Structure

Workflows use two types of queues:

### Linear (Parallel)
Tasks run simultaneously:
```json
{
  "type": "linear",
  "tasks": [
    {"model": "thinking_ai", "prompt": "Task 1", "output_variable": "result1"},
    {"model": "thinking_ai", "prompt": "Task 2", "output_variable": "result2"}
  ]
}
```

### Inline (Sequential)
Tasks run one after another:
```json
{
  "type": "inline",
  "tasks": [
    {"model": "thinking_ai", "prompt": "Step 1", "output_variable": "step1"},
    {"model": "thinking_ai", "prompt": "Step 2 using {step1}", "output_variable": "step2"}
  ]
}
```

## Prompt Addons

Enhance responses with specialized addons:

```json
{
  "model": "thinking_ai",
  "prompt": "Write a blog post about AI",
  "output_variable": "blog_post",
  "config": {
    "addons": ["blog_writing", "seo_optimization"]
  }
}
```

Available addons include:
- Content: `blog_writing`, `storytelling`, `case_study`
- Marketing: `email_campaigns`, `ad_copy`, `landing_page`
- Social: `instagram`, `linkedin`, `tiktok`, `twitter`
- Business: `business_proposal`, `swot_analysis`, `customer_persona`
- And 40+ more!

## Troubleshooting

### Port Already in Use
```bash
# Change port in api_server.py or set environment variable
export PORT=8080
python api_server.py
```

### API Key Errors
- Check your API keys in `orchestration_config.json`
- Ensure keys are valid and have sufficient credits

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Read Full Documentation**: See `ORCHESTRATION_README.md`
2. **Explore Templates**: Check out workflow templates in the config
3. **Create Custom Workflows**: Build your own multi-step AI workflows
4. **Add Prompt Addons**: Enhance outputs with specialized instructions
5. **Monitor Performance**: Use the stats endpoint to track usage

## Support

- **Documentation**: `ORCHESTRATION_README.md`
- **Test Client**: `python test_client.py`
- **API Docs**: http://localhost:8000/docs

## Key Features to Try

✅ **Automatic Task Classification** - Send any request, get optimal routing
✅ **Parallel Processing** - Multiple AI tasks running simultaneously
✅ **Variable Passing** - Chain tasks together with data flow
✅ **50+ Prompt Addons** - Specialized enhancements for any task
✅ **Error Recovery** - Automatic retries and fallbacks
✅ **Cost Optimization** - 70-80% savings through smart routing

Happy Orchestrating! 🚀
