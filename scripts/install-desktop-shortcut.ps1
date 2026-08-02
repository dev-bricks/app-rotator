[CmdletBinding()]
param(
    [string]$ShortcutName = "App Rotator",
    [string]$PythonCommand = "python.exe"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$installRoot = Join-Path $env:LOCALAPPDATA "Programs\AppRotator"
$venvRoot = Join-Path $installRoot "venv"
$python = Join-Path $venvRoot "Scripts\python.exe"
$pythonw = Join-Path $venvRoot "Scripts\pythonw.exe"
$rotator = Join-Path $venvRoot "Scripts\app-rotator.exe"
$sourceIcon = Join-Path $repoRoot "src\app_rotator\assets\app-rotator-icon.ico"
$installedIcon = Join-Path $installRoot "app-rotator.ico"

if (-not $env:LOCALAPPDATA) {
    throw "LOCALAPPDATA is not available for this user."
}
if (-not (Test-Path -LiteralPath $sourceIcon -PathType Leaf)) {
    throw "Packaged icon is missing: $sourceIcon"
}

New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $basePython = Get-Command $PythonCommand -CommandType Application -ErrorAction Stop |
        Where-Object { $_.Source -notlike "*\Microsoft\WindowsApps\*" } |
        Select-Object -First 1
    if (-not $basePython) {
        throw "No non-Store Python runtime was found. Pass -PythonCommand with a native python.exe path."
    }
    & $basePython.Source -m venv $venvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the per-user App Rotator environment."
    }
}

$venvConfig = Get-Content -LiteralPath (Join-Path $venvRoot "pyvenv.cfg") -Raw
if ($venvConfig -like "*\Microsoft\WindowsApps\*") {
    throw "The existing App Rotator environment uses Store Python and virtualizes LOCALAPPDATA. Remove it and rerun with -PythonCommand pointing to a native Python runtime."
}

& $python -m pip install --disable-pip-version-check $repoRoot
if ($LASTEXITCODE -ne 0) {
    throw "App Rotator installation failed."
}
Copy-Item -LiteralPath $sourceIcon -Destination $installedIcon -Force

$configPath = Join-Path $env:LOCALAPPDATA "AppRotator\config.json"
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    & $rotator config-init
    if ($LASTEXITCODE -ne 0) {
        throw "Safe initial configuration could not be created."
    }
}

$desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
if (-not $desktop) {
    throw "Windows did not return a Desktop special folder for this user."
}
$shortcutPath = Join-Path $desktop "$ShortcutName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = '-m app_rotator tray'
$shortcut.WorkingDirectory = $installRoot
$shortcut.IconLocation = "$installedIcon,0"
$shortcut.Description = "Start App Rotator in the notification area"
$shortcut.Save()

Write-Output $shortcutPath
