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
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo Compiling campaign module...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src" /I "src\shared" /I "enet/include" src\coop_campaign.c src\campaign_ipc.c src\battle_end.c src\coop_config.c src\coop_gvars.c src\set_xp.c
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo Compiling shared modules...
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src" /I "src\shared" /I "enet/include" src\shared\battle_net.c src\shared\exe_personality.c src\shared\hook.c src\shared\crash_report.c src\shared\crash_ring.c src\shared\crash_watchdog.c src\shared\crash_classify.c src\shared\module_dir.c src\shared\wsedict.c src\shared\modglobals.c src\shared\warband_addrs_wse2.c src\shared\nettune.c src\shared\xp.c
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo Compiling ENet...
cl.exe /nologo /O1 /MD /GS- /W0 /c /D "WIN32" /D "NDEBUG" /I "enet/include" enet\callbacks.c enet\compress.c enet\host.c enet\list.c enet\packet.c enet\peer.c enet\protocol.c enet\win32.c
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo Linking CoopWSEPlugin.dll...
link.exe /nologo /DLL /MAP:bin\CoopWSEPlugin.map /OUT:bin\CoopWSEPlugin.dll plugin_main.obj coop_campaign.obj campaign_ipc.obj battle_end.obj coop_config.obj coop_gvars.obj set_xp.obj battle_net.obj exe_personality.obj hook.obj crash_report.obj crash_ring.obj crash_watchdog.obj crash_classify.obj module_dir.obj wsedict.obj modglobals.obj warband_addrs_wse2.obj nettune.obj xp.obj callbacks.obj compress.obj host.obj list.obj packet.obj peer.obj protocol.obj win32.obj kernel32.lib user32.lib ws2_32.lib winmm.lib shell32.lib
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo === Build successful: CoopWSEPlugin.dll ===
del *.obj 2>nul
call "%~dp0deploy.bat"
exit /b 0
