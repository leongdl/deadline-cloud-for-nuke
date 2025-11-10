# Update Nuke Submitter Python Source Files
# Copies Python files from src to C:\Users\RDP\DeadlineCloudForNukeSubmitter\deadline

param(
    [switch]$DryRun
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourcePath = Join-Path (Split-Path -Parent $scriptDir) "src\deadline"
$destPath = "C:\Users\RDP\DeadlineCloudForNukeSubmitter\deadline"

# Check if destination exists
if (-not (Test-Path $destPath)) {
    Write-Host "Destination path does not exist: $destPath" -ForegroundColor Red
    exit 1
}

# Check if source exists
if (-not (Test-Path $sourcePath)) {
    Write-Host "Source path does not exist: $sourcePath" -ForegroundColor Red
    exit 1
}

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be copied" -ForegroundColor Yellow
    Write-Host "Finding Python and YAML files that would be updated from $sourcePath to $destPath..." -ForegroundColor Green
} else {
    Write-Host "Copying Python and YAML files from $sourcePath to $destPath..." -ForegroundColor Green
}

# Get all Python and YAML files recursively from src
$pythonFiles = Get-ChildItem -Path $sourcePath -Include "*.py", "*.yaml" -Recurse

$copiedCount = 0
$newCount = 0
$skippedCount = 0

foreach ($file in $pythonFiles) {
    # Get relative path from source
    $relativePath = $file.FullName.Substring((Resolve-Path $sourcePath).Path.Length + 1)
    $destFile = Join-Path $destPath $relativePath
    
    # Check if destination file exists
    $fileExists = Test-Path $destFile
    
    if ($DryRun) {
        if ($fileExists) {
            Write-Host "  Would update: $relativePath" -ForegroundColor Cyan
            $copiedCount++
        } else {
            Write-Host "  Would create new: $relativePath" -ForegroundColor Green
            $newCount++
        }
    } else {
        # Create destination directory if needed
        $destDir = Split-Path $destFile -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Copy the file
        Copy-Item -Path $file.FullName -Destination $destFile -Force
        
        if ($fileExists) {
            Write-Host "  Updated: $relativePath" -ForegroundColor Cyan
            $copiedCount++
        } else {
            Write-Host "  Created new: $relativePath" -ForegroundColor Green
            $newCount++
        }
    }
}

if ($DryRun) {
    Write-Host "`nDry run complete! Would update: $copiedCount, Would create new: $newCount, Would skip: $skippedCount" -ForegroundColor Green
} else {
    Write-Host "`nComplete! Updated: $copiedCount, Created new: $newCount, Skipped: $skippedCount" -ForegroundColor Green
}
