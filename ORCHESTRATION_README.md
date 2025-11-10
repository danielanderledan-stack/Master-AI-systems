# Master AI Orchestration System

A sophisticated AI orchestration system that intelligently coordinates specialized AI models to handle tasks of varying complexity through dynamic workflow generation.

## Overview

The Master AI Orchestration System revolutionizes how AI models work together by:

- **Intelligent Task Classification**: Automatically categorizes requests as Low (L), Medium (M), or High (H) complexity
- **Dynamic Workflow Generation**: Creates optimized workflows in JSON format for complex tasks
- **Multi-Model Coordination**: Orchestrates specialized AI models for optimal results
- **Cost Optimization**: Achieves 70-80% cost reduction by routing tasks to appropriate models
- **Resilient Operation**: Implements sophisticated error handling, retries, and fallbacks

## System Architecture

```
User Request
    ↓
Categorizer AI (meta-llama/llama-3.1-8b-instruct)
    ↓
┌─────────┬──────────┬─────────────┐
│    L    │    M     │      H      │
│         │          │             │
│ Thinking│ Medium   │  Thinking   │
│   AI    │   AI     │  AI + Fast  │
│         │          │  Response   │
└─────────┴──────────┴─────────────┘
                           ↓
                    Workflow Generation
                           ↓
                    ┌──────────────┐
                    │ Linear Queue │ (Parallel Tasks)
                    └──────────────┘
                           ↓
                    ┌──────────────┐
                    │ Inline Queue │ (Sequential Tasks)
                    └──────────────┘
                           ↓
                    Finished Task AI
```

## AI Models

### Core Models
- **Categorizer AI**: `meta-llama/llama-3.1-8b-instruct` - Task complexity classification
- **Fast AI**: `openai/gpt-oss-safeguard-20b` - Simple to medium queries
- **Medium AI**: `meta-llama/llama-3.3-70b-instruct` - More difficult queries
- **Thinking AI**: `moonshotai/kimi-k2-thinking` - Complex tasks and orchestration

### Specialized Models
- **Code AI**: `moonshotai/kimi-k2-thinking` - Programming and code generation
- **Image Analysis AI**: `google/gemini-2.5-pro` - Visual content evaluation
- **Imagen 4 Ultra**: High-quality image generation
- **Veo 3.1**: Video content generation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Aliexpress-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys in `orchestration_config.json`:
```json
{
  "api_keys": {
    "openrouter": "your-openrouter-key",
    "google_ai": "your-google-ai-key"
  }
}
```

## Usage

### Running Locally

Start the API server:
```bash
python api_server.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "message": "Create a marketing campaign for eco-friendly water bottles",
  "session_id": "optional-session-id",
  "context_tokens": 0
}
```

Response:
```json
{
  "session_id": "uuid-session-id",
  "response": "I'm going to create a comprehensive marketing campaign...",
  "timestamp": "2025-11-10T12:00:00",
  "category": "H"
}
```

#### 3. Execute Custom Workflow
```bash
POST /workflow
Content-Type: application/json

{
  "workflow": [
    {
      "type": "linear",
      "tasks": [
        {
          "model": "thinking_ai",
          "prompt": "Research {topic}",
          "output_variable": "research",
          "config": {
            "temperature": 0.7,
            "addons": ["research"]
          }
        }
      ]
    }
  ],
  "variables": {
    "topic": "renewable energy"
  }
}
```

#### 4. Use Workflow Template
```bash
POST /template/research_report
Content-Type: application/json

{
  "topic": "artificial intelligence",
  "audience": "business executives"
}
```

#### 5. List Available Models
```bash
GET /models
```

#### 6. List Prompt Addons
```bash
GET /addons
```

## Workflow Templates

### Research Report
Generates comprehensive research reports with:
- Primary and secondary research
- Company analysis
- Executive summary
- Future outlook

### Marketing Campaign
Creates complete marketing campaigns with:
- Creative concept development
- Social media copy (Instagram, Twitter, Facebook)
- Product imagery
- Video content
- Email templates

### Code Project
Develops software projects with:
- Architecture design
- Implementation
- Testing
- Documentation

## Prompt Addons

The system includes 50 specialized prompt addons for enhanced capabilities:

### Content Creation
- `blog_writing` - Compelling blog posts with SEO optimization
- `headline_optimization` - Attention-grabbing headlines
- `storytelling` - Narrative-driven content
- `case_study` - Professional case studies

### Marketing
- `email_campaigns` - Strategic email sequences
- `ad_copy` - High-converting advertisements
- `landing_page` - Optimized landing pages
- `value_proposition` - Clear value statements

### Social Media
- `instagram` - Instagram-optimized content
- `linkedin` - Professional LinkedIn posts
- `tiktok` - TikTok video scripts
- `twitter` - Concise Twitter threads

### Business
- `business_proposal` - Professional proposals
- `executive_presentation` - Executive-level presentations
- `swot_analysis` - Strategic SWOT analysis
- `customer_persona` - Detailed customer personas

And many more! See `orchestration_config.json` for the complete list.

## Request Flow

1. **User Opens Chatbox**: Warmup prompts sent to categorizer and fast AI
2. **User Sends Message**:
   - If contains image → use image model
   - If context > 100k tokens → force thinking AI
   - If context > 200k tokens → force Gemini 2.5 Pro
   - If tokens > 900k → deny request
   - Otherwise → categorize request

3. **Categorization**:
   - **L**: Direct to Thinking AI for tasks/hard questions
   - **M**: Route to Medium AI for difficult queries
   - **H**: Use Thinking AI with full orchestration

4. **High Complexity Flow (H)**:
   - Fast Response AI sends immediate acknowledgment
   - Master AI generates JSON workflow
   - System executes workflow (linear + inline queues)
   - Finished Task AI delivers results

## Queue System

### Linear Queue
Tasks on the same line run simultaneously (parallel execution):
```json
{
  "type": "linear",
  "tasks": [
    {"model": "research_ai", "prompt": "Task 1", "output_variable": "result1"},
    {"model": "product_ai", "prompt": "Task 2", "output_variable": "result2"}
  ]
}
```

### Inline Queue
Tasks run sequentially, one at a time:
```json
{
  "type": "inline",
  "tasks": [
    {"model": "thinking_ai", "prompt": "Step 1 using {result1}", "output_variable": "step1"},
    {"model": "thinking_ai", "prompt": "Step 2 using {step1}", "output_variable": "step2"}
  ]
}
```

## Variable System

Tasks can reference outputs from previous tasks using `{variable_name}`:

```json
{
  "workflow": [
    {
      "type": "inline",
      "tasks": [
        {
          "model": "thinking_ai",
          "prompt": "Research climate change",
          "output_variable": "research"
        }
      ]
    },
    {
      "type": "inline",
      "tasks": [
        {
          "model": "thinking_ai",
          "prompt": "Write an article about: {research}",
          "output_variable": "article"
        }
      ]
    }
  ]
}
```

## Error Handling

The system implements sophisticated error handling:

### Error Types
- **Transient**: Network issues, rate limits (automatic retry with exponential backoff)
- **Persistent**: API errors, auth failures (manual intervention)
- **Resource**: Memory limits, timeouts (scale or optimize)
- **Logical**: Invalid inputs (fallback alternatives)
- **Fatal**: Unrecoverable errors (circuit breaking)

### Retry Strategy
- Base delay: 1 second
- Max delay: 30 seconds
- Exponential backoff with jitter
- Maximum retries: 3-5 (depending on error type)

### Circuit Breaker
- Failure threshold: 5 failures
- Timeout: 60 seconds
- Automatic recovery with half-open state

## Deployment to Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Railway will automatically detect the configuration
4. Set environment variables (if needed)
5. Deploy!

The system uses:
- `Procfile` for process definition
- `railway.json` for Railway-specific configuration
- `runtime.txt` for Python version

## Configuration

All system configuration is in `orchestration_config.json`:

```json
{
  "system": {
    "name": "Master AI Orchestration System",
    "environment": "production",
    "logLevel": "INFO"
  },
  "orchestration": {
    "maxConcurrentWorkflows": 1000,
    "defaultTimeoutSeconds": 300,
    "maxRetries": 3
  },
  "queuing": {
    "highPriorityRatio": 0.6,
    "mediumPriorityRatio": 0.3,
    "lowPriorityRatio": 0.1
  }
}
```

## Cost Optimization

The system achieves 70-80% cost reduction through:

1. **Intelligent Routing**: Simple queries → smaller, cheaper models
2. **Parallel Processing**: Independent tasks run simultaneously
3. **Model Fallbacks**: Automatic switching on failures
4. **Rate Limiting**: Prevents quota exhaustion
5. **Caching**: Future enhancement for repeated requests

## Monitoring

Built-in monitoring includes:

- Request/response tracking
- Model performance metrics
- Error rate monitoring
- Cost tracking by model
- Queue depth monitoring

Access stats via:
```bash
GET /stats
```

## Examples

### Simple Query (Category M)
```python
import httpx

response = httpx.post("http://localhost:8000/chat", json={
    "message": "What are the benefits of renewable energy?"
})
print(response.json())
```

### Complex Task (Category H)
```python
response = httpx.post("http://localhost:8000/chat", json={
    "message": "Create a complete marketing campaign for eco-friendly water bottles including social media posts, product images, and a promotional video"
})
print(response.json())
```

### Custom Workflow
```python
workflow = {
    "workflow": [
        {
            "type": "linear",
            "tasks": [
                {
                    "model": "thinking_ai",
                    "prompt": "Research {topic}",
                    "output_variable": "research",
                    "config": {"temperature": 0.7, "addons": ["research"]}
                }
            ]
        }
    ],
    "variables": {"topic": "quantum computing"}
}

response = httpx.post("http://localhost:8000/workflow", json=workflow)
print(response.json())
```

## Troubleshooting

### Issue: Rate limit errors
**Solution**: The system implements automatic rate limiting. If you encounter rate limits, they'll be handled automatically with exponential backoff.

### Issue: Workflow execution fails
**Solution**: Check the AI Workers Failed AI response for details. The system provides clear error messages and retry suggestions.

### Issue: Slow response times
**Solution**: Complex workflows may take time. The Fast Response AI provides immediate acknowledgment while work proceeds in the background.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions, please open a GitHub issue.
