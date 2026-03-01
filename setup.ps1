$ErrorActionPreference = "Continue"

$LogFile = "$PSScriptRoot\setup.log"
Start-Transcript -Path $LogFile -Append

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "      SupMTI Intelligent Chatbot - Automated Setup       " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for API Keys
Write-Host "Welcome! Let's configure your Chatbot environments." -ForegroundColor Yellow
$openrouterKey = Read-Host "1. Paste your OpenRouter API Key (press Enter to skip)"
$openaiKey = Read-Host "2. Paste your OpenAI API Key for Voice (press Enter to skip)"
$fallbackKey = Read-Host "3. Paste your Fallback LLM Key (press Enter to skip)"

# Create .env
$envPath = "$PSScriptRoot\backend\.env"
$envExamplePath = "$PSScriptRoot\backend\.env.example"

Write-Progress -Activity "SupMTI Setup" -Status "Creating Configurations" -PercentComplete 10

if (Test-Path $envExamplePath) {
    $envContent = Get-Content $envExamplePath -Raw
    
    if (-not [string]::IsNullOrWhiteSpace($openrouterKey)) {
        $envContent = $envContent -replace "OPENROUTER_API_KEY=.*", "OPENROUTER_API_KEY=$openrouterKey"
    }

    if ($envContent -notmatch "OPENAI_API_KEY=") {
        $envContent += "`nOPENAI_API_KEY=$openaiKey"
    } else {
        $envContent = $envContent -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$openaiKey"
    }
    
    if ($envContent -notmatch "FALLBACK_API_KEY=") {
        $envContent += "`nFALLBACK_API_KEY=$fallbackKey"
    } else {
        $envContent = $envContent -replace "FALLBACK_API_KEY=.*", "FALLBACK_API_KEY=$fallbackKey"
    }
    
    # Also update the embedding model just in case it's an old .env.example
    $envContent = $envContent -replace "EMBEDDING_MODEL=all-MiniLM-L6-v2", "EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2"

    Set-Content -Path $envPath -Value $envContent
    Write-Host "[Info] Generated your new backend/.env file!" -ForegroundColor Green
} else {
    Write-Host "[Warning] backend/.env.example not found!" -ForegroundColor Red
}

# 1. Setup Backend (Python)
Write-Progress -Activity "SupMTI Setup" -Status "Setting up Python Backend Environment" -PercentComplete 30
Set-Location "$PSScriptRoot\backend"

if (-not (Test-Path "venv")) {
    Write-Host "[Info] Creating Python virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Progress -Activity "SupMTI Setup" -Status "Installing Backend Dependencies" -PercentComplete 50
Write-Host "[Info] Installing backend dependencies (this will take a minute..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install --upgrade pip | Out-Default
& .\venv\Scripts\pip.exe install -r requirements.txt | Out-Default

Write-Progress -Activity "SupMTI Setup" -Status "Ingesting Knowledge Base into AI Vector Database" -PercentComplete 75
Write-Host "[Info] Ingesting Mock Knowledge Base into ChromaDB..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m scripts.ingest | Out-Default

Set-Location "$PSScriptRoot"

# 2. Setup Frontend (Node.js)
Write-Progress -Activity "SupMTI Setup" -Status "Setting up Frontend Environment" -PercentComplete 85
Set-Location "$PSScriptRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "[Info] Installing frontend Node modules..." -ForegroundColor Yellow
    npm install | Out-Default
}
Set-Location "$PSScriptRoot"

Write-Progress -Activity "SupMTI Setup" -Status "Finishing Up" -PercentComplete 100
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Success! The SupMTI Chatbot setup is complete." -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching background servers in new windows..." -ForegroundColor Yellow

# Launch
Start-Process "cmd.exe" -ArgumentList "/k cd backend && venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
Start-Process "cmd.exe" -ArgumentList "/k cd frontend && npm run dev" -WindowStyle Normal

Write-Host "The Frontend is available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "The Backend docs are available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "A full log of this setup was saved to setup.log" -ForegroundColor Gray

Stop-Transcript
Read-Host -Prompt "Press Enter to exit setup..."
