#!/usr/bin/env python3
"""
Simple executable launcher for AliExpress scraper with auto dependency installation
"""

import sys
import subprocess
import os
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_dependencies():
    """Install all required dependencies"""
    print("🔍 Checking dependencies...\n")

    required_packages = {
        'browser_use': 'browser-use>=0.1.0',
        'openai': 'openai>=1.12.0',
        'langchain_openai': 'langchain-openai>=0.0.5',
        'playwright': 'playwright>=1.40.0',
        'aiohttp': 'aiohttp>=3.9.0',
        'bs4': 'beautifulsoup4>=4.12.0',
    }

    missing_packages = []

    for package, pip_package in required_packages.items():
        if not check_package(package):
            missing_packages.append(pip_package)

    if missing_packages:
        print(f"📦 Installing {len(missing_packages)} missing packages...")
        print()

        # Install pip packages
        for package in missing_packages:
            print(f"   Installing {package}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-q", package],
                    stdout=subprocess.DEVNULL
                )
                print(f"   ✓ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"   ✗ Failed to install {package}: {e}")
                return False

        print()

        # Install Playwright browsers
        print("🌐 Installing Playwright browsers...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("   ✓ Playwright browsers installed")
        except subprocess.CalledProcessError:
            print("   ⚠ Playwright browser installation failed (will retry later)")

        print()
    else:
        print("✅ All dependencies already installed!\n")

    return True

def check_api_key():
    """Check if API key is set"""
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        print()
        print("Please set your OpenRouter API key:")
        print()
        print("  Linux/macOS:")
        print("    export OPENROUTER_API_KEY='your-key-here'")
        print()
        print("  Windows (PowerShell):")
        print("    $env:OPENROUTER_API_KEY='your-key-here'")
        print()
        print("  Windows (CMD):")
        print("    set OPENROUTER_API_KEY=your-key-here")
        print()
        print("Get your API key at: https://openrouter.ai/keys")
        print()
        return False

    return True

def main():
    """Main launcher"""
    print()
    print("=" * 60)
    print("  AliExpress AI Scraper - Auto Launcher")
    print("  Powered by OpenRouter (Gemini 2.0 Flash)")
    print("=" * 60)
    print()

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        print(f"   Current version: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)

    # Install dependencies if needed
    if not install_dependencies():
        print("❌ Dependency installation failed!")
        sys.exit(1)

    # Check API key
    if not check_api_key():
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python run.py \"PRODUCT NAME\" [output_file.json]")
        print()
        print("Example:")
        print("  python run.py \"RGB FAN 120MM X3\"")
        print("  python run.py \"Gaming Mouse\" custom_output.json")
        print()
        sys.exit(1)

    product_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "product_result.json"

    print("🚀 Starting scraper...")
    print(f"   Product: {product_name}")
    print(f"   Output: {output_file}")
    print()

    # Import and run scraper
    try:
        import asyncio
        from scraper import AliExpressScraper

        async def run_scraper():
            scraper = AliExpressScraper()
            result = await scraper.scrape_product(product_name, output_file)

            print()
            print("=" * 60)
            print("✅ SUCCESS! Product scraped and analyzed")
            print("=" * 60)
            print()
            print(f"Title: {result.title}")
            print(f"Price: {result.price}")
            print()
            print(f"Description:\n{result.description}")
            print()
            print(f"Images ({len(result.images)}):")
            for i, img in enumerate(result.images, 1):
                print(f"  {i}. {img}")
            print()
            print(f"📄 Full results saved to: {output_file}")
            print()

        asyncio.run(run_scraper())

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"{str(e)}")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
