<#
.SYNOPSIS
    Marec Insights Studio - Setup & Launch Script
#>
Write-Host "Setting up Marec Insights Studio..." -ForegroundColor Green
pip install -r requirements.txt
streamlit run app.py
