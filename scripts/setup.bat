@echo off
setlocal

cd "C:\Program Files"
git clone https://github.com/s-liwka/gato.git

python -m venv "C:\Program Files\gato\.venv"
call "C:\Program Files\gato\.venv\Scripts\activate.bat"

pip install -r "C:\Program Files\gato\requirements.txt"

cscript //nologo "C:\Program Files\gato\scripts\create-shortcut.vbs" "%USERPROFILE%\Desktop\Gato.lnk" "C:\Program Files\gato\scripts\gato-gui.bat" "C:\Program Files\gato" "C:\Program Files\gato\resources\gato_pelon.ico"

echo ####################################
echo #      GATO SETUP SUCCESSFUL       #
echo ####################################
pause