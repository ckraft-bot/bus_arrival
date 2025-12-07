import os
import csv
from datetime import datetime
import pytz
import streamlit as st
from dotenv import load_dotenv

# -----------------------------
# Config
# -----------------------------
load_dotenv()

DATA_DIR = os.getenv("DATA")
STOP_A = os.getenv("CARTA_STOP_CODE_A")
STOP_B = os.getenv("CARTA_STOP_CODE_B") 
ROUTE = os.getenv("CARTA_ROUTE")
tz = pytz.timezone("America/New_York")

st.set_page_config(layout="centered")

# -----------------------------
# Global styling (Items 1–4)
# -----------------------------
st.markdown("""
<style>
    body {
        background-color: #0A0A0A;
    }
    .main {
        background-color: #0A0A0A;
        color: #F2F2F2;
        font-family: 'Roboto Mono', monospace;
    }
    .board-header {
        font-size: 2rem;
        color: #4DA6FF;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 2px;
    }
    .arrival-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        padding: 0.6rem 0;
        font-size: 1.3rem;
        border-bottom: 1px solid #333;
    }
    .status {
        color: #FFCC00;
        text-align: right;
    }
    .stop-label {
        font-size: 1.5rem;
        margin-top: 2rem;
        text-align: center;
        color: #4DA6FF;
    }

    /* Updating animation */
    @keyframes blink {
        0% {opacity: 0;}
        50% {opacity: 1;}
        100% {opacity: 0;}
    }
    .dot1 { animation: blink 1s infinite; }
    .dot2 { animation: blink 1s infinite 0.2s; }
    .dot3 { animation: blink 1s infinite 0.4s; }
</style>
""", unsafe_allow_html=True)

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

    for st_row in stop_times:
        if st_row["stop_id"] != stop_id:
            continue
        if st_row["trip_id"] not in trips:
            continue
        try:
            arr_time = datetime.strptime(st_row["arrival_time"], "%H:%M:%S").time()
        except ValueError:
            continue
        upcoming.append(arr_time)

    upcoming.sort()
    return upcoming[:limit]

# -----------------------------
# Display board rows
# -----------------------------
def display_arrivals(label, arrivals):
    st.markdown(f"<div class='stop-label'>STOP {label}</div>", unsafe_allow_html=True)

    if not arrivals:
        st.write("No upcoming buses found.")
        return

    st.markdown(
        "<div class='arrival-row'><strong>TIME</strong><strong>ROUTE</strong><strong>STATUS</strong></div>",
        unsafe_allow_html=True
    )

    for t in arrivals:
        time_str = t.strftime("%I:%M %p")
        st.markdown(
            f"""
            <div class='arrival-row'>
                <div>{time_str}</div>
                <div>{ROUTE}</div>
                <div class='status'>DELAYED</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# UI
# -----------------------------
st.markdown("<div class='board-header'>TENNESSEE BUS SCHEDULE</div>", unsafe_allow_html=True)

arrivals_inbound = next_arrivals(STOP_A)
arrivals_outbound = next_arrivals(STOP_B)

display_arrivals(STOP_A, arrivals_inbound)
display_arrivals(STOP_B, arrivals_outbound)

st.markdown("""
    <div style='text-align:center;margin-top:20px;color:#4DA6FF;font-family:monospace;'>
        Updating<span class="dot1">.</span><span class="dot2">.</span><span class="dot3">.</span>
    </div>
""", unsafe_allow_html=True)
