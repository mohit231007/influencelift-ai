[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$LaunchApp,
    [switch]$LaunchApi
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Resolve-PythonLauncher {
    $candidates = @(
        @{ Command = "py"; Arguments = @("-3.12") },
        @{ Command = "py"; Arguments = @("-3.11") },
        @{ Command = "py"; Arguments = @("-3.10") },
        @{ Command = "python"; Arguments = @() }
    )

    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Command -ErrorAction SilentlyContinue)) {
            continue
        }

        & $candidate.Command @($candidate.Arguments) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $candidate
        }
    }

    throw "Python 3.10, 3.11, or 3.12 was not found. Install Python 3.12 and rerun this script."
}

$launcher = Resolve-PythonLauncher
$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Step "Creating the virtual environment"
    & $launcher.Command @($launcher.Arguments) -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}

if (-not $SkipInstall) {
    Write-Step "Installing project and QA dependencies"
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

    & $venvPython -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { throw "Project installation failed." }
}

Write-Step "Running lint checks"
& $venvPython -m ruff check .
if ($LASTEXITCODE -ne 0) { throw "Ruff checks failed." }

Write-Step "Running automated tests"
& $venvPython -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }

Write-Step "Compiling Python modules"
& $venvPython -m compileall -q src api app scripts
if ($LASTEXITCODE -ne 0) { throw "Compilation failed." }

Write-Step "Generating deterministic QA data"
& $venvPython scripts/generate_demo_data.py --rows 500 --seed 42 --output data/generated/qa_train.csv
if ($LASTEXITCODE -ne 0) { throw "Demo-data generation failed." }

Write-Step "Training a QA model bundle"
& $venvPython scripts/train.py --input data/generated/qa_train.csv --model-output artifacts/qa_model_bundle.joblib --metrics-output artifacts/qa_metrics.json --folds 3 --model-version qa-local
if ($LASTEXITCODE -ne 0) { throw "Model training failed." }

Write-Step "Generating batch predictions"
& $venvPython scripts/predict.py --input data/sample/synthetic_campaigns.csv --model artifacts/qa_model_bundle.joblib --output artifacts/qa_predictions.csv
if ($LASTEXITCODE -ne 0) { throw "Batch prediction failed." }

Write-Step "QA completed successfully"
Write-Host "Metrics:      artifacts\qa_metrics.json" -ForegroundColor Green
Write-Host "Predictions:  artifacts\qa_predictions.csv" -ForegroundColor Green

if ($LaunchApp) {
    Write-Step "Launching Streamlit at http://localhost:8501"
    Start-Process -FilePath $venvPython -ArgumentList @("-m", "streamlit", "run", "app/Home.py") -WorkingDirectory $RepoRoot
}

if ($LaunchApi) {
    Write-Step "Launching FastAPI at http://localhost:8000/docs"
    Start-Process -FilePath $venvPython -ArgumentList @("-m", "uvicorn", "api.main:app", "--reload", "--port", "8000") -WorkingDirectory $RepoRoot
}

if ($LaunchApp -or $LaunchApi) {
    Write-Host "Services were started in separate processes. Close those process windows when QA is complete." -ForegroundColor Yellow
}
