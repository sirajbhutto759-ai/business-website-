Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
pythonwExe = strPath & "\venv\Scripts\pythonw.exe"
scriptFile = strPath & "\run_desktop.py"
WshShell.Run """" & pythonwExe & """ """ & scriptFile & """", 0, False
