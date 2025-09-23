"""
Quick test script to run the hospital analytics system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

try:
    from src.main import main
    
    print("🏥 Starting Hospital Patient Analytics System...")
    print("=" * 60)
    
    # Run the main analysis
    main()
    
except Exception as e:
    print(f"❌ Error running analysis: {e}")
    print("\nTrying to run individual components...")
    
    try:
        from src.data_processing.data_loader import DataLoader
        print("✅ DataLoader imported successfully")
        
        from src.analysis.admission_analysis import AdmissionAnalyzer
        print("✅ AdmissionAnalyzer imported successfully")
        
        from src.prediction.admission_predictor import AdmissionPredictor
        print("✅ AdmissionPredictor imported successfully")
        
        from src.visualization.charts import ChartGenerator
        print("✅ ChartGenerator imported successfully")
        
        print("\n🎉 All components loaded successfully!")
        print("📊 You can now run the analysis using:")
        print("   python src/main.py")
        print("🌐 Or start the dashboard with:")
        print("   streamlit run dashboard/app.py")
        
    except Exception as e2:
        print(f"❌ Error importing components: {e2}")
        print("Please check the requirements.txt and install dependencies with:")
        print("   pip install -r requirements.txt")
