@echo off
setlocal

cd "C:\Program Files"
git clone https://github.com/s-liwka/gato.git

python -m venv .venv
call ".venv\Scripts\activate.bat"

pip install -r "C:\Program Files\gato\requirements.txt"

set SCRIPT="C:\Program Files\gato\scripts\gato-gui.bat"
set SHORTCUT="%USERPROFILE%\Desktop\Gato.lnk"
cscript //nologo "C:\Program Files\gato\scripts\create-shortcut.vbs" "%SHORTCUT%" "%SCRIPT%" "C:\Program Files\gato" "C:\Program Files\gato\resources\gato_pelon.ico"

echo ####################################
echo #      GATO SETUP SUCCESSFUL       #
echo ####################################
pause