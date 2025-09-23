# 🏥 Hospital Patient Analytics - Setup Instructions

## 🚀 Quick Start (Automated Setup)

We've created automated setup scripts that will handle everything for you:

### Option 1: PowerShell Script (Recommended)
```powershell
# Run this command in PowerShell (as Administrator if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_and_run.ps1
```

### Option 2: Batch File (Alternative)
```cmd
# Double-click or run in Command Prompt
setup_and_run.bat
```

## 📋 What These Scripts Do

1. **🔍 Check Python Installation** - Verifies Python is available
2. **📦 Create Virtual Environment** - Sets up isolated Python environment
3. **⬆️ Upgrade Pip** - Ensures latest package installer
4. **📥 Install Requirements** - Installs all necessary packages
5. **🧪 Run System Tests** - Verifies all components work
6. **📊 Run Analysis** - Performs comprehensive data analysis
7. **📁 Create Directories** - Sets up export folders
8. **🌐 Launch Dashboard** - Starts interactive Streamlit dashboard

## 🛠️ Manual Setup (If Scripts Don't Work)

If the automated scripts don't work, follow these manual steps:

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Requirements
```bash
pip install -r requirements_simple.txt
```

### Step 4: Run Tests
```bash
python test_system.py
```

### Step 5: Run Analysis
```bash
python run_demo.py
```

### Step 6: Start Dashboard
```bash
streamlit run dashboard/app.py
```

## 📊 System Requirements

- **Python**: 3.8 - 3.11 (3.10 recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10/11, macOS, or Linux

## 🌐 Accessing the Dashboard

Once the scripts complete, the dashboard will automatically open in your web browser at:
- **URL**: http://localhost:8501
- **Features**: Interactive charts, data exploration, real-time analysis

## 🔧 Troubleshooting

### PowerShell Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found
- Install Python 3.10 from [python.org](https://python.org)
- Make sure Python is added to your PATH

### Port 8501 Already in Use
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Virtual Environment Issues
- Delete the `venv` folder and run the script again
- Or manually create: `python -m venv venv`

## 📁 Project Structure

```
Hospital Analytics/
├── 📄 setup_and_run.ps1      # PowerShell setup script
├── 📄 setup_and_run.bat      # Batch setup script
├── 📁 venv/                  # Virtual environment (created by scripts)
├── 📁 src/                   # Source code
├── 📁 dashboard/             # Streamlit dashboard
├── 📁 exports/               # Generated reports and charts
└── 📁 admission hospital data/  # Data files
```

## 🎯 Next Steps After Setup

1. **📊 Explore Dashboard** - Interactive data visualization
2. **📓 Open Jupyter Notebook** - `jupyter notebook notebooks/01_data_exploration.ipynb`
3. **📈 View Generated Charts** - Check `exports/charts/` folder
4. **📋 Read Analysis Reports** - Check `exports/reports/` folder

## 🆘 Need Help?

If you encounter any issues:
1. Check the terminal/command prompt output for error messages
2. Ensure Python 3.10 is installed and accessible
3. Try running the manual setup steps one by one
4. Check that all data files are in the `admission hospital data/` folder

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ All 4 system tests pass
- ✅ Analysis completes with key insights
- ✅ Dashboard opens in your browser
- ✅ Interactive charts are visible and responsive
