param(
  [string]$Name = "SubtitleCollage"
)

$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
  Push-Location frontend
  npm run build
  Pop-Location

  Push-Location backend
  if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3.11 -m venv .venv
  }
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
  .\.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --clean `
    --name $Name `
    --add-data "..\frontend\dist;frontend\dist" `
    --add-data "app;app" `
    desktop.py
  Pop-Location

  New-Item -ItemType Directory -Force "release" | Out-Null
  if (Test-Path "release\$Name") {
    Remove-Item -Recurse -Force "release\$Name"
  }
  Copy-Item -Recurse -Force "backend\dist\$Name" "release\$Name"
  New-Item -ItemType Directory -Force "release\$Name\data" | Out-Null

  Write-Host ""
  Write-Host "Build complete: $PSScriptRoot\release\$Name\$Name.exe"
}
finally {
  Pop-Location
}
