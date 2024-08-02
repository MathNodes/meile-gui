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

pyinstaller meile_gui.spec