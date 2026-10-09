@echo off
setlocal
rem Usage: coop_launch_all.bat [num_battle_servers]
rem Starts the campaign server, N battle-server slots (default 2, max 4),
rem then the client. Battle slot s listens on port 7241+2*s.
rem
rem The exes are GUI-subsystem and open their own windows, so we launch them
rem DIRECTLY here (like the client) instead of through the per-server .bat
rem wrappers -- wrapping in a .bat leaves an extra blank cmd console idling
rem for the server's lifetime. The standalone coop_*_server_*.bat files stay
rem for launching a single server by hand (they add an echo + pause).
set SLOTS=%1
if "%SLOTS%"=="" set SLOTS=2
if %SLOTS% GTR 4 set SLOTS=4
if %SLOTS% LSS 1 set SLOTS=1
set /a LAST=%SLOTS%-1

rem The campaign server continues the world in slot COOP_SAVE_NO under
rem Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames: slot 0 is
rem sg00.sav; the debug launcher uses slot 1 (sg01.sav). Delete that file
rem to start a new world. A missing file starts a new world.
if "%COOP_SAVE_NO%"=="" set COOP_SAVE_NO=0
echo Starting campaign server + %SLOTS% battle server(s)...
start "Coop Campaign Server" "mb_warband_wse2_dedicated_campaign.exe" --config-path server_config.ini -r Configs\CampaignCoop.txt --module NativeCoop --load-game --save-no %COOP_SAVE_NO%
timeout /t 3 >nul

for /l %%s in (0,1,%LAST%) do (
  rem set-then-start: start snapshots the environment, so COOP_BATTLE_SLOT
  rem is captured per iteration without delayed expansion.
  set COOP_BATTLE_SLOT=%%s
  start "Coop Battle Server %%s" "mb_warband_wse2_dedicated.exe" -r Configs\BattleServer_%%s.txt -m NativeCoop
)

timeout /t 2 >nul
start "" "mb_warband_wse2.exe" -m NativeCoop
endlocal
