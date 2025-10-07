#!/usr/bin/env python3
"""
Simple usage example for the UTM Finder webapp components
"""

from app import check_utm_source

# Test different URLs
test_cases = [
    ("https://example.com?utm_source=chatgpt.com&utm_medium=referral", True),
    ("https://example.com?utm_source=google", False),
    ("https://example.com", False),
    ("https://chatgpt.com?utm_source=chatgpt.com", True),
]

print("Testing UTM Source Detection:")
print("-" * 50)

for url, expected in test_cases:
    result = check_utm_source(url)
    status = "✓" if result == expected else "✗"
    print(f"{status} {url}")
    print(f"  Expected: {expected}, Got: {result}\n")

print("\nAll tests completed!")
