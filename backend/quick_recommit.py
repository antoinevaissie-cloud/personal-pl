#!/usr/bin/env python3
"""Quick script to re-run import commit with fixed rules engine"""

import requests
import json

# Re-run the import commit
print("Re-running import commit for July 2025...")

# You'll need to be logged in through the browser
# Or update with your actual JWT token
response = requests.post(
    "http://localhost:8000/api/import/commit",
    headers={
        "Content-Type": "application/json",
        # Get this from browser DevTools > Network > Authorization header
        "Authorization": "Bearer YOUR_TOKEN_HERE"
    },
    json={"period_month": "2025-07-01"}
)

if response.status_code == 200:
    print("✅ Success! Categories should now be applied.")
    result = response.json()
    print(f"Processed: {result.get('transactions_derived', 0)} transactions")
    print(f"Uncategorized: {result.get('uncategorized_count', 0)}")
else:
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print("\nPlease use the frontend instead:")