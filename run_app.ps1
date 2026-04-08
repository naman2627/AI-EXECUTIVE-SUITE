# run_app.ps1 - PowerShell script to run the app
$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot

Write-Host "[1/3] Killing processes on ports 8000 and 5173..." -ForegroundColor Cyan
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Write-Host "    Ports cleared." -ForegroundColor Green

Write-Host "[2/3] Loading .env..." -ForegroundColor Cyan
$EnvPath = Join-Path $Root ".env"
if (Test-Path $EnvPath) {
    Get-Content $EnvPath | ForEach-Object {
        $line = $_.Trim()
        if ($line -match "^([^#=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove surrounding quotes if they exist
            $value = $value -replace '^"|"$', ''
            $value = $value -replace "^'|'$", ""
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    $preview = if ($env:GROQ_API_KEY) { $env:GROQ_API_KEY.Substring(0, [math]::Min(12, $env:GROQ_API_KEY.Length)) + "..." } else { "NOT FOUND" }
    Write-Host "    .env loaded. GROQ_API_KEY = $preview" -ForegroundColor Green
} else {
    Write-Host "    No .env file found!" -ForegroundColor Yellow
}

Write-Host "[3/3] Starting servers..." -ForegroundColor Cyan

# Start Backend
$BackendCmd = "cd '$Root'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd

# Start Frontend
$FrontendCmd = "cd '$Root\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd

Write-Host "`nBoth servers launched in separate windows!" -ForegroundColor Green
Write-Host "  Frontend -> http://localhost:5173"
Write-Host "  Backend  -> http://127.0.0.1:8000"
Write-Host "`nClose those windows to stop the servers."
