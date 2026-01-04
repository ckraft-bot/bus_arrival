#!/usr/bin/env python3
"""
Simple test script to verify the API connection
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import SLTransportAPI, BusArrivalDisplay


def test_api_connection():
    """Test basic API connectivity"""
    print("Testing SL Transport API connection...\n")
    
    api = SLTransportAPI()
    
    # Test 1: Fetch all sites
    print("Test 1: Fetching all sites...")
    try:
        import requests
        response = requests.get("https://transport.integration.sl.se/v1/sites")
        if response.status_code == 200:
            sites = response.json()
            print(f"✓ Success! Found {len(sites)} sites")
        else:
            print(f"✗ Failed with status code {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Get specific site info (Slussen)
    print("\nTest 2: Getting site info for Slussen (9192)...")
    site_info = api.get_site_info(9192)
    if site_info:
        print(f"✓ Success! Site name: {site_info.get('name')}")
    else:
        print("✗ Failed to get site info")
        return False
    
    # Test 3: Get departures
    print("\nTest 3: Getting departures from Slussen...")
    departures = api.get_departures(9192)
    if departures and 'departures' in departures:
        count = len(departures['departures'])
        print(f"✓ Success! Found {count} departures")
        
        if count > 0:
            first = departures['departures'][0]
            line = first.get('line', {})
            print(f"  First departure: Line {line.get('designation')} to {first.get('destination')}")
    else:
        print("✗ Failed to get departures (might be no service at this time)")
    
    print("\n" + "="*70)
    print("All tests completed!")
    return True


def test_display():
    """Test the display output"""
    print("\n" + "="*70)
    print("Testing display output...\n")
    
    display = BusArrivalDisplay([9192])
    display.display_departures()
    
    print("\n" + "="*70)
    print("Display test completed!")


if __name__ == "__main__":
    success = test_api_connection()
    
    if success:
        print("\n")
        response = input("Run display test? (y/n): ")
        if response.lower() == 'y':
            test_display()