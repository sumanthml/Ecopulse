"""
EcoPulse AI Prompt Templates
Safe, responsible environmental intelligence prompts.

Safety rules:
    - Do NOT diagnose medical conditions
    - Do NOT claim certainty about pollution causes
    - Do NOT invent sensor readings
    - Use hedging language: "may indicate", "suggests", "is consistent with"
"""

SYSTEM_PROMPT = """You are EcoPulse Environmental Intelligence, an AI assistant that provides 
environmental analysis and recommendations based on measured air quality data.

CRITICAL RULES:
1. You ONLY analyze data that has been provided to you. NEVER invent readings.
2. Use cautious language: "may indicate", "suggests", "is consistent with", "could be associated with"
3. Do NOT diagnose medical conditions or provide medical advice
4. Do NOT claim certainty about pollution causes — suggest possible explanations
5. Always recommend consulting local environmental authorities for official guidance
6. Frame recommendations around general well-being, not medical treatment
7. Acknowledge data limitations when relevant
8. All numerical values in your analysis come from actual measurements — cite them directly"""


def environmental_summary_prompt(data: dict) -> str:
    """Generate prompt for environmental summary/insight."""
    return f"""Analyze the following environmental measurements and provide a concise environmental intelligence summary.

MEASURED DATA:
- Location: {data.get('location', 'Unknown')}
- Current AQI: {data.get('current_aqi', 'N/A')} ({data.get('aqi_category', 'N/A')})
- Previous AQI (2h ago): {data.get('previous_aqi', 'N/A')}
- AQI Change: {data.get('aqi_change_percent', 'N/A')}%
- Dominant Pollutant: {data.get('dominant_pollutant', 'N/A')}
- PM2.5: {data.get('pm25_current', 'N/A')} µg/m³ (2h avg: {data.get('pm25_average_2h', 'N/A')})
- PM10: {data.get('pm10_current', 'N/A')} µg/m³
- NO2: {data.get('no2_current', 'N/A')} µg/m³
- SO2: {data.get('so2_current', 'N/A')} µg/m³
- O3: {data.get('o3_current', 'N/A')} µg/m³
- CO: {data.get('co_current', 'N/A')} mg/m³
- Temperature: {data.get('temperature', 'N/A')}°C
- Humidity: {data.get('humidity', 'N/A')}%
- Wind Speed: {data.get('wind_speed', 'N/A')} m/s
- Peak Period: {data.get('peak_period', 'N/A')}

Provide:
1. A brief assessment of current conditions (2-3 sentences)
2. Possible contributing factors (use cautious language)
3. Short-term outlook based on current trends
4. General recommendations for the public

Keep the response under 200 words. Be factual and cite the measured values."""


def daily_report_prompt(data: dict) -> str:
    """Generate prompt for daily environmental report."""
    return f"""Generate a daily environmental report based on these measurements.

DAILY SUMMARY FOR: {data.get('location', 'Unknown')}
DATE: {data.get('date', 'Today')}

STATISTICS:
- Average AQI: {data.get('avg_aqi', 'N/A')}
- Maximum AQI: {data.get('max_aqi', 'N/A')}  
- Minimum AQI: {data.get('min_aqi', 'N/A')}
- Dominant Pollutant: {data.get('dominant_pollutant', 'N/A')}
- Avg PM2.5: {data.get('avg_pm25', 'N/A')} µg/m³
- Max PM2.5: {data.get('max_pm25', 'N/A')} µg/m³
- Avg PM10: {data.get('avg_pm10', 'N/A')} µg/m³
- Avg Temperature: {data.get('avg_temp', 'N/A')}°C
- Peak Pollution Period: {data.get('peak_period', 'N/A')}
- Lowest Pollution Period: {data.get('lowest_period', 'N/A')}
- Total Readings: {data.get('total_readings', 'N/A')}
- Alerts Triggered: {data.get('alerts_count', 0)}
- Anomalies Detected: {data.get('anomalies_count', 0)}

Structure the report with:
1. Executive Summary (2-3 sentences)
2. Air Quality Overview
3. Notable Events / Anomalies
4. Trend Analysis
5. Recommendations

Keep under 300 words. Use measured values. Acknowledge any data gaps."""


def anomaly_explanation_prompt(data: dict) -> str:
    """Generate prompt for anomaly explanation."""
    return f"""An anomaly has been detected in environmental monitoring data. Provide a brief explanation.

ANOMALY DETAILS:
- Location: {data.get('location', 'Unknown')}
- Parameter: {data.get('parameter', 'N/A')}
- Current Value: {data.get('current_value', 'N/A')}
- Recent Baseline: {data.get('baseline_value', 'N/A')}
- Change: {data.get('change_percent', 'N/A')}%
- Time: {data.get('timestamp', 'N/A')}
- Temperature: {data.get('temperature', 'N/A')}°C
- Wind Speed: {data.get('wind_speed', 'N/A')} m/s

Provide:
1. What this anomaly may indicate (use cautious language)
2. Possible explanations (list 2-3 possibilities)
3. Whether this is consistent with known pollution patterns
4. Recommended monitoring actions

Keep under 150 words."""


def recommendation_prompt(data: dict) -> str:
    """Generate prompt for health/activity recommendations."""
    return f"""Based on current air quality conditions, provide general activity recommendations.

CURRENT CONDITIONS:
- Location: {data.get('location', 'Unknown')}
- AQI: {data.get('current_aqi', 'N/A')} ({data.get('aqi_category', 'N/A')})
- PM2.5: {data.get('pm25', 'N/A')} µg/m³
- Temperature: {data.get('temperature', 'N/A')}°C

Provide 3-4 brief, actionable recommendations. 
Do NOT provide medical advice. 
Focus on activity timing and general well-being.
Keep under 100 words."""
