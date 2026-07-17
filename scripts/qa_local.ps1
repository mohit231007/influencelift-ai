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

function Test-PythonCandidate {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$Arguments = @()
    )

    # A stale Windows Python launcher can exist even when the referenced
    # interpreter has been uninstalled. Native stderr must not stop the
    # entire QA script before the next candidate is tested.
    try {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $versionOutput = & $Command @Arguments -c "import sys; print('.'.join(map(str, sys.version_info[:3]))); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>&1
        $exitCode = $LASTEXITCODE
    }
    catch {
        $versionOutput = $null
        $exitCode = 1
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }

    if ($exitCode -ne 0) {
        return $null
    }

    $version = ($versionOutput | Select-Object -Last 1).ToString().Trim()
    return @{
        Command = $Command
        Arguments = $Arguments
        Version = $version
    }
}

function Resolve-PythonLauncher {
    # Prefer direct executables because the Windows py launcher may contain
    # stale registrations for Python versions that are no longer installed.
    $candidates = @(
        @{ Command = "python"; Arguments = @() },
        @{ Command = "python3"; Arguments = @() },
        @{ Command = "py"; Arguments = @("-3.13") },
        @{ Command = "py"; Arguments = @("-3.12") },
        @{ Command = "py"; Arguments = @("-3.11") },
        @{ Command = "py"; Arguments = @("-3.10") },
        @{ Command = "py"; Arguments = @("-3") }
    )

    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Command -ErrorAction SilentlyContinue)) {
            continue
        }

        $resolved = Test-PythonCandidate -Command $candidate.Command -Arguments $candidate.Arguments
        if ($null -ne $resolved) {
            return $resolved
        }
    }

    throw "Python 3.10 or newer was not found. Install a supported Python version and rerun this script."
}

$launcher = Resolve-PythonLauncher
$launcherLabel = "$($launcher.Command) $($launcher.Arguments -join ' ')".Trim()
Write-Host "Using Python $($launcher.Version) via: $launcherLabel" -ForegroundColor Green

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
