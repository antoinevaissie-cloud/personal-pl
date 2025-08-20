#!/usr/bin/env python
"""Test commit endpoint"""
import requests
import json

# Login first
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "testuser", "password": "testpass123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Logged in successfully")

# Try to commit October 2025
commit_response = requests.post(
    "http://localhost:8000/api/import/commit",
    headers={"Authorization": f"Bearer {token}"},
    json={"period_month": "2025-10"}
)

print(f"Commit response status: {commit_response.status_code}")
print(f"Commit response: {json.dumps(commit_response.json(), indent=2)}")

# Check what months have data
import sys
sys.path.append('backend')
from db.duck import get_conn

# This will fail due to lock, but let's try with curl instead