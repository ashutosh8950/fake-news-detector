$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$prototypeDir = Join-Path $repoRoot "evaluation_results\new_release_candidate_2026-10-22\task44_synthetic_prototype"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Write-Error "Safe verification stopped: expected virtual-environment interpreter was not found at $python"
    exit 1
}

Push-Location $repoRoot
try {
    Write-Host "[1/2] Model-free local readiness smoke tests"
    & $python -m pytest -q tests/smoke/test_local_readiness_smoke.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke-test group failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }

    Write-Host "[2/2] Isolated synthetic Track B regression tests"
    & $python -m unittest discover -s $prototypeDir -p "test_synthetic*.py" -q
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Synthetic regression group failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }

    Write-Host "SAFE LOCAL VERIFICATION PASSED: both approved model-free groups completed."
    exit 0
}
finally {
    Pop-Location
}
