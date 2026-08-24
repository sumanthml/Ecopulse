"""
EcoPulse AQI Calculation Service
Standard: US EPA AQI

Implements the AQI calculation formula:
    I = ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C - BP_lo) + I_lo

Where:
    I  = the AQI sub-index for the pollutant
    C  = the pollutant concentration (truncated)
    BP_hi / BP_lo = concentration breakpoints
    I_hi / I_lo   = corresponding AQI breakpoints

The overall AQI is the maximum sub-index across all pollutants.
The pollutant with the highest sub-index is the "dominant pollutant".
"""

import logging
from typing import Optional
from app.services.aqi_breakpoints import (
    POLLUTANT_CONFIG,
    Breakpoint,
    get_aqi_category,
    get_aqi_color,
)

logger = logging.getLogger(__name__)


def calculate_sub_index(concentration: float, breakpoints: list[Breakpoint]) -> Optional[int]:
    """
    Calculate the AQI sub-index for a single pollutant.

    Uses linear interpolation between breakpoints:
        I = ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C - BP_lo) + I_lo

    Args:
        concentration: The pollutant concentration value.
        breakpoints: List of Breakpoint objects for this pollutant.

    Returns:
        The calculated sub-index (integer), or None if out of range.
    """
    if concentration < 0:
        return None

    for bp in breakpoints:
        if bp.c_low <= concentration <= bp.c_high:
            # Linear interpolation
            aqi = ((bp.i_high - bp.i_low) / (bp.c_high - bp.c_low)) * (concentration - bp.c_low) + bp.i_low
            return round(aqi)

    # Concentration exceeds all breakpoints — extrapolate from last range
    if concentration > breakpoints[-1].c_high:
        last = breakpoints[-1]
        aqi = ((last.i_high - last.i_low) / (last.c_high - last.c_low)) * (concentration - last.c_low) + last.i_low
        return min(round(aqi), 999)  # Cap at 999

    return None


def calculate_aqi(
    pm25: Optional[float] = None,
    pm10: Optional[float] = None,
    co: Optional[float] = None,
    no2: Optional[float] = None,
    so2: Optional[float] = None,
    o3: Optional[float] = None,
) -> dict:
    """
    Calculate the overall AQI from available pollutant concentrations.

    The AQI is the maximum sub-index across all available pollutants.
    At least one pollutant must be provided.

    Args:
        pm25: PM2.5 concentration in µg/m³
        pm10: PM10 concentration in µg/m³
        co: CO concentration in mg/m³
        no2: NO2 concentration in µg/m³
        so2: SO2 concentration in µg/m³
        o3: O3 concentration in µg/m³

    Returns:
        dict with keys: aqi, category, dominant_pollutant, sub_indices, color
    """
    pollutant_values = {
        "pm25": pm25,
        "pm10": pm10,
        "co": co,
        "no2": no2,
        "so2": so2,
        "o3": o3,
    }

    sub_indices = {}

    for key, value in pollutant_values.items():
        if value is not None and key in POLLUTANT_CONFIG:
            config = POLLUTANT_CONFIG[key]
            sub_index = calculate_sub_index(value, config["breakpoints"])
            if sub_index is not None:
                sub_indices[config["name"]] = {
                    "value": sub_index,
                    "concentration": value,
                    "unit": config["unit"],
                }

    if not sub_indices:
        return {
            "aqi": 0,
            "category": "Unknown",
            "dominant_pollutant": None,
            "sub_indices": {},
            "color": "#999999",
        }

    # Overall AQI = maximum sub-index
    dominant_name = max(sub_indices, key=lambda k: sub_indices[k]["value"])
    overall_aqi = sub_indices[dominant_name]["value"]
    category = get_aqi_category(overall_aqi)
    color = get_aqi_color(overall_aqi)

    logger.debug(f"AQI calculated: {overall_aqi} ({category}), dominant: {dominant_name}")

    return {
        "aqi": overall_aqi,
        "category": category,
        "dominant_pollutant": dominant_name,
        "sub_indices": sub_indices,
        "color": color,
    }


def classify_aqi(aqi: int) -> dict:
    """Get full classification details for an AQI value."""
    return {
        "aqi": aqi,
        "category": get_aqi_category(aqi),
        "color": get_aqi_color(aqi),
    }
