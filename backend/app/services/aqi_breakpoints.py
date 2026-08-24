"""
EcoPulse AQI Breakpoint Configuration
Standard: US EPA (United States Environmental Protection Agency)

AQI Breakpoints define the relationship between pollutant concentrations
and the AQI index value. Each pollutant has concentration ranges (breakpoints)
that map to AQI ranges.

Reference: https://www.airnow.gov/aqi/aqi-basics/
EPA Technical Assistance Document for the Reporting of Daily Air Quality (2018)

IMPORTANT: This implements the US EPA AQI standard only.
Do not claim universal AQI compatibility.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Breakpoint:
    """A single AQI breakpoint range."""
    c_low: float    # Concentration low
    c_high: float   # Concentration high
    i_low: int      # AQI low
    i_high: int     # AQI high


# ── AQI Category Definitions ──

AQI_CATEGORIES = [
    {"min": 0, "max": 50, "label": "Good", "color": "#00e400"},
    {"min": 51, "max": 100, "label": "Moderate", "color": "#ffff00"},
    {"min": 101, "max": 150, "label": "Unhealthy for Sensitive Groups", "color": "#ff7e00"},
    {"min": 151, "max": 200, "label": "Unhealthy", "color": "#ff0000"},
    {"min": 201, "max": 300, "label": "Very Unhealthy", "color": "#8f3f97"},
    {"min": 301, "max": 500, "label": "Hazardous", "color": "#7e0023"},
]


def get_aqi_category(aqi: int) -> str:
    """Get the AQI category label for a given AQI value."""
    for cat in AQI_CATEGORIES:
        if cat["min"] <= aqi <= cat["max"]:
            return cat["label"]
    if aqi > 500:
        return "Hazardous"
    return "Unknown"


def get_aqi_color(aqi: int) -> str:
    """Get the display color for a given AQI value."""
    for cat in AQI_CATEGORIES:
        if cat["min"] <= aqi <= cat["max"]:
            return cat["color"]
    if aqi > 500:
        return "#7e0023"
    return "#999999"


# ── PM2.5 Breakpoints (µg/m³, 24-hour average) ──
PM25_BREAKPOINTS = [
    Breakpoint(0.0, 12.0, 0, 50),
    Breakpoint(12.1, 35.4, 51, 100),
    Breakpoint(35.5, 55.4, 101, 150),
    Breakpoint(55.5, 150.4, 151, 200),
    Breakpoint(150.5, 250.4, 201, 300),
    Breakpoint(250.5, 350.4, 301, 400),
    Breakpoint(350.5, 500.4, 401, 500),
]

# ── PM10 Breakpoints (µg/m³, 24-hour average) ──
PM10_BREAKPOINTS = [
    Breakpoint(0, 54, 0, 50),
    Breakpoint(55, 154, 51, 100),
    Breakpoint(155, 254, 101, 150),
    Breakpoint(255, 354, 151, 200),
    Breakpoint(355, 424, 201, 300),
    Breakpoint(425, 504, 301, 400),
    Breakpoint(505, 604, 401, 500),
]

# ── CO Breakpoints (mg/m³, 8-hour average) ──
# EPA uses ppm, converted: 1 ppm CO = ~1.145 mg/m³ at STP
CO_BREAKPOINTS = [
    Breakpoint(0.0, 5.04, 0, 50),      # ~4.4 ppm
    Breakpoint(5.05, 10.94, 51, 100),   # ~9.5 ppm
    Breakpoint(10.95, 14.94, 101, 150), # ~13 ppm
    Breakpoint(14.95, 17.94, 151, 200), # ~15.4 ppm
    Breakpoint(17.95, 35.44, 201, 300), # ~30.4 ppm
    Breakpoint(35.45, 46.94, 301, 400), # ~40.4 ppm
    Breakpoint(46.95, 57.94, 401, 500), # ~50.4 ppm
]

# ── NO2 Breakpoints (µg/m³, 1-hour average) ──
# EPA uses ppb, converted: 1 ppb NO2 = ~1.88 µg/m³ at STP
NO2_BREAKPOINTS = [
    Breakpoint(0, 100, 0, 50),       # ~53 ppb
    Breakpoint(101, 188, 51, 100),   # ~100 ppb
    Breakpoint(189, 677, 101, 150),  # ~360 ppb
    Breakpoint(678, 1221, 151, 200), # ~650 ppb
    Breakpoint(1222, 2349, 201, 300),# ~1250 ppb
    Breakpoint(2350, 3101, 301, 400),# ~1650 ppb
    Breakpoint(3102, 3853, 401, 500),# ~2050 ppb
]

# ── SO2 Breakpoints (µg/m³, 1-hour average) ──
# EPA uses ppb, converted: 1 ppb SO2 = ~2.62 µg/m³ at STP
SO2_BREAKPOINTS = [
    Breakpoint(0, 93, 0, 50),        # ~35 ppb
    Breakpoint(94, 197, 51, 100),    # ~75 ppb
    Breakpoint(198, 487, 101, 150),  # ~186 ppb
    Breakpoint(488, 797, 151, 200),  # ~304 ppb
    Breakpoint(798, 1583, 201, 300), # ~604 ppb
    Breakpoint(1584, 2107, 301, 400),# ~804 ppb
    Breakpoint(2108, 2631, 401, 500),# ~1004 ppb
]

# ── O3 Breakpoints (µg/m³, 8-hour average) ──
# EPA uses ppm, converted: 1 ppm O3 = ~1960 µg/m³ at STP
O3_BREAKPOINTS = [
    Breakpoint(0, 108, 0, 50),       # ~0.054 ppm
    Breakpoint(109, 140, 51, 100),   # ~0.070 ppm
    Breakpoint(141, 170, 101, 150),  # ~0.085 ppm
    Breakpoint(171, 210, 151, 200),  # ~0.105 ppm
    Breakpoint(211, 400, 201, 300),  # ~0.200 ppm
    Breakpoint(401, 504, 301, 400),  # not standard — extended range
    Breakpoint(505, 604, 401, 500),  # not standard — extended range
]


# ── Pollutant Configuration Map ──

POLLUTANT_CONFIG = {
    "pm25": {
        "name": "PM2.5",
        "unit": "µg/m³",
        "breakpoints": PM25_BREAKPOINTS,
        "description": "Fine Particulate Matter (diameter ≤ 2.5 µm)",
    },
    "pm10": {
        "name": "PM10",
        "unit": "µg/m³",
        "breakpoints": PM10_BREAKPOINTS,
        "description": "Coarse Particulate Matter (diameter ≤ 10 µm)",
    },
    "co": {
        "name": "CO",
        "unit": "mg/m³",
        "breakpoints": CO_BREAKPOINTS,
        "description": "Carbon Monoxide",
    },
    "no2": {
        "name": "NO2",
        "unit": "µg/m³",
        "breakpoints": NO2_BREAKPOINTS,
        "description": "Nitrogen Dioxide",
    },
    "so2": {
        "name": "SO2",
        "unit": "µg/m³",
        "breakpoints": SO2_BREAKPOINTS,
        "description": "Sulfur Dioxide",
    },
    "o3": {
        "name": "O3",
        "unit": "µg/m³",
        "breakpoints": O3_BREAKPOINTS,
        "description": "Ozone",
    },
}


# ── Alert Thresholds (configurable) ──

ALERT_THRESHOLDS = {
    "pm25": [
        {"threshold": 35.5, "severity": "MODERATE", "label": "PM2.5 exceeds moderate level"},
        {"threshold": 55.5, "severity": "HIGH", "label": "PM2.5 unhealthy level"},
        {"threshold": 150.5, "severity": "CRITICAL", "label": "PM2.5 very unhealthy level"},
    ],
    "pm10": [
        {"threshold": 155, "severity": "MODERATE", "label": "PM10 exceeds moderate level"},
        {"threshold": 255, "severity": "HIGH", "label": "PM10 unhealthy level"},
        {"threshold": 355, "severity": "CRITICAL", "label": "PM10 very unhealthy level"},
    ],
    "no2": [
        {"threshold": 101, "severity": "MODERATE", "label": "NO2 exceeds moderate level"},
        {"threshold": 189, "severity": "HIGH", "label": "NO2 unhealthy level"},
    ],
    "so2": [
        {"threshold": 94, "severity": "MODERATE", "label": "SO2 exceeds moderate level"},
        {"threshold": 198, "severity": "HIGH", "label": "SO2 unhealthy level"},
    ],
    "co": [
        {"threshold": 5.05, "severity": "MODERATE", "label": "CO exceeds moderate level"},
        {"threshold": 10.95, "severity": "HIGH", "label": "CO unhealthy level"},
    ],
    "o3": [
        {"threshold": 109, "severity": "MODERATE", "label": "O3 exceeds moderate level"},
        {"threshold": 171, "severity": "HIGH", "label": "O3 unhealthy level"},
    ],
    "aqi": [
        {"threshold": 101, "severity": "MODERATE", "label": "AQI unhealthy for sensitive groups"},
        {"threshold": 151, "severity": "HIGH", "label": "AQI unhealthy"},
        {"threshold": 201, "severity": "CRITICAL", "label": "AQI very unhealthy"},
        {"threshold": 301, "severity": "CRITICAL", "label": "AQI hazardous"},
    ],
}
