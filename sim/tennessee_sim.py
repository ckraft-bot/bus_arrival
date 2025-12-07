import os
import csv
from datetime import datetime
import pytz
import streamlit as st
from dotenv import load_dotenv

# -----------------------------
# Config
# -----------------------------
DATA_DIR = r"C:\Users\Clair\Documents\GitHub\bus_arrival\gtfs_current"

load_dotenv()
STOP_A = os.getenv("CARTA_STOP_CODE_A")
STOP_B = os.getenv("CARTA_STOP_CODE_B") 
ROUTE = os.getenv("CARTA_ROUTE")
tz = pytz.timezone("America/New_York")

# -----------------------------
# Load GTFS Data
# -----------------------------
def load_trips():
    trips = {}
    with open(os.path.join(DATA_DIR, "trips.txt")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["route_id"] == ROUTE:
                trips[row["trip_id"]] = row
    return trips

def load_stop_times():
    stop_times = []
    with open(os.path.join(DATA_DIR, "stop_times.txt")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            stop_times.append(row)
    return stop_times

# -----------------------------
# Next arrivals
# -----------------------------
def next_arrivals(stop_id, limit=5):
    stop_times = load_stop_times()
    trips = load_trips()
    upcoming = []

    for st in stop_times:
        if st["stop_id"] != stop_id:
            continue
        if st["trip_id"] not in trips:
            continue
        try:
            arr_time = datetime.strptime(st["arrival_time"], "%H:%M:%S").time()
        except ValueError:
            continue
        upcoming.append(arr_time)

    upcoming.sort()
    return upcoming[:limit]

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="centered")
st.title("Scheduled Bus Arrival")

def display_arrivals(label, arrivals):
    st.markdown(f"**{'='*20} {label} {'='*20}**")
    if not arrivals:
        st.write("No upcoming buses found.")
    else:
        for t in arrivals:
            st.write(t.strftime("%I:%M %p"))

arrivals_inbound = next_arrivals(STOP_A)
arrivals_outbound = next_arrivals(STOP_B)

display_arrivals(f"Inbound (Stop {STOP_A})", arrivals_inbound)
display_arrivals(f"Outbound (Stop {STOP_B})", arrivals_outbound)
