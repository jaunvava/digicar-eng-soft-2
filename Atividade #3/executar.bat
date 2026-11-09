@echo off
REM Compila e executa o Sistema de Pagamentos (Windows)
cd /d "%~dp0"
if exist out rmdir /s /q out
dir /s /b src\*.java > fontes.txt
javac -encoding UTF-8 -d out @fontes.txt
if errorlevel 1 (
    del fontes.txt
    echo Falha na compilacao.
    pause
    exit /b 1
)
del fontes.txt
java -cp out pagamentos.app.Main
pause
