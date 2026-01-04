#!/usr/bin/env python3
"""
SL Bus Arrival Display
Based on the bus_arrival project but adapted for SL (Stockholm) public transport
"""

import requests
import time
from datetime import datetime
import os
from typing import List, Dict, Optional
from zoneinfo import ZoneInfo

# Hard-lock timezone to Sweden
SWEDEN_TZ = ZoneInfo("Europe/Stockholm")

# Cutoff forecast
MAX_MINUTES_AHEAD = 60


class SLTransportAPI:
    """Handler for SL Transport API"""

    BASE_URL = "https://transport.integration.sl.se/v1"

    def __init__(self):
        self.session = requests.Session()

    def get_site_info(self, site_id: int) -> Optional[Dict]:
        try:
            response = self.session.get(f"{self.BASE_URL}/sites")
            response.raise_for_status()
            sites = response.json()

            for site in sites:
                if site.get("id") == site_id:
                    return site
            return None
        except Exception as e:
            print(f"Error fetching site info: {e}")
            return None

    def get_departures(self, site_id: int, forecast: int = 30) -> Optional[Dict]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sites/{site_id}/departures",
                params={"forecast": forecast},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching departures: {e}")
            return None


class BusArrivalDisplay:
    """Main display handler for bus arrivals"""

    def __init__(self, site_ids: List[int]):
        self.api = SLTransportAPI()
        self.site_ids = site_ids

    def format_time_display(self, scheduled: str, expected: str = None):
        """
        SL timestamps are inconsistent:
        - Sometimes UTC (with Z)
        - Sometimes local Stockholm time (no tzinfo)

        This function handles both correctly.
        """
        try:
            target_time_str = expected or scheduled
            dt = datetime.fromisoformat(target_time_str.replace("Z", "+00:00"))

            # CRITICAL FIX:
            # If no timezone info, assume Stockholm local time
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=SWEDEN_TZ)
            else:
                dt = dt.astimezone(SWEDEN_TZ)

            now_se = datetime.now(SWEDEN_TZ)
            minutes = int((dt - now_se).total_seconds() // 60)

            if minutes <= 0:
                return "Nu", 0
            elif minutes == 1:
                return "1 min", 1
            else:
                return f"{minutes} min", minutes

        except Exception as e:
            print(f"Error formatting time: {e}")
            return "?", None

    def get_transport_icon(self, transport_mode: str) -> str:
        return {
            "BUS": "🚌",
            "METRO": "🚇",
            "TRAIN": "🚆",
            "TRAM": "🚊",
            "SHIP": "⛴️",
            "FERRY": "⛴️",
        }.get(transport_mode, "🚌")

    def display_departures(self):
        print("\n" + "=" * 80)
        print(
            f"SL BUSS AVGÅNGAR - {datetime.now(SWEDEN_TZ).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 80 + "\n")

        for site_id in self.site_ids:
            site_info = self.api.get_site_info(site_id)
            if not site_info:
                print(f"❌ Site {site_id} not found\n")
                continue

            site_name = site_info.get("name", f"Site {site_id}")
            print(f"📍 {site_name} (Site ID: {site_id})")
            print("-" * 80)

            departures_data = self.api.get_departures(site_id)
            if not departures_data or "departures" not in departures_data:
                print("   No departure information available\n")
                continue

            departures = departures_data["departures"]
            if not departures:
                print("   No bus departures in the next 30 minutes\n")
                continue

            shown = set()
            count = 0
            max_display = 10

            for dep in departures:
                if count >= max_display:
                    break

                line = dep.get("line", {})
                transport_mode = line.get("transport_mode", "BUS")

                # Only buses
                if transport_mode != "BUS":
                    continue

                line_no = line.get("designation", "N/A")
                destination = dep.get("destination", "Unknown")
                scheduled = dep.get("scheduled", "")
                expected = dep.get("expected")

                key = f"{line_no}-{destination}"
                if key in shown:
                    continue

                time_str, minutes = self.format_time_display(scheduled, expected)

                # HARD FILTER: ignore far-future services
                if minutes is None or minutes > MAX_MINUTES_AHEAD:
                    continue

                state = dep.get("state", "")
                delay = (
                    " ⏱️" if state == "EXPECTEDATSTOP"
                    else " ❌" if state == "CANCELLED"
                    else ""
                )

                print(
                    f"   🚌 Line {line_no:>4} → {destination:<25} {time_str:>8}{delay}"
                )

                shown.add(key)
                count += 1

            if count == 0:
                print("   No bus departures found\n")

            if departures_data.get("stop_deviations"):
                print("\n   ⚠️  Deviations:")
                for d in departures_data["stop_deviations"][:3]:
                    print(f"      • {d.get('message', '')}")

            print()


def main():
    site_ids = [
        int(x.strip())
        for x in os.getenv("SITE_IDS", "9192,9001").split(",")
    ]
    refresh_interval = int(os.getenv("REFRESH_INTERVAL", "60"))

    print("🚌 SL Bus Arrival Display Starting...")
    print("Timezone locked to Europe/Stockholm")
    print(f"Monitoring sites: {site_ids}")
    print(f"Refresh interval: {refresh_interval} seconds")

    display = BusArrivalDisplay(site_ids)

    try:
        while True:
            display.display_departures()
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\nDisplay stopped by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
