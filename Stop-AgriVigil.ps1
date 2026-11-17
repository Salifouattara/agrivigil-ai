$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot '.local/processes.json'
if (!(Test-Path $statePath)) { Write-Host 'Aucun processus AgriVigil enregistre.'; exit 0 }
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$expected = @{ backend = (Join-Path $PSScriptRoot 'backend/manage.py'); frontend = (Join-Path $PSScriptRoot 'frontend/node_modules/vite/bin/vite.js') }
foreach ($service in @('backend', 'frontend')) {
    $taskProcessId = [int]$state.$service
    $taskProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $taskProcessId" -ErrorAction SilentlyContinue
    if ($taskProcess -and $taskProcess.CommandLine.Replace('/', '\').Contains($expected[$service].Replace('/', '\'))) {
        Stop-Process -Id $taskProcessId
        Write-Host "$service arrete."
    }
}
