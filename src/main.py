"""
Main execution script for Hospital Patient Analytics
"""

import logging
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

from .data_processing.data_loader import DataLoader
from .analysis.admission_analysis import AdmissionAnalyzer
from .prediction.admission_predictor import AdmissionPredictor
from .visualization.charts import ChartGenerator
from .config import PROCESSED_DATA_DIR, EXPORTS_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hospital_analytics.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Main execution function for hospital analytics
    """
    logger.info("Starting Hospital Patient Analytics")
    
    try:
        # Step 1: Load Data
        logger.info("Step 1: Loading hospital data")
        loader = DataLoader()
        data = loader.load_all_data()
        
        # Print data summary
        summary = loader.get_data_summary()
        logger.info("Data loaded successfully:")
        for dataset, stats in summary.items():
            logger.info(f"  {dataset}: {stats}")
        
        # Step 2: Perform Analysis
        logger.info("Step 2: Performing comprehensive analysis")
        analyzer = AdmissionAnalyzer(data['admission'])
        analysis_results = analyzer.generate_comprehensive_report()
        
        # Save analysis results
        analysis_file = EXPORTS_DIR / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            json_compatible_results = convert_to_json_compatible(analysis_results)
            json.dump(json_compatible_results, f, indent=2, default=str)
        
        logger.info(f"Analysis results saved to {analysis_file}")
        
        # Step 3: Generate Predictions
        logger.info("Step 3: Generating predictions")
        predictor = AdmissionPredictor(data['admission'])
        
        # Daily predictions
        daily_predictions = predictor.predict_daily_admissions(30)
        logger.info(f"Generated predictions for next 30 days")
        
        # Busy period predictions
        busy_periods = predictor.predict_busy_periods()
        logger.info(f"Identified {busy_periods.get('busy_day_count', 0)} historical busy periods")
        
        # Capacity analysis
        capacity_analysis = predictor.analyze_capacity_requirements()
        logger.info("Completed capacity analysis")
        
        # Save prediction results
        prediction_results = {
            'daily_predictions': daily_predictions,
            'busy_periods': busy_periods,
            'capacity_analysis': capacity_analysis
        }
        
        prediction_file = EXPORTS_DIR / f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(prediction_file, 'w') as f:
            json_compatible_predictions = convert_to_json_compatible(prediction_results)
            json.dump(json_compatible_predictions, f, indent=2, default=str)
        
        logger.info(f"Prediction results saved to {prediction_file}")
        
        # Step 4: Generate Visualizations
        logger.info("Step 4: Generating visualizations")
        chart_gen = ChartGenerator()
        
        # Create charts directory
        charts_dir = EXPORTS_DIR / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # Generate key charts
        charts = generate_key_charts(chart_gen, data['admission'], analysis_results, prediction_results)
        
        # Save charts
        for chart_name, fig in charts.items():
            chart_file = charts_dir / f"{chart_name}.html"
            chart_gen.save_chart(fig, str(chart_file), 'html')
            logger.info(f"Saved chart: {chart_name}")
        
        # Step 5: Generate Summary Report
        logger.info("Step 5: Generating summary report")
        generate_summary_report(analysis_results, prediction_results)
        
        logger.info("Hospital Patient Analytics completed successfully!")
        
        # Print key insights
        print_key_insights(analysis_results, prediction_results)
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise


def convert_to_json_compatible(obj):
    """
    Convert numpy types and other non-JSON-serializable types to JSON-compatible types
    """
    if isinstance(obj, dict):
        return {k: convert_to_json_compatible(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_compatible(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


def generate_key_charts(chart_gen, admission_data, analysis_results, prediction_results):
    """
    Generate key charts for the analysis
    """
    charts = {}
    
    try:
        # Age distribution
        charts['age_distribution'] = chart_gen.create_age_distribution_chart(admission_data['AGE'])
        
        # Disease prevalence
        if 'disease_analysis' in analysis_results and 'disease_prevalence' in analysis_results['disease_analysis']:
            charts['disease_prevalence'] = chart_gen.create_disease_prevalence_chart(
                analysis_results['disease_analysis']['disease_prevalence']
            )
        
        # Temporal trends
        if 'temporal_analysis' in analysis_results:
            charts['temporal_trends'] = chart_gen.create_temporal_trends_chart(
                analysis_results['temporal_analysis']
            )
        
        # Predictions
        if 'daily_predictions' in prediction_results:
            charts['admission_predictions'] = chart_gen.create_admission_prediction_chart(
                prediction_results['daily_predictions']
            )
        
        # Risk factors
        if 'risk_analysis' in analysis_results:
            charts['risk_factors'] = chart_gen.create_risk_factor_analysis_chart(
                analysis_results['risk_analysis']
            )
        
        # Geographic distribution
        if 'geographical_analysis' in analysis_results:
            charts['geographic_distribution'] = chart_gen.create_geographical_distribution_chart(
                analysis_results['geographical_analysis']
            )
        
        # Outcomes
        charts['patient_outcomes'] = chart_gen.create_outcome_analysis_chart(admission_data['OUTCOME'])
        
        # Length of stay
        charts['length_of_stay'] = chart_gen.create_length_of_stay_analysis(admission_data['DURATION OF STAY'])
        
    except Exception as e:
        logger.error(f"Error generating charts: {e}")
    
    return charts


def generate_summary_report(analysis_results, prediction_results):
    """
    Generate a summary report
    """
    report_file = EXPORTS_DIR / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w') as f:
        f.write("HOSPITAL PATIENT ANALYTICS - SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Data Summary
        f.write("DATA SUMMARY\n")
        f.write("-" * 20 + "\n")
        if 'summary' in analysis_results:
            summary = analysis_results['summary']
            f.write(f"Total Admissions: {summary.get('total_admissions', 'N/A'):,}\n")
            f.write(f"Date Range: {summary.get('date_range', {}).get('start', 'N/A')} to {summary.get('date_range', {}).get('end', 'N/A')}\n")
            f.write(f"Average Patient Age: {summary.get('average_age', 0):.1f} years\n")
            f.write(f"Average Length of Stay: {summary.get('average_length_of_stay', 0):.1f} days\n\n")
        
        # Key Findings
        f.write("KEY FINDINGS\n")
        f.write("-" * 20 + "\n")
        
        # Age analysis
        if 'age_analysis' in analysis_results:
            age_dist = analysis_results['age_analysis'].get('age_distribution', {})
            if age_dist:
                most_common_age_group = max(age_dist.keys(), key=lambda x: age_dist[x])
                f.write(f"Most Common Age Group: {most_common_age_group}\n")
        
        # Disease analysis
        if 'disease_analysis' in analysis_results:
            disease_data = analysis_results['disease_analysis'].get('disease_prevalence', {})
            if disease_data:
                top_disease = max(disease_data.keys(), key=lambda x: disease_data[x].get('count', 0))
                f.write(f"Most Common Condition: {top_disease}\n")
        
        # Geographic analysis
        if 'geographical_analysis' in analysis_results:
            location_dist = analysis_results['geographical_analysis'].get('location_distribution', {})
            if location_dist:
                total_patients = sum(location_dist.values())
                rural_pct = (location_dist.get('R', 0) / total_patients) * 100
                f.write(f"Rural Patients: {rural_pct:.1f}%\n")
        
        f.write("\n")
        
        # Predictions Summary
        f.write("PREDICTIONS SUMMARY\n")
        f.write("-" * 20 + "\n")
        
        if 'busy_periods' in prediction_results:
            busy_data = prediction_results['busy_periods']
            f.write(f"Busy Day Threshold: {busy_data.get('threshold', 'N/A')} admissions\n")
            f.write(f"Historical Busy Days: {busy_data.get('busy_day_count', 'N/A')}\n")
            f.write(f"Predicted Future Busy Days: {busy_data.get('predicted_busy_days', 'N/A')}\n")
        
        if 'capacity_analysis' in prediction_results:
            capacity = prediction_results['capacity_analysis'].get('peak_requirements', {})
            f.write(f"Maximum Daily Capacity Needed: {capacity.get('max_daily_admissions', 'N/A')}\n")
            f.write(f"95th Percentile Capacity: {capacity.get('percentile_95', 'N/A')}\n")
    
    logger.info(f"Summary report saved to {report_file}")


def print_key_insights(analysis_results, prediction_results):
    """
    Print key insights to console
    """
    print("\n" + "=" * 60)
    print("KEY INSIGHTS FROM HOSPITAL PATIENT ANALYTICS")
    print("=" * 60)
    
    # Data overview
    if 'summary' in analysis_results:
        summary = analysis_results['summary']
        print(f"\n📊 DATA OVERVIEW:")
        print(f"   • Total admissions analyzed: {summary.get('total_admissions', 'N/A'):,}")
        print(f"   • Average patient age: {summary.get('average_age', 0):.1f} years")
        print(f"   • Average length of stay: {summary.get('average_length_of_stay', 0):.1f} days")
    
    # Top diseases
    if 'disease_analysis' in analysis_results:
        disease_data = analysis_results['disease_analysis'].get('disease_prevalence', {})
        if disease_data:
            top_diseases = sorted(disease_data.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:3]
            print(f"\n🦠 TOP MEDICAL CONDITIONS:")
            for i, (disease, data) in enumerate(top_diseases, 1):
                print(f"   {i}. {disease}: {data.get('count', 0)} cases ({data.get('percentage', 0):.1f}%)")
    
    # Capacity insights
    if 'capacity_analysis' in prediction_results:
        capacity = prediction_results['capacity_analysis'].get('peak_requirements', {})
        print(f"\n🏥 CAPACITY REQUIREMENTS:")
        print(f"   • Maximum daily admissions: {capacity.get('max_daily_admissions', 'N/A')}")
        print(f"   • 95th percentile capacity: {capacity.get('percentile_95', 'N/A')}")
        print(f"   • Recommended daily capacity: {capacity.get('percentile_90', 'N/A')}")
    
    # Busy periods
    if 'busy_periods' in prediction_results:
        busy_data = prediction_results['busy_periods']
        print(f"\n📈 BUSY PERIOD ANALYSIS:")
        print(f"   • Busy day threshold: {busy_data.get('threshold', 'N/A')} admissions")
        print(f"   • Historical busy days: {busy_data.get('busy_day_count', 'N/A')}")
        if 'predicted_busy_days' in busy_data:
            print(f"   • Predicted future busy days: {busy_data.get('predicted_busy_days', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check the exports/ directory for detailed results.")
    print("Run 'streamlit run dashboard/app.py' to view the interactive dashboard.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
