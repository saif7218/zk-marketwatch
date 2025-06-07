# Simple Deployment Script for Streamlit App

# 1. Create .streamlit directory if it doesn't exist
if (-not (Test-Path ".streamlit")) {
    New-Item -ItemType Directory -Path ".streamlit" | Out-Null
    Write-Host "✅ Created .streamlit directory"
}

# 2. Create config.toml
@'
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
'@ | Out-File -FilePath ".streamlit/config.toml" -Encoding utf8
Write-Host "✅ Created Streamlit config"

# 3. Copy requirements.txt to root if it exists in zk_dashboard
if (Test-Path "zk_dashboard/requirements.txt") {
    Copy-Item -Path "zk_dashboard/requirements.txt" -Destination "." -Force
    Write-Host "✅ Copied requirements.txt to root"
}

# 4. Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# 5. Run the Streamlit app
Write-Host "🚀 Starting Streamlit app..."
streamlit run zk_dashboard/app.py
