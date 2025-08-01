#!/usr/bin/env python3
"""
Debug script to test the opportunity search endpoint
"""
import requests
import json

def test_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    # Test root endpoint
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Root error: {e}")
    
    # Test docs endpoint  
    print("\nTesting docs endpoint...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Docs: {response.status_code} - Available")
    except Exception as e:
        print(f"Docs error: {e}")
    
    # Test openapi endpoint
    print("\nTesting OpenAPI spec...")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            print(f"OpenAPI: {response.status_code}")
            print("Available paths:")
            for path in spec.get("paths", {}):
                print(f"  {path}")
        else:
            print(f"OpenAPI: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"OpenAPI error: {e}")
    
    # Test the problematic endpoint
    print("\nTesting /opportunity/search endpoint...")
    try:
        response = requests.get(f"{base_url}/opportunity/search")
        print(f"Opportunity search: {response.status_code} - {response.text}")
        if response.status_code != 200:
            print("Headers:", response.headers)
    except Exception as e:
        print(f"Opportunity search error: {e}")

    # Test auth endpoints
    print("\nTesting auth endpoint...")
    try:
        response = requests.get(f"{base_url}/auth/me")
        print(f"Auth me: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Auth me error: {e}")

if __name__ == "__main__":
    test_endpoint()