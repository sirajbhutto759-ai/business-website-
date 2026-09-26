$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "Siraj UPS and Solar.lnk"
$IconPath = "c:\Users\siraj\Desktop\Siraj UPS\app_icon.ico"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = '"c:\Users\siraj\Desktop\Siraj UPS\launch_silent.vbs"'
$Shortcut.WorkingDirectory = "c:\Users\siraj\Desktop\Siraj UPS"
$Shortcut.IconLocation = "$IconPath, 0"
$Shortcut.Description = "Siraj UPS & Solar Billing and Inventory System"
$Shortcut.Save()

# Force Windows Explorer to refresh desktop icon cache
$code = @"
[DllImport("shell32.dll", CharSet = CharSet.Auto, SetLastError = true)]
public static extern void SHChangeNotify(int wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);
"@
$type = Add-Type -MemberDefinition $code -Name "Win32SHChangeNotify" -Namespace "Win32Functions" -PassThru
$type::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)

Write-Host "Desktop shortcut icon updated successfully at: $ShortcutPath"
