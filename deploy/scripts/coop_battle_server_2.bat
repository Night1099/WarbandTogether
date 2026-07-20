@echo off
set COOP_BATTLE_SLOT=2
echo Starting Coop Battle Server slot 2 (WSE2) on port 7245...
mb_warband_wse2_dedicated.exe -r Configs\BattleServer_2.txt -m NativeCoop
pause
