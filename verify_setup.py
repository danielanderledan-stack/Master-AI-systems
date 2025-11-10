#!/usr/bin/env python3
"""
Verification script to check if all dependencies are installed correctly
Run this before using the scraper
"""

import sys
import os


def check_python_version():
    """Check if Python version is 3.8+"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    packages = {
        'openai': 'OpenAI client (for OpenRouter)',
        'langchain_openai': 'LangChain OpenAI',
        'browser_use': 'Browser Use automation',
        'playwright': 'Playwright browser automation',
    }

    all_installed = True

    for package, description in packages.items():
        print(f"Checking {description}...", end=" ")
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not found")
            all_installed = False

    return all_installed


def check_api_key():
    """Check if OPENROUTER_API_KEY is set"""
    print("Checking OPENROUTER_API_KEY...", end=" ")
    api_key = os.getenv('OPENROUTER_API_KEY')

    if api_key:
        # Mask most of the key
        masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
        print(f"✓ Set ({masked})")
        return True
    else:
        print("✗ Not set")
        return False


def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    print("Checking Playwright browsers...", end=" ")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Try to get browser
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✓ Chromium installed")
                return True
            except Exception as e:
                print(f"✗ Chromium not installed ({str(e)[:30]}...)")
                return False
    except Exception as e:
        print(f"✗ Error checking ({str(e)[:30]}...)")
        return False


def check_api_connection():
    """Test connection to OpenRouter API"""
    print("Testing OpenRouter API connection...", end=" ")
    try:
        from openai import OpenAI

        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("⊘ Skipped (no API key)")
            return None

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        # Simple test request
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        print("✓ API connection successful")
        return True

    except Exception as e:
        print(f"✗ Failed ({str(e)[:50]}...)")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "="*60)
    print(" "*15 + "Setup Verification")
    print("="*60 + "\n")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("API Key", check_api_key),
        ("Playwright Browsers", check_playwright_browsers),
        ("API Connection", check_api_connection),
    ]

    results = {}

    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        results[check_name] = check_func()
        print()

    # Summary
    print("="*60)
    print("Summary")
    print("="*60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    print(f"\n✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    if skipped > 0:
        print(f"⊘ Skipped: {skipped}")

    if failed == 0 and passed > 0:
        print("\n🎉 All checks passed! You're ready to use the scraper.")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")

        if not results.get("Dependencies"):
            print("\nTo install dependencies:")
            print("  pip install -r requirements.txt")

        if not results.get("Playwright Browsers"):
            print("\nTo install Playwright browsers:")
            print("  playwright install")

        if not results.get("API Key"):
            print("\nTo set API key:")
            print("  export OPENROUTER_API_KEY='your-key-here'")
            print("\nGet your key at: https://openrouter.ai/keys")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
