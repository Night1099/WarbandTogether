@echo off
echo Starting Coop Campaign Server (loopback enabled)...
mb_warband_wse2_dedicated_campaign.exe --config-path server_config.ini -r Configs\CampaignCoop.txt --module NativeCoop
pause
