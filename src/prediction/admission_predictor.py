"""
Admission prediction models for Hospital Patient Analytics
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import joblib

try:
    from ..config import RANDOM_STATE, TEST_SIZE
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import RANDOM_STATE, TEST_SIZE

logger = logging.getLogger(__name__)


class AdmissionPredictor:
    """
    Predicts hospital admission patterns and busy periods
    """
    
    def __init__(self, admission_data: pd.DataFrame):
        """
        Initialize AdmissionPredictor
        
        Args:
            admission_data: DataFrame containing historical admission data
        """
        self.data = admission_data.copy()
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare data for prediction models"""
        logger.info("Preparing data for prediction models")
        
        # Convert dates
        self.data['admission_date'] = pd.to_datetime(self.data['D.O.A'], format='%d/%m/%Y', errors='coerce')
        self.data['discharge_date'] = pd.to_datetime(self.data['D.O.D'], format='%d/%m/%Y', errors='coerce')
        
        # Extract temporal features
        self.data['year'] = self.data['admission_date'].dt.year
        self.data['month'] = self.data['admission_date'].dt.month
        self.data['day'] = self.data['admission_date'].dt.day
        self.data['day_of_week'] = self.data['admission_date'].dt.dayofweek
        self.data['day_of_year'] = self.data['admission_date'].dt.dayofyear
        self.data['week_of_year'] = self.data['admission_date'].dt.isocalendar().week
        self.data['is_weekend'] = (self.data['day_of_week'] >= 5).astype(int)
        
        # Create seasonal features
        self.data['season'] = self.data['month'].apply(self._get_season)
        
        # Create holiday indicators (simplified)
        self.data['is_holiday'] = self._create_holiday_indicator()
        
        # Create daily admission counts for time series prediction
        self.daily_admissions = self.data.groupby('admission_date').size().reset_index(name='admission_count')
        self.daily_admissions = self._add_temporal_features(self.daily_admissions)
        
    def _get_season(self, month: int) -> int:
        """Convert month to season (0=Winter, 1=Spring, 2=Summer, 3=Fall)"""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Fall
            
    def _create_holiday_indicator(self) -> pd.Series:
        """Create simplified holiday indicator"""
        # This is a simplified version - in practice, you'd use a proper holiday library
        holidays = []
        # Add major holidays (simplified example)
        for year in self.data['year'].unique():
            if not pd.isna(year):
                # New Year's Day
                holidays.append(pd.Timestamp(f'{int(year)}-01-01'))
                # Independence Day (assuming Indian context)
                holidays.append(pd.Timestamp(f'{int(year)}-08-15'))
                # Gandhi Jayanti
                holidays.append(pd.Timestamp(f'{int(year)}-10-02'))
        
        return self.data['admission_date'].isin(holidays).astype(int)
        
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal features to daily admissions data"""
        df = df.copy()
        df['year'] = df['admission_date'].dt.year
        df['month'] = df['admission_date'].dt.month
        df['day'] = df['admission_date'].dt.day
        df['day_of_week'] = df['admission_date'].dt.dayofweek
        df['day_of_year'] = df['admission_date'].dt.dayofyear
        df['week_of_year'] = df['admission_date'].dt.isocalendar().week
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['season'] = df['month'].apply(self._get_season)
        
        # Add lag features
        for lag in [1, 3, 7, 14, 30]:
            df[f'admission_count_lag_{lag}'] = df['admission_count'].shift(lag)
            
        # Add rolling averages
        for window in [3, 7, 14, 30]:
            df[f'admission_count_rolling_{window}'] = df['admission_count'].rolling(window=window).mean()
            
        return df
        
    def predict_daily_admissions(self, days_ahead: int = 30) -> Dict:
        """
        Predict daily admission counts for the next N days
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary containing predictions and model metrics
        """
        logger.info(f"Predicting daily admissions for next {days_ahead} days")
        
        # Prepare features
        feature_cols = [
            'month', 'day_of_week', 'day_of_year', 'week_of_year',
            'is_weekend', 'season', 'admission_count_lag_1',
            'admission_count_lag_3', 'admission_count_lag_7',
            'admission_count_rolling_3', 'admission_count_rolling_7'
        ]
        
        # Remove rows with NaN values (due to lag features)
        clean_data = self.daily_admissions.dropna()
        
        if len(clean_data) < 30:
            logger.warning("Insufficient data for prediction")
            return {'error': 'Insufficient data for prediction'}
        
        X = clean_data[feature_cols]
        y = clean_data['admission_count']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=False
        )
        
        # Train models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=RANDOM_STATE),
            'linear_regression': LinearRegression()
        }
        
        model_results = {}
        
        for name, model in models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions on test set
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            model_results[name] = {
                'model': model,
                'mae': mae,
                'mse': mse,
                'r2': r2,
                'predictions': y_pred.tolist()
            }
            
        # Select best model based on R²
        best_model_name = max(model_results.keys(), key=lambda x: model_results[x]['r2'])
        best_model = model_results[best_model_name]['model']
        
        # Generate future predictions
        future_predictions = self._generate_future_predictions(best_model, feature_cols, days_ahead)
        
        return {
            'best_model': best_model_name,
            'model_metrics': {name: {k: v for k, v in results.items() if k != 'model'} 
                            for name, results in model_results.items()},
            'future_predictions': future_predictions,
            'feature_importance': self._get_feature_importance(best_model, feature_cols)
        }
        
    def _generate_future_predictions(self, model: Any, feature_cols: List[str], days_ahead: int) -> List[Dict]:
        """Generate predictions for future dates"""
        predictions = []
        
        # Get the last date in the data
        last_date = self.daily_admissions['admission_date'].max()
        
        # Create future dates
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        for date in future_dates:
            # Create features for this date
            features = {
                'month': date.month,
                'day_of_week': date.weekday(),
                'day_of_year': date.timetuple().tm_yday,
                'week_of_year': date.isocalendar()[1],
                'is_weekend': 1 if date.weekday() >= 5 else 0,
                'season': self._get_season(date.month)
            }
            
            # For lag features, use recent actual or predicted values
            # This is a simplified approach - in practice, you'd use a more sophisticated method
            recent_values = self.daily_admissions['admission_count'].tail(30).mean()
            features.update({
                'admission_count_lag_1': recent_values,
                'admission_count_lag_3': recent_values,
                'admission_count_lag_7': recent_values,
                'admission_count_rolling_3': recent_values,
                'admission_count_rolling_7': recent_values
            })
            
            # Make prediction
            X_pred = pd.DataFrame([features])[feature_cols]
            prediction = model.predict(X_pred)[0]
            
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_admissions': max(0, int(round(prediction)))  # Ensure non-negative integer
            })
            
        return predictions
        
    def _get_feature_importance(self, model: Any, feature_cols: List[str]) -> Dict:
        """Get feature importance from the model"""
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(feature_cols, model.feature_importances_))
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        else:
            return {}
            
    def predict_busy_periods(self, threshold_percentile: float = 75) -> Dict:
        """
        Identify and predict busy periods based on historical patterns
        
        Args:
            threshold_percentile: Percentile above which periods are considered busy
            
        Returns:
            Dictionary containing busy period analysis
        """
        logger.info(f"Predicting busy periods (threshold: {threshold_percentile}th percentile)")
        
        # Calculate threshold for busy periods
        threshold = np.percentile(self.daily_admissions['admission_count'], threshold_percentile)
        
        # Identify historical busy periods
        busy_days = self.daily_admissions[
            self.daily_admissions['admission_count'] >= threshold
        ].copy()
        
        # Analyze patterns in busy periods
        busy_patterns = {
            'threshold': threshold,
            'busy_day_count': len(busy_days),
            'busy_day_percentage': (len(busy_days) / len(self.daily_admissions)) * 100,
            'average_busy_day_admissions': busy_days['admission_count'].mean(),
            'busy_months': busy_days['month'].value_counts().to_dict(),
            'busy_days_of_week': busy_days['day_of_week'].value_counts().to_dict(),
            'busy_seasons': busy_days['season'].value_counts().to_dict()
        }
        
        # Predict future busy periods
        daily_predictions = self.predict_daily_admissions(90)  # 3 months ahead
        
        if 'future_predictions' in daily_predictions:
            future_busy_periods = [
                pred for pred in daily_predictions['future_predictions']
                if pred['predicted_admissions'] >= threshold
            ]
            
            busy_patterns['future_busy_periods'] = future_busy_periods
            busy_patterns['predicted_busy_days'] = len(future_busy_periods)
            
        return busy_patterns
        
    def analyze_capacity_requirements(self) -> Dict:
        """
        Analyze hospital capacity requirements based on admission patterns
        
        Returns:
            Dictionary containing capacity analysis
        """
        logger.info("Analyzing capacity requirements")
        
        capacity_analysis = {}
        
        # Basic capacity metrics
        daily_stats = self.daily_admissions['admission_count'].describe()
        capacity_analysis['daily_admission_stats'] = daily_stats.to_dict()
        
        # Peak capacity requirements
        capacity_analysis['peak_requirements'] = {
            'max_daily_admissions': int(self.daily_admissions['admission_count'].max()),
            'percentile_95': int(np.percentile(self.daily_admissions['admission_count'], 95)),
            'percentile_90': int(np.percentile(self.daily_admissions['admission_count'], 90)),
            'percentile_75': int(np.percentile(self.daily_admissions['admission_count'], 75))
        }
        
        # Monthly capacity patterns
        monthly_capacity = self.daily_admissions.groupby('month')['admission_count'].agg([
            'mean', 'max', 'std'
        ])
        capacity_analysis['monthly_patterns'] = monthly_capacity.to_dict()
        
        # Day of week patterns
        dow_capacity = self.daily_admissions.groupby('day_of_week')['admission_count'].agg([
            'mean', 'max', 'std'
        ])
        capacity_analysis['day_of_week_patterns'] = dow_capacity.to_dict()
        
        return capacity_analysis
        
    def save_models(self, filepath: str) -> None:
        """Save trained models to file"""
        joblib.dump({
            'models': self.models,
            'scalers': self.scalers,
            'encoders': self.encoders,
            'feature_importance': self.feature_importance
        }, filepath)
        logger.info(f"Models saved to {filepath}")
        
    def load_models(self, filepath: str) -> None:
        """Load trained models from file"""
        saved_data = joblib.load(filepath)
        self.models = saved_data['models']
        self.scalers = saved_data['scalers']
        self.encoders = saved_data['encoders']
        self.feature_importance = saved_data['feature_importance']
        logger.info(f"Models loaded from {filepath}")


def main():
    """
    Main function to demonstrate admission prediction
    """
    print("AdmissionPredictor module loaded successfully")
    print("Use this class with loaded admission data to perform predictions")


if __name__ == "__main__":
    main()
