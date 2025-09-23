"""
Data loading utilities for Hospital Patient Analytics
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

try:
    from ..config import (
        ADMISSION_DATA_PATH, MORTALITY_DATA_PATH, POLLUTION_DATA_PATH,
        TABLE_HEADINGS_PATH, DATE_FORMAT, COLUMN_MAPPINGS
    )
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import (
        ADMISSION_DATA_PATH, MORTALITY_DATA_PATH, POLLUTION_DATA_PATH,
        TABLE_HEADINGS_PATH, DATE_FORMAT, COLUMN_MAPPINGS
    )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handles loading and initial processing of hospital data files
    """
    
    def __init__(self, data_directory: Optional[Path] = None):
        """
        Initialize DataLoader
        
        Args:
            data_directory: Path to directory containing data files
        """
        self.data_directory = data_directory or Path(".")
        self.admission_data = None
        self.mortality_data = None
        self.pollution_data = None
        self.table_headings = None
        
    def load_admission_data(self) -> pd.DataFrame:
        """
        Load hospital admission data
        
        Returns:
            DataFrame containing admission data
        """
        try:
            file_path = self.data_directory / ADMISSION_DATA_PATH
            logger.info(f"Loading admission data from {file_path}")
            
            self.admission_data = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Loaded {len(self.admission_data)} admission records")
            
            # Basic data type optimization
            self.admission_data = self._optimize_dtypes(self.admission_data)
            
            return self.admission_data
            
        except FileNotFoundError:
            logger.error(f"Admission data file not found at {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading admission data: {e}")
            raise
            
    def load_mortality_data(self) -> pd.DataFrame:
        """
        Load mortality data
        
        Returns:
            DataFrame containing mortality data
        """
        try:
            file_path = self.data_directory / MORTALITY_DATA_PATH
            logger.info(f"Loading mortality data from {file_path}")
            
            self.mortality_data = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Loaded {len(self.mortality_data)} mortality records")
            
            return self.mortality_data
            
        except FileNotFoundError:
            logger.error(f"Mortality data file not found at {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading mortality data: {e}")
            raise
            
    def load_pollution_data(self) -> pd.DataFrame:
        """
        Load environmental pollution data
        
        Returns:
            DataFrame containing pollution data
        """
        try:
            file_path = self.data_directory / POLLUTION_DATA_PATH
            logger.info(f"Loading pollution data from {file_path}")
            
            self.pollution_data = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Loaded {len(self.pollution_data)} pollution records")
            
            return self.pollution_data
            
        except FileNotFoundError:
            logger.error(f"Pollution data file not found at {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading pollution data: {e}")
            raise
            
    def load_table_headings(self) -> pd.DataFrame:
        """
        Load table headings/data dictionary
        
        Returns:
            DataFrame containing column descriptions
        """
        try:
            file_path = self.data_directory / TABLE_HEADINGS_PATH
            logger.info(f"Loading table headings from {file_path}")
            
            self.table_headings = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.table_headings)} column descriptions")
            
            return self.table_headings
            
        except FileNotFoundError:
            logger.error(f"Table headings file not found at {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading table headings: {e}")
            raise
            
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all data files
        
        Returns:
            Dictionary containing all loaded DataFrames
        """
        logger.info("Loading all data files...")
        
        data = {}
        data['admission'] = self.load_admission_data()
        data['mortality'] = self.load_mortality_data()
        data['pollution'] = self.load_pollution_data()
        data['headings'] = self.load_table_headings()
        
        logger.info("All data files loaded successfully")
        return data
        
    def get_data_summary(self) -> Dict:
        """
        Get summary statistics for loaded data
        
        Returns:
            Dictionary containing data summary
        """
        summary = {}
        
        if self.admission_data is not None:
            summary['admission'] = {
                'rows': len(self.admission_data),
                'columns': len(self.admission_data.columns),
                'memory_usage': self.admission_data.memory_usage(deep=True).sum() / 1024**2,  # MB
                'missing_values': self.admission_data.isnull().sum().sum(),
                'date_range': self._get_date_range(self.admission_data, 'D.O.A')
            }
            
        if self.mortality_data is not None:
            summary['mortality'] = {
                'rows': len(self.mortality_data),
                'columns': len(self.mortality_data.columns),
                'memory_usage': self.mortality_data.memory_usage(deep=True).sum() / 1024**2,  # MB
            }
            
        if self.pollution_data is not None:
            summary['pollution'] = {
                'rows': len(self.pollution_data),
                'columns': len(self.pollution_data.columns),
                'memory_usage': self.pollution_data.memory_usage(deep=True).sum() / 1024**2,  # MB
                'date_range': self._get_date_range(self.pollution_data, 'DATE')
            }
            
        return summary
        
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize data types to reduce memory usage
        
        Args:
            df: DataFrame to optimize
            
        Returns:
            DataFrame with optimized data types
        """
        # Convert binary columns to boolean
        binary_cols = ['SMOKING ', 'ALCOHOL', 'DM', 'HTN', 'CAD', 'PRIOR CMP', 'CKD']
        for col in binary_cols:
            if col in df.columns:
                df[col] = df[col].astype('boolean')
                
        # Convert categorical columns
        categorical_cols = ['GENDER', 'RURAL', 'TYPE OF ADMISSION-EMERGENCY/OPD', 'OUTCOME']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
                
        # Convert numeric columns to appropriate types
        numeric_cols = ['AGE', 'DURATION OF STAY', 'duration of intensive unit stay']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
        
    def _get_date_range(self, df: pd.DataFrame, date_col: str) -> Optional[Tuple[str, str]]:
        """
        Get date range for a DataFrame
        
        Args:
            df: DataFrame containing date column
            date_col: Name of date column
            
        Returns:
            Tuple of (min_date, max_date) or None if column doesn't exist
        """
        if date_col not in df.columns:
            return None
            
        try:
            dates = pd.to_datetime(df[date_col], format=DATE_FORMAT, errors='coerce')
            return (dates.min().strftime('%Y-%m-%d'), dates.max().strftime('%Y-%m-%d'))
        except Exception:
            return None
            
    def export_processed_data(self, output_dir: Path) -> None:
        """
        Export processed data to files
        
        Args:
            output_dir: Directory to save processed data
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.admission_data is not None:
            self.admission_data.to_csv(output_dir / 'admission_processed.csv', index=False)
            logger.info(f"Exported processed admission data to {output_dir / 'admission_processed.csv'}")
            
        if self.mortality_data is not None:
            self.mortality_data.to_csv(output_dir / 'mortality_processed.csv', index=False)
            logger.info(f"Exported processed mortality data to {output_dir / 'mortality_processed.csv'}")
            
        if self.pollution_data is not None:
            self.pollution_data.to_csv(output_dir / 'pollution_processed.csv', index=False)
            logger.info(f"Exported processed pollution data to {output_dir / 'pollution_processed.csv'}")


def main():
    """
    Main function to demonstrate data loading
    """
    loader = DataLoader()
    
    try:
        # Load all data
        data = loader.load_all_data()
        
        # Print summary
        summary = loader.get_data_summary()
        print("Data Summary:")
        print("=" * 50)
        for dataset, stats in summary.items():
            print(f"\n{dataset.upper()} DATA:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
