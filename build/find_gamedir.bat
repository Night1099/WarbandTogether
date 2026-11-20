@echo off
rem Sets GAMEDIR to the Warband install directory if not already set.
rem Detection order: Steam registry, every Steam library, common drive roots.
rem Intentionally no setlocal -- GAMEDIR is exported to the caller.
if defined GAMEDIR exit /b 0

set "STEAMROOT="
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v SteamPath 2^>nul ^| findstr /i "SteamPath"') do set "STEAMROOT=%%B"
if defined STEAMROOT set "STEAMROOT=%STEAMROOT:/=\%"
if defined STEAMROOT if exist "%STEAMROOT%\steamapps\common\MountBlade Warband\mb_warband.exe" set "GAMEDIR=%STEAMROOT%\steamapps\common\MountBlade Warband"
if defined GAMEDIR exit /b 0

del "%TEMP%\coop_steam_libs.txt" 2>nul
if defined STEAMROOT if exist "%STEAMROOT%\steamapps\libraryfolders.vdf" powershell -NoProfile -Command "Select-String '\"path\"\s+\"(.+?)\"' -Path '%STEAMROOT%\steamapps\libraryfolders.vdf' | ForEach-Object { $_.Matches[0].Groups[1].Value -replace '\\\\','\' }" > "%TEMP%\coop_steam_libs.txt" 2>nul
if exist "%TEMP%\coop_steam_libs.txt" for /f "usebackq delims=" %%P in ("%TEMP%\coop_steam_libs.txt") do if not defined GAMEDIR if exist "%%P\steamapps\common\MountBlade Warband\mb_warband.exe" set "GAMEDIR=%%P\steamapps\common\MountBlade Warband"
del "%TEMP%\coop_steam_libs.txt" 2>nul
if defined GAMEDIR exit /b 0

for %%D in (C D E F G H J K L M) do for %%R in ("%%D:\SteamLibrary" "%%D:\Program Files (x86)\Steam" "%%D:\Steam") do if not defined GAMEDIR if exist "%%~R\steamapps\common\MountBlade Warband\mb_warband.exe" set "GAMEDIR=%%~R\steamapps\common\MountBlade Warband"
exit /b 0
