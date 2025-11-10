#!/usr/bin/env python3
"""
Example usage of the AliExpress scraper
Demonstrates different use cases
"""

import asyncio
import json
from scraper import AliExpressScraper


async def example_basic_search():
    """Basic product search example"""
    print("Example 1: Basic Product Search")
    print("="*60)

    scraper = AliExpressScraper()

    # Search for a product
    product_name = "RGB FAN 120MM X3"
    result = await scraper.scrape_product(product_name, "example_output.json")

    print(f"\nTitle: {result.title}")
    print(f"Price: {result.price}")
    print(f"\nDescription:\n{result.description}")
    print(f"\nImages: {len(result.images)} found")

    print("\n" + "="*60 + "\n")


async def example_custom_parameters():
    """Example with custom search parameters"""
    print("Example 2: Custom Parameters")
    print("="*60)

    scraper = AliExpressScraper()

    # Search with fewer results for faster testing
    products = await scraper.scrape_with_browser_use_direct(
        product_name="Gaming Keyboard",
        max_results=5  # Only scrape top 5 products
    )

    print(f"\nFound {len(products)} products:")
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product.title[:60]}...")
        print(f"   Price: {product.price}")
        print(f"   Rating: {product.rating}")
        print(f"   Orders: {product.orders}")

    # Now select and generate content
    if products:
        ai_result = scraper.select_and_generate_content(products)
        print(f"\n\nClaude selected product #{ai_result['selected_index']}")
        print(f"Generated title: {ai_result['title']}")

    print("\n" + "="*60 + "\n")


async def example_error_handling():
    """Example showing error handling"""
    print("Example 3: Error Handling")
    print("="*60)

    scraper = AliExpressScraper()

    try:
        # Try searching for something that might not exist
        result = await scraper.scrape_product(
            "xyzabc123nonexistent",
            "error_test.json"
        )
        print("Search completed successfully")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\n" + "="*60 + "\n")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AliExpress Scraper - Usage Examples" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")

    # Run examples
    # Note: Comment out examples you don't want to run

    # await example_basic_search()
    # await example_custom_parameters()
    # await example_error_handling()

    print("\nTo run these examples, uncomment them in the main() function")
    print("and ensure your ANTHROPIC_API_KEY is set.\n")


if __name__ == "__main__":
    asyncio.run(main())
