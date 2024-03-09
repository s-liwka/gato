@echo off
setlocal

cd "C:\Program Files"
git clone https://github.com/s-liwka/gato.git

cd gato
python -m venv .venv
call .venv\Scripts\activate

pip install -r requirements.txt

deactivate

set SCRIPT="C:\Program Files\gato\scripts\gato-gui.bat"
set SHORTCUT="%USERPROFILE%\Desktop\Gato.lnk"
set WScriptShell=WScript.CreateObject("WScript.Shell")
set Shortcut=WScriptShell.CreateShortcut(SHORTCUT)
Shortcut.TargetPath=SCRIPT
Shortcut.WorkingDirectory="C:\Program Files\gato"
Shortcut.IconLocation="C:\Program Files\gato\resources\gato_pelon.ico"
Shortcut.Save

echo ####################################
echo #      GATO SETUP SUCCESSFUL       #
echo ####################################
pause