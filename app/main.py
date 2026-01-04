#!/usr/bin/env python3
"""
SL Bus Arrival Display
Based on the bus_arrival project but adapted for SL (Stockholm) public transport
"""

import requests
import time
from datetime import datetime
import json
import os
from typing import List, Dict, Optional


class SLTransportAPI:
    """Handler for SL Transport API"""
    
    BASE_URL = "https://transport.integration.sl.se/v1"
    
    def __init__(self):
        self.session = requests.Session()
        
    def get_site_info(self, site_id: int) -> Optional[Dict]:
        """
        Get information about a specific site
        
        Args:
            site_id: The site ID (e.g., 9192 for Slussen)
            
        Returns:
            Site information or None if not found
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/sites")
            response.raise_for_status()
            sites = response.json()
            
            for site in sites:
                if site.get('id') == site_id:
                    return site
            return None
        except Exception as e:
            print(f"Error fetching site info: {e}")
            return None
    
    def get_departures(self, site_id: int, forecast: int = 30) -> Optional[Dict]:
        """
        Get real-time departures from a site
        
        Args:
            site_id: The site ID to get departures from
            forecast: Number of minutes to forecast (default 30)
            
        Returns:
            Departure information or None if error
        """
        try:
            params = {
                'forecast': forecast
            }
            response = self.session.get(
                f"{self.BASE_URL}/sites/{site_id}/departures",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching departures: {e}")
            return None


class BusArrivalDisplay:
    """Main display handler for bus arrivals"""
    
    def __init__(self, site_ids: List[int]):
        """
        Initialize the display
        
        Args:
            site_ids: List of site IDs to monitor (e.g., [9192, 9001])
        """
        self.api = SLTransportAPI()
        self.site_ids = site_ids
        
    def format_time_display(self, scheduled: str, expected: str = None) -> str:
        """
        Format departure time for display
        
        Args:
            scheduled: Scheduled departure time (ISO format)
            expected: Expected departure time (ISO format)
            
        Returns:
            Formatted string showing time or minutes until departure
        """
        try:
            # Parse the expected or scheduled time
            target_time_str = expected if expected else scheduled
            target_time = datetime.fromisoformat(target_time_str.replace('Z', '+00:00'))
            now = datetime.now(target_time.tzinfo)
            
            # Calculate minutes until departure
            diff = target_time - now
            minutes = int(diff.total_seconds() / 60)
            
            if minutes < 0:
                return "Nu"
            elif minutes == 0:
                return "Nu"
            elif minutes == 1:
                return "1 min"
            else:
                return f"{minutes} min"
                
        except Exception as e:
            print(f"Error formatting time: {e}")
            return scheduled.split('T')[1][:5] if 'T' in scheduled else scheduled
    
    def get_transport_icon(self, transport_mode: str) -> str:
        """
        Get an icon/emoji for the transport mode
        
        Args:
            transport_mode: The transport mode (BUS, METRO, TRAIN, etc.)
            
        Returns:
            An appropriate icon/emoji
        """
        icons = {
            'BUS': '🚌',
            'METRO': '🚇',
            'TRAIN': '🚆',
            'TRAM': '🚊',
            'SHIP': '⛴️',
            'FERRY': '⛴️'
        }
        return icons.get(transport_mode, '🚌')
    
    def display_departures(self):
        """Display departures for all configured sites"""
        
        print("\n" + "="*80)
        print(f"SL AVGÅNGAR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        for site_id in self.site_ids:
            # Get site information
            site_info = self.api.get_site_info(site_id)
            if not site_info:
                print(f"❌ Site {site_id} not found\n")
                continue
            
            site_name = site_info.get('name', f'Site {site_id}')
            print(f"📍 {site_name} (Site ID: {site_id})")
            print("-" * 80)
            
            # Get departures
            departures_data = self.api.get_departures(site_id)
            if not departures_data or 'departures' not in departures_data:
                print("   No departure information available\n")
                continue
            
            departures = departures_data['departures']
            
            if not departures:
                print("   No departures in the next 30 minutes\n")
                continue
            
            # Group departures by line
            lines_shown = set()
            count = 0
            max_display = 10  # Show max 10 departures per site
            
            for departure in departures:
                if count >= max_display:
                    break
                
                line = departure.get('line', {})
                line_designation = line.get('designation', 'N/A')
                transport_mode = line.get('transport_mode', 'BUS')
                
                destination = departure.get('destination', 'Unknown')
                scheduled = departure.get('scheduled', '')
                expected = departure.get('expected')
                display_time = self.format_time_display(scheduled, expected)
                
                # Get delay information
                state = departure.get('state', 'UNKNOWN')
                delay_indicator = ""
                if state == "EXPECTEDATSTOP":
                    delay_indicator = " ⏱️"
                elif state == "CANCELLED":
                    delay_indicator = " ❌"
                
                # Display format
                icon = self.get_transport_icon(transport_mode)
                line_key = f"{line_designation}-{destination}"
                
                # Only show each line-destination combo once
                if line_key not in lines_shown:
                    print(f"   {icon} Line {line_designation:>4} → {destination:<25} {display_time:>8}{delay_indicator}")
                    lines_shown.add(line_key)
                    count += 1
            
            # Show stop deviations if any
            if 'stop_deviations' in departures_data and departures_data['stop_deviations']:
                print("\n   ⚠️  Deviations:")
                for deviation in departures_data['stop_deviations'][:3]:  # Max 3 deviations
                    message = deviation.get('message', '')
                    print(f"      • {message}")
            
            print()


def main():
    """Main entry point"""
    
    # Configuration
    # Default site IDs - you can change these to your preferred stops
    # 9192 = Slussen
    # 9001 = T-Centralen  
    # 1079 = Odenplan
    
    site_ids_str = os.getenv('SITE_IDS', '9192,9001')
    site_ids = [int(x.strip()) for x in site_ids_str.split(',')]
    
    # Refresh interval in seconds
    refresh_interval = int(os.getenv('REFRESH_INTERVAL', '60'))
    
    print("🚌 SL Bus Arrival Display Starting...")
    print(f"Monitoring sites: {site_ids}")
    print(f"Refresh interval: {refresh_interval} seconds")
    
    display = BusArrivalDisplay(site_ids)
    
    try:
        while True:
            display.display_departures()
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n\n👋 Display stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()