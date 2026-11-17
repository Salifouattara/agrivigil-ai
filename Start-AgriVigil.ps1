$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.local'
$backendDir = Join-Path $projectRoot 'backend'
$frontendDir = Join-Path $projectRoot 'frontend'
$managePath = Join-Path $backendDir 'manage.py'
$vitePath = Join-Path $frontendDir 'node_modules/vite/bin/vite.js'
if (!(Test-Path (Join-Path $backendDir '.env'))) { throw 'Le fichier backend/.env est absent.' }
if (!(Test-Path $vitePath)) { throw 'Installe les dependances avec npm install dans frontend.' }
foreach ($port in @(5185, 5173)) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
        throw "Le port $port est deja utilise. Si AgriVigil tourne, ouvre http://127.0.0.1:5173 ; pour le relancer, utilise Stop-AgriVigil.ps1."
    }
}
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$pythonPath = (Get-Command python).Source
$nodePath = (Get-Command node).Source
& $pythonPath $managePath migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'La preparation de la base a echoue.' }
$backendProcess = Start-Process -FilePath $pythonPath -WorkingDirectory $backendDir -ArgumentList @('-u', ('"' + $managePath + '"'), 'runserver', '127.0.0.1:5185', '--noreload') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeDir 'backend.out.log') -RedirectStandardError (Join-Path $runtimeDir 'backend.err.log')
$frontendProcess = Start-Process -FilePath $nodePath -WorkingDirectory $frontendDir -ArgumentList @(('"' + $vitePath + '"'), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeDir 'frontend.out.log') -RedirectStandardError (Join-Path $runtimeDir 'frontend.err.log')
@{ backend = $backendProcess.Id; frontend = $frontendProcess.Id } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimeDir 'processes.json')
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    try {
        $health = Invoke-RestMethod 'http://127.0.0.1:5185/api/health/' -TimeoutSec 2
        $page = Invoke-WebRequest 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 2
        if ($health.service -eq 'agrivigil' -and $page.StatusCode -eq 200) {
            Write-Host 'AgriVigil est pret : http://127.0.0.1:5173/'
            Write-Host 'Arret : .\Stop-AgriVigil.ps1'
            exit 0
        }
    } catch { Start-Sleep -Milliseconds 500 }
}
throw 'Demarrage incomplet. Consulter les fichiers de log dans .local.'
