#!/usr/bin/env python3
"""
Test script for opportunities endpoints
"""
import requests
import json

def test_opportunities():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing opportunities endpoints...")
    
    # Test list opportunities (GET /)
    print("\n1. Testing GET /v1/opportunities/")
    try:
        response = requests.get(f"{base_url}/v1/opportunities/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} opportunities")
            if data:
                print(f"First opportunity: {data[0].get('title', 'No title')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test search opportunities (GET /search)
    print("\n2. Testing GET /v1/opportunities/search")
    try:
        response = requests.get(f"{base_url}/v1/opportunities/search")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} opportunities via search")
            if data:
                print(f"First opportunity: {data[0].get('title', 'No title')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test search with filters
    print("\n3. Testing GET /v1/opportunities/search?limit=5")
    try:
        response = requests.get(f"{base_url}/v1/opportunities/search?limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} opportunities with limit")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_opportunities()