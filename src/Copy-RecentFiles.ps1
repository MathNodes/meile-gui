<#
.SYNOPSIS
    Copies files modified within N days from the current directory to a
    specified destination, preserving the directory structure.

.DESCRIPTION
    Prompts the user for a destination path and a number of days. Recursively
    finds all files in the current directory modified within the last N days
    and copies them to the destination, maintaining the relative folder layout.
#>

# Prompt user for inputs
$Destination = Read-Host "Enter the destination path"
$DaysInput   = Read-Host "Enter how many days old (files modified within the last N days)"

# Validate days input
[int]$Days = 0
if (-not [int]::TryParse($DaysInput, [ref]$Days) -or $Days -lt 0) {
    Write-Error "Invalid number of days. Please enter a non-negative integer."
    exit 1
}

# Validate / create destination
if (-not (Test-Path -LiteralPath $Destination)) {
    try {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
        Write-Host "Created destination directory: $Destination" -ForegroundColor Cyan
    }
    catch {
        Write-Error "Failed to create destination '$Destination': $_"
        exit 1
    }
}

# Resolve full paths
$SourceRoot      = (Get-Location).Path
$DestinationRoot = (Resolve-Path -LiteralPath $Destination).Path
$CutoffDate      = (Get-Date).AddDays(-$Days)

Write-Host ""
Write-Host "Source:      $SourceRoot"
Write-Host "Destination: $DestinationRoot"
Write-Host "Cutoff date: $CutoffDate (files modified after this date)"
Write-Host ""

# Find and copy files
$Files = Get-ChildItem -Path $SourceRoot -Recurse -File |
         Where-Object { $_.LastWriteTime -ge $CutoffDate }

if (-not $Files) {
    Write-Host "No files found matching the criteria." -ForegroundColor Yellow
    exit 0
}

$CopiedCount = 0
foreach ($File in $Files) {
    # Compute path relative to the source root
    $RelativePath = $File.FullName.Substring($SourceRoot.Length).TrimStart('\','/')
    $TargetPath   = Join-Path -Path $DestinationRoot -ChildPath $RelativePath
    $TargetDir    = Split-Path -Path $TargetPath -Parent

    # Ensure target directory exists
    if (-not (Test-Path -LiteralPath $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

    try {
        Copy-Item -LiteralPath $File.FullName -Destination $TargetPath -Force
        Write-Host "Copied: $RelativePath" -ForegroundColor Green
        $CopiedCount++
    }
    catch {
        Write-Warning "Failed to copy '$($File.FullName)': $_"
    }
}

Write-Host ""
Write-Host "Done. Copied $CopiedCount file(s) to $DestinationRoot" -ForegroundColor Cyan