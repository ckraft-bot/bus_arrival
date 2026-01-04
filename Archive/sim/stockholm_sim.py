import os
import time
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import streamlit as st

WIDTH = 800
HEIGHT = 480

# Configuration
SITE_IDS = "9193,9001"  # 9193 = Gamla Stan, 9001 = T-Centralen

def get_sl_departures(site_id, forecast=30):
    """
    Get departures from SL Transport API
    
    Args:
        site_id: Site ID (e.g., 9193 for Gamla Stan)
        forecast: Minutes to forecast (default 30)
    
    Returns:
        List of tuples: (line_designation, arrival_times, transport_mode)
    """
    url = f"https://transport.integration.sl.se/v1/sites/{site_id}/departures"
    params = {"forecast": forecast}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            print(f"Error fetching site {site_id}: {r.status_code}")
            return []

        data = r.json()
        departures = data.get("departures", [])
        
        # Group by line and get up to 3 departure times per line
        line_times = {}
        
        for dep in departures:
            line = dep.get("line", {})
            line_designation = line.get("designation", "?")
            transport_mode = line.get("transport_mode", "BUS")
            
            # FILTER: Only include buses
            if transport_mode != "BUS":
                continue
            
            scheduled = dep.get("scheduled", "")
            expected = dep.get("expected") or scheduled
            
            if not expected:
                continue
            
            try:
                # Parse the time and calculate minutes until departure
                expected_dt = datetime.fromisoformat(expected.replace('Z', '+00:00'))
                now = datetime.now(expected_dt.tzinfo)
                diff = (expected_dt - now).total_seconds() / 60
                minutes = max(round(diff), 0)
                
                # Group by line
                key = (line_designation, transport_mode)
                if key not in line_times:
                    line_times[key] = []
                
                if len(line_times[key]) < 3:
                    line_times[key].append(minutes)
                    
            except Exception as e:
                print(f"Error parsing time: {e}")
                continue
        
        # Convert to list format: (line_designation, [times], mode)
        result = []
        for (line_designation, mode), times in sorted(line_times.items()):
            result.append((line_designation, times, mode))
        
        return result[:6]  # Limit to 6 lines per side
        
    except Exception as e:
        print(f"Error fetching departures for site {site_id}: {e}")
        return []


def get_site_name(site_id):
    """Get the name of a site from its ID"""
    try:
        r = requests.get("https://transport.integration.sl.se/v1/sites", timeout=10)
        if r.status_code == 200:
            sites = r.json()
            for site in sites:
                if site.get("id") == site_id:
                    return site.get("name", f"Site {site_id}")
    except:
        pass
    return f"Site {site_id}"


def get_transport_icon(transport_mode):
    """Get text icon for transport mode"""
    icons = {
        'BUS': '🚌',
        'METRO': '🚇',
        'TRAIN': '🚆',
        'TRAM': '🚊',
        'SHIP': '⛴',
        'FERRY': '⛴'
    }
    return icons.get(transport_mode, '🚌')


def draw_bus_screen(departures_A, departures_B, site_name_A, site_name_B):
    """
    Draw the e-ink screen simulation
    
    Args:
        departures_A: List of (line, times, mode) for site A
        departures_B: List of (line, times, mode) for site B
        site_name_A: Name of site A
        site_name_B: Name of site B
    """
    img = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 28)
        font_line = ImageFont.truetype("arialbd.ttf", 32)
        font_time = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_line = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_title = ImageFont.load_default()
            font_line = ImageFont.load_default()
            font_time = ImageFont.load_default()

    # Column layout
    col_offset = WIDTH // 2
    
    # Left side (Site A)
    y = 20
    # Truncate site name if too long
    site_a_short = site_name_A if len(site_name_A) <= 15 else site_name_A[:13] + "..."
    draw.text((80, y), site_a_short, font=font_title, fill=0)
    y += 50

    for line_designation, times, mode in departures_A:
        # Draw line number box
        draw.rectangle((20, y, 140, y + 60), fill=0)
        
        # Center the line number in the box
        line_text = str(line_designation)
        # Simple centering (approximate)
        text_x = 50 if len(line_text) <= 2 else 40
        draw.text((text_x, y + 8), line_text, font=font_line, fill=255)
        
        # Draw arrival times
        times_text = " | ".join(str(t) for t in times)
        draw.text((160, y + 12), times_text, font=font_time, fill=0)
        
        y += 70
        
        # Stop if we run out of space
        if y > HEIGHT - 80:
            break

    # Right side (Site B)
    y = 20
    site_b_short = site_name_B if len(site_name_B) <= 15 else site_name_B[:13] + "..."
    draw.text((col_offset + 80, y), site_b_short, font=font_title, fill=0)
    y += 50

    for line_designation, times, mode in departures_B:
        # Draw line number box
        draw.rectangle((col_offset + 20, y, col_offset + 140, y + 60), fill=0)
        
        # Center the line number
        line_text = str(line_designation)
        text_x = col_offset + 50 if len(line_text) <= 2 else col_offset + 40
        draw.text((text_x, y + 8), line_text, font=font_line, fill=255)
        
        # Draw arrival times
        times_text = " | ".join(str(t) for t in times)
        draw.text((col_offset + 160, y + 12), times_text, font=font_time, fill=0)
        
        y += 70
        
        if y > HEIGHT - 80:
            break

    # Add timestamp at bottom
    timestamp = datetime.now().strftime("%H:%M:%S")
    draw.text((WIDTH // 2 - 50, HEIGHT - 30), timestamp, font=font_time, fill=0)

    return img


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="centered", page_title="SL Departure Simulator")

st.title("🚌 SL Bus Arrival Simulator")

# Get site IDs from hardcoded configuration
site_ids = [int(x.strip()) for x in SITE_IDS.split(",")]

if len(site_ids) < 2:
    st.error("Please provide at least 2 site IDs in SITE_IDS environment variable")
    st.stop()

SITE_A = site_ids[0]
SITE_B = site_ids[1]

# Sidebar controls
st.sidebar.header("Settings")
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 10, 120, 30)
forecast_time = st.sidebar.slider("Forecast time (minutes)", 15, 60, 30)

# Show site names
site_name_A = get_site_name(SITE_A)
site_name_B = get_site_name(SITE_B)

st.sidebar.markdown("### Monitoring Sites")
st.sidebar.write(f"**Left:** {site_name_A} ({SITE_A})")
st.sidebar.write(f"**Right:** {site_name_B} ({SITE_B})")

# Info message
st.info("🚌 This simulates an e-ink display showing real-time SL **bus departures only**. "
        f"Currently showing: {site_name_A} and {site_name_B}. "
        "Edit SITE_IDS in the script to change sites.")

placeholder = st.empty()
status_placeholder = st.empty()

# Main loop
while True:
    try:
        status_placeholder.text(f"Fetching departures... (refreshes every {refresh_rate}s)")
        
        # Fetch departures from both sites
        departures_A = get_sl_departures(SITE_A, forecast=forecast_time)
        departures_B = get_sl_departures(SITE_B, forecast=forecast_time)
        
        # Draw the screen
        screen = draw_bus_screen(departures_A, departures_B, site_name_A, site_name_B)
        
        # Display
        placeholder.image(screen, caption=f"Simulated E-Ink Display (800x480) - {datetime.now().strftime('%H:%M:%S')}", 
                         use_container_width=True)
        
        status_placeholder.success(f"✅ Last updated: {datetime.now().strftime('%H:%M:%S')} | "
                                  f"Next update in {refresh_rate}s")
        
    except Exception as e:
        status_placeholder.error(f"❌ Error: {str(e)}")
        st.exception(e)
    
    time.sleep(refresh_rate)