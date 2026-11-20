@echo off
rem Deploys built artifacts from bin\ to the game directory.
rem Called automatically at the end of each build script; safe to run standalone.
rem Set GAMEDIR to override; otherwise the Warband install is auto-detected
rem from the Steam registry, every Steam library, and common drive roots.
rem A file locked by a running game/server prints a WARN and is skipped --
rem close the game/servers and rerun build\deploy.bat to finish.
cd /d %~dp0\..

if not defined GAMEDIR call "%~dp0find_gamedir.bat"
if not defined GAMEDIR (
    echo WARN: no Warband install found -- set GAMEDIR to your MountBlade Warband directory
    exit /b 1
)
if not exist "%GAMEDIR%\mb_warband.exe" (
    echo WARN: game not found at %GAMEDIR% -- deploy skipped
    exit /b 1
)
echo Deploying to: %GAMEDIR%

set DEPLOY_WARN=0

if exist bin\CoopWSEPlugin.dll (
    copy /Y bin\CoopWSEPlugin.dll "%GAMEDIR%\" >nul && echo Deployed CoopWSEPlugin.dll || (echo WARN: could not copy CoopWSEPlugin.dll ^(file locked by running game/server?^) & set /a DEPLOY_WARN+=1)
)
if exist bin\warband_coop.asi (
    copy /Y bin\warband_coop.asi "%GAMEDIR%\" >nul && echo Deployed warband_coop.asi || (echo WARN: could not copy warband_coop.asi ^(file locked by running game/server?^) & set /a DEPLOY_WARN+=1)
)
if exist bin\winmm.dll (
    copy /Y bin\winmm.dll "%GAMEDIR%\" >nul && echo Deployed winmm.dll || (echo WARN: could not copy winmm.dll ^(file locked by running game/server?^) & set /a DEPLOY_WARN+=1)
)

rem The winmm proxy forwards to the real system winmm saved as winmm_sys.dll.
if exist bin\winmm.dll if not exist "%GAMEDIR%\winmm_sys.dll" (
    copy /Y "%SystemRoot%\SysWOW64\winmm.dll" "%GAMEDIR%\winmm_sys.dll" >nul && echo Created winmm_sys.dll from system copy || (echo WARN: could not copy winmm_sys.dll ^(file locked by running game/server?^) & set /a DEPLOY_WARN+=1)
)

if not exist "%GAMEDIR%\coop.ini" (
    copy /Y deploy\coop.ini "%GAMEDIR%\" >nul && echo Created coop.ini
)

if %DEPLOY_WARN%==0 (
    echo === Deploy complete: %GAMEDIR% ===
) else (
    echo === Deploy finished with %DEPLOY_WARN% warning^(s^) -- close game/servers and rerun build\deploy.bat ===
)
exit /b 0
