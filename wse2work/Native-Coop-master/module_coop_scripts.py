# -*- coding: cp1254 -*-
from header_common import *
from header_operations import *
from header_presentations import *
from module_constants import *
from header_parties import *
from header_skills import *
from header_mission_templates import *
from header_items import *
from header_triggers import *
from header_terrain_types import *
from header_music import *
from header_map_icons import *
from ID_animations import *

####################################################################################################################
# scripts is a list of script records.
# Each script record contns the following two fields:
# 1) Script id: The prefix "script_" will be inserted when referencing scripts.
# 2) Operation block: This must be a valid operation block. See header_operations.py for reference.
####################################################################################################################

coop_scripts = [

   ("coop_troop_can_use_item",
   [
    (try_begin), 
      (neg|is_vanilla_warband),
      (store_script_param, ":troop", 1),
      (store_script_param, ":item", 2),
      (store_script_param, ":item_modifier", 3),

      (item_get_difficulty, ":difficulty", ":item"),
      (item_get_type, ":type", ":item"),

      (try_begin),
        (eq, ":difficulty", 0), # don't apply imod modifiers if item has no requirement
      (else_try),
        (eq, ":item_modifier", imod_stubborn),
        (val_add, ":difficulty", 1),
      (else_try),
        (eq, ":item_modifier", imod_timid),
        (val_sub, ":difficulty", 1),
      (else_try),
        (eq, ":item_modifier", imod_heavy),
        (neq, ":type", itp_type_horse),
        (val_add, ":difficulty", 1),	  
      (else_try),
        (eq, ":item_modifier", imod_strong),
        (val_add, ":difficulty", 2),	  
      (else_try),
        (eq, ":item_modifier", imod_masterwork),
        (val_add, ":difficulty", 4),	  
      (try_end),
	  	  
      (try_begin),
        (eq, ":type", itp_type_horse),
        (store_skill_level, ":skill_level_leadership_var_1", skl_riding, ":troop"),
      (else_try),
        (eq, ":type", itp_type_shield),
        (store_skill_level, ":skill_level_leadership_var_1", skl_shield, ":troop"),
      (else_try),
        (eq, ":type", itp_type_bow),
        (store_skill_level, ":skill_level_leadership_var_1", skl_power_draw, ":troop"),
      (else_try),
        (eq, ":type", itp_type_thrown),
        (store_skill_level, ":skill_level_leadership_var_1", skl_power_throw, ":troop"),
      (else_try),
        (store_attribute_level, ":skill_level_leadership_var_1", ":troop", ca_strength),
      (try_end),
      
      (try_begin),
        (lt, ":skill_level_leadership_var_1", ":difficulty"),
        (assign, reg0, 0),
      (else_try),
        (assign, reg0, 1),
      (try_end),

    (try_end),
   ]),


 #
 # script_coop_on_admin_panel_load
  ("coop_on_admin_panel_load",
    [
        # (assign, "$coop_battle_state", coop_battle_state_setup_mp), #debug
        # (assign, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
      (try_begin), 
        (neg|is_vanilla_warband),
        (dict_create, "$coop_dict"),
        (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
        (dict_load_file, "$coop_dict", s41, 2),

        (dict_get_int, "$coop_battle_state", "$coop_dict", "@battle_state"), # 0 = no battle 1 = is setup 2 = is done
        (eq, "$coop_battle_state", coop_battle_state_setup_sp),
        (dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_setup_mp), # disable starting twice
        (assign, "$coop_battle_state", coop_battle_state_setup_mp),
        (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
        (dict_save, "$coop_dict", s41),

#PREPARE TO CREATE PARTIES
        #assigning constants before copy reg to parties
        (assign, "$coop_cur_temp_party_enemy", coop_temp_party_enemy_begin), #store current spawn party
        (assign, "$coop_cur_temp_party_ally", coop_temp_party_ally_begin), #store current spawn party
        (assign, "$coop_main_party_spawn", coop_temp_party_ally_begin), #main party spawn party

        (call_script, "script_coop_copy_file_to_parties_mp"),	#also copies admin settings to variables

#CHANGE ADMIN PANEL

        (dict_get_int, ":garrison_commander_party", "$coop_dict", "@p_castle_lord"),
        (dict_get_int, ":garrison_party", "$coop_dict", "@p_garrison"),
        (dict_get_int, "$coop_castle_banner", "$coop_dict", "@p_garrison_banner"),
        (dict_get_int, "$coop_battle_type", "$coop_dict", "@map_type"),

        (try_begin),
          (eq, "$coop_battle_type", coop_battle_type_field_battle), #field battle
          (assign, ":coop_game_type", multiplayer_game_type_coop_battle),
        (else_try),
          (eq, "$coop_battle_type", coop_battle_type_village_player_attack), #village battle
          (assign, ":coop_game_type", multiplayer_game_type_coop_battle),
          (store_add, "$coop_garrison_commander_party", coop_temp_party_enemy_begin, ":garrison_commander_party"), 
          (store_add, "$coop_garrison_party", coop_temp_party_enemy_begin, ":garrison_party"), #garrison is first enemy party
        (else_try),
          (eq, "$coop_battle_type", coop_battle_type_village_player_defend), #village battle
          (assign, ":coop_game_type", multiplayer_game_type_coop_battle),
          (store_add, "$coop_garrison_commander_party", coop_temp_party_ally_begin, ":garrison_commander_party"), 
          (store_add, "$coop_garrison_party", coop_temp_party_ally_begin, ":garrison_party"), #garrison is first ally party
        (else_try),
          (eq, "$coop_battle_type", coop_battle_type_siege_player_attack),#player attacking siege
          (assign, ":coop_game_type", multiplayer_game_type_coop_siege),
          (assign, "$defender_team", 0),
          (assign, "$attacker_team", 1),
          (store_add, "$coop_garrison_commander_party", coop_temp_party_enemy_begin, ":garrison_commander_party"), 
          (store_add, "$coop_garrison_party", coop_temp_party_enemy_begin, ":garrison_party"), #garrison is first enemy party
        (else_try),
          (eq, "$coop_battle_type", coop_battle_type_siege_player_defend), #player defending siege
          (assign, ":coop_game_type", multiplayer_game_type_coop_siege), 
          (assign, "$attacker_team", 0),
          (assign, "$defender_team", 1),
          (store_add, "$coop_garrison_commander_party", coop_temp_party_ally_begin, ":garrison_commander_party"), 
          (store_add, "$coop_garrison_party", coop_temp_party_ally_begin, ":garrison_party"), #garrison is first ally party
        (else_try),
          (eq, "$coop_battle_type", coop_battle_type_bandit_lair), #bandit lair battle
          (assign, ":coop_game_type", multiplayer_game_type_coop_battle),
          # (mission_tpl_entry_set_override_flags, "mt_coop_battle", 0, af_override_horse), #NEW
        (else_try),
          (assign, ":coop_game_type", multiplayer_game_type_deathmatch), #cant find type
        (try_end),
        (assign, "$g_multiplayer_game_type", ":coop_game_type"),

        (assign, "$g_multiplayer_selected_map", "scn_random_multi_plain_medium"),
        (dict_get_int, "$coop_battle_scene", "$coop_dict", "@map_scn"),
        (dict_get_int, "$coop_castle_scene", "$coop_dict", "@map_castle"),
        (dict_get_int, "$coop_street_scene", "$coop_dict", "@map_street"),
        (dict_get_int, "$coop_map_party", "$coop_dict", "@map_party_id"),
      #set weather
        (dict_get_int, "$coop_time_of_day", "$coop_dict", "@map_time"),
        (dict_get_int, "$coop_cloud", "$coop_dict", "@map_cloud"),
        (dict_get_int, "$coop_haze", "$coop_dict", "@map_haze"),
        (dict_get_int, "$coop_rain", "$coop_dict", "@map_rain"),#0=none 1=rain 2=snow

        (assign, "$g_multiplayer_ready_for_spawning_agent", 0), #dont start battle yet
        (assign, "$coop_round", coop_round_battle),

        (assign, "$coop_team_1_troop_num", "$coop_num_bots_team_1"),
        (assign, "$coop_team_2_troop_num", "$coop_num_bots_team_2"),

        #set team ratios
        (assign, ":num_bots_team_1", "$coop_num_bots_team_1"),
        (assign, ":num_bots_team_2", "$coop_num_bots_team_2"),
        (val_max, ":num_bots_team_1", 1),

        (dict_get_int, ":battle_advantage", "$coop_dict", "@battle_adv"),#clamp(((15.0f + advantage) / 15.0f), 0.2f, 2.5f) * number of allies

        (val_mul, ":battle_advantage", 1000),
        (val_add, ":battle_advantage", 15000),
        (val_div, ":battle_advantage", 15),
        (val_clamp, ":battle_advantage", 200, 2500),
        # (val_clamp, ":battle_advantage", 700, 1500),

        (try_begin),
          (eq, "$coop_battle_type", coop_battle_type_bandit_lair), #ignore advantage for bandit lair battle
          (assign, ":battle_advantage", 200),
        (try_end),
        (val_mul, ":num_bots_team_2", ":battle_advantage"),
        (store_div, "$coop_team_ratio", ":num_bots_team_2", ":num_bots_team_1"), #(ratio / 1000) * team 1 = team 2
        (val_clamp, "$coop_team_ratio", 500, 2000), #clamp to 0.5 ~ 2.0 (this ends up reducing the effect of battle advantage)

        (dict_get_str, s0, "$coop_dict", "@tm1_name"),
        (faction_set_name, "fac_player_supporters_faction", s0),
        (dict_get_int, "$coop_team_1_faction", "$coop_dict", "@tm0_fac"),
        (dict_get_int, "$coop_team_2_faction", "$coop_dict", "@tm1_fac"),

        #battle size limit
        (try_begin),
          (lt, "$coop_battle_size", coop_min_battle_size), #min setting
          (assign, "$coop_battle_size",  coop_def_battle_size), #default battle size
        (try_end),
		
#Numerical settings template step 2 begin
        (try_begin),
          (lt, "$torch_chance_coop", coop_torch_chance_min), #min setting
          (assign, "$torch_chance_coop",  coop_torch_chance_max), #default battle size
        (try_end),
#Numerical settings template step 2 end

#Numerical settings template step 2 begin
        (try_begin),
          (lt, "$tom_sand_storm_chance", coop_sandstorm_chance_min), #min setting
          (assign, "$tom_sand_storm_chance",  coop_sandstorm_chance_max), #default battle size
        (try_end),
#Numerical settings template step 2 end

      (try_for_range, reg1, 0, 9),
        (dict_get_str, s1, "$coop_dict", "@cls{reg1}_name"),
        (class_set_name, reg1, s1),
      (try_end),

        (assign, "$g_multiplayer_respawn_period", 0), 
        (assign, "$g_multiplayer_factions_voteable", 0), #dont allow these
        (assign, "$g_multiplayer_maps_voteable", 0),    #dont allow these
        (assign, "$g_multiplayer_auto_team_balance_limit", 1000), #set for some scripts but dont show in admin panel
        (assign, "$g_multiplayer_num_bots_voteable", -1), 
		#(assign, "$ai_crouch_mode", 0), #Value 0 to 2, 0 = Crouch & Low Walk, 1 = Crouch only, 2 = No crouching & no low walk
		#
		   # (assign, "$setting_use_dmod", 1), #Commented out in V1.001
			#(call_script, "script_init_item_score"), #No Clue what this is either #Commented out in V1.001
			#(item_set_slot, 20, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(item_set_slot, 11, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(item_set_slot, 19, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(set_fixed_point_multiplier, 100), #Not sure what this is for #Commented out in V1.001
		#	#(set_shader_param_float, "@vFresnelMultiplier", 15),
		#	#(faction_set_slot, "fac_player_supporters_faction", slot_faction_state, 2),
			#(assign, "$g_player_luck", 200), #Not sure what this is #Commented out in V1.001
		#	#(troop_set_slot, "trp_player", slot_troop_occupation, 2),
		#	#(store_random_in_range, ":random_in_range_training_ground_bridge_1", "p_training_ground", "p_bridge_1"),
		#	#(party_relocate_near_party, "p_main_party", ":random_in_range_training_ground_bridge_1", 3),
		#	#(str_store_troop_name, 5, "trp_player"),
		#	#(party_set_name, "p_main_party", 5),
		#	#(call_script, "script_update_party_creation_random_limits"),
		#	#Global variables added below
		#	#Begin add AI Crouching
			#(assign, "$key_crouch", key_caps_lock),
			(assign, "$key_crouch", key_z),
            (assign,"$key_crouch_command", key_comma),
            (assign,"$key_stand_command", key_period),
			(assign,"$g_crouch_speed_limiter", 1),
			#END AI Crouching, files affected: Module_Constants, Module_Scripts (Here and below), module_mission_templates, module_animations, and animacoins.brf last mesh, also probably ani_sneak was removed
			#from load_mod_resource, and instead load_resource ani_crouch and ani_low_walk were probably added.
			#Disable/Enable variables below
			# Not needed (assign, "$battle_time", 1), # look for (eq, "$battle_time", 1), # only shows this if the global is 1 in module_game_menus.
			#(assign, "$ai_crouch_mode", 0), #Commented out in V1.001 #Value 0 to 2, 0 = Crouch & Low Walk, 1 = Crouch only, 2 = No crouching & no low walk
			#(assign, "$coop_desertv3", 0), #Example on how to generate terrain must make it (1) when its scene is set below.
			#1 = Enabled, 0 = disabled (at start if mod option exist in module_presentations)
			#(assign, "$g_player_party_icon", -1), #Not sure if needed #Commented out in V1.001
			#(assign, "$crusade_time", 0), #SP Only
			#(assign, "$g_travel_speed", 75),
			#(assign, "$g_last_payday", 0),
			#(assign, "$g_player_crusading", 0),
			#(assign, "$sp_shield_bash_coop", 1),
			#(assign, "$sp_shield_bash_ai_coop", 0),
			#(assign, "$setting_use_spearwall", 1),

			#(assign, "$g_battle_preparation", -1), # Not sure #Commented out in V1.001
			#(assign, "$g_battle_preparation_phase", 0), # Not sure #Commented out in V1.001
			(assign, "$g_rand_rain_limit", 30), #Commented out in V1.001
			#(assign, "$belfry_sound", 0), #Commented out in V1.001
			#(assign, "$g_reinforcement_waves", 2), #Keep it and see how it goes #Commented out in V1.001
			#Numerical Settings Template Extension begin make sure to edit module_constants def value as well, as the other one here.
			#(assign, "$tom_sand_storm_chance", 20), # Default 20, 100 for testing only.
			#(assign, "$torch_chance_coop", 3), #25% Chance = 25
			#Numerical Settings Template Extension end
			#Must add weapon break, sandstorms, scene effects to Multiplayer as well.
		#	(assign, "$g_faction_names", 0), #SP Only
		#	(assign, "$g_unit_names", 0), #SP Only
			(assign, "$tom_use_banners", 1),
			(assign, "$tom_bonus_banners", 1),
			(assign, "$tom_use_battlefields", 1),
			#(assign, "$tom_weapon_break", 1),
			#(assign, "$tom_lance_breaking", 1),
			(assign, "$coop_generate_reduction", 1),
		#	(assign, "$tom_difficulty_wages", 1),
		#	(assign, "$tom_difficulty_fief", 1),
		#	(assign, "$tom_difficulty_enterprise", 1),
		#	(assign, "$feudal_inefficency", 0),
		#	(assign, "$start_player_crusade", 0),
			#(assign, "$crusader_faction", -5), ##Commented out in V1.001
		#	(assign, "$crusade_start", 0),
		#	(assign, "$crusade_target", 0),
		##	(assign, "$crusade_target_faction", 0),
			#(assign, "$crusader_party_id", -1), #Commented out in V1.001
			#(assign, "$crusader_state", -1), #Commented out in V1.001
			#(assign, "$freelancer_state", 0), #Commented out in V1.001
			#(assign, "$men_are_pleased", 0), #Commented out in V1.001
			#(assign, "$tom_use_longships", 1), #Commented out in V1.001
			#(assign, "$use_feudal_lance", 1), #Commented out in V1.001
		#	(assign, "$use_player_auxiliary", 1), #Not needed for MP
		#	(assign, "$retinue_noble_balt", 0),
		#	(assign, "$retinue_noble_west", 0),
		#	(assign, "$retinue_noble_orthodox", 0),
		#	(assign, "$retinue_noble_muslim", 0),
		#	(assign, "$retinue_noble_mongol", 0),
		#	(assign, "$lance_troop_serving", 0),
		#	(assign, "$lance_troop_reserve", 0),
		#	(assign, "$crusader_order_joined", 0),
		#	(assign, "$culture_pool", 0),
		#	(assign, "$culture_pool_initialized", 0),
		
			
			(assign, "$historical_banners", 1),
			(assign, "$randomize_player_shield", 1),
		#	(assign, "$disable_sisterly_advice", 1),
		#	(assign, "$disable_local_histories", 1),
		#	(assign, "$player_crowned", 0),
		#	(assign, "$default_battle_size", 0),
		#	(assign, "$default_orignal_battle_size", 0),
#
#
#
#
#
#
#
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_add_to_servers_list, "$coop_set_add_to_servers_list"),
        # (multiplayer_send_int_to_server, multiplayer_event_admin_set_anti_cheat, "$coop_set_anti_cheat"),
		(multiplayer_send_int_to_server, multiplayer_event_admin_set_max_num_players, "$coop_set_max_num_players"),
        #(multiplayer_send_int_to_server, multiplayer_event_admin_set_max_num_players, "$coop_set_max_num_players"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_melee_friendly_fire, "$coop_set_melee_friendly_fire"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_friendly_fire, "$coop_set_friendly_fire"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_friendly_fire_damage_self_ratio, "$coop_set_friendly_fire_damage_self_ratio"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_friendly_fire_damage_friend_ratio, "$coop_set_friendly_fire_damage_friend_ratio"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_ghost_mode, "$coop_set_ghost_mode"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_control_block_dir, "$coop_set_control_block_dir"),
        (multiplayer_send_int_to_server, multiplayer_event_admin_set_combat_speed, "$coop_set_combat_speed"),
#Extend


#End Extension
        #these are only set in script_coop_copy_reg_to_settings
        # (assign, "$g_multiplayer_kick_voteable", 1),
        # (assign, "$g_multiplayer_ban_voteable", 1),
        # (assign, "$g_multiplayer_valid_vote_ratio", 51), #more than 50 percent
        # (assign, "$g_multiplayer_player_respawn_as_bot", 0),
      (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
      (dict_save, "$coop_dict", s41),
      (dict_free, "$coop_dict"),

	  (display_message, "@Protip: Some of the settings are grabbed from Single Player, and some settings are saved from Co-Op into future Co-Op sessions in your save.", 0x0016fc07),
	  (display_message, "@Make sure the following ports are forwarded so other players can join: 7240-7247 TCP & UDP.", 0x0016fc07),
	  (display_message, "@Only the host needs to use WSE, joining players can join without using WSE!", 0x0016fc07),
        #Edited Message ENVFIX(display_message, "@Admin panel set."),

      (try_end),
     ]),	
  

  # script_coop_copy_settings_to_file
  ("coop_copy_settings_to_file",
   [
#SP: setup battle
#MP: at battle end
    (try_begin), 
      (neg|is_vanilla_warband),
      (try_begin),
        (game_in_multiplayer_mode),#copy setting at end of battle (only ones that use native variables that may be changed in other modes)
        (server_get_add_to_game_servers_list, "$coop_set_add_to_servers_list"),
        # (server_get_anti_cheat, "$coop_set_anti_cheat"),
        (server_get_max_num_players, "$coop_set_max_num_players"),
        (server_get_friendly_fire, "$coop_set_friendly_fire"),
        (server_get_melee_friendly_fire, "$coop_set_melee_friendly_fire"),
        (server_get_friendly_fire_damage_self_ratio, "$coop_set_friendly_fire_damage_self_ratio"),
        (server_get_friendly_fire_damage_friend_ratio, "$coop_set_friendly_fire_damage_friend_ratio"),
        (server_get_ghost_mode, "$coop_set_ghost_mode"),
        (server_get_control_block_dir, "$coop_set_control_block_dir"),
        (server_get_combat_speed, "$coop_set_combat_speed"),
      (try_end),

      (dict_set_int, "$coop_dict", "@srvr_set0", "$coop_set_add_to_servers_list"),
      # (dict_set_int, "$coop_dict", "@srvr_set1", "$coop_set_anti_cheat"),
      (dict_set_int, "$coop_dict", "@srvr_set2", "$coop_set_max_num_players"),
      (dict_set_int, "$coop_dict", "@srvr_set3", "$coop_battle_size"),
      (dict_set_int, "$coop_dict", "@srvr_set4", "$coop_set_melee_friendly_fire"),
      (dict_set_int, "$coop_dict", "@srvr_set5", "$coop_set_friendly_fire"),
      (dict_set_int, "$coop_dict", "@srvr_set6", "$coop_set_friendly_fire_damage_self_ratio"),
      (dict_set_int, "$coop_dict", "@srvr_set7", "$coop_set_friendly_fire_damage_friend_ratio"),
      (dict_set_int, "$coop_dict", "@srvr_set8", "$coop_set_ghost_mode"),
      (dict_set_int, "$coop_dict", "@srvr_set9", "$coop_set_control_block_dir"),
      (dict_set_int, "$coop_dict", "@srvr_set10", "$coop_set_combat_speed"),
      (dict_set_int, "$coop_dict", "@srvr_set11", "$coop_battle_spawn_formation"),
      (dict_set_int, "$coop_dict", "@srvr_set12", "$g_multiplayer_kick_voteable"),
      (dict_set_int, "$coop_dict", "@srvr_set13", "$g_multiplayer_ban_voteable"),
      (dict_set_int, "$coop_dict", "@srvr_set14", "$g_multiplayer_valid_vote_ratio"),
      (dict_set_int, "$coop_dict", "@srvr_set15", "$g_multiplayer_player_respawn_as_bot"),
      (dict_set_int, "$coop_dict", "@srvr_set16", "$coop_skip_menu"),
      (dict_set_int, "$coop_dict", "@srvr_set17", "$coop_disable_inventory"),
      (dict_set_int, "$coop_dict", "@srvr_set18", "$coop_reduce_damage"),
      (dict_set_int, "$coop_dict", "@srvr_set19", "$coop_no_capture_heroes"),


		#Extend to further commands

				(dict_set_int, "$coop_dict", "@srvr_set20", "$sp_shield_bash_coop"),
				#(dict_set_int, "$coop_dict", "@srvr_set21", "$historical_banners"),
				#(dict_set_int, "$coop_dict", "@srvr_set22", "$randomize_player_shield"),
				(dict_set_int, "$coop_dict", "@srvr_set23", "$coop_extended_camera"),
				(dict_set_int, "$coop_dict", "@srvr_set24", "$sp_shield_bash_ai_coop"),
				#####Begin torch data from save game
				(dict_set_int, "$coop_dict", "@srvr_set25", "$torch_chance_coop"),
				#####End torch data from save game
				(dict_set_int, "$coop_dict", "@srvr_set26", "$tom_sand_storm_chance"),
				(dict_set_int, "$coop_dict", "@srvr_set27", "$tom_sand_storm"),
				(dict_set_int, "$coop_dict", "@srvr_set28", "$voice_set"),
				(dict_set_int, "$coop_dict", "@srvr_set29", "$experimental_archers"),
				(dict_set_int, "$coop_dict", "@srvr_set30", "$g_doghotel_enable_brainy_bots"),
				###Dict Get & Dict Set changes the options in SP after using multiplayer results
	#Dosen't seem to be needed!	

		
		###End extension
		#Might need optimization..
		
		
		
		
		
		
    (try_end),
     ]),	


  # script_coop_copy_file_to_settings
  ("coop_copy_file_to_settings",
   [
#MP: before admin panel
#SP: when use results
    (try_begin), 
      (neg|is_vanilla_warband),
      (dict_get_int, "$coop_set_add_to_servers_list", "$coop_dict", "@srvr_set0"),
      # (dict_get_int, "$coop_set_anti_cheat", "$coop_dict", "@srvr_set1"),
      (dict_get_int, "$coop_set_max_num_players", "$coop_dict", "@srvr_set2"),
      (dict_get_int, "$coop_battle_size", "$coop_dict", "@srvr_set3"),
      (dict_get_int, "$coop_set_melee_friendly_fire", "$coop_dict", "@srvr_set4"),
      (dict_get_int, "$coop_set_friendly_fire", "$coop_dict", "@srvr_set5"),
      (dict_get_int, "$coop_set_friendly_fire_damage_self_ratio", "$coop_dict", "@srvr_set6"),
      (dict_get_int, "$coop_set_friendly_fire_damage_friend_ratio", "$coop_dict", "@srvr_set7"),
      (dict_get_int, "$coop_set_ghost_mode", "$coop_dict", "@srvr_set8"),
      (dict_get_int, "$coop_set_control_block_dir", "$coop_dict", "@srvr_set9"),
      (dict_get_int, "$coop_set_combat_speed", "$coop_dict", "@srvr_set10"),
      (dict_get_int, "$coop_battle_spawn_formation", "$coop_dict", "@srvr_set11"),
      (dict_get_int, "$g_multiplayer_kick_voteable", "$coop_dict", "@srvr_set12"),
      (dict_get_int, "$g_multiplayer_ban_voteable", "$coop_dict", "@srvr_set13"),
      (dict_get_int, "$g_multiplayer_valid_vote_ratio", "$coop_dict", "@srvr_set14"),
      (dict_get_int, "$g_multiplayer_player_respawn_as_bot", "$coop_dict", "@srvr_set15"),
      (dict_get_int, "$coop_skip_menu", "$coop_dict", "@srvr_set16"),
      (dict_get_int, "$coop_disable_inventory", "$coop_dict", "@srvr_set17"),
      (dict_get_int, "$coop_reduce_damage", "$coop_dict", "@srvr_set18"),
      (dict_get_int, "$coop_no_capture_heroes", "$coop_dict", "@srvr_set19"),
	        (dict_get_int, "$sp_shield_bash_coop", "$coop_dict", "@srvr_set20"),
					#(dict_get_int, "$historical_banners", "$coop_dict", "@srvr_set21"),
			     # (dict_get_int, "$randomize_player_shield", "$coop_dict", "@srvr_set22"),
				  (dict_get_int, "$coop_extended_camera", "$coop_dict", "@srvr_set23"),
			      (dict_get_int, "$sp_shield_bash_ai_coop", "$coop_dict", "@srvr_set24"),
				  #####Torch use data from save game begin
				  (dict_get_int, "$torch_chance_coop", "$coop_dict", "@srvr_set25"),
				#####Torch use data from save game end
				(dict_get_int, "$tom_sand_storm_chance", "$coop_dict", "@srvr_set26"),
				(dict_get_int, "$tom_sand_storm", "$coop_dict", "@srvr_set27"),
				(dict_get_int, "$voice_set", "$coop_dict", "@srvr_set28"),
				(dict_get_int, "$experimental_archers", "$coop_dict", "@srvr_set29"),
				(dict_get_int, "$g_doghotel_enable_brainy_bots", "$coop_dict", "@srvr_set30"),

###Dict Get & Dict Set changes the options in SP after using multiplayer results
#Might need optimization
    (try_end),

     ]),	



  # script_coop_set_default_admin_settings
  ("coop_set_default_admin_settings",
   [
    #this should be set to run once at game_start
	#Edit game settings here such as default battle_size, default options (Probably set access inventory as disabled by default), and other things, max players 20 > 200.
	#This file is the module_coop_scripts.py file set settings here!
	#Settings changed by Env at 8th April.
	#Todo: Change spawnformations from default to none default (No longer enable in default) after you implement formations to multiplayer
	#skip_menu is pretty good to have it set as default but if you want to set it as off default then so be it.
	#Parameters for searching (Don't mind this): battlesize battle_size size skip menu Skip_Menu battle_size MP Formation, 20 to 200 max players.
     (try_begin),    #set this first as default, then use saved setting
      (assign, "$coop_set_add_to_servers_list", 1),
      # (assign, "$coop_set_anti_cheat", 0),
	  #COOP WSE BEGIN CUSTOM MAX PLAYERS CODE
      (assign, "$coop_set_max_num_players", 200),
	  #COOP WSE END CUSTOM MAX PLAYERS CODE BY ENVIOUS
	  #(assign, "$coop_set_max_num_players", 64),
      (assign, "$coop_battle_size", coop_def_battle_size), 
	  #Numerical Settings Template step 3 begin make sure to edit module_constants def value as well, as the other one here.
	  			(assign, "$torch_chance_coop", 3), #25% Chance = 25
     (assign, "$tom_sand_storm_chance", coop_sandstorm_chance_def), 
	 (assign, "$torch_chance_coop", coop_torch_chance_def), 
	 #Numerical Settings Template step 3 end
	  #COOP WSE CUSTOM CODE, Change settings here!
	 
      (assign, "$coop_set_melee_friendly_fire", 1),
      (assign, "$coop_set_friendly_fire", 1),
      (assign, "$coop_set_friendly_fire_damage_self_ratio", 0),
      (assign, "$coop_set_friendly_fire_damage_friend_ratio", 3),
      (assign, "$coop_set_ghost_mode", 0),
      (assign, "$coop_set_control_block_dir", 1),
      (assign, "$coop_set_combat_speed", 2), #Default = 0 AKA Slowest
      (assign, "$coop_battle_spawn_formation", 0),
      (assign, "$coop_skip_menu", 1),
      (assign, "$coop_disable_inventory", 1),
      (assign, "$coop_reduce_damage", 0),
	  #Terrain generation, setting default value.
		   # (assign, "$setting_use_dmod", 1), #Commented out in V1.001
			#(call_script, "script_init_item_score"), #No Clue what this is either #Commented out in V1.001
			#(item_set_slot, 20, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(item_set_slot, 11, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(item_set_slot, 19, 1506, 1), #Not sure what this is #Commented out in V1.001
			#(set_fixed_point_multiplier, 100), #Not sure what this is for #Commented out in V1.001
			#(set_shader_param_float, "@vFresnelMultiplier", 15),
			#(faction_set_slot, "fac_player_supporters_faction", slot_faction_state, 2),
			#(assign, "$g_player_luck", 200), #Not sure what this is #Commented out in V1.001
			#(troop_set_slot, "trp_player", slot_troop_occupation, 2),
			#(store_random_in_range, ":random_in_range_training_ground_bridge_1", "p_training_ground", "p_bridge_1"),
			#(party_relocate_near_party, "p_main_party", ":random_in_range_training_ground_bridge_1", 3),
			#(str_store_troop_name, 5, "trp_player"),
			#(party_set_name, "p_main_party", 5),
			#(call_script, "script_update_party_creation_random_limits"),
			#Global variables added below
			#Begin add AI Crouching
			#(assign, "$key_crouch", key_caps_lock),
			(assign, "$key_crouch", key_z),
            (assign,"$key_crouch_command", key_comma),
            (assign,"$key_stand_command", key_period),
			(assign,"$g_crouch_speed_limiter", 1),
			#END AI Crouching, files affected: Module_Constants, Module_Scripts (Here and below), module_mission_templates, module_animations, and animacoins.brf last mesh, also probably ani_sneak was removed
			#from load_mod_resource, and instead load_resource ani_crouch and ani_low_walk were probably added.
			#Disable/Enable variables below
			# Not needed (assign, "$battle_time", 1), # look for (eq, "$battle_time", 1), # only shows this if the global is 1 in module_game_menus.
			(assign, "$ai_crouch_mode", 0), #Value 0 to 2, 0 = Crouch & Low Walk, 1 = Crouch only, 2 = No crouching & no low walk
			#(assign, "$coop_desertv3", 0), #Example on how to generate terrain must make it (1) when its scene is set below.
			#1 = Enabled, 0 = disabled (at start if mod option exist in module_presentations)
			#(assign, "$g_player_party_icon", -1), #Not sure if needed #Commented out in V1.001
			#(assign, "$crusade_time", 0), #SP Only
			#(assign, "$g_travel_speed", 75),
			#(assign, "$g_last_payday", 0),
			#(assign, "$g_player_crusading", 0),
			(assign, "$sp_shield_bash_coop", 1),
			(assign, "$sp_shield_bash_ai_coop", 1),
			(assign, "$experimental_archers", 0),
			 (assign, "$g_doghotel_enable_brainy_bots", -1),
			#(assign, "$setting_use_spearwall", 1),

			#(assign, "$g_battle_preparation", -1), # Not sure  #Commented out in V1.001
			#(assign, "$g_battle_preparation_phase", 0), # Not sure #Commented out in V1.001
			(assign, "$g_rand_rain_limit", 30), #Commented out in V1.001
			#(assign, "$belfry_sound", 0),
			#(assign, "$g_reinforcement_waves", 2), #Keep it and see how it goes #Commented out in V1.001
			#Numerical Settings Template Extension
			#(assign, "$tom_sand_storm_chance", 20), # Default 20, 100 for testing only.

			#Numerical Settings Template Extension
			#Must add weapon break, sandstorms, scene effects to Multiplayer as well.
		#	(assign, "$g_faction_names", 0), #SP Only
		#	(assign, "$g_unit_names", 0), #SP Only
			(assign, "$tom_use_banners", 1),
			(assign, "$tom_bonus_banners", 1),
			(assign, "$tom_use_battlefields", 1),
			#(assign, "$tom_weapon_break", 1),
			#(assign, "$tom_lance_breaking", 1),
			(assign, "$coop_generate_reduction", 1),
		#	(assign, "$tom_difficulty_wages", 1),
		#	(assign, "$tom_difficulty_fief", 1),
		#	(assign, "$tom_difficulty_enterprise", 1),
		#	(assign, "$feudal_inefficency", 0),
		#	(assign, "$start_player_crusade", 0),
			#(assign, "$crusader_faction", -5), #Commented out in V1.001
		#	(assign, "$crusade_start", 0),
		#	(assign, "$crusade_target", 0),
		#	(assign, "$crusade_target_faction", 0),
			#(assign, "$crusader_party_id", -1), #Commented out in V1.001
			#(assign, "$crusader_state", -1), #Commented out in V1.001
			#(assign, "$freelancer_state", 0), #Commented out in V1.001
			#(assign, "$men_are_pleased", 0), #Commented out in V1.001
		#	(assign, "$tom_use_longships", 1), #
		#	(assign, "$use_feudal_lance", 1), #Commented out in V1.001
		#	(assign, "$use_player_auxiliary", 1), #Not needed for MP
		#	(assign, "$retinue_noble_balt", 0),
		#	(assign, "$retinue_noble_west", 0),
		#	(assign, "$retinue_noble_orthodox", 0),
		#	(assign, "$retinue_noble_muslim", 0),
		#	(assign, "$retinue_noble_mongol", 0),
		#	(assign, "$lance_troop_serving", 0),
		#	(assign, "$lance_troop_reserve", 0),
		#	(assign, "$crusader_order_joined", 0),
		#	(assign, "$culture_pool", 0),
		#	(assign, "$culture_pool_initialized", 0),
			(assign, "$historical_banners", 1),
			(assign, "$randomize_player_shield", 1),
		#	(assign, "$disable_sisterly_advice", 1),
		#	(assign, "$disable_local_histories", 1),
		#	(assign, "$player_crowned", 0),
		#	(assign, "$default_battle_size", 0),
		#	(assign, "$default_orignal_battle_size", 0),
	    #(assign, "$coop_generate_swamp", 0),
		#(assign, "$coop_extended_camera", 0),
		#(assign, "$coop_generate_desert", 0), # STEP 4
		#(assign, "$coop_generate_desertv2", 0),
		#(assign, "$coop_generate_desertv3", 0),
		#(assign, "$coop_generate_iberian", 0),
		#(assign, "$coop_generate_iberian2", 0),
		#(assign, "$coop_generate_snow", 0),
		#(assign, "$coop_generate_euro_hillside", 0),
		#End terrain generation
      (assign, "$coop_no_capture_heroes", 1),
      (assign, "$g_multiplayer_kick_voteable", 1),
      (assign, "$g_multiplayer_ban_voteable", 0),
      (assign, "$g_multiplayer_valid_vote_ratio", 63),#more than 50 percent
      (assign, "$g_multiplayer_player_respawn_as_bot", 1),
    (try_end),
     ]),	
#COOP WSE CUSTOM CODE, END CHANGE SETTINGS HERE, BY ENVIOUS.


  # script_coop_get_battle_state
  ("coop_get_battle_state",
   [
    (store_script_param, ":option", 1),
    (try_begin),
      (neg|is_vanilla_warband), #Using WSE (neg means player must be using WSE, if the operation is only is_vanilla_warband that means only run tihs operation if the player is in vanilla mode.)
      (dict_create, ":dict"),
      (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
      (dict_load_file, ":dict", s41, 2),
      (try_begin),
        (eq, ":option", 1),
        (dict_get_int, "$coop_battle_state", ":dict", "@battle_state"), # 0 = no battle 1 = is setup 2 = is done
      (else_try),
        (eq, ":option", 2),
        (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
        (dict_delete_file, s41),
      (else_try),
        (eq, ":option", 3),
        (dict_set_int, ":dict", "@battle_state",coop_battle_state_started),
        (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
        (dict_save, ":dict", s41),

      (try_end),
      (dict_free, ":dict"),
    #(else_try),
      #(display_message, "@Error: WSE is not running."),
	  #Uncomment top two lines to re-enable the WSE error message "WSE ERROR: WSE is not running." when not using WSE, this isn't necessary to uncomment but might be a good idea to after we implement Battle_Time to
	  #Game Mod Options.
    (try_end),
     ]),	



  # script_coop_init_mission_variables
  # This is called EVERY ROUND on ti_before_mission_start
  ("coop_init_mission_variables",
   [
    (assign, "$coop_string_received", 0), #init this global before we get names
    (assign, "$coop_class_string_received", 0), #init this global before we get class names

    (get_max_players, ":num_players"),
    (try_for_range, ":all_player_no", 0, ":num_players"),
      (player_is_active, ":all_player_no"),
      (player_set_slot, ":all_player_no", slot_player_coop_selected_troop, 0), #clear these slots every round
    (try_end),
    (try_begin),
      (neg|multiplayer_is_server),
      # (try_for_range, ":slot", 100, 200),
        # (troop_set_slot, "trp_temp_array_a", ":slot", -1),
        # (troop_set_slot, "trp_temp_array_b", ":slot", -1),
      # (try_end),

        (party_clear, coop_temp_party_enemy_heroes),
        (party_clear, coop_temp_party_ally_heroes),

      (try_for_range, ":slot", 0, 250),
        (troop_set_slot, "trp_temp_troop", ":slot", -1),
      (try_end),
    (try_end),

     ]),	


	#script_coop_get_scene_name
  # INPUT: arg1 = option_index, arg2 = option_value
  ("coop_get_scene_name",
    [
     (store_script_param, ":scene_no", 1),

      (str_store_string, s0, "@Unknown"),
      (try_begin),
        (gt, "$coop_map_party", 0), #if we know the party use it first
        (str_store_party_name, s0,  "$coop_map_party"),
      (else_try),
        (assign, ":scene_party", 0),
        (try_begin),
          (assign, ":end", castles_end),
          (try_for_range, ":castle_no", castles_begin, ":end"),
            (store_sub, ":offset", ":castle_no", castles_begin),
            (val_mul, ":offset", 3),
            (store_add, ":exterior_scene_no", "scn_castle_1_exterior", ":offset"),
            (store_add, ":interior_scene_no", "scn_castle_1_interior", ":offset"),
            (this_or_next|eq, ":scene_no", ":exterior_scene_no"),
            (eq, ":scene_no", ":interior_scene_no"),
            (assign, ":scene_party", ":castle_no"),
            (assign, ":end", 0),
          (try_end),

          (gt, ":end", 0),
          (assign, ":end", towns_end),
          (try_for_range, ":town_no", towns_begin, ":end"),
            (store_sub, ":offset", ":town_no", towns_begin),
            #EnvFix Remove if constant issue (store_add, ":town_center", "scn_town_1_center", ":offset"),
			(store_add, ":town_center", "scn_town_arab_center", ":offset"),
            #Envfix Remove if constant issue (store_add, ":town_castle", "scn_town_1_castle", ":offset"),
			(store_add, ":town_castle", "scn_town_arab_castle", ":offset"),
            #ENvfix Remove if constant issue (store_add, ":town_walls", "scn_town_1_walls", ":offset"),
			(store_add, ":town_walls", "scn_town_arab_walls", ":offset"),
            #Envfix remove if constant issue (store_add, ":town_arena", "scn_town_1_arena", ":offset"),
			(store_add, ":town_arena", "scn_town_arab_arena", ":offset"),

            (this_or_next|eq, ":scene_no", ":town_arena"),
            (this_or_next|eq, ":scene_no", ":town_walls"),
            (this_or_next|eq, ":scene_no", ":town_castle"),
            (eq, ":scene_no", ":town_center"),
            (assign, ":scene_party", ":town_no"),
            (assign, ":end", 0),
          (try_end),
            
          (gt, ":end", 0),
          (assign, ":end", villages_end),
          (try_for_range, ":party_2", villages_begin, ":end"),
            (store_sub, ":offset", ":party_2", villages_begin),
            #ENVFIX (store_add, ":village_scene_no", "scn_village_1", ":offset"),
			(store_add, ":village_scene_no", "trp_village_1_elder", ":offset"),
            (eq, ":village_scene_no", ":scene_no"),
            (assign, ":scene_party", ":party_2"),
            (assign, ":end", 0),
          (try_end),
        (try_end),

        (try_begin),
          (eq, ":end", 0), #if center was found
          (str_store_party_name, s0,  ":scene_party"),
        (else_try),
          (try_begin),
            (eq, ":scene_no", "scn_lair_steppe_bandits"),
            (str_store_string, s0, "@Steppe Bandit Lair"),
          (else_try),
            (eq, ":scene_no", "scn_lair_taiga_bandits"),
            (str_store_string, s0, "@Tundra Bandit Lair"),
          (else_try),
            (eq, ":scene_no", "scn_lair_desert_bandits"),
            (str_store_string, s0, "@Desert Bandit Lair"),
          (else_try),
            (eq, ":scene_no", "scn_lair_forest_bandits"),
            (str_store_string, s0, "@Forest Bandit Camp"),
          (else_try),
            (eq, ":scene_no", "scn_lair_mountain_bandits"),
            (str_store_string, s0, "@Mountain Bandit Hideout"),
          (else_try),
            (eq, ":scene_no", "scn_lair_sea_raiders"),
            (str_store_string, s0, "@Sea Raider Landing"),
          (try_end),
        (try_end),

      (try_end),  

   ]),	


######## 
 #set_trigger_result tells game to add one to option_index and call script again
	#script_coop_server_send_data_before_join
  # INPUT: arg1 = option_index
  ("coop_server_send_data_before_join",
    [
     (store_script_param, ":option_index", 1),
    
     (try_begin),
       (eq, ":option_index", 0),
       (assign, reg0, "$coop_team_1_faction"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 1),
       (assign, reg0, "$coop_team_2_faction"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 2),
       (assign, reg0, "$coop_team_1_troop_num"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 3),
       (assign, reg0, "$coop_team_2_troop_num"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 4),
       (server_get_friendly_fire, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 5),
       (server_get_melee_friendly_fire, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 6),
       (server_get_friendly_fire_damage_self_ratio, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 7),
       (server_get_friendly_fire_damage_friend_ratio, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 8),
       (server_get_ghost_mode, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 9),
       (server_get_control_block_dir, reg0),       
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 10),
       (server_get_combat_speed, reg0),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 11),
       (assign, reg0, "$g_multiplayer_player_respawn_as_bot"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 12),
       (assign, reg0, "$coop_time_of_day"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 13),
       (assign, reg0, "$coop_rain"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 14),
       (assign, reg0, "$coop_cloud"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 15),
       (assign, reg0, "$coop_haze"),
       (set_trigger_result, 1),
     (else_try),
       (eq, ":option_index", 16),
       (assign, reg0, "$coop_castle_banner"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 17),
       (assign, reg0, "$key_crouch"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 18),
       (assign, reg0, "$key_crouch_command"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 19),
       (assign, reg0, "$key_stand_command"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 20),
       (assign, reg0, "$g_crouch_speed_limiter"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 21),
       (assign, reg0, "$ai_crouch_mode"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 22),
       (assign, reg0, "$sp_shield_bash_coop"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 23),
       (assign, reg0, "$sp_shield_bash_ai_coop"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 24),
       (assign, reg0, "$tom_use_banners"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 25),
       (assign, reg0, "$tom_bonus_banners"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 26),
       (assign, reg0, "$tom_use_battlefields"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 27),
       (assign, reg0, "$historical_banners"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 28),
       (assign, reg0, "$randomize_player_shield"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 29),
       (assign, reg0, "$tom_sand_storm_chance"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 30),
       (assign, reg0, "$tom_sand_storm"),
       (set_trigger_result, 1),
	        (else_try),
       (eq, ":option_index", 31),
       (assign, reg0, "$coop_extended_camera"),
       (set_trigger_result, 1),
	   	        (else_try),
       (eq, ":option_index", 32),
       (assign, reg0, "$g_rand_rain_limit"),
       (set_trigger_result, 1),
	   	   	        (else_try),
       (eq, ":option_index", 33),
       (assign, reg0, "$voice_set"),
       (set_trigger_result, 1),
	   #	   	   	        (else_try),
       #(eq, ":option_index", 33),
       #(assign, reg0, "$belfry_positioned"),
       #(set_trigger_result, 1),
	   #	   	        (else_try),
       #(eq, ":option_index", 34),
       #(assign, reg0, "$belfry_sound"),
       #(set_trigger_result, 1),
	   #	   	   	        (else_try),
       #(eq, ":option_index", 35),
       #(assign, reg0, "$coop_use_belfry"),
       #(set_trigger_result, 1),
	  # 	   	   	        (else_try),
      # (eq, ":option_index", 34),
      # (assign, reg0, "$tom_lance_breaking"),
      # (set_trigger_result, 1),
     (try_end),     
       # (assign, reg1, ":option_index"),
       # (display_message, "@server send {reg1} {reg0}"),

   ]),	

	#script_coop_client_receive_data_before_join
  # INPUT: arg1 = option_index, arg2 = option_value
  ("coop_client_receive_data_before_join",
    [
     (store_script_param, ":option_index", 1),
     (store_script_param, ":option_value", 2),

       # (assign, reg1, ":option_index"),
       # (assign, reg2, ":option_value"),
       # (display_message, "@client get {reg1} {reg2}"),
     (try_begin),
       (eq, ":option_index", 0),
       (assign, reg1, 1),
       (str_store_string, s0, "str_team_reg1_faction"),
       (str_store_faction_name, s1, ":option_value"),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 1),
       (assign, reg1, 2),
       (str_store_string, s0, "str_team_reg1_faction"),
       (str_store_faction_name, s1, ":option_value"),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 2),
       (assign, reg1, 1),
       (str_store_string, s0, "@Number of troops on team {reg1}:"),
       (assign, reg0, ":option_value"),
       (str_store_string, s0, "str_s0_reg0"),
     (else_try),
       (eq, ":option_index", 3),
       (assign, reg1, 2),
       (str_store_string, s0, "@Number of troops on team {reg1}:"),
       (assign, reg0, ":option_value"),
       (str_store_string, s0, "str_s0_reg0"),
     (else_try),
       (eq, ":option_index", 4),
       (str_store_string, s0, "str_allow_friendly_fire"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_no_wo_dot"),
       (else_try),
         (str_store_string, s1, "str_yes_wo_dot"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 5),
       (str_store_string, s0, "str_allow_melee_friendly_fire"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_no_wo_dot"),
       (else_try),
         (str_store_string, s1, "str_yes_wo_dot"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 6),
       (str_store_string, s0, "str_friendly_fire_damage_self_ratio"),
       (assign, reg0, ":option_value"),
       (str_store_string, s0, "str_s0_reg0"),
     (else_try),
       (eq, ":option_index", 7),
       (str_store_string, s0, "str_friendly_fire_damage_friend_ratio"),
       (assign, reg0, ":option_value"),
       (str_store_string, s0, "str_s0_reg0"),
     (else_try),
       (eq, ":option_index", 8),
       (str_store_string, s0, "str_spectator_camera"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_free"),
       (else_try),
         (eq, ":option_value", 1),
         (str_store_string, s1, "str_stick_to_any_player"),
       (else_try),
         (eq, ":option_value", 2),
         (str_store_string, s1, "str_stick_to_team_members"),
       (else_try),
         (str_store_string, s1, "str_stick_to_team_members_view"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 9),
       (str_store_string, s0, "str_control_block_direction"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_automatic"),
       (else_try),
         (str_store_string, s1, "str_by_mouse_movement"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 10),
       (str_store_string, s0, "str_combat_speed"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_combat_speed_0"),
       (else_try),
         (eq, ":option_value", 1),
         (str_store_string, s1, "str_combat_speed_1"),
       (else_try),
         (eq, ":option_value", 2),
         (str_store_string, s1, "str_combat_speed_2"),
       (else_try),
         (eq, ":option_value", 3),
         (str_store_string, s1, "str_combat_speed_3"),
       (else_try),
         (str_store_string, s1, "str_combat_speed_4"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 11),
       (str_store_string, s0, "str_players_take_control_of_a_bot_after_death"),
       (try_begin),
         (eq, ":option_value", 0),
         (str_store_string, s1, "str_no_wo_dot"),
       (else_try),
         (str_store_string, s1, "str_yes_wo_dot"),
       (try_end),
       (str_store_string, s0, "str_s0_s1"),
     (else_try),
       (eq, ":option_index", 12),
       (assign, "$coop_time_of_day", ":option_value"),
       (str_store_string, s0, "@Time of day:"),
       (assign, reg0, ":option_value"),
       (str_store_string, s0, "str_s0_reg0"),
     (else_try),
       (eq, ":option_index", 13),
       (assign, "$coop_rain", ":option_value"),
     (else_try),
       (eq, ":option_index", 14),
       (assign, "$coop_cloud", ":option_value"),
     (else_try),
       (eq, ":option_index", 15),
       (assign, "$coop_haze", ":option_value"),
     (else_try),
       (eq, ":option_index", 16),
       (assign, "$coop_castle_banner", ":option_value"),
       (display_message, "@Recieved Scene Data."),
	        (else_try),
       (eq, ":option_index", 17),
       (assign, "$key_crouch", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 18),
       (assign, "$key_crouch_command", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 19),
       (assign, "$key_stand_command", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 20),
       (assign, "$g_crouch_speed_limiter", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 21),
       (assign, "$ai_crouch_mode", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 22),
       (assign, "$sp_shield_bash_coop", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 23),
       (assign, "$sp_shield_bash_ai_coop", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 24),
       (assign, "$tom_use_banners", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 25),
       (assign, "$tom_bonus_banners", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 26),
       (assign, "$tom_use_battlefields", ":option_value"),
       (eq, ":option_index", 27),
       (assign, "$historical_banners", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 28),
       (assign, "$randomize_player_shield", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 29),
       (assign, "$tom_sand_storm_chance", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 30),
       (assign, "$tom_sand_storm", ":option_value"),
	   	        (else_try),
       (eq, ":option_index", 31),
       (assign, "$coop_extended_camera", ":option_value"),
	   	   	        (else_try),
       (eq, ":option_index", 32),
       (assign, "$g_rand_rain_limit", ":option_value"),
	   	   	   	        (else_try),
       (eq, ":option_index", 33),
       (assign, "$voice_set", ":option_value"),
	  # 	   	   	   	        (else_try),
      # (eq, ":option_index", 33),
      # (assign, "$belfry_positioned", ":option_value"),
	  #	   	   	        (else_try),
      #(eq, ":option_index", 34),
      #(assign, "$belfry_sound", ":option_value"),
	  #	  	   	   	        (else_try),
      #(eq, ":option_index", 35),
      #(assign, "$coop_use_belfry", ":option_value"),
	   #	   	   	        (else_try),
       #(eq, ":option_index", 33),
       #(assign, "$tom_weapon_break", ":option_value"),
	   #	   	   	        (else_try),
       #(eq, ":option_index", 34),
       #(assign, "$tom_lance_breaking", ":option_value"),
     (try_end),  

   ]),	


######## 
	 # script_coop_server_player_joined_common
  # Input: arg1 
  # Output: none
  ("coop_server_player_joined_common",
   [
    (store_script_param, ":player_no", 1),

    (try_begin),
      (gt, ":player_no", 0), #dont send stats to server
#	  #Works but could be better
#DEBUG FOR Co-Op display messages Begin
#(display_message, "@TESTING Multiplayer int_2 event coop_scripts A1 - only connecting player should see this."),
		#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_dmod, "$setting_use_dmod"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch, "$key_crouch"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch_command, "$key_crouch_command"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_stand_command, "$key_stand_command"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_crouch_speed_limiter, "$g_crouch_speed_limiter"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_ai_crouch_mode, "$ai_crouch_mode"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_player_party_icon, "$g_player_party_icon"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash, "$sp_shield_bash_coop"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash_ai, "$sp_shield_bash_ai_coop"), #Step 4
					#	(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_spearwall, "$setting_use_spearwall"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation, "$g_battle_preparation"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation_phase, "$g_battle_preparation_phase"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_rand_rain_limit, "$g_rand_rain_limit"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_position, "$belfry_positioned"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_sound, "$belfry_sound"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_use_belfry, "$coop_use_belfry"), #Step 4

			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_reinforcement_waves, "$g_reinforcement_waves"),



			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_banners, "$tom_use_banners"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_bonus_banners, "$tom_bonus_banners"), #Step 4
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_battlefields, "$tom_use_battlefields"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_weapon_break, "$tom_weapon_break"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_lance_breaking, "$tom_lance_breaking"),
			###((multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_coop_generate_reduction, "$coop_generate_reduction"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_faction, "$crusader_faction"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_party_id, "$crusader_party_id"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_state, "$crusader_state"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_freelancer_state, "$freelancer_state"), #Step 4
			
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_men_are_pleased, "$men_are_pleased"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_longships, "$tom_use_longships"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_use_feudal_lance, "$use_feudal_lance"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_historical_banners, "$historical_banners"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_randomize_player_shield, "$randomize_player_shield"),
						#Numerical Settings Template Step 5 Begin (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_sand_storm_chance, "$tom_sand_storm_chance"),
						###((multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_torch_chance, "$torch_chance_coop"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_camera_mode, "$coop_extended_camera"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_voiceset, "$voice_set"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_sand_storm, "$tom_sand_storm"),
						#Numerical Settings Template Step 5 End (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
			#End Extension
			#If adding additional features all you need is to add send to player above and event_subtype, as well as make a new constant in module_constants similiar to coop_set_ right here.
			#If you wish to extend to the menu, you'll have to do more, just read module_coop_presentations.
			
			
      (str_store_faction_name, s0, "fac_player_supporters_faction"),
      (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),

      #send names of main party troop classes
      (try_for_range, ":class", 0, 9),
        (str_store_class_name, s0, ":class"), 
        (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
      (try_end),

      (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_castle_party, "$coop_map_party"),
      (get_max_players, ":num_players"),
      (try_for_range, ":all_player_no", 0, ":num_players"),
        (player_is_active, ":all_player_no"),
        (player_get_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
        (gt, ":other_player_selected_troop", 0),
        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_player_set_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
      (try_end),

      #send list of heroes in battle (since client cannot upgrade character, only send fighting skills)
      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_enemy_heroes),
      (try_for_range, ":stack", 0, ":num_heroes"),
        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_enemy_heroes, ":stack"),	
        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_enemy_heroes),
#NEW
        (try_begin),
          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
          (str_store_troop_name, s0, ":hero_troop"),
          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),

          #(troop_get_face_keys, reg1, ":hero_troop"),
          #(str_store_face_keys, s0, reg1),
          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
        (try_end),

        #(try_for_range, ":attribute", ca_strength, ca_intelligence),#0,1 #Def
		(try_for_range, ":attribute", 0, 2),#0,1
          (store_attribute_level,":value",":hero_troop",":attribute"),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
        (try_end),
        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
          (gt,":value",0),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
        (try_end),
        #(try_for_range, ":wprof", wpt_one_handed_weapon, 7),#DEF
		(try_for_range, ":wprof", 0, 7),
          (store_proficiency_level,":value",":hero_troop",":wprof"),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
        (try_end),
      (try_end),

      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_ally_heroes),
      (try_for_range, ":stack", 0, ":num_heroes"),
        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_ally_heroes, ":stack"),	
        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_ally_heroes),
#NEW


        (try_begin),
          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
          (str_store_troop_name, s0, ":hero_troop"),
          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),

          #(troop_get_face_keys, reg1, ":hero_troop"),
          #(str_store_face_keys, s0, reg1),
          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
        (try_end),

        #(try_for_range, ":attribute", ca_strength, ca_intelligence),#0,1 #Def
		(try_for_range, ":attribute", 0, 2),#0,1
          (store_attribute_level,":value",":hero_troop",":attribute"),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
        (try_end),
        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
          (gt,":value",0),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
        (try_end),
        #(try_for_range, ":wprof", wpt_one_handed_weapon, 7), #Def
		(try_for_range, ":wprof", 0, 7),
          (store_proficiency_level,":value",":hero_troop",":wprof"),
          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
        (try_end),
      (try_end),

    (try_end),
    #do send this to server
#Maybe send more data in here when player joins??

    (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_round, "$coop_round", "$coop_battle_started"), #start welcome message after getting team data
#	 #(display_message, "str_revision"),
#	 (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, "str_revision"), #New
#			#Begin terrain generation
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_swamp, "$coop_generate_swamp"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desert, "$coop_generate_desert"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desertv2, "$coop_generate_desertv2"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desertv3, "$coop_generate_desertv3"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_iberian, "$coop_generate_iberian"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_iberian2, "$coop_generate_iberian2"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_snow, "$coop_generate_snow"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_euro_hillside, "$coop_generate_euro_hillside"), #Step 4
#			#End terrain generation
#			
#			#Extend to all Co-Op Cmds for MP
#			
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_dmod, "$setting_use_dmod"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch, "$key_crouch"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch_command, "$key_crouch_command"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_stand_command, "$key_stand_command"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_crouch_speed_limiter, "$g_crouch_speed_limiter"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_ai_crouch_mode, "$ai_crouch_mode"),
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_player_party_icon, "$g_player_party_icon"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash, "$sp_shield_bash_coop"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash_ai, "$sp_shield_bash_ai_coop"), #Step 4
#					#	(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_spearwall, "$setting_use_spearwall"),
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation, "$g_battle_preparation"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation_phase, "$g_battle_preparation_phase"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_rand_rain_limit, "$g_rand_rain_limit"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_reinforcement_waves, "$g_reinforcement_waves"),
#
#
#
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_banners, "$tom_use_banners"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_bonus_banners, "$tom_bonus_banners"), #Step 4
#						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_battlefields, "$tom_use_battlefields"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_weapon_break, "$tom_weapon_break"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_lance_breaking, "$tom_lance_breaking"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_coop_generate_reduction, "$coop_generate_reduction"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_faction, "$crusader_faction"),
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_party_id, "$crusader_party_id"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_state, "$crusader_state"),
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_freelancer_state, "$freelancer_state"), #Step 4
#			
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_men_are_pleased, "$men_are_pleased"),
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_longships, "$tom_use_longships"), #Step 4
#			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_use_feudal_lance, "$use_feudal_lance"),
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_historical_banners, "$historical_banners"), #Step 4
#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_randomize_player_shield, "$randomize_player_shield"),
#						#Numerical Settings Template Step 5 Begin (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
#						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_sand_storm_chance, "$tom_sand_storm_chance"),
#						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_torch_chance, "$torch_chance_coop"),
#						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_camera_mode, "$coop_extended_camera"),
#						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_sand_storm, "$tom_sand_storm"),
#						#Numerical Settings Template Step 5 End (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
#			#End Extension
#			#If adding additional features all you need is to add send to player above and event_subtype, as well as make a new constant in module_constants similiar to coop_set_ right here.
#			#If you wish to extend to the menu, you'll have to do more, just read module_coop_presentations.
	 
   ]),	


#  # script_coop_server_player_joined_common
#  # Input: arg1 
#  # Output: none
#  ("coop_server_player_joined_common",
#   [
#    (store_script_param, ":player_no", 1),
#
#    (try_begin),
#      (gt, ":player_no", 0), #dont send stats to server
#
#      (str_store_faction_name, s0, "fac_player_supporters_faction"),
#      (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#
#      #send names of main party troop classes
#      (try_for_range, ":class", 0, 9),
#        (str_store_class_name, s0, ":class"), 
#        (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#      (try_end),
#
#      (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_castle_party, "$coop_map_party"),
#      (get_max_players, ":num_players"),
#      (try_for_range, ":all_player_no", 0, ":num_players"),
#        (player_is_active, ":all_player_no"),
#        (player_get_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
#        (gt, ":other_player_selected_troop", 0),
#        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_player_set_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
#      (try_end),
#
#      #send list of heroes in battle (since client cannot upgrade character, only send fighting skills)
#      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_enemy_heroes),
#      (try_for_range, ":stack", 0, ":num_heroes"),
#        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_enemy_heroes, ":stack"),	
#        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_enemy_heroes),
##NEW
#        (try_begin),
#          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
#          (str_store_troop_name, s0, ":hero_troop"),
#          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#
#          #(troop_get_face_keys, reg1, ":hero_troop"),
#          #(str_store_face_keys, s0, reg1),
#          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#        (try_end),
#
#        (try_for_range, ":attribute", ca_strength, ca_intelligence),#0,1
#          (store_attribute_level,":value",":hero_troop",":attribute"),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
#        (try_end),
#        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
#          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
#          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
#          (gt,":value",0),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
#        (try_end),
#        (try_for_range, ":wprof", wpt_one_handed_weapon, 7),
#          (store_proficiency_level,":value",":hero_troop",":wprof"),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
#        (try_end),
#      (try_end),
#
#      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_ally_heroes),
#      (try_for_range, ":stack", 0, ":num_heroes"),
#        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_ally_heroes, ":stack"),	
#        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_ally_heroes),
##NEW
#        (try_begin),
#          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
#          (str_store_troop_name, s0, ":hero_troop"),
#          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#
#          #(troop_get_face_keys, reg1, ":hero_troop"),
#          #(str_store_face_keys, s0, reg1),
#          (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
#        (try_end),
#
#        (try_for_range, ":attribute", ca_strength, ca_intelligence),#0,1
#          (store_attribute_level,":value",":hero_troop",":attribute"),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
#        (try_end),
#        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
#          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
#          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
#          (gt,":value",0),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
#        (try_end),
#        (try_for_range, ":wprof", wpt_one_handed_weapon, 7),
#          (store_proficiency_level,":value",":hero_troop",":wprof"),
#          (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
#        (try_end),
#      (try_end),
#
#    (try_end),
#    #do send this to server
##Maybe send more data in here when player joins??
#    (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_round, "$coop_round", "$coop_battle_started"), #start welcome message after getting team data
#   ]),	
#   
#   
#####BUGGY BEGIN
######## 
#	
#  # script_coop_server_player_joined_common
#  # Input: arg1 
#  # Output: none
#  ("coop_server_player_joined_common",
#   [
#    (store_script_param, ":script_param_1", 1),
#
#    (try_begin),
#      (gt, ":script_param_1", 0), #dont send stats to server
#
#      (str_store_faction_name, s0, "fac_player_supporters_faction"),
#      (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#
#      #send names of main party troop classes
#      (try_for_range, ":class", 0, 9),
#        (str_store_class_name, s0, ":class"), 
#        (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#      (try_end),
#
#      (multiplayer_send_2_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_return_castle_party, "$coop_map_party"),
#      (get_max_players, ":max_players"),
#      (try_for_range, ":all_player_no", 0, ":max_players"),
#        (player_is_active, ":all_player_no"),
#        (player_get_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
#        (gt, ":other_player_selected_troop", 0),
#        (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_player_set_slot, ":other_player_selected_troop", ":all_player_no", slot_player_coop_selected_troop),
#      (try_end),
#
#      #send list of heroes in battle (since client cannot upgrade character, only send fighting skills)
#      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_enemy_heroes),
#      (try_for_range, ":localvariable", 0, ":num_heroes"),
#        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_enemy_heroes, ":localvariable"),	
#        (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_enemy_heroes),
##NEW
#        (try_begin),
#          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
#          (str_store_troop_name, s0, ":hero_troop"),
#          (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#
#          #(troop_get_face_keys, reg1, ":hero_troop"),
#          #(str_store_face_keys, s0, reg1),
#          (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#        (try_end),
#
#        (try_for_range, ":attribute", 0, 2),#0,1
#          (store_attribute_level,":value",":hero_troop",":attribute"),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
#        (try_end),
#        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
#          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
#          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
#          (gt,":value",0),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
#        (try_end),
#        (try_for_range, ":wprof", 0, 7),
#          (store_proficiency_level,":value",":hero_troop",":wprof"),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
#        (try_end),
#      (try_end),
#
#      (party_get_num_companion_stacks, ":num_heroes", coop_temp_party_ally_heroes),
#      (try_for_range, ":localvariable", 0, ":num_heroes"),
#        (party_stack_get_troop_id, ":hero_troop", coop_temp_party_ally_heroes, ":localvariable"),	
#        (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_store_hero_troops, ":hero_troop", coop_temp_party_ally_heroes),
##NEW
#        (try_begin),
#          # (neg|is_between, ":hero_troop", kings_begin, pretenders_end),
#          (str_store_troop_name, s0, ":hero_troop"),
#          (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#
#          #(troop_get_face_keys, reg1, ":hero_troop"),
#          #(str_store_face_keys, s0, reg1),
#          (multiplayer_send_string_to_player, ":script_param_1", multiplayer_event_coop_send_to_player_string, s0),
#        (try_end),
#
#        (try_for_range, ":attribute", 0, 2),#0,1
#          (store_attribute_level,":value",":hero_troop",":attribute"),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_attribute, ":value",":hero_troop",":attribute"),
#        (try_end),
#        (try_for_range, ":skill_level_leadership_var_1", skl_horse_archery, skl_reserved_14),
#          (neg|is_between, ":skill_level_leadership_var_1", "skl_reserved_9", "skl_power_draw"), #skip these skills
#          (store_skill_level,":value",":skill_level_leadership_var_1",":hero_troop"),
#          (gt,":value",0),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_skill, ":value",":hero_troop",":skill_level_leadership_var_1"),
#        (try_end),
#        (try_for_range, ":wprof", 0, 7),
#          (store_proficiency_level,":value",":hero_troop",":wprof"),
#          (multiplayer_send_4_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_troop_raise_proficiency_linear, ":value",":hero_troop",":wprof"),
#        (try_end),
#      (try_end),
#
#    (try_end),
#    #do send this to server
#	#Maybe send more data in here when player joins??
#    (multiplayer_send_3_int_to_player, ":script_param_1", multiplayer_event_coop_send_to_player, coop_event_round, "$coop_round", "$coop_battle_started"), #start welcome message after getting team data
#   ]),	

#####BUGGY END

######## 
	#script_coop_receive_network_message
  # This script is called from the game engine when a new network message is received.
  # INPUT: arg1 = player_no, arg2 = event_type, arg3 = value, arg4 = value_2, arg5 = value_3, arg6 = value_4
  ("coop_receive_network_message",
    [
      (store_script_param, ":player_no", 1),
      (store_script_param, ":event_type", 2),
    #ENVFIX (store_script_param, ":player_no", 1),
	#ENVFIX (store_script_param, ":event_type", 2),
      (store_script_param, ":coop_v3", 3),
      (store_script_param, ":coop_v4", 4),
      (store_script_param, ":coop_v5", 5),
      (store_script_param, ":coop_v6", 6),
      # Thin router: forward by direction. Server-received events (client->
      # server) always ran -- the original (multiplayer_is_server) gate was
      # commented out. Client-received events (server->client) stay gated
      # off dedicated servers.
      (call_script, "script_coop_recv_battle_server_events", ":player_no", ":event_type", ":coop_v3", ":coop_v4", ":coop_v5", ":coop_v6"),
      (try_begin),
        (neg|multiplayer_is_dedicated_server),
        (call_script, "script_coop_recv_battle_client_events", ":player_no", ":event_type", ":coop_v3", ":coop_v4", ":coop_v5", ":coop_v6"),
      (try_end),
      ]),

  ("coop_recv_battle_server_events",
    [
      (store_script_param, ":player_no", 1),
      (store_script_param, ":event_type", 2),
      (try_begin),
        #SERVER EVENTS#
        (eq, ":event_type", multiplayer_event_change_troop_id), #receive player chosen troop
        (this_or_next|eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
        (eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
        (store_script_param, ":troop", 3),
        (try_begin),
          (gt, ":troop", 0),
          (player_get_agent_id, ":player_agent", ":player_no"),
          (this_or_next|eq, ":player_agent", -1),#if spectator
          (neg|agent_is_alive, ":player_agent"), #if dead

          #only continue if hero is not dead yet
          (player_get_team_no, ":player_team", ":player_no"),
          (assign, ":num", 0),
          (try_begin),
            (eq, ":player_team", 0),
            (party_count_members_of_type, ":num", coop_temp_party_enemy_heroes, ":troop"),
          (else_try),
            (eq, ":player_team", 1),
            (party_count_members_of_type, ":num", coop_temp_party_ally_heroes, ":troop"),
          (try_end),
          (eq, ":num", 1),

          (try_begin),
            (eq, "$coop_battle_started", 1),
            (assign, ":end_cond", 0),
            (try_for_agents, ":cur_agent"),
              (eq, ":end_cond", 0),
              (agent_is_alive, ":cur_agent"),
              (agent_is_human, ":cur_agent"),
              (agent_is_non_player, ":cur_agent"),
              (agent_get_troop_id,":script_param_1", ":cur_agent"),
              (eq, ":troop", ":script_param_1"),
              #(troop_is_hero, ":script_param_1"),
              (player_set_troop_id, ":player_no", ":script_param_1"),#NEW
              (player_control_agent, ":player_no", ":cur_agent"),

              (assign, ":end_cond", 1), #break
            (try_end),
          (else_try),
            #only tell other players before spawn, after spawn other players check agents if troop is in use
            (get_max_players, ":num_players"),
            (try_for_range, ":all_player_no", 0, ":num_players"), 
              (player_is_active, ":all_player_no"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_player_set_slot, ":troop", ":player_no", slot_player_coop_selected_troop),
            (try_end),
          (try_end),
          (player_set_slot, ":player_no", slot_player_coop_selected_troop, ":troop"), #server always save to player slot

        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_change_team_no),
        (this_or_next|eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
        (eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
        (store_script_param, ":team", 3),
        (try_begin),
          (eq, ":team", multi_team_spectator),
          (try_begin),
            (eq, "$coop_battle_started", 0), #only send to players before spawn if already picked
            (player_get_slot,  ":player_troop", ":player_no", slot_player_coop_selected_troop),
            (gt, ":player_troop", 0),
            (get_max_players, ":num_players"),
            (try_for_range, ":all_player_no", 0, ":num_players"), 
              (player_is_active, ":all_player_no"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_player_set_slot, 0, ":player_no", slot_player_coop_selected_troop),
            (try_end),
          (try_end),
          (player_set_slot, ":player_no", slot_player_coop_selected_troop, 0),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_set_bot_selection), #also called from native script for slot_player_bot_type_1_wanted, slot_player_bot_type_4_wanted
        (this_or_next|eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
        (eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
        (store_script_param, ":slot_no", 3),
        (store_script_param, ":value", 4),
        (try_begin),
          (is_between, ":slot_no", slot_player_coop_class_0_wanted, slot_player_coop_class_8_wanted + 1), # coop only slots
          (is_between, ":value", 0, 2),
          (player_set_slot, ":player_no", ":slot_no", ":value"),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_open_admin_panel), 
        (try_begin),
          (call_script, "script_coop_get_battle_state", 1), #sets coop_battle_state
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_battle_state, "$coop_battle_state"),
          (this_or_next|eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
          (eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
          (call_script, "script_game_quick_start"), #add this to native event when switching back to native game type
        (try_end),


      # COOP EVENTS#
      (else_try),
        (eq, ":event_type", multiplayer_event_coop_send_to_server),
        (store_script_param, ":event_subtype", 3),

        (try_begin),
          (eq, ":event_subtype", coop_event_start_map),
          (try_begin),
            (player_is_admin, ":player_no"),
            (this_or_next|eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
            (eq, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
            (get_max_players, ":num_players"),
            (try_for_range, ":all_player_no", 0, ":num_players"), 
              (player_is_active, ":all_player_no"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_set_scene_1, "$coop_time_of_day"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_set_scene_2, "$coop_rain"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_set_scene_3, "$coop_cloud"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_set_scene_4, "$coop_haze"),
              (multiplayer_send_4_int_to_player, ":all_player_no", multiplayer_event_coop_send_to_player, coop_event_set_scene_5, "$coop_castle_banner"),
            (try_end),
            (call_script, "script_coop_get_battle_state", 3), #sets state to started
            (team_set_faction, 0, "$coop_team_1_faction"),
            (team_set_faction, 1, "$coop_team_2_faction"),
            (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
            (start_multiplayer_mission, reg0, "$coop_battle_scene", 1),
          (try_end),

        (else_try),
          (eq, ":event_subtype", coop_event_setup_battle), #have server load saved battle
          (try_begin),
            (player_is_admin, ":player_no"),
            (call_script, "script_coop_on_admin_panel_load"),
            (eq, "$coop_battle_state", coop_battle_state_setup_mp),#only if coop battle is setup
            (call_script, "script_coop_server_send_admin_settings_to_player", ":player_no"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_receive_next_string, 3),
            (str_store_server_password, s0),
            (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
            (call_script, "script_coop_get_battle_state", 1), #sets coop_battle_state
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_battle_state, "$coop_battle_state"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_skip_menu, "$coop_skip_menu"),
          (try_end),
        (else_try),
          (eq, ":event_subtype", coop_event_start_battle), 
          (try_begin),
            (eq, "$coop_battle_started", 0),
            (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
            (reset_mission_timer_a),
          (try_end),
        (else_try),
          (eq, ":event_subtype", coop_event_end_battle),
          (try_begin),
            (eq, "$coop_battle_started", 1),
            (call_script, "script_coop_copy_parties_to_file_mp"),
          (try_end),
          (try_begin),
            (neg|multiplayer_is_dedicated_server),
            (finish_mission,0), #alway end
          (try_end),
        (else_try),
          (eq, ":event_subtype", coop_event_open_admin_panel),
          (try_begin),
            (player_is_admin, ":player_no"),
            (call_script, "script_coop_server_send_admin_settings_to_player", ":player_no"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_receive_next_string, 3),
            (str_store_server_password, s0),
            (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),

            (call_script, "script_coop_get_battle_state", 1), #sets coop_battle_state
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_battle_state, "$coop_battle_state"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_skip_menu, "$coop_skip_menu"),
          (try_end),
        (else_try),
          (eq, ":event_subtype", coop_event_open_game_rules),
          (call_script, "script_coop_server_send_admin_settings_to_player", ":player_no"),
          (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_open_game_rules),
        (else_try),
          (eq, ":event_subtype", coop_event_battle_size),
          (store_script_param, ":value", 4),
          (try_begin),
            (ge, ":value", coop_min_battle_size),
            (assign, "$coop_battle_size", ":value"), #store current battle size setting
          (try_end),
        (else_try),
          (eq, ":event_subtype", coop_event_spawn_formation),
          (store_script_param, ":value", 4),
          (assign, "$coop_battle_spawn_formation", ":value"),
		  #Begin terrain generation
	#	 (else_try),
	#	 ####Extend to all
	#	 
	#	         (eq, ":event_subtype", coop_set_setting_use_dmod),
    #    (store_script_param, ":value", 4),
    #    (assign, "$setting_use_dmod", ":value"),
		
		      (else_try),
        (eq, ":event_subtype", coop_set_key_crouch),
        (store_script_param, ":value", 4),
        (assign, "$key_crouch", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_key_crouch_command),
        (store_script_param, ":value", 4),
        (assign, "$key_crouch_command", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_key_stand_command),
        (store_script_param, ":value", 4),
        (assign, "$key_stand_command", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_g_crouch_speed_limiter),
        (store_script_param, ":value", 4),
        (assign, "$g_crouch_speed_limiter", ":value"),
				      (else_try),			  
        (eq, ":event_subtype", coop_set_ai_crouch_mode),
        (store_script_param, ":value", 4),
        (assign, "$ai_crouch_mode", ":value"),
	#			      (else_try),
	#				  
    #    (eq, ":event_subtype", coop_set_g_player_party_icon),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_player_party_icon", ":value"),
				      (else_try),			  
        (eq, ":event_subtype", coop_set_sp_shield_bash),
        (store_script_param, ":value", 4),
        (assign, "$sp_shield_bash_coop", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_sp_shield_bash_ai),
        (store_script_param, ":value", 4),
        (assign, "$sp_shield_bash_ai_coop", ":value"),
		
						      (else_try),
					  
        (eq, ":event_subtype", coop_set_archerpos),
        (store_script_param, ":value", 4),
        (assign, "$experimental_archers", ":value"),
								      (else_try),
					  
        (eq, ":event_subtype", coop_set_ai_mode),
        (store_script_param, ":value", 4),
        (assign, "$g_doghotel_enable_brainy_bots", ":value"),
	#			      (else_try),
	#				  
    #    (eq, ":event_subtype", coop_set_setting_use_spearwall),
    #    (store_script_param, ":value", 4),
    #    (assign, "$setting_use_spearwall", ":value"),
	#			      (else_try),
	#				  
    #    (eq, ":event_subtype", coop_set_g_battle_preparation),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_battle_preparation", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_set_g_battle_preparation_phase),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_battle_preparation_phase", ":value"),
				      (else_try),
        (eq, ":event_subtype", coop_set_g_rand_rain_limit),
        (store_script_param, ":value", 4),
        (assign, "$g_rand_rain_limit", ":value"),
		#						      (else_try),
        #(eq, ":event_subtype", coop_set_belfry_position),
        #(store_script_param, ":value", 4),
        #(assign, "$belfry_positioned", ":value"),
		#				      (else_try),
        #(eq, ":event_subtype", coop_set_belfry_sound),
        #(store_script_param, ":value", 4),
        #(assign, "$belfry_sound", ":value"),
		#						      (else_try),
        #(eq, ":event_subtype", coop_use_belfry),
        #(store_script_param, ":value", 4),
        #(assign, "$coop_use_belfry", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_set_g_reinforcement_waves),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_reinforcement_waves", ":value"),
						      (else_try),
#        (eq, ":event_subtype", coop_set_tom_sand_storm_chance),
#        (store_script_param, ":value", 4),
#        (assign, "$tom_sand_storm_chance", ":value"),
#						      (else_try),
        (eq, ":event_subtype", coop_set_tom_use_banners),
        (store_script_param, ":value", 4),
        (assign, "$tom_use_banners", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_tom_bonus_banners),
        (store_script_param, ":value", 4),
        (assign, "$tom_bonus_banners", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_tom_use_battlefields),
        (store_script_param, ":value", 4),
        (assign, "$tom_use_battlefields", ":value"),
		#				      (else_try),
       #(eq, ":event_subtype", coop_set_tom_weapon_break),
       #(store_script_param, ":value", 4),
       #(assign, "$tom_weapon_break", ":value"),
		#				      (else_try),
       #(eq, ":event_subtype", coop_set_tom_lance_breaking),
       #(store_script_param, ":value", 4),
       #(assign, "$tom_lance_breaking", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_coop_generate_reduction),
        (store_script_param, ":value", 4),
        (assign, "$coop_generate_reduction", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_faction),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_faction", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_party_id),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_party_id", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_state),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_state", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_freelancer_state),
    #    (store_script_param, ":value", 4),
    #    (assign, "$freelancer_state", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_men_are_pleased),
    #    (store_script_param, ":value", 4),
    #    (assign, "$men_are_pleased", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_tom_use_longships),
    #    (store_script_param, ":value", 4),
    #    (assign, "$tom_use_longships", ":value"),	
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_use_feudal_lance),
    #    (store_script_param, ":value", 4),
    #    (assign, "$use_feudal_lance", ":value"),
		      (else_try),
		 
		 
		 ####End Extension

		(eq, ":event_subtype", coop_set_historical_banners),
		(store_script_param, ":value", 4),
		(assign, "$historical_banners", ":value"),
					(else_try),
		(eq, ":event_subtype", coop_set_randomize_player_shield),
		(store_script_param, ":value", 4),
		(assign, "$randomize_player_shield", ":value"),
				  #numerical settings template step 1 begin
					(else_try),
          (eq, ":event_subtype", coop_set_tom_sand_storm_chance),
          (store_script_param, ":value", 4),
          (try_begin),
            (ge, ":value", coop_sandstorm_chance_min),
            (assign, "$tom_sand_storm_chance", ":value"), #store current battle size setting
          (try_end),
		  #numerical settings template step 1 end
		  					(else_try),		
		(eq, ":event_subtype", coop_sand_storm),
		(store_script_param, ":value", 4),
		(assign, "$tom_sand_storm", ":value"),
		(else_try),
          (eq, ":event_subtype", coop_set_torch_chance),
          (store_script_param, ":value", 4),
          (try_begin),
            (ge, ":value", coop_torch_chance_min),
            (assign, "$torch_chance_coop", ":value"), #store current battle size setting
          (try_end),
		  		(else_try),
						(eq, ":event_subtype", coop_voiceset),
          (store_script_param, ":value", 4),
          (assign, "$voice_set", ":value"),
		  		(else_try),
						(eq, ":event_subtype", coop_set_camera_mode),
          (store_script_param, ":value", 4),
          (assign, "$coop_extended_camera", ":value"),
	#	  		  		 (else_try),
	#	(eq, ":event_subtype", coop_generate_swamp),
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_swamp", ":value"),
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_desert), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_desert", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_desertv2), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_desertv2", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_desertv3), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_desertv3", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_iberian), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_iberian", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_iberian2), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_iberian2", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_snow), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_snow", ":value"), 
	#	  		  		 (else_try),
    #      (eq, ":event_subtype", coop_generate_euro_hillside), #STEP 4
    #      (store_script_param, ":value", 4),
    #      (assign, "$coop_generate_euro_hillside", ":value"), 
	#	  
	#	  #End terrain generation
        (else_try),
          (eq, ":event_subtype", coop_event_skip_admin_panel),
          (store_script_param, ":value", 4),
          (assign, "$coop_skip_menu", ":value"),
        (else_try),
          (eq, ":event_subtype", coop_event_disable_inventory),
          (store_script_param, ":value", 4),
          (assign, "$coop_disable_inventory", ":value"),
        (else_try),
          (eq, ":event_subtype", coop_event_reduce_damage),
          (store_script_param, ":value", 4),
          (assign, "$coop_reduce_damage", ":value"),
        (else_try),
          (eq, ":event_subtype", coop_event_no_capture_heroes),
          (store_script_param, ":value", 4),
          (assign, "$coop_no_capture_heroes", ":value"),
        (else_try),
          (eq, ":event_subtype", coop_event_player_open_inventory_before_spawn),
          (try_begin),
            (eq, "$coop_disable_inventory", 0),#inventory access is optional
            (player_get_slot,  ":player_troop", ":player_no", slot_player_coop_selected_troop),
            (gt, ":player_troop", 0),
            (party_count_members_of_type,":num","$coop_main_party_spawn",":player_troop"),
            (eq,":num",1),
            (try_for_range, ":slot", 0, 9),
              (troop_get_inventory_slot, ":player_cur_item", ":player_troop", ":slot"),
              (troop_get_inventory_slot_modifier, ":player_cur_imod", ":player_troop", ":slot"),
              (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_inv_troop_set_slot, ":slot", ":player_cur_item", ":player_cur_imod"),
            (try_end),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_prsnt_coop_item_select), #done
          (try_end),

        (else_try),
          (eq, ":event_subtype", coop_event_player_get_selected_item_types),
          (store_script_param, ":itm_type_1", 4),
          (store_script_param, ":itm_type_2", 5),

          (player_get_slot,  ":player_troop", ":player_no", slot_player_coop_selected_troop),
          (try_begin),
            (player_get_agent_id, ":player_agent", ":player_no"),
            (ge, ":player_agent", 0),
            (agent_get_troop_id, ":player_troop", ":player_agent"),
          (try_end),     
          (troop_is_hero, ":player_troop"),

          (troop_get_inventory_capacity, ":end", "trp_temp_troop"),
          (val_add,":end", 1), 
          (try_for_range, ":slot", 10, ":end"),
            (troop_get_inventory_slot, ":item", "trp_temp_troop", ":slot"), #inventory troop
            (troop_get_inventory_slot_modifier, ":imod", "trp_temp_troop", ":slot"),
            #  (troop_inventory_slot_get_item_amount, ":item_quant", ":troop_2", ":slot"),
            (gt, ":item", 0),
            (item_get_type, ":item_class", ":item"),

            (assign, ":continue_2", 0),
            (try_begin),
              (eq, ":itm_type_1", itp_type_one_handed_wpn),
              (is_between, ":item_class", itp_type_pistol, itp_type_animal), #add firearms here
              (assign, ":continue_2", 1),
            (else_try),
              (is_between, ":item_class", ":itm_type_1", ":itm_type_2"),
              (assign, ":continue_2", 1),
            (try_end),
            (eq, ":continue_2", 1),
            (call_script, "script_coop_troop_can_use_item",":player_troop", ":item", ":imod"),
            (eq, reg0, 1),
            (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_send_inventory, ":slot", ":item", ":imod"),
          # (assign, reg1, ":slot"), 
          # (str_store_item_name, s40, ":item"),
          # (display_message, "@sending inv slot {reg1}  = {reg0} {s40} "),
          (try_end),
          (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_prsnt_coop_item_select), #done

        (else_try),
          (eq, ":event_subtype", coop_event_player_ask_for_selected_item),
          (store_script_param, ":equip_slot", 4),
          (store_script_param, ":item_id", 5),
          (store_script_param, ":party_inv_slot", 6),
          (player_get_slot,  ":player_troop", ":player_no", slot_player_coop_selected_troop),
          (try_begin),
            (player_get_agent_id, ":player_agent", ":player_no"),
            (ge, ":player_agent", 0),
            (agent_get_troop_id, ":player_troop", ":player_agent"),
          (try_end),     
          (troop_is_hero, ":player_troop"),

          (try_begin),
            (gt, ":item_id", 0),
            (ge, ":party_inv_slot", 10),

            (troop_get_inventory_slot, ":cur_item", ":player_troop", ":equip_slot"),
            (troop_get_inventory_slot_modifier, ":cur_imod", ":player_troop", ":equip_slot"),
            (troop_get_inventory_slot, ":new_item", "trp_temp_troop", ":party_inv_slot"),
            (troop_get_inventory_slot_modifier, ":new_imod", "trp_temp_troop", ":party_inv_slot"),

            (try_begin),
              (eq, ":item_id", ":new_item"),
              (call_script, "script_coop_troop_can_use_item",":player_troop", ":new_item", ":new_imod"),
              (eq, reg0, 1),
              (troop_set_inventory_slot, ":player_troop", ":equip_slot", ":new_item"),
              (troop_set_inventory_slot_modifier, ":player_troop", ":equip_slot", ":new_imod"),
              (troop_set_inventory_slot, "trp_temp_troop", ":party_inv_slot", ":cur_item"),
              (troop_set_inventory_slot_modifier, "trp_temp_troop", ":party_inv_slot", ":cur_imod"),
#FIX
              #change item on agent
              # (try_begin),
                # (player_get_agent_id, ":player_agent", ":player_no"),
                # (ge, ":player_agent", 0),
                # (lt, ":equip_slot", 4),
                # (neg|is_vanilla_warband),
                # (agent_set_item_slot, ":player_agent", ":equip_slot", ":new_item", ":new_imod"),# removed in WSE 3 
              # (try_end),

              (try_begin),
                (player_get_agent_id, ":player_agent", ":player_no"),
                (ge, ":player_agent", 0),
                (lt, ":equip_slot", 4),
                (try_begin), 
                  (gt, ":cur_item", 0),
                  (agent_unequip_item,":player_agent",":cur_item",":equip_slot"),
                (try_end),
                (agent_equip_item,":player_agent",":new_item",":equip_slot"),

                (neg|is_vanilla_warband),
                (agent_set_item_slot_modifier, ":player_agent",":equip_slot", ":new_imod"), #Sets <agent_no>'s <item_slot_no> modifier to <item_modifier_no>
              (try_end),



            (else_try),
              (display_message, "@Trade failed."),
            (try_end),
            #after trade refresh that equip slot
            (troop_get_inventory_slot, ":player_cur_item", ":player_troop", ":equip_slot"),
            (troop_get_inventory_slot_modifier, ":player_cur_imod", ":player_troop", ":equip_slot"),
            (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_inv_troop_set_slot, ":equip_slot", ":player_cur_item", ":player_cur_imod"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_prsnt_coop_item_select), #done


            (try_begin), 
              (gt, ":new_item", 0),
              (str_store_item_name, s40, ":new_item"),
            (else_try),
              (str_store_string, s40, "@none"),
            (try_end),
            (try_begin), 
              (gt, ":cur_item", 0),
              (str_store_item_name, s42, ":cur_item"),
            (else_try),
              (str_store_string, s42, "@none"),
            (try_end),
            (str_store_troop_name, s41, ":player_troop"),
            (display_message, "@{s41} traded {s42} for {s40}."),

          (try_end),

        (else_try),
          (eq, ":event_subtype", coop_event_player_remove_selected_item),
          (store_script_param, ":equip_slot", 4),
          (store_script_param, ":item_remove", 5),
          (player_get_slot,  ":player_troop", ":player_no", slot_player_coop_selected_troop),
          (try_begin), #if agent has spawned already
            (player_get_agent_id, ":player_agent", ":player_no"),
            (ge, ":player_agent", 0),
            (agent_get_troop_id, ":player_troop", ":player_agent"),
          (try_end),     
          (troop_is_hero, ":player_troop"),

          (try_begin),
            (gt, ":item_remove", 0),
            (troop_get_inventory_slot, ":cur_item", ":player_troop", ":equip_slot"),
            (troop_get_inventory_slot_modifier, ":cur_imod", ":player_troop", ":equip_slot"),
            (eq, ":item_remove", ":cur_item"),

            (troop_get_inventory_capacity, ":end", "trp_temp_troop"),
            (val_add,":end", 1), 
            (try_for_range, ":party_inv_slot", 10, ":end"),
              (troop_get_inventory_slot, ":party_inv_item", "trp_temp_troop", ":party_inv_slot"),
              (lt, ":party_inv_item", 1),
              (troop_set_inventory_slot, ":player_troop", ":equip_slot", -1),
              (troop_set_inventory_slot_modifier, ":player_troop", ":equip_slot", -1),
              (troop_set_inventory_slot, "trp_temp_troop", ":party_inv_slot", ":cur_item"),
              (troop_set_inventory_slot_modifier, "trp_temp_troop", ":party_inv_slot", ":cur_imod"),

              (try_begin),
                (lt, ":equip_slot", 4),
                (player_get_agent_id, ":player_agent", ":player_no"),
                (ge, ":player_agent", 0),
                (agent_unequip_item, ":player_agent", ":cur_item", ":equip_slot"), #(agent_unequip_item, <agent_id>, <item_id>, [weapon_slot_no]),
              (try_end),
              (assign, ":end", 0),
            (try_end),
          (try_end),

        (else_try),
          (eq, ":event_subtype", coop_event_raise_attribute),
          (store_script_param, ":attr_id", 4),
          (player_get_troop_id, ":troop_no", ":player_no"),
          (troop_get_attribute_points, ":pts", ":troop_no"),
          (gt, ":pts", 0),
          (is_between, ":attr_id", 0, 4),
          (troop_raise_attribute, ":troop_no", ":attr_id", 1),
          (val_sub, ":pts", 1),
          (troop_set_attribute_points, ":troop_no", ":pts"),
          (call_script, "script_coop_save_character", ":player_no"),
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_stat_updated, 0),

        (else_try),
          (eq, ":event_subtype", coop_event_raise_skill),
          (store_script_param, ":skill_id", 4),
          (player_get_troop_id, ":troop_no", ":player_no"),
          (troop_get_skill_points, ":pts", ":troop_no"),
          (gt, ":pts", 0),
          (is_between, ":skill_id", 0, 37),
          (store_skill_level, ":cur_level", ":skill_id", ":troop_no"),
          (lt, ":cur_level", 10),
          (troop_raise_skill, ":troop_no", ":skill_id", 1),
          (val_sub, ":pts", 1),
          (troop_set_skill_points, ":troop_no", ":pts"),
          (call_script, "script_coop_save_character", ":player_no"),
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_stat_updated, 0),

        (else_try),
          (eq, ":event_subtype", coop_event_raise_proficiency),
          (store_script_param, ":prof_id", 4),
          (player_get_troop_id, ":troop_no", ":player_no"),
          (troop_get_proficiency_points, ":pts", ":troop_no"),
          (gt, ":pts", 0),
          (is_between, ":prof_id", 0, 7),
          (troop_raise_proficiency_linear, ":troop_no", ":prof_id", 1),
          (val_sub, ":pts", 1),
          (troop_set_proficiency_points, ":troop_no", ":pts"),
          (call_script, "script_coop_save_character", ":player_no"),
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_stat_updated, 0),

        (else_try),
          (eq, ":event_subtype", coop_event_char_creation_bg),
          (store_script_param, ":gender", 4),
          (store_script_param, ":father", 5),
          (store_script_param, ":earlylife", 6),
          # Store partial choices in player slots
          (player_set_slot, ":player_no", 55, ":gender"),
          (player_set_slot, ":player_no", 56, ":father"),
          (player_set_slot, ":player_no", 57, ":earlylife"),
        (else_try),
          (eq, ":event_subtype", coop_event_char_creation_life),
          (store_script_param, ":adulthood", 4),
          (store_script_param, ":reason", 5),
          # Retrieve stored partial choices
          (player_get_slot, ":gender", ":player_no", 55),
          (player_get_slot, ":father", ":player_no", 56),
          (player_get_slot, ":earlylife", ":player_no", 57),
          # Apply all modifiers
          (call_script, "script_coop_apply_character_creation", ":player_no", ":gender", ":father", ":earlylife", ":adulthood", ":reason"),
          (call_script, "script_coop_send_equipment_to_client", ":player_no"),
          # Spawn near Praven by default
          (player_get_party_id, ":party_no", ":player_no"),
          (party_get_position, pos1, "p_town_6"),
          (set_fixed_point_multiplier, 1),
          (position_get_x, ":px", pos1),
          (position_get_y, ":py", pos1),
          (val_add, ":px", 2),
          (val_add, ":py", 2),
          (position_set_x, pos1, ":px"),
          (position_set_y, pos1, ":py"),
          (party_set_position, ":party_no", pos1),
          (set_fixed_point_multiplier, 1000),
          # Save character
          (call_script, "script_coop_save_character", ":player_no"),

        (else_try),
          (eq, ":event_subtype", coop_event_map_spawn_choice),
          (store_script_param, ":region", 4),
          (player_get_party_id, ":party_no", ":player_no"),
          (assign, reg0, ":region"),
          (assign, reg1, ":party_no"),
          (display_message, "@Spawn choice: region={reg0} party={reg1}"),
          # Get town position
          (try_begin),
            (eq, ":region", 0),
            (party_get_position, pos1, "p_town_6"),  # Praven
          (else_try),
            (eq, ":region", 1),
            (party_get_position, pos1, "p_town_8"),  # Reyvadin
          (else_try),
            (eq, ":region", 2),
            (party_get_position, pos1, "p_town_10"), # Tulga
          (else_try),
            (eq, ":region", 3),
            (party_get_position, pos1, "p_town_1"),  # Sargoth
          (else_try),
            (eq, ":region", 4),
            (party_get_position, pos1, "p_town_5"),  # Jelkala
          (else_try),
            (eq, ":region", 5),
            (party_get_position, pos1, "p_town_19"), # Shariz
          (try_end),
          # Offset slightly so player doesn't land on the town
          (set_fixed_point_multiplier, 1),
          (position_get_x, ":px", pos1),
          (position_get_y, ":py", pos1),
          (val_add, ":px", 2),
          (val_add, ":py", 2),
          (position_set_x, pos1, ":px"),
          (position_set_y, pos1, ":py"),
          (party_set_position, ":party_no", pos1),
          (set_fixed_point_multiplier, 1000),
          (assign, reg0, ":px"),
          (assign, reg1, ":py"),
          (display_message, "@Party moved to ({reg0}, {reg1})."),
          (call_script, "script_coop_save_character", ":player_no"),

        (try_end),


      (try_end),
      ]),

  ("coop_recv_battle_client_events",
    [
      (store_script_param, ":player_no", 1),
      (store_script_param, ":event_type", 2),
    (try_begin),
      (eq, ":event_type", multiplayer_event_coop_send_to_player_string),

      (try_begin),
        (eq, "$coop_string_received", 0), 
        (faction_set_name, "fac_player_supporters_faction", s0),
        (assign, "$coop_string_received", 1), 
      (else_try),
        (eq, "$coop_string_received", 1), 
        (class_set_name, "$coop_class_string_received", s0), #store 8 strings for troop class names
        (val_add, "$coop_class_string_received", 1),

        (try_begin),
          (eq, "$coop_class_string_received", 9), # 8 strings, add one after each = 9
          (assign, "$coop_string_received", 2), 
        (try_end),
      (else_try),
#NEW
        (eq, "$coop_string_received", 2), 
        (troop_set_name, "$coop_last_hero_received", s0),
        (assign, "$coop_string_received", 3), 
      (else_try),
        (eq, "$coop_string_received", 3), 
        (try_begin),
          (neg|is_vanilla_warband),
          (face_keys_store_string, reg1, s0),
          #ENVFIX(troop_set_face_keys, "$coop_last_hero_received", reg1),
        (try_end),
        (assign, "$coop_string_received", 2), 

      (else_try),
        (eq, "$coop_string_received", 4), #set by coop_event_round
        (server_set_password, s0),
      (try_end),

    (else_try),
      (eq, ":event_type", multiplayer_event_coop_send_to_player), 
      (store_script_param, ":event_subtype", 3),

      (try_begin),
        (eq, ":event_subtype", coop_event_store_hero_troops), 
        (store_script_param, ":hero_troop", 4),
        (store_script_param, ":var_6", 5),
        (try_begin),
          (neg|multiplayer_is_server), #server already added heroes to this party
          (party_add_members, ":var_6", ":hero_troop", 1),
        (try_end),
        (assign, "$coop_last_hero_received", ":hero_troop"), #remember troop to receive name
      (else_try),
        (eq, ":event_subtype", coop_event_round), 
        (store_script_param, ":value", 4),
        (store_script_param, ":value2", 5),
        (assign, "$coop_battle_started", ":value2"),
        (assign, "$coop_round", ":value"), #assign siege round
#NEW
#ADd events here

#End add events here
        (assign, "$coop_string_received", 4), #set this after client has received all data
        (neq, "$coop_battle_started", -1),
		#DEBUG FOR Co-Op display messages Begin
		#(display_message, "@Set this after client has received ALL data."),
#		#(multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, "str_revision"), #New #REVISION VERSION
          # player remembers troop selections, send to server when player joins (player id will change between rounds)
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_bot_type_1_wanted, "$g_multiplayer_bot_type_1_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_bot_type_2_wanted, "$g_multiplayer_bot_type_2_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_bot_type_3_wanted, "$g_multiplayer_bot_type_3_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_bot_type_4_wanted, "$g_multiplayer_bot_type_4_wanted"),

          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_0_wanted, "$coop_class_0_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_1_wanted, "$coop_class_1_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_2_wanted, "$coop_class_2_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_3_wanted, "$coop_class_3_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_4_wanted, "$coop_class_4_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_5_wanted, "$coop_class_5_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_6_wanted, "$coop_class_6_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_7_wanted, "$coop_class_7_wanted"),
          (multiplayer_send_2_int_to_server, multiplayer_event_set_bot_selection, slot_player_coop_class_8_wanted, "$coop_class_8_wanted"),
		#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_dmod, "$setting_use_dmod"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch, "$key_crouch"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch_command, "$key_crouch_command"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_stand_command, "$key_stand_command"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_crouch_speed_limiter, "$g_crouch_speed_limiter"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_ai_crouch_mode, "$ai_crouch_mode"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_player_party_icon, "$g_player_party_icon"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash, "$sp_shield_bash_coop"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash_ai, "$sp_shield_bash_ai_coop"), #Step 4
					#	(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_spearwall, "$setting_use_spearwall"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation, "$g_battle_preparation"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation_phase, "$g_battle_preparation_phase"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_rand_rain_limit, "$g_rand_rain_limit"), #Step 4
			#			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_position, "$belfry_positioned"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_sound, "$belfry_sound"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_use_belfry, "$coop_use_belfry"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_reinforcement_waves, "$g_reinforcement_waves"),



			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_banners, "$tom_use_banners"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_bonus_banners, "$tom_bonus_banners"), #Step 4
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_battlefields, "$tom_use_battlefields"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_weapon_break, "$tom_weapon_break"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_lance_breaking, "$tom_lance_breaking"),
			###((multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_coop_generate_reduction, "$coop_generate_reduction"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_faction, "$crusader_faction"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_party_id, "$crusader_party_id"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_state, "$crusader_state"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_freelancer_state, "$freelancer_state"), #Step 4
			
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_men_are_pleased, "$men_are_pleased"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_longships, "$tom_use_longships"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_use_feudal_lance, "$use_feudal_lance"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_historical_banners, "$historical_banners"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_randomize_player_shield, "$randomize_player_shield"),
						#Numerical Settings Template Step 5 Begin (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_sand_storm_chance, "$tom_sand_storm_chance"),
						###((multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_torch_chance, "$torch_chance_coop"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_camera_mode, "$coop_extended_camera"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_voiceset, "$voice_set"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_sand_storm, "$tom_sand_storm"),
						#Numerical Settings Template Step 5 End (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
			#End Extension
        (try_begin), 
          (eq, "$coop_round", coop_round_battle),
          (assign, "$coop_my_team", multi_team_unassigned),  
          (start_presentation, "prsnt_coop_welcome_message"), #start welcome message after getting team data
        (else_try),
          (multiplayer_get_my_player, ":my_player_no"), #change my team in later rounds
          (ge, ":my_player_no", 0),
          (player_set_team_no, ":my_player_no", "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_team_no, "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_troop_id, "$coop_my_troop_no"),
        (try_end),
      (else_try),
        (eq, ":event_subtype", coop_event_troop_banner), 
        (store_script_param, ":value", 4),
        (assign, "$coop_agent_banner", ":value"), #assign spawning troops banner
      (else_try),
        (eq, ":event_subtype", coop_event_troop_raise_attribute),
        (store_script_param, ":value", 4),
        (store_script_param, ":selected_troop", 5),
        (store_script_param, ":attribute", 6),
        (troop_raise_attribute, ":selected_troop", ":attribute", -1000),
        (troop_raise_attribute, ":selected_troop", ":attribute", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_troop_raise_skill),
        (store_script_param, ":value", 4),
        (store_script_param, ":selected_troop", 5),
        (store_script_param, ":skill_level_leadership_var_1", 6),
        (troop_raise_skill, ":selected_troop", ":skill_level_leadership_var_1", -1000),
        (troop_raise_skill, ":selected_troop", ":skill_level_leadership_var_1", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_troop_raise_proficiency_linear),
        (store_script_param, ":value", 4),
        (store_script_param, ":selected_troop", 5),
        (store_script_param, ":prof", 6),
        (troop_raise_proficiency_linear, ":selected_troop", ":prof", -1000),
        (troop_raise_proficiency_linear, ":selected_troop", ":prof", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_troop_set_slot),
        (store_script_param, ":value", 4),
        (store_script_param, ":selected_troop", 5),
        (store_script_param, ":slot", 6),
        (troop_set_slot, ":selected_troop", ":slot", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_player_set_slot),
        (store_script_param, ":value", 4),
        (store_script_param, ":selected_player", 5),
        (store_script_param, ":slot", 6),
        (player_set_slot, ":selected_player", ":slot", ":value"),
        (try_begin), #if receiving other player spawn choice, refresh presentation
          (eq, ":slot", slot_player_coop_selected_troop),
          (assign, "$coop_refresh_troop_select_presentation", 1),

          (try_begin),
            (gt, ":value", 0),
            (str_store_player_username, s40, ":selected_player"),
            (str_store_troop_name, s41, ":value"),
            (display_message, "@{s40} has picked {s41}. "), #tell server when player picks troop
          (try_end), 
        (try_end), 
      (else_try),
        (eq, ":event_subtype", coop_event_inv_troop_set_slot),
        (store_script_param, ":slot", 4),
        (store_script_param, ":item", 5),
        (store_script_param, ":imod", 6),
        (troop_set_slot, "trp_temp_troop", ":slot", ":item"), #item slot 0..8
        (val_add, ":slot", 10),
        (troop_set_slot, "trp_temp_troop", ":slot", ":imod"),#imod slot 10..18


      (else_try),
        (eq, ":event_subtype", coop_event_send_inventory), #receive items of type for equipment slot
        (store_script_param, ":inv_slot", 4),
        (store_script_param, ":item", 5),
        (store_script_param, ":imod", 6),
        #  (store_script_param, ":item_quant", 6), #would need its own message type
        (store_add, ":cur_slot_index", "$coop_num_available_items", multi_data_item_button_indices_begin),
        (store_add, ":cur_imod_index",":cur_slot_index",100),
        (troop_set_slot, "trp_multiplayer_data", ":cur_slot_index", ":item"),
        (troop_set_slot, "trp_temp_troop", ":cur_slot_index", ":inv_slot"), #slot matching multi_data_item_button_indices_begin stores which inventory slot this item is from
        (troop_set_slot, "trp_temp_troop", ":cur_imod_index", ":imod"),
        (val_add, "$coop_num_available_items", 1),
      (else_try),
        (eq, ":event_subtype", coop_event_prsnt_coop_item_select),
        (start_presentation, "prsnt_coop_item_select"), #start presentation after we recieve all inventory
      (else_try),
        (eq, ":event_subtype", coop_event_set_scene_1),
        (store_script_param, ":value", 4),
        (assign, "$coop_time_of_day", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_set_scene_2),
        (store_script_param, ":value", 4),
        (assign, "$coop_rain", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_set_scene_3),
        (store_script_param, ":value", 4),
        (assign, "$coop_cloud", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_set_scene_4),
        (store_script_param, ":value", 4),
        (assign, "$coop_haze", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_set_scene_5),
        (store_script_param, ":value", 4),
        (assign, "$coop_castle_banner", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_return_team_faction),
        (store_script_param, ":team", 4),
        (store_script_param, ":value", 5),
        (try_begin), 
          (eq, ":team", 1),
          (assign, "$coop_team_1_faction", ":value"),
        (else_try),
          (eq, ":team", 2),
          (assign, "$coop_team_2_faction", ":value"),
        (try_end),
      (else_try),
        (eq, ":event_subtype", coop_event_return_team_troop_num),
        (store_script_param, ":team", 4),
        (store_script_param, ":value", 5),
        (try_begin), 
          (eq, ":team", 1),
          (assign, "$coop_team_1_troop_num", ":value"),
        (else_try),
          (eq, ":team", 2),
          (assign, "$coop_team_2_troop_num", ":value"),
        (try_end),
      (else_try),
        (eq, ":event_subtype", coop_event_return_spawn_formation),
        (store_script_param, ":value", 4),
        (assign, "$coop_battle_spawn_formation", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_set_setting_use_dmod),
    #    (store_script_param, ":value", 4),
    #    (assign, "$setting_use_dmod", ":value"),
		
		      (else_try),
        (eq, ":event_subtype", coop_set_key_crouch),
        (store_script_param, ":value", 4),
        (assign, "$key_crouch", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_key_crouch_command),
        (store_script_param, ":value", 4),
        (assign, "$key_crouch_command", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_key_stand_command),
        (store_script_param, ":value", 4),
        (assign, "$key_stand_command", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_g_crouch_speed_limiter),
        (store_script_param, ":value", 4),
        (assign, "$g_crouch_speed_limiter", ":value"),
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_ai_crouch_mode),
        (store_script_param, ":value", 4),
        (assign, "$ai_crouch_mode", ":value"),
				      (else_try),				  
    #    (eq, ":event_subtype", coop_set_g_player_party_icon),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_player_party_icon", ":value"),
	#			      (else_try),
					  
        (eq, ":event_subtype", coop_set_sp_shield_bash),
        (store_script_param, ":value", 4),
        (assign, "$sp_shield_bash_coop", ":value"),
						      (else_try),
					  
        (eq, ":event_subtype", coop_set_archerpos),
        (store_script_param, ":value", 4),
        (assign, "$experimental_archers", ":value"),
		
								      (else_try),
					  
        (eq, ":event_subtype", coop_set_ai_mode),
        (store_script_param, ":value", 4),
        (assign, "$g_doghotel_enable_brainy_bots", ":value"),
		
				      (else_try),
					  
        (eq, ":event_subtype", coop_set_sp_shield_bash_ai),
        (store_script_param, ":value", 4),
        (assign, "$sp_shield_bash_ai_coop", ":value"),
		#		      (else_try),
		#			  
      #(eq, ":event_subtype", coop_set_setting_use_spearwall),
      #(store_script_param, ":value", 4),
      #(assign, "$setting_use_spearwall", ":value"),
	#			      (else_try),
	#				  
    #    (eq, ":event_subtype", coop_set_g_battle_preparation),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_battle_preparation", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_set_g_battle_preparation_phase),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_battle_preparation_phase", ":value"),
				      (else_try),
        (eq, ":event_subtype", coop_set_g_rand_rain_limit),
        (store_script_param, ":value", 4),
        (assign, "$g_rand_rain_limit", ":value"),
		#						      (else_try),
        #(eq, ":event_subtype", coop_set_belfry_position),
        #(store_script_param, ":value", 4),
        #(assign, "$belfry_positioned", ":value"),
		#				      (else_try),
        #(eq, ":event_subtype", coop_set_belfry_sound),
        #(store_script_param, ":value", 4),
        #(assign, "$belfry_sound", ":value"),
		#						      (else_try),
        #(eq, ":event_subtype", coop_use_belfry),
        #(store_script_param, ":value", 4),
        #(assign, "$coop_use_belfry", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_set_g_reinforcement_waves),
    #    (store_script_param, ":value", 4),
    #    (assign, "$g_reinforcement_waves", ":value"),
#						      (else_try),
#        (eq, ":event_subtype", coop_set_tom_sand_storm_chance),
#        (store_script_param, ":value", 4),
#        (assign, "$tom_sand_storm_chance", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_tom_use_banners),
        (store_script_param, ":value", 4),
        (assign, "$tom_use_banners", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_tom_bonus_banners),
        (store_script_param, ":value", 4),
        (assign, "$tom_bonus_banners", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_tom_use_battlefields),
        (store_script_param, ":value", 4),
        (assign, "$tom_use_battlefields", ":value"),
		#				      (else_try),
       #(eq, ":event_subtype", coop_set_tom_weapon_break),
       #(store_script_param, ":value", 4),
       #(assign, "$tom_weapon_break", ":value"),
		#				      (else_try),
       #(eq, ":event_subtype", coop_set_tom_lance_breaking),
       #(store_script_param, ":value", 4),
       #(assign, "$tom_lance_breaking", ":value"),
						      (else_try),
        (eq, ":event_subtype", coop_set_coop_generate_reduction),
        (store_script_param, ":value", 4),
        (assign, "$coop_generate_reduction", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_faction),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_faction", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_party_id),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_party_id", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_crusader_state),
    #    (store_script_param, ":value", 4),
    #    (assign, "$crusader_state", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_freelancer_state),
    #    (store_script_param, ":value", 4),
    #    (assign, "$freelancer_state", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_men_are_pleased),
    #    (store_script_param, ":value", 4),
    #    (assign, "$men_are_pleased", ":value"),
		#				      (else_try),
       #(eq, ":event_subtype", coop_set_tom_use_longships),
       #(store_script_param, ":value", 4),
       #(assign, "$tom_use_longships", ":value"),
	#					      (else_try),
    #    (eq, ":event_subtype", coop_set_use_feudal_lance),
    #    (store_script_param, ":value", 4),
    #    (assign, "$use_feudal_lance", ":value"),
		      (else_try),
        (eq, ":event_subtype", coop_set_historical_banners),
        (store_script_param, ":value", 4),
        (assign, "$historical_banners", ":value"),
				      (else_try),
        (eq, ":event_subtype", coop_set_randomize_player_shield),
        (store_script_param, ":value", 4),
        (assign, "$randomize_player_shield", ":value"),
		#Numerical Settings Template Step 4 begin
		      (else_try),
			          (eq, ":event_subtype", coop_set_tom_sand_storm_chance),
        (store_script_param, ":value", 4),
        (assign, "$tom_sand_storm_chance", ":value"),
				      (else_try),
			          (eq, ":event_subtype", coop_sand_storm),
        (store_script_param, ":value", 4),
        (assign, "$tom_sand_storm", ":value"),
						      (else_try),
			          (eq, ":event_subtype", coop_voiceset),
        (store_script_param, ":value", 4),
        (assign, "$voice_set", ":value"),
		#Numerical Settings Template Step 4 end
				      (else_try),
			          (eq, ":event_subtype", coop_set_torch_chance),
        (store_script_param, ":value", 4),
        (assign, "$torch_chance_coop", ":value"),
		#Numerical Settings Template Step 4 end
      (else_try),
	  			  #Begin terrain generation
        (eq, ":event_subtype", coop_set_camera_mode), # STEP 4
        (store_script_param, ":value", 4),
        (assign, "$coop_extended_camera", ":value"),
				      (else_try),
	#		  #Begin terrain generation
    #    (eq, ":event_subtype", coop_generate_swamp), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_swamp", ":value"),
	#			      (else_try),
    #    (eq, ":event_subtype", coop_generate_desert), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_desert", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_desertv2), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_desertv2", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_desertv3), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_desertv3", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_iberian), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_iberian", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_iberian2), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_iberian2", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_snow), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_snow", ":value"),
    #  (else_try),
	#          (eq, ":event_subtype", coop_generate_euro_hillside), # STEP 4
    #    (store_script_param, ":value", 4),
    #    (assign, "$coop_generate_euro_hillside", ":value"),
    #  (else_try),
	 #Emd terrain generaiton
        (eq, ":event_subtype", coop_event_return_battle_size),
        (store_script_param, ":value", 4),
        (assign, "$coop_battle_size", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_return_game_type),
        (store_script_param, ":value", 4),
        (assign, "$g_multiplayer_game_type", ":value"),
     (else_try),
        (eq, ":event_subtype", coop_event_return_castle_party),
        (store_script_param, ":value", 4),
        (assign, "$coop_map_party", ":value"),
     (else_try),
        (eq, ":event_subtype", coop_event_return_battle_scene),
        (store_script_param, ":value", 4),
        (assign, "$coop_battle_scene", ":value"),
     (else_try),
        (eq, ":event_subtype", coop_event_return_disable_inventory),
        (store_script_param, ":value", 4),
        (assign, "$coop_disable_inventory", ":value"),
     (else_try),
        (eq, ":event_subtype", coop_event_return_reduce_damage),
        (store_script_param, ":value", 4),
        (assign, "$coop_reduce_damage", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_return_no_capture_heroes),
        (store_script_param, ":value", 4),
        (assign, "$coop_no_capture_heroes", ":value"),
      (else_try),
        (eq, ":event_subtype", coop_event_return_skip_menu),
        (store_script_param, ":value", 4),
        (assign, "$coop_skip_menu", ":value"),
        (start_presentation, "prsnt_coop_admin_panel"),#this is the last option in admin panel, so start the presentation
      (else_try),
        (eq, ":event_subtype", coop_event_return_open_game_rules),
        #this is the last message for open rules
        (assign, "$g_multiplayer_show_server_rules", 1),
        (start_presentation, "prsnt_coop_welcome_message"),
      (else_try),
        (eq, ":event_subtype", coop_event_receive_next_string),
        (store_script_param, ":value", 4),
        (assign, "$coop_string_received", ":value"), 
      (else_try),
        (eq, ":event_subtype", coop_event_return_num_reserves),
        (store_script_param, ":team", 4),
        (store_script_param, ":value", 5),
        (try_begin), 
          (eq, ":team", 1),
          (assign, "$coop_num_bots_team_1", ":value"),
        (else_try),
          (eq, ":team", 2),
          (assign, "$coop_num_bots_team_2", ":value"),
        (try_end),
      (else_try),
        (eq, ":event_subtype", coop_event_return_battle_state),
        (store_script_param, ":value", 4),
        (assign, "$coop_battle_state", ":value"), 
      (else_try),
        (eq, ":event_subtype", coop_event_result_saved),
        (assign, "$coop_battle_started", -1),
        (display_message, "@Battle result saved.", 0x000730fc),
		(display_message, "@You can now load back your save and reach the same encounter then hit (Use Multiplayer Battle Results)", 0x000730fc),
		#####MUSICBOX
		(neg|multiplayer_is_dedicated_server),
		##(stop_all_sounds, 1), #Used to be value of 11new
      (try_end), 





    (try_end),
      ]),





#script_coop_server_send_admin_settings_to_player
  # Input: arg1 = player_agent
  # Output: none
  ("coop_server_send_admin_settings_to_player",
    [
     (store_script_param, ":player_no", 1),
            (server_get_renaming_server_allowed, "$g_multiplayer_renaming_server_allowed"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_renaming_server_allowed, "$g_multiplayer_renaming_server_allowed"),
            (server_get_max_num_players, ":max_num_players"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_max_num_players, ":max_num_players"),
            # (server_get_anti_cheat, ":server_anti_cheat"),
            # (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_anti_cheat, ":server_anti_cheat"),
            (server_get_friendly_fire, ":server_friendly_fire"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_friendly_fire, ":server_friendly_fire"),
            (server_get_melee_friendly_fire, ":server_melee_friendly_fire"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_melee_friendly_fire, ":server_melee_friendly_fire"),
            (server_get_friendly_fire_damage_self_ratio, ":friendly_fire_damage_self_ratio"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_friendly_fire_damage_self_ratio, ":friendly_fire_damage_self_ratio"),
            (server_get_friendly_fire_damage_friend_ratio, ":friendly_fire_damage_friend_ratio"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_friendly_fire_damage_friend_ratio, ":friendly_fire_damage_friend_ratio"),
            (server_get_ghost_mode, ":server_ghost_mode"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_ghost_mode, ":server_ghost_mode"),
            (server_get_control_block_dir, ":server_control_block_dir"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_control_block_dir, ":server_control_block_dir"),
            (server_get_combat_speed, ":server_combat_speed"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_combat_speed, ":server_combat_speed"),
            (server_get_add_to_game_servers_list, ":server_add_to_servers_list"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_add_to_servers_list, ":server_add_to_servers_list"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_player_respawn_as_bot, "$g_multiplayer_player_respawn_as_bot"),
            (multiplayer_send_int_to_player, ":player_no", multiplayer_event_return_valid_vote_ratio, "$g_multiplayer_valid_vote_ratio"),
            (str_store_server_name, s0),
            (multiplayer_send_string_to_player, ":player_no", multiplayer_event_return_server_name, s0),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_receive_next_string, 0),
            (str_store_faction_name, s0, "fac_player_supporters_faction"),
            (multiplayer_send_string_to_player, ":player_no", multiplayer_event_coop_send_to_player_string, s0),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_team_faction, 1, "$coop_team_1_faction"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_team_faction, 2, "$coop_team_2_faction"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_team_troop_num, 1, "$coop_team_1_troop_num"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_team_troop_num, 2, "$coop_team_2_troop_num"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_spawn_formation, "$coop_battle_spawn_formation"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_battle_size, "$coop_battle_size"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_game_type, "$g_multiplayer_game_type"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_castle_party, "$coop_map_party"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_battle_scene, "$coop_battle_scene"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_disable_inventory, "$coop_disable_inventory"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_reduce_damage, "$coop_reduce_damage"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_no_capture_heroes, "$coop_no_capture_heroes"),
			#Begin terrain generation
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_swamp, "$coop_generate_swamp"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desert, "$coop_generate_desert"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desertv2, "$coop_generate_desertv2"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_desertv3, "$coop_generate_desertv3"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_iberian, "$coop_generate_iberian"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_iberian2, "$coop_generate_iberian2"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_snow, "$coop_generate_snow"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_generate_euro_hillside, "$coop_generate_euro_hillside"), #Step 4
			#End terrain generation
			
			#Extend to all Co-Op Cmds for MP
			#DEBUG FOR Co-Op display messages Begin
			#(display_message, "@TESTING Multiplayer int_2 event coop_scripts ADMINONLY - only connecting player should see this."),
			#DEBUG FOR Co-Op display messages End
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_dmod, "$setting_use_dmod"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch, "$key_crouch"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_crouch_command, "$key_crouch_command"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_key_stand_command, "$key_stand_command"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_crouch_speed_limiter, "$g_crouch_speed_limiter"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_ai_crouch_mode, "$ai_crouch_mode"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_player_party_icon, "$g_player_party_icon"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash, "$sp_shield_bash_coop"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_archerpos, "$experimental_archers"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_ai_mode, "$g_doghotel_enable_brainy_bots"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_sp_shield_bash_ai, "$sp_shield_bash_ai_coop"), #Step 4
					#	(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_setting_use_spearwall, "$setting_use_spearwall"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation, "$g_battle_preparation"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_battle_preparation_phase, "$g_battle_preparation_phase"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_rand_rain_limit, "$g_rand_rain_limit"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_position, "$belfry_positioned"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_sound, "$belfry_sound"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_use_belfry, "$coop_use_belfry"), #Step 4
			
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_g_reinforcement_waves, "$g_reinforcement_waves"),



			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_banners, "$tom_use_banners"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_bonus_banners, "$tom_bonus_banners"), #Step 4
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_battlefields, "$tom_use_battlefields"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_weapon_break, "$tom_weapon_break"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_lance_breaking, "$tom_lance_breaking"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_coop_generate_reduction, "$coop_generate_reduction"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_faction, "$crusader_faction"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_party_id, "$crusader_party_id"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_crusader_state, "$crusader_state"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_freelancer_state, "$freelancer_state"), #Step 4
			
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_men_are_pleased, "$men_are_pleased"),
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_use_longships, "$tom_use_longships"), #Step 4
			#(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_use_feudal_lance, "$use_feudal_lance"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_historical_banners, "$historical_banners"), #Step 4
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_randomize_player_shield, "$randomize_player_shield"),
						#Numerical Settings Template Step 5 Begin (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_tom_sand_storm_chance, "$tom_sand_storm_chance"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_torch_chance, "$torch_chance_coop"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_camera_mode, "$coop_extended_camera"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_voiceset, "$voice_set"),
						(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_sand_storm, "$tom_sand_storm"),
						#Numerical Settings Template Step 5 End (Note: if you wish to extend so that it allows you to save the changes into the campaign - set dict_get_int and dict_set_int).
			#End Extension
			#If adding additional features all you need is to add send to player above and event_subtype, as well as make a new constant in module_constants similiar to coop_set_ right here.
			#If you wish to extend to the menu, you'll have to do more, just read module_coop_presentations.
      ]),


#script_coop_player_access_inventory
  # Input: arg1 = player_agent
  # Output: none
  ("coop_player_access_inventory",
    [
     (store_script_param, ":player_agent", 1),
        (try_begin),
          (eq, "$coop_disable_inventory", 0),#inventory access is optional
          (agent_get_player_id,":player_no",":player_agent"),#only let troops from main party use box
          (agent_get_troop_id,":player_troop", ":player_agent"),
          (agent_get_slot, ":player_agent_party",":player_agent", slot_agent_coop_spawn_party), #SP party
          (eq, ":player_agent_party", "$coop_main_party_spawn"),
          (troop_is_hero, ":player_troop"),
          
          #first add agent items to troop
          (call_script, "script_coop_player_agent_save_items", ":player_agent"),

          #then send what troop has
          (try_for_range, ":slot", 0, 9),
            (troop_get_inventory_slot, ":player_cur_item", ":player_troop", ":slot"),
            (troop_get_inventory_slot_modifier, ":player_cur_imod", ":player_troop", ":slot"),
            (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_inv_troop_set_slot, ":slot", ":player_cur_item", ":player_cur_imod"),
          (try_end),
          (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_prsnt_coop_item_select), #done
        (try_end),

      ]),

#NEW
#script_coop_player_agent_save_items
  # Input: arg1 = player_agent
  # Output: none
  ("coop_player_agent_save_items",
    [
     (store_script_param, ":player_agent", 1),
      (agent_get_troop_id, ":agent_troop_id", ":player_agent"),
      #store items from agents
      (try_begin), 
        (neg|is_vanilla_warband),
        (try_for_range, ":slot", 0, 4), #weapons only
          (agent_get_item_slot, ":agent_item_id", ":player_agent", ":slot"), 
          (agent_get_item_slot_modifier, ":agent_imod", ":player_agent", ":slot"),
          (troop_set_inventory_slot, ":agent_troop_id", ":slot", ":agent_item_id"),
          (troop_set_inventory_slot_modifier, ":agent_troop_id", ":slot", ":agent_imod"),
        (try_end),
      (try_end),
      ]),



#ITEM BUG WORKAROUND BEGIN#####################################################
# these scripts avoid a bug that removes ranged weapons when certain thrown weapons are equiped
#script_coop_equip_player_agent
  # Input: arg1 = player_agent
  # Output: none
  ("coop_equip_player_agent",
    [
     (store_script_param, ":player_agent", 1),
        (try_begin),
          (agent_get_troop_id,":troop_2", ":player_agent"),
          (troop_is_hero, ":troop_2"),

          (try_for_range, ":slot", 0, 9), #weapon slots (0-3) + armor slots (4-8)
            (troop_get_inventory_slot, ":item", ":troop_2", ":slot"),
            (troop_get_inventory_slot_modifier, ":imod", ":troop_2", ":slot"),
            (try_begin),
              (gt, ":item", 0),
              (agent_equip_item, ":player_agent", ":item", ":slot"),
              (neg|is_vanilla_warband),
              (agent_set_item_slot_modifier, ":player_agent", ":slot", ":imod"),
            (try_end),
          (try_end),
        (try_end),
      ]),
#script_coop_check_item_bug
  ("coop_check_item_bug",
    [
     (store_script_param, ":troop_4", 1),
      (try_begin),
        (troop_is_hero, ":troop_4"),
        (try_for_range, ":slot", 19, 34), #clear slots here
          (troop_set_slot, ":troop_4", ":slot", 0), 
        (try_end),
        (assign, ":has_throw",0),
        (assign, ":has_ranged",0),

        (try_for_range, ":slot", 0, 4), #weapon slots
          (troop_get_inventory_slot, ":item", ":troop_4", ":slot"),
          (troop_get_inventory_slot_modifier, ":imod", ":troop_4", ":slot"),
          (gt, ":item", 0),
          (store_add, ":itm_slot", ":slot", 20),
          (store_add, ":imod_slot", ":slot", 30),
          (troop_set_slot, ":troop_4", ":itm_slot", ":item"), 
          (troop_set_slot, ":troop_4", ":imod_slot", ":imod"), 
          (item_get_type, ":type", ":item"),
          (try_begin),
            (eq, ":type", itp_type_thrown),
            (assign, ":has_throw", 1),
          (else_try),
            (this_or_next|eq, ":type", itp_type_pistol),
            (this_or_next|eq, ":type", itp_type_musket),
            (this_or_next|eq, ":type", itp_type_bow),
            (eq, ":type", itp_type_crossbow),
            (assign, ":has_ranged",1),
          (try_end),
        (try_end),
        (eq, ":has_throw", 1),
        (eq, ":has_ranged", 1),
        (troop_set_slot, ":troop_4", 19, 1), #troop has thrown and ranged
      (try_end),
      ]),
#ITEM BUG WORKAROUND END#####################################################



  #script_coop_display_available_items_from_inventory
  # Input: arg1 = troop_no, arg2 = item_classes_begin, arg3 = item_classes_end, arg4 = pos_x_begin, arg5 = pos_y_begin
  # Output: none
  ("coop_display_available_items_from_inventory",
   [
     #sorting
      (store_add, ":item_slots_end", "$coop_num_available_items", multi_data_item_button_indices_begin),
     (store_sub, ":item_slots_end_minus_one", ":item_slots_end", 1),
     (try_for_range, ":cur_slot", multi_data_item_button_indices_begin, ":item_slots_end_minus_one"),
       (store_add, ":cur_slot_2_begin", ":cur_slot", 1),
       (try_for_range, ":cur_slot_2", ":cur_slot_2_begin", ":item_slots_end"),
         (troop_get_slot, ":item_1", "trp_multiplayer_data", ":cur_slot"),
         (troop_get_slot, ":item_2", "trp_multiplayer_data", ":cur_slot_2"),

         (store_item_value, ":item_1_point", ":item_1"),
         (store_item_value, ":item_2_point", ":item_2"),
         (item_get_type, ":item_1_class", ":item_1"),
         (item_get_type, ":item_2_class", ":item_2"),

         (try_begin),
           (eq, ":item_1_class", 7),
           (assign, ":item_1_class", 12),
         (try_end),
         (try_begin),
           (eq, ":item_2_class", 7),
           (assign, ":item_2_class", 12),
         (try_end),

         (val_mul, ":item_1_class", 1000000), #assuming maximum item price is 1000000
         (val_mul, ":item_2_class", 1000000), #assuming maximum item price is 1000000
         (val_sub, ":item_1_point", ":item_1_class"),
         (val_sub, ":item_2_point", ":item_2_class"),

         (gt, ":item_2_point", ":item_1_point"),
         (troop_set_slot, "trp_multiplayer_data", ":cur_slot", ":item_2"),
         (troop_set_slot, "trp_multiplayer_data", ":cur_slot_2", ":item_1"),

         (troop_get_slot, ":inv_slot_1", "trp_temp_troop", ":cur_slot"), #also sort other data slots
         (troop_get_slot, ":inv_slot_2", "trp_temp_troop", ":cur_slot_2"),
         (troop_set_slot, "trp_temp_troop", ":cur_slot", ":inv_slot_2"),
         (troop_set_slot, "trp_temp_troop", ":cur_slot_2", ":inv_slot_1"),

         (store_add, ":imod_slot", ":cur_slot", 100),
         (store_add, ":imod_slot_2", ":cur_slot_2", 100),
         (troop_get_slot, ":imod_1", "trp_temp_troop", ":imod_slot"),
         (troop_get_slot, ":imod_2", "trp_temp_troop", ":imod_slot_2"),
         (troop_set_slot, "trp_temp_troop", ":imod_slot", ":imod_2"),
         (troop_set_slot, "trp_temp_troop", ":imod_slot_2", ":imod_1"),

       (try_end),
     (try_end),

      (str_clear, s0),
      (create_text_overlay, reg0, s0, tf_scrollable_style_2),
      (position_set_x, pos1, 200),#260
      (position_set_y, pos1, 75),
      (overlay_set_position, reg0, pos1),
      (position_set_x, pos1, 604),
      (position_set_y, pos1, 604),
      (overlay_set_area_size, reg0, pos1),
      (set_container_overlay, reg0),

     (assign, ":x_adder", 100),
     (assign, ":pos_x_begin", 0),
     (store_sub, ":pos_y_begin", "$coop_num_available_items", 1),  #number of items / 6 = number of rows
     (val_div, ":pos_y_begin", 6),
     (val_mul, ":pos_y_begin", 100),
     (val_add, ":pos_y_begin", 10),

     (assign, ":cur_x", ":pos_x_begin"),
     (assign, ":cur_y", ":pos_y_begin"),
     (try_for_range, ":cur_slot", multi_data_item_button_indices_begin, ":item_slots_end"),
       (troop_get_slot, ":item_no", "trp_multiplayer_data", ":cur_slot"),

       (create_image_button_overlay, ":cur_obj", "mesh_mp_inventory_choose", "mesh_mp_inventory_choose"),
       (position_set_x, pos1, 800),#800
       (position_set_y, pos1, 800),#800
       (overlay_set_size, ":cur_obj", pos1),
       (position_set_x, pos1, ":cur_x"),
       (position_set_y, pos1, ":cur_y"),
       (overlay_set_position, ":cur_obj", pos1),
       (create_mesh_overlay_with_item_id, reg0, ":item_no"),
       (store_add, ":item_x", ":cur_x", 50),
       (store_add, ":item_y", ":cur_y", 50),
       (position_set_x, pos1, ":item_x"),
       (position_set_y, pos1, ":item_y"),
       (overlay_set_position, reg0, pos1),

       (val_add, ":cur_x", ":x_adder"),
       (try_begin),
         (gt, ":cur_x", 500),
         (val_sub, ":cur_y", 100),
         (assign, ":cur_x", ":pos_x_begin"),
       (try_end),
     (try_end),
     ]),



  #script_coop_move_belfries_to_their_first_entry_point
  # INPUT: none
  # OUTPUT: none
  ("coop_move_belfries_to_their_first_entry_point",
   [
    (store_script_param, ":belfry_body_scene_prop", 1),
     
    (set_fixed_point_multiplier, 100),    
    (scene_prop_get_num_instances, ":num_belfries", ":belfry_body_scene_prop"),
    
    (try_for_range, ":belfry_no", 0, ":num_belfries"),
      #belfry 
      (scene_prop_get_instance, ":belfry_scene_prop_id", ":belfry_body_scene_prop", ":belfry_no"),
      (prop_instance_get_position, pos0, ":belfry_scene_prop_id"),

      (try_begin),
        (eq, ":belfry_body_scene_prop", "spr_belfry_a"),
        #belfry platform_a
        (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_platform_a", ":belfry_no"),
        #belfry platform_b
        (scene_prop_get_instance, ":belfry_platform_b_scene_prop_id", "spr_belfry_platform_b", ":belfry_no"),
      (else_try),
        #belfry platform_a
        (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_b_platform_a", ":belfry_no"),
      (try_end),
    
      #belfry wheel_1
      (store_mul, ":wheel_no", ":belfry_no", 3),
      (try_begin),
        (eq, ":belfry_body_scene_prop", "spr_belfry_b"),
        (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),    
        (store_mul, ":number_of_belfry_a_wheels", ":number_of_belfry_a", 3),
        (val_add, ":wheel_no", ":number_of_belfry_a_wheels"),
      (try_end),    
      (scene_prop_get_instance, ":belfry_wheel_1_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),
      #belfry wheel_2
      (val_add, ":wheel_no", 1),
      (scene_prop_get_instance, ":belfry_wheel_2_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),
      #belfry wheel_3
      (val_add, ":wheel_no", 1),
      (scene_prop_get_instance, ":belfry_wheel_3_scene_prop_id", "spr_belfry_wheel", ":wheel_no"),


#      (store_add, ":belfry_first_entry_point_id", 11, ":belfry_no"), #belfry entry points are 110..119 and 120..129 and 130..139
      (store_add, ":belfry_first_entry_point_id", 5, ":belfry_no"), #belfry entry points are 110..119 and 120..129 and 130..139


      (try_begin),
        (eq, ":belfry_body_scene_prop", "spr_belfry_b"),
        (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),
        (val_add, ":belfry_first_entry_point_id", ":number_of_belfry_a"),
      (try_end),    
      (val_mul, ":belfry_first_entry_point_id", 10),
      (entry_point_get_position, pos1, ":belfry_first_entry_point_id"),

      #this code block is taken from module_mission_templates.py (multiplayer_server_check_belfry_movement)
      #up down rotation of belfry's next entry point
      (init_position, pos9),
      (position_set_y, pos9, -500), #go 5.0 meters back
      (position_set_x, pos9, -300), #go 3.0 meters left
      (position_transform_position_to_parent, pos10, pos1, pos9), 
      (position_get_distance_to_terrain, ":height_to_terrain_1", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at left part of belfry

      (init_position, pos9),
      (position_set_y, pos9, -500), #go 5.0 meters back
      (position_set_x, pos9, 300), #go 3.0 meters right
      (position_transform_position_to_parent, pos10, pos1, pos9), 
      (position_get_distance_to_terrain, ":height_to_terrain_2", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at right part of belfry

      (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),
      (val_mul, ":height_to_terrain", 100), #because of fixed point multiplier

      (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 2 degrees. #ac sonra
      (init_position, pos20),    
      (position_rotate_x_floating, pos20, ":rotate_angle_of_next_entry_point"),
      (position_transform_position_to_parent, pos23, pos1, pos20),

      #right left rotation of belfry's next entry point
      (init_position, pos9),
      (position_set_x, pos9, -300), #go 3.0 meters left
      (position_transform_position_to_parent, pos10, pos1, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
      (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
      (init_position, pos9),
      (position_set_x, pos9, 300), #go 3.0 meters left
      (position_transform_position_to_parent, pos10, pos1, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
      (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
      (store_sub, ":height_to_terrain_1", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

      (init_position, pos9),
      (position_set_x, pos9, -300), #go 3.0 meters left
      (position_set_y, pos9, -500), #go 5.0 meters forward
      (position_transform_position_to_parent, pos10, pos1, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
      (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
      (init_position, pos9),
      (position_set_x, pos9, 300), #go 3.0 meters left
      (position_set_y, pos9, -500), #go 5.0 meters forward
      (position_transform_position_to_parent, pos10, pos1, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
      (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
      (store_sub, ":height_to_terrain_2", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

      (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),    
      (val_mul, ":height_to_terrain", 100), #100 is because of fixed_point_multiplier
      (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 25 degrees. 
      (val_mul, ":rotate_angle_of_next_entry_point", -1),

      (init_position, pos20),
      (position_rotate_y_floating, pos20, ":rotate_angle_of_next_entry_point"),
      (position_transform_position_to_parent, pos22, pos23, pos20),

      (copy_position, pos1, pos22),
      #end of code block

      #belfry 
      (prop_instance_stop_animating, ":belfry_scene_prop_id"),
      (prop_instance_set_position, ":belfry_scene_prop_id", pos1),
      # (prop_instance_animate_to_position, ":belfry_scene_prop_id", pos1,1), #NEW
    
      #belfry platforms
      (try_begin),
        (eq, ":belfry_body_scene_prop", "spr_belfry_a"),

        #belfry platform_a
        (prop_instance_get_position, pos6, ":belfry_platform_a_scene_prop_id"),
        (position_transform_position_to_local, pos7, pos0, pos6),
        (position_transform_position_to_parent, pos8, pos1, pos7),
        (try_begin),
          (neg|scene_prop_slot_eq, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 0),
     
          (init_position, pos20),
          (position_rotate_x, pos20, 90),
          (position_transform_position_to_parent, pos8, pos8, pos20),
        (try_end),
        (prop_instance_stop_animating, ":belfry_platform_a_scene_prop_id"),
        # (prop_instance_set_position, ":belfry_platform_a_scene_prop_id", pos8),  
        (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos8,1), #NEW
        #belfry platform_b
        (prop_instance_get_position, pos6, ":belfry_platform_b_scene_prop_id"),
        (position_transform_position_to_local, pos7, pos0, pos6),
        (position_transform_position_to_parent, pos8, pos1, pos7),
        (prop_instance_stop_animating, ":belfry_platform_b_scene_prop_id"),
        # (prop_instance_set_position, ":belfry_platform_b_scene_prop_id", pos8),
      (prop_instance_animate_to_position, ":belfry_platform_b_scene_prop_id", pos8,1), #NEW
      (else_try),
        #belfry platform_a
        (prop_instance_get_position, pos6, ":belfry_platform_a_scene_prop_id"),
        (position_transform_position_to_local, pos7, pos0, pos6),
        (position_transform_position_to_parent, pos8, pos1, pos7),
        (try_begin),
          (neg|scene_prop_slot_eq, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 0),
     
          (init_position, pos20),
          (position_rotate_x, pos20, 50),
          (position_transform_position_to_parent, pos8, pos8, pos20),
        (try_end),
        (prop_instance_stop_animating, ":belfry_platform_a_scene_prop_id"),
        # (prop_instance_set_position, ":belfry_platform_a_scene_prop_id", pos8),    
      (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos8,1), #NEW
      (try_end),
    
      #belfry wheel_1
      (store_mul, ":wheel_no", ":belfry_no", 3),
      (try_begin),
        (eq, ":belfry_body_scene_prop", "spr_belfry_b"),
        (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),    
        (store_mul, ":number_of_belfry_a_wheels", ":number_of_belfry_a", 3),
        (val_add, ":wheel_no", ":number_of_belfry_a_wheels"),
      (try_end),
      (prop_instance_get_position, pos6, ":belfry_wheel_1_scene_prop_id"),
      (position_transform_position_to_local, pos7, pos0, pos6),
      (position_transform_position_to_parent, pos8, pos1, pos7),
      (prop_instance_stop_animating, ":belfry_wheel_1_scene_prop_id"),
      # (prop_instance_set_position, ":belfry_wheel_1_scene_prop_id", pos8),
      (prop_instance_animate_to_position, ":belfry_wheel_1_scene_prop_id", pos8,1), #NEW
      #belfry wheel_2
      (prop_instance_get_position, pos6, ":belfry_wheel_2_scene_prop_id"),
      (position_transform_position_to_local, pos7, pos0, pos6),
      (position_transform_position_to_parent, pos8, pos1, pos7),
      (prop_instance_stop_animating, ":belfry_wheel_2_scene_prop_id"),
      # (prop_instance_set_position, ":belfry_wheel_2_scene_prop_id", pos8),
      (prop_instance_animate_to_position, ":belfry_wheel_2_scene_prop_id", pos8,1), #NEW
      #belfry wheel_3
      (prop_instance_get_position, pos6, ":belfry_wheel_3_scene_prop_id"),
      (position_transform_position_to_local, pos7, pos0, pos6),
      (position_transform_position_to_parent, pos8, pos1, pos7),
      (prop_instance_stop_animating, ":belfry_wheel_3_scene_prop_id"),
      # (prop_instance_set_position, ":belfry_wheel_3_scene_prop_id", pos8),
      (prop_instance_animate_to_position, ":belfry_wheel_3_scene_prop_id", pos8,1), #NEW
    (try_end),
    ]),


  # script_cf_coop_siege_assign_men_to_belfry
  # Input: none
  # Output: none (required for siege mission templates)
  ("cf_coop_siege_assign_men_to_belfry",
   [
    (store_script_param, ":pos_no", 1),

    (try_begin),
      (lt, "$belfry_positioned", 3),

      (copy_position, pos42, ":pos_no"),
      (assign, ":belfry_num_men", 0),
        (try_for_agents, ":cur_agent"),#count how many targeting belfry
          (agent_is_alive, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_get_team, ":cur_agent_team", ":cur_agent"),
          (eq, "$attacker_team", ":cur_agent_team"),
          # (agent_get_group, ":agent_group", ":cur_agent"),
          # (eq, ":agent_group", -1),#not player commanded
          (try_begin),
            (agent_get_slot, ":x_pos", ":cur_agent", slot_agent_target_x_pos),
            (neq, ":x_pos", 0),
            (agent_get_slot, ":y_pos", ":cur_agent", slot_agent_target_y_pos),
            (val_add, ":belfry_num_men", 1),
            (init_position, pos41),
            (position_move_x, pos41, ":x_pos"),
            (position_move_y, pos41, ":y_pos"),
            (init_position, pos43),
            (val_mul, ":x_pos", 3),
            (position_move_x, pos43, ":x_pos"),
            (position_move_y, pos43, -1100),
            (position_transform_position_to_parent, pos44, pos42, pos41),
            (position_transform_position_to_parent, pos45, pos42, pos43),
            (agent_get_position, pos46, ":cur_agent"),
            (get_distance_between_positions, ":target_distance", pos46, pos44),
            (get_distance_between_positions, ":waypoint_distance", pos46, pos45),
            (try_begin),
              (this_or_next|lt, ":target_distance", ":waypoint_distance"),
              (lt, ":waypoint_distance", 1600), # > 1/2 pos1 - pos4
              (agent_set_scripted_destination, ":cur_agent", pos44, 1),
            (else_try),
              (agent_set_scripted_destination, ":cur_agent", pos45, 1),
              #(display_message, "@assigned to waypoint"),
            (try_end),

          (try_end),
        (try_end),

      (try_begin),
        (lt, ":belfry_num_men", 20), 


          (try_for_agents, ":cur_agent"), #add more troops if low
            (lt, ":belfry_num_men", 20), #stop adding when max number to push
            (agent_is_alive, ":cur_agent"),
            (agent_get_team, ":cur_agent_team", ":cur_agent"),
            (eq, "$attacker_team", ":cur_agent_team"),
            (agent_get_slot, ":x_pos", ":cur_agent", slot_agent_target_x_pos),
            (eq, ":x_pos", 0),
            (assign, ":y_pos", 0),
            (store_random_in_range, ":side", 0, 2),
            (try_begin),
              (eq, ":side", 1),
              (assign, ":x_pos", -400),
            (else_try),
              (assign, ":x_pos", 400),
            (try_end),
            (val_add, ":belfry_num_men", 1),
            (agent_set_slot, ":cur_agent", slot_agent_target_x_pos, ":x_pos"),
            (agent_set_slot, ":cur_agent", slot_agent_target_y_pos, ":y_pos"),
          (try_end),
      (try_end),
    # (else_try), #we already clear scripted in mission template
      # (try_for_agents, ":cur_agent"),
        # (agent_get_team, ":cur_agent_team", ":cur_agent"),
        # (eq, "$attacker_team", ":cur_agent_team"),
        # (agent_clear_scripted_mode, ":cur_agent"),
      # (try_end),
    (try_end),

  ]),

######## 	
  # script_coop_spawn_formation
  # Input: arg1 = agent_no
  # Output: none
  ("coop_spawn_formation",
    [
      (store_script_param, ":agent_no", 1),
      (try_begin),

        (try_begin),
          (agent_is_human, ":agent_no"), #horse spawns after rider
          (assign, ":human_agent", ":agent_no"), 
        (else_try),
          (agent_get_rider, ":human_agent", ":agent_no"),
        (try_end),

        (agent_get_team, ":agent_team", ":human_agent"),
        (agent_get_division, ":agent_class", ":human_agent"), #agent_get_class only works after horsemen have horses

        (try_begin),
          (neg|agent_is_human, ":agent_no"),
          (assign, ":pos", "$coop_form_line_last_pos"),
        (else_try),
          (eq, ":agent_team", 0),
          (try_begin),
            (eq, ":agent_class", grc_archers),   
            (assign, ":pos", pos25),
            (try_begin),
              (eq, "$coop_form_line_grp_1", 1),  
              (assign, "$coop_form_line_grp_1", 0),    
              (position_move_y, ":pos", -200),
            (else_try),
              (assign, "$coop_form_line_grp_1", 1),   
              (position_move_y, ":pos", 200),
              (position_move_x, ":pos", 100),
            (try_end),
          (else_try),
            (eq, ":agent_class", grc_infantry), 
            (assign, ":pos", pos26), 
            (try_begin),
              (eq, "$coop_form_line_grp_2", 1),  
              (assign, "$coop_form_line_grp_2", 0),    
              (position_move_y, ":pos", -200),
            (else_try),
              (assign, "$coop_form_line_grp_2", 1),   
              (position_move_y, ":pos", 200),
              (position_move_x, ":pos", 100),
            (try_end),
          (else_try),
            (eq, ":agent_class", grc_cavalry),   
            (assign, ":pos", pos27),
            (try_begin),
              (eq, "$coop_form_line_grp_3", 1),  
              (assign, "$coop_form_line_grp_3", 0),    
              (position_move_y, ":pos", -300),
            (else_try),
              (assign, "$coop_form_line_grp_3", 1),   
              (position_move_y, ":pos", 300),
              (position_move_x, ":pos", 100),
            (try_end),
          (try_end),

        (else_try),
          (eq, ":agent_team", 1),
          (try_begin),
            (eq, ":agent_class", grc_archers),   
            (assign, ":pos", pos30),
            (try_begin),
              (eq, "$coop_form_line_grp_4", 1),  
              (assign, "$coop_form_line_grp_4", 0),    
              (position_move_y, ":pos", -200),
            (else_try),
              (assign, "$coop_form_line_grp_4", 1),   
              (position_move_y, ":pos", 200),
              (position_move_x, ":pos", 100),
            (try_end),
          (else_try),
            (eq, ":agent_class", grc_infantry), 
            (assign, ":pos", pos31), 
            (try_begin),
              (eq, "$coop_form_line_grp_5", 1),  
              (assign, "$coop_form_line_grp_5", 0),    
              (position_move_y, ":pos", -200),
            (else_try),
              (assign, "$coop_form_line_grp_5", 1),   
              (position_move_y, ":pos", 200),
              (position_move_x, ":pos", 100),
            (try_end),
          (else_try),
            (eq, ":agent_class", grc_cavalry),  
            (assign, ":pos", pos32),
            (try_begin),
              (eq, "$coop_form_line_grp_6", 1),  
              (assign, "$coop_form_line_grp_6", 0),    
              (position_move_y, ":pos", -300),
            (else_try),
              (assign, "$coop_form_line_grp_6", 1),   
              (position_move_y, ":pos", 300),
              (position_move_x, ":pos", 100),
            (try_end),
          (try_end),
        (try_end),

        # (try_begin),
          # (agent_is_human, ":agent_no"),
          # (position_move_x, ":pos", 100),
        # (try_end),
        (assign, "$coop_form_line_last_pos", ":pos"), #store last pos for horses
        (agent_set_position, ":agent_no", ":pos"),
        (agent_set_scripted_destination, ":agent_no", ":pos", 1),

      (try_end),

      ]),

######## 	
  # script_coop_form_line
  # Input: arg1 = agent_no
  # Output: none
  ("coop_form_line",
    [
      (store_script_param, ":pos_no", 1),
      (store_script_param, ":team", 2),
      (store_script_param, ":class", 3),
      (store_script_param, ":dist_to_next_row", 4),
      (store_script_param, ":dist_to_next_troop", 5),
      (store_script_param, ":num_rows", 6),
      (store_script_param, ":move_to_pos", 7),#set agent at position like spawning

      (store_sub, ":dist_to_first_row", 1, ":num_rows"),
      (val_mul, ":dist_to_first_row", ":dist_to_next_row"),

      (init_position, pos35),
      (copy_position, pos35, ":pos_no"),
      (assign, ":row", 1),
      (try_for_agents, ":agent_no"),
        (agent_is_alive, ":agent_no"),
        (agent_is_human, ":agent_no"),
        (agent_get_team, ":agent_team", ":agent_no"),
        (eq, ":agent_team", ":team"),
        (agent_get_slot, ":x_pos", ":agent_no", slot_agent_target_x_pos), #if agent is not pushing belfry
        (eq, ":x_pos", 0),
        # (agent_get_group, ":agent_group", ":agent_no"),
        # (eq, ":agent_group", -1),
        (agent_get_class, ":agent_class", ":agent_no"),
        (this_or_next|eq, ":class", grc_everyone),   
        (eq, ":agent_class", ":class"),   
        (try_begin),
          (eq, ":move_to_pos", 1), #set agent at position like spawning
          (agent_get_horse, ":agent_horse", ":agent_no"),
          (agent_set_position, ":agent_horse", pos35),
          (agent_set_position, ":agent_no", pos35),
        (try_end),
        (agent_set_scripted_destination, ":agent_no", pos35, 1),
        (try_begin),
          (eq, ":row", ":num_rows"),
          (assign, ":row", 1),
          (position_move_x, pos35, ":dist_to_next_troop"),
          (position_move_y, pos35, ":dist_to_first_row"),
        (else_try),
          (position_move_y, pos35, ":dist_to_next_row"),
          (val_add, ":row", 1),
        (try_end),
      (try_end),

      ]),

######## 	all in party doesnot include castle garrison, by type includes allies
  # script_coop_change_leader_of_bot
  # Input: arg1 = agent_no
  # Output: none
  ("coop_change_leader_of_bot",
    [
      (store_script_param, ":agent_no", 1),

      (agent_get_team, ":team_no", ":agent_no"),
      (agent_get_troop_id,":agent_troop", ":agent_no"),
      (troop_get_slot, ":troop_class", ":agent_troop", slot_troop_current_rumor), #use to store class in MP (so we dont affect ai classes too)
      # (troop_get_class, ":troop_class", ":agent_troop"),
      (agent_get_class, ":agent_class", ":agent_no"),
      (agent_get_slot, ":agent_party_no",":agent_no", slot_agent_coop_spawn_party),# coop party
      (agent_get_group, ":agent_group", ":agent_no"),

      (assign, ":leader_player", -1),
      (get_max_players, ":num_players"),
      (assign, ":end_cond", ":num_players"),
      (try_for_range, ":cur_player", 0, ":end_cond"), #try players till we find one, server gets first pick
        (player_is_active, ":cur_player"),
        (player_get_team_no, ":player_team", ":cur_player"),
        (eq, ":team_no", ":player_team"),
        (player_get_agent_id, ":player_agent", ":cur_player"),
        (ge, ":player_agent", 0),
        (agent_is_alive, ":player_agent"),
        (agent_get_slot, ":player_party_no",":player_agent", slot_agent_coop_spawn_party),# coop party

        (try_begin),#check if players party is garrison commander party
          (eq, ":agent_party_no", "$coop_garrison_party"), #if bot is part of garrison
          (eq, ":player_party_no", "$coop_garrison_commander_party"), #and player is commander of garrison
          (assign, ":player_party_no", ":agent_party_no"), #then player is also part of garrison party
        (try_end),
        (eq, ":agent_party_no", ":player_party_no"), #remove this if hero should command troops in other parties
        (try_begin),
          (eq, ":agent_class", grc_infantry),
          (player_get_slot, ":type_2_wanted", ":cur_player", slot_player_bot_type_2_wanted),
          (eq, ":type_2_wanted", 1), #player wants type 2
          (assign, ":leader_player", ":cur_player"),
          (assign, ":end_cond", 0),
        (else_try),
          (eq, ":agent_class", grc_archers),
          (player_get_slot, ":type_3_wanted", ":cur_player", slot_player_bot_type_3_wanted),
          (eq, ":type_3_wanted", 1), #player wants type 3
          (assign, ":leader_player", ":cur_player"),
          (assign, ":end_cond", 0), 
        (else_try),
          (eq, ":agent_class", grc_cavalry),
          (player_get_slot, ":type_4_wanted", ":cur_player", slot_player_bot_type_4_wanted),
          (eq, ":type_4_wanted", 1), #player wants type 4
          (assign, ":leader_player", ":cur_player"),
          (assign, ":end_cond", 0),
        (else_try),

          (eq, ":agent_party_no", "$coop_main_party_spawn"), #if agent is from main party
          (try_begin),
            (eq, ":troop_class", 0),
            (player_get_slot, ":class_0_wanted", ":cur_player", slot_player_coop_class_0_wanted),
            (eq, ":class_0_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 1),
            (player_get_slot, ":class_1_wanted", ":cur_player", slot_player_coop_class_1_wanted),
            (eq, ":class_1_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 2),
            (player_get_slot, ":class_2_wanted", ":cur_player", slot_player_coop_class_2_wanted),
            (eq, ":class_2_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 3),
            (player_get_slot, ":class_3_wanted", ":cur_player", slot_player_coop_class_3_wanted),
            (eq, ":class_3_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 4),
            (player_get_slot, ":class_4_wanted", ":cur_player", slot_player_coop_class_4_wanted),
            (eq, ":class_4_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 5),
            (player_get_slot, ":class_5_wanted", ":cur_player", slot_player_coop_class_5_wanted),
            (eq, ":class_5_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 6),
            (player_get_slot, ":class_6_wanted", ":cur_player", slot_player_coop_class_6_wanted),
            (eq, ":class_6_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 7),
            (player_get_slot, ":class_7_wanted", ":cur_player", slot_player_coop_class_7_wanted),
            (eq, ":class_7_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (else_try),
            (eq, ":troop_class", 8),
            (player_get_slot, ":class_8_wanted", ":cur_player", slot_player_coop_class_8_wanted),
            (eq, ":class_8_wanted", 1),
            (assign, ":leader_player", ":cur_player"),
            (assign, ":end_cond", 0), 
          (try_end),
        (try_end),
      (try_end),

  # if nobody wants agent check for someone who wants all in party
      (try_begin),
        (eq, ":leader_player", -1),
        (get_max_players, ":num_players"),
        (assign, ":end_cond", ":num_players"),
        (try_for_range, ":cur_player", 0, ":end_cond"), #try players till we find one, server gets first pick
          (player_is_active, ":cur_player"),
          (player_get_team_no, ":player_team", ":cur_player"),
          (eq, ":team_no", ":player_team"),
          (player_get_agent_id, ":player_agent", ":cur_player"),
          (ge, ":player_agent", 0),
          (agent_is_alive, ":player_agent"),
          (agent_get_slot, ":player_party_no",":player_agent", slot_agent_coop_spawn_party),# coop party
          (try_begin),#check if players party is garrison commander party
            (eq, ":agent_party_no", "$coop_garrison_party"), #if bot is part of garrison
            (eq, ":player_party_no", "$coop_garrison_commander_party"), #and player is commander of garrison
            (assign, ":player_party_no", ":agent_party_no"), #then player is also part of garrison party
          (try_end),
          (eq, ":player_party_no",":agent_party_no"), #remove this if hero should command troops in other parties
          (this_or_next|eq, ":agent_group", -1),#not already commanded
          (eq, ":agent_group", ":cur_player"),#commanded by me
          (player_get_slot, ":type_1_wanted", ":cur_player", slot_player_bot_type_1_wanted),
          (eq, ":type_1_wanted", 1), #player wants type 1
          (assign, ":leader_player", ":cur_player"),
          (assign, ":end_cond", 0),
        (try_end),
      (try_end),
      (agent_set_group, ":agent_no", ":leader_player"),

    # (assign, reg13, ":agent_no"), 
    # (str_store_troop_name, s40, ":agent_troop"),
    # (assign, reg10, ":leader_player"), 
    # (assign, reg11, ":team_no"), 
    # (display_message, "@{reg11} leader {reg10} agent{reg13}   {s40}"),


      ]),


#
  # script_coop_find_bot_troop_for_spawn
  # Input: arg1 = team_no
  # Output: reg0 = troop_id, reg1 = group_id
  ("coop_find_bot_troop_for_spawn",
    [
      (store_script_param, ":team_no", 1),


      (assign, ":selected_troop", 0), #if no troop is found (error) spawn trp_player
      (try_begin),	  
        (eq, ":team_no", 0), #enemy team

        (assign, ":end", 40), 
        (try_for_range, ":unused", 0, ":end"),
          (party_stack_get_troop_id, ":selected_troop", "$coop_cur_temp_party_enemy", 0), #get one troop from each party per cycle

          (try_begin),
            (gt, ":selected_troop", 0),
            (assign, ":party", "$coop_cur_temp_party_enemy"),
            (party_remove_members, ":party", ":selected_troop", 1),
            (store_sub, ":slot_pos", ":party", coop_temp_party_enemy_begin),
            (troop_get_slot, "$coop_agent_banner", "trp_temp_array_a", ":slot_pos"),
            (assign, "$coop_agent_party", ":party"),
            (assign, ":end", 0),
          (else_try),
            # trp_player at stack 0 — remove so it doesn't block real troops
            (eq, ":selected_troop", 0),
            (party_remove_members, "$coop_cur_temp_party_enemy", "trp_player", 1),
          (try_end),
          (try_begin),
            (store_add, ":last_party", coop_temp_party_enemy_begin, "$coop_no_enemy_parties"), 
            (val_sub, ":last_party", 1), 
            (eq, "$coop_cur_temp_party_enemy", ":last_party"),
            (assign, "$coop_cur_temp_party_enemy", coop_temp_party_enemy_begin),
          (else_try),
            (val_add, "$coop_cur_temp_party_enemy", 1),
          (try_end),
        (try_end),


      (else_try),
	  	  (eq, ":team_no", 1), #player team + allies

        (assign, ":end", 40), 
        (try_for_range, ":unused", 0, ":end"),
          (party_stack_get_troop_id, ":selected_troop", "$coop_cur_temp_party_ally", 0), #get one troop from each party per cycle
          (try_begin),
            (gt, ":selected_troop", 0),
            (assign, ":party", "$coop_cur_temp_party_ally"),
            (party_remove_members, ":party", ":selected_troop", 1),
            (store_sub, ":slot_pos", ":party", coop_temp_party_ally_begin),
            (troop_get_slot, "$coop_agent_banner", "trp_temp_array_b", ":slot_pos"),
            (assign, "$coop_agent_party", ":party"),
            (assign, ":end", 0),
          (else_try),
            # trp_player at stack 0 — remove so it doesn't block real troops
            (eq, ":selected_troop", 0),
            (party_remove_members, "$coop_cur_temp_party_ally", "trp_player", 1),
          (try_end),
          (try_begin),
            (store_add, ":last_party", coop_temp_party_ally_begin, "$coop_no_ally_parties"), #= one more than total
            (val_sub, ":last_party", 1), 
            (eq, "$coop_cur_temp_party_ally", ":last_party"),
            (assign, "$coop_cur_temp_party_ally", coop_temp_party_ally_begin),
          (else_try),
            (val_add, "$coop_cur_temp_party_ally", 1),
          (try_end),
        (try_end),

      (try_end), 


      #send banner for troop
      (get_max_players, ":num_players"),
      (try_for_range, ":player_no", 1, ":num_players"), #0 is server so starting from 1
        (player_is_active, ":player_no"),
        (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_troop_banner, "$coop_agent_banner"),
      (try_end),
      (call_script, "script_coop_check_item_bug", ":selected_troop"), #ITEM BUG WORKAROUND

      #  debug
      # (assign, reg4, "$coop_agent_banner"), 
      # (str_store_troop_name, s41, ":selected_troop"),
      # (assign, reg6, ":party"), 
      # (display_message, "@spawn {s41} from party {reg6} banner {reg4}"),

      (assign, reg0, ":selected_troop"),
    ]),	


  
    # 
   # script_coop_server_on_agent_killed_or_wounded_common
  # Input: arg1 = dead_agent_no
  ("coop_server_on_agent_killed_or_wounded_common",
   [
    (store_script_param, ":dead_agent_no", 1),
    (store_script_param, ":killer_agent_no", 2),

    (try_begin),
      (ge, ":dead_agent_no", 0),
      (ge, ":killer_agent_no", 0),
      (agent_is_human, ":dead_agent_no"),
      #(agent_is_human, ":killer_agent_no"), #comment if horse can kill human?
      (agent_get_troop_id, ":killer_troop_id", ":killer_agent_no"),
      (agent_get_troop_id, ":dead_troop_id", ":dead_agent_no"),
      (agent_get_team, ":dead_agent_team", ":dead_agent_no"),

      #xp function = (x*x/10 + x*2 + 10)* 2
      (store_character_level,":dead_troop_level",":dead_troop_id"),
      (store_mul, ":xp_gain", ":dead_troop_level", ":dead_troop_level"), 
      (val_div, ":xp_gain", 10), 
      (val_add, ":xp_gain", ":dead_troop_level"),
      (val_add, ":xp_gain", ":dead_troop_level"),
      (val_add, ":xp_gain", 10),
      (val_mul, ":xp_gain", 2),

      #xp message
      (try_begin),
        (eq, ":killer_troop_id", "$coop_my_troop_no"),
        (troop_is_hero, ":killer_troop_id"),
        (eq, "$coop_toggle_messages", 0),
        (assign, reg1, ":xp_gain"), 
        (display_message, "@You got {reg1} experience.", 0x00a4d9a2), #Added colored_message to xp gain in Co-Op.
      (try_end), 

      (try_begin),
        (troop_is_hero, ":dead_troop_id"),
        (try_begin),
          (eq, ":dead_agent_team", 0),
          (party_remove_members, coop_temp_party_enemy_heroes, ":dead_troop_id", 1),	
        (else_try),
          (eq, ":dead_agent_team", 1),
          (party_remove_members, coop_temp_party_ally_heroes, ":dead_troop_id", 1),
        (try_end),
      (try_end),

#only server continue
      (multiplayer_is_server),
      (agent_get_slot, ":killer_agent_party",":killer_agent_no", slot_agent_coop_spawn_party), #slot_agent_coop_spawn_party = SP party
      (agent_get_slot, ":dead_agent_party",":dead_agent_no", slot_agent_coop_spawn_party), #slot_agent_coop_spawn_party = SP party

      (try_begin),
        (eq, ":dead_agent_team", 0),
        (store_sub, ":casualties_party", ":dead_agent_party", coop_temp_party_enemy_begin),
        (val_add, ":casualties_party", coop_temp_casualties_enemy_begin),
      (else_try),
        (eq, ":dead_agent_team", 1),
        (store_sub, ":casualties_party", ":dead_agent_party", coop_temp_party_ally_begin),
        (val_add, ":casualties_party", coop_temp_casualties_ally_begin),
      (try_end),

      (party_add_members, ":casualties_party", ":dead_troop_id", 1),
      (try_begin),
        (this_or_next|troop_is_hero,":dead_troop_id"),
        (agent_is_wounded, ":dead_agent_no"),
        (party_wound_members, ":casualties_party", ":dead_troop_id", 1),
      (try_end),

      (try_begin), #save hit points for dead heroes (15% of pre battle health)
        (troop_is_hero, ":dead_troop_id"),   
        (store_troop_health, ":old_health", ":dead_troop_id"),
        (val_div, ":old_health", 6),
        (troop_set_health, ":dead_troop_id", ":old_health"),
      (try_end), 

#moved from multiplayer_server_on_agent_killed_or_wounded_common for this game type only
      (agent_get_player_id, ":dead_player_no", ":dead_agent_no"),
      (try_begin),
        (ge, ":dead_player_no", 0),
        (player_is_active, ":dead_player_no"),
        (neg|agent_is_non_player, ":dead_agent_no"), #dead agent was player    
        (try_for_agents, ":cur_agent"),
          (agent_is_non_player, ":cur_agent"), #agent is bot
          (agent_is_human, ":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (agent_get_group, ":agent_group", ":cur_agent"),
          (try_begin),
            (eq, ":dead_player_no", ":agent_group"),
            (agent_set_group, ":cur_agent", -1),                 
          (try_end),
        (try_end),
      (try_end),
    (try_end),  


#CLIENT CRASH BUG WORKAROUND BEGIN ################################################################
    (try_begin), #do this so client doesnt crash when rejoining, remove weapons from agent when his player quits
      (ge, ":dead_agent_no", 0),
      (lt, ":killer_agent_no", 0),
      (agent_is_human, ":dead_agent_no"),
      (position_move_y, pos0, 0),
      (position_move_x, pos0, 0),
      (agent_set_position, ":dead_agent_no", pos0),

      (try_for_range, ":slot", 0, 8),
        (agent_get_item_slot, ":cur_item", ":dead_agent_no", ":slot"), 
        (ge, ":cur_item", 0),
        (agent_unequip_item,":dead_agent_no",":cur_item"),
      (try_end),
      (remove_agent, ":dead_agent_no"),
      (agent_fade_out, ":dead_agent_no"),
    (try_end), 
#CLIENT CRASH BUG WORKAROUND END ################################################################
   ]),	

  # 
  # script_coop_sort_party
  # copies heroes first then troops to p_temp_party, and copies back to original party
  # Input: arg1 = dead_agent_no
  ("coop_sort_party",
   [
    (store_script_param, ":var_6", 1),
 

        (party_clear, "p_temp_party"), 
        (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
        (try_for_range, ":stack", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable",":var_6",":stack"),	
	        (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", ":var_6", ":stack"),
          (party_add_members, "p_temp_party", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
        (try_end),

        (try_for_range, ":stack", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", ":stack"),	
	        (neg|troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", ":var_6", ":stack"),
          (party_add_members, "p_temp_party", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
        (try_end),


		    (party_clear, ":var_6"), 
        (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", "p_temp_party"),
        (try_for_range, ":stack", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", "p_temp_party", ":stack"),	
          (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", "p_temp_party", ":stack"),
          (party_add_members, ":var_6", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
        (try_end),

   ]),	

   #####PROBABLY BUGGY
#    # 
# # script_coop_sort_party
# # copies heroes first then troops to p_temp_party, and copies back to original party
# # Input: arg1 = dead_agent_no
# ("coop_sort_party",
#  [
#   (store_script_param, ":var_6", 1),
#
#
#       (party_clear, "p_temp_party"), 
#       (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
#       (try_for_range, ":localvariable", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
#         (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable",":var_6",":localvariable"),	
#	        (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
#         (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", ":var_6", ":localvariable"),
#         (party_add_members, "p_temp_party", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
#       (try_end),
#
#       (try_for_range, ":localvariable", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
#         (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", ":localvariable"),	
#	        (neg|troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
#         (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", ":var_6", ":localvariable"),
#         (party_add_members, "p_temp_party", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
#       (try_end),
#
#
#		    (party_clear, ":var_6"), 
#       (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", "p_temp_party"),
#       (try_for_range, ":localvariable", 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
#         (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", "p_temp_party", ":localvariable"),	
#         (party_stack_get_size, ":party_prisoner_stack_size_var_6_var_9", "p_temp_party", ":localvariable"),
#         (party_add_members, ":var_6", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"),
#       (try_end),
#
#  ]),	
   


###### DATA SCRIPTS ##########################################################################################################

   # 
  # used to copy parties from SP to registers and temp casualty parties from MP to registers 
  # script_coop_copy_parties_to_file_sp
  # Input: arg1 = party_no
  ("coop_copy_parties_to_file_sp",
   [
    (try_begin), 
      (neg|is_vanilla_warband),
        (dict_create, "$coop_dict"),
        (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
        (dict_save, "$coop_dict", s41), #clear battle file

        (dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_setup_sp),

        (call_script, "script_coop_copy_settings_to_file"),	#copy game settings here

#SP ONLY MISC DATA

      #store scene
      (assign, ":scene_to_use", 0),
      (assign, ":scene_castle", 0),
      (assign, ":scene_street", 0),
      (assign, ":scene_party", 0),
      (assign, ":encountered_party", "$g_encountered_party"),
      (try_begin),
        (this_or_next|eq, "$coop_battle_type", coop_battle_type_siege_player_defend),
        (eq, "$coop_battle_type", coop_battle_type_siege_player_attack),
        (try_begin),
          (party_slot_eq, ":encountered_party", slot_party_type, spt_town),
          (party_get_slot, ":scene_to_use", ":encountered_party", slot_town_walls),
          (party_get_slot, ":scene_castle", ":encountered_party", slot_town_castle),
          (party_get_slot, ":scene_street", ":encountered_party", slot_town_center),
          (assign, ":scene_party", ":encountered_party"),
        (else_try),
          (party_slot_eq, ":encountered_party", slot_party_type, spt_castle),
          (party_get_slot, ":scene_to_use", ":encountered_party", slot_castle_exterior),
          (party_get_slot, ":scene_castle", ":encountered_party", slot_town_castle),
          (assign, ":scene_party", ":encountered_party"),
        (try_end),

      (else_try),
        (this_or_next|eq, "$coop_battle_type", coop_battle_type_village_player_attack),
        (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
        (try_begin),
          (party_slot_eq, ":encountered_party", slot_party_type, spt_village),
          (party_get_slot, ":scene_to_use", ":encountered_party", slot_castle_exterior),
          (assign, ":scene_party", ":encountered_party"),
        (else_try),
          (assign, ":encountered_party", "$g_encounter_is_in_village"),
          (party_get_slot, ":scene_to_use", ":encountered_party", slot_castle_exterior),
          (assign, ":scene_party", ":encountered_party"),
        (try_end),

      (else_try),
        (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
        (party_slot_eq, ":encountered_party", slot_party_type, spt_bandit_lair),
        (party_stack_get_troop_id, ":bandit_type", "$g_encountered_party", 0),
        (try_begin),
          (eq, ":bandit_type", "trp_desert_bandit"),
          (assign, ":scene_to_use", "scn_lair_desert_bandits"),
        (else_try),
          (eq, ":bandit_type", "trp_mountain_bandit"),
          (assign, ":scene_to_use", "scn_lair_mountain_bandits"),
        (else_try),
          (eq, ":bandit_type", "trp_forest_bandit"),
          (assign, ":scene_to_use", "scn_lair_forest_bandits"),
        (else_try),
          (eq, ":bandit_type", "trp_taiga_bandit"),
          (assign, ":scene_to_use", "scn_lair_taiga_bandits"),
        (else_try),
          (eq, ":bandit_type", "trp_steppe_bandit"),
          (assign, ":scene_to_use", "scn_lair_steppe_bandits"),
        (else_try),
          (eq, ":bandit_type", "trp_sea_raider"),
          (assign, ":scene_to_use", "scn_lair_sea_raiders"),
        (try_end),

      (else_try),
	  #ASSIGN VARIABLES
	  			
				
		# if field battle or we did not find one
		(party_get_current_terrain, ":terrain_type", "p_main_party"),
		#(assign, ":scene_to_use", "scn_coop_random_med_plain"), # Safeguard for none-existant scene (Sea, etc)
	    #(store_random_in_range, ":offset", 0, 12), # Actual index of the random scene (returns 0-11) (0 Counts as well) so count from 0 and up, which means 4 is 5 if you are counting from 1.
		#(assign, ":scene_to_use_large", "scn_1257_combat_swamp_0"), # Safeguard for sea battles etc does not require terrain type.
		#(val_add, ":scene_to_use_large", ":offset"), 
		###BEGIN SEA SCENES
		(store_random_in_range, ":offset", 0, 7), # Actual index of the random scene (returns 0-11) (0 Counts as well) so count from 0 and up, which means 4 is 5 if you are counting from 1.
		(assign, ":scene_to_use_large", "scn_scene_sea"), # Safeguard for sea battles etc does not require terrain type.
		(val_add, ":scene_to_use_large", ":offset"), 
		###END SEA SCENES
		
		    (store_random_in_range, ":offset", 0, 7), # Changed from 0, 3 to 0,7 to add Nile.
		    (try_begin),
			(eq, ":terrain_type", rt_desert),
		    #(assign, ":scene_to_use", "scn_1257_combat_rocky_desert_0"),
			(assign, ":scene_to_use_large", "scn_1257_combat_rocky_desert_0"),
			(val_add, ":scene_to_use_large", ":offset"), 
			(else_try),
			
			#Add scenes using 
			#(store_random_in_range, ":offset", 0, 3), # Actual index of the random scene (returns 0-9) (0 Counts as well)
			#Then finally
			#(val_add, ":scene_to_use_large", ":offset"), 
			#After (assign, ":scene_to_use_large", "scn_1257_combat_rocky_desert_0 "),
			#Add multiple scenes by  editing  
			# 		(assign, ":scene_to_use_large)", "scn_coop_random_lrg_plain"), # Safeguard
		    #           (store_random_in_range, ":offsetsnow", 0, 10), # Actual index of the random scene (returns 0-9) (0 Counts as well)
			#       (val_add, ":scene_to_use_large", ":offset"),
			# If you got 9 scenes, then use 0, 10 if you got 6 scenes then use 0, 7 always one number is spare.

           (store_random_in_range, ":offset", 0, 16), # Actual index of the random scene (returns 0-9) (0 Counts as well)
			(eq, ":terrain_type", rt_steppe),
			#(assign, ":scene_to_use", "scn_coop_random_lrg_steppe"),
			(assign, ":scene_to_use_large", "scn_random_scene_steppe"),
					(val_add, ":scene_to_use_large", ":offset"), 
			# ... "And on and on and on..." -- Blind Guardian, "Precious Jerusalem"
			# In other words, repeat these for all terrain types you've got covered.
		# READY SET GO
		(else_try),
		(store_random_in_range, ":offset", 0, 18), # Actual index of the random scene (returns 0-9) (0 Counts as well)
			(eq, ":terrain_type", rt_plain),
			#(assign, ":scene_to_use", "scn_1257_combat_euro_0"),
			(assign, ":scene_to_use_large", "scn_random_scene_plain"),
			(val_add, ":scene_to_use_large", ":offset"), 
		(else_try),
				(store_random_in_range, ":offset", 0, 12), # Actual index of the random scene (returns 0-9) (0 Counts as well)
			(eq, ":terrain_type", rt_snow),
			#(assign, ":scene_to_use", "scn_coop_random_med_snow"),
			(assign, ":scene_to_use_large", "scn_random_scene_snow"),
			(val_add, ":scene_to_use_large", ":offset"), 
        (else_try),
						(store_random_in_range, ":offset", 0, 16), # Actual index of the random scene (returns 0-9) (0 Counts as well)
          (eq, ":terrain_type", rt_steppe_forest),
         # (assign, ":scene_to_use", "scn_coop_random_med_steppe_forest"),
          (assign, ":scene_to_use_large", "scn_random_scene_steppe"),
		  (val_add, ":scene_to_use_large", ":offset"), 
        (else_try),
						(store_random_in_range, ":offset", 0, 13), # Actual index of the random scene (returns 0-9) (0 Counts as well)
          (eq, ":terrain_type", rt_forest),
        #  (assign, ":scene_to_use", "scn_coop_random_med_plain_forest"),
          (assign, ":scene_to_use_large", "scn_random_scene_plain_forest"),
		  (val_add, ":scene_to_use_large", ":offset"), 
        (else_try),
						(store_random_in_range, ":offset", 0, 12), # Actual index of the random scene (returns 0-9) (0 Counts as well)
          (eq, ":terrain_type", rt_snow_forest),
        #  (assign, ":scene_to_use", "scn_coop_random_med_snow_forest"),
          (assign, ":scene_to_use_large", "scn_random_scene_snow"),
		  (val_add, ":scene_to_use_large", ":offset"), 
        (else_try),
						(store_random_in_range, ":offset", 0, 7), # Edited from 0, 3 to add Nile.
          (eq, ":terrain_type", rt_desert_forest),
        #  (assign, ":scene_to_use", "scn_coop_random_med_desert_forest"),
          (assign, ":scene_to_use_large", "scn_1257_combat_rocky_desert_0"),
		  (val_add, ":scene_to_use_large", ":offset"), 
		  #V1.000 Added
        (else_try),
          (eq, ":terrain_type", rt_water),
          (assign, ":scene_to_use", "scn_water"),
		            (assign, ":scene_to_use_large", "scn_water"),
		  		  	(else_try),
				
          (eq, ":terrain_type", rt_bridge),
          (assign, ":scene_to_use", "scn_scene_sea"),
		  (assign, ":scene_to_use_large", "scn_scene_sea"),
		  #	(else_try),
		 #(eq, ":current_terrain_main_party", 7), #try to add sea battles
		#	(assign, ":value", "scn_scene_sea"),
		#End V1.000
		  		(try_end),



        (try_begin),
          (store_add, ":total_fit_for_battle", "$g_enemy_fit_for_battle", "$g_friend_fit_for_battle"), #get number of troops for large or medium scene size
          #(gt, ":total_fit_for_battle", 80),
		  (gt, ":total_fit_for_battle", 2),
          (assign, ":scene_to_use", ":scene_to_use_large"), #switch to larger scene 
        (try_end),
      (try_end),

      (dict_set_int, "$coop_dict", "@map_type", "$coop_battle_type"),
      (dict_set_int, "$coop_dict", "@map_scn", ":scene_to_use"),
      (dict_set_int, "$coop_dict", "@map_castle", ":scene_castle"),
      (dict_set_int, "$coop_dict", "@map_street", ":scene_street"),
      (dict_set_int, "$coop_dict", "@map_party_id", ":scene_party"),


      #find which party is castle garrison and which party is commander of garrison
      (dict_set_int, "$coop_dict", "@p_castle_lord", -1), #store null (0 could be a valid number for this variable)
      (assign, ":garrison_lord_party", -1),
      (try_begin), 
        (this_or_next|party_slot_eq, ":encountered_party", slot_party_type, spt_village),
        (this_or_next|party_slot_eq, ":encountered_party", slot_party_type, spt_town),
        (party_slot_eq, ":encountered_party", slot_party_type, spt_castle),
        (party_get_slot, ":cur_leader", ":encountered_party", slot_town_lord),
        (ge, ":cur_leader", 0),
        (troop_get_slot, ":troop_leaded_party", ":cur_leader", slot_troop_leaded_party),
        (ge, ":troop_leaded_party", 0),
        (assign, ":garrison_lord_party", ":troop_leaded_party"),
      (try_end),


      #decide weather
      (party_get_current_terrain, ":terrain_type", "p_main_party"),
      (try_begin),
        (this_or_next|eq, ":terrain_type", rt_plain),
        (this_or_next|eq, ":terrain_type", rt_steppe_forest),
        (this_or_next|eq, ":terrain_type", rt_forest),
        (this_or_next|eq, ":terrain_type", rt_water),
        (this_or_next|eq, ":terrain_type", rt_bridge),
        (eq, ":terrain_type", rt_steppe),

        (assign, ":rain", 1),
      (else_try),
        (this_or_next|eq, ":terrain_type", rt_snow_forest),
        (eq, ":terrain_type", rt_snow),

        (assign, ":rain", 2),
      (else_try),        
        (this_or_next|eq, ":terrain_type", rt_desert_forest),
        (eq, ":terrain_type", rt_desert),

        (assign, ":rain", 0),
      (try_end),

      (store_time_of_day, ":time"),
	    (get_global_cloud_amount, ":cloud"),
	    (get_global_haze_amount, ":haze"),
      (dict_set_int, "$coop_dict", "@map_time", ":time"),
      (dict_set_int, "$coop_dict", "@map_cloud", ":cloud"),
      (dict_set_int, "$coop_dict", "@map_haze", ":haze"),
      (dict_set_int, "$coop_dict", "@map_rain", ":rain"),



      (call_script, "script_calculate_battle_advantage"),
           # (val_mul, reg0, 2),
           # (val_div, reg0, 3), #scale down the advantage a bit in sieges.
      (dict_set_int, "$coop_dict", "@battle_adv", reg0),



      #store faction of parties
      (store_faction_of_party, ":team_faction", "$coop_encountered_party"),
      (dict_set_int, "$coop_dict", "@tm0_fac", ":team_faction"),


      (try_begin),
        (gt, "$g_ally_party", 0),
        (store_faction_of_party, ":team_faction", "$g_ally_party"),
      (else_try),
        (gt, "$players_kingdom", 0),
        (assign, ":team_faction", "$players_kingdom"),
      (else_try),
        (assign, ":team_faction", "fac_player_faction"),
      (try_end),
      (dict_set_int, "$coop_dict", "@tm1_fac", ":team_faction"),

      (str_store_faction_name, s0, "$players_kingdom"),
      (dict_set_str, "$coop_dict", "@tm1_name", s0),

      (try_for_range, reg1, 0, 9),
        (str_store_class_name, s0, reg1), #(str_store_class_name,<string_register>,<class_id>)
        (dict_set_str, "$coop_dict", "@cls{reg1}_name", s0),
      (try_end),


##COPY PARTIES TO REG##


#ADD ENEMY PARTIES

    (assign, reg22, 0), #count heroes

    (party_get_num_attached_parties, ":no_enemy_parties", "$coop_encountered_party"),
    (val_add, ":no_enemy_parties", 1), 
    (dict_set_int, "$coop_dict", "@num_parties_enemy", ":no_enemy_parties"),

    (try_for_range, reg20, 0, ":no_enemy_parties"),
      (try_begin),
        (eq, reg20, 0),#first party
        (assign, ":var_6", "$coop_encountered_party"),
      (else_try),
        (store_sub, ":attached_party_rank", reg20, 1), #sub 1 so rank starts from 0
        (party_get_attached_party_with_rank, ":var_6", "$coop_encountered_party", ":attached_party_rank"),
      (try_end),

      (assign, ":banner_spr", 0), 
	  	    (store_random_in_range, ":offset", 0, 520), # Actual index of the random scene (returns 0-11) (0 Counts as well) so count from 0 and up, which means 4 is 5 if you are counting from 1.
		(assign, ":banner_mesh", "mesh_banner_a01"), # Safeguard for sea battles etc does not require terrain type.
		(val_add, ":banner_mesh", ":offset"), 
      (try_begin),
        (this_or_next|party_slot_eq, ":var_6", slot_party_type, spt_village),
        (this_or_next|party_slot_eq, ":var_6", slot_party_type, spt_town),
        (party_slot_eq, ":var_6", slot_party_type, spt_castle),
        (dict_set_int, "$coop_dict", "@p_garrison", reg20), #store rank of garrison party
        (party_get_slot, ":cur_leader", ":var_6", slot_town_lord), #can't store index of leader party here because we don't know it yet
        (ge, ":cur_leader", 0),
        (troop_get_slot, ":banner_spr", ":cur_leader", slot_troop_banner_scene_prop),
        (dict_set_int, "$coop_dict", "@p_garrison_banner", ":banner_spr"),
      (else_try),
        (party_stack_get_troop_id, ":leader_troop", ":var_6", 0),
        (troop_slot_eq, ":leader_troop", slot_troop_occupation, 2),
        (troop_get_slot, ":banner_spr", ":leader_troop", slot_troop_banner_scene_prop),
      (try_end),
      (try_begin),
        (store_add, ":banner_scene_props_end", banner_scene_props_end_minus_one, 1),
        (is_between, ":banner_spr", banner_scene_props_begin, ":banner_scene_props_end"),
        (val_sub, ":banner_spr", banner_scene_props_begin),
        (store_add, ":banner_mesh", ":banner_spr", arms_meshes_begin),	
      (try_end),
      (try_begin), #store which party is garrison commander
        (eq, ":var_6", ":garrison_lord_party"),
        (dict_set_int, "$coop_dict", "@p_castle_lord", reg20), #store INDEX of garrison party (not party id)
      (try_end),
	
      (dict_set_int, "$coop_dict", "@p_enemy{reg20}_banner", ":banner_mesh"),
      (dict_set_int, "$coop_dict", "@p_enemy{reg20}_partyid", ":var_6"),


      (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
      (dict_set_int, "$coop_dict", "@p_enemy{reg20}_numstacks", ":num_prisoner_stacks_script_param_1_leaded_party_2"),

      (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
        (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", reg21),
        (party_stack_get_size, ":total_stack_size", ":var_6", reg21),
        (party_stack_get_num_wounded, ":num_wounded",":var_6", reg21),

        (try_begin),
          (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (store_troop_health, ":hero_health", ":party_stack_troop_id_temp_party_localvariable"),
          (le, ":hero_health", 15),
          (assign, ":num_wounded", 1),  
        (try_end),
        (store_sub, ":party_prisoner_stack_size_var_6_var_9", ":total_stack_size", ":num_wounded"), 
        (ge, ":party_prisoner_stack_size_var_6_var_9",1), #if alive
        (try_begin),
          (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (dict_set_int, "$coop_dict", "@hero_{reg22}_trp", ":party_stack_troop_id_temp_party_localvariable"),
          (val_add, reg22, 1), 
        (try_end),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_{reg21}_trp", ":party_stack_troop_id_temp_party_localvariable"),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_{reg21}_num", ":party_prisoner_stack_size_var_6_var_9"),
      (try_end),
    (try_end),



#ADD ALLY PARTIES
      (assign, ":no_ally_parties", 1), # start from 1 because main party
      (try_begin),
        (gt, "$g_ally_party", 0), #if allies are attached to ally party
        (assign, ":ally_party", "$g_ally_party"),
        (assign, ":rank_start", 2),
        (val_add, ":no_ally_parties", 1), #add one for ally
      (else_try),
        (assign, ":rank_start", 1),
        (assign, ":ally_party", "p_main_party"), #if allies are attached to us
      (try_end),

    (party_get_num_attached_parties, ":num_attached_parties", ":ally_party"),
    (val_add, ":no_ally_parties", ":num_attached_parties"), 
    (dict_set_int, "$coop_dict", "@num_parties_ally", ":no_ally_parties"),

    (try_for_range, reg20, 0, ":no_ally_parties"),
      (try_begin),
        (eq, reg20, 0),#first party
        (assign, ":var_6", "p_main_party"),
      (else_try),
        (gt, "$g_ally_party", 0),
        (eq, reg20, 1),#second party
        (assign, ":var_6", "$g_ally_party"),
      (else_try),
        (store_sub, ":attached_party_rank", reg20, ":rank_start"), #sub 1 or 2 so rank starts from 0
        (party_get_attached_party_with_rank, ":var_6", ":ally_party", ":attached_party_rank"),
      (try_end),

      (assign, ":banner_spr", 0), 
	  	    (store_random_in_range, ":offset", 0, 520), # Actual index of the random scene (returns 0-11) (0 Counts as well) so count from 0 and up, which means 4 is 5 if you are counting from 1.
		(assign, ":banner_mesh", "mesh_banner_a01"), # Safeguard for sea battles etc does not require terrain type.
		(val_add, ":banner_mesh", ":offset"), 
      (try_begin),
        (eq, ":var_6", "p_main_party"),
	  	    (store_random_in_range, ":offset", 0, 520), # Actual index of the random scene (returns 0-11) (0 Counts as well) so count from 0 and up, which means 4 is 5 if you are counting from 1.
		(assign, ":banner_mesh", "mesh_banner_a01"), # Safeguard for sea battles etc does not require terrain type.
		(val_add, ":banner_mesh", ":offset"), 
      (try_end),
      (try_begin),
        (this_or_next|party_slot_eq, ":var_6", slot_party_type, spt_village),
        (this_or_next|party_slot_eq, ":var_6", slot_party_type, spt_town),
        (party_slot_eq, ":var_6", slot_party_type, spt_castle),
        (dict_set_int, "$coop_dict", "@p_garrison", reg20), #store rank of garrison party
        (party_get_slot, ":cur_leader", ":var_6", slot_town_lord), #can't store index of leader party here because we don't know it yet
        (ge, ":cur_leader", 0),
        (troop_get_slot, ":banner_spr", ":cur_leader", slot_troop_banner_scene_prop),
        (dict_set_int, "$coop_dict", "@p_garrison_banner", ":banner_spr"),
      (else_try),
        (party_stack_get_troop_id, ":leader_troop", ":var_6", 0),
        (troop_is_hero, ":leader_troop"),
        (troop_get_slot, ":banner_spr", ":leader_troop", slot_troop_banner_scene_prop),
      (try_end),
      (try_begin),
        (store_add, ":banner_scene_props_end", banner_scene_props_end_minus_one, 1),
        (is_between, ":banner_spr", banner_scene_props_begin, ":banner_scene_props_end"),
        (val_sub, ":banner_spr", banner_scene_props_begin),
        (store_add, ":banner_mesh", ":banner_spr", arms_meshes_begin),	
      (try_end),

      (try_begin), #store which party is garrison commander
        (eq, ":var_6", ":garrison_lord_party"),
        (dict_set_int, "$coop_dict", "@p_castle_lord", reg20),  #store INDEX of garrison party (not party id)
      (try_end),
	
      (dict_set_int, "$coop_dict", "@p_ally{reg20}_banner", ":banner_mesh"),
      (dict_set_int, "$coop_dict", "@p_ally{reg20}_partyid", ":var_6"), #store party id for SP



      (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
      (dict_set_int, "$coop_dict", "@p_ally{reg20}_numstacks", ":num_prisoner_stacks_script_param_1_leaded_party_2"),
      (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
        (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", reg21),
        (party_stack_get_size, ":total_stack_size", ":var_6", reg21),
        (party_stack_get_num_wounded, ":num_wounded",":var_6", reg21),
        (try_begin),
          (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (store_troop_health, ":hero_health", ":party_stack_troop_id_temp_party_localvariable"),
          (le, ":hero_health", 15),
          (assign, ":num_wounded", 1),  
        (try_end),
        (store_sub, ":party_prisoner_stack_size_var_6_var_9", ":total_stack_size", ":num_wounded"), 
        (ge, ":party_prisoner_stack_size_var_6_var_9",1), #if alive

        (try_begin), #if storing main party
          (eq, ":var_6", "p_main_party"),
          (troop_get_class, ":troop_class", ":party_stack_troop_id_temp_party_localvariable"),
          (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_cls", ":troop_class"),
          (eq, ":party_stack_troop_id_temp_party_localvariable", "trp_player"), 
          (troop_get_type, ":type_script_param_1", "trp_player"),
          (try_begin),
            (eq, ":type_script_param_1", 1),
            (assign, ":party_stack_troop_id_temp_party_localvariable",  "trp_multiplayer_profile_troop_female"),  
          (else_try),
            (assign, ":party_stack_troop_id_temp_party_localvariable",  "trp_multiplayer_profile_troop_male"),  
          (try_end),
        (try_end),

        (try_begin),
          (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
          (dict_set_int, "$coop_dict", "@hero_{reg22}_trp", ":party_stack_troop_id_temp_party_localvariable"),
          (val_add, reg22, 1), 
        (try_end),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_trp", ":party_stack_troop_id_temp_party_localvariable"),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_num", ":party_prisoner_stack_size_var_6_var_9"),
      (try_end),
    (try_end),

    (dict_set_int, "$coop_dict", "@hero_num", reg22),

    (call_script, "script_coop_copy_hero_to_file"), 



    (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
    (dict_save, "$coop_dict", s41), #save new data
    (dict_free, "$coop_dict"),
    (display_message, "@Battle setup complete.", 0x00a2d9ce),
	(display_message, "@You may now click on Multiplayer in the Main Menu > Host Game > Start Map if things look right.", 0x00a2d9ce),
	(display_message, "@If you are using a Dedicated Server you can upload the data from the WSE Folder at My Documents > Mount&Blade Warband/WSE/Medieval_Conquests then load it from the Dedicated Server Administrator Panel, you can upload the file using FTP or PHP Scripts, you would also need to adjust wse_settings.txt path to aim for the .dict files.", 0x00a2d9ce), #0x00 is always necessary before color.
    (try_end),

    ]),	
##B


##E
  # 
   #script_coop_copy_file_to_parties_mp
  # Input: arg1 = party_no
  ("coop_copy_file_to_parties_mp",
   [
    (try_begin), 
      (neg|is_vanilla_warband),

      (dict_get_int, "$coop_no_enemy_parties", "$coop_dict", "@num_parties_enemy"),
      (dict_get_int, "$coop_no_ally_parties", "$coop_dict", "@num_parties_ally"),

  #BOTH MODES
      (call_script, "script_coop_copy_file_to_settings"),	#copy game settings here
      (call_script, "script_coop_copy_file_to_hero"),

  #CLEAR casualty parties
      (try_for_range, ":party_rank", 0, "$coop_no_enemy_parties"),
        (store_add, ":var_6", ":party_rank", coop_temp_casualties_enemy_begin), 
        (party_clear, ":var_6"),
      (try_end),
      (try_for_range, ":party_rank", 0, "$coop_no_ally_parties"),
        (store_add, ":var_6", ":party_rank", coop_temp_casualties_ally_begin), 
        (party_clear, ":var_6"),
      (try_end),

  #ADD TROOPS TO TEMP SPAWN PARTIES 
  #ENEMY TEAM
      (assign, ":total_enemy_troops", 0),
      # (assign, ":cur_slot", 101),
        (party_clear, coop_temp_party_enemy_heroes),
      (try_for_range, reg20, 0, "$coop_no_enemy_parties"), #number of enemy parties
        (call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 0, reg20),
        (assign, ":num_prisoner_stacks_script_param_1_leaded_party_2", reg1),
        (assign, ":banner_mesh", reg2),
        (troop_set_slot, "trp_temp_array_a", reg20, ":banner_mesh"),#encountered party banner
        (store_add, ":var_6", reg20, coop_temp_party_enemy_begin),
        (party_clear, ":var_6"),
        (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (call_script, "script_coop_battle_dict_read_roster_stack", "$coop_dict", 0, reg20, reg21),
          (assign, ":party_stack_troop_id_temp_party_localvariable", reg0),
          (assign, ":party_prisoner_stack_size_var_6_var_9", reg1),
          (party_add_members, ":var_6", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"), #when copy to MP wounded troops have already been removed
          (val_add, ":total_enemy_troops", ":party_prisoner_stack_size_var_6_var_9"),

          (try_begin),
            (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
            (eq, ":party_prisoner_stack_size_var_6_var_9",1), #if alive
            (party_add_members, coop_temp_party_enemy_heroes, ":party_stack_troop_id_temp_party_localvariable", 1),
          (try_end),
        (try_end),
      (try_end), #end enemy parties
      # (troop_set_slot, "trp_temp_array_a", 100, ":cur_slot"),# slot 100 = 100 + number heroes + 1
      (assign, "$coop_num_bots_team_1", ":total_enemy_troops"), #count troops in battle




  #PLAYER TEAM  
      (assign, ":total_ally_troops", 0),
      # (assign, ":cur_slot", 101),
        (party_clear, coop_temp_party_ally_heroes),


      (try_for_range, reg20, 0, "$coop_no_ally_parties"),
        (call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 1, reg20),
        (assign, ":num_prisoner_stacks_script_param_1_leaded_party_2", reg1),
        (assign, ":banner_mesh", reg2),
        (troop_set_slot, "trp_temp_array_b", reg20, ":banner_mesh"),#encountered party banner
        (store_add, ":var_6", reg20, coop_temp_party_ally_begin),
        (party_clear, ":var_6"),
        (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (call_script, "script_coop_battle_dict_read_roster_stack", "$coop_dict", 1, reg20, reg21),
          (assign, ":party_stack_troop_id_temp_party_localvariable", reg0),
          (assign, ":party_prisoner_stack_size_var_6_var_9", reg1),
          (party_add_members, ":var_6", ":party_stack_troop_id_temp_party_localvariable", ":party_prisoner_stack_size_var_6_var_9"), #when copy to MP wounded troops have already been removed
          (val_add, ":total_ally_troops", ":party_prisoner_stack_size_var_6_var_9"),
          (try_begin),
            (eq, reg20, 0), #main party
            (dict_get_int, ":troop_class", "$coop_dict", "@p_ally0_{reg21}_cls"),
            (troop_set_slot, ":party_stack_troop_id_temp_party_localvariable", slot_troop_current_rumor, ":troop_class"), #store main party troop class in this slot
          (try_end),
          (try_begin),
            (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
            (eq, ":party_prisoner_stack_size_var_6_var_9",1), #if alive
            (party_add_members, coop_temp_party_ally_heroes, ":party_stack_troop_id_temp_party_localvariable", 1),
          (try_end),

        (try_end),
      (try_end), #end ally parties
      # (troop_set_slot, "trp_temp_array_b", 100, ":cur_slot"),# slot 100 = 100 + number heroes + 1
      (assign, "$coop_num_bots_team_2", ":total_ally_troops"), #count troops in battle

    (try_end),

      ]),




  # 
   #script_coop_copy_parties_to_file_mp
  # Input: arg1 = party_no
  ("coop_copy_parties_to_file_mp",
   [
    (try_begin), 
      (neg|is_vanilla_warband),
      (dict_create, "$coop_dict"),
      (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
      (dict_load_file, "$coop_dict", s41, 2),

        (dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_end_mp),
        (assign, reg0, "$coop_winner_team"),
        (display_message, "@[BATTLE SAVE] set battle_state=end_mp (4), winner_team={reg0}"),

        (call_script, "script_coop_copy_settings_to_file"),

#At end of MP battle:

      #copy health from ALIVE agents to hero troops here before copying to registers (dead agents health is copied at coop_server_on_agent_killed_or_wounded_common)
      (try_for_agents, ":cur_agent"),
        (agent_is_human, ":cur_agent"),  
        (agent_is_alive, ":cur_agent"),
        (agent_get_troop_id, ":agent_troop_id", ":cur_agent"),
        (troop_is_hero, ":agent_troop_id"),   
        (store_agent_hit_points, ":agent_hit_points", ":cur_agent"),
        (troop_set_health, ":agent_troop_id", ":agent_hit_points"),

        # store items from agents
        (call_script, "script_coop_player_agent_save_items", ":cur_agent"),
      (try_end),

      (try_begin), 
        (eq, "$coop_winner_team", 0),#0 = enemy won
        (dict_set_int, "$coop_dict", "@battle_result", -1), # = battle_result
      (else_try),
        (eq, "$coop_winner_team", 1), #1 = player won
        (dict_set_int, "$coop_dict", "@battle_result", 1),
      (else_try),
        (dict_set_int, "$coop_dict", "@battle_result", 0),
      (try_end),


#ENEMY TEAM
      (try_for_range, reg20, 0, "$coop_no_enemy_parties"),
        (store_add, ":var_6", reg20, coop_temp_casualties_enemy_begin), 
        (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
        (call_script, "script_coop_battle_dict_put_stack_cas_count", 0, reg20, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
        (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", reg21),
          (party_stack_get_size, ":total_stack_size", ":var_6", reg21),
          (party_stack_get_num_wounded, ":num_wounded",":var_6", reg21),
          (try_begin),
            (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
            (store_troop_health, ":hero_health", ":party_stack_troop_id_temp_party_localvariable"),
            (le, ":hero_health", 15),
            (assign, ":num_wounded", 1),  
          (try_end),
          (store_sub, ":dead_size", ":total_stack_size", ":num_wounded"),
          (call_script, "script_coop_battle_dict_put_stack_cas", 0, reg20, reg21,
              ":party_stack_troop_id_temp_party_localvariable", ":dead_size", ":num_wounded"),
        (try_end),
      (try_end),




#ADD PARTIES ATTACHED TO MAIN PARTY
      (try_for_range, reg20, 0, "$coop_no_ally_parties"),
        (store_add, ":var_6", reg20, coop_temp_casualties_ally_begin), 
        (party_get_num_companion_stacks, ":num_prisoner_stacks_script_param_1_leaded_party_2", ":var_6"),
        (call_script, "script_coop_battle_dict_put_stack_cas_count", 1, reg20, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
        (try_for_range, reg21, 0, ":num_prisoner_stacks_script_param_1_leaded_party_2"),
          (party_stack_get_troop_id, ":party_stack_troop_id_temp_party_localvariable", ":var_6", reg21),
          (party_stack_get_size, ":total_stack_size", ":var_6", reg21),
          (party_stack_get_num_wounded, ":num_wounded",":var_6", reg21),
          (try_begin),
            (troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
            (store_troop_health, ":hero_health", ":party_stack_troop_id_temp_party_localvariable"),
            (le, ":hero_health", 15),
            (assign, ":num_wounded", 1),  
          (try_end),
          (store_sub, ":dead_size", ":total_stack_size", ":num_wounded"),
          (call_script, "script_coop_battle_dict_put_stack_cas", 1, reg20, reg21,
              ":party_stack_troop_id_temp_party_localvariable", ":dead_size", ":num_wounded"),
        (try_end),
      (try_end),



      (call_script, "script_coop_copy_hero_to_file"),

      (get_max_players, ":num_players"),
      (try_for_range, ":player_no", 0, ":num_players"), 
        (player_is_active, ":player_no"),
        (player_is_admin, ":player_no"),
        (multiplayer_send_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_result_saved),
      (try_end),
      # ========================================================
      # SP XP parity: battle metadata snapshot
      # ========================================================
      # Single randomness roll shared across all players (R1 in spec).
      # Every player's share is scaled by this same value so multi-player
      # fights produce deterministic relative shares.
      (store_random_in_range, ":rand_pct", 50, 101),
      (dict_set_int, "$coop_dict", "@battle_xp_rand", ":rand_pct"),
      (assign, reg1, ":rand_pct"),
      (display_message, "@[BATTLE SAVE] xp_rand={reg1}"),

      # Snapshot active players in the battle: name + strength weight.
      # reg20 is the slot index; used in key interpolation.
      (assign, reg20, 0),
      (try_for_players, ":player_no", 1),
          (player_is_active, ":player_no"),
          (str_store_player_username, s1, ":player_no"),
          (dict_set_str, "$coop_dict", "@battle_player_{reg20}_name", s1),

          (player_get_agent_id, ":agent_no", ":player_no"),
          (try_begin),
              (ge, ":agent_no", 0),
              (agent_get_troop_id, ":ptroop", ":agent_no"),
              (store_character_level, ":plevel", ":ptroop"),
          (else_try),
              (assign, ":plevel", 1),
          (try_end),
          (store_mul, ":pstrength", ":plevel", 10),
          (dict_set_int, "$coop_dict", "@battle_player_{reg20}_strength", ":pstrength"),

          (assign, reg1, reg20),
          (assign, reg2, ":pstrength"),
          (display_message, "@[BATTLE SAVE] player{reg1} name={s1} strength={reg2}"),

          (val_add, reg20, 1),
      (try_end),
      (dict_set_int, "$coop_dict", "@battle_num_players", reg20),
      (assign, reg1, reg20),
      (display_message, "@[BATTLE SAVE] num_battle_players={reg1}"),

      (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
      (dict_save, "$coop_dict", s41),
      (display_message, "@[BATTLE SAVE] dict saved to {s41} -- campaign server can poll now."),
      # Set to -1 AFTER dict_save so the DLL poll thread only observes this
      # edge once the battle dict is guaranteed to be on disk. The DLL
      # watches for this transition to send PKT_BATTLE_END.
      (assign, "$coop_battle_started", -1),
      (dict_free, "$coop_dict"),
    (try_end),
    ]),




  #
   #script_coop_copy_file_to_parties_sp
  # Input: arg1 = party_no
  ("coop_copy_file_to_parties_sp",
   [
    (try_begin), 
      (neg|is_vanilla_warband),
    (dict_create, "$coop_dict"),
    (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
    (dict_load_file, "$coop_dict", s41, 2),

    (dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_none),
    (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
    (dict_save, "$coop_dict", s41),

    (dict_get_int, "$coop_no_enemy_parties", "$coop_dict", "@num_parties_enemy"),
    (dict_get_int, "$coop_no_ally_parties", "$coop_dict", "@num_parties_ally"),

#BOTH MODES
    (call_script, "script_coop_copy_file_to_settings"),	#copy game settings here before heroes
    (call_script, "script_coop_copy_file_to_hero"), #this sets hero health from battle

#create temp parties or wound parties
    (party_clear, "p_total_enemy_casualties"),
    (party_clear, "p_enemy_casualties"),

    (try_for_range, reg20, 0, "$coop_no_enemy_parties"), #number of enemy parties
      (call_script, "script_coop_battle_dict_get_stack_cas_count", 0, reg20),
      (assign, ":num_casualty_stacks", reg0),
      (call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 0, reg20),
      (assign, ":party_to_kill", reg0),

      (try_for_range, reg21, 0, ":num_casualty_stacks"),
        (call_script, "script_coop_battle_dict_get_stack_cas", 0, reg20, reg21),
        (assign, ":party_stack_troop_id_temp_party_localvariable", reg0),
        (assign, ":stack_dead", reg1),
        (assign, ":stack_wounded", reg2),

          (store_add, ":stack_total_casualties", ":stack_dead", ":stack_wounded"),
          (try_begin),
            (troop_is_hero,":party_stack_troop_id_temp_party_localvariable"),
            (store_random_in_range, ":rand_wound", 40, 71),
            (store_troop_health, ":troop_hp",":party_stack_troop_id_temp_party_localvariable"),
            (val_sub, ":troop_hp", ":rand_wound"),
            (val_max, ":troop_hp", 1),
            (troop_set_health, ":party_stack_troop_id_temp_party_localvariable", ":troop_hp"),
          (else_try),
            (party_remove_members, ":party_to_kill", ":party_stack_troop_id_temp_party_localvariable", ":stack_dead"),#remove from parties
          (try_end),
          (party_wound_members, ":party_to_kill", ":party_stack_troop_id_temp_party_localvariable", ":stack_wounded"),
          (party_add_members, "p_total_enemy_casualties", ":party_stack_troop_id_temp_party_localvariable", ":stack_total_casualties"), #add casualties for loot
          (party_wound_members, "p_total_enemy_casualties", ":party_stack_troop_id_temp_party_localvariable", ":stack_wounded"),
          (party_add_members, "p_enemy_casualties", ":party_stack_troop_id_temp_party_localvariable", ":stack_total_casualties"), #add casualties for reports/morale
          (party_wound_members, "p_enemy_casualties", ":party_stack_troop_id_temp_party_localvariable", ":stack_wounded"),
      (try_end),
    (try_end), #end enemy parties




    (assign, "$any_allies_at_the_last_battle", 0),
    (party_clear, "p_player_casualties"),
    (party_clear, "p_ally_casualties"),
    (try_for_range, reg20, 0, "$coop_no_ally_parties"),
      (call_script, "script_coop_battle_dict_get_stack_cas_count", 1, reg20),
      (assign, ":num_casualty_stacks", reg0),
      (call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 1, reg20),
      (assign, ":party_to_kill", reg0),

      (try_begin),
        (eq, ":party_to_kill", "p_main_party"),
        (assign, ":casualties_party", "p_player_casualties"),
        (party_get_skill_level, ":player_party_surgery", "p_main_party", "skl_surgery"),
        (val_mul, ":player_party_surgery", 4),    #4% per skill level
      (else_try),
        (assign, "$any_allies_at_the_last_battle", 1),
        (assign, ":casualties_party", "p_ally_casualties"),
      (try_end),

      (assign, reg1, ":num_casualty_stacks"),
      (assign, reg2, ":party_to_kill"),
      (display_message, "@[CAMPAIGN CAS] ally{reg20}: {reg1} casualty stacks, party_to_kill={reg2}"),
      (try_for_range, reg21, 0, ":num_casualty_stacks"),
        (call_script, "script_coop_battle_dict_get_stack_cas", 1, reg20, reg21),
        (assign, ":party_stack_troop_id_temp_party_localvariable", reg0),
        (assign, ":stack_dead", reg1),
        (assign, ":stack_wounded", reg2),
        (store_add, ":stack_total_casualties", ":stack_dead", ":stack_wounded"),
        (assign, reg1, ":stack_dead"),
        (assign, reg2, ":stack_wounded"),
        (str_store_troop_name, s1, ":party_stack_troop_id_temp_party_localvariable"),
        (display_message, "@[CAMPAIGN CAS] -- {s1}: dead={reg1} wounded={reg2}"),

        (try_begin),
          (eq, ":party_to_kill", "p_main_party"),
          (try_begin),
            (this_or_next|eq, ":party_stack_troop_id_temp_party_localvariable",  "trp_multiplayer_profile_troop_female"),  
            (eq, ":party_stack_troop_id_temp_party_localvariable",  "trp_multiplayer_profile_troop_male"),  
            (assign, ":party_stack_troop_id_temp_party_localvariable", "trp_player"),
          (try_end),
          (try_begin),#use surgey to heal regular troops in stack
            (neg|troop_is_hero, ":party_stack_troop_id_temp_party_localvariable"),
            (assign, ":end", ":stack_dead"),
            (try_for_range, ":unused", 0, ":end"),#try each dead troop in stack
              (store_random_in_range, ":rand", 0, 100),
              (lt, ":rand", ":player_party_surgery"),
              (val_add, ":stack_wounded", 1),
              (val_sub, ":stack_dead", 1),
            (try_end),
          (try_end),
        (else_try), #ally party
          (troop_is_hero,":party_stack_troop_id_temp_party_localvariable"),#ally lord
          (store_random_in_range, ":rand_wound", 40, 71),
          (store_troop_health, ":troop_hp",":party_stack_troop_id_temp_party_localvariable"),
          (val_sub, ":troop_hp", ":rand_wound"),
          (val_max, ":troop_hp", 1),
          (troop_set_health, ":party_stack_troop_id_temp_party_localvariable", ":troop_hp"),
        (try_end),

        (party_wound_members, ":party_to_kill", ":party_stack_troop_id_temp_party_localvariable", ":stack_wounded"), #wound regular and heroes
        (try_begin),
          (neg|troop_is_hero,":party_stack_troop_id_temp_party_localvariable"),
          (party_remove_members, ":party_to_kill", ":party_stack_troop_id_temp_party_localvariable", ":stack_dead"), #kill regulars
        (try_end),

        #add dead and wounded for casualty report
        (party_add_members, ":casualties_party", ":party_stack_troop_id_temp_party_localvariable", ":stack_total_casualties"),#dead
        (party_wound_members, ":casualties_party", ":party_stack_troop_id_temp_party_localvariable", ":stack_wounded"),#wounded
      (try_end),
    (try_end),


#SP USE RESULT needs to be after troops are healed to count them as routed

      (dict_get_int, "$g_battle_result", "$coop_dict", "@battle_result"),  #-1 = enemy won, 1 = player won
      (try_begin),
        (eq, "$g_battle_result", -1), #enemy won
        (call_script, "script_party_count_members_with_full_health", "p_main_party"), 
        (assign, "$num_routed_us", reg0), 
        (call_script, "script_party_count_members_with_full_health", "p_collective_friends"),        
        (assign, "$num_routed_allies", reg0), #use routed troops to avoid a 2nd round of battle
      (else_try),
        (eq, "$g_battle_result", 1), #player won
        (call_script, "script_party_count_members_with_full_health", "p_collective_enemy"),
        (assign, "$num_routed_enemies", reg0), #use routed troops to avoid a 2nd round of battle
      (else_try),
        (eq, "$g_battle_result", 0), #retreat
      (try_end),


    (dict_free, "$coop_dict"),
    (try_end),
    ]),	




 # 
   # script_coop_copy_register_to_hero_xp
  ("coop_copy_register_to_hero_xp",
    [
      (store_script_param, ":troop", 1),
      (store_script_param, ":troop_xp", 2),
      (try_begin),
        (troop_get_xp, ":troop_default_xp", ":troop"),
        (store_sub, ":xp_to_add", ":troop_xp", ":troop_default_xp"), 

         # (str_store_troop_name, s40, ":troop"),
         # (assign, reg1, ":xp_to_add"),
         # (assign, reg2, ":troop_default_xp"),
         # (assign, reg3, ":troop_xp"),
         # (display_message, "@Adding {reg1} xp to {s40}   {reg2} / {reg3}"),

        (try_begin),
          (gt, ":xp_to_add", 29999),
          (store_div, ":num_times", ":xp_to_add", 29999), 
          (try_for_range, ":unused", 0, ":num_times"),
            (add_xp_to_troop, 29999, ":troop"),
            (val_sub, ":xp_to_add", 29999), 
          (try_end),		 
        (try_end),		 
        (add_xp_to_troop, ":xp_to_add", ":troop"),		 #add leftover xp
      (try_end),	




    ]),	 

   
#pavise_related_things BEGIN   
#("cf_is_behind_pavise",
# [(store_script_param, ":agent_no", 1),   
#  (store_script_param, ":pavise", 2),   
#  (set_fixed_point_multiplier, 100),
#  (assign, ":behind", 0),
#  (agent_get_position, pos5, ":agent_no"),
#  (scene_prop_get_num_instances, ":num_pavises", ":pavise"),
#  (try_for_range, ":pavise_no", 0, ":num_pavises"),
#     (eq, ":behind", 0),
#     (scene_prop_get_instance, ":pavise_prop_id", ":pavise", ":pavise_no"),
#     (prop_instance_is_valid, ":pavise_prop_id"),
#     (scene_prop_get_hit_points, ":hp", ":pavise_prop_id"),
#     (gt, ":hp", 0),
#     (prop_instance_get_position, pos2, ":pavise_prop_id"),
#     (position_transform_position_to_local, pos3, pos5, pos2),
#     (position_get_y, ":posy", pos3),
#     (is_between, ":posy", 0, 100),
#     (position_get_x, ":posx", pos3),
#     (is_between, ":posx", -70, 70),
#     (assign, ":behind", 1),
#   (try_end), 
#   (eq, ":behind", 1), ]),     
#
# 
#("deploy_pavise",
# [(store_script_param, ":agent_no", 1), 
#  (agent_get_wielded_item, ":shield_item", ":agent_no", 1),
#  (try_begin),
#     (is_between, ":shield_item", "itm_tab_shield_pavise_a", "itm_tab_shield_pavise_c"),
#     (assign, ":pavise_shield","spr_pavise_shield3"),
#  (else_try),
#     (is_between, ":shield_item", "itm_tab_shield_pavise_c", "itm_tab_shield_small_round_a"),
#     (assign, ":pavise_shield","spr_pavise_shield1"),
#  (else_try),
#     (assign, ":pavise_shield", 0),
#  (try_end),
#  (try_begin), 
#    (gt, ":pavise_shield", 0),
#    (call_script, "script_cf_agent_pushed_to_crouch",":agent_no"),
#    (set_fixed_point_multiplier, 100),
#    (agent_get_position, pos2, ":agent_no"),
#    (position_move_y, pos2, 75, 0),
#    (position_set_z_to_ground_level, pos2),
#    (set_spawn_position, pos2),
#    (spawn_scene_prop, ":pavise_shield"),
#    (agent_unequip_item, ":agent_no", ":shield_item"),
#  (try_end), ]),   
#pavise_related_things END

# SET heroes SKILL/EQUIPMENT 
  # script_coop_copy_hero_to_file
  # Input: arg1 = hero troop
  # Output: none
  ("coop_copy_hero_to_file",
    [
    (try_begin), 
      (neg|is_vanilla_warband),

      (dict_get_int, ":number_heroes", "$coop_dict", "@hero_num"),
      (try_for_range, reg21, 0, ":number_heroes"),
        (dict_get_int, ":troop_2", "$coop_dict", "@hero_{reg21}_trp"),
        (try_begin),
          (neg|game_in_multiplayer_mode),
          (this_or_next|eq, ":troop_2",  "trp_multiplayer_profile_troop_female"),  
          (eq, ":troop_2",  "trp_multiplayer_profile_troop_male"),  
          (assign, ":troop_2", "trp_player"),
         # (store_troop_gold, ":gold", ":troop_2"), #use this if needed
          # (dict_set_int, "$coop_dict", "@hero_{reg21}_gld", ":gold"),
        (try_end),

				(str_store_troop_name, s0, ":troop_2"),
        (troop_get_xp, ":xp", ":troop_2"),
        (store_troop_health, ":health", ":troop_2"),
        (dict_set_str, "$coop_dict", "@hero_{reg21}_name", s0),
        (dict_set_int, "$coop_dict", "@hero_{reg21}_xp", ":xp"),
        (dict_set_int, "$coop_dict", "@hero_{reg21}_hp", ":health"),

#NEW
        (face_keys_init, reg1),
        #(troop_get_face_keys, reg1, ":troop_2"),
        #(str_store_face_keys, s0, reg1),
        (dict_set_str, "$coop_dict", "@hero_{reg21}_face", s0),
#####PROBABLY BUGGY BEGIN
#        (store_attribute_level, ":0", ":troop_2", 0),
#        (store_attribute_level, ":1", ":troop_2", 1),
#        # (store_attribute_level, ":2", ":troop_2", 2),
#        # (store_attribute_level, ":3", ":troop_2", 3),
#
#        (dict_set_int, "$coop_dict", "@hero_{reg21}_str", ":0"),
#        (dict_set_int, "$coop_dict", "@hero_{reg21}_agi", ":1"),
#        # (dict_set_int, "$coop_dict", "@hero_{reg21}_int", ":2"),
#        # (dict_set_int, "$coop_dict", "@hero_{reg21}_cha", ":3"),
#
#
#        (try_for_range, reg20, "skl_horse_archery", "skl_reserved_14"), #start from "skl_trade" if all skills are needed
#          (neg|is_between, reg20, "skl_reserved_9", "skl_power_draw"), #skip these skills
#          (store_skill_level, ":skill_level_leadership_var_1", reg20, ":troop_2"),
#          (dict_set_int, "$coop_dict", "@hero_{reg21}_skl{reg20}", ":skill_level_leadership_var_1"),
#        (try_end),
#
#        (try_for_range, reg20, 0, 7),  #wpt_firearm = 6 
		#####PROBABLY BUGGY END
		(store_attribute_level, ":0", ":troop_2", 0),
		(store_attribute_level, ":1", ":troop_2", 1),
		
        #(store_attribute_level, ":ca_strength", ":troop_2", ca_strength),          #DEF
        #(store_attribute_level, ":ca_agility", ":troop_2", ca_agility),            #DEF
        # (store_attribute_level, ":ca_intelligence", ":troop_2", ca_intelligence),
        # (store_attribute_level, ":ca_charisma", ":troop_2", ca_charisma),

		  (dict_set_int, "$coop_dict", "@hero_{reg21}_str", ":0"),
		  (dict_set_int, "$coop_dict", "@hero_{reg21}_agi", ":1"),
       #(dict_set_int, "$coop_dict", "@hero_{reg21}_str", ":ca_strength"),        # DEF
       #(dict_set_int, "$coop_dict", "@hero_{reg21}_agi", ":ca_agility"),         # DEF
        # (dict_set_int, "$coop_dict", "@hero_{reg21}_int", ":ca_intelligence"),
        # (dict_set_int, "$coop_dict", "@hero_{reg21}_cha", ":ca_charisma"),


        (try_for_range, reg20, "skl_horse_archery", "skl_reserved_14"), #start from "skl_trade" if all skills are needed
          (neg|is_between, reg20, "skl_reserved_9", "skl_power_draw"), #skip these skills
          (store_skill_level, ":skill_level_leadership_var_1", reg20, ":troop_2"),
          (dict_set_int, "$coop_dict", "@hero_{reg21}_skl{reg20}", ":skill_level_leadership_var_1"),
        (try_end),
		
		(try_for_range, reg20, 0, 7),  #wpt_firearm = 6 
       # (try_for_range, reg20, wpt_one_handed_weapon, 7),  #wpt_firearm = 6  #Def
          (store_proficiency_level, ":prof", ":troop_2", reg20),
          (dict_set_int, "$coop_dict", "@hero_{reg21}_wp{reg20}", ":prof"),
        (try_end),

        (try_begin),
          (neg|is_between, ":troop_2", kings_begin, pretenders_end), #need this so we dont equip lords with civilian clothes in battle
          (try_for_range, reg20, ek_item_0, ek_food), 
            (troop_get_inventory_slot, ":item", ":troop_2", reg20),
            (troop_get_inventory_slot_modifier, ":imod", ":troop_2", reg20),
            (dict_set_int, "$coop_dict", "@hero_{reg21}_itm{reg20}", ":item"),
            (dict_set_int, "$coop_dict", "@hero_{reg21}_imd{reg20}", ":imod"),
          (try_end),

        (try_end),

      (try_end), #end of hero loop


      (try_begin),
        (game_in_multiplayer_mode),
        (assign, ":troop_2", "trp_temp_troop"),
      (else_try),
        (assign, ":troop_2", "trp_player"),
        (store_skill_level, ":skill_level_leadership_var_1", "skl_inventory_management", ":troop_2"),
        (dict_set_int, "$coop_dict", "@player_inv_mgt", ":skill_level_leadership_var_1"),
      (try_end),
      (troop_get_inventory_capacity, ":end", ":troop_2"),
      (val_add,":end", 1), 
      (try_for_range, reg20, 10, ":end"),
        (troop_get_inventory_slot, ":item", ":troop_2", reg20),
        (troop_get_inventory_slot_modifier, ":imod", ":troop_2", reg20),
        (dict_set_int, "$coop_dict", "@party_inv{reg20}_itm", ":item"),
        (dict_set_int, "$coop_dict", "@party_inv{reg20}_imd", ":imod"),
        # (troop_inventory_slot_get_item_amount, ":number", ":troop_2", reg20),
        # (dict_set_int, "$coop_dict", "@party_inv{reg20}_num", ":number"),
      (try_end),
    (try_end),
    ]),	 



# SET heroes SKILL/EQUIPMENT 
  # script_coop_copy_file_to_hero
  # Input: arg1 = hero troop
  # Output: none
  ("coop_copy_file_to_hero",
    [
    (try_begin), 
      (neg|is_vanilla_warband),
      (dict_get_int, ":number_heroes", "$coop_dict", "@hero_num"),
      (try_for_range, reg21, 0, ":number_heroes"),
        (dict_get_int, ":troop_2", "$coop_dict", "@hero_{reg21}_trp"),
        (try_begin),
          (neg|game_in_multiplayer_mode),
          (this_or_next|eq, ":troop_2",  "trp_multiplayer_profile_troop_female"),
          (eq, ":troop_2",  "trp_multiplayer_profile_troop_male"),
          (assign, ":troop_2", "trp_player"),  #in SP use player instead of profile
        (try_end),
        # Skip player pool troops -- handled by per-player character dicts
        (neg|is_between, ":troop_2", multiplayer_campaign_player_troops_begin, multiplayer_campaign_player_troops_end),
        (dict_get_int, ":0", "$coop_dict", "@hero_{reg21}_str"),
        (dict_get_int, ":1", "$coop_dict", "@hero_{reg21}_agi"),
        # (dict_get_int, ":2", "$coop_dict", "@hero_{reg21}_int"),
        # (dict_get_int, ":3", "$coop_dict", "@hero_{reg21}_cha"),

        (store_attribute_level, ":value", ":troop_2", 0),
        (val_sub, ":0", ":value"),
        (store_attribute_level, ":value", ":troop_2", 1),
        (val_sub, ":1", ":value"),

        (troop_raise_attribute, ":troop_2", 0, ":0"),
        (troop_raise_attribute, ":troop_2", 1, ":1"),
        # (troop_raise_attribute, ":troop_2", 2, ":2"),
        # (troop_raise_attribute, ":troop_2", 3, ":3"),

        (try_for_range, reg20, "skl_horse_archery", "skl_reserved_14"), #start from "skl_trade" if all skills are needed
          (neg|is_between, reg20, "skl_reserved_9", "skl_power_draw"), #skip these skills
          (dict_get_int, ":skill_level_leadership_var_1", "$coop_dict", "@hero_{reg21}_skl{reg20}"),
          (store_skill_level, ":value", reg20,":troop_2"),
          (val_sub, ":skill_level_leadership_var_1", ":value"),
          (troop_raise_skill, ":troop_2", reg20, ":skill_level_leadership_var_1"),
          # (try_begin), #NEW
            # (eq, reg20, "skl_ironflesh"),
            # (store_mul, ":added_ironflesh", ":skill_level_leadership_var_1", 2), #get number of hit point that will be added when spawning
          # (try_end),
        (try_end),

        (try_for_range, reg20, 0, 7),  #wpt_firearm = 6 
#####PROBABLY BUGGY END

 #       (dict_get_int, ":ca_strength", "$coop_dict", "@hero_{reg21}_str"),                                                                                #DEF
 #       (dict_get_int, ":ca_agility", "$coop_dict", "@hero_{reg21}_agi"),                                                                                 #DEF
 #       # (dict_get_int, ":ca_intelligence", "$coop_dict", "@hero_{reg21}_int"),                                                                          #DEF
 #       # (dict_get_int, ":ca_charisma", "$coop_dict", "@hero_{reg21}_cha"),                                                                              #DEF
 #                                                                                                                                                         #DEF
 #       (store_attribute_level, ":value", ":troop_2", ca_strength),                                                                                       #DEF
 #       (val_sub, ":ca_strength", ":value"),                                                                                                              #DEF
 #       (store_attribute_level, ":value", ":troop_2", ca_agility),                                                                                        #DEF
 #       (val_sub, ":ca_agility", ":value"),                                                                                                               #DEF
 #                                                                                                                                                         #DEF
 #       (troop_raise_attribute, ":troop_2", ca_strength, ":ca_strength"),                                                                                 #DEF
 #       (troop_raise_attribute, ":troop_2", ca_agility, ":ca_agility"),                                                                                   #DEF
 #       # (troop_raise_attribute, ":troop_2", ca_intelligence, ":ca_intelligence"),                                                                       #DEF
 #       # (troop_raise_attribute, ":troop_2", ca_charisma, ":ca_charisma"),                                                                               #DEF
 #                                                                                                                                                         #DEF
 #       (try_for_range, reg20, "skl_horse_archery", "skl_reserved_14"), #start from "skl_trade" if all skills are needed                                  #DEF
 #         (neg|is_between, reg20, "skl_reserved_9", "skl_power_draw"), #skip these skills                                                                 #DEF
 #         (dict_get_int, ":skill_level_leadership_var_1", "$coop_dict", "@hero_{reg21}_skl{reg20}"),                                                      #DEF
 #         (store_skill_level, ":value", reg20,":troop_2"),                                                                                                #DEF
 #         (val_sub, ":skill_level_leadership_var_1", ":value"),                                                                                           #DEF
 #         (troop_raise_skill, ":troop_2", reg20, ":skill_level_leadership_var_1"),                                                                        #DEF
 #         # (try_begin), #NEW                                                                                                                             #DEF
 #           # (eq, reg20, "skl_ironflesh"),                                                                                                               #DEF
 #           # (store_mul, ":added_ironflesh", ":skill_level_leadership_var_1", 2), #get number of hit point that will be added when spawning              #DEF
 #         # (try_end),                                                                                                                                    #DEF
 #       (try_end),                                                                                                                                        #DEF
 #                                                                                                                                                         #DEF
 #       (try_for_range, reg20, wpt_one_handed_weapon, 7),  #wpt_firearm = 6                                                                               #DEF
          (dict_get_int, ":wprof", "$coop_dict", "@hero_{reg21}_wp{reg20}"),
          (store_proficiency_level, ":value", ":troop_2", reg20),
          (val_sub, ":wprof", ":value"),
          (troop_raise_proficiency_linear, ":troop_2", reg20, ":wprof"),
        (try_end),

        (try_begin),
          (neg|is_between, ":troop_2", kings_begin, pretenders_end), #need this so we dont equip lords with civilian clothes in battle
          (dict_get_str, s0, "$coop_dict", "@hero_{reg21}_name"),
          (try_begin),
            (str_is_empty, s0),
            (str_store_string, s0, "@Player"), #set default name
          (try_end),
          (troop_set_name, ":troop_2", s0),
      
          (try_begin),#only copy inventory to SP when optional
            (this_or_next|game_in_multiplayer_mode), 
            (eq, "$coop_disable_inventory", 0),
            (try_for_range, reg20, ek_item_0, ek_food), 
              (dict_get_int, ":item", "$coop_dict", "@hero_{reg21}_itm{reg20}"),
              (dict_get_int, ":imod", "$coop_dict", "@hero_{reg21}_imd{reg20}"),
              (troop_set_inventory_slot, ":troop_2", reg20, ":item"),
              (troop_set_inventory_slot_modifier, ":troop_2", reg20, ":imod"),
            (try_end),
          (try_end),
        (try_end),
#NEW
        (try_begin),#only set face in MP
          (game_in_multiplayer_mode),
          (dict_get_str, s0, "$coop_dict", "@hero_{reg21}_face"),
          (face_keys_store_string, reg1, s0),
          #ENVFIX(troop_set_face_keys, ":troop_2", reg1),
        (try_end),

        # Companion-hero battle XP: on the live coop battle-results path this
        # is already delivered SP-style by the pool share (party_add_xp in
        # coop_apply_xp_shares), so re-applying the engine's per-kill hero XP
        # here would double-count. coop_apply_battle_results sets the skip
        # flag; the legacy admin-panel restore paths leave it 0 and still get
        # XP from the dict as their sole source.
        (try_begin),
          (neq, "$g_coop_skip_hero_xp_restore", 1),
          (dict_get_int, ":xp", "$coop_dict", "@hero_{reg21}_xp"),
          (call_script, "script_coop_copy_register_to_hero_xp", ":troop_2", ":xp"),
        (try_end),

        (dict_get_int, ":battle_health", "$coop_dict", "@hero_{reg21}_hp"),
        (try_begin),#set health after attributes
          (neg|game_in_multiplayer_mode),
          (main_party_has_troop, ":troop_2"),
          (party_get_skill_level, ":player_party_first_aid", "p_main_party", "skl_first_aid"), #currently we get medic skill before wounding heroes
          (val_mul, ":player_party_first_aid", 5),  #5% per skill level
          (store_troop_health, ":old_health", ":troop_2"),
          (store_sub, ":lost_health", ":old_health",":battle_health"),
          (val_max, ":lost_health", 0), # if <0 we would gain health
          (val_mul, ":lost_health", ":player_party_first_aid"),
          (val_div, ":lost_health", 100),
          (val_add, ":battle_health", ":lost_health"), #add recovered percentage
          (troop_set_health, ":troop_2", ":battle_health"),
        (else_try),
          #NEW not getting this bug anymore 
          #  when setup MP: ironflesh will add alive hitpoint later when troop spawns, so find what % troop should be now to compensate
          # (troop_set_health, ":troop_2", ":battle_health"), 
          # (store_mul, ":hp_x10", ":battle_health",10), 
          # (store_troop_health, ":hp", ":troop_2",1),
          # (val_max, ":hp", 1),
          # (val_div, ":hp_x10", ":hp"), 
          # (val_mul, ":hp_x10", ":added_ironflesh"), 
          # (val_div, ":hp_x10", 10), 
          # (val_sub, ":battle_health", ":hp_x10"), 
          (troop_set_health, ":troop_2", ":battle_health"), 
        (try_end),

        #use this if needed
        # (try_begin),
          # (dict_get_int, ":new_gold", "$coop_dict", "@hero_{reg21}_gld"),
          # (store_troop_gold, ":cur_gold", ":troop_2"), 
          # (gt, ":new_gold", ":cur_gold"),
          # (val_sub, ":new_gold", ":cur_gold"),
          # (troop_add_gold,":troop_2",":new_gold"),
        # (try_end),

      (try_end), #end of hero loop

    
      (try_begin),
        (this_or_next|game_in_multiplayer_mode), 
        (eq, "$coop_disable_inventory", 0),  #inventory is optional
        (try_begin),
          (game_in_multiplayer_mode),
          (assign, ":troop_2", "trp_temp_troop"),
          (dict_get_int, ":skill_level_leadership_var_1", "$coop_dict", "@player_inv_mgt"),
          (store_skill_level, ":value", "skl_inventory_management",":troop_2"),
          (val_sub, ":skill_level_leadership_var_1", ":value"),
          (troop_raise_skill, ":troop_2", "skl_inventory_management", ":skill_level_leadership_var_1"),
        (else_try),
          (assign, ":troop_2", "trp_player"),
        (try_end),
        (troop_get_inventory_capacity, ":end", ":troop_2"),
        (val_add,":end", 1), 
        (try_for_range, reg20, 10, ":end"),
          (dict_get_int, ":item", "$coop_dict", "@party_inv{reg20}_itm"),
          (dict_get_int, ":imod", "$coop_dict", "@party_inv{reg20}_imd"),

          (assign, ":skip",0),
          (try_begin),
            (neg|game_in_multiplayer_mode),
            (is_between, ":item", trade_goods_begin, trade_goods_end), #these items would need to copy correct quantity still need to copy to MP to take up inv capacity 
            (assign, ":skip",1),
          (try_end),

          (eq, ":skip",0),
          (troop_set_inventory_slot, ":troop_2", reg20, ":item"),
          (troop_set_inventory_slot_modifier, ":troop_2", reg20, ":imod"),

          # (dict_get_int, ":number", "$coop_dict", "@party_inv{reg20}_num"),
          # (try_begin),
            # (gt, ":number", 0), 
            # (troop_inventory_slot_set_item_amount, ":troop_2", reg20, ":number"),
          # (try_end),

        (try_end),
      (try_end),

    (try_end),
    ]),	 

##Doghotel begin
#  ("doghotel_initialize_bot_globals",
#  [
#    (store_script_param, ":var0", 1),
#    (assign, "$g_doghotel_batch_offset", 0),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_enable_brainy_bots", 0),
#      (assign, "$g_doghotel_enable_brainy_bots", 1),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_movement_actions_enabled", 0),
#      (assign, "$g_doghotel_movement_actions_enabled", 1),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_batch_size", 0),
#      (assign, "$g_doghotel_batch_size", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_nearby_enemy_radius", 0),
#      (assign, "$g_doghotel_nearby_enemy_radius", 1000),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_nearby_neutral_radius", 0),
#      (assign, "$g_doghotel_nearby_neutral_radius", 5000),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_nearby_ally_radius", 0),
#      (assign, "$g_doghotel_nearby_ally_radius", 5000),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_block_chance", 0),
#      (assign, "$g_doghotel_min_block_chance", 70),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_block_chance", 0),
#      (assign, "$g_doghotel_max_block_chance", 90),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_hold_chance", 0),
#      (assign, "$g_doghotel_min_hold_chance", 20),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_hold_chance", 0),
#      (assign, "$g_doghotel_max_hold_chance", 40),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_feint_chance", 0),
#      (assign, "$g_doghotel_min_feint_chance", 20),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_feint_chance", 0),
#      (assign, "$g_doghotel_max_feint_chance", 40),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_chamber_chance", 0),
#      (assign, "$g_doghotel_min_chamber_chance", 15),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_chamber_chance", 0),
#      (assign, "$g_doghotel_max_chamber_chance", 25),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_weapon_prof", 0),
#      (assign, "$g_doghotel_min_weapon_prof", 100),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_weapon_prof", 0),
#      (assign, "$g_doghotel_max_weapon_prof", 200),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_hold_msec", 0),
#      (assign, "$g_doghotel_min_hold_msec", 250),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_hold_msec", 0),
#      (assign, "$g_doghotel_max_hold_msec", 750),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_consecutive_feints", 0),
#      (assign, "$g_doghotel_max_consecutive_feints", 2),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_poor_block_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_poor_block_reduction", 20),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_poor_hold_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_poor_hold_reduction", 10),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_poor_feint_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_poor_feint_reduction", 10),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_poor_chamber_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_poor_chamber_reduction", 10),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_average_block_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_average_block_reduction", 10),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_average_hold_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_average_hold_reduction", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_average_feint_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_average_feint_reduction", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_ai_average_chamber_reduction", 0),
#      (assign, "$g_doghotel_combat_ai_average_chamber_reduction", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_renown_block_bonus", 0),
#      (assign, "$g_doghotel_renown_block_bonus", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_renown_feint_bonus", 0),
#      (assign, "$g_doghotel_renown_feint_bonus", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_renown_hold_bonus", 0),
#      (assign, "$g_doghotel_renown_hold_bonus", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_renown_chamber_bonus", 0),
#      (assign, "$g_doghotel_renown_chamber_bonus", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_renown_min", 0),
#      (assign, "$g_doghotel_renown_min", 100),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_combat_difficulty", 0),
#      (assign, "$g_doghotel_combat_difficulty", 1),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_anti_autoblock", 0),
#      (assign, "$g_doghotel_anti_autoblock", 1),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_enable_only_for_heroes", 0),
#      (assign, "$g_doghotel_enable_only_for_heroes", 0),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_version_id_netcode", 0),
#      (assign, "$g_doghotel_version_id_netcode", 2),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_version_id", 0),
#      (assign, "$g_doghotel_version_id", 3),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_min_kick_chance", 0),
#      (assign, "$g_doghotel_min_kick_chance", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_max_kick_chance", 0),
#      (assign, "$g_doghotel_max_kick_chance", 20),
#    (try_end),
#  ]),
#
#  ("doghotel_initialize_mp_globals",
#  [
#    (store_script_param, ":var0", 1),
#    (try_begin),
#      (multiplayer_is_server),
#      (assign, "$g_doghotel_multiplayer_brainy_bots_installed_on_server", 1),
#    (else_try),
#      (assign, "$g_doghotel_multiplayer_brainy_bots_installed_on_server", 0),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_ping_limit", 0),
#      (assign, "$g_doghotel_ping_limit", 200),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_stop_test_server_timer", 0),
#      (assign, "$g_doghotel_stop_test_server_timer", 0),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_stop_test_server_after", 0),
#      (assign, "$g_doghotel_stop_test_server_after", 5),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_brainy_message_interval", 0),
#      (assign, "$g_doghotel_brainy_message_interval", 600),
#    (try_end),
#    (try_begin),
#      (this_or_next|eq, ":var0", 1),
#      (eq, "$g_doghotel_duel_add_bots", 0),
#      (assign, "$g_doghotel_duel_add_bots", 1),
#    (try_end),
#  ]),
#
#  ("doghotel_item_get_wpt",
#  [
#    (store_script_param, ":var0", 1),
#    (try_begin),
#      (ge, ":var0", 0),
#      (item_get_type, ":var1", ":var0"),
#    (else_try),
#      (assign, ":var1", 0),
#    (try_end),
#    (try_begin),
#      (eq, ":var1", 2),
#      (assign, reg0, 0),
#    (else_try),
#      (eq, ":var1", 3),
#      (assign, reg0, 1),
#    (else_try),
#      (eq, ":var1", 4),
#      (assign, reg0, 2),
#    (else_try),
#      (this_or_next|eq, ":var1", 8),
#      (eq, ":var1", 5),
#      (assign, reg0, 3),
#    (else_try),
#      (this_or_next|eq, ":var1", 9),
#      (eq, ":var1", 6),
#      (assign, reg0, 4),
#    (else_try),
#      (eq, ":var1", 10),
#      (assign, reg0, 5),
#    (else_try),
#      (this_or_next|eq, ":var1", 16),
#      (this_or_next|eq, ":var1", 17),
#      (eq, ":var1", 18),
#      (assign, reg0, 6),
#    (try_end),
#  ]),
#
#  ("doghotel_reset_bots",
#  [
#    (try_for_agents, ":var0"),
#      (agent_is_active, ":var0"),
#      (agent_is_non_player, ":var0"),
#      (agent_is_human, ":var0"),
#      (agent_is_alive, ":var0"),
#      (agent_set_attack_action, ":var0", -2, 0),
#      (agent_set_attack_action, ":var0", -2, 1),
#      (agent_set_defend_action, ":var0", -2, 1),
#    (try_end),
#  ]),
#
#  ("doghotel_error_message",
#  [
#    (store_script_param, ":var0", 1),
#    (display_message, ":var0", 0x00AB1313),
#    (try_begin),
#      (multiplayer_is_dedicated_server),
#      (server_add_message_to_log, ":var0"),
#    (try_end),
#  ]),
#
#  ("doghotel_kick_agent",
#  [
#    (store_script_param, ":var0", 1),
#    (store_script_param, ":var1", 2),
#    (try_begin),
#      (agent_get_wielded_item, ":var2", ":var0", 0),
#      (eq, ":var2", -1),
#      (agent_get_troop_id, ":var3", ":var0"),
#      (store_attribute_level, ":var4", ":var3", 0),
#      (val_div, ":var4", 3),
#      (val_add, ":var4", 3),
#      (agent_deliver_damage_to_agent_advanced, reg0, ":var0", ":var1", ":var4"),
#    (try_end),
#    (agent_play_sound, ":var0", "snd_blunt_hit"),
#    (agent_set_animation, ":var1", 425),
#  ]),
#
#  ("doghotel_kick_anim",
#  [
#    (store_script_param, ":var0", 1),
#    (agent_set_animation, ":var0", 23),
#  ]),
#
#  ("doghotel_combat_loop",
#  [
#    (store_mission_timer_a_msec, ":var0"),
#    (try_for_agents, ":var1"),
#      (agent_is_active, ":var1"),
#      (agent_is_non_player, ":var1"),
#      (agent_is_human, ":var1"),
#      (agent_is_alive, ":var1"),
#      (agent_get_troop_id, ":var2", ":var1"),
#      (this_or_next|neq, "$g_doghotel_enable_only_for_heroes", 1),
#      (troop_is_hero, ":var2"),
#      (agent_get_slot, ":var3", ":var1", 40),
#      (agent_get_slot, ":var4", ":var1", 36),
#      (agent_get_slot, ":var5", ":var1", 37),
#      (agent_get_attack_action, ":var6", ":var1"),
#      (agent_get_defend_action, ":var7", ":var1"),
#      (agent_get_wielded_item, ":var8", ":var1", 0),
#      (agent_get_wielded_item, ":var9", ":var1", 1),
#      (agent_get_position, pos1, ":var1"),
#      (agent_get_horse, ":var10", ":var1"),
#      (agent_get_slot, ":var11", ":var1", 38),
#      (try_begin),
#        (multiplayer_is_server),
#        (store_skill_level, ":var12", "skl_trainer", ":var2"),
#        (eq, ":var12", 10),
#        (assign, ":var11", 0),
#      (try_end),
#      (try_begin),
#        (ge, ":var8", 0),
#        (item_get_weapon_length, ":var13", ":var8"),
#      (else_try),
#        (assign, ":var13", 100),
#      (try_end),
#      (store_add, ":var14", ":var13", 100),
#      (agent_get_animation, ":var15", ":var1", 0),
#      (agent_get_slot, ":var16", ":var1", 52),
#      (store_sub, ":var17", ":var4", ":var0"),
#      (assign, ":var18", 0),
#      (assign, ":var19", -1),
#      (assign, ":var20", 0),
#      (assign, ":var21", -1),
#      (assign, ":var22", -1),
#      (try_begin),
#        (gt, ":var3", 0),
#        (agent_is_alarmed, ":var1"),
#        (agent_get_troop_id, ":var2", ":var1"),
#        (this_or_next|neq, "$g_doghotel_enable_only_for_heroes", 1),
#        (troop_is_hero, ":var2"),
#        (agent_get_simple_behavior, ":var23", ":var1"),
#        (neq, ":var23", 5),
#        (neq, ":var23", 6),
#        (neq, ":var23", 7),
#        (try_for_range, ":var24", 43, 46),
#          (try_begin),
#            (eq, ":var24", 43),
#            (agent_get_slot, ":var25", ":var1", 43),
#          (else_try),
#            (eq, ":var24", 44),
#            (agent_get_slot, ":var25", ":var1", 44),
#          (else_try),
#            (eq, ":var24", 45),
#            (agent_get_slot, ":var25", ":var1", 45),
#          (else_try),
#            (agent_get_slot, ":var25", ":var1", ":var24"),
#          (try_end),
#          (ge, ":var25", 0),
#          (agent_is_active, ":var25"),
#          (agent_is_human, ":var25"),
#          (agent_is_alive, ":var25"),
#          (agent_get_position, pos2, ":var25"),
#          (agent_get_wielded_item, ":var26", ":var25", 0),
#          (get_distance_between_positions, ":var27", pos1, pos2),
#          (position_transform_position_to_local, pos3, pos1, pos2),
#          (position_get_y, ":var28", pos3),
#          (ge, ":var28", 0),
#          (position_get_rotation_around_z, ":var29", pos3),
#          (set_fixed_point_multiplier, 100),
#          (position_get_x, ":var30", pos3),
#          (assign, ":var31", 150),
#          (try_begin),
#            (ge, ":var26", 0),
#            (item_get_weapon_length, ":var32", ":var26"),
#            (val_add, ":var31", ":var32"),
#          (try_end),
#          (try_begin),
#            (eq, ":var15", 24),
#            (neq, ":var16", 2),
#            (eq, ":var10", -1),
#            (agent_get_horse, ":var33", ":var25"),
#            (eq, ":var33", -1),
#            (copy_position, 4, 2),
#            (position_set_z, pos4, 0),
#            (agent_get_bone_position, pos5, ":var1", 6, 1),
#            (position_get_z, ":var34", pos5),
#            (position_set_z, pos5, 0),
#            (get_distance_between_positions, ":var35", pos4, pos5),
#            (le, ":var35", 30),
#            (agent_get_bone_position, pos6, ":var25", 3, 1),
#            (agent_get_bone_position, pos7, ":var25", 6, 1),
#            (agent_get_bone_position, pos8, ":var25", 9, 1),
#            (position_get_z, ":var36", pos6),
#            (position_get_z, ":var37", pos7),
#            (position_get_z, ":var38", pos8),
#            (assign, ":var39", ":var38"),
#            (assign, ":var40", ":var36"),
#            (val_min, ":var40", ":var37"),
#            (is_between, ":var34", ":var40", ":var39"),
#            (call_script, "script_doghotel_kick_agent", ":var1", ":var25"),
#            (agent_set_slot, ":var1", 36, 0),
#            (agent_set_slot, ":var1", 37, 0),
#            (agent_set_slot, ":var1", 52, 2),
#          (try_end),
#          (try_begin),
#            (neq, ":var18", 6),
#            (try_begin),
#              (eq, ":var16", 1),
#              (eq, ":var10", -1),
#              (le, ":var27", 100),
#              (is_between, ":var30", 0, 10),
#              (neg|is_between, ":var15", 20, 26),
#              (agent_get_animation, ":var41", ":var25", 0),
#              (neg|is_between, ":var41", 20, 24),
#              (agent_get_speed, pos4, ":var25"),
#              (set_fixed_point_multiplier, 100),
#              (position_get_x, ":var42", pos4),
#              (is_between, ":var42", -100, 100),
#              (position_get_y, ":var43", pos4),
#              (ge, ":var43", 0),
#              (assign, ":var18", 6),
#            (try_end),
#            (neq, ":var18", 6),
#            (neq, ":var18", 1),
#            (try_begin),
#              (agent_get_attack_action, ":var44", ":var25"),
#              (eq, ":var44", 2),
#              (neq, ":var6", 2),
#              (le, ":var27", ":var31"),
#              (assign, ":var45", 1),
#              (try_begin),
#                (ge, ":var9", 0),
#                (item_get_type, ":var46", ":var9"),
#                (eq, ":var46", 7),
#              (else_try),
#                (agent_get_slot, ":var47", ":var1", 43),
#                (eq, ":var25", ":var47"),
#              (else_try),
#                (assign, ":var45", 0),
#              (try_end),
#              (try_begin),
#                (agent_is_non_player, ":var25"),
#                (try_begin),
#                  (agent_ai_get_behavior_target, ":var48", ":var25"),
#                  (eq, ":var48", ":var1"),
#                  (is_between, ":var29", 135, 225),
#                (else_try),
#                  (agent_ai_get_look_target, ":var49", ":var25"),
#                  (eq, ":var49", ":var1"),
#                  (is_between, ":var29", 135, 225),
#                (else_try),
#                  (assign, ":var45", 0),
#                (try_end),
#              (else_try),
#                (neg|agent_is_non_player, ":var25"),
#                (is_between, ":var29", 90, 270),
#              (else_try),
#                (assign, ":var45", 0),
#              (try_end),
#              (eq, ":var45", 1),
#              (eq, ":var11", 0),
#              (assign, ":var18", 1),
#              (assign, ":var19", ":var25"),
#            (try_end),
#            (neq, ":var18", 1),
#            (neq, ":var18", 5),
#            (try_begin),
#              (this_or_next|is_between, ":var15", 20, 26),
#              (gt, ":var17", 0),
#              (assign, ":var18", 5),
#              (assign, ":var19", ":var25"),
#            (try_end),
#            (neq, ":var18", 5),
#            (neq, ":var18", 4),
#            (try_begin),
#              (ge, ":var5", 1),
#              (le, ":var27", ":var14"),
#              (assign, ":var18", 4),
#              (assign, ":var19", ":var25"),
#            (try_end),
#            (neq, ":var18", 4),
#            (neq, ":var18", 2),
#            (try_begin),
#              (le, ":var27", ":var14"),
#              (assign, ":var18", 2),
#              (assign, ":var19", ":var25"),
#            (try_end),
#          (try_end),
#          (try_begin),
#            (eq, "$g_doghotel_movement_actions_enabled", 1),
#            (eq, ":var10", -1),
#            (neq, ":var20", 1),
#            (try_begin),
#              (is_between, ":var30", -5, 15),
#              (lt, ":var27", 200),
#              (agent_get_animation, ":var50", ":var25", 0),
#              (is_between, ":var50", 20, 26),
#              (try_begin),
#                (ge, ":var27", 150),
#                (ge, ":var50", 24),
#              (else_try),
#                (ge, ":var27", 150),
#                (set_fixed_point_multiplier, 100),
#                (agent_get_speed, pos4, ":var1"),
#                (position_get_y, ":var51", pos4),
#                (le, ":var51", 50),
#              (else_try),
#                (assign, ":var20", 1),
#                (assign, ":var21", ":var25"),
#              (try_end),
#              (neq, ":var20", 1),
#            (else_try),
#              (eq, ":var18", 1),
#              (ge, ":var26", 0),
#              (item_has_property, ":var26", itp_crush_through),
#              (agent_get_action_dir, ":var52", ":var25"),
#              (eq, ":var52", 3),
#              (is_between, ":var30", -10, 20),
#              (agent_get_wielded_item, ":var53", ":var25", 0),
#              (item_get_weapon_length, ":var54", ":var53"),
#              (store_add, ":var55", ":var54", 150),
#              (lt, ":var27", ":var55"),
#              (try_begin),
#                (neq, ":var16", 1),
#                (agent_set_slot, ":var1", 52, 1),
#              (try_end),
#              (assign, ":var20", 1),
#              (assign, ":var21", ":var25"),
#            (try_end),
#          (try_end),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (ge, ":var19", 0),
#        (agent_get_action_dir, ":var52", ":var19"),
#        (agent_get_wielded_item, ":var26", ":var19", 0),
#      (else_try),
#        (assign, ":var52", -1),
#        (assign, ":var26", -1),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", 6),
#        (call_script, "script_doghotel_kick_anim", ":var1"),
#        (agent_set_slot, ":var1", 52, 0),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", 0),
#        (try_begin),
#          (gt, ":var4", 0),
#          (agent_set_slot, ":var1", 36, 0),
#          (assign, ":var18", -2),
#        (try_end),
#        (try_begin),
#          (gt, ":var5", 0),
#          (agent_set_slot, ":var1", 37, ":var5"),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", 3),
#        (try_begin),
#          (ge, ":var26", 0),
#          (item_get_speed_rating, ":var56", ":var26"),
#        (else_try),
#          (assign, ":var56", 100),
#        (try_end),
#        (try_begin),
#          (ge, ":var56", 95),
#          (store_sub, ":var57", 120, ":var56"),
#          (val_clamp, ":var57", 10, 30),
#          (le, ":var22", ":var57"),
#          (neq, ":var6", 2),
#          (assign, ":var58", -1),
#          (try_begin),
#            (eq, ":var52", 0),
#            (this_or_next|eq, ":var8", -1),
#            (item_has_capability, ":var8", itc_pike|itcf_thrust_onehanded|itcf_thrust_twohanded|itcf_horseback_thrust_onehanded|itcf_thrust_musket),
#            (assign, ":var58", 0),
#          (else_try),
#            (eq, ":var52", 1),
#            (this_or_next|eq, ":var8", -1),
#            (item_has_capability, ":var8", itcf_slashright_onehanded|itcf_slashright_twohanded|itcf_slashright_polearm|itcf_horseback_slashright_onehanded|itcf_horseback_slash_polearm),
#            (assign, ":var58", 2),
#          (else_try),
#            (eq, ":var52", 2),
#            (this_or_next|eq, ":var8", -1),
#            (item_has_capability, ":var8", itcf_slashleft_onehanded|itcf_slashleft_twohanded|itcf_slashleft_polearm|itcf_horseback_slashleft_onehanded|itcf_horseback_slash_polearm),
#            (assign, ":var58", 1),
#          (else_try),
#            (eq, ":var52", 3),
#            (this_or_next|eq, ":var8", -1),
#            (item_has_capability, ":var8", itcf_overswing_onehanded|itcf_overswing_twohanded|itcf_overswing_polearm|itcf_horseback_overswing_right_onehanded|itcf_horseback_overswing_left_onehanded|itcf_overswing_spear|itcf_overswing_musket),
#            (assign, ":var58", 3),
#          (try_end),
#          (ge, ":var58", 0),
#          (agent_set_defend_action, ":var1", -2, 0),
#          (agent_set_defend_action, ":var1", -2, 1),
#          (agent_set_attack_action, ":var1", ":var58", 0),
#        (else_try),
#          (assign, ":var18", 1),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", 1),
#        (assign, ":var45", 0),
#        (try_begin),
#          (eq, ":var8", -1),
#          (eq, ":var26", -1),
#          (assign, ":var45", 1),
#        (else_try),
#          (ge, ":var9", 0),
#          (item_get_type, ":var46", ":var9"),
#          (eq, ":var46", 7),
#          (assign, ":var45", 1),
#        (else_try),
#          (ge, ":var8", 0),
#          (try_begin),
#            (eq, ":var52", 0),
#            (item_has_capability, ":var8", itcf_parry_forward_onehanded|itcf_parry_forward_twohanded|itcf_parry_forward_polearm),
#            (assign, ":var45", 1),
#          (else_try),
#            (eq, ":var52", 1),
#            (item_has_capability, ":var8", itcf_parry_right_onehanded|itcf_parry_right_twohanded|itcf_parry_right_polearm),
#            (assign, ":var45", 1),
#          (else_try),
#            (eq, ":var52", 2),
#            (item_has_capability, ":var8", itcf_parry_left_onehanded|itcf_parry_left_twohanded|itcf_parry_left_polearm),
#            (assign, ":var45", 1),
#          (else_try),
#            (eq, ":var52", 3),
#            (item_has_capability, ":var8", itcf_parry_up_onehanded|itcf_parry_up_twohanded|itcf_parry_up_polearm),
#            (assign, ":var45", 1),
#          (try_end),
#        (try_end),
#        (try_begin),
#          (eq, ":var45", 1),
#          (agent_set_attack_action, ":var1", -2, 0),
#          (try_begin),
#            (this_or_next|eq, ":var52", 0),
#            (eq, ":var52", 3),
#            (agent_set_defend_action, ":var1", ":var52", 1),
#          (else_try),
#            (eq, ":var52", 1),
#            (agent_set_defend_action, ":var1", 2, 1),
#          (else_try),
#            (eq, ":var52", 2),
#            (agent_set_defend_action, ":var1", 1, 1),
#          (try_end),
#        (else_try),
#          (assign, ":var18", 2),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", 4),
#        (try_begin),
#          (eq, ":var6", 1),
#          (agent_set_attack_action, ":var1", -2, 1),
#        (else_try),
#          (agent_set_attack_action, ":var1", -2, 0),
#        (try_end),
#        (try_begin),
#          (eq, ":var7", 2),
#          (agent_set_defend_action, ":var1", 1, 0),
#          (agent_set_defend_action, ":var1", -2, 1),
#          (assign, ":var18", 2),
#          (val_sub, ":var5", 1),
#          (agent_set_slot, ":var1", 37, ":var5"),
#        (else_try),
#          (agent_set_defend_action, ":var1", 3, 1),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (assign, ":var59", -1),
#        (try_begin),
#          (eq, ":var18", 2),
#          (assign, ":var59", 0),
#        (else_try),
#          (eq, ":var18", 5),
#          (assign, ":var59", 1),
#        (try_end),
#        (ge, ":var59", 0),
#        (try_begin),
#          (ge, ":var8", 0),
#          (assign, reg0, -1),
#          (assign, reg1, -1),
#          (assign, reg2, -1),
#          (assign, reg3, -1),
#          (try_begin),
#            (item_has_capability, ":var8", itcf_slashright_onehanded|itcf_slashright_twohanded|itcf_slashright_polearm|itcf_horseback_slashright_onehanded|itcf_horseback_slash_polearm),
#            (assign, reg1, 1),
#          (try_end),
#          (try_begin),
#            (item_has_capability, ":var8", itcf_slashleft_onehanded|itcf_slashleft_twohanded|itcf_slashleft_polearm|itcf_horseback_slashleft_onehanded|itcf_horseback_slash_polearm),
#            (assign, reg2, 2),
#          (try_end),
#          (try_begin),
#            (item_has_capability, ":var8", itcf_overswing_onehanded|itcf_overswing_twohanded|itcf_overswing_polearm|itcf_horseback_overswing_right_onehanded|itcf_horseback_overswing_left_onehanded|itcf_overswing_spear|itcf_overswing_musket),
#            (assign, reg3, 3),
#          (try_end),
#          (try_begin),
#            (item_has_capability, ":var8", itc_pike|itcf_thrust_onehanded|itcf_thrust_twohanded|itcf_horseback_thrust_onehanded|itcf_thrust_musket),
#            (try_begin),
#              (eq, reg1, -1),
#              (eq, reg2, -1),
#              (eq, reg3, -1),
#              (assign, reg0, 0),
#            (else_try),
#              (try_begin),
#                (item_get_type, ":var60", ":var8"),
#                (eq, ":var60", 4),
#                (ge, ":var9", 0),
#                (assign, reg0, 0),
#              (else_try),
#                (agent_get_position, pos2, ":var19"),
#                (get_distance_between_positions, ":var27", pos1, pos2),
#                (this_or_next|gt, ":var27", ":var13"),
#                (gt, ":var27", 200),
#                (assign, reg0, 0),
#              (else_try),
#                (store_random_in_range, ":var61", 1, 4),
#                (eq, ":var61", 1),
#                (assign, reg0, 0),
#              (try_end),
#            (try_end),
#          (try_end),
#        (else_try),
#          (eq, ":var8", -1),
#          (assign, reg0, 0),
#          (assign, reg1, 1),
#          (assign, reg2, 2),
#          (assign, reg3, 3),
#        (try_end),
#        (shuffle_range, 0, 4),
#        (try_begin),
#          (ge, reg0, 0),
#          (agent_set_attack_action, ":var1", reg0, ":var59"),
#        (else_try),
#          (ge, reg1, 0),
#          (agent_set_attack_action, ":var1", reg1, ":var59"),
#        (else_try),
#          (ge, reg2, 0),
#          (agent_set_attack_action, ":var1", reg2, ":var59"),
#        (else_try),
#          (ge, reg3, 0),
#          (agent_set_attack_action, ":var1", reg3, ":var59"),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (eq, ":var18", -2),
#        (agent_set_attack_action, ":var1", -2, 0),
#        (agent_set_attack_action, ":var1", -2, 1),
#        (agent_set_defend_action, ":var1", -2, 1),
#      (try_end),
#      (try_begin),
#        (eq, ":var20", 1),
#        (ge, ":var21", 0),
#        (agent_is_active, ":var21"),
#        (agent_is_human, ":var21"),
#        (agent_is_alive, ":var21"),
#        (copy_position, 4, 1),
#        (position_move_y, pos4, -150, 0),
#        (agent_set_slot, ":var1", 51, 1),
#        (agent_set_scripted_destination, ":var1", pos4, 1),
#      (try_end),
#      (try_begin),
#        (eq, ":var20", 0),
#        (agent_get_slot, ":var62", ":var1", 51),
#        (gt, ":var62", 0),
#        (agent_is_in_special_mode, ":var1"),
#        (agent_clear_scripted_mode, ":var1"),
#        (agent_force_rethink, ":var1"),
#        (agent_set_slot, ":var1", 51, 0),
#      (try_end),
#    (try_end),
#  ]),
#
#  ("doghotel_special_actions",
#  [
#    (store_mission_timer_a_msec, ":var0"),
#    (options_get_combat_ai, ":var1"),
#    (try_begin),
#      (eq, ":var1", 2),
#      (assign, ":var2", "$g_doghotel_combat_ai_poor_block_reduction"),
#      (assign, ":var3", "$g_doghotel_combat_ai_poor_hold_reduction"),
#      (assign, ":var4", "$g_doghotel_combat_ai_poor_feint_reduction"),
#      (assign, ":var5", "$g_doghotel_combat_ai_poor_chamber_reduction"),
#    (else_try),
#      (eq, ":var1", 1),
#      (assign, ":var2", "$g_doghotel_combat_ai_average_block_reduction"),
#      (assign, ":var3", "$g_doghotel_combat_ai_average_hold_reduction"),
#      (assign, ":var4", "$g_doghotel_combat_ai_average_feint_reduction"),
#      (assign, ":var5", "$g_doghotel_combat_ai_average_chamber_reduction"),
#    (else_try),
#      (assign, ":var2", 0),
#      (assign, ":var3", 0),
#      (assign, ":var4", 0),
#      (assign, ":var5", 0),
#    (try_end),
#    (try_for_agents, ":var6"),
#      (agent_is_non_player, ":var6"),
#      (agent_is_human, ":var6"),
#      (agent_is_alive, ":var6"),
#      (agent_is_alarmed, ":var6"),
#      (agent_get_troop_id, ":var7", ":var6"),
#      (this_or_next|neq, "$g_doghotel_enable_only_for_heroes", 1),
#      (troop_is_hero, ":var7"),
#      (agent_get_simple_behavior, ":var8", ":var6"),
#      (neq, ":var8", 5),
#      (neq, ":var8", 6),
#      (neq, ":var8", 7),
#      (agent_get_slot, ":var9", ":var6", 40),
#      (gt, ":var9", 0),
#      (agent_get_animation, ":var10", ":var6", 0),
#      (neg|is_between, ":var10", 20, 26),
#      (agent_get_horse, ":var11", ":var6"),
#      (agent_get_wielded_item, ":var12", ":var6", 0),
#      (agent_get_wielded_item, ":var13", ":var6", 1),
#      (call_script, "script_doghotel_item_get_wpt", ":var12"),
#      (assign, ":var14", 0),
#      (assign, ":var15", 0),
#      (assign, ":var16", 0),
#      (assign, ":var17", 0),
#      (try_begin),
#        (troop_get_slot, ":var18", ":var7", 7),
#        (ge, ":var18", "$g_doghotel_renown_min"),
#        (val_add, ":var14", "$g_doghotel_renown_block_bonus"),
#        (val_add, ":var15", "$g_doghotel_renown_feint_bonus"),
#        (val_add, ":var16", "$g_doghotel_renown_hold_bonus"),
#        (val_add, ":var17", "$g_doghotel_renown_chamber_bonus"),
#      (try_end),
#      (try_begin),
#        (ge, ":var7", 0),
#        (store_proficiency_level, ":var19", ":var7", reg0),
#      (else_try),
#        (assign, ":var19", "$g_doghotel_min_weapon_prof"),
#      (try_end),
#      (val_clamp, ":var19", "$g_doghotel_min_weapon_prof", "$g_doghotel_max_weapon_prof"),
#      (store_sub, ":var20", ":var19", "$g_doghotel_min_weapon_prof"),
#      (try_begin),
#        (ge, ":var12", 0),
#        (item_has_property, ":var12", itp_crush_through),
#        (val_sub, ":var20", 30),
#      (try_end),
#      (val_min, ":var20", 1),
#      (try_begin),
#        (eq, ":var11", -1),
#        (neg|is_between, ":var10", 20, 26),
#        (agent_get_slot, ":var21", ":var6", 52),
#        (neq, ":var21", 1),
#        (store_sub, ":var22", "$g_doghotel_max_kick_chance", "$g_doghotel_min_kick_chance"),
#        (val_clamp, ":var22", 1, 100),
#        (store_div, ":var23", 100, ":var22"),
#        (store_div, ":var24", ":var20", ":var23"),
#        (val_add, ":var24", "$g_doghotel_min_kick_chance"),
#        (try_begin),
#          (eq, ":var12", -1),
#          (val_mul, ":var24", 2),
#        (else_try),
#          (ge, ":var13", 0),
#          (val_div, ":var24", 2),
#        (else_try),
#          (neg|item_has_capability, ":var12", itc_parry_polearm|itcf_parry_forward_onehanded|itcf_parry_up_onehanded|itcf_parry_right_onehanded|itcf_parry_left_onehanded|itcf_parry_forward_twohanded|itcf_parry_up_twohanded|itcf_parry_right_twohanded|itcf_parry_left_twohanded),
#          (val_mul, ":var24", 2),
#        (try_end),
#        (store_random_in_range, ":var25", 0, 100),
#        (ge, ":var24", ":var25"),
#        (agent_set_slot, ":var6", 52, 1),
#      (try_end),
#      (try_begin),
#        (eq, ":var11", -1),
#        (ge, ":var12", 0),
#        (agent_get_slot, ":var26", ":var6", 35),
#        (le, ":var26", 0),
#        (item_has_capability, ":var12", itc_parry_polearm|itcf_parry_forward_onehanded|itcf_parry_up_onehanded|itcf_parry_right_onehanded|itcf_parry_left_onehanded|itcf_parry_forward_twohanded|itcf_parry_up_twohanded|itcf_parry_right_twohanded|itcf_parry_left_twohanded),
#        (store_sub, ":var27", "$g_doghotel_max_chamber_chance", "$g_doghotel_min_chamber_chance"),
#        (val_clamp, ":var27", 1, 100),
#        (store_div, ":var23", 100, ":var27"),
#        (store_div, ":var24", ":var20", ":var23"),
#        (val_add, ":var24", "$g_doghotel_min_chamber_chance"),
#        (val_add, ":var24", ":var17"),
#        (val_sub, ":var24", ":var5"),
#        (store_random_in_range, ":var25", 0, 100),
#        (ge, ":var24", ":var25"),
#        (agent_set_slot, ":var6", 35, 1),
#      (try_end),
#      (try_begin),
#        (this_or_next|eq, ":var12", -1),
#        (this_or_next|item_has_capability, ":var12", itc_parry_polearm|itcf_parry_forward_onehanded|itcf_parry_up_onehanded|itcf_parry_right_onehanded|itcf_parry_left_onehanded|itcf_parry_forward_twohanded|itcf_parry_up_twohanded|itcf_parry_right_twohanded|itcf_parry_left_twohanded),
#        (ge, ":var13", 0),
#        (store_sub, ":var27", "$g_doghotel_max_block_chance", "$g_doghotel_min_block_chance"),
#        (val_clamp, ":var27", 1, 100),
#        (store_div, ":var23", 100, ":var27"),
#        (store_div, ":var24", ":var20", ":var23"),
#        (val_add, ":var24", "$g_doghotel_min_block_chance"),
#        (val_add, ":var24", ":var14"),
#        (val_sub, ":var24", ":var2"),
#        (store_random_in_range, ":var25", 0, 100),
#        (ge, ":var24", ":var25"),
#        (agent_set_slot, ":var6", 38, 0),
#      (else_try),
#        (agent_set_slot, ":var6", 38, 1),
#      (try_end),
#      (try_begin),
#        (this_or_next|eq, ":var12", -1),
#        (this_or_next|item_has_capability, ":var12", itc_parry_polearm|itcf_parry_forward_onehanded|itcf_parry_up_onehanded|itcf_parry_right_onehanded|itcf_parry_left_onehanded|itcf_parry_forward_twohanded|itcf_parry_up_twohanded|itcf_parry_right_twohanded|itcf_parry_left_twohanded),
#        (ge, ":var13", 0),
#        (eq, ":var11", -1),
#        (agent_get_slot, ":var28", ":var6", 36),
#        (store_sub, ":var29", ":var28", ":var0"),
#        (this_or_next|le, ":var28", ":var0"),
#        (neg|is_between, ":var29", 0, "$g_doghotel_max_hold_msec"),
#        (store_sub, ":var27", "$g_doghotel_max_hold_chance", "$g_doghotel_min_hold_chance"),
#        (val_clamp, ":var27", 1, 100),
#        (store_div, ":var23", 100, ":var27"),
#        (store_div, ":var24", ":var20", ":var23"),
#        (val_add, ":var24", "$g_doghotel_min_hold_chance"),
#        (val_add, ":var24", ":var16"),
#        (val_sub, ":var24", ":var3"),
#        (try_begin),
#          (eq, ":var12", -1),
#          (val_div, ":var24", 2),
#        (try_end),
#        (store_random_in_range, ":var25", 0, 100),
#        (try_begin),
#          (ge, ":var24", ":var25"),
#          (try_begin),
#            (ge, "$g_doghotel_min_hold_msec", "$g_doghotel_max_hold_msec"),
#            (assign, ":var30", "$g_doghotel_min_hold_msec"),
#          (else_try),
#            (store_random_in_range, ":var30", "$g_doghotel_min_hold_msec", "$g_doghotel_max_hold_msec"),
#          (try_end),
#          (store_add, ":var31", ":var0", ":var30"),
#          (agent_set_slot, ":var6", 36, ":var31"),
#        (else_try),
#          (agent_set_slot, ":var6", 36, 0),
#        (try_end),
#      (try_end),
#      (try_begin),
#        (eq, ":var11", -1),
#        (this_or_next|eq, ":var12", -1),
#        (item_has_capability, ":var12", itc_parry_polearm|itcf_parry_forward_onehanded|itcf_parry_up_onehanded|itcf_parry_right_onehanded|itcf_parry_left_onehanded|itcf_parry_forward_twohanded|itcf_parry_up_twohanded|itcf_parry_right_twohanded|itcf_parry_left_twohanded),
#        (agent_get_slot, ":var32", ":var6", 37),
#        (le, ":var32", "$g_doghotel_max_consecutive_feints"),
#        (store_sub, ":var27", "$g_doghotel_max_feint_chance", "$g_doghotel_min_feint_chance"),
#        (val_clamp, ":var27", 1, 100),
#        (store_div, ":var23", 100, ":var27"),
#        (store_div, ":var24", ":var20", ":var23"),
#        (val_add, ":var24", "$g_doghotel_min_feint_chance"),
#        (val_add, ":var24", ":var15"),
#        (val_sub, ":var24", ":var4"),
#        (try_begin),
#          (eq, ":var12", -1),
#          (val_div, ":var24", 2),
#        (try_end),
#        (store_random_in_range, ":var25", 0, 100),
#        (ge, ":var24", ":var25"),
#        (val_add, ":var32", 1),
#        (agent_set_slot, ":var6", 37, ":var32"),
#      (try_end),
#    (try_end),
#  ]),
#
#  ("doghotel_distance_calculations",
#  [
#    (assign, ":var0", 0),
#    (assign, ":var1", 0),
#    (store_add, ":var2", "$g_doghotel_batch_offset", "$g_doghotel_batch_size"),
#    (try_for_agents, ":var3"),
#      (val_add, ":var0", 1),
#      (is_between, ":var0", "$g_doghotel_batch_offset", ":var2"),
#      (val_add, ":var1", 1),
#      (agent_is_active, ":var3"),
#      (agent_is_non_player, ":var3"),
#      (agent_is_human, ":var3"),
#      (agent_is_alive, ":var3"),
#      (agent_is_alarmed, ":var3"),
#      (agent_get_troop_id, ":var4", ":var3"),
#      (this_or_next|neq, "$g_doghotel_enable_only_for_heroes", 1),
#      (troop_is_hero, ":var4"),
#      (agent_get_position, pos1, ":var3"),
#      (assign, ":var5", 0),
#      (assign, ":var6", 0),
#      (assign, ":var7", -1),
#      (assign, ":var8", "$g_doghotel_nearby_enemy_radius"),
#      (assign, ":var9", -1),
#      (assign, ":var10", "$g_doghotel_nearby_enemy_radius"),
#      (assign, ":var11", -1),
#      (assign, ":var12", "$g_doghotel_nearby_enemy_radius"),
#      (assign, ":var13", -1),
#      (assign, ":var14", "$g_doghotel_nearby_neutral_radius"),
#      (assign, ":var15", -1),
#      (try_begin),
#        (agent_get_simple_behavior, ":var16", ":var3"),
#        (neq, ":var16", 5),
#        (neq, ":var16", 6),
#        (neq, ":var16", 7),
#        (try_begin),
#          (agent_ai_get_behavior_target, ":var17", ":var3"),
#          (ge, ":var17", 0),
#          (agent_is_active, ":var17"),
#          (agent_is_human, ":var17"),
#          (agent_is_alive, ":var17"),
#          (agent_get_position, pos2, ":var17"),
#          (get_distance_between_positions, ":var18", pos1, pos2),
#          (lt, ":var18", "$g_doghotel_nearby_enemy_radius"),
#          (assign, ":var15", ":var17"),
#        (else_try),
#          (agent_get_slot, ":var19", ":var3", 21),
#          (ge, ":var19", 0),
#          (agent_is_active, ":var19"),
#          (agent_is_human, ":var19"),
#          (agent_is_alive, ":var19"),
#          (assign, ":var15", ":var19"),
#        (try_end),
#      (try_end),
#      (agent_get_team, ":var20", ":var3"),
#      (try_for_agents, ":var21"),
#        (neq, ":var3", ":var21"),
#        (agent_is_human, ":var21"),
#        (agent_is_alive, ":var21"),
#        (assign, ":var22", 1),
#        (try_begin),
#          (multiplayer_is_server),
#          (eq, "$g_multiplayer_game_type", 0),
#          (assign, ":var22", 1),
#        (else_try),
#          (eq, ":var21", ":var15"),
#          (assign, ":var22", 1),
#        (else_try),
#          (agent_get_team, ":var23", ":var21"),
#          (teams_are_enemies, ":var20", ":var23"),
#          (assign, ":var22", 1),
#        (else_try),
#          (assign, ":var22", 0),
#        (try_end),
#        (try_begin),
#          (eq, ":var22", 1),
#          (try_begin),
#            (agent_get_position, pos2, ":var21"),
#            (get_distance_between_positions, ":var18", pos1, pos2),
#            (lt, ":var18", "$g_doghotel_nearby_enemy_radius"),
#            (val_add, ":var5", 1),
#            (lt, ":var18", ":var12"),
#            (position_transform_position_to_local, pos3, pos1, pos2),
#            (position_get_y, ":var24", pos3),
#            (ge, ":var24", 0),
#            (try_begin),
#              (lt, ":var18", ":var8"),
#              (assign, ":var11", ":var9"),
#              (assign, ":var9", ":var7"),
#              (assign, ":var7", ":var21"),
#              (assign, ":var12", ":var10"),
#              (assign, ":var10", ":var8"),
#              (assign, ":var8", ":var18"),
#            (else_try),
#              (lt, ":var18", ":var10"),
#              (assign, ":var11", ":var9"),
#              (assign, ":var9", ":var21"),
#              (assign, ":var12", ":var10"),
#              (assign, ":var10", ":var18"),
#            (else_try),
#              (lt, ":var18", ":var12"),
#              (assign, ":var11", ":var21"),
#              (assign, ":var12", ":var18"),
#            (try_end),
#          (try_end),
#        (try_end),
#        (try_begin),
#          (eq, ":var22", 0),
#          (multiplayer_is_server),
#          (eq, "$g_multiplayer_game_type", 7),
#          (agent_get_slot, ":var25", ":var3", 21),
#          (neq, ":var25", ":var21"),
#          (lt, ":var18", "$g_doghotel_nearby_neutral_radius"),
#          (val_add, ":var6", 1),
#          (lt, ":var18", ":var14"),
#          (try_begin),
#            (lt, ":var18", ":var14"),
#            (assign, ":var13", ":var21"),
#            (assign, ":var14", ":var18"),
#          (try_end),
#        (try_end),
#      (try_end),
#      (agent_set_slot, ":var3", 40, ":var5"),
#      (agent_set_slot, ":var3", 41, ":var6"),
#      (agent_set_slot, ":var3", 43, ":var7"),
#      (agent_set_slot, ":var3", 44, ":var9"),
#      (agent_set_slot, ":var3", 45, ":var11"),
#      (agent_set_slot, ":var3", 47, ":var13"),
#    (try_end),
#    (val_add, "$g_doghotel_batch_offset", ":var1"),
#    (try_begin),
#      (this_or_next|eq, ":var1", 0),
#      (ge, "$g_doghotel_batch_offset", ":var0"),
#      (assign, "$g_doghotel_batch_offset", 0),
#    (try_end),
#  ]),
#
#  ("doghotel_server_message",
#  [
#    (get_max_players, ":var0"),
#    (try_for_range, ":var1", 0, ":var0"),
#      (player_is_active, ":var1"),
#      (multiplayer_send_string_to_player, ":var1", 111, s1),
#    (try_end),
#    (server_add_message_to_log, s1),
#  ]),
#
#  ("doghotel_send_bot_config",
#  [
#    (store_trigger_param_1, ":var0"),
#    (try_begin),
#      (player_is_active, ":var0"),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 0, "$g_doghotel_enable_brainy_bots", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 1, "$g_doghotel_movement_actions_enabled", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 2, "$g_doghotel_batch_size", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 3, "$g_doghotel_nearby_enemy_radius", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 4, "$g_doghotel_nearby_neutral_radius", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 5, "$g_doghotel_nearby_ally_radius", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 6, "$g_doghotel_min_block_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 7, "$g_doghotel_max_block_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 8, "$g_doghotel_min_hold_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 9, "$g_doghotel_max_hold_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 10, "$g_doghotel_min_feint_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 11, "$g_doghotel_max_feint_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 12, "$g_doghotel_min_chamber_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 13, "$g_doghotel_max_chamber_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 14, "$g_doghotel_min_weapon_prof", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 15, "$g_doghotel_max_weapon_prof", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 16, "$g_doghotel_min_hold_msec", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 17, "$g_doghotel_max_hold_msec", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 18, "$g_doghotel_max_consecutive_feints", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 19, "$g_doghotel_combat_ai_poor_block_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 20, "$g_doghotel_combat_ai_poor_hold_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 21, "$g_doghotel_combat_ai_poor_feint_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 22, "$g_doghotel_combat_ai_poor_chamber_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 23, "$g_doghotel_combat_ai_average_block_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 24, "$g_doghotel_combat_ai_average_hold_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 25, "$g_doghotel_combat_ai_average_feint_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 26, "$g_doghotel_combat_ai_average_chamber_reduction", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 27, "$g_doghotel_renown_block_bonus", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 28, "$g_doghotel_renown_feint_bonus", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 29, "$g_doghotel_renown_hold_bonus", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 30, "$g_doghotel_renown_chamber_bonus", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 31, "$g_doghotel_renown_min", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 32, "$g_doghotel_combat_difficulty", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 34, "$g_doghotel_anti_autoblock", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 35, "$g_doghotel_enable_only_for_heroes", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 36, "$g_doghotel_version_id_netcode", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 37, "$g_doghotel_version_id", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 38, "$g_doghotel_min_kick_chance", 4097),
#      (multiplayer_send_3_int_to_player, ":var0", 120, 39, "$g_doghotel_max_kick_chance", 4097),
#    (try_end),
#  ]),
#
#  ("doghotel_configure_close",
#  [
#    (try_begin),
#      (is_presentation_active, "prsnt_doghotel_configure"),
#      (try_begin),
#        (is_between, "$g_doghotel_prsnt_configure_close", 1, 5),
#        (val_add, "$g_doghotel_prsnt_configure_close", 1),
#        (presentation_set_duration, 0),
#      (else_try),
#        (ge, "$g_doghotel_prsnt_configure_close", 5),
#        (call_script, "script_doghotel_error_message", "str_doghotel_unable_to_close_presentation"),
#        (assign, "$g_doghotel_prsnt_configure_close", 0),
#      (try_end),
#    (else_try),
#      (assign, "$g_doghotel_prsnt_configure_close", 0),
#    (try_end),
#  ]),
#  #Doghotel end

  # ------------------------------------------------------------------
  # Battle-dict schema: the roster and casualty key layout
  #   @p_enemy{i}_partyid / _banner / _numstacks      (same for ally)
  #   @p_enemy{i}_{j}_trp / _num                      (same for ally)
  #   @p_enemy{i}_numstacks_cas / @p_ally{i}_numstacks_cas
  #   @p_enemy{i}_{j}_trp_cas / _ded / _wnd           (same for ally)
  #   @p_ally0_{j}_cls  (main-party troop class; single writer/reader pair)
  # is defined HERE and nowhere else. Writers and readers on both the
  # campaign server and the battle server go through the accessor
  # scripts in this section so the spellings cannot drift. The one
  # remaining raw-key site is coop_copy_parties_to_file_sp (the legacy
  # local-battle serializer, which stores real banner meshes and cls
  # keys); tests/test_module_schema.py pins that exception.
  # ------------------------------------------------------------------
  ("coop_battle_dict_put_stack_cas",
    [
      (store_script_param, ":side", 1),        # 0 = enemy, 1 = ally
      (store_script_param, reg20, 2),           # party index
      (store_script_param, reg21, 3),           # stack index
      (store_script_param, ":troop_id", 4),
      (store_script_param, ":dead", 5),
      (store_script_param, ":wounded", 6),
      (try_begin),
        (eq, ":side", 0),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_{reg21}_trp_cas", ":troop_id"),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_{reg21}_ded", ":dead"),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_{reg21}_wnd", ":wounded"),
      (else_try),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_trp_cas", ":troop_id"),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_ded", ":dead"),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_{reg21}_wnd", ":wounded"),
      (try_end),
    ]),

  ("coop_battle_dict_get_stack_cas",
    [
      (store_script_param, ":side", 1),
      (store_script_param, reg20, 2),
      (store_script_param, reg21, 3),
      (try_begin),
        (eq, ":side", 0),
        (dict_get_int, reg0, "$coop_dict", "@p_enemy{reg20}_{reg21}_trp_cas"),
        (dict_get_int, reg1, "$coop_dict", "@p_enemy{reg20}_{reg21}_ded"),
        (dict_get_int, reg2, "$coop_dict", "@p_enemy{reg20}_{reg21}_wnd"),
      (else_try),
        (dict_get_int, reg0, "$coop_dict", "@p_ally{reg20}_{reg21}_trp_cas"),
        (dict_get_int, reg1, "$coop_dict", "@p_ally{reg20}_{reg21}_ded"),
        (dict_get_int, reg2, "$coop_dict", "@p_ally{reg20}_{reg21}_wnd"),
      (try_end),
    ]),

  # Input: arg1 = side (0 enemy / 1 ally), arg2 = party index, arg3 = count.
  ("coop_battle_dict_put_stack_cas_count",
    [
      (store_script_param, ":side", 1),
      (store_script_param, reg20, 2),
      (store_script_param, ":count", 3),
      (try_begin),
        (eq, ":side", 0),
        (dict_set_int, "$coop_dict", "@p_enemy{reg20}_numstacks_cas", ":count"),
      (else_try),
        (dict_set_int, "$coop_dict", "@p_ally{reg20}_numstacks_cas", ":count"),
      (try_end),
    ]),

  # Input: arg1 = side, arg2 = party index. Output: reg0 = casualty stacks.
  ("coop_battle_dict_get_stack_cas_count",
    [
      (store_script_param, ":side", 1),
      (store_script_param, reg20, 2),
      (try_begin),
        (eq, ":side", 0),
        (dict_get_int, reg0, "$coop_dict", "@p_enemy{reg20}_numstacks_cas"),
      (else_try),
        (dict_get_int, reg0, "$coop_dict", "@p_ally{reg20}_numstacks_cas"),
      (try_end),
    ]),

  # Input: arg1 = side, arg2 = party index. Output: reg0 = 1 if that
  # party has a casualty block in the dict, else 0.
  ("coop_battle_dict_has_stack_cas",
    [
      (store_script_param, ":side", 1),
      (store_script_param, reg20, 2),
      (assign, reg0, 0),
      (try_begin),
        (eq, ":side", 0),
        (dict_has_key, "$coop_dict", "@p_enemy{reg20}_numstacks_cas"),
        (assign, reg0, 1),
      (else_try),
        (eq, ":side", 1),
        (dict_has_key, "$coop_dict", "@p_ally{reg20}_numstacks_cas"),
        (assign, reg0, 1),
      (try_end),
    ]),

  # Read twin of coop_battle_dict_write_roster_party.
  # Input: arg1 = dict, arg2 = side, arg3 = party index.
  # Output: reg0 = party id, reg1 = numstacks, reg2 = banner.
  ("coop_battle_dict_read_roster_party",
    [
      (store_script_param, ":rd_dict", 1),
      (store_script_param, ":side", 2),
      (store_script_param, reg20, 3),
      (try_begin),
        (eq, ":side", 0),
        (dict_get_int, reg0, ":rd_dict", "@p_enemy{reg20}_partyid"),
        (dict_get_int, reg1, ":rd_dict", "@p_enemy{reg20}_numstacks"),
        (dict_get_int, reg2, ":rd_dict", "@p_enemy{reg20}_banner"),
      (else_try),
        (dict_get_int, reg0, ":rd_dict", "@p_ally{reg20}_partyid"),
        (dict_get_int, reg1, ":rd_dict", "@p_ally{reg20}_numstacks"),
        (dict_get_int, reg2, ":rd_dict", "@p_ally{reg20}_banner"),
      (try_end),
    ]),

  # Input: arg1 = dict, arg2 = side, arg3 = party index. Output: reg0 =
  # 1 if the roster entry exists (partyid key present), else 0.
  ("coop_battle_dict_has_roster_party",
    [
      (store_script_param, ":rd_dict", 1),
      (store_script_param, ":side", 2),
      (store_script_param, reg20, 3),
      (assign, reg0, 0),
      (try_begin),
        (eq, ":side", 0),
        (dict_has_key, ":rd_dict", "@p_enemy{reg20}_partyid"),
        (assign, reg0, 1),
      (else_try),
        (eq, ":side", 1),
        (dict_has_key, ":rd_dict", "@p_ally{reg20}_partyid"),
        (assign, reg0, 1),
      (try_end),
    ]),

  # Input: arg1 = dict, arg2 = side, arg3 = party index, arg4 = stack.
  # Output: reg0 = troop id, reg1 = stack size.
  ("coop_battle_dict_read_roster_stack",
    [
      (store_script_param, ":rd_dict", 1),
      (store_script_param, ":side", 2),
      (store_script_param, reg20, 3),
      (store_script_param, reg21, 4),
      (try_begin),
        (eq, ":side", 0),
        (dict_get_int, reg0, ":rd_dict", "@p_enemy{reg20}_{reg21}_trp"),
        (dict_get_int, reg1, ":rd_dict", "@p_enemy{reg20}_{reg21}_num"),
      (else_try),
        (dict_get_int, reg0, ":rd_dict", "@p_ally{reg20}_{reg21}_trp"),
        (dict_get_int, reg1, ":rd_dict", "@p_ally{reg20}_{reg21}_num"),
      (try_end),
    ]),

  # ==================================================================
  # CHARACTER FIELD SYNC
  # A synced character field (attr/skill/prof/points/xp/health/gold)
  # is owned end-to-end by the four scripts in this section:
  #   coop_char_client_diff_and_send  -- client: diff vs snapshot, send raises
  #   coop_char_server_receive        -- server: apply raises + pools
  #   coop_send_char_sync_to_client   -- server: authoritative push
  #   coop_char_client_receive        -- client: apply push + mirror snapshot
  # To add a field: touch these four scripts and the constants. Nothing else.
  # ==================================================================
  ("coop_char_client_diff_and_send",
    [
      (multiplayer_get_my_player, ":my_player"),
      (player_get_troop_id, ":my_troop", ":my_player"),
      # Diff attributes
      (try_for_range, ":i", 0, num_coop_attrs),
          (store_attribute_level, ":cur", ":my_troop", ":i"),
          (store_add, ":slot", slot_coop_char_snap_attr_begin, ":i"),
          (troop_get_slot, ":snap", "trp_temp_troop", ":slot"),
          (gt, ":cur", ":snap"),
          (store_sub, ":delta", ":cur", ":snap"),
          (multiplayer_send_3_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
              multiplayer_event_multiplayer_campaign_raise_attribute, ":i", ":delta"),
      (try_end),
      # Diff skills
      (try_for_range, ":i", 0, num_coop_skills),
          (store_skill_level, ":cur", ":i", ":my_troop"),
          (store_add, ":slot", slot_coop_char_snap_skill_begin, ":i"),
          (troop_get_slot, ":snap", "trp_temp_troop", ":slot"),
          (gt, ":cur", ":snap"),
          (store_sub, ":delta", ":cur", ":snap"),
          (multiplayer_send_3_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
              multiplayer_event_multiplayer_campaign_raise_skill, ":i", ":delta"),
      (try_end),
      # Diff proficiencies
      (try_for_range, ":i", 0, num_coop_profs),
          (store_proficiency_level, ":cur", ":my_troop", ":i"),
          (store_add, ":slot", slot_coop_char_snap_prof_begin, ":i"),
          (troop_get_slot, ":snap", "trp_temp_troop", ":slot"),
          (gt, ":cur", ":snap"),
          (store_sub, ":delta", ":cur", ":snap"),
          (multiplayer_send_3_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
              multiplayer_event_multiplayer_campaign_raise_proficiency, ":i", ":delta"),
      (try_end),
      # Engine-authoritative pools (engine cost formulas are variable;
      # server adopts these as-is -- see project-state.md key lessons)
      (troop_get_attribute_points, ":sync_a", ":my_troop"),
      (troop_get_skill_points, ":sync_s", ":my_troop"),
      (troop_get_proficiency_points, ":sync_p", ":my_troop"),
      (multiplayer_send_4_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
          multiplayer_event_multiplayer_campaign_sync_pools, ":sync_a", ":sync_s", ":sync_p"),
      # Request authoritative push-back
      (multiplayer_send_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
          multiplayer_event_multiplayer_campaign_request_char_sync),
  ]),

  ("coop_char_server_receive",
    [
      (store_script_param, ":player_no", 1),
      (store_script_param, ":event_type", 2),
      # Raise handlers apply the stat change but do NOT charge from
      # point pools -- the client engine already deducted the real cost
      # (which varies by level, weapon_master, etc). The authoritative
      # pool values arrive via sync_pools (event 12) after the raises.
      (try_begin),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_attribute),  # 4
        (store_script_param, ":attr_id", 3),
        (store_script_param, ":count", 4),
        (player_get_troop_id, ":troop_no", ":player_no"),
        (is_between, ":attr_id", 0, 4),
        (gt, ":count", 0),
        (try_for_range, ":unused", 0, ":count"),
            (troop_raise_attribute, ":troop_no", ":attr_id", 1),
        (try_end),
        (player_set_slot, ":player_no", slot_player_coop_char_dirty, 1),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_skill),  # 5
        (store_script_param, ":skill_id", 3),
        (store_script_param, ":count", 4),
        (player_get_troop_id, ":troop_no", ":player_no"),
        (is_between, ":skill_id", 0, 42),
        (gt, ":count", 0),
        (try_for_range, ":unused", 0, ":count"),
            (store_skill_level, ":cur_level", ":skill_id", ":troop_no"),
            (lt, ":cur_level", 10),
            (troop_raise_skill, ":troop_no", ":skill_id", 1),
        (try_end),
        (player_set_slot, ":player_no", slot_player_coop_char_dirty, 1),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_proficiency),  # 6
        (store_script_param, ":prof_id", 3),
        (store_script_param, ":delta", 4),
        (player_get_troop_id, ":troop_no", ":player_no"),
        (is_between, ":prof_id", 0, 7),
        (gt, ":delta", 0),
        (try_for_range, ":unused", 0, ":delta"),
            (troop_raise_proficiency_linear, ":troop_no", ":prof_id", 1),
        (try_end),
        (player_set_slot, ":player_no", slot_player_coop_char_dirty, 1),
      (else_try),
        # Client sends its engine-authoritative pool values after all
        # raise events. Replaces the old per-handler manual charging
        # (which used flat costs that diverged from the engine's real
        # cost formulas -- getProficiencyIncrease at 0x5E4DC0 is
        # variable, AGI grants +5 WP only in the native UI, etc).
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_sync_pools),  # 12
        (store_script_param, ":attr_pts", 3),
        (store_script_param, ":skill_pts", 4),
        (store_script_param, ":prof_pts", 5),
        (player_get_troop_id, ":troop_no", ":player_no"),
        (troop_set_attribute_points, ":troop_no", ":attr_pts"),
        (troop_set_skill_points, ":troop_no", ":skill_pts"),
        (troop_set_proficiency_points, ":troop_no", ":prof_pts"),
        (player_set_slot, ":player_no", slot_player_coop_char_dirty, 1),
      (try_end),
  ]),

  ("coop_send_char_sync_to_client",
    [
      (store_script_param, ":player_no", 1),
      (player_get_troop_id, ":troop_no", ":player_no"),
      # Attributes
      (try_for_range, ":attr", 0, 4),
          (store_attribute_level, ":val", ":troop_no", ":attr"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
              multiplayer_event_multiplayer_campaign_server_event_char_sync_attr, ":attr", ":val"),
      (try_end),
      # Skills -- push all 42 unconditionally so client stale values can't
      # persist when the server value is 0 (matches attrs/profs behavior).
      (try_for_range, ":skl", 0, num_coop_skills),
          (store_skill_level, ":val", ":skl", ":troop_no"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
              multiplayer_event_multiplayer_campaign_server_event_char_sync_skill, ":skl", ":val"),
      (try_end),
      # Proficiencies
      (try_for_range, ":wp", 0, 7),
          (store_proficiency_level, ":val", ":troop_no", ":wp"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
              multiplayer_event_multiplayer_campaign_server_event_char_sync_prof, ":wp", ":val"),
      (try_end),
      # Point pools
      (troop_get_attribute_points, ":attr_pts", ":troop_no"),
      (troop_get_skill_points, ":skill_pts", ":troop_no"),
      (troop_get_proficiency_points, ":prof_pts", ":troop_no"),
      (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
          multiplayer_event_multiplayer_campaign_server_event_char_sync_points, ":attr_pts", ":skill_pts", ":prof_pts"),
      # XP and level (server-authoritative)
      (troop_get_xp, ":xp", ":troop_no"),
      (try_begin),
          (eq, "$g_coop_set_xp_go", 1),
          (eq, "$g_coop_set_xp_troop", ":troop_no"),
          (assign, ":xp", "$g_coop_set_xp_value"),
      (try_end),
      (store_character_level, ":level", ":troop_no"),
      (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
          multiplayer_event_multiplayer_campaign_server_event_char_sync_xp, ":xp", ":level"),
      # Health (server-authoritative; native char window reads troop struct)
      (store_troop_health, ":health", ":troop_no"),
      (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
          multiplayer_event_multiplayer_campaign_server_event_char_sync_health, ":health"),
      # Gold
      (store_troop_gold, ":gold", ":troop_no"),
      (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
          multiplayer_event_multiplayer_campaign_server_event_char_sync_gold, ":gold"),
      # Companion hero XP (server-authoritative). The client's local copy of
      # a companion troop drifts -- engine kill XP during local missions,
      # reset on rejoin -- and nothing else syncs it. Push the target value
      # per hero stack; the client applies a signed delta like ev 21.
      (player_get_party_id, ":party_no", ":player_no"),
      (try_begin),
          (party_is_active, ":party_no"),
          (party_get_num_companion_stacks, ":num_stacks", ":party_no"),
          (try_for_range, ":i", 0, ":num_stacks"),
              (party_stack_get_troop_id, ":stack_troop", ":party_no", ":i"),
              (troop_is_hero, ":stack_troop"),
              (neg|is_between, ":stack_troop", multiplayer_campaign_player_troops_begin, multiplayer_campaign_player_troops_end),
              (troop_get_xp, ":hero_xp", ":stack_troop"),
              (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                  multiplayer_event_multiplayer_campaign_server_event_hero_sync_xp, ":stack_troop", ":hero_xp"),
          (try_end),
      (try_end),
      # Done
      (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
          multiplayer_event_multiplayer_campaign_server_event_char_sync_done, 0),

  ]),

  ("coop_char_client_receive",
    [
      (store_script_param, ":event_type", 1),
      (try_begin),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_attr),  # 16
        (store_script_param, ":attr_id", 2),
        (store_script_param, ":val", 3),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (troop_set_attribute, ":troop_no", ":attr_id", ":val"),
        # Mirror into the diff snapshot so the close-poller baseline is
        # the authoritative server value, not whatever the client troop
        # held at C-screen open time. Prevents false-positive raises
        # from the wse_window_opened / request_char_sync race.
        (store_add, ":snap_slot", slot_coop_char_snap_attr_begin, ":attr_id"),
        (troop_set_slot, "trp_temp_troop", ":snap_slot", ":val"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_skill),  # 17
        (store_script_param, ":skill_id", 2),
        (store_script_param, ":val", 3),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (troop_set_skill, ":troop_no", ":skill_id", ":val"),
        (store_add, ":snap_slot", slot_coop_char_snap_skill_begin, ":skill_id"),
        (troop_set_slot, "trp_temp_troop", ":snap_slot", ":val"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_prof),  # 18
        (store_script_param, ":prof_id", 2),
        (store_script_param, ":val", 3),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        # Write directly to client troop struct (engine doesn't replicate troop profs)
        (troop_set_proficiency, ":troop_no", ":prof_id", ":val"),
        (store_add, ":snap_slot", slot_coop_char_snap_prof_begin, ":prof_id"),
        (troop_set_slot, "trp_temp_troop", ":snap_slot", ":val"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_points),  # 19
        (store_script_param, ":attr_pts", 2),
        (store_script_param, ":skill_pts", 3),
        (store_script_param, ":prof_pts", 4),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (troop_set_attribute_points, ":troop_no", ":attr_pts"),
        (troop_set_skill_points, ":troop_no", ":skill_pts"),
        (troop_set_proficiency_points, ":troop_no", ":prof_pts"),
        (troop_set_slot, "trp_temp_troop", slot_coop_char_snap_attr_pts, ":attr_pts"),
        (troop_set_slot, "trp_temp_troop", slot_coop_char_snap_skill_pts, ":skill_pts"),
        (troop_set_slot, "trp_temp_troop", slot_coop_char_snap_prof_pts, ":prof_pts"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_xp),  # 21
        (store_script_param, ":xp", 2),
        # Param 3 is :level but we don't pull it -- level is derived from XP
        # by the engine, so fixing XP fixes the displayed level automatically.
        # Write authoritative XP into the client troop struct so the native
        # character window displays the correct value. add_xp_to_troop
        # accepts negative deltas (header_operations.py:938), which is how
        # we undo the client engine's local kill-XP inflation on rejoin.
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (troop_get_xp, ":cur_xp", ":troop_no"),
        (store_sub, ":delta_xp", ":xp", ":cur_xp"),
        (try_begin),
            (neq, ":delta_xp", 0),
            (add_xp_to_troop, ":delta_xp", ":troop_no"),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_hero_sync_xp),  # 43
        (store_script_param, ":hero_troop", 2),
        (store_script_param, ":xp", 3),
        # Companion troop XP: same signed-delta apply as ev 21. Level is
        # derived from XP by the engine, so the sheet corrects fully.
        (troop_is_hero, ":hero_troop"),
        (neg|is_between, ":hero_troop", multiplayer_campaign_player_troops_begin, multiplayer_campaign_player_troops_end),
        (troop_get_xp, ":cur_xp", ":hero_troop"),
        (store_sub, ":delta_xp", ":xp", ":cur_xp"),
        (try_begin),
            (neq, ":delta_xp", 0),
            (add_xp_to_troop, ":delta_xp", ":hero_troop"),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_health),  # 24
        (store_script_param, ":health", 2),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (troop_set_health, ":troop_no", ":health"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_done),  # 20
        # Mark the diff snapshot as ready. Close-poller gate checks this
        # flag before firing raise events, so a fast close that races
        # the push simply leaves snap_ready=0 and skips the diff.
        (assign, "$g_coop_char_snap_ready", 1),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_gold),  # 23
        (store_script_param, ":gold_val", 2),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (store_troop_gold, ":cg", ":troop_no"),
        (try_begin), (gt, ":cg", 0), (troop_remove_gold, ":troop_no", ":cg"), (try_end),
        (try_begin), (gt, ":gold_val", 0), (troop_add_gold, ":troop_no", ":gold_val"), (try_end),
      (try_end),
  ]),

  # ==================================================================
  # CLIENT-SIDE GROUP HANDLERS (campaign server->client pushes)
  # Extracted from multiplayer_campaign_server_events so that dispatcher
  # stays a thin router. Signature is (event_type, p2, p3, p4); arms read
  # payload params 2-4 exactly as they did inline.
  # ==================================================================
  ("coop_client_recv_inventory",
    [
      (store_script_param, ":event_type", 1),
      (try_begin),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_inv_bag_slot),  # 25
        (store_script_param, ":slot", 2),
        (store_script_param, ":item", 3),
        (store_script_param, ":imod", 4),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (try_begin),
            (eq, ":slot", -1),
            # Clear signal: wipe all bag slots to remove stale data
            (try_for_range, ":bag_slot", 10, 106),
                (troop_set_inventory_slot, ":troop_no", ":bag_slot", -1),
            (try_end),
        (else_try),
            # Normal: set specific bag slot
            (troop_set_inventory_slot, ":troop_no", ":slot", ":item"),
            (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":imod"),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_inv_sync_done),  # 26
        (assign, "$g_coop_inv_sync_ready", 1),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_center_trade_price),  # 29
        (store_script_param, ":item_offset", 2),
        (store_script_param, ":price_factor", 3),
        # Write trade good price into client's copy of center party
        (store_add, ":price_slot", slot_town_trade_good_prices_begin, ":item_offset"),
        (party_set_slot, "$g_coop_center_party", ":price_slot", ":price_factor"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_merchant_slot),  # 30
        (store_script_param, ":slot", 2),
        (store_script_param, ":item_id", 3),
        (store_script_param, ":imod", 4),
        (try_begin),
            (eq, ":slot", -1),
            # Clear signal: wipe merchant troop inventory
            (troop_clear_inventory, "trp_find_item_cheat"),
        (else_try),
            # Set specific slot on local merchant troop
            (troop_set_inventory_slot, "trp_find_item_cheat", ":slot", ":item_id"),
            (troop_set_inventory_slot_modifier, "trp_find_item_cheat", ":slot", ":imod"),
        (try_end),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_sync_done),  # 31
        # Snapshot merchant inventory into trp_temp_array_b for close-diff
        (try_for_range, ":slot", 0, 96),
            (troop_get_inventory_slot, ":item", "trp_find_item_cheat", ":slot"),
            (troop_get_inventory_slot_modifier, ":imod", "trp_find_item_cheat", ":slot"),
            (store_add, ":snap_item", slot_coop_trade_snap_item_begin, ":slot"),
            (troop_set_slot, "trp_temp_array_b", ":snap_item", ":item"),
            (store_add, ":snap_mod", slot_coop_trade_snap_mod_begin, ":slot"),
            (troop_set_slot, "trp_temp_array_b", ":snap_mod", ":imod"),
        (try_end),
        # Record gold before trade for delta computation
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":my_troop", ":my_player"),
        (store_troop_gold, "$g_coop_trade_gold_before", ":my_troop"),
        # Set trade screen open -- poller diffs on close
        (assign, "$g_coop_trade_screen_open", 1),
        # Set encountered party so native price callbacks work
        (assign, "$g_encountered_party", "$g_coop_center_party"),
        # Player inventory snapshot is handled by wse_window_opened (window_inventory)
        # which fires when change_screen_trade opens the trade window
        (change_screen_trade, "trp_find_item_cheat"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_gold_sync),  # 32
        (store_script_param, ":gold_val", 2),
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (store_troop_gold, ":cg", ":troop_no"),
        (try_begin), (gt, ":cg", 0), (troop_remove_gold, ":troop_no", ":cg"), (try_end),
        (try_begin), (gt, ":gold_val", 0), (troop_add_gold, ":troop_no", ":gold_val"), (try_end),
      (try_end),
  ]),

  ("coop_client_recv_recruit",
    [
      (store_script_param, ":event_type", 1),
      (try_begin),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_recruit_data),  # 33
        (store_script_param, ":troop_id", 2),
        (store_script_param, ":amount", 3),
        (store_script_param, ":cost", 4),
        (assign, "$g_coop_recruit_troop", ":troop_id"),
        (assign, "$g_coop_recruit_amount", ":amount"),
        (assign, "$g_coop_recruit_cost", ":cost"),
        (jump_to_menu, "mnu_coop_recruit_volunteers"),
      (else_try),
        (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_recruit_result),  # 34
        (store_script_param, ":count", 2),
        (store_script_param, ":new_gold", 3),
        # Update client gold
        (multiplayer_get_my_player, ":my_player"),
        (player_get_troop_id, ":troop_no", ":my_player"),
        (store_troop_gold, ":cg", ":troop_no"),
        (try_begin), (gt, ":cg", 0), (troop_remove_gold, ":troop_no", ":cg"), (try_end),
        (try_begin), (gt, ":new_gold", 0), (troop_add_gold, ":troop_no", ":new_gold"), (try_end),
        # Add troops to client party
        (player_get_party_id, ":my_party", ":my_player"),
        (try_begin),
            (gt, ":count", 0),
            (party_add_members, ":my_party", "$g_coop_recruit_troop", ":count"),
            (assign, reg1, ":count"),
            (str_store_troop_name, s1, "$g_coop_recruit_troop"),
            (display_message, "@Recruited {reg1} {s1}.", 0xFF44FF44),
        (else_try),
            (display_message, "@Recruitment failed - not enough gold or no volunteers.", 0xFFFF4444),
        (try_end),
        # Return to center menu
        (jump_to_menu, "mnu_coop_center_encounter"),
      (try_end),
  ]),

  ("coop_client_start_siege_local",
    [
      (store_script_param, ":event_type", 1),
      # Launch the wall assault locally. Mirrors encounter_fight_sp plus
      # the vanilla castle_lead_attack consequence chain. Results flow
      # back through the unchanged debrief + event-17 pipeline.
      (store_script_param, ":wall_scene", 2),
      (store_script_param, ":with_belfry", 3),
      (party_clear, "p_coop_local_player_cas"),
      (party_clear, "p_coop_local_enemy_cas"),
      (assign, "$g_coop_local_cas_recording", 1),
      (assign, "$g_battle_result", 0),
      (assign, "$g_engaged_enemy", 1),
      (assign, "$g_encountered_party", "$g_coop_center_party"),
      (assign, "$current_town", "$g_coop_center_party"),
      (call_script, "script_calculate_renown_value"),
      (call_script, "script_calculate_battle_advantage"),
      (assign, ":battle_advantage", reg0),
      (val_mul, ":battle_advantage", 2),
      (val_div, ":battle_advantage", 3), #scale down the advantage a bit in sieges (vanilla)
      (set_battle_advantage, ":battle_advantage"),
      (set_party_battle_mode),
      (assign, "$g_siege_battle_state", 1),
      (assign, "$cant_talk_to_enemy", 0),
      # Side-swapped coop copies -- the engine binds the center to the
      # attacker side on a coop client (see the template comments).
      # Vanilla template selection: belfry-capable centers get the tower
      # assault (starts away from the wall, pushed by the player bots).
      (try_begin),
          (eq, ":with_belfry", 1),
          (set_jump_mission, "mt_coop_castle_attack_walls_belfry"),
      (else_try),
          (set_jump_mission, "mt_coop_castle_attack_walls_ladder"),
      (try_end),
      (jump_to_scene, ":wall_scene"),
      (jump_to_menu, "mnu_coop_local_battle_debrief"),
      (assign, "$g_coop_asi_local_battle", 1),
      (change_screen_mission),
  ]),

  # ------------------------------------------------------------------
  # PLAYER-PARTY CASUALTY CORE
  # The one place that applies a stack's battle losses to a player-side
  # campaign party. Both battle modes call it: the dedicated path's
  # ally loop (coop_apply_battle_results) and the local-fight result
  # arm (event 17). Rules: MP-profile remap, surgery saves, wound
  # survivors, heroes never removed, casualties accounted.
  # ------------------------------------------------------------------
  ("coop_apply_player_stack_casualty",
    [
      (store_script_param, ":party_no", 1),
      (store_script_param, ":troop_id", 2),
      (store_script_param, ":dead", 3),
      (store_script_param, ":wounded", 4),
      (store_script_param, ":surgery", 5),   # surgery skill x4; 0 = no saves
      (store_add, ":total_cas", ":dead", ":wounded"),

      # Map MP profile troops to trp_player
      (try_begin),
        (this_or_next|eq, ":troop_id", "trp_multiplayer_profile_troop_female"),
        (eq, ":troop_id", "trp_multiplayer_profile_troop_male"),
        (assign, ":troop_id", "trp_player"),
      (try_end),

      # Clamp to what the party actually has (local reports can race)
      (try_begin),
        (party_is_active, ":party_no"),
        (party_count_members_of_type, ":have", ":party_no", ":troop_id"),
        (val_min, ":dead", ":have"),
        (val_max, ":dead", 0),

        (str_store_troop_name, s1, ":troop_id"),
        (assign, reg1, ":dead"),
        (assign, reg2, ":wounded"),
        (display_message, "@[BATTLE RESULTS] CAS: {s1} dead={reg1} wounded={reg2}"),

        # Surgery: native rule -- each dead unit survives as wounded at
        # P = 0.25 + 0.04*surgery_level (engine resolver 0x4BB310). ":surgery"
        # arrives pre-scaled as skill*4, so the wound threshold out of 100 is
        # 25 + surgery, capped at 100. The 25% base applies even at surgery 0.
        (try_begin),
          (neg|troop_is_hero, ":troop_id"),
          (store_add, ":wound_pct", ":surgery", 25),
          (val_min, ":wound_pct", 100),
          (assign, ":end", ":dead"),
          (try_for_range, ":unused", 0, ":end"),
            (store_random_in_range, ":rand", 0, 100),
            (lt, ":rand", ":wound_pct"),
            (val_add, ":wounded", 1),
            (val_sub, ":dead", 1),
          (try_end),
        (try_end),

        # Remove dead, wound survivors
        (party_wound_members, ":party_no", ":troop_id", ":wounded"),
        (try_begin),
          (neg|troop_is_hero, ":troop_id"),
          (party_remove_members, ":party_no", ":troop_id", ":dead"),
        (try_end),

        # Casualty report parties
        (party_add_members, "p_player_casualties", ":troop_id", ":total_cas"),
        (party_wound_members, "p_player_casualties", ":troop_id", ":wounded"),
      (try_end),
  ]),

  # ==================================================================
  # CAMPAIGN: CHARACTER PERSISTENCE (save/load/creation)
  # ==================================================================

   ("coop_save_character",
   [
       # param 1: player_no
       (store_script_param, ":player_no", 1),

       (player_get_troop_id, ":troop_no", ":player_no"),
       (player_get_party_id, ":party_no", ":player_no"),

       # Build dict name: "coop_char_{username}"
       (str_store_player_username, s10, ":player_no"),
       (str_store_string, s11, "@coop_char_{s10}"),

       # Preserve @char_pending_* fields across the dict rebuild.
       # coop_apply_battle_results Phase 1 stashes these into char dicts
       # of players who haven't rejoined yet; a concurrent save here must
       # not wipe them.
       (assign, ":preserved_pending", 0),
       (assign, ":preserved_party_xp", 0),
       (assign, ":preserved_hero_xp", 0),
       (assign, ":preserved_siege_center", 0),
       (dict_create, "$coop_char_preserve_dict"),
       (dict_load_file, "$coop_char_preserve_dict", s11),
       (try_begin),
           (dict_has_key, "$coop_char_preserve_dict", "@char_battle_pending"),
           (dict_get_int, ":preserved_pending", "$coop_char_preserve_dict", "@char_battle_pending"),
       (try_end),
       (try_begin),
           (dict_has_key, "$coop_char_preserve_dict", "@char_siege_center"),
           (dict_get_int, ":preserved_siege_center", "$coop_char_preserve_dict", "@char_siege_center"),
       (try_end),
       (try_begin),
           (dict_has_key, "$coop_char_preserve_dict", "@char_pending_party_xp"),
           (dict_get_int, ":preserved_party_xp", "$coop_char_preserve_dict", "@char_pending_party_xp"),
       (try_end),
       (try_begin),
           (dict_has_key, "$coop_char_preserve_dict", "@char_pending_hero_xp"),
           (dict_get_int, ":preserved_hero_xp", "$coop_char_preserve_dict", "@char_pending_hero_xp"),
       (try_end),
       (try_begin),
           (neq, ":preserved_pending", 0),
           (assign, reg1, ":preserved_pending"),
           (assign, reg2, ":preserved_party_xp"),
           (assign, reg3, ":preserved_hero_xp"),
           (display_message, "@[CHAR SAVE] preserved pending={reg1} party_xp={reg2} hero_xp={reg3}"),
       (try_end),
       (dict_free, "$coop_char_preserve_dict"),

       (dict_create, "$coop_char_dict"),

       # Level and XP
       # If a DLL set_xp is pending for this troop, use the DLL target
       # value instead of troop_get_xp (which is stale until the DLL
       # processes the command after this frame).
       (store_character_level, ":level", ":troop_no"),
       (troop_get_xp, ":xp", ":troop_no"),
       (try_begin),
           (eq, "$g_coop_set_xp_go", 1),
           (eq, "$g_coop_set_xp_troop", ":troop_no"),
           (assign, ":xp", "$g_coop_set_xp_value"),
           (display_message, "@[CHAR SAVE] using DLL set_xp target instead of troop_get_xp"),
       (try_end),
       (assign, reg1, ":level"),
       (assign, reg2, ":xp"),
       (assign, reg3, ":player_no"),
       (display_message, "@[CHAR SAVE] player {reg3}: level={reg1} xp={reg2}"),
       (dict_set_int, "$coop_char_dict", "@char_level", ":level"),
       (dict_set_int, "$coop_char_dict", "@char_xp", ":xp"),

       # Attributes (indexed keys, same pattern as skills/profs)
       (try_for_range, ":attr", 0, num_coop_attrs),
           (assign, reg0, ":attr"),
           (str_store_string, s12, "@char_attr_{reg0}"),
           (store_attribute_level, ":val", ":troop_no", ":attr"),
           (dict_set_int, "$coop_char_dict", s12, ":val"),
       (try_end),

       # Unspent points
       (troop_get_attribute_points, ":val", ":troop_no"),
       (dict_set_int, "$coop_char_dict", "@char_pts_attr", ":val"),
       (troop_get_skill_points, ":val", ":troop_no"),
       (dict_set_int, "$coop_char_dict", "@char_pts_skl", ":val"),
       (troop_get_proficiency_points, ":val", ":troop_no"),
       (dict_set_int, "$coop_char_dict", "@char_pts_prof", ":val"),

       # Skills
       (try_for_range, ":skl", 0, num_coop_skills),
           (assign, reg0, ":skl"),
           (str_store_string, s12, "@char_skl_{reg0}"),
           (store_skill_level, ":val", ":skl", ":troop_no"),
           (dict_set_int, "$coop_char_dict", s12, ":val"),
       (try_end),

       # Weapon proficiencies (0-6)
       (try_for_range, ":wp", 0, 7),
           (assign, reg0, ":wp"),
           (str_store_string, s12, "@char_wp_{reg0}"),
           (store_proficiency_level, ":val", ":troop_no", ":wp"),
           (dict_set_int, "$coop_char_dict", s12, ":val"),
       (try_end),

       # Equipment slots (0-8: head, body, foot, gloves, weapon1-4, horse)
       (try_for_range, ":slot", 0, 9),
           (assign, reg0, ":slot"),
           (str_store_string, s12, "@char_itm_{reg0}"),
           (str_store_string, s13, "@char_imd_{reg0}"),
           (troop_get_inventory_slot, ":item", ":troop_no", ":slot"),
           (troop_get_inventory_slot_modifier, ":imod", ":troop_no", ":slot"),
           (dict_set_int, "$coop_char_dict", s12, ":item"),
           (dict_set_int, "$coop_char_dict", s13, ":imod"),
       (try_end),

       # Bag inventory (slots 10-105)
       (try_for_range, ":slot", 10, 106),
           (troop_get_inventory_slot, ":item", ":troop_no", ":slot"),
           (try_begin),
               (neq, ":item", -1),
               (gt, ":item", 0),
               (troop_get_inventory_slot_modifier, ":imod", ":troop_no", ":slot"),
               (assign, reg0, ":slot"),
               (str_store_string, s12, "@char_bag_{reg0}"),
               (str_store_string, s13, "@char_bag_mod_{reg0}"),
               (dict_set_int, "$coop_char_dict", s12, ":item"),
               (dict_set_int, "$coop_char_dict", s13, ":imod"),
           (try_end),
       (try_end),

       # Map position -- use explicit multiplier so load can match
       (try_begin),
           (party_is_active, ":party_no"),
           (set_fixed_point_multiplier, 1),
           (party_get_position, pos1, ":party_no"),
           (position_get_x, ":pos_x", pos1),
           (position_get_y, ":pos_y", pos1),
           (set_fixed_point_multiplier, 1000),
           (dict_set_int, "$coop_char_dict", "@char_spawn_x", ":pos_x"),
           (dict_set_int, "$coop_char_dict", "@char_spawn_y", ":pos_y"),
       (try_end),

       # Gold
       (store_troop_gold, ":gold", ":troop_no"),
       (dict_set_int, "$coop_char_dict", "@char_gold", ":gold"),

       # Banner
       (try_begin),
           (party_is_active, ":party_no"),
           (party_get_banner_icon, ":banner", ":party_no"),
           (dict_set_int, "$coop_char_dict", "@char_banner", ":banner"),
       (try_end),

       # Party troop stacks. Player troops are excluded (the join flow
       # re-binds them); everything else -- including companion heroes --
       # must be saved, because the load rebuild is party_clear +
       # re-add-from-dict and anything skipped here is lost on rejoin.
       (try_begin),
           (party_is_active, ":party_no"),
           (party_get_num_companion_stacks, ":num_stacks", ":party_no"),
           (assign, reg1, ":num_stacks"),
           (assign, reg2, ":party_no"),
           (display_message, "@[CHAR SAVE] party {reg2} has {reg1} stacks"),
           (assign, ":save_idx", 0),
           (try_for_range, ":i", 0, ":num_stacks"),
               (party_stack_get_troop_id, ":stack_troop", ":party_no", ":i"),
               (neg|is_between, ":stack_troop", multiplayer_campaign_player_troops_begin, multiplayer_campaign_player_troops_end),
               (party_stack_get_size, ":stack_size", ":party_no", ":i"),
               (party_stack_get_num_wounded, ":stack_wounded", ":party_no", ":i"),
               # Stack XP drives troop upgrades -- meaningless for heroes
               # (hero XP lives on the troop itself).
               (assign, ":stack_xp", 0),
               (try_begin),
                   (neg|troop_is_hero, ":stack_troop"),
                   (party_stack_get_experience, ":stack_xp", ":party_no", ":i"),
               (try_end),
               (assign, reg0, ":save_idx"),
               (str_store_string, s12, "@char_party_troop_{reg0}"),
               (str_store_string, s13, "@char_party_count_{reg0}"),
               (str_store_string, s14, "@char_party_wound_{reg0}"),
               (str_store_string, s15, "@char_party_xp_{reg0}"),
               (dict_set_int, "$coop_char_dict", s12, ":stack_troop"),
               (dict_set_int, "$coop_char_dict", s13, ":stack_size"),
               (dict_set_int, "$coop_char_dict", s14, ":stack_wounded"),
               (dict_set_int, "$coop_char_dict", s15, ":stack_xp"),
               (val_add, ":save_idx", 1),
           (try_end),
           (dict_set_int, "$coop_char_dict", "@char_party_stacks", ":save_idx"),
       (try_end),

       # Write back preserved pending fields (zero if no prior stash)
       (dict_set_int, "$coop_char_dict", "@char_battle_pending", ":preserved_pending"),
       (dict_set_int, "$coop_char_dict", "@char_pending_party_xp", ":preserved_party_xp"),
       (dict_set_int, "$coop_char_dict", "@char_pending_hero_xp", ":preserved_hero_xp"),
       (dict_set_int, "$coop_char_dict", "@char_siege_center", ":preserved_siege_center"),

       (dict_save, "$coop_char_dict", s11),
       (dict_free, "$coop_char_dict"),

       (assign, reg0, ":player_no"),
       (display_message, "@Character saved for player {reg0}."),
   ]),

   ("coop_load_character",
   [
       # param 1: player_no
       # Returns reg0: 1 if loaded, 0 if no save found
       (store_script_param, ":player_no", 1),

       (player_get_troop_id, ":troop_no", ":player_no"),
       (player_get_party_id, ":party_no", ":player_no"),

       # Build dict name
       (str_store_player_username, s10, ":player_no"),
       (str_store_string, s11, "@coop_char_{s10}"),

       (dict_create, "$coop_char_dict"),
       (dict_load_file, "$coop_char_dict", s11),

       (try_begin),
           (neg|dict_has_key, "$coop_char_dict", "@char_level"),
           # No save file -- starter party
           (dict_free, "$coop_char_dict"),
           (try_begin),
               (party_is_active, ":party_no"),
               (party_add_members, ":party_no", "trp_nord_recruit", 30),
               # Starter companion hero -- one per player slot so two players
               # never share the same unique NPC (heroes are wounded, never
               # removed, by the casualty core). Persisted like any other
               # stack once the char dict is first saved.
               (store_mod, ":npc_offset", ":player_no", 16),
               (store_add, ":companion", "trp_npc1", ":npc_offset"),
               (party_add_members, ":party_no", ":companion", 1),
               # Starting gold -- zero first, then set
               (store_troop_gold, ":cg", ":troop_no"),
               (try_begin), (gt, ":cg", 0), (troop_remove_gold, ":troop_no", ":cg"), (try_end),
               (troop_add_gold, ":troop_no", 10000),
           (try_end),
           (assign, reg0, 0),
       (else_try),
           # Apply saved data to troop

           # Attributes -- raise by +1 in loop to avoid engine XP inflation
           (try_for_range, ":attr", 0, num_coop_attrs),
               (assign, reg0, ":attr"),
               (str_store_string, s12, "@char_attr_{reg0}"),
               (dict_get_int, ":val", "$coop_char_dict", s12),
               (store_attribute_level, ":cur", ":troop_no", ":attr"),
               (val_sub, ":val", ":cur"),
               (try_for_range, ":unused", 0, ":val"),
                   (troop_raise_attribute, ":troop_no", ":attr", 1),
               (try_end),
           (try_end),

           # Skills -- raise by +1 in loop
           (try_for_range, ":skl", 0, num_coop_skills),
               (assign, reg0, ":skl"),
               (str_store_string, s12, "@char_skl_{reg0}"),
               (dict_get_int, ":val", "$coop_char_dict", s12),
               (store_skill_level, ":cur", ":skl", ":troop_no"),
               (val_sub, ":val", ":cur"),
               (try_for_range, ":unused", 0, ":val"),
                   (troop_raise_skill, ":troop_no", ":skl", 1),
               (try_end),
           (try_end),

           # Weapon proficiencies -- raise_linear by +1 in loop (raise_proficiency has diminishing returns)
           (try_for_range, ":wp", 0, 7),
               (assign, reg0, ":wp"),
               (str_store_string, s12, "@char_wp_{reg0}"),
               (dict_get_int, ":val", "$coop_char_dict", s12),
               (store_proficiency_level, ":cur", ":troop_no", ":wp"),
               (val_sub, ":val", ":cur"),
               (try_for_range, ":unused", 0, ":val"),
                   (troop_raise_proficiency_linear, ":troop_no", ":wp", 1),
               (try_end),
           (try_end),

           # XP -- use add_xp_to_troop for positive deltas, signal DLL for
           # negative deltas.  add_xp_to_troop clamps negatives to 0
           # (engine addExperienceToTroop at 0x4B8480 does max(xp,0)).
           # The DLL writes m_experience + m_level directly in the troop
           # struct from coop_post_frame (runs after scripts this frame).
           (dict_get_int, ":val", "$coop_char_dict", "@char_xp"),
           (troop_get_xp, ":current_xp", ":troop_no"),
           (assign, reg1, ":val"),
           (assign, reg2, ":current_xp"),
           (store_sub, reg3, ":val", ":current_xp"),
           (assign, reg4, ":player_no"),
           (display_message, "@[CHAR LOAD] player {reg4}: dict_xp={reg1} current_xp={reg2} delta={reg3}"),
           (store_sub, ":xp_delta", ":val", ":current_xp"),
           (try_begin),
             (gt, ":xp_delta", 0),
             # Positive delta -- add_xp_to_troop works (capped at 29999 per call)
             (assign, ":xp_remaining", ":xp_delta"),
             (try_begin),
               (gt, ":xp_remaining", 29999),
               (try_for_range, ":unused", 0, 100),
                 (gt, ":xp_remaining", 29999),
                 (add_xp_to_troop, 29999, ":troop_no"),
                 (val_sub, ":xp_remaining", 29999),
               (try_end),
             (try_end),
             (try_begin),
               (gt, ":xp_remaining", 0),
               (add_xp_to_troop, ":xp_remaining", ":troop_no"),
             (try_end),
             (assign, reg1, ":xp_delta"),
             (display_message, "@[CHAR LOAD] add_xp_to_troop +{reg1}"),
           (else_try),
             (lt, ":xp_delta", 0),
             # Negative delta -- engine can't subtract.
             # Signal DLL to write XP directly after this frame.
             # Store the target XP; any Phase 2 addition that runs later
             # in this frame will add_xp_to_troop on top, which is fine
             # because the DLL set overwrites the total.  So we also
             # store the base in $g_coop_set_xp_value and let Phase 2
             # add its delta to the global before the DLL processes it.
             (assign, "$g_coop_set_xp_troop", ":troop_no"),
             (assign, "$g_coop_set_xp_value", ":val"),
             (assign, "$g_coop_set_xp_go", 1),
             (assign, reg1, ":val"),
             (display_message, "@[CHAR LOAD] DLL set_xp queued: troop xp={reg1} (negative delta)"),
           (try_end),

           # Unspent points
           (dict_get_int, ":val", "$coop_char_dict", "@char_pts_attr"),
           (troop_set_attribute_points, ":troop_no", ":val"),
           (dict_get_int, ":val", "$coop_char_dict", "@char_pts_skl"),
           (troop_set_skill_points, ":troop_no", ":val"),
           (dict_get_int, ":val", "$coop_char_dict", "@char_pts_prof"),
           (troop_set_proficiency_points, ":troop_no", ":val"),

           # Equipment -- validate item IDs against current build's item table
           (try_for_range, ":slot", 0, 9),
               (assign, reg0, ":slot"),
               (str_store_string, s12, "@char_itm_{reg0}"),
               (str_store_string, s13, "@char_imd_{reg0}"),
               (dict_get_int, ":item", "$coop_char_dict", s12),
               (dict_get_int, ":imod", "$coop_char_dict", s13),
               (assign, reg1, ":item"),
               (assign, reg2, ":imod"),
               (try_begin),
                   (is_between, ":item", 1, coop_new_items_end),
                   (troop_set_inventory_slot, ":troop_no", ":slot", ":item"),
                   (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":imod"),
               (else_try),
                   (gt, ":item", 0),
               (try_end),
           (try_end),
           (call_script, "script_coop_check_item_bug", ":troop_no"),

           # Bag inventory (slots 10-105)
           (try_for_range, ":slot", 10, 106),
               (assign, reg0, ":slot"),
               (str_store_string, s12, "@char_bag_{reg0}"),
               (try_begin),
                   (dict_has_key, "$coop_char_dict", s12),
                   (dict_get_int, ":item", "$coop_char_dict", s12),
                   (str_store_string, s13, "@char_bag_mod_{reg0}"),
                   (dict_get_int, ":imod", "$coop_char_dict", s13),
                   (try_begin),
                       (is_between, ":item", 1, coop_new_items_end),
                       (troop_set_inventory_slot, ":troop_no", ":slot", ":item"),
                       (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":imod"),
                   (try_end),
               (try_end),
           (try_end),

           # Gold -- zero out first (troop persists in server memory between joins)
           (store_troop_gold, ":cur_gold", ":troop_no"),
           (try_begin),
               (gt, ":cur_gold", 0),
               (troop_remove_gold, ":troop_no", ":cur_gold"),
           (try_end),
           (try_begin),
               (dict_has_key, "$coop_char_dict", "@char_gold"),
               (dict_get_int, ":gold", "$coop_char_dict", "@char_gold"),
               (gt, ":gold", 0),
               (troop_add_gold, ":troop_no", ":gold"),
           (try_end),

           # Map position -- only restore if dict has valid coordinates
           (try_begin),
               (party_is_active, ":party_no"),
               (dict_has_key, "$coop_char_dict", "@char_spawn_x"),
               (dict_get_int, ":pos_x", "$coop_char_dict", "@char_spawn_x"),
               (dict_get_int, ":pos_y", "$coop_char_dict", "@char_spawn_y"),
               (assign, reg1, ":pos_x"),
               (assign, reg2, ":pos_y"),
               (gt, ":pos_x", 0),
               (gt, ":pos_y", 0),
               (set_fixed_point_multiplier, 1),
               (init_position, pos1),
               (position_set_x, pos1, ":pos_x"),
               (position_set_y, pos1, ":pos_y"),
               (party_set_position, ":party_no", pos1),
               (set_fixed_point_multiplier, 1000),
           (try_end),

           # Banner
           (dict_get_int, ":banner", "$coop_char_dict", "@char_banner"),
           (try_begin),
               (gt, ":banner", 0),
               (party_is_active, ":party_no"),
               (party_set_banner_icon, ":party_no", ":banner"),
           (try_end),

           # Party troop stacks
           (try_begin),
               (party_is_active, ":party_no"),
               (dict_has_key, "$coop_char_dict", "@char_party_stacks"),
               (dict_get_int, ":num_stacks", "$coop_char_dict", "@char_party_stacks"),
               (assign, reg1, ":num_stacks"),
               (assign, reg2, ":party_no"),
               (display_message, "@[CHAR LOAD] party rebuild: {reg1} stacks for party {reg2}"),
               (party_clear, ":party_no"),
               (try_for_range, ":i", 0, ":num_stacks"),
                   (assign, reg0, ":i"),
                   (str_store_string, s12, "@char_party_troop_{reg0}"),
                   (str_store_string, s13, "@char_party_count_{reg0}"),
                   (str_store_string, s14, "@char_party_wound_{reg0}"),
                   (str_store_string, s15, "@char_party_xp_{reg0}"),
                   (dict_get_int, ":stack_troop", "$coop_char_dict", s12),
                   (dict_get_int, ":stack_size", "$coop_char_dict", s13),
                   (dict_get_int, ":stack_wounded", "$coop_char_dict", s14),
                   (assign, ":stack_xp", 0),
                   (try_begin),
                       (dict_has_key, "$coop_char_dict", s15),
                       (dict_get_int, ":stack_xp", "$coop_char_dict", s15),
                   (try_end),
                   (gt, ":stack_size", 0),
                   (party_add_members, ":party_no", ":stack_troop", ":stack_size"),
                   (try_begin),
                       (gt, ":stack_wounded", 0),
                       (party_wound_members, ":party_no", ":stack_troop", ":stack_wounded"),
                   (try_end),
                   (try_begin),
                       (gt, ":stack_xp", 0),
                       (party_add_xp_to_stack, ":party_no", ":i", ":stack_xp"),
                   (try_end),
               (try_end),
           (try_end),

           (dict_free, "$coop_char_dict"),
           (assign, reg0, 1),
       (try_end),
   ]),

   # The local-siege target must survive the client's disconnect into the
   # local mission AND the player_no/party reassignment on rejoin (player
   # slots and the slot-indexed party are handed out fresh each join), so
   # it lives in the username-keyed char dict, not in player/party slots.
   # coop_save_character preserves @char_siege_center across dict rebuilds.

   # script_coop_char_siege_center_set
   # Input: player_no, center party id (0 = clear)
   ("coop_char_siege_center_set",
   [
       (store_script_param, ":player_no", 1),
       (store_script_param, ":center_no", 2),
       (str_store_player_username, s10, ":player_no"),
       (str_store_string, s11, "@coop_char_{s10}"),
       (dict_create, "$coop_char_siege_dict"),
       (dict_load_file, "$coop_char_siege_dict", s11),
       (dict_set_int, "$coop_char_siege_dict", "@char_siege_center", ":center_no"),
       (dict_save, "$coop_char_siege_dict", s11),
       (dict_free, "$coop_char_siege_dict"),
   ]),

   # script_coop_char_siege_center_get
   # Input: player_no. Output: reg0 = center party id (0 = none)
   ("coop_char_siege_center_get",
   [
       (store_script_param, ":player_no", 1),
       (str_store_player_username, s10, ":player_no"),
       (str_store_string, s11, "@coop_char_{s10}"),
       (assign, ":center_no", 0),
       (dict_create, "$coop_char_siege_dict"),
       (dict_load_file, "$coop_char_siege_dict", s11),
       (try_begin),
           (dict_has_key, "$coop_char_siege_dict", "@char_siege_center"),
           (dict_get_int, ":center_no", "$coop_char_siege_dict", "@char_siege_center"),
       (try_end),
       (dict_free, "$coop_char_siege_dict"),
       (assign, reg0, ":center_no"),
   ]),

   ("coop_apply_character_creation",
   [
       (store_script_param, ":player_no", 1),
       (store_script_param, ":gender", 2),
       (store_script_param, ":father", 3),
       (store_script_param, ":earlylife", 4),
       (store_script_param, ":adulthood", 5),
       (store_script_param, ":reason", 6),

       (player_get_troop_id, ":troop_no", ":player_no"),

       # Set gender
       (troop_set_type, ":troop_no", ":gender"),

       # Base attributes: STR 5, AGI 5, INT 4, CHA 5
       (troop_set_attribute, ":troop_no", ca_strength, 5),
       (troop_set_attribute, ":troop_no", ca_agility, 5),
       (troop_set_attribute, ":troop_no", ca_intelligence, 4),
       (troop_set_attribute, ":troop_no", ca_charisma, 5),

       # Gender bonus
       (try_begin),
           (eq, ":gender", 0), # male
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_charisma, 1),
       (else_try),
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
       (try_end),

       # Global base bonus (all backgrounds)
       (troop_raise_attribute, ":troop_no", ca_strength, 1),
       (troop_raise_attribute, ":troop_no", ca_agility, 1),
       (troop_raise_attribute, ":troop_no", ca_charisma, 1),
       (troop_raise_skill, ":troop_no", skl_leadership, 1),
       (troop_raise_skill, ":troop_no", skl_riding, 1),

       # --- Father's background ---
       (try_begin),
           (eq, ":father", cb_noble),
           (try_begin),
               (eq, ":gender", 0), # male noble
               (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
               (troop_raise_attribute, ":troop_no", ca_charisma, 2),
               (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
               (troop_raise_skill, ":troop_no", skl_power_strike, 1),
               (troop_raise_skill, ":troop_no", skl_riding, 1),
               (troop_raise_skill, ":troop_no", skl_tactics, 1),
               (troop_raise_skill, ":troop_no", skl_leadership, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 10),
               (troop_raise_proficiency, ":troop_no", wpt_two_handed_weapon, 10),
               (troop_raise_proficiency, ":troop_no", wpt_polearm, 10),
           (else_try), # female noble
               (troop_raise_attribute, ":troop_no", ca_intelligence, 2),
               (troop_raise_attribute, ":troop_no", ca_charisma, 1),
               (troop_raise_skill, ":troop_no", skl_wound_treatment, 1),
               (troop_raise_skill, ":troop_no", skl_riding, 2),
               (troop_raise_skill, ":troop_no", skl_first_aid, 1),
               (troop_raise_skill, ":troop_no", skl_leadership, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 20),
           (try_end),
       (else_try),
           (eq, ":father", cb_merchant),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 2),
           (troop_raise_attribute, ":troop_no", ca_charisma, 1),
           (troop_raise_skill, ":troop_no", skl_riding, 1),
           (troop_raise_skill, ":troop_no", skl_leadership, 1),
           (troop_raise_skill, ":troop_no", skl_trade, 2),
           (troop_raise_skill, ":troop_no", skl_inventory_management, 1),
           (troop_raise_proficiency, ":troop_no", wpt_two_handed_weapon, 10),
       (else_try),
           (eq, ":father", cb_guard),
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_attribute, ":troop_no", ca_charisma, 1),
           (troop_raise_skill, ":troop_no", skl_ironflesh, 1),
           (troop_raise_skill, ":troop_no", skl_power_strike, 1),
           (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
           (troop_raise_skill, ":troop_no", skl_leadership, 1),
           (troop_raise_skill, ":troop_no", skl_trainer, 1),
           (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 10),
           (troop_raise_proficiency, ":troop_no", wpt_two_handed_weapon, 15),
           (troop_raise_proficiency, ":troop_no", wpt_polearm, 20),
           (troop_raise_proficiency, ":troop_no", wpt_throwing, 10),
       (else_try),
           (eq, ":father", cb_forester),
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_agility, 2),
           (troop_raise_skill, ":troop_no", skl_power_draw, 1),
           (troop_raise_skill, ":troop_no", skl_tracking, 1),
           (troop_raise_skill, ":troop_no", skl_pathfinding, 1),
           (troop_raise_skill, ":troop_no", skl_spotting, 1),
           (troop_raise_skill, ":troop_no", skl_athletics, 1),
           (troop_raise_proficiency, ":troop_no", wpt_two_handed_weapon, 10),
           (troop_raise_proficiency, ":troop_no", wpt_archery, 30),
       (else_try),
           (eq, ":father", cb_nomad),
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (try_begin),
               (eq, ":gender", 0),
               (troop_raise_skill, ":troop_no", skl_power_draw, 1),
               (troop_raise_skill, ":troop_no", skl_horse_archery, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 10),
               (troop_raise_proficiency, ":troop_no", wpt_archery, 30),
               (troop_raise_proficiency, ":troop_no", wpt_throwing, 10),
           (else_try),
               (troop_raise_skill, ":troop_no", skl_wound_treatment, 1),
               (troop_raise_skill, ":troop_no", skl_first_aid, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 5),
               (troop_raise_proficiency, ":troop_no", wpt_archery, 20),
               (troop_raise_proficiency, ":troop_no", wpt_throwing, 5),
           (try_end),
           (troop_raise_skill, ":troop_no", skl_pathfinding, 1),
           (troop_raise_skill, ":troop_no", skl_riding, 2),
       (else_try),
           (eq, ":father", cb_thief),
           (troop_raise_attribute, ":troop_no", ca_agility, 3),
           (troop_raise_skill, ":troop_no", skl_athletics, 2),
           (troop_raise_skill, ":troop_no", skl_power_throw, 1),
           (troop_raise_skill, ":troop_no", skl_inventory_management, 1),
           (troop_raise_skill, ":troop_no", skl_looting, 1),
           (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 20),
           (troop_raise_proficiency, ":troop_no", wpt_throwing, 20),
       (try_end),

       # --- Early life ---
       (try_begin),
           (eq, ":earlylife", 0), # page
           (troop_raise_attribute, ":troop_no", ca_charisma, 1),
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_skill, ":troop_no", skl_power_strike, 1),
           (troop_raise_skill, ":troop_no", skl_persuasion, 1),
           (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 15),
           (troop_raise_proficiency, ":troop_no", wpt_polearm, 5),
       (else_try),
           (eq, ":earlylife", 1), # apprentice
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_skill, ":troop_no", skl_engineer, 1),
           (troop_raise_skill, ":troop_no", skl_trade, 1),
       (else_try),
           (eq, ":earlylife", 2), # urchin
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (troop_raise_skill, ":troop_no", skl_spotting, 1),
           (troop_raise_skill, ":troop_no", skl_looting, 1),
           (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 15),
           (troop_raise_proficiency, ":troop_no", wpt_throwing, 5),
       (else_try),
           (eq, ":earlylife", 3), # steppe child
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_skill, ":troop_no", skl_horse_archery, 1),
           (troop_raise_skill, ":troop_no", skl_power_throw, 1),
           (troop_raise_proficiency, ":troop_no", wpt_archery, 15),
       (else_try),
           (eq, ":earlylife", 4), # shop assistant
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (troop_raise_attribute, ":troop_no", ca_charisma, 1),
           (troop_raise_skill, ":troop_no", skl_inventory_management, 1),
           (troop_raise_skill, ":troop_no", skl_trade, 1),
       (try_end),

       # --- Young adulthood ---
       # Button index depends on gender (squire=male only, lady=female only)
       (try_begin),
           (eq, ":gender", 0), # male: squire(0), troubadour(1), student(2), peddler(3), craftsman(4), poacher(5)
           (try_begin),
               (eq, ":adulthood", 0), # squire
               (troop_raise_attribute, ":troop_no", ca_strength, 1),
               (troop_raise_attribute, ":troop_no", ca_agility, 1),
               (troop_raise_skill, ":troop_no", skl_riding, 1),
               (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
               (troop_raise_skill, ":troop_no", skl_power_strike, 1),
               (troop_raise_skill, ":troop_no", skl_leadership, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 30),
               (troop_raise_proficiency, ":troop_no", wpt_two_handed_weapon, 30),
               (troop_raise_proficiency, ":troop_no", wpt_polearm, 30),
               (troop_raise_proficiency, ":troop_no", wpt_archery, 10),
               (troop_raise_proficiency, ":troop_no", wpt_crossbow, 10),
               (troop_raise_proficiency, ":troop_no", wpt_throwing, 10),
               (troop_set_inventory_slot, ":troop_no", ek_body, "itm_leather_jerkin"),
               (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
               (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_sword_medieval_a"),
               (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
               (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
           (else_try),
               (eq, ":adulthood", 1), # troubadour
               (call_script, "script_coop_apply_adulthood_troubadour", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 2), # student
               (call_script, "script_coop_apply_adulthood_student", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 3), # peddler
               (call_script, "script_coop_apply_adulthood_peddler", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 4), # craftsman
               (call_script, "script_coop_apply_adulthood_craftsman", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 5), # poacher
               (call_script, "script_coop_apply_adulthood_poacher", ":troop_no"),
           (try_end),
       (else_try), # female: lady(0), troubadour(1), student(2), peddler(3), craftsman(4), poacher(5)
           (try_begin),
               (eq, ":adulthood", 0), # lady-in-waiting
               (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
               (troop_raise_attribute, ":troop_no", ca_charisma, 1),
               (troop_raise_skill, ":troop_no", skl_persuasion, 2),
               (troop_raise_skill, ":troop_no", skl_riding, 1),
               (troop_raise_skill, ":troop_no", skl_wound_treatment, 1),
               (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 10),
               (troop_raise_proficiency, ":troop_no", wpt_crossbow, 15),
               (troop_set_inventory_slot, ":troop_no", ek_head, "itm_woolen_hood"),
               (troop_set_inventory_slot, ":troop_no", ek_body, "itm_woolen_dress"),
               (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_dagger"),
               (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
               (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
           (else_try),
               (eq, ":adulthood", 1), # troubadour
               (call_script, "script_coop_apply_adulthood_troubadour", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 2), # student
               (call_script, "script_coop_apply_adulthood_student", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 3), # peddler
               (call_script, "script_coop_apply_adulthood_peddler", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 4), # craftsman
               (call_script, "script_coop_apply_adulthood_craftsman", ":troop_no"),
           (else_try),
               (eq, ":adulthood", 5), # poacher
               (call_script, "script_coop_apply_adulthood_poacher", ":troop_no"),
           (try_end),
       (try_end),

       # --- Reason for adventuring ---
       (try_begin),
           (eq, ":reason", 0), # revenge
           (troop_raise_attribute, ":troop_no", ca_strength, 2),
           (troop_raise_skill, ":troop_no", skl_power_strike, 1),
       (else_try),
           (eq, ":reason", 1), # loss
           (troop_raise_attribute, ":troop_no", ca_charisma, 2),
           (troop_raise_skill, ":troop_no", skl_ironflesh, 1),
       (else_try),
           (eq, ":reason", 2), # wanderlust
           (troop_raise_attribute, ":troop_no", ca_agility, 2),
           (troop_raise_skill, ":troop_no", skl_pathfinding, 1),
       (else_try),
           (eq, ":reason", 3), # forced out
           (troop_raise_attribute, ":troop_no", ca_strength, 1),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
       (else_try),
           (eq, ":reason", 4), # greed
           (troop_raise_attribute, ":troop_no", ca_agility, 1),
           (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
           (troop_raise_skill, ":troop_no", skl_looting, 1),
       (try_end),

       # Default starting equipment
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_leather_jerkin"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_sword_medieval_a"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_hunting_bow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_arrows"),

       # Set starting unspent points
       (troop_set_attribute_points, ":troop_no", 4),
       (troop_set_skill_points, ":troop_no", 2),
       (troop_set_proficiency_points, ":troop_no", 60),

       # Starter party troops (added via coop_load_character no-save path)
       (player_get_party_id, ":party_no", ":player_no"),

       # TEST/DEBUG: give a stack of Nord Huscarls (trp_nord_champion) so
       # sieges can be tested with a real attacking force. Remove before release.
       (party_add_members, ":party_no", "trp_nord_champion", 100),

       (display_message, "@Character creation complete."),
   ]),

   # Shared adulthood sub-scripts
   ("coop_apply_adulthood_troubadour",
   [
       (store_script_param, ":troop_no", 1),
       (troop_raise_attribute, ":troop_no", ca_charisma, 2),
       (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
       (troop_raise_skill, ":troop_no", skl_persuasion, 1),
       (troop_raise_skill, ":troop_no", skl_leadership, 1),
       (troop_raise_skill, ":troop_no", skl_pathfinding, 1),
       (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 25),
       (troop_raise_proficiency, ":troop_no", wpt_crossbow, 10),
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_tabard"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_sword_medieval_a"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
   ]),

   ("coop_apply_adulthood_student",
   [
       (store_script_param, ":troop_no", 1),
       (troop_raise_attribute, ":troop_no", ca_intelligence, 2),
       (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
       (troop_raise_skill, ":troop_no", skl_surgery, 1),
       (troop_raise_skill, ":troop_no", skl_wound_treatment, 1),
       (troop_raise_skill, ":troop_no", skl_persuasion, 1),
       (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 20),
       (troop_raise_proficiency, ":troop_no", wpt_crossbow, 20),
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_linen_tunic"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_woolen_hose"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_sword_medieval_a"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
   ]),

   ("coop_apply_adulthood_peddler",
   [
       (store_script_param, ":troop_no", 1),
       (troop_raise_attribute, ":troop_no", ca_charisma, 1),
       (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
       (troop_raise_skill, ":troop_no", skl_riding, 1),
       (troop_raise_skill, ":troop_no", skl_trade, 1),
       (troop_raise_skill, ":troop_no", skl_pathfinding, 1),
       (troop_raise_skill, ":troop_no", skl_inventory_management, 1),
       (troop_raise_proficiency, ":troop_no", wpt_polearm, 15),
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_leather_jacket"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
       (troop_set_inventory_slot, ":troop_no", ek_head, "itm_fur_hat"),
       (troop_set_inventory_slot, ":troop_no", ek_gloves, "itm_leather_gloves"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_staff"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
   ]),

   ("coop_apply_adulthood_craftsman",
   [
       (store_script_param, ":troop_no", 1),
       (troop_raise_attribute, ":troop_no", ca_strength, 1),
       (troop_raise_attribute, ":troop_no", ca_intelligence, 1),
       (troop_raise_skill, ":troop_no", skl_weapon_master, 1),
       (troop_raise_skill, ":troop_no", skl_engineer, 1),
       (troop_raise_skill, ":troop_no", skl_tactics, 1),
       (troop_raise_skill, ":troop_no", skl_trade, 1),
       (troop_raise_proficiency, ":troop_no", wpt_one_handed_weapon, 15),
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_coarse_tunic"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_sword_medieval_b_small"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_crossbow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_bolts"),
   ]),

   ("coop_apply_adulthood_poacher",
   [
       (store_script_param, ":troop_no", 1),
       (troop_raise_attribute, ":troop_no", ca_strength, 1),
       (troop_raise_attribute, ":troop_no", ca_agility, 1),
       (troop_raise_skill, ":troop_no", skl_power_draw, 1),
       (troop_raise_skill, ":troop_no", skl_tracking, 1),
       (troop_raise_skill, ":troop_no", skl_spotting, 1),
       (troop_raise_skill, ":troop_no", skl_athletics, 1),
       (troop_raise_proficiency, ":troop_no", wpt_polearm, 10),
       (troop_raise_proficiency, ":troop_no", wpt_archery, 35),
       (troop_set_inventory_slot, ":troop_no", ek_body, "itm_rawhide_coat"),
       (troop_set_inventory_slot, ":troop_no", ek_foot, "itm_hide_boots"),
       (troop_set_inventory_slot, ":troop_no", ek_item_0, "itm_hatchet"),
       (troop_set_inventory_slot, ":troop_no", ek_item_1, "itm_hunting_bow"),
       (troop_set_inventory_slot, ":troop_no", ek_item_2, "itm_barbed_arrows"),
   ]),

  ("coop_creation_show_step",
  [
    (try_begin),
        (eq, "$g_coop_creation_step", 0),
        # Gender selection
        (create_text_overlay, reg0, "@Choose your gender:", tf_center_justify|tf_with_outline),
        (overlay_set_color, reg0, 0xFFFFFF),
        (position_set_x, pos1, 500),
        (position_set_y, pos1, 600),
        (overlay_set_position, reg0, pos1),
        (position_set_x, pos1, 1500),
        (position_set_y, pos1, 1500),
        (overlay_set_size, reg0, pos1),

        (create_button_overlay, "$g_coop_creation_opt_0", "@Male", tf_center_justify),
        (position_set_x, pos1, 400),
        (position_set_y, pos1, 500),
        (overlay_set_position, "$g_coop_creation_opt_0", pos1),

        (create_button_overlay, "$g_coop_creation_opt_1", "@Female", tf_center_justify),
        (position_set_x, pos1, 600),
        (position_set_y, pos1, 500),
        (overlay_set_position, "$g_coop_creation_opt_1", pos1),

    (else_try),
        (eq, "$g_coop_creation_step", 1),
        # Father's background
        (create_text_overlay, reg0, "@Your father was...", tf_center_justify|tf_with_outline),
        (overlay_set_color, reg0, 0xFFFFFF),
        (position_set_x, pos1, 500),
        (position_set_y, pos1, 680),
        (overlay_set_position, reg0, pos1),
        (position_set_x, pos1, 1500),
        (position_set_y, pos1, 1500),
        (overlay_set_size, reg0, pos1),

        (assign, ":y", 620),
        # Noble
        (create_button_overlay, reg0, "@An impoverished noble", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 60, reg0),
        (val_sub, ":y", 45),
        # Merchant
        (create_button_overlay, reg0, "@A travelling merchant", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 61, reg0),
        (val_sub, ":y", 45),
        # Guard
        (create_button_overlay, reg0, "@A veteran warrior", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 62, reg0),
        (val_sub, ":y", 45),
        # Forester
        (create_button_overlay, reg0, "@A hunter", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 63, reg0),
        (val_sub, ":y", 45),
        # Nomad
        (create_button_overlay, reg0, "@A steppe nomad", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 64, reg0),
        (val_sub, ":y", 45),
        # Thief
        (create_button_overlay, reg0, "@A thief", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 65, reg0),

    (else_try),
        (eq, "$g_coop_creation_step", 2),
        # Early life
        (create_text_overlay, reg0, "@You spent your early life as...", tf_center_justify|tf_with_outline),
        (overlay_set_color, reg0, 0xFFFFFF),
        (position_set_x, pos1, 500),
        (position_set_y, pos1, 680),
        (overlay_set_position, reg0, pos1),
        (position_set_x, pos1, 1500),
        (position_set_y, pos1, 1500),
        (overlay_set_size, reg0, pos1),

        (assign, ":y", 600),
        (create_button_overlay, reg0, "@A page at a nobleman's court", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 60, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@A craftsman's apprentice", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 61, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@A street urchin", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 62, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@A steppe child", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 63, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@A shop assistant", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 64, reg0),

    (else_try),
        (eq, "$g_coop_creation_step", 3),
        # Young adulthood
        (create_text_overlay, reg0, "@As a young adult, you became...", tf_center_justify|tf_with_outline),
        (overlay_set_color, reg0, 0xFFFFFF),
        (position_set_x, pos1, 500),
        (position_set_y, pos1, 700),
        (overlay_set_position, reg0, pos1),
        (position_set_x, pos1, 1500),
        (position_set_y, pos1, 1500),
        (overlay_set_size, reg0, pos1),

        (assign, ":y", 640),
        (assign, ":num_options", 0),

        # Squire (male only)
        (try_begin),
            (eq, "$g_coop_creation_gender", 0),
            (create_button_overlay, reg0, "@A squire", 0),
            (position_set_x, pos1, 200),
            (position_set_y, pos1, ":y"),
            (overlay_set_position, reg0, pos1),
            (store_add, ":slot", ":num_options", 60),
            (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
            (val_sub, ":y", 40),
            (val_add, ":num_options", 1),
        (try_end),
        # Lady-in-waiting (female only)
        (try_begin),
            (eq, "$g_coop_creation_gender", 1),
            (create_button_overlay, reg0, "@A lady-in-waiting", 0),
            (position_set_x, pos1, 200),
            (position_set_y, pos1, ":y"),
            (overlay_set_position, reg0, pos1),
            (store_add, ":slot", ":num_options", 60),
            (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
            (val_sub, ":y", 40),
            (val_add, ":num_options", 1),
        (try_end),
        # Troubadour
        (create_button_overlay, reg0, "@A troubadour", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (store_add, ":slot", ":num_options", 60),
        (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
        (val_sub, ":y", 40),
        (val_add, ":num_options", 1),
        # Student
        (create_button_overlay, reg0, "@A university student", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (store_add, ":slot", ":num_options", 60),
        (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
        (val_sub, ":y", 40),
        (val_add, ":num_options", 1),
        # Peddler
        (create_button_overlay, reg0, "@A goods peddler", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (store_add, ":slot", ":num_options", 60),
        (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
        (val_sub, ":y", 40),
        (val_add, ":num_options", 1),
        # Smith
        (create_button_overlay, reg0, "@A smith", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (store_add, ":slot", ":num_options", 60),
        (troop_set_slot, "trp_temp_array_a", ":slot", reg0),
        (val_sub, ":y", 40),
        (val_add, ":num_options", 1),
        # Poacher
        (create_button_overlay, reg0, "@A game poacher", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (store_add, ":slot", ":num_options", 60),
        (troop_set_slot, "trp_temp_array_a", ":slot", reg0),

        # Store number of options for handler
        (troop_set_slot, "trp_temp_array_a", 59, ":num_options"),

    (else_try),
        (eq, "$g_coop_creation_step", 4),
        # Reason for adventuring
        (create_text_overlay, reg0, "@You decided to become an adventurer because...", tf_center_justify|tf_with_outline),
        (overlay_set_color, reg0, 0xFFFFFF),
        (position_set_x, pos1, 500),
        (position_set_y, pos1, 680),
        (overlay_set_position, reg0, pos1),
        (position_set_x, pos1, 1500),
        (position_set_y, pos1, 1500),
        (overlay_set_size, reg0, pos1),

        (assign, ":y", 600),
        (create_button_overlay, reg0, "@You wanted personal revenge", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 60, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@You lost a loved one", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 61, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@You had a taste for adventure", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 62, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@You were forced out of your home", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 63, reg0),
        (val_sub, ":y", 45),
        (create_button_overlay, reg0, "@You wanted money and power", 0),
        (position_set_x, pos1, 200),
        (position_set_y, pos1, ":y"),
        (overlay_set_position, reg0, pos1),
        (troop_set_slot, "trp_temp_array_a", 64, reg0),
    (try_end),
  ]),

  # ==================================================================
  # CAMPAIGN: PLAYER LIFECYCLE (join/exit/defeat/initial info)
  # ==================================================================

	("multiplayer_campaign_send_initial_information",
	[
		(store_script_param, ":player_no", 1),
	 
		(try_for_parties, ":party_no"),
			(party_get_banner_icon, ":banner_icon", ":party_no"),
			(try_begin),
				(gt, ":banner_icon", 0),
				(multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_party_set_banner_icon, ":party_no", ":banner_icon"),
			(try_end),
			
			(party_get_extra_icon, ":extra_icon", ":party_no"),
			(try_begin),
				(gt, ":extra_icon", 0),
				(multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_party_set_extra_icon, ":party_no", ":extra_icon"),
			(try_end),
			
			(party_get_slot, ":state", ":party_no", slot_village_state),
			(try_begin),
				(this_or_next|eq, ":state", svs_being_raided),
				(this_or_next|eq, ":state", svs_looted),
				(eq, ":state", svs_under_siege),
				(multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_party_set_extra_text, ":party_no", ":state"),
			(try_end),
			
			(party_get_slot, ":state", ":party_no", slot_village_smoke_added),
			(try_begin),
				(this_or_next|eq, ":state", 1),
				(eq, ":state", 2),
				(multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_party_add_particle_system, ":party_no", ":state"),
			(try_end),
		(try_end),
    ]),

   ("multiplayer_campaign_player_joined",
   [
		(store_script_param, ":player_no", 1),

		(store_mission_timer_a, ":player_join_time"),
		(player_set_slot, ":player_no", slot_player_join_time, ":player_join_time"),
		
		(str_store_player_username, s0, ":player_no"),
	   
		(store_add, ":troop_no", multiplayer_campaign_player_troops_begin, ":player_no"),
		(troop_set_name, ":troop_no", s0),
		(player_set_troop_id, ":player_no", ":troop_no"),
	   
		(store_add, ":party_no", multiplayer_campaign_player_parties_begin, ":player_no"),
		(party_set_name, ":party_no", s0),
		(player_set_party_id, ":player_no", ":party_no"),
		(enable_party, ":party_no"),

		# Load persisted character or create defaults
		(call_script, "script_coop_load_character", ":player_no"),
		(assign, ":char_loaded", reg0),

		# Apply results for every slot with a pending or ended battle.
		# (A failed condition op inside try_for_range skips to the next
		# iteration, so this visits all slots.)
		(try_for_range, ":bslot", 0, coop_battle_num_slots),
			(call_script, "script_coop_battle_slot_get_in_progress", ":bslot"),
			(assign, ":bs_pending", reg0),
			(call_script, "script_coop_battle_slot_get_ended", ":bslot"),
			(val_add, ":bs_pending", reg0),
			(gt, ":bs_pending", 0),
			(call_script, "script_coop_apply_battle_results", ":player_no", ":bslot"),
		(try_end),

		# Re-announce battles still open, so a (re)joining client's B-key
		# chooser isn't blind to fights started before it connected. The
		# chooser table is client-side state and dies with the connection;
		# only the ev-10 push can rebuild it. Runs after the apply loop so
		# finished slots have already been consumed and closed.
		(try_for_range, ":aslot", 0, coop_battle_num_slots),
			(call_script, "script_coop_battle_slot_get_in_progress", ":aslot"),
			(eq, reg0, 1),
			(call_script, "script_coop_battle_slot_get_ended", ":aslot"),
			(eq, reg0, 0),
			(assign, ":ann_state", coop_battle_state_none),
			(assign, ":ann_enemy", -1),
			(dict_create, ":ann_dict"),
			(try_begin),
				(call_script, "script_coop_battle_slot_dict_name", ":aslot"),
				(dict_load_file, ":ann_dict", s41, 2),
				(dict_get_int, ":ann_state", ":ann_dict", "@battle_state"),
				(call_script, "script_coop_battle_dict_has_roster_party", ":ann_dict", 0, 0),
				(eq, reg0, 1),
				(call_script, "script_coop_battle_dict_read_roster_party", ":ann_dict", 0, 0),
				(assign, ":ann_enemy", reg0),
			(try_end),
			(dict_free, ":ann_dict"),
			(ge, ":ann_state", coop_battle_state_setup_sp),
			(le, ":ann_state", coop_battle_state_started),
			(gt, ":ann_enemy", 0),
			(store_mul, ":ann_port", ":aslot", 2),
			(val_add, ":ann_port", coop_battle_port_base),
			(multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_available, ":ann_port", 0, ":ann_enemy"),
		(try_end),

		# ========================================================
		# Phase 2: apply this player's pending SP XP delta (if any)
		# ========================================================
		# Every rejoiner runs this; if @char_battle_pending was stashed
		# during Phase 1 of a prior rejoin (or this one), apply now.
		# Decoupled from battle_state so late rejoiners still get their
		# delta even after battle_state has been cleared.
		(assign, ":phase2_applied", 0),
		(str_store_player_username, s10, ":player_no"),
		(str_store_string, s11, "@coop_char_{s10}"),
		(dict_create, "$coop_char_apply_dict"),
		(dict_load_file, "$coop_char_apply_dict", s11),
		(try_begin),
			(dict_has_key, "$coop_char_apply_dict", "@char_battle_pending"),
			(dict_get_int, ":pending_flag", "$coop_char_apply_dict", "@char_battle_pending"),
			(eq, ":pending_flag", 1),

			(player_get_party_id, ":party_no", ":player_no"),
			(dict_get_int, ":party_share", "$coop_char_apply_dict", "@char_pending_party_xp"),
			(dict_get_int, ":hero_share",  "$coop_char_apply_dict", "@char_pending_hero_xp"),

			(call_script, "script_coop_apply_xp_shares", ":player_no", ":party_share", ":hero_share"),

			# Clear pending so subsequent rejoins don't double-apply
			(dict_set_int, "$coop_char_apply_dict", "@char_battle_pending", 0),
			(dict_set_int, "$coop_char_apply_dict", "@char_pending_party_xp", 0),
			(dict_set_int, "$coop_char_apply_dict", "@char_pending_hero_xp", 0),
			(dict_save, "$coop_char_apply_dict", s11),
			(assign, ":phase2_applied", 1),
		(try_end),
		(dict_free, "$coop_char_apply_dict"),

		# Persist Phase 2 XP. Phase 1 (coop_apply_battle_results) already
		# saves internally at :52191, so we only save here when Phase 2
		# actually applied. Plain rejoins skip this -- the post-load troop
		# state matches the dict, so there's nothing new to persist.
		# The dict_save above must land before coop_save_character runs --
		# its preserve block reads @char_pending_* from disk, not memory.
		(try_begin),
			(eq, ":phase2_applied", 1),
			(call_script, "script_coop_save_character", ":player_no"),
		(try_end),

		# Char sync must precede the inventory pushes: the engine bounds
		# troop_set_inventory_slot by getNumInventorySlots()+10 (skill-derived,
		# 30+6*IM+10), so bag slots above the IM-0 cap are silently dropped
		# if they arrive before the skill push raises the client troop's IM.
		(call_script, "script_coop_send_char_sync_to_client", ":player_no"),
		(call_script, "script_coop_send_equipment_to_client", ":player_no"),
		(call_script, "script_coop_send_inventory_to_client", ":player_no"),
		(call_script, "script_coop_send_party_upgradeable_to_client", ":player_no"),
		(try_begin),
			(eq, ":char_loaded", 0),
			# No saved character -- trigger character creation
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_first_join, 0),
		(try_end),

		(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_camera_follow_party, ":party_no"),

		(call_script, "script_multiplayer_campaign_send_initial_information", ":player_no"),
		
		(try_for_players, ":current_player_no", 1),
			(multiplayer_send_2_int_to_player, ":current_player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_player_joined, ":player_no"),
		(try_end),
    ]),

	("multiplayer_campaign_player_exit",
	[
		(store_script_param, ":player_no", 1),

		(player_get_party_id, ":party_no", ":player_no"),

		# Re-enable before saving so a party that was disabled at local-fight
		# start (event 16) still has its roster persisted. coop_save_character
		# skips the troop-stack save for inactive parties, and disable_party
		# only hides the party -- the roster still lives in the party struct.
		(enable_party, ":party_no"),
		(call_script, "script_coop_save_character", ":player_no"),
		(try_begin),
			(party_is_active, ":party_no"),
			(disable_party, ":party_no"),
		(try_end),

		# Release center lock held by this player
		(player_get_slot, ":locked_center", ":player_no", slot_player_coop_locked_center),
		(try_begin),
			(gt, ":locked_center", 0),
			(party_set_slot, ":locked_center", slot_center_coop_lock_player, -1),
			(player_set_slot, ":player_no", slot_player_coop_locked_center, 0),
		(try_end),

		(try_for_players, ":current_player_no", 1),
			(multiplayer_send_2_int_to_player, ":current_player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_player_exit, ":player_no"),
		(try_end),
	]),

	("multiplayer_campaign_player_party_defeated",
	[
		(store_script_param, ":party_no", 1),

		(assign, ":max_dist", 0),
		(party_get_position, pos1, ":party_no"),
		(try_for_range, ":unused", 0, 10),
			(map_get_random_position_around_position, pos0, pos1, 10),
			(get_distance_between_positions, ":dist", pos0, pos1),
			(ge, ":dist", ":max_dist"),
			(assign, ":max_dist", ":dist"),
			(copy_position, pos2, pos0),
		(try_end),  

		(party_set_position, ":party_no", pos2),
		
		(party_get_player_id, ":player_no", ":party_no"),
		(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_camera_follow_party, ":party_no"),
		
		(try_for_players, ":current_player_no", 1),
			(multiplayer_send_2_int_to_player, ":current_player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_player_party_defeated, ":player_no"),
		(try_end),
	]),

	# script_coop_find_player_no_by_name
	# Input: s1 holds the target username
	# Output: reg0 = player_no if matched, -1 if no active player has that name
	#
	# Used by Phase 1 stash logic to map each @battle_player_{i}_name entry
	# back to a currently connected player_no, so we can look up their
	# campaign party_id and decide host vs joiner routing.
	("coop_find_player_no_by_name", [
		(assign, ":result", -1),
		(try_for_players, ":candidate_pno", 1),
			(player_is_active, ":candidate_pno"),
			(str_store_player_username, s2, ":candidate_pno"),
			(try_begin),
				(str_equals, s1, s2),
				(assign, ":result", ":candidate_pno"),
			(try_end),
		(try_end),
		(assign, reg0, ":result"),
	]),

  # ==================================================================
  # CLIENT SCREEN-CLOSE DIFFS
  # One script per native screen, mirroring the char field sync
  # contract: each owns its snapshot layout and its sends. The 0.5s
  # poller in module_simple_triggers.py holds only the open/closed
  # gates and delegates here.
  # ==================================================================

	# Party screen closed: diff vs the trp_temp_troop snapshot, send
	# upgrades then dismissals.
	("coop_party_client_diff_and_send", [

          (multiplayer_get_my_player, ":my_player"),
          (player_get_party_id, ":my_party", ":my_player"),

          (troop_get_slot, ":snap_count", "trp_temp_troop", slot_coop_party_snap_count),

          # Pass 1: compute decrease deltas, store in snapshot slot 2
          (try_for_range, ":i", 0, ":snap_count"),
              (store_mul, ":base", ":i", slot_coop_party_snap_stride),
              (val_add, ":base", slot_coop_party_snap_begin),
              (troop_get_slot, ":snap_troop", "trp_temp_troop", ":base"),
              (store_add, ":off", ":base", 1),
              (troop_get_slot, ":snap_size", "trp_temp_troop", ":off"),
              (assign, ":cur_size", 0),
              (party_get_num_companion_stacks, ":num_cur", ":my_party"),
              (try_for_range, ":j", 0, ":num_cur"),
                  (party_stack_get_troop_id, ":ct", ":my_party", ":j"),
                  (eq, ":ct", ":snap_troop"),
                  (party_stack_get_size, ":cur_size", ":my_party", ":j"),
              (try_end),
              (store_sub, ":delta", ":snap_size", ":cur_size"),
              (val_max, ":delta", 0),
              (store_add, ":off", ":base", 2),
              (troop_set_slot, "trp_temp_troop", ":off", ":delta"),
          (try_end),

          # Pass 2: find increases in current party, match to upgrades
          (party_get_num_companion_stacks, ":num_cur", ":my_party"),
          (try_for_range, ":j", 0, ":num_cur"),
              (party_stack_get_troop_id, ":cur_troop", ":my_party", ":j"),
              (party_stack_get_size, ":cur_size", ":my_party", ":j"),
              (assign, ":was", 0),
              (try_for_range, ":i", 0, ":snap_count"),
                  (store_mul, ":base", ":i", slot_coop_party_snap_stride),
                  (val_add, ":base", slot_coop_party_snap_begin),
                  (troop_get_slot, ":st", "trp_temp_troop", ":base"),
                  (eq, ":st", ":cur_troop"),
                  (store_add, ":off", ":base", 1),
                  (troop_get_slot, ":was", "trp_temp_troop", ":off"),
              (try_end),
              (gt, ":cur_size", ":was"),
              (store_sub, ":added", ":cur_size", ":was"),
              (try_for_range, ":i", 0, ":snap_count"),
                  (gt, ":added", 0),
                  (store_mul, ":base", ":i", slot_coop_party_snap_stride),
                  (val_add, ":base", slot_coop_party_snap_begin),
                  (troop_get_slot, ":src", "trp_temp_troop", ":base"),
                  (store_add, ":off", ":base", 2),
                  (troop_get_slot, ":rem", "trp_temp_troop", ":off"),
                  (gt, ":rem", 0),
                  (assign, ":match", 0),
                  (troop_get_upgrade_troop, ":upg", ":src", 0),
                  (try_begin),
                      (eq, ":upg", ":cur_troop"),
                      (assign, ":match", 1),
                  (else_try),
                      (troop_get_upgrade_troop, ":upg", ":src", 1),
                      (eq, ":upg", ":cur_troop"),
                      (assign, ":match", 1),
                  (try_end),
                  (eq, ":match", 1),
                  (assign, ":n", ":added"),
                  (val_min, ":n", ":rem"),
                  (val_sub, ":rem", ":n"),
                  (troop_set_slot, "trp_temp_troop", ":off", ":rem"),
                  (val_sub, ":added", ":n"),
                  (multiplayer_send_4_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
                      multiplayer_event_multiplayer_campaign_party_upgrade, ":src", ":cur_troop", ":n"),
              (try_end),
          (try_end),

          # Pass 3: send remaining unmatched decreases as dismissals
          (try_for_range, ":i", 0, ":snap_count"),
              (store_mul, ":base", ":i", slot_coop_party_snap_stride),
              (val_add, ":base", slot_coop_party_snap_begin),
              (troop_get_slot, ":snap_troop", "trp_temp_troop", ":base"),
              (store_add, ":off", ":base", 2),
              (troop_get_slot, ":rem", "trp_temp_troop", ":off"),
              (gt, ":rem", 0),
              (multiplayer_send_3_int_to_server, multiplayer_event_multiplayer_campaign_client_events,
                  multiplayer_event_multiplayer_campaign_party_dismiss, ":snap_troop", ":rem"),
          (try_end),
	]),

	# Inventory screen closed: diff equip + bag slots vs snapshot, send
	# inv_change per slot then inv_sync_back_done.
	("coop_inv_client_diff_and_send", [

          (multiplayer_get_my_player, ":my_player"),
          (player_get_troop_id, ":my_troop", ":my_player"),

          # Diff equipment slots 0-9
          (try_for_range, ":slot", 0, 10),
              (troop_get_inventory_slot, ":cur_item", ":my_troop", ":slot"),
              (troop_get_inventory_slot_modifier, ":cur_mod", ":my_troop", ":slot"),
              (store_add, ":snap_item_slot", slot_coop_inv_snap_equip_item_begin, ":slot"),
              (troop_get_slot, ":snap_item", "trp_temp_troop", ":snap_item_slot"),
              (store_add, ":snap_mod_slot", slot_coop_inv_snap_equip_mod_begin, ":slot"),
              (troop_get_slot, ":snap_mod", "trp_temp_troop", ":snap_mod_slot"),
              (assign, ":changed", 0),
              (try_begin),
                  (neq, ":cur_item", ":snap_item"),
                  (assign, ":changed", 1),
              (else_try),
                  (neq, ":cur_mod", ":snap_mod"),
                  (assign, ":changed", 1),
              (try_end),
              (eq, ":changed", 1),
              (multiplayer_send_4_int_to_server,
                  multiplayer_event_multiplayer_campaign_client_events,
                  multiplayer_event_multiplayer_campaign_inv_change,
                  ":slot", ":cur_item", ":cur_mod"),
          (try_end),

          # Diff bag slots 10-105
          (try_for_range, ":slot", 10, 106),
              (troop_get_inventory_slot, ":cur_item", ":my_troop", ":slot"),
              (troop_get_inventory_slot_modifier, ":cur_mod", ":my_troop", ":slot"),
              (store_sub, ":offset", ":slot", 10),
              (store_add, ":snap_item_slot", slot_coop_inv_snap_bag_item_begin, ":offset"),
              (troop_get_slot, ":snap_item", "trp_temp_troop", ":snap_item_slot"),
              (store_add, ":snap_mod_slot", slot_coop_inv_snap_bag_mod_begin, ":offset"),
              (troop_get_slot, ":snap_mod", "trp_temp_troop", ":snap_mod_slot"),
              (assign, ":changed", 0),
              (try_begin),
                  (neq, ":cur_item", ":snap_item"),
                  (assign, ":changed", 1),
              (else_try),
                  (neq, ":cur_mod", ":snap_mod"),
                  (assign, ":changed", 1),
              (try_end),
              (eq, ":changed", 1),
              (multiplayer_send_4_int_to_server,
                  multiplayer_event_multiplayer_campaign_client_events,
                  multiplayer_event_multiplayer_campaign_inv_change,
                  ":slot", ":cur_item", ":cur_mod"),
          (try_end),

          # Signal batch done -> server saves
          (multiplayer_send_int_to_server,
              multiplayer_event_multiplayer_campaign_client_events,
              multiplayer_event_multiplayer_campaign_inv_sync_back_done),
	]),

	# Trade screen closed: diff merchant inventory vs snapshot, send
	# trade_change per slot then trade_done with the gold delta.
	("coop_trade_client_diff_and_send", [

          (multiplayer_get_my_player, ":my_player"),
          (player_get_troop_id, ":my_troop", ":my_player"),

          # Diff merchant inventory against snapshot in trp_temp_array_b
          (try_for_range, ":slot", 0, 96),
              (troop_get_inventory_slot, ":cur_item", "trp_find_item_cheat", ":slot"),
              (troop_get_inventory_slot_modifier, ":cur_mod", "trp_find_item_cheat", ":slot"),
              (store_add, ":snap_item_slot", slot_coop_trade_snap_item_begin, ":slot"),
              (troop_get_slot, ":snap_item", "trp_temp_array_b", ":snap_item_slot"),
              (store_add, ":snap_mod_slot", slot_coop_trade_snap_mod_begin, ":slot"),
              (troop_get_slot, ":snap_mod", "trp_temp_array_b", ":snap_mod_slot"),
              (assign, ":changed", 0),
              (try_begin),
                  (neq, ":cur_item", ":snap_item"),
                  (assign, ":changed", 1),
              (else_try),
                  (neq, ":cur_mod", ":snap_mod"),
                  (assign, ":changed", 1),
              (try_end),
              (eq, ":changed", 1),
              (multiplayer_send_4_int_to_server,
                  multiplayer_event_multiplayer_campaign_client_events,
                  multiplayer_event_multiplayer_campaign_trade_change,
                  ":slot", ":cur_item", ":cur_mod"),
          (try_end),

          # Compute gold delta and send trade_done
          (store_troop_gold, ":cur_gold", ":my_troop"),
          (store_sub, ":gold_delta", ":cur_gold", "$g_coop_trade_gold_before"),
          (multiplayer_send_2_int_to_server,
              multiplayer_event_multiplayer_campaign_client_events,
              multiplayer_event_multiplayer_campaign_trade_done, ":gold_delta"),

          # Player inventory diff is handled by the inv_screen_open block above
          # (wse_window_opened already set $g_coop_inv_screen_open=1 when trade opened)
	]),

  # ==================================================================
  # CAMPAIGN: NETWORK EVENT HANDLERS (extracted arms)
  # Rule: a dispatcher arm that exceeds ~10 lines or needs a comment
  # gets a named coop_ev_srv_* / coop_ev_cli_* script here; shorter
  # arms stay inline in the dispatcher.
  # ==================================================================

	# ch125 ev 2: map-party status text. Input: party_no, svs_* state.
	("coop_ev_srv_party_set_extra_text", [
		(store_script_param, ":party_no", 1),
		(store_script_param, ":state", 2),
		(try_begin),
			(eq, ":state", svs_normal),
			(party_set_extra_text, ":party_no", "str_empty_string"),
		(else_try),
			(eq, ":state", svs_being_raided),
			(party_set_extra_text, ":party_no", "@(Being Raided)"),
		(else_try),
			(eq, ":state", svs_looted),
			(party_set_extra_text, ":party_no", "@(Looted)"),
		(else_try),
			(eq, ":state", svs_under_siege),
			(party_set_extra_text, ":party_no", "@(Under Siege)"),
		(try_end),
	]),

	# ch125 ev 3: map-party particle state (1 = burning, 2 = looted).
	("coop_ev_srv_party_add_particle_system", [
		(store_script_param, ":party_no", 1),
		(store_script_param, ":state", 2),
		(try_begin),
			(eq, ":state", 1),
			(party_add_particle_system, ":party_no", "psys_map_village_fire"),
			(party_add_particle_system, ":party_no", "psys_map_village_fire_smoke"),
		(else_try),
			(eq, ":state", 2),
			(party_clear_particle_systems, ":party_no"),
			(party_add_particle_system, ":party_no", "psys_map_village_looted_smoke"),
		(else_try),
			(party_clear_particle_systems, ":party_no"),
		(try_end),
	]),

	# ch125 ev 5: join announcement + username/face on the joined troop.
	("coop_ev_srv_player_joined", [
		(store_script_param, ":player_no", 1),
		(str_store_player_username, s0, ":player_no"),
		(display_message, "@{s0} has joined the game."),
		(try_begin),
			(player_get_troop_id, ":troop_no", ":player_no"),
			(ge, ":troop_no", 0),
			(troop_set_name, ":troop_no", s0),
			(str_store_player_face_keys, s1, ":player_no"),
			(troop_set_face_keys, ":troop_no", s1),
		(try_end),
	]),

	# ch125 ev 8: store encounter data and open the encounter menu.
	("coop_ev_srv_player_start_encounter", [
		(store_script_param, ":encountered_party", 1),
		(store_script_param, ":encountered_party_2", 2),
		(store_script_param, ":terrain", 3),
		(assign, "$g_encountered_party", ":encountered_party"),
		(assign, "$g_encountered_party_2", ":encountered_party_2"),
		(assign, "$g_coop_local_battle_terrain", ":terrain"),
		(try_begin),
			(gt, ":encountered_party", 0),
			(party_get_num_companions, "$g_encounter_enemy_count", ":encountered_party"),
		(else_try),
			(assign, "$g_encounter_enemy_count", 0),
		(try_end),
		(assign, "$g_coop_encounter_done", 0),
		(jump_to_menu, "mnu_multiplayer_campaign_encounter"),
	]),

	# ch125 ev 10: battle server ready on a port. Initiator defers a
	# connect to the game-loop trigger; everyone else arms the B-key
	# chooser for that slot.
	("coop_ev_srv_battle_available", [
		(store_script_param, ":bport", 1),
		(store_script_param, ":is_initiator", 2),
		(store_script_param, ":enemy_party", 3),
		(try_begin),
			# Initiator: connect straight away (they clicked the menu).
			(eq, ":is_initiator", 1),
			(eq, "$g_coop_battle_requested", 1),
			(assign, "$g_coop_battle_requested", 0),
			# Build battle address from stored server IP (s59) + port.
			# multiplayer_connect_to_server must run from game-loop
			# context, not the network receive handler -- defer to the
			# simple trigger via a pending flag.
			(assign, reg10, ":bport"),
			(str_store_string, s58, "@{s59}:{reg10}"),
			(display_message, "@Connecting to battle server: {s58}"),
			(assign, "$g_coop_battle_connect_pending", 1),
		(else_try),
			# Non-initiator: record this slot in the battle chooser table.
			# Never while our own request is in flight -- a pending
			# initiator joining someone else's battle would orphan their
			# allocated slot.
			(neq, "$g_coop_battle_requested", 1),
			(store_sub, ":slot", ":bport", coop_battle_port_base),
			(val_div, ":slot", 2),
			(call_script, "script_coop_battle_chooser_set", ":slot", ":bport", ":enemy_party"),
			(str_store_party_name, s0, ":enemy_party"),
			(display_message, "@Battle started vs {s0} -- press B to pick a battle.", 0xFF44FF44),
		(try_end),
	]),

	# Shared tail of ch49 ev 1 (start_battle) and ev 26 (request_siege):
	# allocate a pool slot, save all characters, serialize the battle
	# dict, and announce battle_available to every player. Rejects with
	# ch125 ev 44 when the pool is full.
	("coop_battle_launch_on_free_slot", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":ally_party", 2),
		(store_script_param, ":target_party", 3),
		(store_script_param, ":battle_type", 4),
		(str_store_player_username, s0, ":player_no"),
		(call_script, "script_coop_battle_find_free_slot"),
		(assign, ":slot", reg0),
		(try_begin),
			(lt, ":slot", 0),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_rejected, 0),
			(try_begin),
				(eq, ":battle_type", coop_battle_type_field_battle),
				(display_message, "@{s0}: battle rejected -- no free battle server slot."),
			(else_try),
				(display_message, "@{s0}: siege rejected -- no free battle server slot."),
			(try_end),
		(else_try),
			(try_begin),
				(eq, ":battle_type", coop_battle_type_field_battle),
				(party_get_num_companions, ":player_count", ":ally_party"),
				(party_get_num_companions, ":enemy_count", ":target_party"),
				(assign, reg1, ":player_count"),
				(assign, reg2, ":enemy_count"),
				(assign, reg3, ":slot"),
				(display_message, "@{s0}: Writing battle data (slot {reg3}) -- {reg1} allies vs {reg2} enemies."),
			(try_end),

			# Save all connected players' characters before battle
			(get_max_players, ":max_p"),
			(try_for_range, ":p", 1, ":max_p"),
				(player_is_active, ":p"),
				(call_script, "script_coop_save_character", ":p"),
			(try_end),

			# Write encounter data to this slot's dict file
			(call_script, "script_coop_write_battle_data", ":ally_party", ":target_party", ":battle_type", ":slot"),
			(call_script, "script_coop_battle_slot_set_in_progress", ":slot", 1),

			# Announce to ALL players (initiator included) with the slot's
			# port and the target party id (clients resolve the name locally).
			(store_mul, ":bport", ":slot", 2),
			(val_add, ":bport", coop_battle_port_base),
			(get_max_players, ":num_players"),
			(try_for_range, ":cur_player", 1, ":num_players"),
				(player_is_active, ":cur_player"),
				(assign, ":is_init", 0),
				(try_begin),
					(eq, ":cur_player", ":player_no"),
					(assign, ":is_init", 1),
				(try_end),
				(multiplayer_send_4_int_to_player, ":cur_player", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_available, ":bport", ":is_init", ":target_party"),
			(try_end),
		(try_end),
	]),

	# ch49 ev 1: player asks for a dedicated field battle vs their
	# current battle opponent.
	("coop_ev_cli_start_battle", [
		(store_script_param, ":player_no", 1),
		(str_store_player_username, s0, ":player_no"),
		(player_get_party_id, ":player_party", ":player_no"),
		(party_get_battle_opponent, ":enemy_party", ":player_party"),
		(try_begin),
			(gt, ":enemy_party", 0),
			(party_is_active, ":enemy_party"),
			(call_script, "script_coop_battle_launch_on_free_slot", ":player_no", ":player_party", ":enemy_party", coop_battle_type_field_battle),
		(else_try),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_rejected, 0),
			(display_message, "@{s0}: No valid enemy for battle -- auto-calc fallback."),
			(try_begin),
				(gt, ":player_party", 0),
				(party_is_active, ":player_party"),
				(party_leave_cur_battle, ":player_party"),
			(try_end),
			(leave_encounter),
			(end_current_battle),
		(try_end),
	]),

	# ch49 ev 26: player assaults a center -- siege on the battle server.
	# The center party itself is the besieged target; its garrison defends.
	("coop_ev_cli_request_siege", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":center_party", 2),
		(str_store_player_username, s0, ":player_no"),
		(player_get_party_id, ":player_party", ":player_no"),
		(try_begin),
			(gt, ":center_party", 0),
			(party_is_active, ":center_party"),
			(call_script, "script_coop_battle_launch_on_free_slot", ":player_no", ":player_party", ":center_party", coop_battle_type_siege_player_attack),
		(else_try),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_rejected, 0),
			(display_message, "@{s0}: Siege target invalid."),
		(try_end),
	]),

	# ch125 ev 22: per-stack num_upgradeable push onto my party.
	("coop_ev_srv_party_stack_num_upgradeable", [
		(store_script_param, ":stack_idx", 1),
		(store_script_param, ":stack_upg", 2),
		(multiplayer_get_my_player, ":my_player"),
		(player_get_party_id, ":my_party", ":my_player"),
		(try_begin),
			(party_is_active, ":my_party"),
			(party_get_num_companion_stacks, ":ns", ":my_party"),
			(lt, ":stack_idx", ":ns"),
			(party_stack_set_num_upgradeable, ":my_party", ":stack_idx", ":stack_upg"),
		(try_end),
	]),

	# ch49 ev 27: local siege vs AI; server replies ch125 ev 42.
	("coop_ev_cli_request_siege_local", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":center_party", 2),
            # Player leads the wall assault locally (SP-style vs AI). Mirrors
            # start_local_fight (busy flag, baseline save, freeze party), plus
            # stashes the assaulted center in the char dict so the event-17
            # aftermath knows this was a siege. The wall scene must be sent
            # from here -- center party slots are not synced to clients.
            (str_store_player_username, s0, ":player_no"),
            (try_begin),
                (gt, ":center_party", 0),
                (party_is_active, ":center_party"),
                (party_get_slot, ":ptype", ":center_party", slot_party_type),
                (this_or_next|eq, ":ptype", spt_town),
                (eq, ":ptype", spt_castle),
                (try_begin),
                    (eq, ":ptype", spt_town),
                    (party_get_slot, ":wall_scene", ":center_party", slot_town_walls),
                (else_try),
                    (party_get_slot, ":wall_scene", ":center_party", slot_castle_exterior),
                (try_end),
                (gt, ":wall_scene", 0),
                (display_message, "@{s0}: Entering local siege assault."),
                (player_set_slot, ":player_no", slot_player_coop_in_local_encounter, 1),
                (call_script, "script_coop_save_character", ":player_no"),
                (call_script, "script_coop_char_siege_center_set", ":player_no", ":center_party"),
                (player_get_party_id, ":ls_party", ":player_no"),
                (try_begin),
                    (party_is_active, ":ls_party"),
                    (disable_party, ":ls_party"),
                    (display_message, "@{s0}: party frozen for local siege."),
                (try_end),
                # Belfry flag picks the mission variant client-side (the slot
                # is not synced to clients).
                (party_get_slot, ":with_belfry", ":center_party", slot_center_siege_with_belfry),
                (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                    multiplayer_event_multiplayer_campaign_server_event_start_siege_local, ":wall_scene", ":with_belfry"),
            (else_try),
                (display_message, "@{s0}: Local siege target invalid."),
            (try_end),
        	]),

	# ch49 ev 3: final char-creation choice -- create the character.
	("coop_ev_cli_char_creation_life", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":adulthood", 2),
		(store_script_param, ":reason", 3),
            (player_get_slot, ":gender", ":player_no", 55),
            (player_get_slot, ":father", ":player_no", 56),
            (player_get_slot, ":earlylife", ":player_no", 57),
            (call_script, "script_coop_apply_character_creation", ":player_no", ":gender", ":father", ":earlylife", ":adulthood", ":reason"),
            # Char sync first (fresh attrs/skills/profs): keeps the next
            # C-screen snapshot in step with server state, and the engine
            # bounds inventory-slot writes by the skill-derived capacity --
            # skills must land on the client troop before bag slots (same
            # ordering as multiplayer_campaign_player_joined).
            (call_script, "script_coop_send_char_sync_to_client", ":player_no"),
            (call_script, "script_coop_send_equipment_to_client", ":player_no"),
            (call_script, "script_coop_send_inventory_to_client", ":player_no"),
            (call_script, "script_coop_save_character", ":player_no"),
        	]),

	# ch49 ev 10: dismiss troops from the player party.
	("coop_ev_cli_party_dismiss", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":dismiss_troop", 2),
		(store_script_param, ":dismiss_count", 3),
            (player_get_party_id, ":party_no", ":player_no"),
            (try_begin),
                (party_is_active, ":party_no"),
                (gt, ":dismiss_count", 0),
                (le, ":dismiss_count", 100),
                (neg|troop_is_hero, ":dismiss_troop"),
                (party_count_members_of_type, ":have", ":party_no", ":dismiss_troop"),
                (ge, ":have", ":dismiss_count"),
                (party_remove_members, ":party_no", ":dismiss_troop", ":dismiss_count"),
                (call_script, "script_coop_save_character", ":player_no"),
            (try_end),
        	]),

	# ch49 ev 11: upgrade a stack in the player party.
	("coop_ev_cli_party_upgrade", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":from_troop", 2),
		(store_script_param, ":to_troop", 3),
		(store_script_param, ":upg_count", 4),
            (player_get_party_id, ":party_no", ":player_no"),
            (try_begin),
                (party_is_active, ":party_no"),
                (gt, ":upg_count", 0),
                (le, ":upg_count", 100),
                (neg|troop_is_hero, ":from_troop"),
                # Validate upgrade path
                (assign, ":valid", 0),
                (troop_get_upgrade_troop, ":upg1", ":from_troop", 0),
                (try_begin),
                    (eq, ":upg1", ":to_troop"),
                    (assign, ":valid", 1),
                (else_try),
                    (troop_get_upgrade_troop, ":upg2", ":from_troop", 1),
                    (eq, ":upg2", ":to_troop"),
                    (assign, ":valid", 1),
                (try_end),
                (eq, ":valid", 1),
                (party_count_members_of_type, ":have", ":party_no", ":from_troop"),
                (ge, ":have", ":upg_count"),
                # Charge the native upgrade gold cost. The client engine already
                # deducted this locally in the party screen (game_get_upgrade_cost
                # by from-troop level); the server must mirror it or the next gold
                # push refunds the client, making upgrades free. Reject if the
                # player can no longer afford it (forged/oversized ev-11).
                (call_script, "script_game_get_upgrade_cost", ":from_troop"),
                (store_mul, ":upg_cost", reg0, ":upg_count"),
                (player_get_troop_id, ":up_trp", ":player_no"),
                (store_troop_gold, ":up_gold", ":up_trp"),
                (ge, ":up_gold", ":upg_cost"),
                (troop_remove_gold, ":up_trp", ":upg_cost"),
                (party_remove_members, ":party_no", ":from_troop", ":upg_count"),
                (party_add_members, ":party_no", ":to_troop", ":upg_count"),
                (call_script, "script_coop_save_character", ":player_no"),
            (try_end),
        	]),

	# ch49 ev 18: player enters a town/village center.
	("coop_ev_cli_enter_center", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":center_id", 2),
            (try_begin),
                (party_get_slot, ":ptype", ":center_id", slot_party_type),
                (this_or_next|eq, ":ptype", spt_town),
                (this_or_next|eq, ":ptype", spt_castle),
                (eq, ":ptype", spt_village),
                (party_get_slot, ":lock_player", ":center_id", slot_center_coop_lock_player),
                (assign, ":center_type", coop_center_type_village),
                (try_begin),
                    (eq, ":ptype", spt_town),
                    (assign, ":center_type", coop_center_type_town),
                (else_try),
                    (eq, ":ptype", spt_castle),
                    (assign, ":center_type", coop_center_type_castle),
                (try_end),
                (try_begin),
                    (eq, ":lock_player", -1),
                    (party_set_slot, ":center_id", slot_center_coop_lock_player, ":player_no"),
                    (player_set_slot, ":player_no", slot_player_coop_locked_center, ":center_id"),
                    (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                        multiplayer_event_multiplayer_campaign_server_event_center_encounter, ":center_id", ":center_type"),
                (else_try),
                    (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                        multiplayer_event_multiplayer_campaign_server_event_center_locked, ":center_id", 0),
                (try_end),
            (try_end),
        	]),

	# ch49 ev 22: trade closed -- apply and persist the result.
	("coop_ev_cli_trade_done", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":gold_delta", 2),
            (player_get_troop_id, ":troop_no", ":player_no"),
            # Apply gold delta (can be negative = player bought, positive = player sold)
            (try_begin),
                (gt, ":gold_delta", 0),
                (troop_add_gold, ":troop_no", ":gold_delta"),
            (else_try),
                (lt, ":gold_delta", 0),
                (store_mul, ":abs_delta", ":gold_delta", -1),
                (troop_remove_gold, ":troop_no", ":abs_delta"),
            (try_end),
            (call_script, "script_coop_save_character", ":player_no"),
            # Push corrected gold back
            (store_troop_gold, ":new_gold", ":troop_no"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_trade_gold_sync, ":new_gold"),
        	]),

	# ch49 ev 23: volunteer recruitment in a center.
	("coop_ev_cli_request_recruit", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":center_id", 2),
		(store_script_param, ":count", 3),
            # Validate lock
            (try_begin),
                (is_between, ":center_id", centers_begin, centers_end),
                (party_get_slot, ":lock_player", ":center_id", slot_center_coop_lock_player),
                (eq, ":lock_player", ":player_no"),
                (try_begin),
                    (eq, ":count", 0),
                    # Info request: send volunteer pool data
                    (party_get_slot, ":vol_troop", ":center_id", slot_center_volunteer_troop_type),
                    (party_get_slot, ":vol_amount", ":center_id", slot_center_volunteer_troop_amount),
                    (try_begin),
                        (gt, ":vol_troop", 0),
                        (gt, ":vol_amount", 0),
                        # Calculate cost per recruit (base cost from troop)
                        (call_script, "script_game_get_join_cost", ":vol_troop"),
                        (assign, ":cost_per", reg0),
                        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                            multiplayer_event_multiplayer_campaign_server_event_recruit_data, ":vol_troop", ":vol_amount", ":cost_per"),
                    (else_try),
                        # No volunteers
                        (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                            multiplayer_event_multiplayer_campaign_server_event_recruit_data, 0, 0, 0),
                    (try_end),
                (else_try),
                    # Actual recruit request (count > 0)
                    (gt, ":count", 0),
                    (party_get_slot, ":vol_troop", ":center_id", slot_center_volunteer_troop_type),
                    (party_get_slot, ":vol_amount", ":center_id", slot_center_volunteer_troop_amount),
                    (val_min, ":count", ":vol_amount"),
                    (gt, ":count", 0),
                    (call_script, "script_game_get_join_cost", ":vol_troop"),
                    (assign, ":cost_per", reg0),
                    (store_mul, ":total_cost", ":cost_per", ":count"),
                    (player_get_troop_id, ":troop_no", ":player_no"),
                    (store_troop_gold, ":gold", ":troop_no"),
                    (try_begin),
                        (ge, ":gold", ":total_cost"),
                        (troop_remove_gold, ":troop_no", ":total_cost"),
                        (player_get_party_id, ":party_no", ":player_no"),
                        (party_add_members, ":party_no", ":vol_troop", ":count"),
                        # Deplete volunteer pool
                        (store_sub, ":remaining", ":vol_amount", ":count"),
                        (try_begin),
                            (le, ":remaining", 0),
                            (party_set_slot, ":center_id", slot_center_volunteer_troop_type, -1),
                            (party_set_slot, ":center_id", slot_center_volunteer_troop_amount, 0),
                        (else_try),
                            (party_set_slot, ":center_id", slot_center_volunteer_troop_amount, ":remaining"),
                        (try_end),
                        (store_troop_gold, ":new_gold", ":troop_no"),
                        (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                            multiplayer_event_multiplayer_campaign_server_event_recruit_result, ":count", ":new_gold"),
                        (call_script, "script_coop_save_character", ":player_no"),
                    (else_try),
                        # Not enough gold
                        (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                            multiplayer_event_multiplayer_campaign_server_event_recruit_result, 0, ":gold"),
                    (try_end),
                (try_end),
            (try_end),
        # --- Local SP encounter server handlers (events 16, 17, 24, 25) ---
        	]),

	# ch49 ev 16: client starts a local SP-style fight.
	("coop_ev_cli_start_local_fight", [
		(store_script_param, ":player_no", 1),
            # Client is fighting encounter locally. Mark busy, save baseline,
            # and freeze the party so the server stops simulating it for the
            # duration of the local battle (mirrors player_exit). Rejoin
            # re-enables via enable_party in multiplayer_campaign_player_joined.
            (str_store_player_username, s0, ":player_no"),
            (display_message, "@{s0}: Entering local SP battle."),
            (player_set_slot, ":player_no", slot_player_coop_in_local_encounter, 1),
            (call_script, "script_coop_save_character", ":player_no"),
            # A field fight supersedes any abandoned local siege -- clear the
            # stash so its win can't be misread as a siege capture.
            (call_script, "script_coop_char_siege_center_set", ":player_no", 0),
            (player_get_party_id, ":lf_party", ":player_no"),
            (try_begin),
                (party_is_active, ":lf_party"),
                (disable_party, ":lf_party"),
                (display_message, "@{s0}: party frozen for local battle."),
            (try_end),
        	]),

	# ch49 ev 17: local fight outcome + XP delta from the client.
	("coop_ev_cli_local_fight_result", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":sub_type", 2),
		(store_script_param, ":p4", 3),
		(store_script_param, ":p5", 4),
            # Client reports local fight outcome.
            # Param 3: win_loss (1=win,-1=loss,0=retreat) OR -2 (per-stack casualty data)
            # When win_loss >= -1: param4 = total_casualties, param5 = xp_gained (delta)
            # When win_loss == -2: param4 = troop_id, param5 = killed_count
            (str_store_player_username, s0, ":player_no"),
            (try_begin),
                (neq, ":sub_type", -2),
                # Main result packet: win_loss, total_casualties, xp_gained.
                # p5 is a gained delta (debrief measured after-before), NOT an
                # absolute XP value.
                (assign, ":win_loss", ":sub_type"),
                (assign, ":total_casualties", ":p4"),
                (assign, ":xp_gained", ":p5"),
                (assign, reg1, ":win_loss"),
                (assign, reg2, ":total_casualties"),
                (assign, reg3, ":xp_gained"),
                (display_message, "@{s0}: Local fight result: win={reg1} casualties={reg2} xp_gained={reg3}"),
                # Clear busy flag
                (player_set_slot, ":player_no", slot_player_coop_in_local_encounter, 0),
                # Apply XP SP-style to hero + all troop stacks.
                (try_begin),
                    (gt, ":xp_gained", 0),
                    (call_script, "script_coop_apply_xp_shares", ":player_no", ":xp_gained", 0),
                (try_end),
                # Handle encounter aftermath
                (player_get_party_id, ":player_party", ":player_no"),
                # Local siege? request_siege_local stashed the assaulted
                # center in the char dict -- player_no and the slot-indexed
                # party are reassigned on the post-mission rejoin, so only
                # the username-keyed dict identifies the siege reliably.
                # (The center lock needs no handling here: the disconnect
                # into the local mission already released it via player_exit.)
                (call_script, "script_coop_char_siege_center_get", ":player_no"),
                (assign, ":siege_center", reg0),
                (try_begin),
                    (gt, ":siege_center", 0),
                    (call_script, "script_coop_char_siege_center_set", ":player_no", 0),
                    (assign, reg4, ":siege_center"),
                    (assign, reg5, ":win_loss"),
                    (display_message, "@[LOCAL SIEGE] center={reg4} win={reg5}"),
                    (try_begin),
                        (eq, ":win_loss", 1),
                        # Walls taken: the garrison is spent and the center falls.
                        (party_clear, ":siege_center"),
                        (call_script, "script_give_center_to_faction_aux", ":siege_center", "fac_player_faction"),
                        (str_store_party_name, s1, ":siege_center"),
                        (display_message, "@{s0} has captured {s1}!"),
                    (try_end),
                (else_try),
                    (eq, ":win_loss", 1),
                    # Victory: destroy enemy party. The engine won't remove
                    # an emptied party on its own; never remove centers (a
                    # local siege's opponent is the center, owned by the
                    # @char_siege_center capture block above).
                    (party_get_battle_opponent, ":enemy_party", ":player_party"),
                    (try_begin),
                        (gt, ":enemy_party", 0),
                        (party_is_active, ":enemy_party"),
                        (party_get_slot, ":enemy_type", ":enemy_party", slot_party_type),
                        (neq, ":enemy_type", spt_castle),
                        (neq, ":enemy_type", spt_town),
                        (neq, ":enemy_type", spt_village),
                        (party_leave_cur_battle, ":enemy_party"),
                        (party_clear, ":enemy_party"),
                        (remove_party, ":enemy_party"),
                    (try_end),
                (try_end),
                # Disengage from battle
                (try_begin),
                    (gt, ":player_party", 0),
                    (party_is_active, ":player_party"),
                    (party_leave_cur_battle, ":player_party"),
                (try_end),
                # Save character
                (call_script, "script_coop_save_character", ":player_no"),
                # Re-push char sync: the join-time push predates this event,
                # so the client's player/companion XP is stale until now.
                (call_script, "script_coop_send_char_sync_to_client", ":player_no"),
                # Notify client encounter is resolved
                (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                    multiplayer_event_multiplayer_campaign_server_event_encounter_resolved, 0),
            (else_try),
                # Per-stack casualty data: troop_id, killed_count
                (assign, ":troop_id", ":p4"),
                (assign, ":killed", ":p5"),
                (try_begin),
                    (gt, ":killed", 0),
                    (player_get_party_id, ":party_no", ":player_no"),
                    (party_get_skill_level, ":surgery", ":party_no", "skl_surgery"),
                    (val_mul, ":surgery", 4),
                    (call_script, "script_coop_apply_player_stack_casualty", ":party_no", ":troop_id", ":killed", 0, ":surgery"),
                (try_end),
            (try_end),
        	]),

  # ==================================================================
  # CAMPAIGN: NETWORK DISPATCHERS (channels 125/49)
  # ==================================================================

	("multiplayer_campaign_server_events",
	[
		(store_script_param, ":event_type", 1),
	 
		(try_begin),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_party_set_banner_icon),
			(store_script_param, ":party_no", 2),
            (store_script_param, ":banner_icon", 3),
			(party_set_banner_icon, ":party_no", ":banner_icon"),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_party_set_extra_icon),
			(store_script_param, ":party_no", 2),
            (store_script_param, ":extra_icon", 3),
			(party_set_extra_icon, ":party_no", ":extra_icon"),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_party_set_extra_text),
			(store_script_param, ":party_no", 2),
			(store_script_param, ":state", 3),
			(call_script, "script_coop_ev_srv_party_set_extra_text", ":party_no", ":state"),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_party_add_particle_system),
			(store_script_param, ":party_no", 2),
			(store_script_param, ":state", 3),
			(call_script, "script_coop_ev_srv_party_add_particle_system", ":party_no", ":state"),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_camera_follow_party),
			(store_script_param, ":party_no", 2),
			(set_camera_follow_party, ":party_no", 1),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_player_joined),
			(store_script_param, ":player_no", 2),
			(call_script, "script_coop_ev_srv_player_joined", ":player_no"),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_player_exit),
			(store_script_param, ":player_no", 2),
			(str_store_player_username, s0, ":player_no"),
			(display_message, "@{s0} has left the game."),
		(else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_player_party_defeated),
			(store_script_param, ":player_no", 2),
			(str_store_player_username, s0, ":player_no"),
			(display_message, "@{s0} was defeated in battle but managed to escape."),
        (else_try),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_player_start_encounter),
			(store_script_param, ":encountered_party", 2),
			(store_script_param, ":encountered_party_2", 3),
			(store_script_param, ":terrain", 4),
			(call_script, "script_coop_ev_srv_player_start_encounter", ":encountered_party", ":encountered_party_2", ":terrain"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_encounter_resolved),
            # Server resolved the battle - set flag for simple trigger to clear encounter
            # leave_encounter must run from game loop context, not network handler
            (assign, "$g_coop_encounter_done", 1),
		(else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_battle_available),
            (store_script_param, ":bport", 2),
            (store_script_param, ":is_initiator", 3),
            (store_script_param, ":enemy_party", 4),
            (call_script, "script_coop_ev_srv_battle_available", ":bport", ":is_initiator", ":enemy_party"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_battle_slot_closed),
            (store_script_param, ":closed_slot", 2),
            (call_script, "script_coop_battle_chooser_clear", ":closed_slot"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_battle_rejected),
            (store_script_param, ":reject_reason", 2),
            (assign, "$g_coop_battle_requested", 0),
            (try_begin),
                (eq, ":reject_reason", 1),
                (display_message, "@Battle server lost -- battle aborted.", 0xFFFF4444),
            (else_try),
                (display_message, "@All battle servers are busy -- try again shortly.", 0xFFFF4444),
            (try_end),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_first_join),
            (assign, "$g_coop_creation_step", 0),
            (start_presentation, "prsnt_multiplayer_campaign_character_creation"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_stat_updated),
            (try_begin),
                (is_presentation_active, "prsnt_multiplayer_campaign_character_window"),
                (presentation_set_duration, 0),
                (start_presentation, "prsnt_multiplayer_campaign_character_window"),
            (try_end),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_data),
            (display_message, "@Opening map spawn picker..."),
            (start_presentation, "prsnt_multiplayer_campaign_map_spawn_picker"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_equip_slot),
            (store_script_param, ":slot", 2),
            (store_script_param, ":item", 3),
            (store_script_param, ":imod", 4),
            # Write to troop struct so native inventory screen sees equipment
            (multiplayer_get_my_player, ":my_player"),
            (player_get_troop_id, ":troop_no", ":my_player"),
            (troop_set_inventory_slot, ":troop_no", ":slot", ":item"),
            (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":imod"),
        (else_try),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_attr),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_skill),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_prof),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_points),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_xp),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_health),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_done),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_hero_sync_xp),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_char_sync_gold),
            (store_script_param, ":p2", 2),
            (store_script_param, ":p3", 3),
            (store_script_param, ":p4", 4),
            (call_script, "script_coop_char_client_receive", ":event_type", ":p2", ":p3", ":p4"),
        (else_try),
            # Inventory + trade data pushes -- client applies to its local
            # troop/merchant copies. Handler owns the whole trade-screen push
            # (prices, merchant slots, gold) as one concern.
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_inv_bag_slot),  # 25
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_inv_sync_done),  # 26
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_center_trade_price),  # 29
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_merchant_slot),  # 30
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_sync_done),  # 31
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_trade_gold_sync),  # 32
            (store_script_param, ":p2", 2),
            (store_script_param, ":p3", 3),
            (store_script_param, ":p4", 4),
            (call_script, "script_coop_client_recv_inventory", ":event_type", ":p2", ":p3", ":p4"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_party_stack_num_upgradeable),  # 22
            (store_script_param, ":stack_idx", 2),
            (store_script_param, ":stack_upg", 3),
            (call_script, "script_coop_ev_srv_party_stack_num_upgradeable", ":stack_idx", ":stack_upg"),
        # --- Center interaction events (27-35) ---
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_center_encounter),  # 27
            (store_script_param, ":center_party", 2),
            (store_script_param, ":center_type", 3),
            (store_script_param, ":scene_id", 4),
            (assign, "$g_coop_center_party", ":center_party"),
            (assign, "$g_coop_center_type", ":center_type"),
            (assign, "$g_coop_center_scene", ":scene_id"),
            (assign, "$g_encountered_party", ":center_party"),
            (assign, "$g_coop_encounter_done", 0),
            (jump_to_menu, "mnu_coop_center_encounter"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_center_locked),  # 28
            (store_script_param, ":center_party", 2),
            (assign, "$g_coop_center_party", ":center_party"),
            (assign, "$g_coop_encounter_done", 0),
            (jump_to_menu, "mnu_coop_center_locked"),
        (else_try),
            # Recruit volunteers UI: server pushes the recruit offer (data)
            # then the outcome (result). Handler shows the menu and applies
            # recruited troops + gold client-side.
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_recruit_data),  # 33
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_recruit_result),  # 34
            (store_script_param, ":p2", 2),
            (store_script_param, ":p3", 3),
            (store_script_param, ":p4", 4),
            (call_script, "script_coop_client_recv_recruit", ":event_type", ":p2", ":p3", ":p4"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_center_leave_ack),  # 35
            (assign, "$g_coop_center_party", 0),
            (assign, "$g_coop_encounter_done", 1),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_server_event_start_siege_local),  # 42
            (store_script_param, ":p2", 2),
            (store_script_param, ":p3", 3),
            (store_script_param, ":p4", 4),
            (call_script, "script_coop_client_start_siege_local", ":event_type", ":p2", ":p3", ":p4"),
		(try_end),
    ]),

    ("multiplayer_campaign_client_events",
	[
        (store_script_param, ":player_no", 1),
		(store_script_param, ":event_type", 2),

		(try_begin),
			(eq, ":event_type", multiplayer_event_multiplayer_campaign_leave_encounter),
			(display_message, "@Player leaving encounter"),
            (player_get_party_id, ":party_no", ":player_no"),
            (try_begin),
                (party_is_active, ":party_no"),
                (party_leave_cur_battle, ":party_no"),
            (try_end),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_start_battle),
            (call_script, "script_coop_ev_cli_start_battle", ":player_no"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_request_siege),
            (store_script_param, ":center_party", 3),
            (call_script, "script_coop_ev_cli_request_siege", ":player_no", ":center_party"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_request_siege_local),
            (store_script_param, ":center_party", 3),
            (call_script, "script_coop_ev_cli_request_siege_local", ":player_no", ":center_party"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_char_creation_bg),
            (store_script_param, ":gender", 3),
            (store_script_param, ":father", 4),
            (store_script_param, ":earlylife", 5),
            (player_set_slot, ":player_no", 55, ":gender"),
            (player_set_slot, ":player_no", 56, ":father"),
            (player_set_slot, ":player_no", 57, ":earlylife"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_char_creation_life),
            (store_script_param, ":adulthood", 3),
            (store_script_param, ":reason", 4),
            (call_script, "script_coop_ev_cli_char_creation_life", ":player_no", ":adulthood", ":reason"),
        (else_try),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_attribute),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_skill),
            (this_or_next|eq, ":event_type", multiplayer_event_multiplayer_campaign_raise_proficiency),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_sync_pools),
            (store_script_param, ":p3", 3),
            (store_script_param, ":p4", 4),
            (store_script_param, ":p5", 5),
            (call_script, "script_coop_char_server_receive", ":player_no", ":event_type", ":p3", ":p4", ":p5"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_request_char_sync),  # 7
            # Flush deferred save if any raises were applied
            (try_begin),
                (player_get_slot, ":dirty", ":player_no", slot_player_coop_char_dirty),
                (eq, ":dirty", 1),
                (call_script, "script_coop_save_character", ":player_no"),
                (player_set_slot, ":player_no", slot_player_coop_char_dirty, 0),
            (try_end),
            (call_script, "script_coop_send_char_sync_to_client", ":player_no"),
            (call_script, "script_coop_send_party_upgradeable_to_client", ":player_no"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_party_dismiss),
            (store_script_param, ":dismiss_troop", 3),
            (store_script_param, ":dismiss_count", 4),
            (call_script, "script_coop_ev_cli_party_dismiss", ":player_no", ":dismiss_troop", ":dismiss_count"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_party_upgrade),
            (store_script_param, ":from_troop", 3),
            (store_script_param, ":to_troop", 4),
            (store_script_param, ":upg_count", 5),
            (call_script, "script_coop_ev_cli_party_upgrade", ":player_no", ":from_troop", ":to_troop", ":upg_count"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_inv_change),  # 14
            (store_script_param, ":slot", 3),
            (store_script_param, ":item", 4),
            (store_script_param, ":imod", 5),
            (player_get_troop_id, ":troop_no", ":player_no"),
            (troop_set_inventory_slot, ":troop_no", ":slot", ":item"),
            (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":imod"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_inv_sync_back_done),  # 15
            # Validate the batch server-side before persisting: reject item
            # minting/duplication, commit or revert. (Replaces the bare save.)
            (call_script, "script_coop_inv_sync_back_validate_and_save", ":player_no"),
        # --- Center interaction client events (18-23) ---
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_enter_center),
            (store_script_param, ":center_id", 3),
            (call_script, "script_coop_ev_cli_enter_center", ":player_no", ":center_id"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_leave_center),  # 19
            # Release center lock held by this player
            (player_get_slot, ":locked_center", ":player_no", slot_player_coop_locked_center),
            (try_begin),
                (gt, ":locked_center", 0),
                (party_set_slot, ":locked_center", slot_center_coop_lock_player, -1),
                (player_set_slot, ":player_no", slot_player_coop_locked_center, 0),
            (try_end),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_center_leave_ack, 0),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_request_trade),  # 20
            (store_script_param, ":merchant_type", 3),
            (player_get_slot, ":locked_center", ":player_no", slot_player_coop_locked_center),
            (try_begin),
                (gt, ":locked_center", 0),
                (call_script, "script_coop_send_merchant_to_client", ":player_no", ":locked_center", ":merchant_type"),
            (try_end),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_trade_change),  # 21
            (store_script_param, ":slot", 3),
            (store_script_param, ":item_id", 4),
            (store_script_param, ":imod", 5),
            # Apply to the merchant troop the player was trading with
            (player_get_slot, ":merchant_troop", ":player_no", slot_player_coop_merchant_troop),
            (try_begin),
                (gt, ":merchant_troop", 0),
                (troop_set_inventory_slot, ":merchant_troop", ":slot", ":item_id"),
                (troop_set_inventory_slot_modifier, ":merchant_troop", ":slot", ":imod"),
            (try_end),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_trade_done),
            (store_script_param, ":gold_delta", 3),
            (call_script, "script_coop_ev_cli_trade_done", ":player_no", ":gold_delta"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_request_recruit),
            (store_script_param, ":center_id", 3),
            (store_script_param, ":count", 4),
            (call_script, "script_coop_ev_cli_request_recruit", ":player_no", ":center_id", ":count"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_start_local_fight),
            (call_script, "script_coop_ev_cli_start_local_fight", ":player_no"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_local_fight_result),
            (store_script_param, ":sub_type", 3),
            (store_script_param, ":p4", 4),
            (store_script_param, ":p5", 5),
            (call_script, "script_coop_ev_cli_local_fight_result", ":player_no", ":sub_type", ":p4", ":p5"),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_start_local_visit),  # 24
            # Client is visiting center locally. Just mark busy.
            (str_store_player_username, s0, ":player_no"),
            (display_message, "@{s0}: Entering local SP center visit."),
            (player_set_slot, ":player_no", slot_player_coop_in_local_encounter, 2),
        (else_try),
            (eq, ":event_type", multiplayer_event_multiplayer_campaign_local_visit_done),  # 25
            # Client finished local center visit. Release lock, clear busy flag.
            (str_store_player_username, s0, ":player_no"),
            (display_message, "@{s0}: Local center visit complete."),
            (player_set_slot, ":player_no", slot_player_coop_in_local_encounter, 0),
            # Release center lock
            (player_get_slot, ":locked_center", ":player_no", slot_player_coop_locked_center),
            (try_begin),
                (gt, ":locked_center", 0),
                (party_set_slot, ":locked_center", slot_center_coop_lock_player, -1),
                (player_set_slot, ":player_no", slot_player_coop_locked_center, 0),
            (try_end),
            # Save character (gold/inventory may have changed)
            (call_script, "script_coop_save_character", ":player_no"),
            # Notify client encounter resolved
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_encounter_resolved, 0),
		(try_end),
    ]),

  # ==================================================================
  # CAMPAIGN: BATTLE PIPELINE (write data, apply results, XP)
  # ==================================================================

	# ==================================================================
	# BATTLE SERVER POOL: per-slot state helpers
	# ==================================================================
	# Slot s state lives in $g_coop_battle_in_progress_<s> (module-owned)
	# and $g_coop_battle_ended_<s> (DLL writes 1 on PKT_BATTLE_END or IPC
	# peer loss; module consumes and clears). $g_coop_battle_slots_online
	# is a DLL-owned bitmask of connected battle-server IPC peers.
	# Battle servers learn their own slot via $coop_battle_slot, written
	# by the COOP_BATTLE plugin from the COOP_BATTLE_SLOT env var.

	# script_coop_battle_slot_dict_name
	# Input: arg1 = slot. Output: s41 = "coop_battle_{slot}" (reg41 clobbered).
	("coop_battle_slot_dict_name", [
		(store_script_param, ":slot", 1),
		(assign, reg41, ":slot"),
		(str_store_string, s41, "@coop_battle_{reg41}"),
	]),

	# script_coop_battle_slot_get_in_progress -- Input: arg1 = slot. Output: reg0.
	("coop_battle_slot_get_in_progress", [
		(store_script_param, ":slot", 1),
		(try_begin),
			(eq, ":slot", 0),
			(assign, reg0, "$g_coop_battle_in_progress_0"),
		(else_try),
			(eq, ":slot", 1),
			(assign, reg0, "$g_coop_battle_in_progress_1"),
		(else_try),
			(eq, ":slot", 2),
			(assign, reg0, "$g_coop_battle_in_progress_2"),
		(else_try),
			(eq, ":slot", 3),
			(assign, reg0, "$g_coop_battle_in_progress_3"),
		(else_try),
			(assign, reg0, 0),
		(try_end),
	]),

	# script_coop_battle_slot_set_in_progress -- Input: arg1 = slot, arg2 = value.
	("coop_battle_slot_set_in_progress", [
		(store_script_param, ":slot", 1),
		(store_script_param, ":value", 2),
		(try_begin),
			(eq, ":slot", 0),
			(assign, "$g_coop_battle_in_progress_0", ":value"),
		(else_try),
			(eq, ":slot", 1),
			(assign, "$g_coop_battle_in_progress_1", ":value"),
		(else_try),
			(eq, ":slot", 2),
			(assign, "$g_coop_battle_in_progress_2", ":value"),
		(else_try),
			(eq, ":slot", 3),
			(assign, "$g_coop_battle_in_progress_3", ":value"),
		(try_end),
	]),

	# script_coop_battle_slot_get_ended -- Input: arg1 = slot. Output: reg0.
	("coop_battle_slot_get_ended", [
		(store_script_param, ":slot", 1),
		(try_begin),
			(eq, ":slot", 0),
			(assign, reg0, "$g_coop_battle_ended_0"),
		(else_try),
			(eq, ":slot", 1),
			(assign, reg0, "$g_coop_battle_ended_1"),
		(else_try),
			(eq, ":slot", 2),
			(assign, reg0, "$g_coop_battle_ended_2"),
		(else_try),
			(eq, ":slot", 3),
			(assign, reg0, "$g_coop_battle_ended_3"),
		(else_try),
			(assign, reg0, 0),
		(try_end),
	]),

	# script_coop_battle_slot_clear_ended -- Input: arg1 = slot.
	("coop_battle_slot_clear_ended", [
		(store_script_param, ":slot", 1),
		(try_begin),
			(eq, ":slot", 0),
			(assign, "$g_coop_battle_ended_0", 0),
		(else_try),
			(eq, ":slot", 1),
			(assign, "$g_coop_battle_ended_1", 0),
		(else_try),
			(eq, ":slot", 2),
			(assign, "$g_coop_battle_ended_2", 0),
		(else_try),
			(eq, ":slot", 3),
			(assign, "$g_coop_battle_ended_3", 0),
		(try_end),
	]),

	# ==================================================================
	# BATTLE CHOOSER: client-side per-slot availability table
	# ==================================================================
	# Fills the "press B to pick a battle" dashboard. Each announced slot
	# (ch125 ev battle_available) stores its port + enemy party id here;
	# ev battle_slot_closed clears it. $g_coop_battle_available stays a
	# cheap "at least one battle listed" boolean for the B-key trigger.

	# script_coop_battle_chooser_set -- Input: slot, port, enemy_party_id.
	("coop_battle_chooser_set", [
		(store_script_param, ":slot", 1),
		(store_script_param, ":port", 2),
		(store_script_param, ":enemy", 3),
		(try_begin),
			(eq, ":slot", 0),
			(assign, "$coop_avail_valid_0", 1),
			(assign, "$coop_avail_port_0", ":port"),
			(assign, "$coop_avail_enemy_0", ":enemy"),
		(else_try),
			(eq, ":slot", 1),
			(assign, "$coop_avail_valid_1", 1),
			(assign, "$coop_avail_port_1", ":port"),
			(assign, "$coop_avail_enemy_1", ":enemy"),
		(else_try),
			(eq, ":slot", 2),
			(assign, "$coop_avail_valid_2", 1),
			(assign, "$coop_avail_port_2", ":port"),
			(assign, "$coop_avail_enemy_2", ":enemy"),
		(else_try),
			(eq, ":slot", 3),
			(assign, "$coop_avail_valid_3", 1),
			(assign, "$coop_avail_port_3", ":port"),
			(assign, "$coop_avail_enemy_3", ":enemy"),
		(try_end),
		(assign, "$g_coop_battle_available", 1),
	]),

	# script_coop_battle_chooser_clear -- Input: slot. Clears one entry and
	# recomputes the "any available" boolean by scanning the remaining slots.
	("coop_battle_chooser_clear", [
		(store_script_param, ":slot", 1),
		(try_begin),
			(eq, ":slot", 0),
			(assign, "$coop_avail_valid_0", 0),
		(else_try),
			(eq, ":slot", 1),
			(assign, "$coop_avail_valid_1", 0),
		(else_try),
			(eq, ":slot", 2),
			(assign, "$coop_avail_valid_2", 0),
		(else_try),
			(eq, ":slot", 3),
			(assign, "$coop_avail_valid_3", 0),
		(try_end),
		(store_add, ":any", "$coop_avail_valid_0", "$coop_avail_valid_1"),
		(val_add, ":any", "$coop_avail_valid_2"),
		(val_add, ":any", "$coop_avail_valid_3"),
		(try_begin),
			(gt, ":any", 0),
			(assign, "$g_coop_battle_available", 1),
		(else_try),
			(assign, "$g_coop_battle_available", 0),
		(try_end),
	]),

	# script_coop_battle_broadcast_slot_closed -- Input: slot. SERVER-side:
	# tell every active player to drop this slot from their chooser table.
	("coop_battle_broadcast_slot_closed", [
		(store_script_param, ":slot", 1),
		(get_max_players, ":num_players"),
		(try_for_range, ":cur_player", 1, ":num_players"),
			(player_is_active, ":cur_player"),
			(multiplayer_send_2_int_to_player, ":cur_player", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_slot_closed, ":slot"),
		(try_end),
	]),

	# script_coop_battle_find_free_slot
	# Output: reg0 = first slot that is online (IPC peer connected) and not
	# in progress, or -1 if the pool is exhausted/offline.
	("coop_battle_find_free_slot", [
		(assign, ":found", -1),
		(try_for_range, ":slot", 0, coop_battle_num_slots),
			(eq, ":found", -1),
			(assign, ":bit", 1),
			(val_lshift, ":bit", ":slot"),
			(assign, ":mask", "$g_coop_battle_slots_online"),
			(val_div, ":mask", ":bit"),
			(val_mod, ":mask", 2),
			(eq, ":mask", 1),
			(call_script, "script_coop_battle_slot_get_in_progress", ":slot"),
			(eq, reg0, 0),
			(assign, ":found", ":slot"),
		(try_end),
		(try_begin),
			# Rejection diagnostic: show exactly what allocation saw
			(eq, ":found", -1),
			(assign, reg10, "$g_coop_battle_slots_online"),
			(call_script, "script_coop_battle_slot_get_in_progress", 0),
			(assign, reg11, reg0),
			(call_script, "script_coop_battle_slot_get_in_progress", 1),
			(assign, reg12, reg0),
			(call_script, "script_coop_battle_slot_get_in_progress", 2),
			(assign, reg13, reg0),
			(call_script, "script_coop_battle_slot_get_in_progress", 3),
			(assign, reg14, reg0),
			(display_message, "@[POOL] no free slot: online_mask={reg10} in_progress={reg11},{reg12},{reg13},{reg14}"),
		(try_end),
		(assign, reg0, ":found"),
	]),

	# script_coop_battle_dict_write_roster_party
	# Serializes one campaign party as battle-roster entry {index} on {side}:
	# @p_{enemy|ally}{i}_partyid/banner/numstacks + per-stack _trp/_num
	# (alive counts only -- wounded subtracted, matching the MP loader).
	# skip_first=1 omits stack 0 (party leader, e.g. the player character);
	# stack keys are re-based so the loader sees a dense 0..N-1 range.
	# slot_mark > 0 also marks the party as fighting in that battle slot
	# (rostered <=> marked, so third parties bounce off every participant).
	# INPUT: p1 dict, p2 side (0=enemy/1=ally), p3 index, p4 party_id,
	#        p5 skip_first, p6 slot_mark
	# OUTPUT: reg0 = total alive troops written
	# Clobbers reg20/reg21/reg22 (dict-key interpolation) -- callers must not hold live values there.
	("coop_battle_dict_write_roster_party", [
		(store_script_param, ":wr_dict", 1),
		(store_script_param, ":wr_side", 2),
		(store_script_param, ":wr_index", 3),
		(store_script_param, ":wr_party", 4),
		(store_script_param, ":wr_skip", 5),
		(store_script_param, ":wr_mark", 6),

		(assign, reg20, ":wr_index"),
		(party_get_num_companion_stacks, ":wr_num_stacks", ":wr_party"),
		(store_sub, ":wr_out_stacks", ":wr_num_stacks", ":wr_skip"),
		(val_max, ":wr_out_stacks", 0),
		(assign, ":wr_total", 0),
		(try_begin),
			(eq, ":wr_side", 0),
			(dict_set_int, ":wr_dict", "@p_enemy{reg20}_partyid", ":wr_party"),
			(dict_set_int, ":wr_dict", "@p_enemy{reg20}_banner", 0),
			(dict_set_int, ":wr_dict", "@p_enemy{reg20}_numstacks", ":wr_out_stacks"),
			(try_for_range, reg21, ":wr_skip", ":wr_num_stacks"),
				(party_stack_get_troop_id, ":wr_troop", ":wr_party", reg21),
				(party_stack_get_size, ":wr_size", ":wr_party", reg21),
				(party_stack_get_num_wounded, ":wr_wnd", ":wr_party", reg21),
				(store_sub, ":wr_alive", ":wr_size", ":wr_wnd"),
				(val_max, ":wr_alive", 0),
				(store_sub, reg22, reg21, ":wr_skip"),
				(dict_set_int, ":wr_dict", "@p_enemy{reg20}_{reg22}_trp", ":wr_troop"),
				(dict_set_int, ":wr_dict", "@p_enemy{reg20}_{reg22}_num", ":wr_alive"),
				(val_add, ":wr_total", ":wr_alive"),
			(try_end),
		(else_try),
			(dict_set_int, ":wr_dict", "@p_ally{reg20}_partyid", ":wr_party"),
			(dict_set_int, ":wr_dict", "@p_ally{reg20}_banner", 0),
			(dict_set_int, ":wr_dict", "@p_ally{reg20}_numstacks", ":wr_out_stacks"),
			(try_for_range, reg21, ":wr_skip", ":wr_num_stacks"),
				(party_stack_get_troop_id, ":wr_troop", ":wr_party", reg21),
				(party_stack_get_size, ":wr_size", ":wr_party", reg21),
				(party_stack_get_num_wounded, ":wr_wnd", ":wr_party", reg21),
				(store_sub, ":wr_alive", ":wr_size", ":wr_wnd"),
				(val_max, ":wr_alive", 0),
				(store_sub, reg22, reg21, ":wr_skip"),
				(dict_set_int, ":wr_dict", "@p_ally{reg20}_{reg22}_trp", ":wr_troop"),
				(dict_set_int, ":wr_dict", "@p_ally{reg20}_{reg22}_num", ":wr_alive"),
				(val_add, ":wr_total", ":wr_alive"),
			(try_end),
		(try_end),
		(try_begin),
			(gt, ":wr_mark", 0),
			(party_set_slot, ":wr_party", slot_party_coop_battle_slot, ":wr_mark"),
		(try_end),
		(assign, reg0, ":wr_total"),
	]),

	# Write encounter party data to coop_battle dict file for the battle server.
	# Called on campaign server when client requests MP battle.
	# arg1 = player/ally party, arg2 = enemy party
	("coop_write_battle_data", [
		(store_script_param, ":ally_party", 1),
		(store_script_param, ":enemy_party", 2),
		(store_script_param, ":wbd_slot", 4),
		(store_add, ":wbd_mark", ":wbd_slot", 1),

		(dict_create, ":dict"),
		(dict_set_int, ":dict", "@battle_state", coop_battle_state_setup_sp),
		(dict_set_int, ":dict", "@battle_host_party", ":ally_party"),
		(assign, reg1, ":ally_party"),
		(display_message, "@[BATTLE SETUP] host_party={reg1}"),

		# Look up host player by matching ally_party to each active player's party_id
		(str_clear, s15),
		(try_for_players, ":hp_player_no", 1),
			(player_is_active, ":hp_player_no"),
			(player_get_party_id, ":hp_party", ":hp_player_no"),
			(eq, ":hp_party", ":ally_party"),
			(str_store_player_username, s15, ":hp_player_no"),
		(try_end),
		(dict_set_str, ":dict", "@battle_host_player_name", s15),
		(display_message, "@[BATTLE SETUP] host_player_name={s15}"),

		(store_script_param, ":battle_type", 3),
		(dict_set_int, ":dict", "@map_type", ":battle_type"),

		(try_begin),
			# --- SIEGE: enemy_party is the besieged center; read its siege scenes ---
			(this_or_next|eq, ":battle_type", coop_battle_type_siege_player_attack),
			(eq, ":battle_type", coop_battle_type_siege_player_defend),
			(assign, ":scene_castle", 0),
			(assign, ":scene_street", 0),
			(try_begin),
				(party_slot_eq, ":enemy_party", slot_party_type, spt_town),
				(party_get_slot, ":battle_scene", ":enemy_party", slot_town_walls),
				(party_get_slot, ":scene_castle", ":enemy_party", slot_town_castle),
				(party_get_slot, ":scene_street", ":enemy_party", slot_town_center),
			(else_try),
				(party_get_slot, ":battle_scene", ":enemy_party", slot_castle_exterior),
				(party_get_slot, ":scene_castle", ":enemy_party", slot_town_castle),
			(try_end),
			(dict_set_int, ":dict", "@map_scn", ":battle_scene"),
			(dict_set_int, ":dict", "@map_castle", ":scene_castle"),
			(dict_set_int, ":dict", "@map_street", ":scene_street"),
			(dict_set_int, ":dict", "@map_party_id", ":enemy_party"),
		(else_try),
			# --- FIELD: pick scene based on terrain at encounter location ---
		(party_get_current_terrain, ":terrain", ":ally_party"),
		(assign, reg3, ":terrain"),
		(display_message, "@Terrain type: {reg3}"),
		(assign, ":scene_med", "scn_random_multi_plain_medium"),
		(assign, ":scene_lrg", "scn_random_multi_plain_large"),
		(try_begin),
			(this_or_next|eq, ":terrain", rt_steppe),
			(eq, ":terrain", rt_steppe_forest),
			(assign, ":scene_med", "scn_random_multi_steppe_medium"),
			(assign, ":scene_lrg", "scn_random_multi_steppe_large"),
		(else_try),
			(eq, ":terrain", rt_snow),
			(assign, ":scene_med", "scn_random_multi_snow_medium"),
			(assign, ":scene_lrg", "scn_random_multi_snow_large"),
		(else_try),
			(this_or_next|eq, ":terrain", rt_desert),
			(eq, ":terrain", rt_desert_forest),
			(assign, ":scene_med", "scn_random_multi_desert_medium"),
			(assign, ":scene_lrg", "scn_random_multi_desert_large"),
		(else_try),
			(eq, ":terrain", rt_snow_forest),
			(assign, ":scene_med", "scn_random_multi_snow_forest_medium"),
			(assign, ":scene_lrg", "scn_random_multi_snow_forest_large"),
		(else_try),
			(eq, ":terrain", rt_forest),
			(assign, ":scene_med", "scn_random_multi_plain_medium"),
			(assign, ":scene_lrg", "scn_random_multi_plain_large"),
		(try_end),
		# Large scene for big battles
		(party_get_num_companions, ":total_a", ":ally_party"),
		(party_get_num_companions, ":total_e", ":enemy_party"),
		(store_add, ":total_troops", ":total_a", ":total_e"),
		(try_begin),
			(gt, ":total_troops", 80),
			(assign, ":battle_scene", ":scene_lrg"),
		(else_try),
			(assign, ":battle_scene", ":scene_med"),
		(try_end),
		(dict_set_int, ":dict", "@map_scn", ":battle_scene"),
		(dict_set_int, ":dict", "@map_castle", 0),
		(dict_set_int, ":dict", "@map_street", 0),
		(dict_set_int, ":dict", "@map_party_id", 0),
		(try_end),

		# Weather
		(store_time_of_day, ":time"),
		(dict_set_int, ":dict", "@map_time", ":time"),
		(dict_set_int, ":dict", "@map_cloud", 50),
		(dict_set_int, ":dict", "@map_haze", 50),
		(dict_set_int, ":dict", "@map_rain", 0),

		# Factions
		(store_faction_of_party, ":enemy_fac", ":enemy_party"),
		(dict_set_int, ":dict", "@tm0_fac", ":enemy_fac"),
		(store_faction_of_party, ":ally_fac", ":ally_party"),
		(dict_set_int, ":dict", "@tm1_fac", ":ally_fac"),
		(str_store_faction_name, s0, ":ally_fac"),
		(dict_set_str, ":dict", "@tm1_name", s0),

		# Garrison: for a siege the besieged center is serialized as enemy party 0
		# (the @p_enemy0_* stacks below), and the loader maps @p_garrison /
		# @p_castle_lord as enemy-party indices (coop_on_admin_panel_load).
		# Field battles have no garrison.
		(try_begin),
			(this_or_next|eq, ":battle_type", coop_battle_type_siege_player_attack),
			(eq, ":battle_type", coop_battle_type_siege_player_defend),
			(dict_set_int, ":dict", "@p_castle_lord", 0),
			(dict_set_int, ":dict", "@p_garrison", 0),
			(assign, ":gar_banner", 0),
			(party_get_slot, ":gar_lord", ":enemy_party", slot_town_lord),
			(try_begin),
				(ge, ":gar_lord", 0),
				(troop_get_slot, ":gar_banner", ":gar_lord", slot_troop_banner_scene_prop),
			(try_end),
			(dict_set_int, ":dict", "@p_garrison_banner", ":gar_banner"),
		(else_try),
			(dict_set_int, ":dict", "@p_castle_lord", -1),
			(dict_set_int, ":dict", "@p_garrison", -1),
			(dict_set_int, ":dict", "@p_garrison_banner", 0),
		(try_end),

		# Server settings defaults
		(dict_set_int, ":dict", "@srvr_set0", 0),
		(dict_set_int, ":dict", "@srvr_set2", 10),
		(dict_set_int, ":dict", "@srvr_set3", coop_def_battle_size),
		(dict_set_int, ":dict", "@srvr_set4", 0),
		(dict_set_int, ":dict", "@srvr_set5", 0),
		(dict_set_int, ":dict", "@srvr_set6", 0),
		(dict_set_int, ":dict", "@srvr_set7", 0),
		(dict_set_int, ":dict", "@srvr_set8", 0),
		(dict_set_int, ":dict", "@srvr_set9", 0),
		(dict_set_int, ":dict", "@srvr_set10", 2),
		(dict_set_int, ":dict", "@srvr_set11", 0),

		# --- Enemy parties ---
		# enemy0 = the encountered party / besieged center (the loader maps
		# @p_garrison/@p_castle_lord to index 0). For attack sieges, parties
		# attached to the center (garrisoned defender lords) follow as
		# enemy1..N; casualties round-trip per party via @p_enemy{i}_partyid.
		(assign, ":num_enemy_parties", 0),
		(assign, ":enemy_total", 0),
		(call_script, "script_coop_battle_dict_write_roster_party", ":dict", 0, ":num_enemy_parties", ":enemy_party", 0, ":wbd_mark"),
		(val_add, ":enemy_total", reg0),
		(val_add, ":num_enemy_parties", 1),
		(try_begin),
			(eq, ":battle_type", coop_battle_type_siege_player_attack),
			(party_get_num_attached_parties, ":num_att", ":enemy_party"),
			(try_for_range, ":att_i", 0, ":num_att"),
				(lt, ":num_enemy_parties", 40),
				(party_get_attached_party_with_rank, ":att_party", ":enemy_party", ":att_i"),
				(gt, ":att_party", 0),
				(party_is_active, ":att_party"),
				(party_get_num_companions, ":att_count", ":att_party"),
				(gt, ":att_count", 0),
				(call_script, "script_coop_battle_dict_write_roster_party", ":dict", 0, ":num_enemy_parties", ":att_party", 0, ":wbd_mark"),
				(val_add, ":enemy_total", reg0),
				(val_add, ":num_enemy_parties", 1),
				(str_store_party_name, s11, ":att_party"),
				(display_message, "@[BATTLE SETUP] defender attachment joins: {s11}"),
			(try_end),
		(try_end),
		(dict_set_int, ":dict", "@num_parties_enemy", ":num_enemy_parties"),

		# --- Ally parties ---
		# ally0 = the initiating player's party, leader stack excluded (the
		# player fights as their own MP agent). For attack sieges, friendly
		# AI parties within coop_siege_join_radius of the center join as
		# ally1..N -- the placeholder selection rule until a siege camp
		# exists. @p_ally{i}_partyid routes casualties back per party.
		(assign, ":num_ally_parties", 0),
		(assign, ":ally_bot_total", 0),
		(call_script, "script_coop_battle_dict_write_roster_party", ":dict", 1, ":num_ally_parties", ":ally_party", 1, ":wbd_mark"),
		(val_add, ":ally_bot_total", reg0),
		(val_add, ":num_ally_parties", 1),
		(try_begin),
			(eq, ":battle_type", coop_battle_type_siege_player_attack),
			(store_faction_of_party, ":sr_center_fac", ":enemy_party"),
			(store_faction_of_party, ":sr_init_fac", ":ally_party"),
			(try_for_parties, ":near_party"),
				(lt, ":num_ally_parties", 40),
				(neq, ":near_party", ":ally_party"),
				(neq, ":near_party", ":enemy_party"),
				(party_is_active, ":near_party"),
				(party_get_slot, ":np_type", ":near_party", slot_party_type),
				(neq, ":np_type", spt_town),
				(neq, ":np_type", spt_castle),
				(neq, ":np_type", spt_village),
				(party_slot_eq, ":near_party", slot_party_coop_battle_slot, 0),
				(store_distance_to_party_from_party, ":np_dist", ":near_party", ":enemy_party"),
				(le, ":np_dist", coop_siege_join_radius),
				(store_faction_of_party, ":np_fac", ":near_party"),
				(store_relation, ":np_rel_center", ":np_fac", ":sr_center_fac"),
				(lt, ":np_rel_center", 0),
				(store_relation, ":np_rel_init", ":np_fac", ":sr_init_fac"),
				(ge, ":np_rel_init", 0),
				(assign, ":np_is_player", 0),
				(try_for_players, ":np_pl", 1),
					(player_is_active, ":np_pl"),
					(player_get_party_id, ":np_pl_party", ":np_pl"),
					(eq, ":np_pl_party", ":near_party"),
					(assign, ":np_is_player", 1),
				(try_end),
				(eq, ":np_is_player", 0),
				(party_get_num_companions, ":np_count", ":near_party"),
				(gt, ":np_count", 0),
				(call_script, "script_coop_battle_dict_write_roster_party", ":dict", 1, ":num_ally_parties", ":near_party", 0, ":wbd_mark"),
				(val_add, ":ally_bot_total", reg0),
				(val_add, ":num_ally_parties", 1),
				(str_store_party_name, s11, ":near_party"),
				(display_message, "@[BATTLE SETUP] attacker ally joins: {s11}"),
			(try_end),
		(try_end),
		(dict_set_int, ":dict", "@num_parties_ally", ":num_ally_parties"),

		# Battle advantage from full roster totals (+1 = the player agent).
		(store_add, ":adv_allies", ":ally_bot_total", 1),
		(assign, ":adv_div", ":enemy_total"),
		(val_max, ":adv_div", 1),
		(store_mul, ":adv", ":adv_allies", 15),
		(val_div, ":adv", ":adv_div"),
		(val_sub, ":adv", 15),
		(dict_set_int, ":dict", "@battle_adv", ":adv"),

		# Class names (use defaults)
		(try_for_range, reg1, 0, 9),
			(str_store_class_name, s0, reg1),
			(dict_set_str, ":dict", "@cls{reg1}_name", s0),
		(try_end),

		(call_script, "script_coop_battle_slot_dict_name", ":wbd_slot"),
		(dict_save, ":dict", s41),
		(dict_free, ":dict"),

		(assign, reg1, ":ally_bot_total"),
		(assign, reg2, ":enemy_total"),
		(assign, reg3, ":num_ally_parties"),
		(assign, reg4, ":num_enemy_parties"),
		(display_message, "@Battle data written: {reg1} ally troops ({reg3} parties) + player vs {reg2} enemies ({reg4} parties)."),
	]),

	# Apply battle results to the rejoining player's current party.
	# Called from multiplayer_campaign_player_joined when battle_in_progress or
	# battle_ended (DLL IPC signal). Reads battle dict, applies enemy casualties
	# to campaign enemy parties, ally casualties + XP to the player's party by troop type.
	("coop_apply_battle_results", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":slot", 2),
		(player_get_party_id, ":party_no", ":player_no"),

		(call_script, "script_coop_battle_slot_get_ended", ":slot"),
		(assign, ":slot_ended", reg0),
		(assign, reg1, ":slot"),
		(assign, reg2, ":slot_ended"),
		(display_message, "@[BATTLE RESULTS] slot {reg1} apply (ended={reg2})"),

		(try_begin),
			(neg|is_vanilla_warband),
			(dict_create, "$coop_dict"),
			(call_script, "script_coop_battle_slot_dict_name", ":slot"),
			(dict_load_file, "$coop_dict", s41, 2),
			(dict_get_int, ":state", "$coop_dict", "@battle_state"),

			# Compute participant membership before gating on end_mp state,
			# so a rejoin into a slot for a battle this player didn't fight
			# never consumes that battle's results.
			(assign, ":arp_participant", 0),
			(str_store_player_username, s10, ":player_no"),
			(dict_get_int, ":arp_np", "$coop_dict", "@battle_num_players"),
			(try_for_range, reg23, 0, ":arp_np"),
				(dict_get_str, s12, "$coop_dict", "@battle_player_{reg23}_name"),
				(str_equals, s10, s12),
				(assign, ":arp_participant", 1),
			(try_end),

			(eq, ":state", coop_battle_state_end_mp),
			(eq, ":arp_participant", 1),

			# Clear state immediately to prevent double-apply
			(call_script, "script_coop_battle_slot_set_in_progress", ":slot", 0),
			(call_script, "script_coop_battle_slot_clear_ended", ":slot"),
			(call_script, "script_coop_battle_broadcast_slot_closed", ":slot"),
			(dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_none),
			(call_script, "script_coop_battle_slot_dict_name", ":slot"),
			(dict_save, "$coop_dict", s41),

			(display_message, "@[BATTLE RESULTS] applying to current party..."),

			# Restore game settings and hero health from battle. Companion-hero
			# XP is delivered by the pool share below, so suppress the dict XP
			# re-application inside copy_file_to_hero (avoids double-counting the
			# engine's per-kill hero XP).
			(call_script, "script_coop_copy_file_to_settings"),
			(assign, "$g_coop_skip_hero_xp_restore", 1),
			(call_script, "script_coop_copy_file_to_hero"),
			(assign, "$g_coop_skip_hero_xp_restore", 0),

		# --- Verify casualty data exists (written in same save as end_mp) ---
		(try_begin),
			(call_script, "script_coop_battle_dict_has_stack_cas", 0, 0),
			(eq, reg0, 1),
			(display_message, "@[BATTLE RESULTS] casualty keys: PRESENT"),
		(else_try),
			(display_message, "@[BATTLE RESULTS] casualty keys: MISSING -- stale end_mp?"),
		(try_end),

		# --- Enemy casualties (applied to campaign enemy parties by dict party ID) ---
		(dict_get_int, "$coop_no_enemy_parties", "$coop_dict", "@num_parties_enemy"),
		(assign, reg1, "$coop_no_enemy_parties"),
		(display_message, "@[BATTLE RESULTS] num_enemy_parties={reg1}"),
		(party_clear, "p_total_enemy_casualties"),
		(party_clear, "p_enemy_casualties"),

		(try_for_range, reg20, 0, "$coop_no_enemy_parties"),
			(call_script, "script_coop_battle_dict_get_stack_cas_count", 0, reg20),
			(assign, ":num_cas_stacks", reg0),
			(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 0, reg20),
			(assign, ":enemy_party", reg0),
			(assign, reg1, ":num_cas_stacks"),
			(assign, reg2, ":enemy_party"),
			(display_message, "@[BATTLE RESULTS] enemy{reg20}: cas_stacks={reg1} party={reg2}"),
			(try_for_range, reg21, 0, ":num_cas_stacks"),
				(call_script, "script_coop_battle_dict_get_stack_cas", 0, reg20, reg21),
				(assign, ":troop_id", reg0),
				(assign, ":dead", reg1),
				(assign, ":wounded", reg2),
				(store_add, ":total_cas", ":dead", ":wounded"),
				(try_begin),
					(troop_is_hero, ":troop_id"),
					(store_random_in_range, ":rand_wound", 40, 71),
					(store_troop_health, ":hp", ":troop_id"),
					(val_sub, ":hp", ":rand_wound"),
					(val_max, ":hp", 1),
					(troop_set_health, ":troop_id", ":hp"),
				(else_try),
					(party_remove_members, ":enemy_party", ":troop_id", ":dead"),
				(try_end),
				(party_wound_members, ":enemy_party", ":troop_id", ":wounded"),
				(party_add_members, "p_total_enemy_casualties", ":troop_id", ":total_cas"),
				(party_wound_members, "p_total_enemy_casualties", ":troop_id", ":wounded"),
				(party_add_members, "p_enemy_casualties", ":troop_id", ":total_cas"),
				(party_wound_members, "p_enemy_casualties", ":troop_id", ":wounded"),
			(try_end),
		(try_end),

		# ========================================================
		# Phase 1: SP XP parity -- first-rejoiner stash
		# ========================================================
		# Compute pool, iterate snapshot players, stash per-player
		# deltas into each char dict. Runs once per battle (inside the
		# @battle_state == end_mp guard).
		(try_begin),
			(dict_has_key, "$coop_dict", "@battle_num_players"),
			(dict_has_key, "$coop_dict", "@battle_host_party"),
			(dict_has_key, "$coop_dict", "@battle_xp_rand"),
			(call_script, "script_coop_compute_sp_xp_pool_from_dict"),
			(assign, ":base_pool", reg0),

			(dict_get_int, ":num_bp", "$coop_dict", "@battle_num_players"),
			(dict_get_int, ":host_party_id", "$coop_dict", "@battle_host_party"),

			# Sum total strength
			(assign, ":total_strength", 0),
			(try_for_range, reg20, 0, ":num_bp"),
				(dict_get_int, ":s_i", "$coop_dict", "@battle_player_{reg20}_strength"),
				(val_add, ":total_strength", ":s_i"),
			(try_end),

			(assign, reg1, ":base_pool"),
			(assign, reg2, ":num_bp"),
			(assign, reg3, ":total_strength"),
			(display_message, "@[BATTLE RESULTS] Phase1: pool={reg1} nplayers={reg2} strength_sum={reg3}"),

			(try_begin),
				(gt, ":total_strength", 0),
				(try_for_range, reg20, 0, ":num_bp"),
					(dict_get_int, ":my_strength", "$coop_dict", "@battle_player_{reg20}_strength"),
					# share = base_pool * my_strength / total_strength
					(store_mul, ":share", ":base_pool", ":my_strength"),
					(val_div, ":share", ":total_strength"),

					# Load this player's name into s1
					(dict_get_str, s1, "$coop_dict", "@battle_player_{reg20}_name"),

					# Match to connected player_no (for party_id lookup)
					(call_script, "script_coop_find_player_no_by_name"),
					(assign, ":matched_pno", reg0),

					# Decide host vs joiner by comparing username to @battle_host_player_name
					# (party_id changes across disconnect/rejoin, so name is the stable key)
					(assign, ":is_host", 0),
					(try_begin),
						(dict_has_key, "$coop_dict", "@battle_host_player_name"),
						(dict_get_str, s3, "$coop_dict", "@battle_host_player_name"),
						(str_equals, s1, s3),
						(assign, ":is_host", 1),
					(try_end),

					# Build char dict path: "@coop_char_{username}"
					(str_store_string, s2, "@coop_char_{s1}"),

					(dict_create, "$coop_char_stash_dict"),
					(dict_load_file, "$coop_char_stash_dict", s2),

					(try_begin),
						(eq, ":is_host", 1),
						(dict_set_int, "$coop_char_stash_dict", "@char_pending_party_xp", ":share"),
						(dict_set_int, "$coop_char_stash_dict", "@char_pending_hero_xp", 0),
						(assign, reg1, ":share"),
						(display_message, "@[BATTLE RESULTS] Phase1: stashed HOST {s1} party_xp={reg1}"),
					(else_try),
						(dict_set_int, "$coop_char_stash_dict", "@char_pending_party_xp", 0),
						(dict_set_int, "$coop_char_stash_dict", "@char_pending_hero_xp", ":share"),
						(assign, reg1, ":share"),
						(display_message, "@[BATTLE RESULTS] Phase1: stashed JOINER {s1} hero_xp={reg1}"),
					(try_end),
					(dict_set_int, "$coop_char_stash_dict", "@char_battle_pending", 1),
					(dict_save, "$coop_char_stash_dict", s2),
					(dict_free, "$coop_char_stash_dict"),
				(try_end),
			(else_try),
				(display_message, "@[BATTLE RESULTS] Phase1: skipped XP stash -- zero total strength"),
			(try_end),
		(else_try),
			(display_message, "@[BATTLE RESULTS] Phase1: skipped -- missing @battle_num_players or host_party or xp_rand key"),
		(try_end),

		# --- Ally casualties (applied to CURRENT party by troop type) ---
		(assign, "$any_allies_at_the_last_battle", 0),
		(party_clear, "p_player_casualties"),
		(party_clear, "p_ally_casualties"),
		(party_get_skill_level, ":surgery", ":party_no", "skl_surgery"),
		(val_mul, ":surgery", 4),

		# Ally casualty routing: the host party's stacks (ally0) go through
		# the player-casualty path against the rejoiner's rebuilt party;
		# foreign partyids are AI attacker parties -- apply directly to the
		# campaign party like the enemy loop (no surgery, no player-casualty
		# accounting, no XP pool contribution). Dicts written before
		# @p_ally{i}_partyid existed fall back to the player path.
		(dict_get_int, "$coop_no_ally_parties", "$coop_dict", "@num_parties_ally"),
		(assign, reg1, "$coop_no_ally_parties"),
		(display_message, "@[BATTLE RESULTS] num_ally_parties={reg1}"),
		(dict_get_int, ":aa_host_party", "$coop_dict", "@battle_host_party"),
		(try_for_range, reg20, 0, "$coop_no_ally_parties"),
			(call_script, "script_coop_battle_dict_get_stack_cas_count", 1, reg20),
			(assign, ":num_cas_stacks", reg0),
			(assign, reg1, ":num_cas_stacks"),
			(display_message, "@[BATTLE RESULTS] ally{reg20}: cas_stacks={reg1}"),
			(assign, ":aa_partyid", -1),
			(try_begin),
				(call_script, "script_coop_battle_dict_has_roster_party", "$coop_dict", 1, reg20),
				(eq, reg0, 1),
				(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 1, reg20),
				(assign, ":aa_partyid", reg0),
			(try_end),
			(try_begin),
				(this_or_next|eq, ":aa_partyid", -1),
				(eq, ":aa_partyid", ":aa_host_party"),
				(try_for_range, reg21, 0, ":num_cas_stacks"),
					(call_script, "script_coop_battle_dict_get_stack_cas", 1, reg20, reg21),
					(assign, ":troop_id", reg0),
					(assign, ":dead", reg1),
					(assign, ":wounded", reg2),
					(call_script, "script_coop_apply_player_stack_casualty", ":party_no", ":troop_id", ":dead", ":wounded", ":surgery"),
				(try_end),
			(else_try),
				(gt, ":aa_partyid", 0),
				(party_is_active, ":aa_partyid"),
				(try_for_range, reg21, 0, ":num_cas_stacks"),
					(call_script, "script_coop_battle_dict_get_stack_cas", 1, reg20, reg21),
					(assign, ":troop_id", reg0),
					(assign, ":dead", reg1),
					(assign, ":wounded", reg2),
					(try_begin),
						(troop_is_hero, ":troop_id"),
						(store_random_in_range, ":rand_wound", 40, 71),
						(store_troop_health, ":hp", ":troop_id"),
						(val_sub, ":hp", ":rand_wound"),
						(val_max, ":hp", 1),
						(troop_set_health, ":troop_id", ":hp"),
					(else_try),
						(party_remove_members, ":aa_partyid", ":troop_id", ":dead"),
					(try_end),
					(party_wound_members, ":aa_partyid", ":troop_id", ":wounded"),
				(try_end),
			(try_end),
		(try_end),

		# Battle result for encounter resolution
		(dict_get_int, "$g_battle_result", "$coop_dict", "@battle_result"),
		(try_begin),
			(eq, "$g_battle_result", -1),
			(call_script, "script_party_count_members_with_full_health", ":party_no"),
			(assign, "$num_routed_us", reg0),
		(else_try),
			(eq, "$g_battle_result", 1),
			(call_script, "script_party_count_members_with_full_health", "p_collective_enemy"),
			(assign, "$num_routed_enemies", reg0),
		(try_end),

		# Dedicated siege win: capture the besieged center, mirroring the local
		# siege aftermath (event 17). @map_party_id holds the center party and
		# @map_type marks a player-attack siege; this block runs once (the whole
		# apply is gated on @battle_state == end_mp). Field battles have
		# @map_party_id == 0 and are unaffected.
		(try_begin),
			(eq, "$g_battle_result", 1),
			(dict_get_int, ":siege_map_type", "$coop_dict", "@map_type"),
			(eq, ":siege_map_type", coop_battle_type_siege_player_attack),
			(dict_get_int, ":siege_center", "$coop_dict", "@map_party_id"),
			(gt, ":siege_center", 0),
			(party_is_active, ":siege_center"),
			(party_clear, ":siege_center"),
			(call_script, "script_give_center_to_faction_aux", ":siege_center", "fac_player_faction"),
			(str_store_party_name, s1, ":siege_center"),
			(display_message, "@{s1} has fallen to the coop players!"),
		(try_end),

		# Battle aftermath: the campaign engine never resolves this battle
		# itself (it was fought on the battle server), and the rejoining
		# player gets a REBUILT party -- the original engaged party is gone,
		# so the enemy cannot be resolved via party_get_battle_opponent.
		# Use the dict party ids instead. Every enemy party is released from
		# the stale battle association; on victory non-center parties are
		# also destroyed (party_clear alone leaves a 0-troop party on the
		# map). Centers are owned by the siege capture block above.
		(try_for_range, reg20, 0, "$coop_no_enemy_parties"),
			(call_script, "script_coop_battle_dict_has_roster_party", "$coop_dict", 0, reg20),
			(eq, reg0, 1),
			(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 0, reg20),
			(assign, ":beaten_party", reg0),
			(gt, ":beaten_party", 0),
			(party_is_active, ":beaten_party"),
			(party_leave_cur_battle, ":beaten_party"),
			(party_set_slot, ":beaten_party", slot_party_coop_battle_slot, 0),
			(try_begin),
				(eq, "$g_battle_result", 1),
				(party_get_slot, ":beaten_type", ":beaten_party", slot_party_type),
				(neq, ":beaten_type", spt_castle),
				(neq, ":beaten_type", spt_town),
				(neq, ":beaten_type", spt_village),
				(party_clear, ":beaten_party"),
				(remove_party, ":beaten_party"),
				(assign, reg1, ":beaten_party"),
				(display_message, "@[BATTLE RESULTS] removed beaten party {reg1}"),
			(try_end),
		(try_end),

		# Release AI ally parties: leave the stale battle association and
		# clear the slot marker. Friendlies are never removed -- they resume
		# map AI regardless of result. ally0 (the initiator's write-time
		# party) is usually gone by now -- the rejoin rebuilt it -- hence the
		# party_is_active guard.
		(try_for_range, reg20, 0, "$coop_no_ally_parties"),
			(call_script, "script_coop_battle_dict_has_roster_party", "$coop_dict", 1, reg20),
			(eq, reg0, 1),
			(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 1, reg20),
			(assign, ":ar_party", reg0),
			(gt, ":ar_party", 0),
			(party_is_active, ":ar_party"),
			(party_leave_cur_battle, ":ar_party"),
			(party_set_slot, ":ar_party", slot_party_coop_battle_slot, 0),
			# A wiped non-hero ally (e.g. an allied caravan lost in a
			# siege) leaves an empty party the campaign engine never
			# garbage-collects. Remove it, same as beaten enemy parties
			# above -- but never the host party, and never a center.
			(try_begin),
				(neq, ":ar_party", ":aa_host_party"),
				(party_get_num_companions, ":ar_count", ":ar_party"),
				(le, ":ar_count", 0),
				(party_get_slot, ":ar_type", ":ar_party", slot_party_type),
				(neq, ":ar_type", spt_town),
				(neq, ":ar_type", spt_castle),
				(neq, ":ar_type", spt_village),
				(party_clear, ":ar_party"),
				(remove_party, ":ar_party"),
				(assign, reg1, ":ar_party"),
				(display_message, "@[BATTLE RESULTS] removed wiped ally party {reg1}"),
			(try_end),
		(try_end),

		(try_begin),
			(gt, ":party_no", 0),
			(party_is_active, ":party_no"),
			(party_leave_cur_battle, ":party_no"),
		(try_end),

		(dict_free, "$coop_dict"),

		# Save character with post-battle party state
		(call_script, "script_coop_save_character", ":player_no"),

		# Tell client to clear encounter -- the caller is a participant of
		# this battle by construction (gated above by :arp_participant).
		(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_encounter_resolved, 0),

		(display_message, "@[BATTLE RESULTS] applied. Encounter resolved."),

		(else_try),
			# Ended flag set but dict never reached end_mp: the battle
			# server died mid-battle (the DLL flags ended on IPC peer
			# loss). Release the parties and free the slot -- no results.
			# The state guard keeps a finished battle's dict (end_mp, a
			# non-participant joiner fell past the first arm) out of the
			# abort path -- it must wait in the retry arm for a participant.
			(eq, ":slot_ended", 1),
			(neq, ":state", coop_battle_state_end_mp),
			(dict_get_int, ":ab_num_enemy", "$coop_dict", "@num_parties_enemy"),
			(try_for_range, reg20, 0, ":ab_num_enemy"),
				(call_script, "script_coop_battle_dict_has_roster_party", "$coop_dict", 0, reg20),
				(eq, reg0, 1),
				(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 0, reg20),
				(assign, ":ab_party", reg0),
				(gt, ":ab_party", 0),
				(party_is_active, ":ab_party"),
				(party_leave_cur_battle, ":ab_party"),
				(party_set_slot, ":ab_party", slot_party_coop_battle_slot, 0),
			(try_end),
			(dict_get_int, ":ab_num_ally", "$coop_dict", "@num_parties_ally"),
			(try_for_range, reg20, 0, ":ab_num_ally"),
				(call_script, "script_coop_battle_dict_has_roster_party", "$coop_dict", 1, reg20),
				(eq, reg0, 1),
				(call_script, "script_coop_battle_dict_read_roster_party", "$coop_dict", 1, reg20),
				(assign, ":ab_aparty", reg0),
				(gt, ":ab_aparty", 0),
				(party_is_active, ":ab_aparty"),
				(party_leave_cur_battle, ":ab_aparty"),
				(party_set_slot, ":ab_aparty", slot_party_coop_battle_slot, 0),
			(try_end),
			(player_get_party_id, ":ab_pparty", ":player_no"),
			(try_begin),
				(gt, ":ab_pparty", 0),
				(party_is_active, ":ab_pparty"),
				(party_leave_cur_battle, ":ab_pparty"),
			(try_end),
			(dict_set_int, "$coop_dict", "@battle_state", coop_battle_state_abandoned),
			(call_script, "script_coop_battle_slot_dict_name", ":slot"),
			(dict_save, "$coop_dict", s41),
			(call_script, "script_coop_battle_slot_set_in_progress", ":slot", 0),
			(call_script, "script_coop_battle_slot_clear_ended", ":slot"),
			(call_script, "script_coop_battle_broadcast_slot_closed", ":slot"),
			(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_battle_rejected, 1),
			(display_message, "@[BATTLE RESULTS] battle server lost -- slot freed, parties released."),
			(dict_free, "$coop_dict"),
		(else_try),
			# Battle still running (in_progress poll) -- retry on next join
			(dict_free, "$coop_dict"),
		(try_end),
	]),

	# script_coop_compute_sp_xp_pool_from_dict
	# Input: $coop_dict loaded, @battle_xp_rand present
	# Output: reg0 = randomized pool (pre-strength-scaling)
	#
	# Direct port of party_give_xp_and_gold (SP, module_scripts.py:15286).
	# Iterates @p_enemy{i}_{j}_ded/wnd entries, applies (level+10)^2/10*size,
	# caps at 40000, multiplies by @battle_xp_rand/100.
	("coop_compute_sp_xp_pool_from_dict", [
		(assign, ":total_gain", 0),
		(dict_get_int, ":num_enemy_parties", "$coop_dict", "@num_parties_enemy"),
		(try_for_range, reg20, 0, ":num_enemy_parties"),
			(call_script, "script_coop_battle_dict_get_stack_cas_count", 0, reg20),
			(assign, ":num_cas_stacks", reg0),
			(try_for_range, reg21, 0, ":num_cas_stacks"),
				(call_script, "script_coop_battle_dict_get_stack_cas", 0, reg20, reg21),
				(assign, ":troop_id", reg0),
				(assign, ":dead", reg1),
				(assign, ":wounded", reg2),
				(store_add, ":stack_cas", ":dead", ":wounded"),
				(gt, ":stack_cas", 0),
				(neg|troop_is_hero, ":troop_id"),
				(store_character_level, ":enemy_level", ":troop_id"),
				(store_add, ":gain", ":enemy_level", 10),
				(val_mul, ":gain", ":gain"),
				(val_div, ":gain", 10),
				(store_mul, ":stack_gain", ":gain", ":stack_cas"),
				(val_add, ":total_gain", ":stack_gain"),
			(try_end),
		(try_end),
		(val_min, ":total_gain", 40000),
		(dict_get_int, ":rand_pct", "$coop_dict", "@battle_xp_rand"),
		(val_mul, ":total_gain", ":rand_pct"),
		(val_div, ":total_gain", 100),
		(assign, reg1, ":total_gain"),
		(display_message, "@[SP XP POOL] base={reg1}"),
		(assign, reg0, ":total_gain"),
	]),

	# Canonical XP application: distribute party_xp SP-style across the whole
	# party (hero + troop stacks) and apply hero_xp to the hero only. Both are
	# base-safe: a pending DLL set_xp for the hero accumulates the gained amount
	# into the DLL target instead of adding to a stale base. Each share applies
	# only when > 0 (additive, not exclusive).
	# INPUT: param1 player_no, param2 party_xp, param3 hero_xp
	("coop_apply_xp_shares", [
		(store_script_param, ":player_no", 1),
		(store_script_param, ":party_xp", 2),
		(store_script_param, ":hero_xp", 3),

		(player_get_party_id, ":party_no", ":player_no"),
		(player_get_troop_id, ":ptrp", ":player_no"),
		(str_store_player_username, s10, ":player_no"),

		# Party share -> SP-style distribution across all stacks (incl. hero).
		(try_begin),
			(gt, ":party_xp", 0),
			(troop_get_xp, ":pre_party_xp", ":ptrp"),
			(party_add_xp, ":party_no", ":party_xp"),
			(troop_get_xp, ":post_party_xp", ":ptrp"),
			(store_sub, ":hero_gained", ":post_party_xp", ":pre_party_xp"),
			(try_begin),
				(eq, "$g_coop_set_xp_go", 1),
				(eq, "$g_coop_set_xp_troop", ":ptrp"),
				(val_add, "$g_coop_set_xp_value", ":hero_gained"),
			(try_end),
			(assign, reg1, ":party_xp"),
			(display_message, "@[XP] {s10} +{reg1} party XP (party_add_xp)"),
		(try_end),

		# Hero share -> hero troop only.
		(try_begin),
			(gt, ":hero_xp", 0),
			(try_begin),
				(eq, "$g_coop_set_xp_go", 1),
				(eq, "$g_coop_set_xp_troop", ":ptrp"),
				(val_add, "$g_coop_set_xp_value", ":hero_xp"),
			(else_try),
				(add_xp_to_troop, ":hero_xp", ":ptrp"),
			(try_end),
			(assign, reg1, ":hero_xp"),
			(display_message, "@[XP] {s10} +{reg1} hero XP"),
		(try_end),
	]),

  # ==================================================================
  # CAMPAIGN: ECONOMY/MISC (merchant push, item drops, equipment/inventory/party-xp push)
  # ==================================================================

    # Push merchant inventory + trade good prices to a client for trade screen
    # INPUT: param1 = player_no, param2 = center_party, param3 = merchant_type
    ("coop_send_merchant_to_client",
    [
        (store_script_param, ":player_no", 1),
        (store_script_param, ":center_party", 2),
        (store_script_param, ":merchant_type", 3),

        # Resolve merchant troop from center party slot
        (assign, ":merchant_troop", -1),
        (try_begin),
            (eq, ":merchant_type", coop_merchant_type_weaponsmith),
            (party_get_slot, ":merchant_troop", ":center_party", slot_town_weaponsmith),
        (else_try),
            (eq, ":merchant_type", coop_merchant_type_armorer),
            (party_get_slot, ":merchant_troop", ":center_party", slot_town_armorer),
        (else_try),
            (eq, ":merchant_type", coop_merchant_type_horse),
            (party_get_slot, ":merchant_troop", ":center_party", slot_town_horse_merchant),
        (else_try),
            (eq, ":merchant_type", coop_merchant_type_goods),
            (party_get_slot, ":merchant_troop", ":center_party", slot_town_merchant),
        (else_try),
            (eq, ":merchant_type", coop_merchant_type_village_elder),
            (party_get_slot, ":merchant_troop", ":center_party", slot_town_elder),
        (try_end),

        (try_begin),
            (gt, ":merchant_troop", 0),
            # Store which merchant troop the player is trading with (for trade_change)
            (player_set_slot, ":player_no", slot_player_coop_merchant_troop, ":merchant_troop"),

            # Push trade good prices for goods/village merchants
            (try_begin),
                (this_or_next|eq, ":merchant_type", coop_merchant_type_goods),
                (eq, ":merchant_type", coop_merchant_type_village_elder),
                (try_for_range, ":offset", 0, num_trade_goods),
                    (store_add, ":price_slot", slot_town_trade_good_prices_begin, ":offset"),
                    (party_get_slot, ":price", ":center_party", ":price_slot"),
                    (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                        multiplayer_event_multiplayer_campaign_server_event_center_trade_price, ":offset", ":price"),
                (try_end),
            (try_end),

            # Push player gold
            (player_get_troop_id, ":troop_no", ":player_no"),
            (store_troop_gold, ":gold", ":troop_no"),
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_trade_gold_sync, ":gold"),

            # Clear + push merchant inventory
            (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_trade_merchant_slot, -1, 0, 0),
            (try_for_range, ":slot", 0, 96),
                (troop_get_inventory_slot, ":item", ":merchant_troop", ":slot"),
                (ge, ":item", 0),
                (troop_get_inventory_slot_modifier, ":imod", ":merchant_troop", ":slot"),
                (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                    multiplayer_event_multiplayer_campaign_server_event_trade_merchant_slot, ":slot", ":item", ":imod"),
            (try_end),

            # Signal sync done -> client opens trade screen
            (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                multiplayer_event_multiplayer_campaign_server_event_trade_sync_done, 0),
        (try_end),
    ]),

   # Server-authoritative inventory commit for a client's inventory-screen
   # batch (event 15). The native inventory screen can only move, equip, or
   # drop items -- it never introduces new item types (trade/drops/quests are
   # applied server-side before the diff). So the post-edit troop inventory
   # must be a sub-multiset of the pre-edit one: no item type's count may
   # increase. The pre-edit inventory is still on disk in the char dict
   # (coop_save_character runs only after this check), so we validate against
   # it, commit on success, and revert the whole batch from the dict on any
   # violation -- blocking a client from minting or duplicating items.
   # Per-player dict, so concurrent inventory batches from different players
   # do not race.
   ("coop_inv_sync_back_validate_and_save",
   [
       (store_script_param, ":player_no", 1),
       (player_get_troop_id, ":troop_no", ":player_no"),
       (str_store_player_username, s10, ":player_no"),
       (str_store_string, s11, "@coop_char_{s10}"),

       (dict_create, "$coop_inv_base"),
       (dict_load_file, "$coop_inv_base", s11),

       # Validate: for each item held post-edit, its count in the troop must
       # not exceed its count in the pre-edit dict baseline.
       (assign, ":ok", 1),
       (try_for_range, ":slot", 0, 106),
           (eq, ":ok", 1),
           (troop_get_inventory_slot, ":item", ":troop_no", ":slot"),
           (gt, ":item", 0),

           (assign, ":post_ct", 0),
           (try_for_range, ":s2", 0, 106),
               (troop_get_inventory_slot, ":it2", ":troop_no", ":s2"),
               (eq, ":it2", ":item"),
               (val_add, ":post_ct", 1),
           (try_end),

           (assign, ":base_ct", 0),
           (try_for_range, ":s3", 0, 9),
               (assign, reg5, ":s3"),
               (str_store_string, s12, "@char_itm_{reg5}"),
               (try_begin),
                   (dict_has_key, "$coop_inv_base", s12),
                   (dict_get_int, ":bitem", "$coop_inv_base", s12),
                   (eq, ":bitem", ":item"),
                   (val_add, ":base_ct", 1),
               (try_end),
           (try_end),
           (try_for_range, ":s4", 10, 106),
               (assign, reg5, ":s4"),
               (str_store_string, s12, "@char_bag_{reg5}"),
               (try_begin),
                   (dict_has_key, "$coop_inv_base", s12),
                   (dict_get_int, ":bitem", "$coop_inv_base", s12),
                   (eq, ":bitem", ":item"),
                   (val_add, ":base_ct", 1),
               (try_end),
           (try_end),

           (gt, ":post_ct", ":base_ct"),
           (assign, ":ok", 0),
           (display_message, "@[INV GUARD] {s10}: rejected inventory batch (item minted/duplicated)"),
       (try_end),

       (try_begin),
           (eq, ":ok", 1),
           (call_script, "script_coop_save_character", ":player_no"),
       (else_try),
           # Revert equipment slots 0-8 from the baseline dict.
           (try_for_range, ":slot", 0, 9),
               (assign, reg5, ":slot"),
               (str_store_string, s12, "@char_itm_{reg5}"),
               (assign, ":bitem", -1),
               (assign, ":bimod", 0),
               (try_begin),
                   (dict_has_key, "$coop_inv_base", s12),
                   (dict_get_int, ":bitem", "$coop_inv_base", s12),
                   (str_store_string, s13, "@char_imd_{reg5}"),
                   (try_begin),
                       (dict_has_key, "$coop_inv_base", s13),
                       (dict_get_int, ":bimod", "$coop_inv_base", s13),
                   (try_end),
               (try_end),
               (troop_set_inventory_slot, ":troop_no", ":slot", ":bitem"),
               (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":bimod"),
           (try_end),
           # Revert bag slots 10-105: present keys restored, others cleared.
           (try_for_range, ":slot", 10, 106),
               (assign, reg5, ":slot"),
               (str_store_string, s12, "@char_bag_{reg5}"),
               (try_begin),
                   (dict_has_key, "$coop_inv_base", s12),
                   (dict_get_int, ":bitem", "$coop_inv_base", s12),
                   (str_store_string, s13, "@char_bag_mod_{reg5}"),
                   (assign, ":bimod", 0),
                   (try_begin),
                       (dict_has_key, "$coop_inv_base", s13),
                       (dict_get_int, ":bimod", "$coop_inv_base", s13),
                   (try_end),
                   (troop_set_inventory_slot, ":troop_no", ":slot", ":bitem"),
                   (troop_set_inventory_slot_modifier, ":troop_no", ":slot", ":bimod"),
               (else_try),
                   (troop_set_inventory_slot, ":troop_no", ":slot", -1),
               (try_end),
           (try_end),
           # Re-push authoritative inventory so the client's view matches.
           (call_script, "script_coop_send_equipment_to_client", ":player_no"),
           (call_script, "script_coop_send_inventory_to_client", ":player_no"),
       (try_end),
       (dict_free, "$coop_inv_base"),
   ]),

   # Sends the player's 9 equipment slots to the client via coop_event_inv_troop_set_slot.
   # Client stores in trp_temp_troop slots 0-8 (items) and 10-18 (modifiers).
   ("coop_send_equipment_to_client",
   [
       (store_script_param, ":player_no", 1),
       (player_get_troop_id, ":troop_no", ":player_no"),
       (try_for_range, ":slot", 0, 9),
           (troop_get_inventory_slot, ":item", ":troop_no", ":slot"),
           (troop_get_inventory_slot_modifier, ":imod", ":troop_no", ":slot"),
           (multiplayer_send_4_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events, multiplayer_event_multiplayer_campaign_server_event_equip_slot, ":slot", ":item", ":imod"),
       (try_end),
   ]),

   ("coop_send_inventory_to_client",
   [
       # Sends bag inventory (slots 10-105) to the requesting client.
       # Equipment (slots 0-9) is already pushed on join via coop_send_equipment_to_client.
       (store_script_param, ":player_no", 1),
       (player_get_troop_id, ":troop_no", ":player_no"),
       # Send clear signal (slot=-1) then only non-empty bag slots.
       # This avoids sending all 96 slots (which overflows the send buffer)
       # while still clearing stale client data from previous sessions.
       (multiplayer_send_4_int_to_player, ":player_no",
           multiplayer_event_multiplayer_campaign_server_events,
           multiplayer_event_multiplayer_campaign_server_event_inv_bag_slot,
           -1, 0, 0),
       (try_for_range, ":slot", 10, 106),
           (troop_get_inventory_slot, ":item", ":troop_no", ":slot"),
           (try_begin),
               (neq, ":item", -1),
               (gt, ":item", 0),
               (troop_get_inventory_slot_modifier, ":imod", ":troop_no", ":slot"),
               (multiplayer_send_4_int_to_player, ":player_no",
                   multiplayer_event_multiplayer_campaign_server_events,
                   multiplayer_event_multiplayer_campaign_server_event_inv_bag_slot,
                   ":slot", ":item", ":imod"),
           (try_end),
       (try_end),
       (multiplayer_send_2_int_to_player, ":player_no",
           multiplayer_event_multiplayer_campaign_server_events,
           multiplayer_event_multiplayer_campaign_server_event_inv_sync_done, 0),
   ]),

   ("coop_send_party_upgradeable_to_client",
   [
       (store_script_param, ":player_no", 1),
       (player_get_party_id, ":party_no", ":player_no"),
       (try_begin),
           (party_is_active, ":party_no"),
           (party_get_num_companion_stacks, ":num_stacks", ":party_no"),
           (try_for_range, ":i", 0, ":num_stacks"),
               (party_stack_get_troop_id, ":trp", ":party_no", ":i"),
               (neg|troop_is_hero, ":trp"),
               (party_stack_get_num_upgradeable, ":upg", ":party_no", ":i"),
               (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_multiplayer_campaign_server_events,
                   multiplayer_event_multiplayer_campaign_server_event_party_stack_num_upgradeable, ":i", ":upg"),
           (try_end),
       (try_end),
   ]),

  #script_coop_generate_item_drop
  # INPUT: none
  # OUTPUT: reg0 = item_id
  ("coop_generate_item_drop",
   [
     (store_script_param, ":player_id", 1),
     #(store_script_param, ":instance_id", 1),
     #(store_script_param, ":user_id", 2),

     (store_random_in_range, "$g_ccoop_currently_dropping_item", coop_drops_begin, coop_drops_end), #change this to add variation to the items that drop - any item should work! The description will be hidden for regular items
     #(assign, "$g_ccoop_currently_dropping_item", "itm_javelin_bow"), ##DEBUG - makes chests always drop the same item - useful for testing!
     (player_set_slot, ":player_id", slot_player_coop_dropped_item, "$g_ccoop_currently_dropping_item"), #we hold the item in a slot, server-side, to prevent funny business!
     #(assign, reg0, ":dropped_item"),
     
     
     ]),

  #script_coop_drop_item
  # INPUT: arg1 = item_id
  # OUTPUT: none
  ("coop_drop_item",
   [
     (store_script_param, reg0, 1),
     (store_script_param, reg1, 2),
     (store_script_param, reg2, 3),
     
     #script simply starts the presentation but could have extra features added

     (start_presentation, "prsnt_coop_assign_drop_to_group_member"),
     
     
     ]),
]
