import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

import streamlit as st

load_dotenv()

WIDTH = 800
HEIGHT = 480

def get_bus_arrival(LTA_API_KEY, bus_stop_code):
    url = f"https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival?BusStopCode={bus_stop_code}"
    headers = {
        "AccountKey": LTA_API_KEY,
        "accept": "application/json"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return []

    data = r.json()
    services = data.get("Services", [])
    bus_info = []

    for svc in services:
        service_no = svc["ServiceNo"]
        arrival_times = []

        for key in ["NextBus", "NextBus2", "NextBus3"]:
            eta = svc.get(key, {}).get("EstimatedArrival")
            if eta:
                eta_dt = datetime.strptime(eta, "%Y-%m-%dT%H:%M:%S%z")
                diff = (eta_dt - datetime.now(eta_dt.tzinfo)).total_seconds() / 60
                arrival_times.append(max(round(diff), 0))

        if arrival_times:
            bus_info.append((service_no, arrival_times))

    return bus_info


def draw_bus_screen(bus_info_A, bus_info_B):
    img = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # font = ImageFont.truetype("OpenSans-Bold.ttf", 32) # doesnt exist
    font = ImageFont.truetype("arialbd.ttf", 32)

    y = 20
    col_offset = WIDTH // 2

    draw.text((120, y), "Downstairs", font=font, fill=0)

    for svc, times in bus_info_A:
        draw.rectangle((20, y + 50, 180, y + 110), fill=0)
        draw.text((50, y + 58), svc, font=font, fill=255)
        draw.text((220, y + 55), " | ".join(map(str, times)), font=font, fill=0)
        y += 70

    y = 20
    draw.text((120 + col_offset, y), "Opposite", font=font, fill=0)

    for svc, times in bus_info_B:
        draw.rectangle((20 + col_offset, y + 50, 180 + col_offset, y + 110), fill=0)
        draw.text((50 + col_offset, y + 58), svc, font=font, fill=255)
        draw.text((220 + col_offset, y + 55), " | ".join(map(str, times)), font=font, fill=0)
        y += 70

    return img

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="centered")

st.title("Bus Arrival Simulator")

LTA_API_KEY = os.getenv("LTA_API_KEY")
STOP_A = os.getenv("BUS_STOP_CODE_A")
STOP_B = os.getenv("BUS_STOP_CODE_B")

refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 10, 120, 30)

placeholder = st.empty()

while True:
    A = get_bus_arrival(LTA_API_KEY, STOP_A)
    B = get_bus_arrival(LTA_API_KEY, STOP_B)

    screen = draw_bus_screen(A, B)

    placeholder.image(screen, caption="Simulated E-Ink Display", use_container_width=True)

    time.sleep(refresh_rate)
