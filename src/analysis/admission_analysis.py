"""
Admission pattern analysis for Hospital Patient Analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

try:
    from ..config import AGE_GROUPS, MEDICAL_CONDITIONS, RISK_FACTORS
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import AGE_GROUPS, MEDICAL_CONDITIONS, RISK_FACTORS

logger = logging.getLogger(__name__)


class AdmissionAnalyzer:
    """
    Analyzes hospital admission patterns and trends
    """
    
    def __init__(self, admission_data: pd.DataFrame):
        """
        Initialize AdmissionAnalyzer
        
        Args:
            admission_data: DataFrame containing admission data
        """
        self.data = admission_data.copy()
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare data for analysis"""
        # Convert dates
        self.data['admission_date'] = pd.to_datetime(self.data['D.O.A'], format='%d/%m/%Y', errors='coerce')
        self.data['discharge_date'] = pd.to_datetime(self.data['D.O.D'], format='%d/%m/%Y', errors='coerce')
        
        # Create age groups
        self.data['age_group'] = self.data['AGE'].apply(self._categorize_age)
        
        # Create month and year columns
        self.data['admission_month'] = self.data['admission_date'].dt.month
        self.data['admission_year'] = self.data['admission_date'].dt.year
        self.data['admission_day_of_week'] = self.data['admission_date'].dt.day_name()
        
        # Calculate length of stay
        self.data['calculated_los'] = (self.data['discharge_date'] - self.data['admission_date']).dt.days
        
    def _categorize_age(self, age: float) -> str:
        """Categorize age into groups"""
        if pd.isna(age):
            return 'Unknown'
        
        for group_name, (min_age, max_age) in AGE_GROUPS.items():
            if min_age <= age <= max_age:
                return group_name
                
        return 'Other'
        
    def analyze_admission_rates_by_age(self) -> Dict:
        """
        Analyze admission rates by age groups
        
        Returns:
            Dictionary containing age-based admission statistics
        """
        logger.info("Analyzing admission rates by age groups")
        
        age_analysis = {}
        
        # Overall age distribution
        age_dist = self.data['age_group'].value_counts()
        age_analysis['age_distribution'] = age_dist.to_dict()
        
        # Age statistics
        age_stats = self.data['AGE'].describe()
        age_analysis['age_statistics'] = age_stats.to_dict()
        
        # Age vs outcome
        age_outcome = pd.crosstab(self.data['age_group'], self.data['OUTCOME'])
        age_analysis['age_vs_outcome'] = age_outcome.to_dict()
        
        # Age vs length of stay
        age_los = self.data.groupby('age_group')['DURATION OF STAY'].agg(['mean', 'median', 'std'])
        age_analysis['age_vs_length_of_stay'] = age_los.to_dict()
        
        # Age vs admission type
        age_admission_type = pd.crosstab(self.data['age_group'], self.data['TYPE OF ADMISSION-EMERGENCY/OPD'])
        age_analysis['age_vs_admission_type'] = age_admission_type.to_dict()
        
        return age_analysis
        
    def analyze_admission_rates_by_disease(self) -> Dict:
        """
        Analyze admission rates by disease/condition
        
        Returns:
            Dictionary containing disease-based admission statistics
        """
        logger.info("Analyzing admission rates by disease")
        
        disease_analysis = {}
        
        # Disease prevalence
        disease_prevalence = {}
        for condition in MEDICAL_CONDITIONS:
            if condition in self.data.columns:
                # Convert to numeric, treating non-numeric values as 0
                condition_data = pd.to_numeric(self.data[condition], errors='coerce').fillna(0)
                prevalence = condition_data.sum()
                total_patients = len(self.data)
                disease_prevalence[condition] = {
                    'count': int(prevalence),
                    'percentage': (prevalence / total_patients) * 100
                }
        
        disease_analysis['disease_prevalence'] = disease_prevalence
        
        # Top diseases by count
        disease_counts = [(k, v['count']) for k, v in disease_prevalence.items()]
        disease_counts.sort(key=lambda x: x[1], reverse=True)
        disease_analysis['top_diseases'] = disease_counts[:10]
        
        # Disease co-occurrence matrix
        condition_cols = [col for col in MEDICAL_CONDITIONS if col in self.data.columns]
        if condition_cols:
            # Convert all condition columns to numeric
            condition_data = self.data[condition_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
            cooccurrence = condition_data.corr()
            disease_analysis['disease_cooccurrence'] = cooccurrence.to_dict()
        
        # Disease vs age groups
        disease_age = {}
        for condition in MEDICAL_CONDITIONS[:5]:  # Top 5 for performance
            if condition in self.data.columns:
                condition_data = pd.to_numeric(self.data[condition], errors='coerce').fillna(0)
                condition_by_age = self.data[condition_data == 1]['age_group'].value_counts()
                disease_age[condition] = condition_by_age.to_dict()
        
        disease_analysis['disease_by_age'] = disease_age
        
        return disease_analysis
        
    def analyze_temporal_patterns(self) -> Dict:
        """
        Analyze temporal admission patterns
        
        Returns:
            Dictionary containing temporal analysis results
        """
        logger.info("Analyzing temporal admission patterns")
        
        temporal_analysis = {}
        
        # Monthly patterns
        monthly_admissions = self.data['admission_month'].value_counts().sort_index()
        temporal_analysis['monthly_patterns'] = monthly_admissions.to_dict()
        
        # Daily patterns
        daily_admissions = self.data['admission_day_of_week'].value_counts()
        temporal_analysis['daily_patterns'] = daily_admissions.to_dict()
        
        # Yearly trends
        if 'admission_year' in self.data.columns:
            yearly_admissions = self.data['admission_year'].value_counts().sort_index()
            temporal_analysis['yearly_trends'] = yearly_admissions.to_dict()
        
        # Seasonal analysis
        season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                     3: 'Spring', 4: 'Spring', 5: 'Spring',
                     6: 'Summer', 7: 'Summer', 8: 'Summer',
                     9: 'Fall', 10: 'Fall', 11: 'Fall'}
        
        self.data['season'] = self.data['admission_month'].map(season_map)
        seasonal_admissions = self.data['season'].value_counts()
        temporal_analysis['seasonal_patterns'] = seasonal_admissions.to_dict()
        
        return temporal_analysis
        
    def analyze_risk_factors(self) -> Dict:
        """
        Analyze risk factors and their impact on admissions
        
        Returns:
            Dictionary containing risk factor analysis
        """
        logger.info("Analyzing risk factors")
        
        risk_analysis = {}
        
        # Risk factor prevalence
        risk_prevalence = {}
        for risk_factor in RISK_FACTORS:
            if risk_factor in self.data.columns:
                risk_data = pd.to_numeric(self.data[risk_factor], errors='coerce').fillna(0)
                prevalence = risk_data.sum()
                total_patients = len(self.data)
                risk_prevalence[risk_factor] = {
                    'count': int(prevalence),
                    'percentage': (prevalence / total_patients) * 100
                }
        
        risk_analysis['risk_factor_prevalence'] = risk_prevalence
        
        # Risk factors vs outcomes
        risk_outcomes = {}
        for risk_factor in RISK_FACTORS:
            if risk_factor in self.data.columns:
                outcome_by_risk = pd.crosstab(self.data[risk_factor], self.data['OUTCOME'])
                risk_outcomes[risk_factor] = outcome_by_risk.to_dict()
        
        risk_analysis['risk_vs_outcomes'] = risk_outcomes
        
        # Multiple risk factors
        risk_cols = [col for col in RISK_FACTORS if col in self.data.columns]
        if risk_cols:
            self.data['total_risk_factors'] = self.data[risk_cols].sum(axis=1)
            risk_distribution = self.data['total_risk_factors'].value_counts().sort_index()
            risk_analysis['multiple_risk_factors'] = risk_distribution.to_dict()
        
        return risk_analysis
        
    def analyze_geographical_patterns(self) -> Dict:
        """
        Analyze geographical admission patterns (Rural vs Urban)
        
        Returns:
            Dictionary containing geographical analysis
        """
        logger.info("Analyzing geographical patterns")
        
        geo_analysis = {}
        
        # Rural vs Urban distribution
        location_dist = self.data['RURAL'].value_counts()
        geo_analysis['location_distribution'] = location_dist.to_dict()
        
        # Location vs age groups
        location_age = pd.crosstab(self.data['RURAL'], self.data['age_group'])
        geo_analysis['location_vs_age'] = location_age.to_dict()
        
        # Location vs diseases
        location_disease = {}
        for condition in MEDICAL_CONDITIONS[:10]:  # Top 10 for performance
            if condition in self.data.columns:
                condition_by_location = pd.crosstab(self.data['RURAL'], self.data[condition])
                location_disease[condition] = condition_by_location.to_dict()
        
        geo_analysis['location_vs_disease'] = location_disease
        
        # Location vs outcomes
        location_outcome = pd.crosstab(self.data['RURAL'], self.data['OUTCOME'])
        geo_analysis['location_vs_outcome'] = location_outcome.to_dict()
        
        return geo_analysis
        
    def generate_comprehensive_report(self) -> Dict:
        """
        Generate comprehensive admission analysis report
        
        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Generating comprehensive admission analysis report")
        
        report = {
            'summary': {
                'total_admissions': len(self.data),
                'date_range': {
                    'start': self.data['admission_date'].min().strftime('%Y-%m-%d'),
                    'end': self.data['admission_date'].max().strftime('%Y-%m-%d')
                },
                'average_age': self.data['AGE'].mean(),
                'average_length_of_stay': self.data['DURATION OF STAY'].mean()
            },
            'age_analysis': self.analyze_admission_rates_by_age(),
            'disease_analysis': self.analyze_admission_rates_by_disease(),
            'temporal_analysis': self.analyze_temporal_patterns(),
            'risk_analysis': self.analyze_risk_factors(),
            'geographical_analysis': self.analyze_geographical_patterns()
        }
        
        return report


def main():
    """
    Main function to demonstrate admission analysis
    """
    # This would typically load data using DataLoader
    print("AdmissionAnalyzer module loaded successfully")
    print("Use this class with loaded admission data to perform analysis")


if __name__ == "__main__":
    main()
