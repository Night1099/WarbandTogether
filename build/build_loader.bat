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

echo Compiling coop_loader...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" src\loader\coop_loader.c
if errorlevel 1 goto :error

echo Linking winmm.dll (forwarded exports via .def)...
link.exe /nologo /DLL /OUT:bin\winmm.dll /IMPLIB:bin\winmm_proxy.lib /DEF:src\loader\winmm_proxy.def coop_loader.obj kernel32.lib user32.lib winmm.lib
if errorlevel 1 goto :error

echo === Build successful: winmm.dll ===
del coop_loader.obj 2>nul
call "%~dp0deploy.bat"
exit /b 0
:error
echo === BUILD FAILED ===
del coop_loader.obj 2>nul
exit /b 1
