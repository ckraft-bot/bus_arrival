#!/usr/bin/env python3
"""
Utility script to search for SL sites
"""

import requests
import sys


def search_sites(query: str = None):
    """
    Search for SL sites
    
    Args:
        query: Optional search term to filter sites
    """
    try:
        print("Fetching all SL sites...")
        response = requests.get("https://transport.integration.sl.se/v1/sites")
        response.raise_for_status()
        sites = response.json()
        
        print(f"Found {len(sites)} sites\n")
        
        # Filter if query provided
        if query:
            query = query.lower()
            sites = [s for s in sites if query in s.get('name', '').lower()]
            print(f"Filtered to {len(sites)} sites matching '{query}'\n")
        
        # Display results
        if not sites:
            print("No sites found")
            return
        
        print(f"{'ID':<8} {'Name':<40} {'Abbreviation':<12}")
        print("-" * 70)
        
        for site in sites[:50]:  # Limit to first 50 results
            site_id = site.get('id', 'N/A')
            name = site.get('name', 'Unknown')
            abbr = site.get('abbreviation', '')
            
            print(f"{site_id:<8} {name:<40} {abbr:<12}")
        
        if len(sites) > 50:
            print(f"\n... and {len(sites) - 50} more sites")
            print("Tip: Use a search term to narrow results")
        
        print(f"\nTo use a site, add its ID to your .env file:")
        print(f"SITE_IDS=9192,9001")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_site_details(site_id: int):
    """
    Get detailed information about a specific site
    
    Args:
        site_id: The site ID to look up
    """
    try:
        print(f"Fetching details for site {site_id}...\n")
        
        # Get site info
        response = requests.get("https://transport.integration.sl.se/v1/sites?expand=true")
        response.raise_for_status()
        sites = response.json()
        
        site = None
        for s in sites:
            if s.get('id') == site_id:
                site = s
                break
        
        if not site:
            print(f"Site {site_id} not found")
            return
        
        # Display site details
        print(f"Site ID:      {site.get('id')}")
        print(f"Name:         {site.get('name')}")
        print(f"Abbreviation: {site.get('abbreviation', 'N/A')}")
        print(f"GID:          {site.get('gid', 'N/A')}")
        print(f"Latitude:     {site.get('lat', 'N/A')}")
        print(f"Longitude:    {site.get('lon', 'N/A')}")
        
        if 'stop_areas' in site and site['stop_areas']:
            print(f"\nStop Areas:   {', '.join(str(sa) for sa in site['stop_areas'])}")
        
        # Try to get current departures
        print(f"\nFetching current departures...")
        dep_response = requests.get(
            f"https://transport.integration.sl.se/v1/sites/{site_id}/departures",
            params={'forecast': 60}
        )
        
        if dep_response.status_code == 200:
            dep_data = dep_response.json()
            departures = dep_data.get('departures', [])
            
            if departures:
                print(f"Found {len(departures)} departures in the next hour")
                print("\nNext 5 departures:")
                for i, dep in enumerate(departures[:5], 1):
                    line = dep.get('line', {})
                    print(f"  {i}. Line {line.get('designation', 'N/A')} to {dep.get('destination', 'Unknown')}")
            else:
                print("No departures in the next hour")
        else:
            print("Could not fetch departure information")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    
    if len(sys.argv) > 2 and sys.argv[1] == "details":
        # Get details about a specific site
        try:
            site_id = int(sys.argv[2])
            get_site_details(site_id)
        except ValueError:
            print("Error: Site ID must be a number")
            sys.exit(1)
    elif len(sys.argv) > 1:
        # Search with query
        query = ' '.join(sys.argv[1:])
        search_sites(query)
    else:
        # Show all sites (or help)
        print("SL Site Search Utility")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 app/find_sites.py [search term]     # Search for sites")
        print("  python3 app/find_sites.py details [ID]      # Get site details")
        print("\nExamples:")
        print("  python3 app/find_sites.py slussen")
        print("  python3 app/find_sites.py details 9192")
        print()
        
        response = input("Show all sites? (y/n): ")
        if response.lower() == 'y':
            search_sites()


if __name__ == "__main__":
    main()