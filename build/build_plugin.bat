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

echo Compiling plugin_main.cpp...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src" /I "src\shared" /I "enet/include" /TP src\plugin_main.cpp
if errorlevel 1 goto :error

echo Compiling campaign module...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src" /I "src\shared" /I "enet/include" src\coop_campaign.c
if errorlevel 1 goto :error

echo Compiling shared modules...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src" /I "src\shared" /I "enet/include" src\shared\battle_net.c src\shared\hook.c src\shared\crash_report.c src\shared\wsedict.c src\shared\modglobals.c src\shared\warband_addrs_wse2.c
if errorlevel 1 goto :error

echo Compiling ENet...
cl.exe /nologo /O1 /MD /GS- /W0 /c /D "WIN32" /D "NDEBUG" /I "enet/include" enet\callbacks.c enet\compress.c enet\host.c enet\list.c enet\packet.c enet\peer.c enet\protocol.c enet\win32.c
if errorlevel 1 goto :error

echo Linking CoopWSEPlugin.dll...
link.exe /nologo /DLL /MAP:bin\CoopWSEPlugin.map /OUT:bin\CoopWSEPlugin.dll plugin_main.obj coop_campaign.obj battle_net.obj hook.obj crash_report.obj wsedict.obj modglobals.obj warband_addrs_wse2.obj callbacks.obj compress.obj host.obj list.obj packet.obj peer.obj protocol.obj win32.obj kernel32.lib user32.lib ws2_32.lib winmm.lib shell32.lib
if errorlevel 1 goto :error

echo === Build successful: CoopWSEPlugin.dll ===
del *.obj 2>nul
call "%~dp0deploy.bat"
exit /b 0
:error
echo === BUILD FAILED ===
del *.obj 2>nul
exit /b 1
