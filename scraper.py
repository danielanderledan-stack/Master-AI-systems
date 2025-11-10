#!/usr/bin/env python3
"""
AliExpress Product Scraper with AI Selection and Content Generation
Uses Browser Use for automation and OpenRouter API (Gemini) for intelligent product selection
"""

import asyncio
import json
import logging
import sys
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Represents a product from AliExpress"""
    index: int
    title: str
    price: str
    rating: Optional[str]
    orders: Optional[str]
    description: str
    url: str


@dataclass
class ProductResult:
    """Final result with AI-generated content"""
    title: str
    price: str
    description: str
    images: List[str]


class AliExpressScraper:
    """Scraper for AliExpress products with AI-powered selection"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize scraper with API key"""
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        # OpenAI client configured for OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        # LangChain LLM for Browser Use (OpenRouter-compatible)
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
        )

        self.model = "google/gemini-2.0-flash-001"

    async def search_and_scrape(self, product_name: str, max_results: int = 12) -> List[Product]:
        """
        Search AliExpress and scrape top results

        Args:
            product_name: Product to search for
            max_results: Maximum number of results to scrape (default: 12)

        Returns:
            List of Product objects
        """
        logger.info(f"Starting search for: {product_name}")

        browser = Browser(
            config=BrowserConfig(
                headless=True,
                disable_security=True,
            )
        )

        try:
            # Create task for the browser agent
            search_task = f"""
            Go to AliExpress website (https://www.aliexpress.com).
            Search for "{product_name}".
            Extract information from the top {max_results} search results.

            For each product, extract:
            1. Product title
            2. Price (with currency symbol)
            3. Star rating (if available)
            4. Number of orders/sold (if available)
            5. Brief description or key specs (if visible)
            6. Product URL

            Return the data in a structured format.
            """

            agent = Agent(
                task=search_task,
                llm=self.llm,
                browser=browser,
            )

            logger.info("Browser automation starting...")
            result = await agent.run()

            # Parse the result - Browser Use returns extracted data
            products = self._parse_search_results(result, max_results)
            logger.info(f"Successfully scraped {len(products)} products")

            return products

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        finally:
            await browser.close()

    def _parse_search_results(self, result, max_results: int) -> List[Product]:
        """Parse browser agent results into Product objects"""
        # Browser Use agent returns structured data
        # This is a simplified parser - adjust based on actual Browser Use output
        products = []

        # The result from Browser Use contains extracted information
        # Parse it into our Product dataclass
        if hasattr(result, 'extracted_content'):
            data = result.extracted_content
        else:
            # Fallback: try to extract from result history
            data = str(result)

        logger.info("Parsing search results...")

        # Note: Browser Use typically structures data in a parseable format
        # For production, you'd parse the actual structured output
        # This is a placeholder that should be adapted to Browser Use's actual output format

        # For now, create a simple structure
        # In practice, Browser Use will return structured data that needs to be parsed
        logger.warning("Using simplified result parsing - adjust based on Browser Use output format")

        return products

    async def scrape_with_browser_use_direct(self, product_name: str, max_results: int = 12) -> List[Product]:
        """
        Use Browser Use with comprehensive extraction in one task
        """
        logger.info(f"Searching AliExpress for: {product_name}")

        browser = Browser(
            config=BrowserConfig(
                headless=True,  # Set to False for debugging
                disable_security=True,
            )
        )

        products = []

        try:
            # Single comprehensive task for Browser Use agent
            comprehensive_task = f"""
            Go to https://www.aliexpress.com and search for "{product_name}".

            Wait for the search results to fully load.

            Extract detailed information from the first {max_results} products shown in the search results.

            For each product (up to {max_results} products), extract:
            1. Product title (full text)
            2. Price (with currency symbol, e.g., "$29.99" or "US $29.99")
            3. Star rating (e.g., "4.5" or "4.7 out of 5")
            4. Number of orders/sold (e.g., "1000+ sold" or "500 orders")
            5. Product description or key features (if visible on the search results page)
            6. Product URL (the clickable link to the product page)

            Present each product's information clearly, numbered from 1 to {max_results}.

            Format each product like this:
            Product #1:
            Title: [product title]
            Price: [price]
            Rating: [rating]
            Orders: [number sold/ordered]
            Description: [brief description or specs if available]
            URL: [product page URL]

            ---

            If a field is not available, write "Not available" for that field.
            """

            agent = Agent(
                task=comprehensive_task,
                llm=self.llm,
                browser=browser,
            )

            logger.info("Starting Browser Use agent for comprehensive extraction...")
            result = await agent.run()

            logger.info("Extraction completed, parsing results...")

            # Parse the comprehensive result
            products = self._parse_comprehensive_results(result, max_results)

            if not products:
                logger.warning("No products extracted from results")

            return products

        except Exception as e:
            logger.error(f"Error during browser automation: {e}")
            raise
        finally:
            await browser.close()

    def _parse_comprehensive_results(self, result, max_results: int) -> List[Product]:
        """Parse comprehensive extraction results into Product objects"""
        import re

        products = []

        # Convert result to text
        if hasattr(result, 'final_result'):
            result_text = str(result.final_result())
        elif hasattr(result, 'extracted_content'):
            result_text = str(result.extracted_content)
        else:
            result_text = str(result)

        logger.info(f"Parsing result text (length: {len(result_text)} chars)")

        # Split by product markers
        product_sections = re.split(r'Product #\d+:', result_text)

        for i, section in enumerate(product_sections[1:], 0):  # Skip first empty split
            if i >= max_results:
                break

            try:
                # Extract fields using regex
                title_match = re.search(r'Title:\s*(.+?)(?:\n|Price:|$)', section, re.DOTALL)
                price_match = re.search(r'Price:\s*(.+?)(?:\n|Rating:|$)', section, re.DOTALL)
                rating_match = re.search(r'Rating:\s*(.+?)(?:\n|Orders:|$)', section, re.DOTALL)
                orders_match = re.search(r'Orders:\s*(.+?)(?:\n|Description:|$)', section, re.DOTALL)
                desc_match = re.search(r'Description:\s*(.+?)(?:\n|URL:|$)', section, re.DOTALL)
                url_match = re.search(r'URL:\s*(.+?)(?:\n|---|$)', section, re.DOTALL)

                title = title_match.group(1).strip() if title_match else f"Product {i+1}"
                price = price_match.group(1).strip() if price_match else "N/A"
                rating = rating_match.group(1).strip() if rating_match else "N/A"
                orders = orders_match.group(1).strip() if orders_match else "N/A"
                description = desc_match.group(1).strip() if desc_match else "N/A"
                url = url_match.group(1).strip() if url_match else "https://www.aliexpress.com"

                # Clean up "Not available" entries
                if "not available" in title.lower():
                    title = f"Product {i+1}"
                if "not available" in price.lower():
                    price = "N/A"
                if "not available" in rating.lower():
                    rating = "N/A"
                if "not available" in orders.lower():
                    orders = "N/A"
                if "not available" in description.lower():
                    description = "N/A"

                product = Product(
                    index=i,
                    title=title,
                    price=price,
                    rating=rating,
                    orders=orders,
                    description=description,
                    url=url
                )

                products.append(product)
                logger.info(f"Parsed product {i}: {title[:60]}...")

            except Exception as e:
                logger.warning(f"Failed to parse product section {i}: {e}")
                continue

        logger.info(f"Successfully parsed {len(products)} products")
        return products

    def _parse_single_product(self, result, index: int) -> Optional[Product]:
        """Parse a single product from browser agent result"""
        try:
            # Extract text from result
            result_text = str(result)

            # Simple parsing logic - adjust based on actual Browser Use output
            return Product(
                index=index,
                title=self._extract_field(result_text, "title"),
                price=self._extract_field(result_text, "price"),
                rating=self._extract_field(result_text, "rating"),
                orders=self._extract_field(result_text, "orders"),
                description=self._extract_field(result_text, "description"),
                url=self._extract_field(result_text, "url"),
            )
        except Exception as e:
            logger.warning(f"Failed to parse product: {e}")
            return None

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field from text (basic implementation)"""
        # This is a simplified extraction - adjust based on Browser Use output
        return f"[{field_name}]"  # Placeholder

    def select_and_generate_content(self, products: List[Product]) -> Dict:
        """
        Single OpenRouter API call to select best product AND generate content

        Args:
            products: List of scraped products

        Returns:
            Dict with selected_index, title, and description
        """
        logger.info(f"Calling OpenRouter (Gemini) to select from {len(products)} products and generate content...")

        # Prepare products data for AI
        products_data = [
            {
                "index": p.index,
                "title": p.title,
                "price": p.price,
                "rating": p.rating,
                "orders": p.orders,
                "description": p.description,
            }
            for p in products
        ]

        prompt = f"""You are selecting the best product from AliExpress and creating SEO-optimized content for it.

STEP 1: Select the best product from these options based on:
- Rating (prefer 4.5+ stars)
- Order volume (prefer high number of orders)
- Price (reasonable for the category)
- Overall value and quality indicators

STEP 2: For the selected product, generate:
- An SEO-optimized title (compelling, includes key features, 60-80 characters)
- A detailed description (2-4 paragraphs, SEO-friendly, highlights benefits and features)

Products:
{json.dumps(products_data, indent=2)}

Return ONLY a JSON object in this exact format (no other text):
{{
  "selected_index": <index_number>,
  "title": "generated title here",
  "description": "generated description here"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)

            logger.info(f"Claude selected product index: {result['selected_index']}")
            return result

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    async def extract_product_images(self, product_url: str, max_images: int = 5) -> List[str]:
        """
        Extract image URLs from the selected product page

        Args:
            product_url: URL of the selected product
            max_images: Maximum number of images to extract

        Returns:
            List of image URLs
        """
        logger.info(f"Extracting images from: {product_url}")

        # Validate URL
        if not product_url or product_url == "https://www.aliexpress.com" or product_url == "N/A":
            logger.warning("Invalid product URL, cannot extract images")
            return []

        browser = Browser(
            config=BrowserConfig(
                headless=True,
                disable_security=True,
            )
        )

        try:
            image_agent = Agent(
                task=f"""
                Navigate to {product_url}

                Wait for the product page to fully load.

                Find and extract the main product image URLs from the product gallery.

                Look for:
                - Main product image
                - Thumbnail images in the gallery
                - High-resolution image URLs (typically from ae01.alicdn.com, ae02.alicdn.com, etc.)

                Extract up to {max_images} image URLs.

                For each image, provide the direct URL (ending in .jpg, .png, .webp, etc.)

                Format your response like this:
                Image 1: [full URL]
                Image 2: [full URL]
                Image 3: [full URL]

                Only include valid, complete image URLs.
                """,
                llm=self.llm,
                browser=browser,
            )

            result = await image_agent.run()

            # Parse image URLs from result
            images = self._parse_image_urls_enhanced(str(result), max_images)

            if not images:
                logger.warning("No images extracted, trying fallback parsing")
                # Fallback to simple URL extraction
                images = self._parse_image_urls(str(result), max_images)

            logger.info(f"Extracted {len(images)} image URLs")

            return images

        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return []
        finally:
            await browser.close()

    def _parse_image_urls_enhanced(self, result_text: str, max_images: int) -> List[str]:
        """Enhanced parsing for structured image results"""
        import re

        images = []

        # Convert result object to text
        if hasattr(result_text, 'final_result'):
            text = str(result_text.final_result())
        else:
            text = str(result_text)

        # Look for "Image N: URL" pattern
        image_matches = re.findall(r'Image \d+:\s*(https?://[^\s]+)', text, re.IGNORECASE)

        for url in image_matches[:max_images]:
            # Clean up URL
            url = url.rstrip('.,;)')
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                images.append(url)

        return images

    def _parse_image_urls(self, result_text: str, max_images: int) -> List[str]:
        """Parse image URLs from browser result"""
        import re

        # Find URLs that look like image URLs
        url_pattern = r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|webp|gif)'
        urls = re.findall(url_pattern, result_text, re.IGNORECASE)

        # Filter for AliExpress CDN images
        alicdn_images = [url for url in urls if 'alicdn.com' in url]

        # Return up to max_images
        return alicdn_images[:max_images] if alicdn_images else urls[:max_images]

    async def scrape_product(self, product_name: str, output_file: str = "product_result.json") -> ProductResult:
        """
        Main workflow: search, scrape, select, generate content, extract images

        Args:
            product_name: Product to search for
            output_file: Output JSON file path

        Returns:
            ProductResult object
        """
        try:
            # Step 1: Search and scrape products
            products = await self.scrape_with_browser_use_direct(product_name)

            if not products:
                raise ValueError("No products found in search results")

            # Step 2: Single Claude API call for selection + content generation
            ai_result = self.select_and_generate_content(products)

            # Get selected product
            selected_index = ai_result['selected_index']
            selected_product = products[selected_index]

            # Step 3: Extract images from selected product
            images = await self.extract_product_images(selected_product.url)

            # Step 4: Create final result
            result = ProductResult(
                title=ai_result['title'],
                price=selected_product.price,
                description=ai_result['description'],
                images=images
            )

            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, ensure_ascii=False)

            logger.info(f"Results saved to {output_file}")
            return result

        except Exception as e:
            logger.error(f"Error in scrape_product workflow: {e}")
            raise


async def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scraper.py \"PRODUCT NAME\"")
        print('Example: python scraper.py "RGB FAN 120MM X3"')
        sys.exit(1)

    product_name = sys.argv[1]
    output_file = "product_result.json"

    # Optional: custom output file
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    try:
        scraper = AliExpressScraper()
        result = await scraper.scrape_product(product_name, output_file)

        print("\n" + "="*60)
        print("SUCCESS! Product scraped and analyzed")
        print("="*60)
        print(f"\nTitle: {result.title}")
        print(f"Price: {result.price}")
        print(f"\nDescription:\n{result.description}")
        print(f"\nImages ({len(result.images)}):")
        for i, img in enumerate(result.images, 1):
            print(f"  {i}. {img}")
        print(f"\nFull results saved to: {output_file}")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
