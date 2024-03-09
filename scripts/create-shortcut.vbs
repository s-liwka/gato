Set WScriptShell = CreateObject("WScript.Shell")
Set Shortcut = WScriptShell.CreateShortcut(WScript.Arguments(0))
Shortcut.TargetPath = WScript.Arguments(1)
Shortcut.WorkingDirectory = WScript.Arguments(2)
Shortcut.IconLocation = WScript.Arguments(3)
Shortcut.Save