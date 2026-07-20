@echo off
setlocal
rem Usage: coop_launch_all.bat [num_battle_servers]
rem Starts the campaign server, N battle-server slots (default 2, max 4),
rem then the client. Battle slot s listens on port 7241+2*s.
set SLOTS=%1
if "%SLOTS%"=="" set SLOTS=2
if %SLOTS% GTR 4 set SLOTS=4
if %SLOTS% LSS 1 set SLOTS=1
set /a LAST=%SLOTS%-1

echo Starting campaign server + %SLOTS% battle server(s)...
start "Coop Campaign Server" "coop_campaign_server.bat"
timeout /t 3 >nul

for /l %%s in (0,1,%LAST%) do (
  start "Coop Battle Server %%s" "coop_battle_server_%%s.bat"
)

timeout /t 2 >nul
start "" "mb_warband_wse2.exe" -m NativeCoop
endlocal
