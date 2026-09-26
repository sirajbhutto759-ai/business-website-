$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "Siraj UPS & Solar (Standalone App).lnk"
$ExePath = "C:\Users\siraj\Desktop\Siraj UPS Software Portable\SirajUPS_Software.exe"
$WorkingDir = "C:\Users\siraj\Desktop\Siraj UPS Software Portable"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.Description = "Siraj UPS & Solar Standalone Executable"
$Shortcut.Save()

Write-Host "Standalone executable shortcut created successfully!"
