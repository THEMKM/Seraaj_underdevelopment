#!/usr/bin/env python3
"""
Debug script to test the opportunity search endpoint
"""
import requests
import traceback

def test_search_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing /opportunity/search endpoint...")
    try:
        response = requests.get(f"{base_url}/opportunity/search")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    print("\nTesting basic health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.text}")
    except Exception as e:
        print(f"Health Error: {e}")

if __name__ == "__main__":
    test_search_endpoint()