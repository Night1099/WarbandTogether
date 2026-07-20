@echo off
cd /d %~dp0
for /f "tokens=*" %%i in ('"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -property installationPath 2^>nul') do set VSDIR=%%i
if not defined VSDIR (
    echo ERROR: Visual Studio not found.
    exit /b 1
)
call "%VSDIR%\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul 2>&1
cd /d %~dp0\..
if not exist bin mkdir bin

echo Compiling warband_coop...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src\shared" src\asi\coop.c src\shared\hook.c src\shared\modglobals.c src\shared\warband_addrs_wse2.c
if errorlevel 1 goto :error

echo Linking warband_coop.asi...
link.exe /nologo /DLL /OUT:bin\warband_coop.asi coop.obj hook.obj modglobals.obj warband_addrs_wse2.obj kernel32.lib user32.lib ws2_32.lib
if errorlevel 1 goto :error

echo === Build successful: warband_coop.asi ===
del *.obj 2>nul
call "%~dp0deploy.bat"
exit /b 0
:error
echo === BUILD FAILED ===
exit /b 1
