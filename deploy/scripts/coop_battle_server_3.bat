@echo off
set COOP_BATTLE_SLOT=3
echo Starting Coop Battle Server slot 3 (WSE2) on port 7247...
mb_warband_wse2_dedicated.exe -r Configs\BattleServer_3.txt -m NativeCoop
pause
