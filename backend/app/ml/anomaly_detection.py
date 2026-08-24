"""
EcoPulse Anomaly Detection
Uses Isolation Forest for detecting unusual pollution patterns.

Anomaly detection is numerical and deterministic.
Groq AI is used ONLY to explain anomalies after detection.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.pollution_reading import PollutionReading

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Isolation Forest-based anomaly detection for pollution data."""

    def __init__(self):
        self._models = {}

    async def detect_anomalies(
        self,
        db: AsyncSession,
        location_id: UUID,
        current_reading: Optional[dict] = None,
        lookback_hours: int = 24,
    ) -> list[dict]:
        """
        Detect anomalies in recent pollution data.
        
        Uses Isolation Forest on features: PM2.5, PM10, NO2, CO, SO2, O3.
        
        Returns list of detected anomalies with details.
        """
        from sklearn.ensemble import IsolationForest

        # Fetch recent readings for baseline
        start_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        result = await db.execute(
            select(PollutionReading)
            .where(
                and_(
                    PollutionReading.location_id == location_id,
                    PollutionReading.timestamp >= start_time,
                )
            )
            .order_by(PollutionReading.timestamp)
        )
        readings = result.scalars().all()

        if len(readings) < 20:
            return []

        # Build feature matrix
        features = []
        for r in readings:
            row = [
                r.pm25 or 0,
                r.pm10 or 0,
                r.no2 or 0,
                r.co or 0,
                r.so2 or 0,
                r.o3 or 0,
            ]
            features.append(row)

        X = np.array(features)

        # Train Isolation Forest
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,  # Expect ~5% anomalies
            random_state=42,
        )
        predictions = model.fit_predict(X)
        scores = model.score_samples(X)

        # Identify anomalies
        anomalies = []
        param_names = ["PM2.5", "PM10", "NO2", "CO", "SO2", "O3"]
        param_keys = ["pm25", "pm10", "no2", "co", "so2", "o3"]

        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                reading = readings[i]

                # Calculate which parameter deviated most
                means = np.mean(X, axis=0)
                stds = np.std(X, axis=0)
                stds[stds == 0] = 1  # Avoid division by zero
                z_scores = (X[i] - means) / stds

                max_deviation_idx = np.argmax(np.abs(z_scores))
                max_param = param_names[max_deviation_idx]
                max_param_key = param_keys[max_deviation_idx]
                current_val = X[i][max_deviation_idx]
                baseline_val = means[max_deviation_idx]

                change_pct = ((current_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0

                severity = "LOW"
                if abs(change_pct) > 100:
                    severity = "CRITICAL"
                elif abs(change_pct) > 50:
                    severity = "HIGH"
                elif abs(change_pct) > 25:
                    severity = "MODERATE"

                anomalies.append({
                    "timestamp": reading.timestamp.isoformat(),
                    "parameter": max_param,
                    "parameter_key": max_param_key,
                    "current_value": round(float(current_val), 1),
                    "baseline_value": round(float(baseline_val), 1),
                    "change_percent": round(float(change_pct), 1),
                    "anomaly_score": round(float(score), 4),
                    "severity": severity,
                    "z_score": round(float(z_scores[max_deviation_idx]), 2),
                    "location_id": str(location_id),
                })

        logger.info(f"Anomaly detection: {len(anomalies)} anomalies found in {len(readings)} readings")
        return anomalies

    async def check_reading_anomaly(
        self,
        db: AsyncSession,
        location_id: UUID,
        reading_data: dict,
    ) -> Optional[dict]:
        """
        Quick check if a single new reading is anomalous.
        Uses statistical deviation from recent baseline.
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=6)
        result = await db.execute(
            select(PollutionReading)
            .where(
                and_(
                    PollutionReading.location_id == location_id,
                    PollutionReading.timestamp >= start_time,
                )
            )
            .order_by(desc(PollutionReading.timestamp))
            .limit(50)
        )
        readings = result.scalars().all()

        if len(readings) < 10:
            return None

        # Check each pollutant for significant deviation
        params = {
            "pm25": ("PM2.5", "µg/m³"),
            "pm10": ("PM10", "µg/m³"),
            "no2": ("NO2", "µg/m³"),
            "co": ("CO", "mg/m³"),
            "so2": ("SO2", "µg/m³"),
            "o3": ("O3", "µg/m³"),
        }

        for key, (name, unit) in params.items():
            current = reading_data.get(key)
            if current is None:
                continue

            historical = [getattr(r, key) for r in readings if getattr(r, key) is not None]
            if len(historical) < 5:
                continue

            mean = np.mean(historical)
            std = np.std(historical)

            if std == 0:
                continue

            z = (current - mean) / std

            if abs(z) > 3:  # 3 standard deviations = significant anomaly
                change_pct = ((current - mean) / mean * 100) if mean > 0 else 0
                return {
                    "parameter": name,
                    "parameter_key": key,
                    "current_value": current,
                    "baseline_mean": round(float(mean), 1),
                    "baseline_std": round(float(std), 1),
                    "z_score": round(float(z), 2),
                    "change_percent": round(float(change_pct), 1),
                    "severity": "CRITICAL" if abs(z) > 5 else "HIGH",
                    "unit": unit,
                }

        return None


# Singleton
anomaly_detector = AnomalyDetector()
