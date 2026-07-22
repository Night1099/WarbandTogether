@echo off
REM package_mod.bat -- assemble a shareable coop mod package
REM
REM Collects the module data, DLLs, ASIs, configs, and server scripts from
REM the game directory and this repo, then zips them into
REM   %COOP_PKG_DIR%\warband_coop_<timestamp>.zip   (default: <repo>\dist)
REM
REM Layout of the produced zip mirrors the Warband install root, so the
REM recipient can extract into their MountBlade Warband directory directly.
REM
REM Requires: Windows 10+ (for PowerShell Compress-Archive)

setlocal enabledelayedexpansion

REM ---- Config -----------------------------------------------------------

for %%I in ("%~dp0..") do set "REPO_ROOT=%%~fI"
call "%~dp0find_gamedir.bat"
set "GAME_DIR=%GAMEDIR%"
set "MODULE_NAME=NativeCoop"
if not defined COOP_PKG_DIR set "COOP_PKG_DIR=%REPO_ROOT%\dist"
set "DEST_DIR=%COOP_PKG_DIR%"
if not defined WSE2_ZIP set "WSE2_ZIP=%REPO_ROOT%\third_party\WSE2.zip"

REM ---- Locate tools (use absolute paths; cmd PATH is unreliable) --------

set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
set "TAR_EXE=%SystemRoot%\System32\tar.exe"

if not exist "%PS_EXE%" set "PS_EXE="
if not exist "%TAR_EXE%" (
    echo ERROR: tar.exe not found at %TAR_EXE%
    echo Windows 10 1803 or later is required.
    exit /b 1
)

REM ---- Timestamp --------------------------------------------------------

set "TIMESTAMP="
if defined PS_EXE (
    set "TS_TMP=%TEMP%\warband_ts_%RANDOM%%RANDOM%.txt"
    "%PS_EXE%" -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'" > "!TS_TMP!" 2>nul
    if exist "!TS_TMP!" (
        set /p TIMESTAMP=<"!TS_TMP!"
        del /q "!TS_TMP!"
    )
)
if not defined TIMESTAMP set "TIMESTAMP=%RANDOM%%RANDOM%"

set "ZIP_NAME=warband_coop_%TIMESTAMP%.zip"
set "ZIP_PATH=%DEST_DIR%\%ZIP_NAME%"

REM ---- Staging ----------------------------------------------------------

set "STAGE_DIR=%TEMP%\warband_coop_pkg_%RANDOM%%RANDOM%"
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
mkdir "%STAGE_DIR%" || goto :error_nostaging

echo [package_mod] Staging at: %STAGE_DIR%
echo [package_mod] Destination: %ZIP_PATH%

REM ---- Pre-flight -------------------------------------------------------

if not exist "%REPO_ROOT%" (
    echo MISSING REPO: %REPO_ROOT%
    goto :error
)
if not defined GAME_DIR (
    echo MISSING GAME DIR -- set GAMEDIR to your MountBlade Warband directory
    goto :error
)
if not exist "%GAME_DIR%" (
    echo MISSING GAME DIR: %GAME_DIR%
    goto :error
)
if not exist "%GAME_DIR%\Modules\%MODULE_NAME%" (
    echo MISSING MODULE: %GAME_DIR%\Modules\%MODULE_NAME%
    goto :error
)

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%" 2>nul
if not exist "%DEST_DIR%" (
    echo CANNOT CREATE DEST: %DEST_DIR%
    goto :error
)

REM ---- WSE2 distribution (extracted first; patched files overwrite) -----
REM Ship the COMPLETE upstream WSE2 rev-1145 zip verbatim so no engine
REM resource is ever missing (CommonRes brf, languages, msvcr120, ...).
REM Everything staged after this overwrites the stock copies -- in
REM particular the coop-patched exes and our server_config.ini.

if not exist "%WSE2_ZIP%" (
    echo MISSING: %WSE2_ZIP%
    echo Place the pinned WSE2 rev-1145 release zip there ^(or set WSE2_ZIP^).
    goto :error
)
echo [package_mod] Extracting WSE2 distribution: %WSE2_ZIP%
"%TAR_EXE%" -x -f "%WSE2_ZIP%" -C "%STAGE_DIR%" || goto :error

REM ---- DLLs and ASIs ----------------------------------------------------
REM Prefer freshly built files from the repo root, fall back to game dir.

echo [package_mod] Copying DLLs and ASIs...

call :copy_pref bin\CoopWSEPlugin.dll || goto :error
call :copy_pref bin\winmm.dll          || goto :error
call :copy_pref bin\warband_coop.asi   || goto :error
call :copy_pref winmm_sys.dll      || goto :error
call :copy_pref dinput8.dll        || goto :error
call :copy_pref coop_loader.dll    || goto :error
call :copy_pref char_screen_hooks.asi || goto :error

REM ---- WSE2 engine (pinned rev 1145 + on-disk coop patches) -------------
REM The client must run a byte-identical engine: warband_coop.asi hooks
REM hardcoded addresses and the exe carries file patches (ASLR off, .text
REM writable, opcode-3415 fix, dual-port LAN scan). Ship the host's exact
REM binaries instead of relying on the recipient's own WSE2 install.

echo [package_mod] Copying WSE2 engine files...
for %%F in (mb_warband_wse2.exe mb_warband_wse2_dedicated.exe mb_warband_wse2_dedicated_campaign.exe wse2_launcher.exe fmodex_wse2.dll steam_api_wse2.dll steam_appid.txt lua51.dll postFX_WSE2.fx postFX.fx Fxaa3_11.h Native_WSE2.bat) do (
    if not exist "%GAME_DIR%\%%F" (
        echo MISSING: %GAME_DIR%\%%F
        goto :error
    )
    copy /y "%GAME_DIR%\%%F" "%STAGE_DIR%\%%F" >nul || goto :error
    echo   %%F
)

REM The WSE2 zip ships a stock server_config.ini at the root, which is the
REM path the campaign launch script reads -- overwrite it with ours.
copy /y "%REPO_ROOT%\deploy\configs\server_config.ini" "%STAGE_DIR%\server_config.ini" >nul || goto :error

REM ---- coop.ini ---------------------------------------------------------
REM The package ships the CLIENT ini (Mode=client, HostIP of the campaign
REM server) so a plain extract-over-install works on a player's PC. The
REM host machine keeps its own coop.ini via build\deploy.bat.

echo [package_mod] Copying coop.ini (client mode)...
if not exist "%REPO_ROOT%\deploy\coop_client.ini" (
    echo MISSING: %REPO_ROOT%\deploy\coop_client.ini
    goto :error
)
copy /y "%REPO_ROOT%\deploy\coop_client.ini" "%STAGE_DIR%\coop.ini" >nul || goto :error

REM ---- Configs ----------------------------------------------------------

echo [package_mod] Copying server configs...
mkdir "%STAGE_DIR%\Configs" || goto :error
for %%F in (BattleServer_0.txt BattleServer_1.txt BattleServer_2.txt BattleServer_3.txt CampaignCoop.txt battle_server_config.ini server_config.ini) do (
    if not exist "%REPO_ROOT%\deploy\configs\%%F" (
        echo MISSING: %REPO_ROOT%\deploy\configs\%%F
        goto :error
    )
    copy /y "%REPO_ROOT%\deploy\configs\%%F" "%STAGE_DIR%\Configs\%%F" >nul || goto :error
    echo   Configs\%%F
)

REM ---- Launch scripts ---------------------------------------------------

echo [package_mod] Copying launch scripts...
for %%F in (coop_campaign_server.bat coop_battle_server_0.bat coop_battle_server_1.bat coop_battle_server_2.bat coop_battle_server_3.bat coop_launch_all.bat coop_client2.bat) do (
    if not exist "%REPO_ROOT%\deploy\scripts\%%F" (
        echo MISSING: %REPO_ROOT%\deploy\scripts\%%F
        goto :error
    )
    copy /y "%REPO_ROOT%\deploy\scripts\%%F" "%STAGE_DIR%\%%F" >nul || goto :error
    echo   %%F
)

REM ---- Module data ------------------------------------------------------

echo [package_mod] Copying module data from %GAME_DIR%\Modules\%MODULE_NAME%...
mkdir "%STAGE_DIR%\Modules\%MODULE_NAME%" || goto :error
xcopy /e /i /q /y "%GAME_DIR%\Modules\%MODULE_NAME%" "%STAGE_DIR%\Modules\%MODULE_NAME%" >nul || goto :error

REM ---- README -----------------------------------------------------------

echo [package_mod] Adding README_INSTALL.txt...
copy /y "%REPO_ROOT%\deploy\README_INSTALL.txt" "%STAGE_DIR%\README_INSTALL.txt" >nul || goto :error

REM ---- Zip via PowerShell Compress-Archive (absolute path) --------------

if not defined PS_EXE (
    echo ERROR: PowerShell not found at expected path; cannot create zip.
    echo Expected: %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe
    goto :error
)

echo [package_mod] Zipping with Compress-Archive...
if exist "%ZIP_PATH%" del /q "%ZIP_PATH%"
"%PS_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path (Join-Path '%STAGE_DIR%' '*') -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 (
    echo ZIP FAILED
    goto :error
)
if not exist "%ZIP_PATH%" (
    echo ZIP FAILED: output file was not created
    goto :error
)

REM Verify the zip is non-empty
for %%S in ("%ZIP_PATH%") do set "ZIP_RAW_SIZE=%%~zS"
if "%ZIP_RAW_SIZE%"=="0" (
    echo ZIP FAILED: output file is empty
    goto :error
)

REM ---- Cleanup ----------------------------------------------------------

rmdir /s /q "%STAGE_DIR%"

REM ---- Report -----------------------------------------------------------

for %%S in ("%ZIP_PATH%") do set "ZIP_SIZE=%%~zS"
set /a ZIP_SIZE_MB=%ZIP_SIZE% / 1024 / 1024
echo.
echo [package_mod] Done.
echo [package_mod] Package: %ZIP_PATH%
echo [package_mod] Size:    %ZIP_SIZE_MB% MB (%ZIP_SIZE% bytes)

endlocal
exit /b 0

REM ---- Subroutines ------------------------------------------------------

:copy_pref
REM %1 = path relative to REPO_ROOT (may include a subdirectory, e.g. bin\x.dll);
REM the package always stages/looks up just the filename, so the game-dir
REM fallback and staged copy use the basename regardless of the repo subdir.
set "DEST_NAME=%~nx1"
if exist "%REPO_ROOT%\%~1" (
    copy /y "%REPO_ROOT%\%~1" "%STAGE_DIR%\%DEST_NAME%" >nul
    if errorlevel 1 exit /b 1
    echo   %DEST_NAME% ^(from repo build^)
    exit /b 0
)
if exist "%GAME_DIR%\%DEST_NAME%" (
    copy /y "%GAME_DIR%\%DEST_NAME%" "%STAGE_DIR%\%DEST_NAME%" >nul
    if errorlevel 1 exit /b 1
    echo   %DEST_NAME% ^(from game dir^)
    exit /b 0
)
echo   MISSING: %DEST_NAME%
exit /b 1

REM ---- Error paths ------------------------------------------------------

:error
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
:error_nostaging
echo.
echo [package_mod] FAILED
endlocal
exit /b 1
