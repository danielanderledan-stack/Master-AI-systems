# AliExpress AI-Powered Product Scraper

Automate AliExpress product searching with AI-powered selection and SEO content generation using Browser Use and OpenRouter API (Gemini 2.0 Flash).

## Features

- **Automated Web Scraping**: Uses Browser Use library to navigate and scrape AliExpress
- **AI Product Selection**: Gemini 2.0 Flash analyzes products and selects the best option
- **SEO Content Generation**: Automatically generates optimized titles and descriptions
- **Image Extraction**: Extracts product images from the selected item
- **Single API Call**: Efficient design with one API call per search
- **Auto-Install**: Dependencies install automatically on first run
- **Simple Executable**: Just run `python run.py "product name"`

## Quick Start (3 Steps)

### 1. Get an OpenRouter API Key

Visit [https://openrouter.ai/keys](https://openrouter.ai/keys) and create a free account to get your API key.

### 2. Set your API key

**Linux/macOS:**
```bash
export OPENROUTER_API_KEY='your-key-here'
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY='your-key-here'
```

**Windows (CMD):**
```cmd
set OPENROUTER_API_KEY=your-key-here
```

### 3. Run the scraper

```bash
python run.py "RGB FAN 120MM X3"
```

That's it! Dependencies will install automatically on first run.

## Usage

### Basic Usage

```bash
python run.py "RGB FAN 120MM X3"
```

### Custom Output File

```bash
python run.py "Gaming Mouse" custom_output.json
```

### Advanced Usage (Direct Script)

If you prefer to use the scraper directly:

```bash
python scraper.py "Product Name" [output_file.json]
```

## Example Output

The script generates a JSON file (`product_result.json` by default) with this structure:

```json
{
  "title": "RGB LED Gaming Mouse - 7 Programmable Buttons, 6400 DPI, Ergonomic Design",
  "price": "$29.99",
  "description": "Elevate your gaming experience with our professional RGB gaming mouse...",
  "images": [
    "https://ae01.alicdn.com/image1.jpg",
    "https://ae01.alicdn.com/image2.jpg",
    "https://ae01.alicdn.com/image3.jpg"
  ]
}
```

## How It Works

1. **Search & Scrape**: Browser Use navigates to AliExpress and scrapes top 10-15 results
2. **Extract Data**: Collects title, price, rating, orders, and descriptions
3. **AI Selection**: Gemini 2.0 Flash analyzes all products and selects the best option
4. **Content Generation**: Same API call generates SEO-optimized title and description
5. **Image Extraction**: Browser Use extracts image URLs from the selected product
6. **Save Results**: Outputs structured JSON file

## Technical Details

### Architecture

- **Browser Automation**: Browser Use (Playwright-based)
- **AI Model**: Google Gemini 2.0 Flash via OpenRouter
- **API**: OpenRouter API (OpenAI-compatible)
- **API Efficiency**: Single API call for selection + content generation
- **Rate Limiting**: 2-3 second delays between actions

### Why OpenRouter + Gemini?

- **Cost-effective**: Gemini 2.0 Flash is very affordable
- **Fast**: Flash model provides quick responses
- **Reliable**: OpenRouter provides stable API access
- **Compatible**: Works with OpenAI API standards

## Manual Installation (Optional)

If you prefer manual installation:

### 1. Clone the repository

```bash
git clone <repository-url>
cd Aliexpress-scraper
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set API key

```bash
export OPENROUTER_API_KEY='your-key-here'
```

## Requirements

- Python 3.8+
- OPENROUTER_API_KEY environment variable
- Internet connection

Dependencies (auto-installed):
- browser-use >= 0.1.0
- openai >= 1.12.0
- langchain-openai >= 0.0.5
- playwright >= 1.40.0
- aiohttp >= 3.9.0
- beautifulsoup4 >= 4.12.0

## Configuration

### Scraper Settings

Edit `scraper.py` to customize:

```python
max_results = 12  # Number of products to scrape (10-15 recommended)
max_images = 5    # Number of images to extract
headless = True   # Set to False for debugging
```

### AI Model

The scraper uses `google/gemini-2.0-flash-001`. To change the model, edit `scraper.py`:

```python
self.model = "google/gemini-2.0-flash-001"  # Change this
```

Other OpenRouter models you can try:
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4-turbo`
- `meta-llama/llama-3.2-90b-vision-instruct`

## Troubleshooting

### "OPENROUTER_API_KEY environment variable not set"

**Solution:** Set your API key as shown in Quick Start step 2.

### Dependencies fail to install

**Solution:** Install manually:
```bash
pip install -r requirements.txt
playwright install chromium
```

### "No products found in search results"

**Possible causes:**
- AliExpress might be blocking automated requests
- Network connectivity issues
- Product search term too specific

**Solution:** Try a different search term or check your internet connection.

### Slow execution

**Normal behavior:** The scraper takes 1-3 minutes per product search.

**To speed up:** Reduce `max_results` in the code (default is 12, try 5-8).

### Browser automation fails

**Solution:** Make sure Playwright browsers are installed:
```bash
python -m playwright install chromium
```

## Cost Estimation

Using Gemini 2.0 Flash via OpenRouter is very affordable:

- **Per search**: ~$0.001-0.003 USD
- **100 searches**: ~$0.10-0.30 USD

OpenRouter pricing: [https://openrouter.ai/docs/pricing](https://openrouter.ai/docs/pricing)

## Best Practices

1. **Rate Limiting**: Don't abuse the scraper - add appropriate delays
2. **Error Handling**: Always check for empty results
3. **API Usage**: Monitor your OpenRouter usage and costs
4. **Legal Compliance**: Respect AliExpress Terms of Service
5. **Data Validation**: Verify scraped data before use

## Files

- `run.py` - Simple executable launcher with auto-install
- `scraper.py` - Main scraper implementation
- `requirements.txt` - Python dependencies
- `verify_setup.py` - Setup verification script
- `example_usage.py` - Usage examples
- `.env.example` - Environment variable template

## Development

### Debug Mode

Set `headless=False` in `scraper.py` to see the browser in action:

```python
browser = Browser(
    config=BrowserConfig(
        headless=False,  # Show browser window
        disable_security=True,
    )
)
```

### Logging

Adjust logging level in `scraper.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # More detailed logs
```

## Limitations

- Requires stable internet connection
- AliExpress site structure changes may break scraping
- Browser automation is slower than API-based solutions
- Regional restrictions may apply

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check the [QUICKSTART.md](QUICKSTART.md) guide
- Review the troubleshooting section above
- Run `python verify_setup.py` to diagnose problems

## Credits

Built with:
- [Browser Use](https://github.com/browser-use/browser-use)
- [OpenRouter](https://openrouter.ai/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)
- [Playwright](https://playwright.dev/)

## Updates

- **v2.0**: Switched to OpenRouter + Gemini 2.0 Flash for better performance and lower costs
- **v2.0**: Added auto-install launcher (`run.py`) for easier setup
- **v1.0**: Initial release with Claude API
