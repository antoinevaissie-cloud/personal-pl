#!/usr/bin/env python3
"""Test script to verify Boursorama category extraction"""

import pandas as pd
import json
from etl.boursorama import load_boursorama_csv

def test_boursorama_categories():
    # Read sample CSV file
    csv_path = "../data/bourorama_euro_accounts.csv"  # Adjust path if needed
    
    print("Testing Boursorama CSV category extraction...")
    print("=" * 60)
    
    try:
        with open(csv_path, 'rb') as f:
            content = f.read()
        
        # Load using the Boursorama parser
        rows = load_boursorama_csv(content)
        
        print(f"✅ Loaded {len(rows)} transactions")
        
        # Check category distribution
        categories = {}
        for row in rows:
            extra = row.get('extra', {})
            cat_parent = extra.get('category_parent', 'None')
            cat = extra.get('category', 'None')
            
            if cat_parent not in categories:
                categories[cat_parent] = []
            categories[cat_parent].append(cat)
        
        print(f"\n📊 Found {len(categories)} unique parent categories:")
        for parent, subcats in categories.items():
            unique_subcats = set(subcats)
            print(f"  • {parent}: {len(unique_subcats)} subcategories, {len(subcats)} transactions")
            
        # Show sample transactions with categories
        print("\n📝 Sample transactions with categories:")
        for i, row in enumerate(rows[:5]):
            extra = row.get('extra', {})
            print(f"\n{i+1}. {row['description'][:50]}")
            print(f"   Amount: {row['amount']} {row['currency']}")
            print(f"   Category Parent: {extra.get('category_parent', 'N/A')}")
            print(f"   Category: {extra.get('category', 'N/A')}")
            
    except FileNotFoundError:
        print(f"❌ CSV file not found at {csv_path}")
        print("   Please update the path or ensure the file exists")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_boursorama_categories()