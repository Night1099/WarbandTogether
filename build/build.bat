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
cl.exe /nologo /O1 /MD /GS- /W3 /c /D "WIN32" /D "NDEBUG" /I "src\shared" src\asi\coop.c src\shared\hook.c src\shared\modglobals.c src\shared\warband_addrs_wse2.c src\asi\steam_flat.c src\asi\steam_tunnel.c src\asi\asi_rglstring.c src\asi\asi_publish.c src\asi\local_result.c src\asi\local_mission.c src\asi\browser_row.c src\asi\autojoin.c src\asi\asi_patch.c src\asi\asi_config.c src\asi\asi_gvars.c
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo Linking warband_coop.asi...
link.exe /nologo /DLL /OUT:bin\warband_coop.asi coop.obj hook.obj modglobals.obj warband_addrs_wse2.obj steam_flat.obj steam_tunnel.obj asi_rglstring.obj asi_publish.obj local_result.obj local_mission.obj browser_row.obj autojoin.obj asi_patch.obj asi_config.obj asi_gvars.obj kernel32.lib user32.lib ws2_32.lib
if errorlevel 1 (del *.obj 2>nul & echo === BUILD FAILED === & exit /b 1)

echo === Build successful: warband_coop.asi ===
del *.obj 2>nul
call "%~dp0deploy.bat"
exit /b 0
