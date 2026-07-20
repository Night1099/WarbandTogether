@echo off
set COOP_BATTLE_SLOT=0
echo Starting Coop Battle Server slot 0 (WSE2) on port 7241...
mb_warband_wse2_dedicated.exe -r Configs\BattleServer_0.txt -m NativeCoop
pause
