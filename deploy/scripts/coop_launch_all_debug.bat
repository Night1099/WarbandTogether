@echo off
rem Usage: coop_launch_all_debug.bat [num_battle_servers]
rem Same as coop_launch_all.bat, but the campaign server marks every party
rem map-visible (no fog of war) for debugging. The flag reaches the module
rem through the campaign server's environment: the host plugin reads
rem COOP_DEBUG_REVEAL and writes it into "coop server cfg campaign.wsedict".
set COOP_DEBUG_REVEAL=1
call "%~dp0coop_launch_all.bat" %*
