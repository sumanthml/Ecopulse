"""
EcoPulse Prediction Service
ML-based pollution forecasting using Scikit-learn.

Models:
    - RandomForestRegressor
    - GradientBoostingRegressor

Forecast targets: PM2.5, AQI
Forecast horizons: 1h, 3h, 6h

Metrics: MAE, RMSE, R²
"""
import logging
import pickle
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.pollution_reading import PollutionReading
from app.models.aqi_record import AQIRecord

logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = Path(__file__).parent.parent.parent / "models_cache"
MODEL_DIR.mkdir(exist_ok=True)


class PredictionService:
    """ML prediction service for pollution forecasting."""

    def __init__(self):
        self.models = {}
        self._load_cached_models()

    def _load_cached_models(self):
        """Load previously trained models from disk."""
        for model_file in MODEL_DIR.glob("*.pkl"):
            try:
                with open(model_file, "rb") as f:
                    self.models[model_file.stem] = pickle.load(f)
                logger.info(f"Loaded cached model: {model_file.stem}")
            except Exception as e:
                logger.warning(f"Failed to load model {model_file.stem}: {e}")

    async def train_model(
        self,
        db: AsyncSession,
        location_id: uuid.UUID,
        target: str = "pm25",
        days: int = 30,
    ) -> dict:
        """
        Train prediction models for a specific location and target.
        
        Pipeline:
            Historical readings → Feature engineering → Training dataset →
            Model training → Validation → Saved model
        
        Args:
            db: Database session
            location_id: Location UUID
            target: Target variable ('pm25' or 'aqi')
            days: Number of days of historical data to use
        
        Returns:
            Training metrics (MAE, RMSE, R²)
        """
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        # Fetch training data
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            select(PollutionReading)
            .where(
                and_(
                    PollutionReading.location_id == location_id,
                    PollutionReading.timestamp >= start_date,
                )
            )
            .order_by(PollutionReading.timestamp)
        )
        readings = result.scalars().all()

        if len(readings) < 50:
            return {"error": "Insufficient data for training (need at least 50 readings)"}

        # Feature engineering
        X, y = self._engineer_features(readings, target)

        if len(X) < 30:
            return {"error": "Insufficient valid features after engineering"}

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train models
        models = {
            "random_forest": RandomForestRegressor(
                n_estimators=100, max_depth=15, random_state=42, n_jobs=-1
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
            ),
        }

        results = {}
        best_model = None
        best_r2 = -float("inf")

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            results[name] = {
                "mae": round(float(mae), 4),
                "rmse": round(float(rmse), 4),
                "r2": round(float(r2), 4),
            }

            if r2 > best_r2:
                best_r2 = r2
                best_model = (name, model)

            logger.info(f"Model {name}: MAE={mae:.4f}, RMSE={rmse:.4f}, R²={r2:.4f}")

        # Save best model
        if best_model:
            model_key = f"{location_id}_{target}"
            self.models[model_key] = {
                "model": best_model[1],
                "name": best_model[0],
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "metrics": results[best_model[0]],
                "feature_count": X.shape[1],
            }

            model_path = MODEL_DIR / f"{model_key}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.models[model_key], f)

        return {
            "target": target,
            "location_id": str(location_id),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "models": results,
            "best_model": best_model[0] if best_model else None,
            "best_metrics": results.get(best_model[0]) if best_model else None,
        }

    async def predict(
        self,
        db: AsyncSession,
        location_id: uuid.UUID,
        target: str = "pm25",
        horizons: list[int] = [1, 3, 6],
    ) -> dict:
        """
        Generate predictions for specified forecast horizons.
        
        Args:
            horizons: List of hours to forecast (e.g. [1, 3, 6])
        
        Returns:
            Predictions with confidence and model info
        """
        model_key = f"{location_id}_{target}"
        if model_key not in self.models:
            return {
                "error": "No trained model available. Train a model first using POST /api/predictions/train",
                "target": target,
            }

        model_info = self.models[model_key]
        model = model_info["model"]

        # Get recent readings for features
        result = await db.execute(
            select(PollutionReading)
            .where(PollutionReading.location_id == location_id)
            .order_by(desc(PollutionReading.timestamp))
            .limit(24)
        )
        recent = list(reversed(result.scalars().all()))

        if len(recent) < 5:
            return {"error": "Insufficient recent data for prediction"}

        predictions = []
        for horizon in horizons:
            features = self._extract_prediction_features(recent, horizon)
            if features is not None:
                pred_value = float(model.predict(features.reshape(1, -1))[0])
                predictions.append({
                    "horizon_hours": horizon,
                    "predicted_value": round(max(0, pred_value), 2),
                    "target": target,
                    "unit": "µg/m³" if target == "pm25" else "",
                    "predicted_at": datetime.now(timezone.utc).isoformat(),
                    "forecast_time": (datetime.now(timezone.utc) + timedelta(hours=horizon)).isoformat(),
                })

        return {
            "location_id": str(location_id),
            "target": target,
            "model": model_info["name"],
            "model_metrics": model_info["metrics"],
            "trained_at": model_info["trained_at"],
            "predictions": predictions,
            "disclaimer": "PREDICTED values — not actual measurements",
        }

    def _engineer_features(self, readings, target: str):
        """
        Create feature matrix from readings.
        
        Features:
            - Previous pollutant values (lag 1, 2, 3)
            - Rolling averages (3, 6, 12 readings)
            - Temperature, humidity, wind speed, pressure
            - Hour of day (sin/cos encoded)
            - Day of week (sin/cos encoded)
        """
        data = []
        for r in readings:
            row = {
                "pm25": r.pm25 or 0,
                "pm10": r.pm10 or 0,
                "no2": r.no2 or 0,
                "so2": r.so2 or 0,
                "co": r.co or 0,
                "o3": r.o3 or 0,
                "temperature": r.temperature or 25,
                "humidity": r.humidity or 50,
                "wind_speed": r.wind_speed or 2,
                "pressure": r.pressure or 1013,
                "hour_sin": np.sin(2 * np.pi * r.timestamp.hour / 24),
                "hour_cos": np.cos(2 * np.pi * r.timestamp.hour / 24),
                "dow_sin": np.sin(2 * np.pi * r.timestamp.weekday() / 7),
                "dow_cos": np.cos(2 * np.pi * r.timestamp.weekday() / 7),
            }
            data.append(row)

        if len(data) < 10:
            return np.array([]), np.array([])

        # Create lag features and rolling averages
        features = []
        targets = []

        for i in range(6, len(data)):
            row = list(data[i].values())

            # Lag features
            for lag in [1, 2, 3]:
                row.append(data[i - lag].get(target, 0))

            # Rolling averages
            for window in [3, 6]:
                vals = [data[i - j].get(target, 0) for j in range(window)]
                row.append(np.mean(vals))

            features.append(row)
            targets.append(data[i].get(target, 0))

        return np.array(features), np.array(targets)

    def _extract_prediction_features(self, readings, horizon: int):
        """Extract features for a single prediction."""
        if len(readings) < 6:
            return None

        latest = readings[-1]
        now = datetime.now(timezone.utc)
        future_hour = (now + timedelta(hours=horizon)).hour
        future_dow = (now + timedelta(hours=horizon)).weekday()

        features = [
            latest.pm25 or 0,
            latest.pm10 or 0,
            latest.no2 or 0,
            latest.so2 or 0,
            latest.co or 0,
            latest.o3 or 0,
            latest.temperature or 25,
            latest.humidity or 50,
            latest.wind_speed or 2,
            latest.pressure or 1013,
            np.sin(2 * np.pi * future_hour / 24),
            np.cos(2 * np.pi * future_hour / 24),
            np.sin(2 * np.pi * future_dow / 7),
            np.cos(2 * np.pi * future_dow / 7),
        ]

        # Lag features
        for lag in [1, 2, 3]:
            idx = max(0, len(readings) - 1 - lag)
            features.append(getattr(readings[idx], "pm25", 0) or 0)

        # Rolling averages
        for window in [3, 6]:
            vals = [getattr(readings[max(0, len(readings) - 1 - j)], "pm25", 0) or 0 for j in range(window)]
            features.append(np.mean(vals))

        return np.array(features)


# Singleton
prediction_service = PredictionService()
