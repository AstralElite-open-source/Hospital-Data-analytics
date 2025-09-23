"""
Streamlit Dashboard for Hospital Patient Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_processing.data_loader import DataLoader
from src.analysis.admission_analysis import AdmissionAnalyzer
from src.prediction.admission_predictor import AdmissionPredictor
from src.visualization.charts import ChartGenerator

# Page configuration
st.set_page_config(
    page_title="Hospital Patient Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache hospital data"""
    try:
        loader = DataLoader()
        data = loader.load_all_data()
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def get_analysis_results(admission_data):
    """Get cached analysis results"""
    analyzer = AdmissionAnalyzer(admission_data)
    return analyzer.generate_comprehensive_report()

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Hospital Patient Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Overview", "Admission Analysis", "Disease Analysis", "Predictions", "Geographic Analysis"]
    )
    
    # Load data
    with st.spinner("Loading hospital data..."):
        data = load_data()
    
    if data is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    admission_data = data['admission']
    
    # Generate analysis results
    with st.spinner("Analyzing data..."):
        analysis_results = get_analysis_results(admission_data)
    
    # Initialize chart generator
    chart_gen = ChartGenerator()
    
    # Page routing
    if page == "Overview":
        show_overview(admission_data, analysis_results, chart_gen)
    elif page == "Admission Analysis":
        show_admission_analysis(admission_data, analysis_results, chart_gen)
    elif page == "Disease Analysis":
        show_disease_analysis(admission_data, analysis_results, chart_gen)
    elif page == "Predictions":
        show_predictions(admission_data, chart_gen)
    elif page == "Geographic Analysis":
        show_geographic_analysis(admission_data, analysis_results, chart_gen)

def show_overview(admission_data, analysis_results, chart_gen):
    """Show overview dashboard"""
    st.header("📊 Hospital Analytics Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Admissions",
            f"{analysis_results['summary']['total_admissions']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Average Age",
            f"{analysis_results['summary']['average_age']:.1f} years",
            delta=None
        )
    
    with col3:
        st.metric(
            "Avg Length of Stay",
            f"{analysis_results['summary']['average_length_of_stay']:.1f} days",
            delta=None
        )
    
    with col4:
        discharge_rate = (admission_data['OUTCOME'] == 'DISCHARGE').mean() * 100
        st.metric(
            "Discharge Rate",
            f"{discharge_rate:.1f}%",
            delta=None
        )
    
    # Date range
    st.info(f"📅 Data Range: {analysis_results['summary']['date_range']['start']} to {analysis_results['summary']['date_range']['end']}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Age Distribution")
        age_chart = chart_gen.create_age_distribution_chart(admission_data['AGE'])
        st.plotly_chart(age_chart, use_container_width=True)
    
    with col2:
        st.subheader("Patient Outcomes")
        outcome_chart = chart_gen.create_outcome_analysis_chart(admission_data['OUTCOME'])
        st.plotly_chart(outcome_chart, use_container_width=True)
    
    # Temporal trends
    st.subheader("Temporal Admission Patterns")
    temporal_chart = chart_gen.create_temporal_trends_chart(analysis_results['temporal_analysis'])
    st.plotly_chart(temporal_chart, use_container_width=True)

def show_admission_analysis(admission_data, analysis_results, chart_gen):
    """Show admission analysis dashboard"""
    st.header("🏥 Admission Pattern Analysis")
    
    # Age group analysis
    st.subheader("Admission by Age Groups")
    age_data = analysis_results['age_analysis']
    
    # Age distribution chart
    age_chart = chart_gen.create_age_distribution_chart(admission_data['AGE'], 'histogram')
    st.plotly_chart(age_chart, use_container_width=True)
    
    # Age group table
    age_dist_df = pd.DataFrame.from_dict(age_data['age_distribution'], orient='index', columns=['Count'])
    age_dist_df['Percentage'] = (age_dist_df['Count'] / age_dist_df['Count'].sum() * 100).round(2)
    st.dataframe(age_dist_df)
    
    # Risk factors
    st.subheader("Risk Factor Analysis")
    if 'risk_analysis' in analysis_results:
        risk_chart = chart_gen.create_risk_factor_analysis_chart(analysis_results['risk_analysis'])
        st.plotly_chart(risk_chart, use_container_width=True)
    
    # Length of stay analysis
    st.subheader("Length of Stay Analysis")
    los_chart = chart_gen.create_length_of_stay_analysis(admission_data['DURATION OF STAY'])
    st.plotly_chart(los_chart, use_container_width=True)

def show_disease_analysis(admission_data, analysis_results, chart_gen):
    """Show disease analysis dashboard"""
    st.header("🦠 Disease Prevalence Analysis")
    
    disease_data = analysis_results['disease_analysis']
    
    # Disease prevalence chart
    st.subheader("Top Disease Conditions")
    disease_chart = chart_gen.create_disease_prevalence_chart(disease_data['disease_prevalence'])
    st.plotly_chart(disease_chart, use_container_width=True)
    
    # Disease statistics table
    st.subheader("Disease Statistics")
    disease_df = pd.DataFrame.from_dict(disease_data['disease_prevalence'], orient='index')
    disease_df = disease_df.sort_values('count', ascending=False)
    st.dataframe(disease_df.head(20))
    
    # Disease co-occurrence
    if 'disease_cooccurrence' in disease_data:
        st.subheader("Disease Co-occurrence Patterns")
        st.info("Correlation matrix showing how often diseases occur together")
        
        # Show top correlations
        cooccurrence_df = pd.DataFrame(disease_data['disease_cooccurrence'])
        
        # Get top correlations (excluding self-correlations)
        correlations = []
        for i in cooccurrence_df.index:
            for j in cooccurrence_df.columns:
                if i != j and not pd.isna(cooccurrence_df.loc[i, j]):
                    correlations.append((i, j, cooccurrence_df.loc[i, j]))
        
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if correlations:
            st.write("**Top Disease Correlations:**")
            for disease1, disease2, corr in correlations[:10]:
                st.write(f"• {disease1} ↔ {disease2}: {corr:.3f}")

def show_predictions(admission_data, chart_gen):
    """Show prediction dashboard"""
    st.header("🔮 Admission Predictions & Forecasting")
    
    # Prediction parameters
    col1, col2 = st.columns(2)
    with col1:
        days_ahead = st.slider("Days to Predict", 7, 90, 30)
    with col2:
        threshold_percentile = st.slider("Busy Period Threshold (%ile)", 50, 95, 75)
    
    if st.button("Generate Predictions"):
        with st.spinner("Generating predictions..."):
            predictor = AdmissionPredictor(admission_data)
            
            # Daily predictions
            st.subheader("Daily Admission Predictions")
            predictions = predictor.predict_daily_admissions(days_ahead)
            
            if 'error' not in predictions:
                prediction_chart = chart_gen.create_admission_prediction_chart(predictions)
                st.plotly_chart(prediction_chart, use_container_width=True)
                
                # Model performance
                st.subheader("Model Performance")
                metrics_df = pd.DataFrame(predictions['model_metrics']).T
                st.dataframe(metrics_df)
                
                # Feature importance
                if predictions['feature_importance']:
                    st.subheader("Feature Importance")
                    importance_df = pd.DataFrame.from_dict(
                        predictions['feature_importance'], 
                        orient='index', 
                        columns=['Importance']
                    )
                    st.bar_chart(importance_df)
            
            # Busy periods
            st.subheader("Busy Period Analysis")
            busy_periods = predictor.predict_busy_periods(threshold_percentile)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Busy Day Threshold", f"{busy_periods['threshold']:.0f} admissions")
                st.metric("Historical Busy Days", f"{busy_periods['busy_day_count']}")
            with col2:
                st.metric("Busy Day %", f"{busy_periods['busy_day_percentage']:.1f}%")
                if 'predicted_busy_days' in busy_periods:
                    st.metric("Predicted Busy Days", f"{busy_periods['predicted_busy_days']}")
            
            # Capacity analysis
            st.subheader("Capacity Requirements")
            capacity_analysis = predictor.analyze_capacity_requirements()
            
            capacity_metrics = capacity_analysis['peak_requirements']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Daily", capacity_metrics['max_daily_admissions'])
            with col2:
                st.metric("95th Percentile", capacity_metrics['percentile_95'])
            with col3:
                st.metric("90th Percentile", capacity_metrics['percentile_90'])
            with col4:
                st.metric("75th Percentile", capacity_metrics['percentile_75'])

def show_geographic_analysis(admission_data, analysis_results, chart_gen):
    """Show geographic analysis dashboard"""
    st.header("🗺️ Geographic Distribution Analysis")
    
    geo_data = analysis_results['geographical_analysis']
    
    # Rural vs Urban distribution
    st.subheader("Rural vs Urban Patient Distribution")
    geo_chart = chart_gen.create_geographical_distribution_chart(geo_data)
    st.plotly_chart(geo_chart, use_container_width=True)
    
    # Location vs outcomes
    st.subheader("Outcomes by Location")
    if 'location_vs_outcome' in geo_data:
        outcome_df = pd.DataFrame(geo_data['location_vs_outcome'])
        st.dataframe(outcome_df)
        
        # Outcome rates by location
        outcome_rates = outcome_df.div(outcome_df.sum(axis=1), axis=0) * 100
        st.bar_chart(outcome_rates)
    
    # Disease patterns by location
    st.subheader("Disease Patterns by Location")
    if 'location_vs_disease' in geo_data:
        st.info("Showing disease prevalence differences between rural and urban areas")
        
        # Calculate disease rates for rural vs urban
        location_disease_summary = {}
        for disease, data in geo_data['location_vs_disease'].items():
            if isinstance(data, dict) and len(data) > 0:
                rural_cases = data.get('R', {}).get(1, 0)
                urban_cases = data.get('U', {}).get(1, 0)
                total_rural = sum(data.get('R', {}).values())
                total_urban = sum(data.get('U', {}).values())
                
                if total_rural > 0 and total_urban > 0:
                    rural_rate = (rural_cases / total_rural) * 100
                    urban_rate = (urban_cases / total_urban) * 100
                    location_disease_summary[disease] = {
                        'Rural Rate (%)': rural_rate,
                        'Urban Rate (%)': urban_rate,
                        'Difference': urban_rate - rural_rate
                    }
        
        if location_disease_summary:
            disease_location_df = pd.DataFrame(location_disease_summary).T
            disease_location_df = disease_location_df.sort_values('Difference', ascending=False)
            st.dataframe(disease_location_df.head(10))

if __name__ == "__main__":
    main()
