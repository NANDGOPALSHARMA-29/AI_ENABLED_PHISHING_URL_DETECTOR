# prepare_and_train.ps1
# Usage: run from phishdetect\data OR run with full path.
# This script:
#  - converts openphish_raw.txt -> openphish_norm.csv (or sample)
#  - converts benign_raw.csv -> benign_norm.csv
#  - optionally triggers training in backend (requires venv & train_real.py present)
#
# Edit $SAMPLE_COUNT to limit number of phish records used (0 = use all)

param(
    [int]$SAMPLE_COUNT = 0,          # 0 => use whole openphish list; else use first N
    [switch]$RunTraining             # add -RunTraining to call backend train_real.py after conversion
)

$ErrorActionPreference = "Stop"

# Paths (adjust if your folder structure differs)
$DataDir = Get-Location
$BackendDir = Join-Path $DataDir "..\backend" | Resolve-Path -Relative
$OpenPhishRaw = Join-Path $DataDir "openphish_raw.txt"
$OpenPhishNorm = Join-Path $DataDir "openphish_norm.csv"
$OpenPhishSample = Join-Path $DataDir "openphish_sample.csv"
$BenignRaw = Join-Path $DataDir "benign_raw.csv"
$BenignNorm = Join-Path $DataDir "benign_norm.csv"

Write-Host "Data dir: $DataDir"
Write-Host "Backend dir (expected): $BackendDir"

# 1) Check files exist
if (-not (Test-Path $OpenPhishRaw)) {
    Write-Error "openphish_raw.txt not found in $DataDir. Download it first (https://openphish.com/feed.txt)."
    exit 1
}
if (-not (Test-Path $BenignRaw)) {
    Write-Error "benign_raw.csv not found in $DataDir. Create it with a 'domain' column."
    exit 1
}

# 2) Convert or sample OpenPhish -> CSV
if ($SAMPLE_COUNT -gt 0) {
    Write-Host "Creating sample of first $SAMPLE_COUNT lines from openphish..."
    # create header
    "url,label" | Out-File -FilePath $OpenPhishSample -Encoding utf8
    Get-Content $OpenPhishRaw -TotalCount $SAMPLE_COUNT | ForEach-Object { "$_ ,1" } >> $OpenPhishSample
    Write-Host "Saved sample CSV -> $OpenPhishSample"
    # also copy to openphish_norm.csv (train script picks up *.csv)
    Copy-Item -Path $OpenPhishSample -Destination $OpenPhishNorm -Force
    Write-Host "Also copied sample to $OpenPhishNorm"
} else {
    Write-Host "Converting entire openphish feed to CSV: $OpenPhishNorm"
    "url,label" | Out-File -FilePath $OpenPhishNorm -Encoding utf8
    Get-Content $OpenPhishRaw | ForEach-Object { "$_ ,1" } >> $OpenPhishNorm
    Write-Host "Saved $OpenPhishNorm"
}

# 3) Convert benign_raw.csv -> benign_norm.csv
Write-Host "Converting benign_raw.csv -> benign_norm.csv"
# We'll call python inline to use pandas safely (handles commas/newlines)
$pyCmd = @"
import pandas as pd
df = pd.read_csv(r'$BenignRaw', dtype=str)
if 'domain' in df.columns:
    df = df[['domain']].dropna().drop_duplicates()
    df['url'] = 'https://' + df['domain'].str.strip()
else:
    df['url'] = df.iloc[:,0]
out = df[['url']].dropna().drop_duplicates()
out['label'] = 0
out.to_csv(r'$BenignNorm', index=False)
print('Saved benign_norm.csv rows:', len(out))
"@
# run python -c with here-string
python - <<PY -c $pyCmd
PY

Write-Host "Created benign_norm.csv at $BenignNorm"

# 4) Summary
Write-Host "`nFiles now in $DataDir:"
Get-ChildItem -Filter *.csv | Select-Object Name, Length
Write-Host "`nConversion complete."

# 5) Optional: Run training (if requested)
if ($RunTraining) {
    Write-Host "`nRunning training in backend..."
    Push-Location $BackendDir
    # If you use venv, adjust activation command below. Example for venv\Scripts\Activate.ps1
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        Write-Host "Activating venv..."
        & .\venv\Scripts\Activate.ps1
    }
    # run training
    python train_real.py
    Pop-Location
    Write-Host "Training finished (check backend output)."
}
