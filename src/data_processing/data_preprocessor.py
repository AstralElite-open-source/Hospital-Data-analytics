"""
Data preprocessing utilities for Hospital Patient Analytics
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles data preprocessing for machine learning models
    """
    
    def __init__(self):
        """Initialize DataPreprocessor"""
        self.scalers = {}
        self.encoders = {}
    
    def preprocess_for_modeling(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Preprocess data for machine learning models
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (processed DataFrame, preprocessing info)
        """
        logger.info("Preprocessing data for modeling")
        
        processed_df = df.copy()
        preprocessing_info = {}
        
        # Handle missing values
        processed_df = self._handle_missing_values(processed_df)
        
        # Encode categorical variables
        processed_df = self._encode_categorical_variables(processed_df)
        
        # Scale numerical features
        processed_df = self._scale_numerical_features(processed_df)
        
        preprocessing_info['scalers'] = self.scalers
        preprocessing_info['encoders'] = self.encoders
        
        return processed_df, preprocessing_info
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values"""
        # Simple strategy: fill with median for numeric, mode for categorical
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'Unknown', inplace=True)
        
        return df
    
    def _encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_columns:
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col].astype(str))
            self.encoders[col] = encoder
        
        return df
    
    def _scale_numerical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns
        
        for col in numerical_columns:
            scaler = StandardScaler()
            df[col] = scaler.fit_transform(df[[col]])
            self.scalers[col] = scaler
        
        return df


def main():
    """Main function for testing"""
    print("DataPreprocessor module loaded successfully")


if __name__ == "__main__":
    main()
