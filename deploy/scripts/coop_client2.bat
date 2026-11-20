@echo off
rem Launches a second game client with its own config profile, for testing
rem two players on one machine. The profile dir is created on first run.
rem Development only: WSE2 refuses a second instance unless the client exe
rem carries the mutex patch (docs/wse2-binary-patches.md), so it is not packaged.
set "P2DIR=%USERPROFILE%\Documents\Mount&Blade Warband WSE2 P2"
if not exist "%P2DIR%" mkdir "%P2DIR%"
echo Launching Player 2 (separate profile)...
mb_warband_wse2.exe --config-path "%P2DIR%\rgl_config_p2.ini" --module NativeCoop
