s# SL Bus Arrival Display

A real-time public transport departure board for Stockholm's SL network, inspired by the [Singapore bus_arrival project](https://github.com/awesomelionel/singapore-bus-timing-edisplay).

This project displays real-time departure information from SL (Storstockholms Lokaltrafik) using Trafiklab's open APIs.

## Features

- 🚌 Real-time departure information for buses
- 📍 Monitor multiple stops simultaneously  
- ⏱️ Shows countdown timers (e.g., "5 min", "Nu")
- ⚠️ Displays service disruptions and deviations
- 🔄 Auto-refreshing display
- 🆓 **No API key required** - uses SL's public Transport API

## Requirements

- Python 3.7+
- Internet connection

## Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd bus_arrival_sl
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your sites (optional):
   ```bash
   cp .env.example .env
   # Edit .env to set your preferred site IDs
   ```

## Configuration

The application can be configured via environment variables or a `.env` file:

### Site IDs

You need to find the Site IDs for your desired stops. 

**Option 1: Browse the full list**
Visit the SL sites endpoint: https://transport.integration.sl.se/v1/sites

**Option 2: Common Stockholm sites**
- 9192 = Slussen
- 9001 = T-Centralen  
- 1079 = Odenplan
- 9180 = Kungsträdgården
- 9189 = Fridhemsplan
- 9193 = Gamla Stan

### Environment Variables

```bash
# Site IDs to monitor (comma-separated)
SITE_IDS=9192,9001
# Refresh interval in seconds (default: 60)
REFRESH_INTERVAL=60
```

## Usage

### Basic Usage

```bash
python3 app/main.py
```

### With Custom Sites

```bash
# Set site IDs directly
SITE_IDS=9192,9001 python3 app/main.py

# Or use environment variables
export SITE_IDS=9192,9001
export REFRESH_INTERVAL=30
python3 app/main.py
```

## Example Output

```
================================================================================
SL BUSS AVGÅNGAR - 2026-01-04 17:18:55
================================================================================

📍 Slussen (Site ID: 9192)
--------------------------------------------------------------------------------
   🚌 Line  71T → Henriksdalsviadukten       357 min
   🚌 Line    2 → Norrtull                   357 min
   🚌 Line  444 → Västra Orminge             358 min
   🚌 Line    3 → Södersjukhuset             358 min
   🚌 Line   53 → Karolinska institutet      359 min
   🚌 Line    3 → Karolinska sjukhuset       360 min
   🚌 Line  402 → Nacka Forum                361 min
   🚌 Line  414 → Orminge centrum            361 min
   🚌 Line    2 → Sofia                      361 min
   🚌 Line  474 → Hemmesta                   362 min

📍 T-Centralen (Site ID: 9001)
--------------------------------------------------------------------------------
   🚌 Line   69 → Centralen                  363 min
   🚌 Line   65 → Skeppsholmen               367 min
   🚌 Line   65 → Hornsberg                  368 min
   🚌 Line   69 → Djurgårdsbrunn             387 min

   ⚠️  Deviations:
      • Korta tåg. Gå mot mitten av plattformen.
```

## API Information

This project uses the **SL Transport API** from Trafiklab, which provides:

- Real-time departures and arrivals
- Line information
- Service disruptions
- Stop locations

### API Details

- **No API key required** for the Transport API
- Base URL: `https://transport.integration.sl.se/v1`
- Documentation: https://www.trafiklab.se/api/our-apis/sl/transport/

### Key Concepts

- **Site**: A grouping of stop areas (e.g., "T-Centralen")
- **StopArea**: A grouping of stop points with same traffic type
- **StopPoint**: A specific platform/quay where vehicles stop

## Running as a Service

To run this automatically at startup on Linux systems:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/sl_display.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=SL Bus Arrival Display Service
   After=multi-user.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/bus_arrival_sl/app/main.py
   WorkingDirectory=/path/to/bus_arrival_sl/
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi
   Environment="SITE_IDS=9192,9001"

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable sl_display.service
   sudo systemctl start sl_display.service
   sudo systemctl status sl_display.service
   ```

## E-Ink Display Integration

This project is designed to work with e-ink displays similar to the original Singapore project. To integrate with a Waveshare e-ink display:

1. Install the Waveshare e-Paper library:
   ```bash
   git clone https://github.com/waveshare/e-Paper.git
   cp -r e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd lib/
   ```

2. Modify `app/main.py` to use the e-ink display instead of console output

3. See the original [Singaporean bus arrival project](https://github.com/awesomelionel/singapore-bus-timing-edisplay) for e-ink display examples

## Hardware Setup (Optional)

For a physical departure board display:

1. **Raspberry Pi Zero W** (or any Raspberry Pi)
2. **Waveshare 7.5" e-Paper HAT** (or similar e-ink display)
3. **5V 3A Power Supply**
4. **Picture Frame** (IKEA Ribba or 3D-printed case)

## Differences from Singapore Version

This Swedish version differs from the original Singapore project:

- ✅ **No API key needed** - SL Transport API is freely accessible
- Uses SL's Transport API instead of Singapore's LTA DataMall
- 🚇 Supports multiple transport modes (metro, bus, train, tram, ferry) but this program will filter to only buses
- 📍 Uses Site IDs instead of bus stop codes
- ⏱️ Real-time countdown in minutes
- ⚠️ Displays service disruptions

## API Rate Limiting

The SL Transport API doesn't require an API key, but you should:

- Not make excessive requests
- Keep refresh intervals reasonable (30-60 seconds minimum)
- Cache data when appropriate
- Consider using GTFS Regional for bulk data needs

## Troubleshooting

### Site ID Not Found
- Verify your site ID at https://transport.integration.sl.se/v1/sites
- Make sure you're using the numeric ID (not the GID)

### No Departures Shown
- Check if the site has active service at the current time
- Try increasing the forecast parameter (default is 30 minutes)
- Verify your internet connection

### Connection Errors
- Check your internet connection
- The API may be temporarily unavailable - check https://status.trafiklab.se

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Resources

- [Trafiklab SL Transport API](https://www.trafiklab.se/api/our-apis/sl/transport/)
- [Trafiklab Documentation](https://www.trafiklab.se/docs/)
- [Original Singapore Project](https://github.com/awesomelionel/singapore-bus-timing-edisplay)
- [SL Journey Planner](https://sl.se)

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- Inspired by [awesomelionel/singapore-bus-timing-edisplay](https://github.com/awesomelionel/singapore-bus-timing-edisplay)
- Data provided by [Trafiklab](https://www.trafiklab.se/)
- Transport services by [SL](https://sl.se)