@echo off
rem Deploys built artifacts from bin\ to the game directory.
rem Called automatically at the end of each build script; safe to run standalone.
rem A file locked by a running game/server prints a WARN and is skipped --
rem close the game/servers and rerun build\deploy.bat to finish.
cd /d %~dp0\..
if not defined GAMEDIR set "GAMEDIR=F:\SteamLibrary\steamapps\common\MountBlade Warband"
if not exist "%GAMEDIR%\mb_warband.exe" (
    echo WARN: game not found at %GAMEDIR% -- deploy skipped
    exit /b 1
)

set DEPLOY_WARN=0

if exist bin\CoopWSEPlugin.dll (
    copy /Y bin\CoopWSEPlugin.dll "%GAMEDIR%\" >nul && echo Deployed CoopWSEPlugin.dll || call :warn CoopWSEPlugin.dll
)
if exist bin\warband_coop.asi (
    copy /Y bin\warband_coop.asi "%GAMEDIR%\" >nul && echo Deployed warband_coop.asi || call :warn warband_coop.asi
)
if exist bin\winmm.dll (
    copy /Y bin\winmm.dll "%GAMEDIR%\" >nul && echo Deployed winmm.dll || call :warn winmm.dll
)

rem The winmm proxy forwards to the real system winmm saved as winmm_sys.dll.
if exist bin\winmm.dll if not exist "%GAMEDIR%\winmm_sys.dll" (
    copy /Y "%SystemRoot%\SysWOW64\winmm.dll" "%GAMEDIR%\winmm_sys.dll" >nul && echo Created winmm_sys.dll from system copy || call :warn winmm_sys.dll
)

if not exist "%GAMEDIR%\coop.ini" (
    copy /Y deploy\coop.ini "%GAMEDIR%\" >nul && echo Created coop.ini ^(default: host mode^)
)

if exist lua\main.lua (
    if not exist "%GAMEDIR%\Modules\COOP\lua" mkdir "%GAMEDIR%\Modules\COOP\lua"
    copy /Y lua\main.lua "%GAMEDIR%\Modules\COOP\lua\" >nul && echo Deployed lua\main.lua || call :warn main.lua
)

if %DEPLOY_WARN%==0 (
    echo === Deploy complete: %GAMEDIR% ===
) else (
    echo === Deploy finished with %DEPLOY_WARN% warning^(s^) -- close game/servers and rerun build\deploy.bat ===
)

rem Package a shareable client zip from the freshly deployed artifacts.
rem A packaging failure never fails the deploy itself.
call "%~dp0package_mod.bat"
if errorlevel 1 echo WARN: package_mod.bat failed -- deploy itself is complete
exit /b 0

:warn
echo WARN: could not copy %1 ^(file locked by running game/server?^)
set /a DEPLOY_WARN+=1
exit /b 0
