@echo off
rem Sets GAMEDIR to the Warband install directory if not already set.
rem Detection order: Steam registry, every Steam library, common drive roots.
rem Intentionally no setlocal -- GAMEDIR is exported to the caller.
if defined GAMEDIR goto :eof

set "STEAMROOT="
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v SteamPath 2^>nul ^| findstr /i "SteamPath"') do set "STEAMROOT=%%B"
if defined STEAMROOT set "STEAMROOT=%STEAMROOT:/=\%"
call :try_steam_root "%STEAMROOT%"
if defined GAMEDIR goto :eof
if not defined STEAMROOT goto :scan_drives
if not exist "%STEAMROOT%\steamapps\libraryfolders.vdf" goto :scan_drives
powershell -NoProfile -Command "Select-String '\"path\"\s+\"(.+?)\"' -Path '%STEAMROOT%\steamapps\libraryfolders.vdf' | ForEach-Object { $_.Matches[0].Groups[1].Value -replace '\\\\','\' }" > "%TEMP%\coop_steam_libs.txt" 2>nul
for /f "usebackq delims=" %%P in ("%TEMP%\coop_steam_libs.txt") do call :try_steam_root "%%P"
del "%TEMP%\coop_steam_libs.txt" 2>nul
if defined GAMEDIR goto :eof
:scan_drives
for %%D in (C D E F G H J K L M) do (
    call :try_steam_root "%%D:\SteamLibrary"
    call :try_steam_root "%%D:\Program Files (x86)\Steam"
    call :try_steam_root "%%D:\Steam"
)
goto :eof

:try_steam_root
if defined GAMEDIR exit /b 0
if "%~1"=="" exit /b 0
if exist "%~1\steamapps\common\MountBlade Warband\mb_warband.exe" set "GAMEDIR=%~1\steamapps\common\MountBlade Warband"
exit /b 0
