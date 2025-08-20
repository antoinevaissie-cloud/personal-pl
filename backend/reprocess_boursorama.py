#!/usr/bin/env python3
"""Reprocess Boursorama transactions with built-in categories"""

import requests
import json
from datetime import date

# Configuration
API_URL = "http://localhost:8000"
PERIOD_MONTH = "2025-07-01"

def get_auth_token():
    """Get auth token - you may need to update with your actual credentials"""
    # Try to login with test credentials
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": "antoinevaissie", "password": "test123"}  # Update password
    )
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to login. Please update credentials in the script.")
        return None

def reprocess_import(token):
    """Re-run import commit to apply categories"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Run import commit
    print(f"Running import commit for {PERIOD_MONTH}...")
    response = requests.post(
        f"{API_URL}/api/import/commit",
        headers=headers,
        json={"period_month": PERIOD_MONTH}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Import commit successful!")
        print(f"  - Transactions processed: {result.get('transactions_derived', 0)}")
        print(f"  - Uncategorized: {result.get('uncategorized_count', 0)}")
        return True
    else:
        print(f"❌ Import commit failed: {response.status_code}")
        print(f"   {response.text}")
        return False

def check_pl_summary(token):
    """Check P&L summary to see categories"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nFetching P&L summary for {PERIOD_MONTH}...")
    response = requests.post(
        f"{API_URL}/api/pl/summary",
        headers=headers,
        json={
            "month": PERIOD_MONTH,
            "accounts": ["Boursorama"],
            "exclude_transfers": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n📊 P&L Summary:")
        print(f"  Income: €{result['summary']['income']:.2f}")
        print(f"  Expenses: €{result['summary']['expenses']:.2f}")
        print(f"  Net: €{result['summary']['net']:.2f}")
        
        print("\n📂 Categories:")
        for cat in result.get('categories', []):
            if cat['net'] != 0:
                print(f"  {cat['category']}: €{cat['net']:.2f} (Income: €{cat['income']:.2f}, Expense: €{cat['expense']:.2f})")
        
        if result.get('uncategorized_count', 0) > 0:
            print(f"\n⚠️  Still have {result['uncategorized_count']} uncategorized transactions")
    else:
        print(f"❌ Failed to get P&L summary: {response.status_code}")

if __name__ == "__main__":
    print("Reprocessing Boursorama transactions with built-in categories...")
    print("-" * 60)
    
    # You can either:
    # 1. Get token via login (update password above)
    # 2. Or copy your token from browser DevTools
    
    # Option 1: Login
    # token = get_auth_token()
    
    # Option 2: Paste your token here (get from browser DevTools > Network > Authorization header)
    token = input("Please paste your JWT token from the browser (or press Enter to try login): ").strip()
    
    if not token:
        token = get_auth_token()
    
    if token:
        if reprocess_import(token):
            check_pl_summary(token)
    else:
        print("\n⚠️  No valid token. Please:")
        print("  1. Copy your JWT token from browser DevTools")
        print("  2. Or update the login credentials in this script")