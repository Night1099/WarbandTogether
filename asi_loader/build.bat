@echo off
for /f "tokens=*" %%i in ('"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -products * -latest -property installationPath 2^>nul') do set VSDIR=%%i
if not defined VSDIR (
    echo ERROR: Visual Studio not found.
    exit /b 1
)
call "%VSDIR%\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul 2>&1
cd /d %~dp0

echo Compiling dinput8 ASI loader...
cl.exe /nologo /O1 /GS- /W3 /Zl /c /D "WIN32" /D "NDEBUG" dinput8_loader.c
if errorlevel 1 goto :error

echo Linking dinput8.dll...
link.exe /nologo /DLL /NODEFAULTLIB /ENTRY:DllMain /DEF:dinput8.def /OUT:dinput8.dll dinput8_loader.obj kernel32.lib user32.lib
if errorlevel 1 goto :error

echo === Build successful: dinput8.dll ===
del *.obj *.lib *.exp 2>nul
exit /b 0
:error
echo === BUILD FAILED ===
exit /b 1
