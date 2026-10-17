param (
    [string]$Version
)

# Calculate milliseconds since Unix epoch
$unixEpoch = [datetime]"1970-01-01T00:00:00Z"
$currentDateTime = [datetime]::UtcNow
$timeSpan = $currentDateTime - $unixEpoch
$millisecondsSinceEpoch = [math]::Round($timeSpan.TotalMilliseconds)

$distDir = "C:\Users\freqn\Projects\Meile 2.0\dist"
$buildDir = "C:\Users\freqn\Projects\Meile 2.0\build"
$srcBinDir = "C:\Users\freqn\Projects\Meile 2.0\src\bin"
$signTool = "C:\certs\signtool.exe"
$certPath = "C:\certs\meile.pfx"
$certPass = 'vkirkvC@Mgq^6Sn4t^ZtqTe*n63qFuio'
$timestampServer = "http://timestamp.digicert.com"

if (Test-Path -Path $distDir) {
    Remove-Item -Path $distDir -Recurse -Force
}
if (Test-Path -Path $buildDir) {
    Remove-Item -Path $buildDir -Recurse -Force
}

$filePath = "C:\Users\freqn\Projects\Meile 2.0\src\typedef\konstants.py"
$fileContent = Get-Content -Path $filePath -Raw
$fileContent = $fileContent -replace 'VERSION\s*=\s*".*"', "VERSION = `"$Version`""
$fileContent = $fileContent -replace 'BUILD\s*=\s*".*"', "BUILD = `"$millisecondsSinceEpoch`""
Set-Content -Path $filePath -Value $fileContent

# Sign all .exe files in src/bin recursively (before PyInstaller bundles them)
Write-Host "Signing bundled executables in $srcBinDir ..."
$exeFiles = Get-ChildItem -Path $srcBinDir -Recurse -Filter *.exe
foreach ($exe in $exeFiles) {
    Write-Host "  Signing: $($exe.FullName)"
    & $signTool sign /fd SHA256 /f $certPath /p $certPass /tr $timestampServer /td SHA256 "$($exe.FullName)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Signing failed for $($exe.FullName)" -ForegroundColor Red
    }
}

# Activate virtual environment so pyinstaller and dependencies are available
$venvPath = "C:\Users\freqn\Projects\Meile 2.0\meile2.0"
. "$venvPath\Scripts\Activate.ps1"

pyinstaller meile_gui.spec

# Sign the main built executable
Write-Host "Signing main executable: C:\Users\freqn\Projects\Meile 2.0\dist\Meile.exe"
& $signTool sign /fd SHA256 /f $certPath /p $certPass /tr $timestampServer /td SHA256 "C:\Users\freqn\Projects\Meile 2.0\dist\Meile.exe"