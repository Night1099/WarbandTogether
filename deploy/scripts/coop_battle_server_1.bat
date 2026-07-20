@echo off
set COOP_BATTLE_SLOT=1
echo Starting Coop Battle Server slot 1 (WSE2) on port 7243...
mb_warband_wse2_dedicated.exe -r Configs\BattleServer_1.txt -m NativeCoop
pause
