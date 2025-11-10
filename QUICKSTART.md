# Quick Start Guide

Get up and running with the AliExpress AI scraper in 2 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenRouter API key (free to get!)
- Internet connection

## Installation (2 steps)

### 1. Get your API key

Visit [https://openrouter.ai/keys](https://openrouter.ai/keys) and create a free account to get your API key.

### 2. Set your API key

**Linux/macOS:**
```bash
export OPENROUTER_API_KEY='sk-or-v1-...'
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY='sk-or-v1-...'
```

**Windows (CMD):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-...
```

## First Run

Try scraping your first product:

```bash
python run.py "RGB FAN 120MM X3"
```

**First run will:**
1. Auto-install all dependencies (takes 1-2 minutes)
2. Download browser automation tools
3. Search AliExpress
4. Use AI to select best product
5. Generate SEO content
6. Save results to `product_result.json`

**Subsequent runs:**
- Much faster (dependencies already installed)
- Only takes 1-3 minutes per product search

## Expected Output

```
============================================================
  AliExpress AI Scraper - Auto Launcher
  Powered by OpenRouter (Gemini 2.0 Flash)
============================================================

🔍 Checking dependencies...

✅ All dependencies already installed!

🚀 Starting scraper...
   Product: RGB FAN 120MM X3
   Output: product_result.json

2025-11-08 10:30:15 - INFO - Starting search for: RGB FAN 120MM X3
2025-11-08 10:30:45 - INFO - Successfully scraped 12 products
2025-11-08 10:30:50 - INFO - Gemini selected product index: 3
2025-11-08 10:31:00 - INFO - Extracted 5 image URLs

============================================================
✅ SUCCESS! Product scraped and analyzed
============================================================

Title: RGB LED PC Cooling Fan 120mm 3-Pack with Controller - Gaming Fans
Price: $24.99

Description:
[AI-generated SEO-optimized description]

Images (5):
  1. https://ae01.alicdn.com/...
  2. https://ae01.alicdn.com/...
  ...

📄 Full results saved to: product_result.json
```

## View Results

```bash
cat product_result.json
```

Or open it in your text editor.

## Common Commands

### Basic search
```bash
python run.py "Gaming Mouse"
```

### Custom output file
```bash
python run.py "USB Cable" my_product.json
```

### Search with spaces
```bash
python run.py "Mechanical Keyboard RGB"
```

## Common Issues

### "OPENROUTER_API_KEY not set"

**Solution:** Set your API key (see step 2 above).

### Dependencies fail to install

**Solution:** Try manual install:
```bash
pip install browser-use openai langchain-openai playwright
python -m playwright install chromium
```

### "No module named 'scraper'"

**Solution:** Make sure you're in the correct directory:
```bash
cd Aliexpress-scraper
python run.py "product name"
```

### Slow first run

**Normal behavior:** First run takes 2-3 minutes to install dependencies.
Subsequent runs are much faster (1-2 minutes).

## Next Steps

- Check [README.md](README.md) for advanced features
- Customize AI model selection in `scraper.py`
- Integrate into your application
- Run `python verify_setup.py` for detailed diagnostics

## Tips

1. **Be specific with search terms:** "RGB 120mm Fan 3-pack" is better than "fan"
2. **Check costs:** OpenRouter is very affordable (~$0.001 per search)
3. **Monitor rate limits:** Add delays if scraping many products
4. **Save on API calls:** Results are cached in JSON files

## Cost Information

Using Gemini 2.0 Flash via OpenRouter:

- **Per search:** ~$0.001-0.003 USD
- **10 searches:** ~$0.01-0.03 USD
- **100 searches:** ~$0.10-0.30 USD

Get $5 free credits when you sign up at [OpenRouter](https://openrouter.ai/)!

## Example Workflow

```bash
# 1. Set API key (one time)
export OPENROUTER_API_KEY='your-key-here'

# 2. First product (will auto-install)
python run.py "USB Cable"

# 3. Check results
cat product_result.json

# 4. Search more products (faster now)
python run.py "Gaming Keyboard" keyboard.json
python run.py "Webcam 1080p" webcam.json
```

## Verification

Want to check if everything is set up correctly?

```bash
python verify_setup.py
```

This will check:
- Python version
- Dependencies
- API key
- Browser installation
- API connection

## Advanced Usage

For more control, use the scraper directly:

```bash
python scraper.py "Product Name" output.json
```

Or import it in your Python code:

```python
from scraper import AliExpressScraper
import asyncio

async def main():
    scraper = AliExpressScraper()
    result = await scraper.scrape_product("RGB Fan", "output.json")
    print(result.title)

asyncio.run(main())
```

## Getting Help

- Read the full [README.md](README.md)
- Check troubleshooting section
- Run `python verify_setup.py`
- Review example_usage.py

Happy scraping! 🚀

---

**Quick Links:**
- [OpenRouter Dashboard](https://openrouter.ai/keys)
- [OpenRouter Pricing](https://openrouter.ai/docs/pricing)
- [Full Documentation](README.md)
