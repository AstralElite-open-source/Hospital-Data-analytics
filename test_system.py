"""
Test script for Hospital Patient Analytics system
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

def test_data_loading():
    """Test data loading functionality"""
    try:
        from data_processing.data_loader import DataLoader
        
        print("📊 Testing data loading...")
        loader = DataLoader()
        
        # Try to load admission data
        admission_data = loader.load_admission_data()
        print(f"✅ Loaded {len(admission_data)} admission records")
        
        # Get summary
        summary = loader.get_data_summary()
        print("✅ Generated data summary")
        
        return True, admission_data
        
    except Exception as e:
        print(f"❌ Error in data loading: {e}")
        return False, None

def test_analysis():
    """Test analysis functionality"""
    try:
        from analysis.admission_analysis import AdmissionAnalyzer
        
        print("🔍 Testing analysis...")
        
        # Load data first
        success, admission_data = test_data_loading()
        if not success:
            return False
            
        # Run analysis
        analyzer = AdmissionAnalyzer(admission_data)
        
        # Test individual analysis methods
        age_analysis = analyzer.analyze_admission_rates_by_age()
        print("✅ Age analysis completed")
        
        disease_analysis = analyzer.analyze_admission_rates_by_disease()
        print("✅ Disease analysis completed")
        
        temporal_analysis = analyzer.analyze_temporal_patterns()
        print("✅ Temporal analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return False

def test_visualization():
    """Test visualization functionality"""
    try:
        from visualization.charts import ChartGenerator
        
        print("📈 Testing visualization...")
        chart_gen = ChartGenerator()
        print("✅ ChartGenerator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in visualization: {e}")
        return False

def test_prediction():
    """Test prediction functionality"""
    try:
        from prediction.admission_predictor import AdmissionPredictor
        
        print("🔮 Testing prediction...")
        
        # Load data first
        success, admission_data = test_data_loading()
        if not success:
            return False
            
        predictor = AdmissionPredictor(admission_data)
        print("✅ AdmissionPredictor initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 Hospital Patient Analytics - System Test")
    print("=" * 60)
    
    # Check if data files exist
    data_files = [
        "admission hospital data/HDHI Admission data.csv",
        "admission hospital data/HDHI Mortality Data.csv", 
        "admission hospital data/HDHI Pollution Data.csv",
        "admission hospital data/table_headings.csv"
    ]
    
    print("📁 Checking data files...")
    all_files_exist = True
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n⚠️  Some data files are missing. Please ensure all data files are in the correct location.")
        return
    
    # Test components
    tests = [
        ("Data Loading", test_data_loading),
        ("Analysis", test_analysis),
        ("Visualization", test_visualization),
        ("Prediction", test_prediction)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_name == "Data Loading":
                success, _ = test_func()
            else:
                success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\n📊 Next steps:")
        print("1. Run analysis: python -m src.main")
        print("2. Start dashboard: streamlit run dashboard/app.py")
        print("3. Explore data: jupyter notebook notebooks/01_data_exploration.ipynb")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    main()
