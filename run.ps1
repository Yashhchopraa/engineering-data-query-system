param(

    [Parameter(Position = 0)]

    [string]$Command = "help"

)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $ProjectRoot


if ($Command -eq "start") {

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host " Engineering Data Query System" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    # ----------------------------------------
    # CHECK PYTHON ENVIRONMENT
    # ----------------------------------------

    $VenvActivate =
        Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

    if (-not (Test-Path $VenvActivate)) {

        Write-Host "ERROR: .venv not found." -ForegroundColor Red

        Write-Host ""
        Write-Host "Create it with:"
        Write-Host "python -m venv .venv"
        Write-Host ""

        exit 1

    }


    # ----------------------------------------
    # START BACKEND
    # ----------------------------------------

    Write-Host "Starting backend API..." -ForegroundColor Yellow

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$ProjectRoot'; & '$VenvActivate'; python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
    )


    # Give backend a moment to start

    Start-Sleep -Seconds 2


    # ----------------------------------------
    # CHECK FRONTEND
    # ----------------------------------------

    $FrontendPath =
        Join-Path $ProjectRoot "frontend"

    if (-not (Test-Path $FrontendPath)) {

        Write-Host "ERROR: frontend folder not found." -ForegroundColor Red

        exit 1

    }


    # ----------------------------------------
    # START FRONTEND
    # ----------------------------------------

    Write-Host "Starting frontend..." -ForegroundColor Yellow

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$FrontendPath'; npm run dev"
    )


    # ----------------------------------------
    # DONE
    # ----------------------------------------

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host " Application started successfully!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""

    Write-Host "Backend:"
    Write-Host "http://127.0.0.1:8000"

    Write-Host ""

    Write-Host "Frontend:"
    Write-Host "http://localhost:5173"

    Write-Host ""

    Write-Host "Two terminal windows have been opened."
    Write-Host ""

}


elseif ($Command -eq "generate") {

    python scripts\generate_data.py

}


elseif ($Command -eq "benchmark") {

    python scripts\run_benchmarks.py

}


elseif ($Command -eq "tree") {

    tree /F

}


else {

    Write-Host ""

    Write-Host "Engineering Data Query System"

    Write-Host ""

    Write-Host "Available commands:"

    Write-Host ""

    Write-Host ".\run.ps1 start"
    Write-Host "    Start backend API and frontend"

    Write-Host ""

    Write-Host ".\run.ps1 generate"
    Write-Host "    Generate engineering data"

    Write-Host ""

    Write-Host ".\run.ps1 benchmark"
    Write-Host "    Run benchmarks"

    Write-Host ""

    Write-Host ".\run.ps1 tree"
    Write-Host "    Display project tree"

    Write-Host ""

}