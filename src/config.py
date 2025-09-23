"""
Configuration settings for Hospital Patient Analytics
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, NOTEBOOKS_DIR, DASHBOARD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data file paths
ADMISSION_DATA_PATH = Path("admission hospital data/HDHI Admission data.csv")
MORTALITY_DATA_PATH = Path("admission hospital data/HDHI Mortality Data.csv")
POLLUTION_DATA_PATH = Path("admission hospital data/HDHI Pollution Data.csv")
TABLE_HEADINGS_PATH = Path("admission hospital data/table_headings.csv")

# Analysis parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.2

# Visualization settings
FIGURE_SIZE = (12, 8)
DPI = 300
STYLE = 'whitegrid'

# Dashboard settings
DASHBOARD_HOST = "localhost"
DASHBOARD_PORT = 8501
DEBUG_MODE = True

# Model parameters
MAX_FEATURES = 50
N_ESTIMATORS = 100
LEARNING_RATE = 0.1

# Date formats
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

# Column mappings for better readability
COLUMN_MAPPINGS = {
    'D.O.A': 'admission_date',
    'D.O.D': 'discharge_date',
    'AGE': 'age',
    'GENDER': 'gender',
    'RURAL': 'location_type',
    'TYPE OF ADMISSION-EMERGENCY/OPD': 'admission_type',
    'month year': 'month_year',
    'DURATION OF STAY': 'length_of_stay',
    'duration of intensive unit stay': 'icu_stay_duration',
    'OUTCOME': 'outcome',
    'SMOKING ': 'smoking',
    'ALCOHOL': 'alcohol',
    'DM': 'diabetes',
    'HTN': 'hypertension',
    'CAD': 'coronary_artery_disease',
    'PRIOR CMP': 'cardiomyopathy',
    'CKD': 'chronic_kidney_disease'
}

# Medical condition columns
MEDICAL_CONDITIONS = [
    'SEVERE ANAEMIA', 'ANAEMIA', 'STABLE ANGINA', 'ACS', 'STEMI',
    'ATYPICAL CHEST PAIN', 'HEART FAILURE', 'HFREF', 'HFNEF',
    'VALVULAR', 'CHB', 'SSS', 'AKI', 'CVA INFRACT', 'CVA BLEED',
    'AF', 'VT', 'PSVT', 'CONGENITAL', 'UTI', 'NEURO CARDIOGENIC SYNCOPE',
    'ORTHOSTATIC', 'INFECTIVE ENDOCARDITIS', 'DVT', 'CARDIOGENIC SHOCK',
    'SHOCK', 'PULMONARY EMBOLISM', 'CHEST INFECTION'
]

# Laboratory test columns
LAB_TESTS = [
    'HB', 'TLC', 'PLATELETS', 'GLUCOSE', 'UREA', 'CREATININE',
    'BNP', 'RAISED CARDIAC ENZYMES', 'EF'
]

# Risk factors
RISK_FACTORS = ['SMOKING ', 'ALCOHOL', 'DM', 'HTN', 'CAD', 'PRIOR CMP', 'CKD']

# Age groups for analysis
AGE_GROUPS = {
    'Young Adult (18-35)': (18, 35),
    'Middle Age (36-50)': (36, 50),
    'Older Adult (51-65)': (51, 65),
    'Elderly (66-80)': (66, 80),
    'Very Elderly (80+)': (80, 120)
}

# Color palettes for visualizations
COLOR_PALETTES = {
    'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'medical': ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
    'sequential': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
    'diverging': ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
}
