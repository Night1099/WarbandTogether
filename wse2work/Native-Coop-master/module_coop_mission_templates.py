# -*- coding: cp1254 -*-
from header_common import *
from header_operations import *
from header_mission_templates import *
from header_animations import *
from header_sounds import *
from header_music import *
from header_items import *
from module_constants import *

#from module_mission_templates import *


####################################################################################################################
#   Each mission-template is a tuple that contains the following fields:
#  1) Mission-template id (string): used for referencing mission-templates in other files.
#     The prefix mt_ is automatically added before each mission-template id
#
#  2) Mission-template flags (int): See header_mission-templates.py for a list of available flags
#  3) Mission-type(int): Which mission types this mission template matches.
#     For mission-types to be used with the default party-meeting system,
#     this should be 'charge' or 'charge_with_ally' otherwise must be -1.
#     
#  4) Mission description text (string).
#  5) List of spawn records (list): Each spawn record is a tuple that contains the following fields:
#    5.1) entry-no: Troops spawned from this spawn record will use this entry
#    5.2) spawn flags.
#    5.3) alter flags. which equipment will be overriden
#    5.4) ai flags.
#    5.5) Number of troops to spawn.
#    5.6) list of equipment to add to troops spawned from here (maximum 8).
#  6) List of triggers (list).
#     See module_triggers.py for infomation about triggers.
#
#  Please note that mission templates is work in progress and can be changed in the future versions.
# 
####################################################################################################################


coop_server_check_polls = (
  1, 5, 0,
  [
    (multiplayer_is_server),
    (eq, "$g_multiplayer_poll_running", 1),
    (eq, "$g_multiplayer_poll_ended", 0),
    (store_mission_timer_a, ":mission_timer"),
    (store_add, ":total_votes", "$g_multiplayer_poll_no_count", "$g_multiplayer_poll_yes_count"),
    (this_or_next|eq, ":total_votes", "$g_multiplayer_poll_num_sent"),
    (gt, ":mission_timer", "$g_multiplayer_poll_end_time"),
    (call_script, "script_cf_multiplayer_evaluate_poll"),
    ],
  [
    (assign, "$g_multiplayer_poll_running", 0),
    ])


coop_store_respawn_as_bot = (  
      ti_on_agent_killed_or_wounded, 0, 0, [(multiplayer_is_server)],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (try_begin),#store player location for respawn as bot
           
           (agent_is_human, ":dead_agent_no"),
           (neg|agent_is_non_player, ":dead_agent_no"),

           (ge, ":dead_agent_no", 0),
           (agent_get_player_id, ":dead_agent_player_id", ":dead_agent_no"),
           (ge, ":dead_agent_player_id", 0),

           (set_fixed_point_multiplier, 100),

           (agent_get_player_id, ":dead_agent_player_id", ":dead_agent_no"),
           (agent_get_position, pos0, ":dead_agent_no"),

           (position_get_x, ":x_coor", pos0),
           (position_get_y, ":y_coor", pos0),
           (position_get_z, ":z_coor", pos0),
         
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_x, ":x_coor"),
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_y, ":y_coor"),
           (player_set_slot, ":dead_agent_player_id", slot_player_death_pos_z, ":z_coor"),
         (try_end), 
 
    ])



coop_respawn_as_bot = (  
      2, 0, 0, [
        (multiplayer_is_server),
        (eq, "$g_multiplayer_player_respawn_as_bot", 1),
      ],#respawn as bot
       [
       #spawning as a bot (if option ($g_multiplayer_player_respawn_as_bot) is 1)
         (get_max_players, ":num_players"),
         (try_for_range, ":player_no", 0, ":num_players"),
           (player_is_active, ":player_no"),
           (neg|player_is_busy_with_menus, ":player_no"),
           (try_begin),
            (player_get_team_no, ":player_team", ":player_no"),

            (assign, ":value_4", 0),
            (player_get_agent_id, ":player_agent", ":player_no"),
            (try_begin),
             (ge, ":player_agent", 0),
             (neg|agent_is_alive, ":player_agent"),
             (assign, ":value_4", 1),
            (else_try),
             (lt, ":player_agent", 0),
             (player_get_slot, ":player_selected_troop", ":player_no", slot_player_coop_selected_troop),
             (le, ":player_selected_troop", 0),
             (assign, ":value_4", 2),
            (try_end),
            (gt, ":value_4", 0),

             # (agent_get_time_elapsed_since_removed, ":elapsed_time", ":player_agent"),
             # (gt, ":elapsed_time", "$g_multiplayer_respawn_period"),

             (assign, ":is_found", 0),
             (try_for_agents, ":cur_agent"),
               (eq, ":is_found", 0),
               (agent_is_alive, ":cur_agent"),
               (agent_is_human, ":cur_agent"),
               (agent_is_non_player, ":cur_agent"),
               (agent_get_team ,":cur_team", ":cur_agent"),
               (eq, ":cur_team", ":player_team"),
               (agent_get_position, pos0, ":cur_agent"),
               (assign, ":is_found", 1),
             (try_end),

            (try_begin), #if we have not spawned store pos of ally
             (eq, ":value_4", 2),
             (set_fixed_point_multiplier, 100),
             (position_get_x, ":x_coor", pos0),
             (position_get_y, ":y_coor", pos0),
             (position_get_z, ":z_coor", pos0),
             (player_set_slot, ":player_no", slot_player_death_pos_x, ":x_coor"),
             (player_set_slot, ":player_no", slot_player_death_pos_y, ":y_coor"),
             (player_set_slot, ":player_no", slot_player_death_pos_z, ":z_coor"),
            (try_end),

             (try_begin),
               (eq, ":is_found", 1),
               (call_script, "script_find_most_suitable_bot_to_control", ":player_no"),
               (player_control_agent, ":player_no", reg0),
             (try_end),
           (try_end),
         (try_end),
         ])



# Trigger Param 1: damage inflicted agent_id
# Trigger Param 2: damage dealer agent_id
# Trigger Param 3: inflicted damage
# Register 0: damage dealer item_id
# Position Register 0: position of the blow
#                      rotation gives the direction of the blow
# Trigger result: if returned result is greater than or equal to zero, inflicted damage is set to the value specified by the module.
coop_server_reduce_damage = (
  ti_on_agent_hit, 0, 0,
    [    
      (multiplayer_is_server),
      (eq, "$coop_reduce_damage", 1),
    ],
    [
        (store_trigger_param_1, ":hit_agent"),
        (store_trigger_param_2, ":attacker_agent"),
        (store_trigger_param_3, ":damage"),
        # (assign, ":weapon", reg0),
        (gt, ":damage", 0), #dont do anything for 0 damage
        (agent_is_human, ":hit_agent"),
        (agent_is_human, ":attacker_agent"),
        (neg|agent_is_non_player, ":hit_agent"), #damage is for player agent
        (store_div, ":new_damage", ":damage", 4),
        (set_trigger_result, ":new_damage"),
    ])

#player_crouch_coop = (0, 0, 2,
#  [
#   ###No multiplayer until patch for crouching
# (neg|multiplayer_is_server), #Only if player is NOT server possibly unneeded.
# (neg|game_in_multiplayer_mode), #Only if game is NOT in multiplayer
# ##No multiplayer until patch for crouching
#  (neg|main_hero_fallen),(key_clicked,"$key_crouch"),
#   (get_player_agent_no, ":player_agent"), 
#   (gt,  ":player_agent", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#   (agent_get_horse, ":horse", ":player_agent"), 
#   (le, ":horse", 0),
#
#   (try_begin),
#   #pavise_related_things BEGIN
#   #   (key_is_down, key_left_control),
#   #   (call_script, "script_deploy_pavise", ":player_agent"),
#   #(else_try),
#   #pavise_related_things END
#      (agent_get_slot, ":crouching", ":player_agent", slot_agent_crouching),
#      (eq, ":crouching", 0),
#      (agent_set_animation, ":player_agent", "anim_stand_to_crouch"),
#      (agent_set_slot, ":player_agent", slot_agent_crouching, 1),
#   (else_try),         
#      (agent_set_animation, ":player_agent", "anim_crouch_to_stand"),
#      (agent_set_slot, ":player_agent", slot_agent_crouching, 0),
#   (try_end)], [])
#
#crouching_command_coop = (0, 0, 0,
#  [
#   ###No multiplayer until patch for crouching
# (neg|multiplayer_is_server), #Only if player is NOT server possibly unneeded.
# (neg|game_in_multiplayer_mode), #Only if game is NOT in multiplayer
# ##No multiplayer until patch for crouching
#  (neg|main_hero_fallen),
#   (assign, ":command", -1),
#   (try_begin),
#     (key_clicked, "$key_crouch_command"),
#     #Pavise related things BEGIN
#     #(try_begin),
#     #   (key_is_down, key_left_control),
#     #   (assign, ":command", 2),
#     #(else_try),
#     #Pavise related things END
#        (assign, ":command", 1),
#     #Pavise related things BEGIN
#     #(try_end),   
#     #Pavise related things END
#   (else_try),
#     (key_clicked, "$key_stand_command"),   
#     (assign, ":command", 0),
#   (try_end),
#   (ge, ":command", 0),
#   (call_script, "script_cf_crouch_command_coop", ":command"),], []) 
#   
#crouching_scan = (0, 0, 0,  [
# ###No multiplayer until patch for crouching
# (neg|multiplayer_is_server), #Only if player is NOT server possibly unneeded.
# (neg|game_in_multiplayer_mode), #Only if game is NOT in multiplayer
# ##No multiplayer until patch for crouching
#(call_script, "script_crouching_scan"),], [])
#
#crouching_triggers = [player_crouch_coop,crouching_command_coop,crouching_scan]
coop_mission_templates = [
    # --- Local SP battle for coop clients ---
    # Uses mtef_visitor_source so troops come from set_visitor() calls,
    # bypassing the engine's m_involvedPartyNos which isn't populated on MP clients.
    # Entry 0: player (team 0, defender side)
    # Entries 1-15: player's party troops (team 0)
    # Entries 16-31: enemy troops (team 1)
    (
    "coop_local_battle",mtf_battle_mode|mtf_synch_inventory,-1,
    "You lead your men to battle.",
    [
     (0,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (1,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (2,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (3,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (4,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (5,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (6,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (7,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (8,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (9,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (10,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (11,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (12,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (13,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (14,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (15,mtef_visitor_source|mtef_team_0,0,aif_start_alarmed,1,[]),
     (16,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (17,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (18,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (19,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (20,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (21,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (22,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (23,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (24,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (25,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (26,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (27,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (28,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (29,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (30,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     (31,mtef_visitor_source|mtef_team_1,0,aif_start_alarmed,1,[]),
     ],
    [
      (ti_on_agent_spawn, 0, 0, [],
       [
         (store_trigger_param_1, ":agent_no"),
         (agent_get_troop_id, ":troop_id", ":agent_no"),
         (agent_set_team, ":agent_no", 0),
         # Enemies at entries 16-31 are team 1
         (agent_get_entry_no, ":entry", ":agent_no"),
         (try_begin),
             (ge, ":entry", 16),
             (agent_set_team, ":agent_no", 1),
         (try_end),
       ]),

      (ti_tab_pressed, 0, 0,
       [],
       [(try_begin),
          (neq, "$g_battle_result", 0),
          (set_trigger_result, 1),
        (else_try),
          (display_message, "@Cannot leave during battle."),
        (try_end),
       ]),

      # Battle end detection
      (3, 0, 0,
       [(main_hero_fallen),],
       [(assign, "$g_battle_result", -1),
        (set_mission_result, -1),
        (finish_mission, 0),
       ]),

      (1, 4, ti_once,
       [
         (store_mission_timer_a, ":time"),
         (ge, ":time", 4),
         (all_enemies_defeated, 2),
       ],
       [
         (assign, "$g_battle_result", 1),
         (set_mission_result, 1),
         (finish_mission, 1),
       ]),
    ]
    ),


# USE FOR COOP BATTLE
    (
    "coop_battle",mtf_battle_mode,-1,
    "You lead your men to battle.",
    [     #need spawns 0-63 in multiplayer mode
      (0,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (1,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (2,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (3,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (4,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (5,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (6,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (7,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),

      (8,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (9,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (10,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,0,1,[]),
      (11,mtef_visitor_source|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),#NEW
      (12,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (13,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (14,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (15,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (16,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (17,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (18,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (19,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (20,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (21,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (22,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (23,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (24,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (25,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (26,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (27,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (28,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (29,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (30,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (31,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (32,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (33,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (34,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (35,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (36,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (37,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (38,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (39,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (40,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (41,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (42,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (43,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (44,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (45,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (46,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (47,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (48,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (49,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (50,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (51,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (52,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (53,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (54,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (55,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (56,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (57,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (58,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (59,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (60,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (61,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (62,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (63,mtef_visitor_source,0,aif_start_alarmed,1,[]),

     ],
    [

      coop_server_check_polls,
      coop_server_reduce_damage,
      coop_respawn_as_bot,
      coop_store_respawn_as_bot,


#mordr does not work in MP = SCRIPT ERROR ON OPCODE 1785: Invalid Group ID: 1;
     # common_battle_order_panel,
     # common_battle_order_panel_tick,

#multiplayer_once_at_the_first_frame
      
      (ti_server_player_joined, 0, 0, [],
       [
        (store_trigger_param_1, ":player_no"),
       #  (call_script, "script_multiplayer_server_player_joined_common", ":player_no"), #dont clear slots
        (call_script, "script_multiplayer_send_initial_information", ":player_no"),
        (call_script, "script_coop_server_player_joined_common", ":player_no"),

        # Auto-load battle data when first player joins
        (try_begin),
          (eq, "$coop_battle_state", coop_battle_state_none),
          (call_script, "script_coop_on_admin_panel_load"),
          (try_begin),
            (eq, "$coop_battle_state", coop_battle_state_setup_mp),
            (team_set_faction, 0, "$coop_team_1_faction"),
            (team_set_faction, 1, "$coop_team_2_faction"),
            (assign, "$g_multiplayer_team_1_faction", "$coop_team_1_faction"),
            (assign, "$g_multiplayer_team_2_faction", "$coop_team_2_faction"),
            (assign, "$g_multiplayer_next_team_1_faction", "$coop_team_1_faction"),
            (assign, "$g_multiplayer_next_team_2_faction", "$coop_team_2_faction"),
            (try_begin),
              # First load: restart mission on correct scene
              (eq, "$coop_scene_loaded", 0),
              (assign, "$coop_needs_scene_restart", 1),
            (else_try),
              # Second load (after scene restart): start the battle
              (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
              (assign, "$coop_battle_started", 1),
            (try_end),
          (try_end),
        (try_end),

        # Skip player 0 — that's the dedicated server, not a real player
        (try_begin),
          (gt, ":player_no", 0),
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_return_next_team_faction, 1, "$coop_team_1_faction"),
          (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_return_next_team_faction, 2, "$coop_team_2_faction"),
          (player_set_team_no, ":player_no", 1),
          # Assign campaign troop and load character data from persisted dict
          (store_add, ":troop_no", multiplayer_campaign_player_troops_begin, ":player_no"),
          (player_set_troop_id, ":player_no", ":troop_no"),
          (call_script, "script_coop_load_character", ":player_no"),
        (try_end),

         ]),

      # Deferred mission restart — start_multiplayer_mission can't run during player join
      (1, 0, 0,
       [(multiplayer_is_server),
        (eq, "$coop_needs_scene_restart", 1),
       ],
       [
        (assign, "$coop_needs_scene_restart", 0),
        (assign, "$coop_scene_loaded", 1),
        # Reset dict and state so battle data re-loads fresh after scene change
        (try_begin),
          (neg|is_vanilla_warband),
          (dict_create, ":d"),
          (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
          (dict_load_file, ":d", s41, 2),
          (dict_set_int, ":d", "@battle_state", coop_battle_state_setup_sp),
          (dict_save, ":d", s41),
          (dict_free, ":d"),
        (try_end),
        (assign, "$coop_battle_state", coop_battle_state_none),
        (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
        (start_multiplayer_mission, reg0, "$coop_battle_scene", 1),
       ]),

      (ti_before_mission_start, 0, 0, [],
       [
         (assign, "$g_multiplayer_game_type", multiplayer_game_type_coop_battle),
#remove
#         (call_script, "script_multiplayer_server_before_mission_start_common"), #dont set time of day, reset commanded troops
 #        (call_script, "script_multiplayer_init_mission_variables"),
##########
         (call_script, "script_initialize_banner_info"),
         (call_script, "script_coop_init_mission_variables"),
         (assign, "$coop_needs_scene_restart", 0),

         # Pre-read factions from dict so engine starts with correct teams
         (try_begin),
           (neg|is_vanilla_warband),
           (dict_create, ":pre_dict"),
           (call_script, "script_coop_battle_slot_dict_name", "$coop_battle_slot"),
           (dict_load_file, ":pre_dict", s41, 2),
           (dict_get_int, ":enemy_fac", ":pre_dict", "@tm0_fac"),
           (dict_get_int, ":ally_fac", ":pre_dict", "@tm1_fac"),
           (dict_free, ":pre_dict"),
           (try_begin),
             (gt, ":enemy_fac", 0),
             (team_set_faction, 0, ":enemy_fac"),
             (team_set_faction, 1, ":ally_fac"),
             (assign, "$g_multiplayer_team_1_faction", ":enemy_fac"),
             (assign, "$g_multiplayer_team_2_faction", ":ally_fac"),
             (assign, "$g_multiplayer_next_team_1_faction", ":enemy_fac"),
             (assign, "$g_multiplayer_next_team_2_faction", ":ally_fac"),
           (try_end),
         (try_end),



         (assign, "$g_waiting_for_confirmation_to_terminate", 0),
         (assign, "$g_round_ended", 0),
         (assign, "$coop_winner_team", -1),
         (assign, "$coop_battle_started", 0),

        # (assign, reg1, "$coop_time_of_day"), 
        # (assign, reg2, "$coop_cloud"), 
        # (assign, reg3, "$coop_haze"), 
        # (display_message, "@time {reg1} cloud {reg2} haze {reg3}"),

          #set_weather
         (scene_set_day_time, "$coop_time_of_day"),
	       (set_global_cloud_amount, "$coop_cloud"),
	       (set_global_haze_amount, "$coop_haze"),

          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (set_global_haze_amount, 95), #remove sunlight
         # (try_end),

         (assign, ":rain_amount", "$coop_cloud"),
         (assign, ":rain_type", "$coop_rain"),
         (try_begin),
           (lt, ":rain_amount", 75), #less than = no rain
           (assign, ":rain_amount", 0),
           (assign, ":rain_type", 0),
         (try_end),
         (set_rain, ":rain_type" , ":rain_amount"), #1=rain 2=snow

         ]),

      # Initial spawn — one life per battle, no respawn after death
      (1, 0, 0,
       [(multiplayer_is_server),
        (eq, "$coop_battle_started", 1),
       ],
       [
        (get_max_players, ":num_players"),
        (try_for_range, ":player_no", 1, ":num_players"),
          (player_is_active, ":player_no"),
          (neg|player_is_busy_with_menus, ":player_no"),
          (player_slot_eq, ":player_no", slot_player_spawned_this_round, 0),
          (player_get_agent_id, ":agent_id", ":player_no"),
          (lt, ":agent_id", 0),
          (player_get_team_no, ":team", ":player_no"),
          (lt, ":team", multi_team_spectator),
          (player_get_troop_id, ":troop", ":player_no"),
          (ge, ":troop", 0),
          (player_spawn_new_agent, ":player_no", 0),
          (player_set_slot, ":player_no", slot_player_spawned_this_round, 1),
        (try_end),
       ]),

      (ti_after_mission_start, 0, 0, [],
       [
         (call_script, "script_initialize_all_scene_prop_slots"),
         (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),
         (call_script, "script_multiplayer_move_moveable_objects_initial_positions"),
         (assign, "$g_multiplayer_bot_type_1_wanted", 1),#set player wants all troops in party (host will override clients)#this should be optional

        # (assign, "$g_multiplayer_ready_for_spawning_agent", 1), #set by start battle command in presentations

          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),#limit fog
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (try_begin),
             # (eq,  "$coop_rain", 2), #if snow
             # (set_fog_distance, 200), #set fog closer
           # (else_try),
             # (set_fog_distance, 600),
           # (try_end),
         # (try_end),

        (try_begin),
          (multiplayer_is_server),
          (start_presentation, "prsnt_coop_start_battle"),
        (else_try),
          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_is_admin, ":my_player_no"),
          (start_presentation, "prsnt_coop_start_battle"),
        (try_end),

        (try_begin),
          (multiplayer_is_server),
          (assign, "$coop_reinforce_size", 10),
          (assign, "$coop_reinforce", 1),
          (assign, "$coop_alive_team1", 0),#store count for reinforcement spawn
          (assign, "$coop_alive_team2", 0),


            #init spawn positions
          (entry_point_get_position, pos25, 32),
          (copy_position, pos26, pos25),
          (position_move_y, pos26, 600),
          (copy_position, pos27, pos25),
          (position_move_y, pos27, 1500),

          (entry_point_get_position, pos30, 0),
          (copy_position, pos31, pos30),
          (position_move_y, pos31, 600),
          (copy_position, pos32, pos30),
          (position_move_y, pos32, 1500),

            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, ":ally", 1), 
              (assign, ":enemy", 2),#inside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, ":ally", 2),#inside village
              (assign, ":enemy", 1),
            (else_try),
              (assign, ":ally", 0),
              (assign, ":enemy", 32),
            (try_end),

           (entry_point_get_position, pos2, ":enemy"),
           (entry_point_get_position, pos3, ":ally"),
           (position_set_z_to_ground_level, pos2),
           (position_set_z_to_ground_level, pos3),

           (set_spawn_position, pos2),
           (spawn_scene_prop, "spr_coop_inventory", 0),   

           (set_spawn_position, pos3),
           (spawn_scene_prop, "spr_coop_inventory", 0),  
           (assign, "$coop_inventory_box", reg0),

        (try_end),

        ]),



 #multiplayer_server_spawn_bots
      (0, 0, 0, [],
       [
        (try_begin),
        (multiplayer_is_server),
        (eq, "$g_multiplayer_ready_for_spawning_agent", 1),


        (assign, ":battle_size", "$coop_battle_size"),
        (try_begin), 
          (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
          (assign, ":battle_size", coop_min_battle_size),
        (try_end),

        #regulate troop spawn
        (store_add, ":total_bots", "$coop_alive_team1", "$coop_alive_team2"),
        (store_sub, ":reinforce_bots", ":battle_size", "$coop_reinforce_size"),#when less troops than battle size
        (try_begin),
          (le, ":total_bots", ":reinforce_bots"), #when total alive < battle size - reinforce size
          (assign, "$coop_reinforce", 1),
        (try_end),
        (try_begin),
          (ge, ":total_bots", ":battle_size"), 
          (assign, "$coop_reinforce", 0),
        (try_end),

        (try_begin),
          (eq, "$coop_reinforce", 1), #ready for reinforcements

          #pick team by size
          (store_add, ":total_req", "$coop_num_bots_team_1", "$coop_num_bots_team_2"),
          (gt, ":total_req", 0), #reserves 

          (assign, ":alive_team1", "$coop_alive_team1"),
          (assign, ":alive_team2", "$coop_alive_team2"),
          (val_max, ":alive_team1", 1),
          (val_mul, ":alive_team2", 1000),
          (store_div, ":ratio_current", ":alive_team2", ":alive_team1"), 

          (try_begin),
            (this_or_next|eq, "$coop_num_bots_team_2", 0), #skip ratio if other team has no reinforcements
            (ge, ":ratio_current", "$coop_team_ratio"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),#add to team 1
          (else_try),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),#add to team 2
          (try_end),



          #if one team is almost out of troops, choose that team
          (try_begin), #use one try so small armies don't override
            (le, "$coop_alive_team1", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),
          (else_try),
            (le, "$coop_alive_team2", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),
          (try_end),

          (call_script, "script_coop_find_bot_troop_for_spawn", ":selected_team"),
          (assign, ":selected_troop", reg0),

          (try_begin),
            (eq, ":selected_team", 0),     
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, reg0, 2),#peasants inside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, reg0, 1),#bandits outside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
              (store_random_in_range, ":random_entry_point", 2, 11),
              (assign, reg0, ":random_entry_point"),#bandits 
            (else_try),
              (assign, reg0, 32),#spawn point 32
            (try_end),
          (else_try),
            (try_begin),#player team
              (eq, "$coop_battle_type", coop_battle_type_village_player_attack),
              (assign, reg0, 1), #player outside village
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_village_player_defend),
              (assign, reg0, 2),#player inside village

#NEW
            (else_try),
              (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
              (assign, reg0, 11),#player inside village

            (else_try),
              (assign, reg0, 0),#spawn point 0
            (try_end),
          (try_end),

          (store_current_scene, ":cur_scene"),
          (modify_visitors_at_site, ":cur_scene"),
          (add_visitors_to_current_scene, reg0, ":selected_troop", 1, ":selected_team", -1),#don't assign group at spawn
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_begin),
            (eq, ":selected_team", 0),
            (val_sub, "$coop_num_bots_team_1", 1),
          (else_try),
            (eq, ":selected_team", 1),
            (val_sub, "$coop_num_bots_team_2", 1),
          (try_end),
        (try_end),    
        (try_end),    
        ]),
 


#multiplayer_server_manage_bots
      (3, 0, 0, [], 
       [
        (multiplayer_is_server),
        (store_mission_timer_a, ":seconds_past_since_round_started"),

        #this can be used to make the bigger team charge first
        # (try_begin),#pick attacker to charge
          # (gt, "$coop_alive_team1", "$coop_alive_team2"), 
          # (assign, ":team_charge", 0),
        # (else_try),
          # (assign, ":team_charge", 1),
        # (try_end),

          # (assign, ":hold_time", "$coop_alive_team1"),
          # (val_max, ":hold_time", "$coop_alive_team2"), 
          # (val_div, ":hold_time", 5), #larger team / 5
          (store_add, ":hold_time", "$coop_alive_team1", "$coop_alive_team2"),
          (val_div, ":hold_time", 2), 
          (val_clamp, ":hold_time", 10, 41),

        (try_for_agents, ":cur_agent"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (call_script, "script_coop_change_leader_of_bot", ":cur_agent"),

          # (agent_get_group, ":agent_group", ":cur_agent"),
          # (agent_get_team, ":agent_team", ":cur_agent"),
          (try_begin),
            (this_or_next|eq, "$coop_battle_type", coop_battle_type_village_player_attack), #no delay for village raid
            (eq, "$coop_battle_type", coop_battle_type_village_player_defend), #village battle
            (agent_clear_scripted_mode, ":cur_agent"),
          (else_try),
            (gt, ":seconds_past_since_round_started", ":hold_time"), #everyone hold
            # (this_or_next|ge, ":agent_group", 0),#player commanded
            # (this_or_next|eq, ":agent_team", ":team_charge"), #start attacker charge
            # (gt, ":seconds_past_since_round_started", 40), #all charge
            (agent_clear_scripted_mode, ":cur_agent"),
          (try_end),
        (try_end),

          (get_max_players, ":num_players"),
          (try_for_range, ":player_no", 1, ":num_players"), #0 is server so starting from 1
            (player_is_active, ":player_no"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 1,  "$coop_num_bots_team_1"),
            (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 2,  "$coop_num_bots_team_2"),
          (try_end),

        ]),


      (ti_on_agent_spawn, 0, 0, [],#called by client also
       [
        (store_trigger_param_1, ":agent_no"),
        (try_begin),
          (eq, "$coop_battle_started", 0),
          (assign, "$coop_battle_started", 1),
        (try_end),
          (try_begin), #add alive team counts for server and client
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (try_begin),
              (eq, ":agent_team", 0),
              (val_add, "$coop_alive_team1", 1), #Patched to an extent here are the teams that can be probably be used for group IDS!
            (else_try),
              (eq, ":agent_team", 1),
              (val_add, "$coop_alive_team2", 1),
            (try_end),
          (try_end),


        (try_begin),
          (multiplayer_is_server),
          (try_begin),
            (eq, "$coop_battle_spawn_formation", 1),
            (eq, "$coop_battle_type", coop_battle_type_field_battle), #not for village raids
            (call_script, "script_coop_spawn_formation", ":agent_no"), #move agent to spawn position
          (try_end),


#NEW
          (try_begin),
            (eq, "$coop_battle_type", coop_battle_type_bandit_lair),
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (eq, ":agent_team", 1),
            (entry_point_get_position, pos30, 0),
            (agent_set_position, ":agent_no", pos30),
          (try_end),

          #check this script for changes, currently only sets multiplayer_ready_for_spawning_agent
          # (call_script, "script_multiplayer_server_on_agent_spawn_common", ":agent_no"),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
          (agent_set_slot, ":agent_no", slot_agent_coop_spawn_party, "$coop_agent_party"), #store party of agent

          (call_script, "script_coop_equip_player_agent", ":agent_no"), #ITEM BUG WORKAROUND
        (try_end),

        (try_begin),
          (agent_is_human, ":agent_no"),
          (agent_get_troop_id,":script_param_1", ":agent_no"),

      #common_battle_init_banner 
        (call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":agent_no", ":script_param_1"),

        #when client's chosen troop spawns, request control of it
          (eq, ":script_param_1", "$coop_my_troop_no"),

          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_set_team_no, ":my_player_no", "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_team_no, "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_troop_id, "$coop_my_troop_no"),
        (try_end),

         ]),


      (ti_on_agent_killed_or_wounded, 0, 0, [],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (store_trigger_param_2, ":killer_agent_no"),
#new
         (call_script, "script_coop_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
	       (call_script, "script_multiplayer_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
     

         (assign, ":number_of_alive_1", 0),
         (assign, ":number_of_alive_2", 0),
          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team, ":cur_agent_team", ":cur_agent"),
            (try_begin),
              (eq, ":cur_agent_team", 0),
              (val_add, ":number_of_alive_1", 1),
            (else_try),
              (eq, ":cur_agent_team", 1),
              (val_add, ":number_of_alive_2", 1),
            (try_end),
          (try_end),
         (assign, "$coop_alive_team1", ":number_of_alive_1"),
         (assign, "$coop_alive_team2", ":number_of_alive_2"),

        (try_begin), #check round end        
          (this_or_next|eq, ":number_of_alive_1", 0),
          (eq, ":number_of_alive_2", 0),
          (try_begin), #assign my initial team value (only used to set color of multiplayer_message_type_round_result_in_battle_mode)
            (multiplayer_get_my_player, ":my_player_no"),
            (ge, ":my_player_no", 0),
            (player_get_team_no, "$coop_my_team", ":my_player_no"),
            (player_get_team_no, "$my_team_at_start_of_round", ":my_player_no"),
            (player_get_agent_id, ":my_agent_id", ":my_player_no"),
            (ge, ":my_agent_id", 0),
            (agent_get_troop_id, "$coop_my_troop_no", ":my_agent_id"),
          (try_end),     

          (try_begin),
            (eq, "$coop_alive_team1", 0),#if team 1 is dead
            (assign, "$coop_winner_team", 1),
          (else_try),
            (eq, "$coop_alive_team2", 0),#if team 2 is dead
            (assign, "$coop_winner_team", 0),
          (try_end),

          (call_script, "script_show_multiplayer_message", multiplayer_message_type_round_result_in_battle_mode, "$coop_winner_team"), #team 2 is winner 
          (store_mission_timer_a, "$g_round_finish_time"),
          (assign, "$g_round_ended", 1),
        (try_end),


         ]),

      # Dedicated battle server end-of-round handler:
      # 1) save battle results (writes @coop_battle dict and signals DLL via
      #    $coop_battle_started = -1), 2) kick players, 3) restart mission.
      # The save MUST happen here, not in a separate ti_once trigger, because
      # this trigger's start_multiplayer_mission restarts the mission and
      # clears $g_round_ended before any later trigger would run.
      (10, 0, ti_once, [(eq, "$g_round_ended", 1)],
       [
        (try_begin),
          (multiplayer_is_server),
          (multiplayer_is_dedicated_server),

          # Save results first (while $coop_battle_started is still 1).
          # coop_copy_parties_to_file_mp writes dict then sets battle_started
          # to -1 after dict_save, which the DLL poll thread observes as the
          # edge to send PKT_BATTLE_END to the campaign server.
          (try_begin),
            (eq, "$coop_battle_started", 1),
            (call_script, "script_coop_copy_parties_to_file_mp"),
          (try_end),

          (get_max_players, ":num_players"),
          (try_for_range, ":player_no", 1, ":num_players"),
            (player_is_active, ":player_no"),
            (kick_player, ":player_no"),
          (try_end),

          (assign, "$g_round_ended", 0),
          # Do NOT reset $coop_battle_started here -- leave it at -1 so the
          # DLL poll thread has a window to observe the edge. The new
          # mission's ti_before_mission_start trigger will reset it to 0.
          (assign, "$coop_battle_state", coop_battle_state_none),
          (assign, "$coop_scene_loaded", 0),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
          (start_multiplayer_mission, reg0, "scn_random_multi_plain_medium", 1),
          (display_message, "@Battle server reset -- ready for next battle."),
        (try_end),
       ]),


      (ti_tab_pressed, 0, 0, [],
       [
         (try_begin),
           (assign, "$g_multiplayer_stats_chart_opened_manually", 1),
           (start_presentation, "prsnt_coop_stats_chart"),
         (try_end),


         ]),

      (ti_escape_pressed, 0, 0, [],
       [
         (neg|is_presentation_active, "prsnt_coop_escape_menu"),
         (neg|is_presentation_active, "prsnt_coop_stats_chart"),
         (eq, "$g_waiting_for_confirmation_to_terminate", 0),
         (start_presentation, "prsnt_coop_escape_menu"),
         ]),
		 ##BEGIN ADDITIONAL TRIGGERS

#####Camera mode by Rubik Begin Co-Op
 (0, 0, 0, [(eq, "$coop_extended_camera", 1),
 (neg|multiplayer_is_dedicated_server),
 ],
  [
    (multiplayer_get_my_player, ":my_player_no"),
    (player_get_agent_id, ":player_agent", ":my_player_no"),
    (gt, ":player_agent", -1),
    (agent_get_look_position, pos1, ":player_agent"),
    (position_move_z, pos1, "$g_camera_z"),
    (position_move_y, pos1, "$g_camera_y"),
    (agent_get_horse, ":horse_agent", ":player_agent"),
    (try_begin),
      (ge, ":horse_agent", 0),
      (position_move_z, pos1, 80),
    (try_end),
    (mission_cam_set_position, pos1),
    (try_begin),
      (key_is_down, key_left_control),
      (assign, ":move_val", 50),
    (else_try),
      (assign, ":move_val", 10),
    (try_end),
    (try_begin),
      (key_clicked, key_up),
      (mission_cam_set_mode, 1),
      (val_add, "$g_camera_z", ":move_val"),
    (else_try),
      (key_clicked, key_down),
      (mission_cam_set_mode, 1),
      (val_sub, "$g_camera_z", ":move_val"),
    (else_try),
      (key_clicked, key_left),
      (mission_cam_set_mode, 1),
      (val_add, "$g_camera_y", ":move_val"),
    (else_try),
      (key_clicked, key_right),
      (mission_cam_set_mode, 1),
      (val_sub, "$g_camera_y", ":move_val"),
    (try_end),
    (try_begin),
      (this_or_next|game_key_clicked, gk_view_char),
      (this_or_next|game_key_clicked, gk_zoom),
      (game_key_clicked, gk_cam_toggle),
      (mission_cam_set_mode, 0),
    (try_end),
  ]),
  #####Camera mode by Rubik End Co-Op
  
  
  	###Voice-over for Infantry, archers & Cavalry
		
		(0.0, 0.3, 0.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
		(neg|main_hero_fallen),
			(game_key_clicked, 29) #Everyone!
			
		],

		[
		(call_script, "script_identify_battle_voices_all")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 30), #Infantry
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_inf")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 31), #Archers
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_archers")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 32), #Cavalry
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_cav")
		]),
		###Voice-over for Infantry, archers & Cavalry	
  
  
  
		 ###########Torch (Coop Version) by troycall/Envious Arm begin
																	(25.0, 25.0, 120.0, #Repeat checks every 2 minute, delay trigger check by 25 seconds.
																	#(-25.0, 20.0, 0.0, # Start 25 seconds earlier, delay by 20 seconds if pass, restart every 0 seconds.
																	#(-25.0, 0.0, 0.0, #Enabling this forces random chance to be 100%
																	#(ti_on_agent_spawn, 0, 0, #Enabling this forces random chance to be 100%
																	#(20, 0, ti_once, #Proper one, but reinforcements do not get assigned torches.
        [
		(multiplayer_is_server),
          (mission_tpl_are_all_agents_spawned), 
          #(is_currently_night) #Check if currently night time SP only.
		  
		  #Extension time test for Co-Op
		  #(store_time_of_day, ":hour"),
          #(this_or_next|gt, ":cur_hour", 21), #greater then 9 PM
          #(le, ":cur_hour", 5) #lower then 5 AM
		  #(this_or_next|is_between,":hour",21,25),
		  #(is_between,":hour",1,6)
		  #(is_between, ":cur_hour", 21, 24),
		  #END Extension for Co-Op
		  
        ],
        [

		  ####DEFAULT
		   #(try_for_agents, ":agent"),
            #(agent_get_wielded_item, ":item", ":agent", 1),
            #(gt, ":item", -1),
            #(agent_unequip_item, ":agent", ":item"),
            #(agent_equip_item, ":agent", "itm_torch"),
            #(agent_set_wielded_item, ":agent", "itm_torch"),           
          #(try_end),
		  ####END DEFAULT
		  
		  (try_for_agents, ":agent"), #Try for agents...
		  #Extension
		  (agent_is_alive, ":agent"), #For performance reasons
		  #End
		  (agent_is_human, ":agent"), #Performance
          (agent_is_non_player, ":agent"), #Uncommenting this includes player on spawning with torch, may be necessary to uncomment at module_coop_mission_templates.
		  
		 ##########Default Order
		 #######		  (agent_is_human, ":agent"), #Performance
         #######(agent_is_non_player, ":agent"), #Uncommenting this includes player on spawning with torch, may be necessary to uncomment at module_coop_mission_templates.
		 #######
		 ########Extension
		 #######(agent_is_active, ":agent"), #For performance reasons
		 #######(agent_is_alive, ":agent"), #For performance reasons
		 ########End
		  ############
		  
          #BEGIN DEBUG
          #(assign, reg10, ":agent"),
          #(str_clear, s10),
          #(str_store_string, s10, "@New agent: {reg10}"),
          #END DEBUG
         (agent_get_wielded_item, ":rhanditem", ":agent", 0),  #Obtain right hand item
          (agent_get_wielded_item, ":item", ":agent", 1), # Left hand: shield or -1
          #BEGIN DEBUG
          #(assign, reg10, ":item"),
          #(str_store_string, s10, "@{s10}. LH: {reg10}"),
		  #(display_message, "@Main block Phase A finalized"),
          #END DEBUG

          (try_begin),
		  (neg|is_between, ":rhanditem", "itm_club_with_spike_head", "itm_wooden_shield"),
		  (neg|is_between, ":rhanditem", "itm_lance_banner_jer", "itm_cross_end"), #Update item slots
		    (gt, ":item", -1), #Check if the agent wields any item in the left hand, this or next.
            #(neq, ":item", -1),# Check if the agent wields any item in the left hand
            (neq, ":item", "itm_torch"), #If agent is using torch, ignore him.
            #(display_message, "@PASSED neg tests"), #Debug message
			
            (store_random_in_range, ":chance", 1, 101), # Chance of item being assigned
            (try_begin),
			  (le, ":chance", "$torch_chance_coop"), #25% = 25
				#lt           = neg | ge # less than		-- (lt,<value>,<value>),
				#neq          = neg | eq # not equal to		-- (neq,<value>,<value>),
				#le           = neg | gt # less or equal to	-- (le,<value>,<value>),
              (agent_unequip_item, ":agent", ":item"),
			  
              #BEGIN DEBUG
              #(str_store_item_name, s11, ":item"),
              #(str_store_string, s10, "@{s10}. Removed item: {s11}"),
			  #(display_message, "@(agent_unequip_item, :agent, :item PASSED."),
              #END DEBUG

               
                (agent_equip_item, ":agent", "itm_torch"), #Tell agent to equip the item
                 #(display_message, "@(agent_equip_item, :agent, :item PASSED."),
                  (agent_set_wielded_item, ":agent", "itm_torch"), #Required for infantry only, cavarly can work without it.
                  #(display_message, "@(agent_set_wielded_item, :agent, :item PASSED."),
                 
                 
                  #BEGIN DEBUG
                #(else_try),
                  #(str_store_string, s10, "@{s10}. Failed random chance."),
                (try_end),
               
              #(else_try),
                #(str_store_string, s10, "@{s10}. Invalid agent for torch"),
              (try_end),
             
              #(display_message, s10),
			  (try_end),
              #END DEBUG
      ]),
	  
###########Torch (Coop Version) by troycall/Envious Arm end
		 
		 		#Morale

		#		(-25.0, 0.0, 0.0,
		#[],
        #
		#[
		#	(store_trigger_param_1, ":trigger_param_1"),
		#	(call_script, "script_agent_reassign_team", ":trigger_param_1"),
		#	(assign, ":var_2", 5000),
		#	(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
		#	(store_character_level, ":character_level_troop_id_trigger_param_1", ":troop_id_trigger_param_1"),
		#	(val_mul, ":character_level_troop_id_trigger_param_1", 35),
		#	(val_add, ":var_2", ":character_level_troop_id_trigger_param_1"),
		#	(store_random_in_range, ":random_in_range_0_3000", 0, 3000),
		#	(val_add, ":var_2", ":random_in_range_0_3000"),
		#	(agent_get_party_id, ":party_id_trigger_param_1", ":trigger_param_1"),
		#	(ge, ":party_id_trigger_param_1", 0),
		#	(party_get_morale, ":morale_party_id_trigger_param_1", ":party_id_trigger_param_1"),
		#	(store_sub, ":value", ":morale_party_id_trigger_param_1", 70),
		#	(val_mul, ":value", 30),
		#	(val_add, ":var_2", ":value"),
		#	(agent_set_slot, ":trigger_param_1", slot_agent_courage_score, ":var_2")
		#]),
		
#				 		(-25.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#			(call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":trigger_param_1", ":troop_id_trigger_param_1")
#		]),
#						(-26.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(store_trigger_param_2, ":trigger_param_2"),
#			(store_trigger_param_3, ":trigger_param_3"),
#			(try_begin),
#				(ge, ":trigger_param_1", 0),
#				(neg|agent_is_ally, ":trigger_param_1"),
#				(agent_is_human, ":trigger_param_1"),
#				(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#				(party_add_members, "p_total_enemy_casualties", ":troop_id_trigger_param_1", 1),
#				(eq, ":trigger_param_3", 1),
#				(party_wound_members, "p_total_enemy_casualties", ":troop_id_trigger_param_1", 1),
#			(try_end),
#			(call_script, "script_apply_death_effect_on_courage_scores", ":trigger_param_1", ":trigger_param_2")
#		]),
#		#MoraleEnd

		(-28.0, 0.3, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
		],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(store_trigger_param_2, ":trigger_param_2"),
			(store_trigger_param_3, ":trigger_param_3"),
			(assign, ":var_4", reg0),
			(agent_is_human, ":trigger_param_1"),
			(get_player_agent_no, ":player_agent_no"),
#			(try_begin),
#				#(eq, "$tom_weapon_break", 1),
#				(eq, ":trigger_param_1", ":player_agent_no"),
#				(store_random_in_range, ":random_in_range_0_1000", 0, 1000),
#				(eq, ":random_in_range_0_1000", 1),
#				(store_random_in_range, ":random_in_range_4_8", 4, 8),
#				(troop_get_inventory_slot, ":inventory_slot_player_random_in_range_4_8", "trp_player", ":random_in_range_4_8"),
#				(gt, ":inventory_slot_player_random_in_range_4_8", 0),
#				(str_store_item_name, 20, ":inventory_slot_player_random_in_range_4_8"),
#				(troop_get_inventory_slot_modifier, ":inventory_slot_modifier_player_random_in_range_4_8", "trp_player", ":random_in_range_4_8"),
#				(try_begin),
#					(eq, ":inventory_slot_modifier_player_random_in_range_4_8", 6),
#					(display_message, "@Your {s20} is too crapy to fall apart!", 0x00ff0000),
#				(else_try),
#					(troop_add_item, "trp_broken_items", ":inventory_slot_player_random_in_range_4_8", ":inventory_slot_modifier_player_random_in_range_4_8"),
#					(troop_set_inventory_slot_modifier, "trp_player", ":random_in_range_4_8", 6),
#					(display_message, "@Your {s20} cracks!", 0x00ff0000),
#				(try_end),
#			(try_end),
			(try_begin),
				#(eq, "$tom_weapon_break", 1),
				(eq, ":trigger_param_2", ":player_agent_no"),
				(is_between, ":var_4", 1, "itm_cross_end"), #Previously itm_items_end
				(neg|is_between, ":var_4", "itm_light_lance", "itm_wooden_shield"),
				(item_get_type, ":type_var_4", ":var_4"),
				(ge, ":trigger_param_3", 10),
				(neq, ":type_var_4", 10),
				(neq, ":type_var_4", 8),
				(neq, ":type_var_4", 9),
				(neq, ":type_var_4", 5),
				(neq, ":type_var_4", 6),
				(store_random_in_range, ":random_in_range_0_1000", 0, 600),
				(eq, ":random_in_range_0_1000", 1),
				(assign, ":value", -1),
				(try_for_range, ":random_in_range_4_8", 0, 4),
					(troop_get_inventory_slot, ":inventory_slot_player_random_in_range_4_8_2", "trp_player", ":random_in_range_4_8"),
					(eq, ":inventory_slot_player_random_in_range_4_8_2", ":var_4"),
					(assign, ":value", ":random_in_range_4_8"),
				(try_end),
				(gt, ":value", 0),
				(str_store_item_name, 20, ":var_4"),
				(troop_get_inventory_slot_modifier, ":inventory_slot_modifier_player_random_in_range_4_8", "trp_player", ":value"),
				(try_begin),
					(eq, ":inventory_slot_modifier_player_random_in_range_4_8", 6),
					(display_message, "@Your {s20} falls apart!", 0x00ff0000),
					(agent_unequip_item, ":player_agent_no", ":var_4"),
					(troop_remove_item, "trp_player", ":var_4"),
					(troop_remove_item, "trp_broken_items", ":var_4"),
				(else_try),
					(troop_add_item, "trp_broken_items", ":var_4", ":inventory_slot_modifier_player_random_in_range_4_8"),
					(troop_set_inventory_slot_modifier, "trp_player", ":value", 6),
					(display_message, "@Your {s20} cracks!", 0x00ff0000),
				(try_end),
			(try_end),
			(agent_get_horse, ":horse_trigger_param_2", ":trigger_param_2"),
			(try_begin),
				#(eq, "$tom_lance_breaking", 1),
				(gt, ":horse_trigger_param_2", 0),
				(this_or_next|is_between, ":var_4", "itm_light_lance", "itm_spear_a"), #Updated item slots
				(is_between, ":var_4", "itm_lance_banner_jer", "itm_pike_banner_teu"), #Updated item slots
				(ge, ":trigger_param_3", 50),
				(store_random_in_range, ":random_in_range_0_100", 0, 100),
				(gt, ":random_in_range_0_100", 20),
				(try_begin),
					(eq, ":trigger_param_2", ":player_agent_no"),
					(display_message, "@You broke your lance!", 0x00ff0000),
				(try_end),
				########Add effects on weapon break *Lances*
        (agent_get_position, pos1, ":trigger_param_2"),
		(agent_play_sound, ":trigger_param_1", "snd_shield_broken"),
		(particle_system_burst, "psys_lanse", pos1, 10),
        (particle_system_burst, "psys_lanse_straw", pos1, 30),
                ####Extend to Lanse_Blood
		#(particle_system_burst, "psys_lanse_blood", pos1, 10),
        #(particle_system_burst, "psys_lanse_blood", pos1, 30),
		        ########End Effects
				(agent_unequip_item, ":trigger_param_2", ":var_4"),
			(else_try),
				(this_or_next|is_between, ":var_4", "itm_bamboo_spear", "itm_wooden_shield"), #Updated item slots
				(is_between, ":var_4", "itm_pike_banner_teu", "itm_items_end"), #Updated item slots
				(le, ":horse_trigger_param_2", 0),
				(ge, ":trigger_param_3", 8),
				(store_random_in_range, ":random_in_range_0_100", 0, 100),
				(ge, ":random_in_range_0_100", 90),
				(try_begin),
					(eq, ":trigger_param_2", ":player_agent_no"),
					(display_message, "@You broke your spear!", 0x00ff0000),
				(try_end),
				########Add effects on weapon break *Spears*
        (agent_get_position, pos1, ":trigger_param_2"),
		(agent_play_sound, ":trigger_param_1", "snd_shield_broken"),
		(store_random_in_range, ":psys_to_use", "psys_lanse", "psys_lanse_blood"),
		(particle_system_burst, ":psys_to_use", pos1, 7), #Default = 10 (Higher = Bigger Particles)
        (particle_system_burst, ":psys_to_use", pos1, 21), #Default = 30 (Higher = Bigger Particles)
                ####Extend to Lanse_Blood
		#(particle_system_burst, "psys_lanse_blood", pos1, 10),
        #(particle_system_burst, "psys_lanse_blood", pos1, 30),
		        ########End Effects
				(agent_unequip_item, ":trigger_param_2", ":var_4"),
			(try_end),
			###Envfix weapon breaking patch start here
		]),
		
		#####Patched to an extent LONG BEGIN (Spearwall)
		(0.2, 0.0, ti_once,
		[(multiplayer_is_server),],

		[
			(assign, "$spear_in_position", 0),
			(try_for_agents, ":var_1"),
			#Identify player troop and don't change his items.
			#Identify player troop end
				(agent_set_slot, ":var_1", slot_agent_bought_horse, 0),
				(agent_set_slot, ":var_1", 27, 0),
				(agent_set_slot, ":var_1", 28, 0),
				(agent_set_slot, ":var_1", 29, 0),
				(agent_set_slot, ":var_1", 30, 0),
			(try_end)
		]),
		
		
##		#Testing Trigger begin
#		(1.0, 0.0, ti_once,
#
#
#
#
#				#
#
#		[
#		(multiplayer_is_server),
#		],
#
#		[
#		(store_current_scene, ":cur_scene_co"), #Store current Scene
#		(is_between, ":cur_scene_co", "scn_scene_sea", "scn_random_scene_plain_forest"), #If swamp *Plain Forest*
#		(try_for_range, ":entry_pts", 0, 33),
#		(mission_tpl_entry_set_override_flags, "mt_coop_battle", ":entry_pts", af_override_horse), #NEW
#
#		#(mission_tpl_entry_set_override_flags, "mt_coop_battle", 1, af_override_horse), #NEW
#		#(mission_tpl_entry_set_override_flags, "mt_coop_battle", 4, af_override_horse), #NEW
#		(try_end),
#		]),
#		#NEW
#		#Testing trigger end	
				
				
				#(ti_after_mission_start, 0.0, ti_once,
				(ti_after_mission_start, 0.0, ti_once,
		[
		(multiplayer_is_server),
		],

		[
		#(try_for_range, ":entry_ptsz", 0, 33),
		#(neg|mission_tpl_entry_set_override_flags, "mt_coop_battle", ":entry_ptsz", af_override_horse), #NEW
		#(try_end),
		#(multiplayer_is_server),
		#(display_message, "@TEST COOP SCENE TRIGGER"),
		#(store_script_param, ":mt_coop_battle"), #Probably not needed.
		(store_current_scene, ":cur_scene_coop"), #Store current Scene
		#  #BEGIN DEBUG
        #  (assign, reg10, ":cur_scene_coop"),
        #  (str_clear, s10),
        #  (str_store_string, s10, "@Current Scene: {reg10}"),
        #  
		#  #1257_combat_mountain_9 = 504
		#  #1257_combat_mountain_6 = 516
		#  (display_message, s10),
		##	#END DEBUG 
		  
(try_begin), #Desert rocky, and desert mountain 1 (similiar to rocky desert)
(this_or_next|eq, ":cur_scene_coop", "scn_1257_combat_rocky_desert_0"), #if rocky desert
(eq, ":cur_scene_coop", "scn_1257_combat_mountain_desert_1"), #if rocky desert
(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 80),
						(assign, "$coop_generate_desert", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 30),
						(assign, "$coop_generate_desertv2", 1),
						(try_end),
						
(else_try),  #Mountain 0 (The long path)
(eq, ":cur_scene_coop", "scn_1257_combat_mountain_desert_0"), ##if 1257_combat_snow_0 to scn_manor *one less*
(assign, "$coop_generate_desert", 1),
						
(else_try),  #Desert niles
(is_between, ":cur_scene_coop", "scn_sitd_battle_nile_1", "scn_random_scene_steppe"), ##if 1257_combat_snow_0 to scn_manor *one less*
(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 80),
						(assign, "$coop_generate_desertv2", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 0),
						(assign, "$coop_generate_desertv3", 1),
						(try_end),

						
(else_try), #Steppe
(this_or_next|is_between, ":cur_scene_coop", "scn_1257_combat_iberian_0", "scn_1257_combat_iberian_hillside_0"), ##if steppes
(eq, ":cur_scene_coop", "scn_random_scene_steppe"), #if random_scene_steppe
(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 80), #Lower chance of big forest
						(assign, "$coop_generate_iberian2", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 0), #Higher chance of small trees
						(assign, "$coop_generate_iberian", 1),
						(try_end),
	
(else_try), #Iberian Continnatuion (Steppe)
(is_between, ":cur_scene_coop", "scn_1257_combat_iberian_hillside_0", "scn_random_scene_plain"), #If swamp *Plain Forest*

	(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 20), #Bigger chance of big forest
						(assign, "$coop_generate_iberian2", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 0), #Lower chance of small forest
						(assign, "$coop_generate_iberian", 1),
						(try_end),
						
(else_try), #Swamps
(is_between, ":cur_scene_coop", "scn_1257_combat_swamp_0", "scn_1257_combat_rocky_desert_0"), #If swamp *Plain Forest*
(assign, "$coop_generate_swamp", 1),

(else_try), #Steppe_forest
(is_between, ":cur_scene_coop", "scn_1257_combat_euro_0", "scn_1257_combat_euro_hillside_0"), ##if 1257_combat_snow_0 to scn_manor *one less*
(assign, "$coop_generate_euro_hillside", 1),

#Additional this dosen't exist in SP.
	(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 50), #Bigger chance of big forest
						(assign, "$coop_generate_swamp", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 0), #Lower chance of small forest
						(assign, "$coop_generate_iberian2", 1),
						(try_end),
						#Additional this dosen't exist in SP.

(else_try), #Steppe_forest
(eq, ":cur_scene_coop", "scn_random_scene_plain"), ##if 1257_combat_snow_0 to scn_manor *one less*
(assign, "$coop_generate_swamp", 1),

###Disabled disable horses use EQ and try_begin and try_end probably with a presentation option.
#(else_try), #Sea
#(is_between, ":cur_scene_coop", "scn_scene_sea", "scn_random_scene_plain_forest"), #If swamp *Plain Forest*
#(mission_tpl_entry_set_override_flags, "mt_coop_battle", 0, af_override_horse), #NEW
###
(else_try), #Steppe_forest
(is_between, ":cur_scene_coop", "scn_1257_combat_euro_hillside_0", "scn_1257_combat_mountain_0"), ##if 1257_combat_snow_0 to scn_manor *one less*
(assign, "$coop_generate_euro_hillside", 1),

#Additional this dosen't exist in SP
	(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 70), #Bigger chance of big forest
						(assign, "$coop_generate_swamp", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 50), #Lower chance of small forest
						(assign, "$coop_generate_iberian2", 1),
						(try_end),
#Additional this dosen't exist in SP.

(else_try), #Steppe_forest
(is_between, ":cur_scene_coop", "scn_1257_combat_mountain_7", "scn_random_scene_snow"), ##if 1257_combat_snow_0 to scn_manor *one less*
	(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(try_begin),
						(ge, ":random_in_range_0_101", 20),
						(assign, "$coop_generate_swamp", 1),
					(else_try),
						(ge, ":random_in_range_0_101", 0),
						(assign, "$coop_generate_iberian2", 1),
						(try_end),

(else_try), #Snow & Snow Forest
#(this_or_next|is_between, ":cur_scene_coop", 507, 517), ##if 1257_combat_snow_0 to scn_manor *one less*
#(eq, ":cur_scene_coop", 505), #if random_scene_snow
(this_or_next|is_between, ":cur_scene_coop", "scn_1257_combat_snow_0", "scn_manor"), ##if 1257_combat_snow_0 to scn_manor *one less*
(eq, ":cur_scene_coop", "scn_random_scene_snow"), #if random_scene_snow
(assign, "$coop_generate_snow", 1), #Assign snow, in this case the heavy snow can be randomly generated.
(try_end),
		]),
		#NEW
	
	#####MUSICBOX BEGIN
	
##Patch
	(ti_before_mission_start, 0, ti_once, #Fire every 680 seconds, todo: track each individual track time and start next track as soon as first one is over.
	[
	(neg|multiplayer_is_dedicated_server), #Dedicateds dont play sound
	#(multiplayer_is_server), #Only server should play the sound (for a test, you should uncomment this, and comment the line above to see if track executes in server-side, see if it executes in cleint-side.)
	],
		
  [
  (display_message, "@You can enable music by holding O, and disable music by holding P."),
  (music_set_situation, mtf_sit_fight),
  (assign, "$music_timer", 0), #Patch
   #Field related extend to sieges
  #(store_random_in_range, ":randomizer", 0, 1),
  #(try_begin),
  #(eq, ":randomizer", 0),
  #####Always randomize tracks in co-op.
  (store_random_in_range, ":euro_randomizernext", 1, 12),
  (store_random_in_range, ":medi_randomizer", 1, 8),
  (store_random_in_range, ":arab_randomizer", 1, 9),
  (assign, "$track_count_field", ":euro_randomizernext"),
  (assign, "$track_count_field_medi", ":medi_randomizer"),
  (assign, "$track_count_field_arabs", ":arab_randomizer"),
  #(try_end),
  #Field related extend to sieges
  ##(stop_all_sounds, 1), #Simple patch for players who connect to a new server, stop the playing sound.
  ]),
  
  
  	(0, 0, 3, [ #680 #(ti_after_mission_start, 0, 680, [ #680
	(neg|multiplayer_is_dedicated_server),
	(try_begin),
	(this_or_next|key_is_down, key_o),
	(key_clicked, key_o),
	(eq, "$disallow_music", 1),# Resetting value when track ends.
	(assign, "$disallow_music", 0),# Resetting value when track ends.
	(assign, "$music_timer", 0),# Resetting value when track ends.
	(display_message, "@Music enabled!", 0x006495ed),
	(music_set_situation, mtf_sit_fight), #Field
	(else_try),
	(this_or_next|key_is_down, key_p),
	(key_clicked, key_p),
	(eq, "$disallow_music", 0),# Resetting value when track ends.
	(assign, "$disallow_music", 1),# Resetting value when track ends.
	(play_track, "track_reset_silence", 2),
	(display_message, "@Music disabled!", 0x00ff0000),
	(music_set_situation, mtf_sit_tavern), #Field
	(try_end),
	(eq, "$disallow_music", 0),# Resetting value when track ends.
	],
		
  [
		  #(display_message, "@Executing music code"),
		  (store_mission_timer_b, ":time_msec"),
		  #Debug
		  #(assign, reg10, ":time_msec"),
          #(str_clear, s10),
          #(str_store_string, s10, "@Timer: {reg10}"),
		  # (display_message, s10), #Debug message
		   #Debug
			#if next action time is lower than current time, play the sound
			(ge, ":time_msec", "$music_timer"),
			(reset_mission_timer_b), #Resetting mission timer, too.
			(assign, "$music_timer", 0),# Resetting value when track ends.
		
  #Euro only
     (try_begin),
      (ge, "$track_count_field", 11),
      (assign, "$track_count_field", 1),
    (else_try),
      (val_add, "$track_count_field", 1),
	  (ge, "$track_count_field", 11),
	  (assign, "$track_count_field", 1),
    (try_end),
  #Euro only
  
  #Mediterrain only
  
       (try_begin),
      (ge, "$track_count_field_medi", 8),
      (assign, "$track_count_field_medi", 1),
    (else_try),
      (val_add, "$track_count_field_medi", 1),
	  (ge, "$track_count_field_medi", 8),
	  (assign, "$track_count_field_medi", 1),
    (try_end),
  #Mediterrain only
  
  
  #Arabs only

       (try_begin),
      (ge, "$track_count_field_arabs", 8),
      (assign, "$track_count_field_arabs", 1),
    (else_try),
      (val_add, "$track_count_field_arabs", 1),
	  (ge, "$track_count_field_arabs", 8),
	  (assign, "$track_count_field_arabs", 1),
    (try_end),
	#Arabs only
  
  #Pause between music length in seconds
  #(val_add, "$music_timer", 2),# 5 seconds added
  #Pause between music length in seconds
  
  
	(store_current_scene, ":cur_scene_coop_music"),
	(try_begin),
	(is_between, ":cur_scene_coop_music", "scn_random_scene_steppe", "scn_random_scene_plain"), ##Steppe
	#Begin mediterrain music 5 tracks total
	(try_begin),
	(eq, "$track_count_field_medi", 1), #
	(play_track, "track_medib1", 2),
	(val_add, "$music_timer", 206),# 1 second added
	(else_try),
	
	(eq, "$track_count_field_medi", 2), #
	(play_track, "track_medib3", 2),
	(val_add, "$music_timer", 209),#
	(else_try),
	
	(eq, "$track_count_field_medi", 3), #
	(play_track, "track_medib4", 2),
	(val_add, "$music_timer", 237),#
	(else_try),

	(eq, "$track_count_field_medi", 4), #
	(play_track, "track_medib5", 2),
	(val_add, "$music_timer", 229),#
	(else_try),
	(eq, "$track_count_field_medi", 5), #
	(play_track, "track_medib6", 2),
	(val_add, "$music_timer", 127),#
	(else_try),
	(eq, "$track_count_field_medi", 6), #
	(play_track, "track_medib7", 2),
	(val_add, "$music_timer", 161),#
	
	(else_try),
	(eq, "$track_count_field_medi", 7), #
	(play_track, "track_medib8", 2),
	(val_add, "$music_timer", 250),#
	(try_end),
	(else_try),
	(is_between, ":cur_scene_coop_music", "scn_random_scene_plain", "scn_manor"),  ##Euro
	#Begin Euro Music
	(try_begin),
	(eq, "$track_count_field", 1), #
	(play_track, "track_eurob1", 2),
	(val_add, "$music_timer", 319),#
	(else_try),
	(eq, "$track_count_field", 2), #
	(play_track, "track_eurob2", 2),
	(val_add, "$music_timer", 279),#
	(else_try),
	
	(eq, "$track_count_field", 3), #
	(play_track, "track_eurob3", 2),
	(val_add, "$music_timer", 248),#
	(else_try),
	
	(eq, "$track_count_field", 4), #
	(play_track, "track_eurob4", 2),
	(val_add, "$music_timer", 332),#
	(else_try),
	
	(eq, "$track_count_field", 5), #
	(play_track, "track_eurob5", 2),
	(val_add, "$music_timer", 93),#
		(else_try),
	
	(eq, "$track_count_field", 6), #
	(play_track, "track_eurob6", 2),
	(val_add, "$music_timer", 76),#
		(else_try),
	
	(eq, "$track_count_field", 7), #
	(play_track, "track_eurob7", 2),
	(val_add, "$music_timer", 80),#
		(else_try),
	
	(eq, "$track_count_field", 8), #
	(play_track, "track_eurob8", 2),
	(val_add, "$music_timer", 58),#
		(else_try),
	
	(eq, "$track_count_field", 9), #
	(play_track, "track_eurob9", 2),
	(val_add, "$music_timer", 58),#
		(else_try),
	
#	(eq, "$track_count_field", 10), #
#	(play_track, "track_eurob10"),
#	(val_add, "$music_timer", 123),#
#		(else_try),
	
	(eq, "$track_count_field", 10), #
	(play_track, "track_eurob11", 2),
	(val_add, "$music_timer", 335),#
	(try_end),
	
	
	
	(else_try),
	(is_between, ":cur_scene_coop_music", "scn_random_scene_plain", "scn_manor"),  ##Euro
	#Begin Euro Music
	(try_begin),
	(eq, "$track_count_field", 1), #
	(play_track, "track_eurob1", 2),
	(val_add, "$music_timer", 319),#
	(else_try),
	(eq, "$track_count_field", 2), #
	(play_track, "track_eurob2", 2),
	(val_add, "$music_timer", 279),#
	(else_try),
	
	(eq, "$track_count_field", 3), #
	(play_track, "track_eurob3", 2),
	(val_add, "$music_timer", 248),#
	(else_try),
	
	(eq, "$track_count_field", 4), #
	(play_track, "track_eurob4", 2),
	(val_add, "$music_timer", 332),#
	(else_try),
	
	(eq, "$track_count_field", 5), #
	(play_track, "track_eurob5", 2),
	(val_add, "$music_timer", 93),#
		(else_try),
	
	(eq, "$track_count_field", 6), #
	(play_track, "track_eurob6", 2),
	(val_add, "$music_timer", 76),#
		(else_try),
	
	(eq, "$track_count_field", 7), #
	(play_track, "track_eurob7", 2),
	(val_add, "$music_timer", 80),#
		(else_try),
	
	(eq, "$track_count_field", 8), #
	(play_track, "track_eurob8", 2),
	(val_add, "$music_timer", 58),#
		(else_try),
	
	(eq, "$track_count_field", 9), #
	(play_track, "track_eurob9", 2),
	(val_add, "$music_timer", 58),#
		(else_try),
	
#	(eq, "$track_count_field", 10), #
#	(play_track, "track_eurob10"),
#	(val_add, "$music_timer", 123),#
#		(else_try),
	
	(eq, "$track_count_field", 10), #
	(play_track, "track_eurob11", 2),
	(val_add, "$music_timer", 335),#
	(try_end),
	
	(else_try),
	(is_between, ":cur_scene_coop_music", "scn_1257_combat_rocky_desert_0", "scn_random_scene_steppe"), ##Desert
	#Begin arab music
	(try_begin),
	(eq, "$track_count_field_arabs", 1), #
	(play_track, "track_arabb1", 2),
	(val_add, "$music_timer", 262),#
	(else_try),
	(eq, "$track_count_field_arabs", 2), #
	(play_track, "track_arabb2", 2),
	(val_add, "$music_timer", 291),#
	#(else_try),
	#(eq, "$track_count_field_arabs", 3), #
	#(play_track, "track_arabb3"),
	(else_try),
	(eq, "$track_count_field_arabs", 3), #
	(play_track, "track_arabb4", 2),
	(val_add, "$music_timer", 104),#
	(else_try),
	
	(eq, "$track_count_field_arabs", 4), #
	(play_track, "track_arabb5", 2),
	(val_add, "$music_timer", 76),#
		(else_try),
	
	(eq, "$track_count_field_arabs", 5), #
	(play_track, "track_arabb6", 2),
	(val_add, "$music_timer", 218),#
	
			(else_try),
	(eq, "$track_count_field_arabs", 6), #
	(play_track, "track_arabb8", 2),
	(val_add, "$music_timer", 209),#
			(else_try),
	(eq, "$track_count_field_arabs", 7), #
	(play_track, "track_arabb9", 2),
	(val_add, "$music_timer", 103),#
	#	(else_try),
	#
	#(eq, "$track_count_field_arabs", 7), #
	#(play_track, "track_arabb7"),
	(try_end),
	(try_end),
	
  ]),
  
##Patch

		#####MUSICBOX END
#		(0.5, 0.0, 0.0,
#		[
#			(eq, "$setting_use_spearwall", 1) #Disabled due to errors in coop_server_agent_wounded maybe you can figure it out #Patched to an extent
#		],
#
#		[
#			(set_fixed_point_multiplier, 100),
#			(try_for_agents, ":var_1"),
#				(agent_is_alive, ":var_1"),
#				(agent_get_slot, ":var_1_27", ":var_1", 27),
#				(agent_get_slot, ":var_1_28", ":var_1", 28),
#				(agent_get_slot, ":var_1_29", ":var_1", 29),
#				(agent_get_position, 1, ":var_1"),
#				(position_get_x, ":position_x_1", 1),
#				(position_get_y, ":position_y_1", 1),
#				(position_get_z, ":position_z_1", 1),
#				(position_set_x, 2, ":var_1_27"),
#				(position_set_y, 2, ":var_1_28"),
#				(position_set_z, 2, ":var_1_29"),
#				(position_set_x, 1, ":position_x_1"),
#				(position_set_y, 1, ":position_y_1"),
#				(position_set_z, 1, ":position_z_1"),
#				(agent_get_speed, 5, ":var_1"),
#				(call_script, "script_vector_length", 5),
#				(assign, ":var_8", reg0),
#				(agent_set_slot, ":var_1", 27, ":position_x_1"),
#				(agent_set_slot, ":var_1", 28, ":position_y_1"),
#				(agent_set_slot, ":var_1", 29, ":position_z_1"),
#				(agent_set_slot, ":var_1", 30, ":var_8"),
#			(try_end),
#			(set_fixed_point_multiplier, 100)
#		]),
#
#		(0.0, 0.0, 0.0,
#		[
#			(eq, "$spear_in_position", 1),
#			(this_or_next|game_key_clicked, 6),
#			(this_or_next|game_key_clicked, 7),
#			(this_or_next|game_key_clicked, 7),
#			(this_or_next|game_key_clicked, 0),
#			(this_or_next|game_key_clicked, 1),
#			(this_or_next|game_key_clicked, 2),
#			(this_or_next|game_key_clicked, 3),
#			(this_or_next|game_key_clicked, 14),
#			(this_or_next|game_key_clicked, 15),
#			(this_or_next|game_key_clicked, 4),
#			(game_key_clicked, 17)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(display_message, "@Releasing spear.", 0x006495ed),
#			(agent_set_animation, ":player_agent_no", "anim_release_thrust_staff"),
#			(assign, "$spear_in_position", 0)
#		]),
#
#		(0.2, 0.0, 0.0,
#		[
#			(eq, "$setting_use_spearwall", 1) #Not buggy patched to an extent
#		],
#
#		[
#			(try_for_agents, ":var_1"),
#				(agent_get_horse, ":horse_var_1", ":var_1"),
#				(le, ":horse_var_1", 0),
#				(agent_get_slot, ":var_1_bought_horse", ":var_1", slot_agent_bought_horse),
#				(lt, ":var_1_bought_horse", 10),
#				(val_add, ":var_1_bought_horse", 2),
#				(agent_set_slot, ":var_1", slot_agent_bought_horse, ":var_1_bought_horse"),
#			(try_end)
#		]),
#
#		(3.0, 0.0, 0.0,
#		[
#			(eq, "$spear_in_position", 1)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(agent_set_animation, ":player_agent_no", "anim_spearwall_hold")
#		]),
#
#		#Crouching works properly but has errors in the player faction side, however no errors in the other side, in MP please test to see if errors from other players produce it to you.
#		(0.1, 0.0, 0.0,
#		[
#			(eq, "$setting_use_spearwall", 1) # Patched to an extent (Disabled) if you can figure out having 2 group id's that'll make it work right.
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_get_team, ":team_player_agent_no", ":player_agent_no"),
#			(try_for_agents, ":var_3"),
#				(agent_is_alive, ":var_3"),
#				(neq, ":var_3", ":player_agent_no"),
#				(agent_is_human, ":var_3"),
#				(agent_get_horse, ":horse_var_3", ":var_3"),
#				(le, ":horse_var_3", 0),
#				(agent_get_slot, ":var_3_bought_horse", ":var_3", slot_agent_bought_horse),
#				(ge, ":var_3_bought_horse", 10),
#				(agent_get_simple_behavior, ":simple_behavior_var_3", ":var_3"),
#				(agent_get_team, ":team_var_3", ":var_3"),
#				(agent_get_class, ":class_var_3", ":var_3"),
#				(team_get_movement_order, ":movement_order_team_var_3_class_var_3", ":team_var_3", ":class_var_3"),
#				(assign, ":value", 0),
#				(try_begin),
#					(neq, ":team_var_3", ":team_player_agent_no"),
#					(this_or_next|eq, ":simple_behavior_var_3", 0),
#					(this_or_next|eq, ":simple_behavior_var_3", 9),
#					(eq, ":simple_behavior_var_3", 1),
#					(assign, ":value", 1),
#				(else_try),
#					(this_or_next|eq, ":movement_order_team_var_3_class_var_3", 0),
#					(eq, ":movement_order_team_var_3_class_var_3", 11),
#					(this_or_next|eq, ":simple_behavior_var_3", 0),
#					(this_or_next|eq, ":simple_behavior_var_3", 9),
#					(this_or_next|eq, ":simple_behavior_var_3", 4),
#					(eq, ":simple_behavior_var_3", 1),
#					(assign, ":value", 1),
#				(try_end),
#				(eq, ":value", 1),
#				(agent_get_troop_id, ":troop_id_var_3", ":var_3"),
#				(store_proficiency_level, ":proficiency_level_troop_id_var_3_2", ":troop_id_var_3", 2),
#				(store_character_level, ":character_level_troop_id_var_3", ":troop_id_var_3"),
#				(ge, ":character_level_troop_id_var_3", 12),
#				(ge, ":proficiency_level_troop_id_var_3_2", 120),
#				(neg|troop_is_mounted, ":troop_id_var_3"),
#				(agent_slot_eq, ":var_3", slot_agent_is_running_away, 0),
#				(assign, ":value", 0),
#				(agent_get_wielded_item, ":wielded_item_var_3_0", ":var_3", 0),
#				(agent_get_wielded_item, ":wielded_item_var_3_1", ":var_3", 1),
#				(assign, ":value_2", 145),
#				(try_for_range, ":item", "itm_bamboo_spear", "itm_wooden_shield"),
#					(this_or_next|eq, ":wielded_item_var_3_0", ":item"),
#					(eq, ":wielded_item_var_3_1", ":item"),
#					(assign, ":value", 1),
#					(try_begin),
#						(eq, ":item", "itm_bamboo_spear"),
#						(assign, ":value_2", 200),
#					(else_try),
#						(eq, ":item", "itm_spear_a"),
#						(assign, ":value_2", 156),
#					(else_try),
#						(eq, ":item", "itm_spear_b"),
#						(assign, ":value_2", 155),
#					(else_try),
#						(eq, ":item", "itm_spear_c"),
#						(assign, ":value_2", 135),
#					(else_try),
#						(eq, ":item", "itm_spear_d"),
#						(assign, ":value_2", 143),
#					(else_try),
#						(eq, ":item", "itm_spear_e"),
#						(assign, ":value_2", 142),
#					(else_try),
#						(eq, ":item", "itm_spear_f"),
#						(assign, ":value_2", 146),
#					(else_try),
#						(eq, ":item", "itm_spear_g"),
#						(assign, ":value_2", 142),
#					(else_try),
#						(eq, ":item", "itm_spear_h"),
#						(assign, ":value_2", 145),
#					(else_try),
#						(eq, ":item", "itm_spear_i"),
#						(assign, ":value_2", 141),
#					(else_try),
#						(eq, ":item", "itm_spear_j"),
#						(assign, ":value_2", 170),
#					(else_try),
#						(eq, ":item", "itm_spear_k"),
#						(assign, ":value_2", 160),
#					(else_try),
#						(eq, ":item", "itm_spear_l"),
#						(assign, ":value_2", 170),
#					(else_try),
#						(eq, ":item", "itm_spear_m"),
#						(assign, ":value_2", 160),
#					(else_try),
#						(eq, ":item", "itm_spear_n"),
#						(assign, ":value_2", 175),
#					(else_try),
#						(eq, ":item", "itm_spear_o"),
#						(assign, ":value_2", 150),
#					(else_try),
#						(eq, ":item", "itm_spear_p"),
#						(assign, ":value_2", 160),
#					(try_end),
#				(try_end),
#				(eq, ":value", 1),
#				(assign, ":value_3", -1),
#				(agent_get_position, 1, ":var_3"),
#				(try_for_agents, ":var_19"),
#					(agent_is_alive, ":var_19"),
#					(neg|agent_is_human, ":var_19"),
#					(agent_get_rider, ":rider_var_19", ":var_19"),
#					(ge, ":rider_var_19", 0),
#					(agent_get_team, ":team_rider_var_19", ":rider_var_19"),
#					(teams_are_enemies, ":team_var_3", ":team_rider_var_19"),
#					(agent_get_position, 2, ":var_19"),
#					(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
#					(lt, ":distance_between_positions_1_2", ":value_2"),
#					(neg|position_is_behind_position, 2, 1),
#					(agent_get_slot, ":var_19_30", ":var_19", 30),
#					(gt, ":var_19_30", 0),
#					(assign, ":value_3", ":var_19"),
#				(try_end),
#				(gt, ":value_3", -1),
#				(agent_play_sound, ":value_3", "snd_metal_hit_high_armor_high_damage"),
#				(store_agent_hit_points, ":agent_hit_points_value_3_0", ":value_3", 0),
#				(store_agent_hit_points, ":agent_hit_points_value_3_1", ":value_3", 1),
#				(assign, reg22, ":var_19_30"),
#				(val_mul, ":var_19_30", 10),
#				(val_sub, ":agent_hit_points_value_3_0", ":var_19_30"),
#				(val_max, ":agent_hit_points_value_3_0", 0),
#				(agent_set_slot, ":var_3", slot_agent_bought_horse, 0),
#				(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
#				(agent_get_position, 2, ":value_3"),
#				(agent_set_look_target_position, ":var_3", 2),
#				(agent_set_attack_action, ":var_3", 0, 0),
#				(agent_deliver_damage_to_agent, ":var_3", ":value_3"),
#				(agent_deliver_damage_to_agent, ":var_3", ":value_3"),
#				(agent_deliver_damage_to_agent, ":var_3", ":value_3"),
#				(agent_deliver_damage_to_agent, ":var_3", ":value_3"),
#				(agent_get_troop_id, ":troop_id_var_3", ":var_3"),
#				(str_store_troop_name, 21, ":troop_id_var_3"),
#				(agent_get_troop_id, ":troop_id_value_3", ":value_3"),
#				(str_store_troop_name, 20, ":troop_id_value_3"),
#				(store_agent_hit_points, ":agent_hit_points_value_3_0", ":value_3", 1),
#				(val_sub, ":agent_hit_points_value_3_1", ":agent_hit_points_value_3_0"),
#				(assign, reg1, ":agent_hit_points_value_3_1"),
#				(try_begin),
#					(eq, ":value_3", ":horse_player_agent_no"),
#					(display_message, "@Your horse received {reg1} damage from a braced spear!", 0x00ff4040),
#				(try_end),
#			(try_end),
#			(set_fixed_point_multiplier, 100)
#		]),
#
#		(0.1, 0.0, 0.0,
#		[
#			(eq, "$spear_in_position", 1)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(store_agent_hit_points, ":agent_hit_points_player_agent_no_1", ":player_agent_no", 1),
#			(lt, ":agent_hit_points_player_agent_no_1", "$spear_hp"),
#			(display_message, "@The injury causes your grip on the spear to slip!", 0x00ff4040),
#			(agent_set_animation, ":player_agent_no", "anim_release_thrust_staff"),
#			(assign, "$spear_in_position", 0),
#			(set_fixed_point_multiplier, 100)
#		]),
#
#		(0.1, 0.0, 0.0,
#		[
#			(eq, "$spear_in_position", 1)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(agent_get_slot, ":player_agent_no_bought_horse", ":player_agent_no", slot_agent_bought_horse),
#			(ge, ":player_agent_no_bought_horse", 10),
#			(assign, ":value", -1),
#			(agent_get_position, 1, ":player_agent_no"),
#			(try_for_agents, ":var_4"),
#				(agent_is_alive, ":var_4"),
#				(neg|agent_is_human, ":var_4"),
#				(agent_get_rider, ":rider_var_4", ":var_4"),
#				(ge, ":rider_var_4", 0),
#				(neg|agent_is_ally, ":rider_var_4"),
#				(agent_get_position, 2, ":var_4"),
#				(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
#				(lt, ":distance_between_positions_1_2", "$spear_dist"),
#				(neg|position_is_behind_position, 2, 1),
#				(agent_get_slot, ":var_4_30", ":var_4", 30),
#				(ge, ":var_4_30", 120),
#				(assign, ":value", ":var_4"),
#			(try_end),
#			(gt, ":value", -1),
#			(agent_play_sound, ":value", "snd_metal_hit_high_armor_high_damage"),
#			(store_agent_hit_points, ":agent_hit_points_value_0", ":value", 0),
#			(store_agent_hit_points, ":agent_hit_points_value_1", ":value", 1),
#			(val_div, ":var_4_30", 2),
#			(val_sub, ":var_4_30", 15),
#			(val_sub, ":agent_hit_points_value_0", ":var_4_30"),
#			(val_max, ":agent_hit_points_value_0", 0),
#			(agent_set_hit_points, ":value", ":agent_hit_points_value_0", 0),
#			(agent_deliver_damage_to_agent, ":value", ":value"),
#			(agent_set_slot, ":player_agent_no", slot_agent_bought_horse, 0),
#			(store_agent_hit_points, ":agent_hit_points_value_0", ":value", 1),
#			(val_sub, ":agent_hit_points_value_1", ":agent_hit_points_value_0"),
#			(assign, reg1, ":agent_hit_points_value_1"),
#			(display_message, "@Spear-wall dealt {reg1} damage!"),
#			(set_fixed_point_multiplier, 100)
#		]),
#
#		(0.0, 0.0, 2.0,
#		[
#			(key_clicked, 48),
#			(eq, "$setting_use_spearwall", 1) #Disable if error #not buggy patched to an extent
#		],
#
#		[
#			(assign, ":value", 0),
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(agent_get_wielded_item, ":wielded_item_player_agent_no_0", ":player_agent_no", 0),
#			(agent_get_wielded_item, ":wielded_item_player_agent_no_1", ":player_agent_no", 1),
#			(assign, "$spear_dist", 145),
#			(try_for_range, ":item", "itm_bamboo_spear", "itm_wooden_shield"),
#				(this_or_next|eq, ":wielded_item_player_agent_no_0", ":item"),
#				(eq, ":wielded_item_player_agent_no_1", ":item"),
#				(assign, ":value", 1),
#				(try_begin),
#					(eq, ":item", "itm_bamboo_spear"),
#					(assign, "$spear_dist", 200),
#				(else_try),
#					(eq, ":item", "itm_spear_a"),
#					(assign, "$spear_dist", 156),
#				(else_try),
#					(eq, ":item", "itm_spear_b"),
#					(assign, "$spear_dist", 155),
#				(else_try),
#					(eq, ":item", "itm_spear_c"),
#					(assign, "$spear_dist", 135),
#				(else_try),
#					(eq, ":item", "itm_spear_d"),
#					(assign, "$spear_dist", 143),
#				(else_try),
#					(eq, ":item", "itm_spear_e"),
#					(assign, "$spear_dist", 142),
#				(else_try),
#					(eq, ":item", "itm_spear_f"),
#					(assign, "$spear_dist", 146),
#				(else_try),
#					(eq, ":item", "itm_spear_g"),
#					(assign, "$spear_dist", 142),
#				(else_try),
#					(eq, ":item", "itm_spear_h"),
#					(assign, "$spear_dist", 145),
#				(else_try),
#					(eq, ":item", "itm_spear_i"),
#					(assign, "$spear_dist", 141),
#				(else_try),
#					(eq, ":item", "itm_spear_j"),
#					(assign, "$spear_dist", 170),
#				(else_try),
#					(eq, ":item", "itm_spear_k"),
#					(assign, "$spear_dist", 160),
#				(else_try),
#					(eq, ":item", "itm_spear_l"),
#					(assign, "$spear_dist", 170),
#				(else_try),
#					(eq, ":item", "itm_spear_m"),
#					(assign, "$spear_dist", 160),
#				(else_try),
#					(eq, ":item", "itm_spear_n"),
#					(assign, "$spear_dist", 175),
#				(else_try),
#					(eq, ":item", "itm_spear_o"),
#					(assign, "$spear_dist", 150),
#				(else_try),
#					(eq, ":item", "itm_spear_p"),
#					(assign, "$spear_dist", 160),
#				(try_end),
#			(try_end),
#			(eq, ":value", 1),
#			(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
#			(le, ":horse_player_agent_no", 0),
#			(neq, "$spear_in_position", 1),
#			(display_message, "@Bracing spear for charge.", 0x006495ed),
#			(agent_set_animation, ":player_agent_no", "anim_spearwall_hold"),
#			(assign, "$spear_in_position", 1),
#			(store_agent_hit_points, "$spear_hp", ":player_agent_no", 1),
#			(set_fixed_point_multiplier, 100)
#		]),
#		#####Patched to an extent LONG END (Spearwall) begin from TOP
#		(-19.0, 0.0, 0.0,
#		[],
##Possibly unneeded
#		[
#			(team_set_relation, 0, 2, 1),
#			(team_set_relation, 1, 3, 1),
#			(call_script, "script_place_player_banner_near_inventory_bms"),
#			(party_clear, "p_routed_enemies"),
#			(assign, "$g_latest_order_1", 1),
#			(assign, "$g_latest_order_2", 1),
#			(assign, "$g_latest_order_3", 1),
#			(assign, "$g_latest_order_4", 1)
#		]),

#		(0.0, 0.0, ti_once,
#		[],

#		[
#			(assign, "$g_battle_won", 0),
#			(assign, "$defender_reinforcement_stage", 0),
#			(assign, "$attacker_reinforcement_stage", 0),
#			(call_script, "script_place_player_banner_near_inventory"),
#			(call_script, "script_combat_music_set_situation_with_culture"),
#			(assign, "$g_defender_reinforcement_limit", "$g_reinforcement_waves"),
#			(assign, "$dmod_current_agent", -1),
#			(assign, "$dmod_move_camera", -1)
#		]),
#Possibly unneeded end
	#	(30.0, 0.0, 0.0,
	#	[],
    #
	#	[]),

#		(2.0, 0.0, 0.0,
#		[],
#
#		[
#			(call_script, "script_check_friendly_kills")
#			#Nifty little feature where it shows party morale loss per team kill
#		]),
#		#Apply courage effect V2
#				(3.0, 0.0, 0.0,
#		[
#			(call_script, "script_apply_effect_of_other_people_on_courage_scores")
#		],
#
#		[]),
#				(3.0, 0.0, 0.0,
#		[
#			(try_for_agents, ":var_1"),
#				(agent_is_human, ":var_1"),
#				(agent_is_alive, ":var_1"),
#				(store_mission_timer_a, ":mission_timer_a"),
#				(ge, ":mission_timer_a", 3),
#				#(call_script, "script_decide_run_away_or_not_coop", ":var_1", ":mission_timer_a"), #Patched to an extent, if you figure it out, its an issue with group ID too I think so you can probably figure it out
#				#(call_script, "script_decide_run_away_or_not", ":var_1", ":mission_timer_a"), #DEFAULT
#			(try_end)
#		],
#Enabling run away
#		[]),
		#End apply courage effects V2
			(-25.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(call_script, "script_set_matching_sexy_boots", ":trigger_param_1")
		]),
				(0.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$sp_shield_bash_coop", 1),
			(game_key_is_down, 7),
			(game_key_clicked, 6)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			
(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_is_active, ":player_agent_no"),
			(agent_is_alive, ":player_agent_no"),
			(neg|agent_slot_ge, ":player_agent_no", 50, 1),
			(agent_get_wielded_item, ":wielded_item_player_agent_no_1", ":player_agent_no", 1),
			(is_between, ":wielded_item_player_agent_no_1", 1, "itm_cross_end"), #Previously itm_items_end
			(item_get_type, ":type_wielded_item_player_agent_no_1", ":wielded_item_player_agent_no_1"),
			(eq, ":type_wielded_item_player_agent_no_1", 7),
			(agent_get_defend_action, ":defend_action_player_agent_no", ":player_agent_no"),
			(eq, ":defend_action_player_agent_no", 2),
			(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
			(eq, ":horse_player_agent_no", -1),
			(agent_set_slot, ":player_agent_no", 50, 3),
			(agent_set_animation, ":player_agent_no", "anim_shield_bash"),
			(agent_get_troop_id, ":troop_id_player_agent_no", ":player_agent_no"),
			(troop_get_type, ":type_wielded_item_player_agent_no_1", ":troop_id_player_agent_no"),
			(try_begin),
				(eq, ":type_wielded_item_player_agent_no_1", 0),
				(agent_play_sound, ":player_agent_no", "snd_man_yell"),
			(else_try),
				(eq, ":type_wielded_item_player_agent_no_1", 1),
				(agent_play_sound, ":player_agent_no", "snd_woman_yell"),
			(try_end),
			(agent_get_position, 1, ":player_agent_no"),
			(assign, ":value", -1),
			(assign, ":value_2", 150),
			(try_for_agents, ":var_18"),
				(agent_is_alive, ":var_18"),
				(agent_is_human, ":var_18"),
				(neg|agent_is_ally, ":var_18"),
				(agent_get_position, 2, ":var_18"),
				(neg|position_is_behind_position, 2, 1),
				(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
				(le, ":distance_between_positions_1_2", ":value_2"),
				(assign, ":value_2", ":distance_between_positions_1_2"),
				(assign, ":value", ":var_18"),
			(try_end),
			(ge, ":value", 0),
			(agent_play_sound, ":value", "snd_wooden_hit_low_armor_high_damage"),
			(agent_get_defend_action, ":defend_action_player_agent_no", ":value"),
			(try_begin),
				(eq, ":defend_action_player_agent_no", 2),
				(neg|position_is_behind_position, 1, 2),
				(agent_get_wielded_item, ":wielded_item_player_agent_no_1", ":value", 1),
				(is_between, ":wielded_item_player_agent_no_1", 1, "itm_cross_end"), #Previously itm_items_end
				(item_get_type, ":type_wielded_item_player_agent_no_1", ":wielded_item_player_agent_no_1"),
				(eq, ":type_wielded_item_player_agent_no_1", 7),
				(agent_set_animation, ":value", "anim_shield_bash"),
			(else_try),
				(agent_set_animation, ":value", "anim_shield_strike"),
			(try_end)
		]),

		(1.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$sp_shield_bash_coop", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			
(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_is_active, ":player_agent_no"),
			(agent_is_alive, ":player_agent_no"),
			(agent_get_slot, ":player_agent_no_50", ":player_agent_no", 50),
			(val_sub, ":player_agent_no_50", 1),
			(val_max, ":player_agent_no_50", 0),
			(agent_set_slot, ":player_agent_no", 50, ":player_agent_no_50")
		]),

		(0.25, 0.0, 0.0,
		[
		(multiplayer_is_server),
			(eq, "$sp_shield_bash_ai_coop", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			
(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(try_for_agents, ":var_2"),
				(neq, ":var_2", ":player_agent_no"),
				(agent_is_alive, ":var_2"),
				(agent_is_human, ":var_2"),
				(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
				(store_skill_level, ":skill_level_shield_troop_id_var_2", "skl_shield", ":troop_id_var_2"),
				(store_proficiency_level, ":proficiency_level_troop_id_var_2_0", ":troop_id_var_2", 0),
				(ge, ":skill_level_shield_troop_id_var_2", 4),
				(ge, ":proficiency_level_troop_id_var_2_0", 200),
				(agent_get_horse, ":horse_var_2", ":var_2"),
				(le, ":horse_var_2", 0),
				(try_begin),
					(neg|agent_slot_ge, ":var_2", 50, 1),
					(agent_slot_eq, ":var_2", slot_agent_is_running_away, 0),
					(agent_get_wielded_item, ":wielded_item_var_2_1", ":var_2", 1),
					(is_between, ":wielded_item_var_2_1", 1, "itm_cross_end"), #Previously itm_items_end
					(item_get_type, ":type_wielded_item_var_2_1", ":wielded_item_var_2_1"),
					(eq, ":type_wielded_item_var_2_1", 7),
					(agent_get_attack_action, ":attack_action_var_2", ":var_2"),
					(eq, ":attack_action_var_2", 0),
					(agent_get_team, ":team_var_2", ":var_2"),
					(agent_get_position, 1, ":var_2"),
					(assign, ":value", -1),
					(assign, ":value_2", 125),
					(try_for_agents, ":var_13"),
						(agent_is_alive, ":var_13"),
						(agent_is_human, ":var_13"),
						(agent_get_position, 2, ":var_13"),
						(neg|position_is_behind_position, 2, 1),
						(agent_get_team, ":team_var_13", ":var_13"),
						(neq, ":team_var_13", ":team_var_2"),
						(try_begin),
							(eq, ":team_var_2", 0),
							(assign, ":value_3", 2),
						(else_try),
							(eq, ":team_var_2", 2),
							(assign, ":value_3", 0),
						(else_try),
							(eq, ":team_var_2", 1),
							(assign, ":value_3", 3),
						(else_try),
							(eq, ":team_var_2", 3),
							(assign, ":value_3", 1),
						(try_end),
						(neq, ":team_var_13", ":value_3"),
						(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
						(le, ":distance_between_positions_1_2", ":value_2"),
						(assign, ":value_2", ":distance_between_positions_1_2"),
						(assign, ":value", ":var_13"),
					(try_end),
					(ge, ":value", 0),
					(agent_get_horse, ":horse_var_2", ":value"),
					(eq, ":horse_var_2", -1),
					(store_random_in_range, ":random_in_range_15_26", 15, 26),
					(agent_set_slot, ":var_2", 50, ":random_in_range_15_26"),
					(agent_set_animation, ":var_2", "anim_shield_bash"),
					(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
					(troop_get_type, ":type_wielded_item_var_2_1", ":troop_id_var_2"),
					(try_begin),
						(eq, ":type_wielded_item_var_2_1", 0),
						(agent_play_sound, ":var_2", "snd_man_yell"),
					(else_try),
						(eq, ":type_wielded_item_var_2_1", 1),
						(agent_play_sound, ":var_2", "snd_woman_yell"),
					(try_end),
					(agent_play_sound, ":value", "snd_wooden_hit_low_armor_high_damage"),
					(agent_get_defend_action, ":attack_action_var_2", ":value"),
					(try_begin),
						(eq, ":attack_action_var_2", 2),
						(neg|position_is_behind_position, 1, 2),
						(agent_get_wielded_item, ":wielded_item_var_2_1", ":value", 1),
						(is_between, ":wielded_item_var_2_1", 1, "itm_cross_end"), #Previously itm_items_end
						(item_get_type, ":type_wielded_item_var_2_1", ":wielded_item_var_2_1"),
						(eq, ":type_wielded_item_var_2_1", 7),
						(agent_set_animation, ":value", "anim_shield_bash"),
					(else_try),
						(agent_set_animation, ":value", "anim_shield_strike"),
					(try_end),
				(try_end),
				(agent_get_slot, ":var_2_50", ":var_2", 50),
				(val_sub, ":var_2_50", 1),
				(val_max, ":var_2_50", 0),
				(agent_set_slot, ":var_2", 50, ":var_2_50"),
			(try_end)
			#Remove if you can get formations to work in MP without it
		]),
#				(0.0, 0.0, ti_once,
#		[
#			(eq, 0, 1),
#			(eq, "$enable_deahtcam", 1), #Not really needed
#			(main_hero_fallen)
#		],
#
#		[
#			(assign, "$fclock", 1),
#			##Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 2), #Not bugged, disabled for performance. #Patched to an extent #Commented to an extent
#			(get_player_agent_no, ":player_agent_no"),
#			
#(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_get_team, ":team_player_agent_no", ":player_agent_no"),
#			#Not bugged, disabled for performance#(team_give_order, ":team_player_agent_no", 9, 2)
#		]),
#		#End remove formations
				(0.0, 0.0, 5.0,
		[(multiplayer_is_server),],
####Probably the code which changes Agent Equipped Item
		[
		
			(get_player_agent_no, ":player_agent_no"),
			
#(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS. #Force spearmen to use their spears in Co-Op, note that uncommenting this will result in the player not having thier weapons auto-switched, but the AI will not use THEIR SPEARS.
			(try_for_agents, ":var_2"),
				(agent_is_human, ":var_2"),
				(agent_is_non_player, ":var_2"), #Added to prevent player from switching weapons
				(neq, ":player_agent_no", ":var_2"),
				(agent_slot_eq, ":var_2", 100, 0),
				(agent_is_alive, ":var_2"),
				(agent_get_horse, ":horse_var_2", ":var_2"),
				(agent_slot_eq, ":var_2", slot_agent_is_running_away, 0),
				(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
				(agent_get_ammo, ":ammo_var_2", ":var_2"),
				(le, ":ammo_var_2", 0),
				(try_begin),
					(gt, ":horse_var_2", 0),
					(neg|troop_is_guarantee_ranged, ":troop_id_var_2"),
					(agent_get_wielded_item, ":wielded_item_var_2_0", ":var_2", 0),
					(neg|is_between, ":wielded_item_var_2_0", "itm_light_lance", "itm_spear_a"),
					(try_for_range, ":item", "itm_light_lance", "itm_spear_a"),
						(agent_set_wielded_item, ":var_2", ":item"),
					(try_end),
				#(else_try),
					#(eq, "$tom_use_banners", 1), #Disable if error bugs
					#(try_for_range, ":item", 1198, 1202),
					#	(agent_set_wielded_item, ":var_2", ":item"),
					#(try_end),
					#(agent_get_wielded_item, ":item", ":var_2", 0),
					#(is_between, ":item", 1198, 1202),
				(else_try),
					(neg|troop_is_guarantee_ranged, ":troop_id_var_2"),
					(le, ":horse_var_2", 0),
					(agent_get_wielded_item, ":wielded_item_var_2_0", ":var_2", 0),
					(is_between, ":wielded_item_var_2_0", "itm_light_lance", "itm_spear_a"),
					(try_for_range, reg0, 0, 4),
						(agent_get_item_slot, ":item", ":var_2", reg0),
						(is_between, ":item", 1, "itm_cross_end"), #Previously itm_items_end
						(neg|is_between, ":item", "itm_light_lance", "itm_bamboo_spear"),
						(item_get_type, ":type_item", ":item"),
						(this_or_next|eq, ":type_item", 3),
						(this_or_next|eq, ":type_item", 4),
						(eq, ":type_item", 2),
						(agent_set_wielded_item, ":var_2", ":item"),
					(try_end),
				(else_try),
					(neg|troop_is_guarantee_ranged, ":troop_id_var_2"),
					(le, ":horse_var_2", 0),
					(agent_get_wielded_item, ":wielded_item_var_2_0", ":var_2", 0),
					(neg|is_between, ":wielded_item_var_2_0", "itm_bamboo_spear", "itm_wooden_shield"),
					(try_for_range, ":item", "itm_bamboo_spear", "itm_wooden_shield"),
						(agent_set_wielded_item, ":var_2", ":item"),
					(try_end),
				(else_try),
					(troop_is_guarantee_ranged, ":troop_id_var_2"),
					#(agent_get_team, ":team_var_2", ":var_2"), #sub_class = group ID! #Need to select multiple group ID's to make it not bug out! patched to an extent
					#(agent_get_team, ":team_var_2", ":var_2"), #DEFAULT
					#Removedforunassignedstuff#(agent_get_division, ":division_var_2", ":var_2"), #Removedforunassignedstuff#
					#(team_get_hold_fire_order, ":hold_fire_order_team_var_2_division_var_2", ":team_var_2", ":division_var_2"), #Patched to an extent

					#Removedforunassignedstuff#(neq, ":hold_fire_order_team_var_2_division_var_2", 1), #No error #Removedforunassignedstuff#
					(is_between, ":wielded_item_var_2_0", 1, "itm_cross_end"), #Previously itm_items_end
					(item_get_type, ":type_wielded_item_var_2_0", ":wielded_item_var_2_0"),
					(this_or_next|le, ":wielded_item_var_2_0", -1),
					(this_or_next|neq, ":type_wielded_item_var_2_0", 10),
					(this_or_next|neq, ":type_wielded_item_var_2_0", 9),
					(neq, ":type_wielded_item_var_2_0", 8),
					#(call_script, "script_get_closest_enemy_distance_new", ":var_2", ":team_var_2", 300),
					#(assign, ":var_13", reg1),
					#(gt, ":var_13", 300),
					(assign, ":value", 4),
					(try_for_range, reg0, 0, ":value"),
						(agent_get_item_slot, ":item_slot_var_2_reg0", ":var_2", reg0),
						(is_between, ":item_slot_var_2_reg0", 1, "itm_cross_end"), #Previously itm_items_end
						(item_get_type, ":type_wielded_item_var_2_0", ":item_slot_var_2_reg0"),
						(this_or_next|eq, ":type_wielded_item_var_2_0", 10),
						(this_or_next|eq, ":type_wielded_item_var_2_0", 8),
						(eq, ":type_wielded_item_var_2_0", 9),
						(agent_set_wielded_item, ":var_2", ":item_slot_var_2_reg0"),
						(assign, ":value", -1),
					(try_end),
				(try_end),
			(try_end)
			#Agent agent equip item
			# 1 error above
			#Cut from here
			]),
		(-19.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(assign, "$gk_order", 0),
			(assign, "$gk_order_hold_over_there", 0),
			(assign, "$autorotate_at_player", 1),
			(assign, "$fclock", 1),
			(try_for_range, ":number", 0, 4),
				(try_for_range, ":number_2", 84, 93),
					(team_set_slot, ":number", ":number_2", -1),
				(try_end),
			(try_end),
			(neq, "$new_session", 1),
			(call_script, "script_init_item_score"),
			(assign, "$new_session", 1)
		]),

		
		#####Patched for performance reasons below trigger
#		(0.0, 0.4, ti_once,
#		[],
#
#		[
#			#(get_player_agent_no, ":player_agent"), #Keep this uncommented
#			#(agent_get_team, "$fplayer_team_no", ":agent_no"), #Comment this out
#			#
#			(get_player_agent_no, "$fplayer_agent_no"), #DEF
#			(gt,  "$fplayer_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_get_team, "$fplayer_team_no", "$fplayer_agent_no"), #DEF #Patched to an extent, if you figure out how to include multiple teams in one line then you can uncomment this and fix it
#			#Not bugged for performance reasons (call_script, "script_store_battlegroup_data_coop"), #Patched to an extent
#			(try_for_agents, ":var_1"),
#				(agent_is_human, ":var_1"),
#				(agent_get_team, ":team_var_1", ":var_1"),
#				(agent_get_troop_id, ":troop_id_var_1", ":var_1"),
#				(store_faction_of_troop, ":faction_of_troop_troop_id_var_1", ":troop_id_var_1"),
#				(team_get_slot, ":team_var_1_1", ":team_var_1", 1),
#				(val_add, ":team_var_1_1", ":faction_of_troop_troop_id_var_1"),
#				(team_set_slot, ":team_var_1", 1, ":team_var_1_1"),
#			(try_end),
#			(try_for_range, ":number", 0, 4),
#				(team_slot_ge, ":number", 4, 1),
#				(team_get_leader, ":leader_number", ":number"),
#				(try_begin),
#					(ge, ":leader_number", 0),
#					(agent_get_troop_id, ":troop_id_leader_number", ":leader_number"),
#					(store_faction_of_troop, ":faction_of_troop_troop_id_leader_number", ":troop_id_leader_number"),
#				(else_try),
#					(team_get_slot, ":number_4", ":number", 4),
#					(team_get_slot, ":team_var_1_1", ":number", 1),
#					(store_mul, ":faction_of_troop_troop_id_leader_number", ":team_var_1_1", 10),
#					(val_div, ":faction_of_troop_troop_id_leader_number", ":number_4"),
#					(val_add, ":faction_of_troop_troop_id_leader_number", 5),
#					(val_div, ":faction_of_troop_troop_id_leader_number", 10),
#				(try_end),
#				(team_set_slot, ":number", 1, ":faction_of_troop_troop_id_leader_number"),
#			(try_end),
#			(display_message, "@Forming ranks."),
#			(assign, ":value", 0),
#			(try_for_range, ":number_2", 0, 9),
#				(store_add, ":value_2", 84, ":number_2"),
#				(this_or_next|team_slot_eq, "$fplayer_team_no", ":value_2", 2),
#				(team_slot_eq, "$fplayer_team_no", ":value_2", 5),
#				(store_add, ":value_2", 12, ":number_2"),
#				(team_get_slot, reg0, "$fplayer_team_no", ":value_2"),
#				(lt, ":value", reg0),
#				(assign, ":value", reg0),
#			(try_end),
#			(assign, ":value_3", 0),
#			(try_begin),
#				(gt, ":value", 0),
#				(val_mul, ":value", 2),
#				(convert_to_fixed_point, ":value"),
#				(store_sqrt, ":value_3", ":value"),
#				(convert_from_fixed_point, ":value_3"),
#				(val_sub, ":value_3", 1),
#				(store_mul, reg0, 2, 50),
#				(val_add, reg0, 300),
#				(val_mul, ":value_3", reg0),
#				(store_mul, ":value_4", 2, 50),
#				(val_add, ":value_4", 67),
#				(val_mul, ":value_4", 2),
#				(val_sub, ":value_3", ":value_4"),
#				(try_begin),
#					(gt, ":value_3", 0),
#					(agent_get_position, 49, "$fplayer_agent_no"),
#					(copy_position, 2, 49),
#					(call_script, "script_team_get_position_of_enemies", 60, "$fplayer_team_no", 9),
#					(call_script, "script_point_y_toward_position", 2, 60),
#					(position_move_y, 2, ":value_3"),
#					(agent_set_position, "$fplayer_agent_no", 2), #POSSIBLE ERROR OPCODE 1711 PATCHED TO AN EXTENT
#				(try_end),
#			(try_end),
#			#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
#			(try_for_range, ":number_2", 0, 9),
#				(store_add, ":value_2", 12, ":number_2"),
#				(team_slot_ge, "$fplayer_team_no", ":value_2", 1),
#				(store_add, ":value_2", 84, ":number_2"),
#				(try_begin),
#					(team_slot_eq, "$fplayer_team_no", ":value_2", 1),
#					#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number_2", 1),
#				(else_try),
#					(this_or_next|team_slot_eq, "$fplayer_team_no", ":value_2", 2),
#					(team_slot_eq, "$fplayer_team_no", ":value_2", 5),
#					#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number_2", 4),
#				(else_try),
#					#Not bugged patched for performance reasons(call_script, "script_get_default_formation", "$fplayer_team_no"),
#					#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number_2", reg0),
#				(try_end),
#			(try_end),
#			(try_begin),
#				(gt, ":value_3", 0),
#				(agent_set_position, "$fplayer_agent_no", 49), #POSSIBLE ERROR OPCODE 1711 PATCHED TO AN EXTENT
#			(try_end)
#		]),
		(0.0, 0.3, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 23)
		],

		[
			(eq, "$gk_order", 23),
			(try_begin),
				(game_key_is_down, 23),
				(assign, "$gk_order_hold_over_there", 1),
				(assign, "$gk_order", 0),
				(assign, "$holdit", 0),
			(else_try),
				(eq, "$holdit", 1),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 0), #Patched to an extent 
				(assign, "$gk_order", 0),
				(assign, "$holdit", 0),
			(try_end)
		]),
				(0.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 23)
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 23),
				(assign, "$holdit", 0),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$holdit", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent, if you figure out how to make it work for both teams then this, and spearwalls, and store_battlegroup_Data would all work, even SP formations
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 5), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),
		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 24),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 24),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 1), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 6), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 25),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 25),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
				##Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 2), #Not bugged, disabled for performance. #Patched to an extent #Commented to an extent
				(assign, "$tom_yell_smelly_peasents", 1),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 8), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 26),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(eq, "$gk_order", 0),
				(assign, "$gk_order", 26),
				#(start_presentation, "prsnt_order_display"),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent group ID issue can be fixed if u figure it out
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 7), #Patched to an extent #Commented to an extent#
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
				#(try_for_range, ":number", 0, 9),
				#	(class_is_listening_order, "$fplayer_team_no", ":number"),
				#	(store_add, ":value", 12, ":number"),
				#	(team_slot_ge, "$fplayer_team_no", ":value", 1),
				#	(assign, "$fclock", 1),
				#	#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 2),
				#	(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), 
				#(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),
		
				(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 27),
(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #patched to an extent
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 14), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
				#(try_for_range, ":number", 0, 9),
				#	(class_is_listening_order, "$fplayer_team_no", ":number"),
				#	(store_add, ":value", 12, ":number"),
				#	(team_slot_ge, "$fplayer_team_no", ":value", 1),
				#	(assign, "$fclock", 1),
				#	#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 3),
				#	(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #patched to an extent
				#(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 28)
		],

		[
			(try_begin),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 4), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
				#(try_for_range, ":number", 0, 9),
				#	(class_is_listening_order, "$fplayer_team_no", ":number"),
				#	(store_add, ":value", 12, ":number"),
				#	(team_slot_ge, "$fplayer_team_no", ":value", 1),
				#	(assign, "$fclock", 1),
				#	#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 4),
				#	(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
				#(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(key_clicked, 65)
		],

		[
			(eq, "$gk_order", 26),
			#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
			#(try_for_range, ":number", 0, 9),
			#	(class_is_listening_order, "$fplayer_team_no", ":number"),
			#	(store_add, ":value", 12, ":number"),
			#	(team_slot_ge, "$fplayer_team_no", ":value", 1),
			#	(assign, "$fclock", 1),
			#	#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 5),
			#	(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
			#(try_end),
			(assign, "$gk_order", 0),
			#(start_presentation, "prsnt_order_display")
		]),

		(0.0, 0.0, 0.0,
		[
			(key_clicked, 66),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(eq, "$gk_order", 26),
			(assign, "$fclock", 1),
			##Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 2), #Not bugged, disabled for performance. #Patched to an extent #Commented to an extent
			(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
			(assign, "$gk_order", 0),
			#(start_presentation, "prsnt_order_display")
		]),
########Disable ability for player to use formations in MP
#		(0.0, 0.0, 0.0,
#		[
#			(this_or_next|game_key_clicked, 30),
#			(this_or_next|game_key_clicked, 31),
#			(this_or_next|game_key_clicked, 32),
#			(this_or_next|game_key_clicked, 33),
#			(this_or_next|game_key_clicked, 34),
#			(this_or_next|game_key_clicked, 35),
#			(this_or_next|game_key_clicked, 36),
#			(this_or_next|game_key_clicked, 37),
#			(this_or_next|game_key_clicked, 38),
#			(this_or_next|game_key_clicked, 39),
#			(this_or_next|game_key_clicked, 40),
#			(game_key_clicked, 29)
#		],
#
#		[
#			(assign, "$gk_order", 0),
#			#(start_presentation, "prsnt_order_display")
#		]),
#		
###########End disable MP Formations
		(0.0, 0.0, 0.0,
		[
		(multiplayer_is_server),#####T
			(key_is_down, 1),
			(is_presentation_active, "prsnt_order_display")
		],

		[
			(assign, "$gk_order", 0),
			(presentation_set_duration, 0)
		]),
		#Patched for performance reasons
		#Begin bugged formations
#				(0.5, 0.0, 0.0,
#		[
#			(eq, "$gk_order_hold_over_there", 1),
#			(neg|game_key_is_down, 23)
#		],
#
#		[
#			(set_fixed_point_multiplier, 100),
#			(assign, "$fclock", 1),
#			(call_script, "script_team_get_position_of_enemies", 60, "$fplayer_team_no", 9),
#			(assign, ":var_1", 0),
#			#(try_for_range, ":number", 0, 9),
#			#	(class_is_listening_order, "$fplayer_team_no", ":number"), #Patched to an extent
#			#	(store_add, ":value", 12, ":number"),
#			#	(team_slot_ge, "$fplayer_team_no", ":value", 1),
#			#	(val_add, ":var_1", 1),
#			#(try_end),
#			(gt, ":var_1", 0),
#			(agent_get_position, 49, "$fplayer_agent_no"), #Patched to an extent
#			#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
#			(try_for_range, ":number", 0, 9),
#				(class_is_listening_order, "$fplayer_team_no", ":number"),
#				(store_add, ":value", 12, ":number"),
#				(team_get_slot, ":fplayer_team_no_value", "$fplayer_team_no", ":value"),
#				(gt, ":fplayer_team_no_value", 0),
#				(store_add, ":value", 93, ":number"),
#				(team_get_slot, ":fplayer_team_no_value_2", "$fplayer_team_no", ":value"),
#				(team_get_order_position, 2, "$fplayer_team_no", ":number"),
#				(call_script, "script_point_y_toward_position", 2, 60),
#				(try_begin),
#					(gt, ":var_1", 1),
#					(agent_set_position, "$fplayer_agent_no", 2), #POSSIBLE ERROR OPCODE 1711 Patched to an extent
#					#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", ":fplayer_team_no_value_2"),
#				(else_try),
#					(neq, ":fplayer_team_no_value_2", 0),
#					(call_script, "script_set_formation_position", "$fplayer_team_no", ":number", 2), #Patched to an extent
#					(store_add, ":value", 102, ":number"),
#					(team_get_slot, ":fplayer_team_no_value_3", "$fplayer_team_no", ":value"),
#					(try_begin),
#						(store_add, ":value", 84, ":number"),
#						(team_get_slot, ":fplayer_team_no_value_4", "$fplayer_team_no", ":value"),
#						(neq, ":fplayer_team_no_value_4", 2),
#						(neq, ":fplayer_team_no_value_4", 5),
#						(call_script, "script_get_centering_amount", ":fplayer_team_no_value_2", ":fplayer_team_no_value", ":fplayer_team_no_value_3"),
#						(try_begin),
#							(eq, ":fplayer_team_no_value_4", 1),
#							(val_mul, reg0, -1),
#							(assign, ":value_2", "script_form_archers"),
#						(else_try),
#							(assign, ":value_2", "script_form_infantry"),
#						(try_end),
#						(position_move_x, 2, reg0),
#					(else_try),
#						(assign, ":value_2", "script_form_cavalry"),
#					(try_end),
#					(copy_position, 1, 2),
#					(call_script, ":value_2", "$fplayer_team_no", ":number", "$fplayer_agent_no", ":fplayer_team_no_value_3", ":fplayer_team_no_value_2"),
#				(try_end),
#				(store_add, ":value", 111, ":number"),
#				(team_set_slot, "$fplayer_team_no", ":value", 0),
#			(try_end),
#			(agent_set_position, "$fplayer_agent_no", 49), #POSSIBLE ERROR OPCODE 1711 PATCHED to an extent
#			(assign, "$gk_order_hold_over_there", 0)
#		]),
		
#####Completly remove option to form formations in MP Begin Patched to an extent
#		(1.0, 0.0, 0.0,
#		[
#			(neg|key_is_down, 65),
#			(neg|key_is_down, 66),
#			(neg|game_key_is_down, 23),
#			(neg|game_key_is_down, 24),
#			(neg|game_key_is_down, 25),
#			(neg|game_key_is_down, 26),
#			(neg|game_key_is_down, 27),
#			(neg|game_key_is_down, 28)
#		],
#
#		[
#			(set_fixed_point_multiplier, 100),
#			(store_mod, ":value", "$fclock", 5),
#			(store_mod, ":value_2", "$fclock", 10),
#			(try_begin),
#				(eq, ":value_2", 0),
#				(try_for_range, ":number", 0, 4),
#					(try_for_range, ":number_2", 0, 9),
#						(store_add, ":value_3", 84, ":number_2"),
#						(this_or_next|team_slot_eq, ":number", ":value_3", 4),
#						(team_slot_eq, ":number", ":value_3", 5),
#						(team_set_slot, ":number", ":value_3", -1),
#					(try_end),
#				(try_end),
#			(try_end),
#			(call_script, "script_store_battlegroup_data_coop"), #Patched to an extent group ID error
#			(call_script, "script_team_get_position_of_enemies", 60, "$fplayer_team_no", 9),
#			(try_begin),
#				(eq, reg0, 0),
#				(try_for_range, ":number_2", 0, 9),
#					(call_script, "script_formation_end", "$fplayer_team_no", ":number_2"),
#				(try_end),
#			(else_try),
#				(assign, "$autorotate_at_player", 0),
#				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
#				(try_for_range, ":number_2", 0, 9),
#					(store_add, ":value_3", 12, ":number_2"),
#					(team_get_slot, ":fplayer_team_no_value_3", "$fplayer_team_no", ":value_3"),
#					(gt, ":fplayer_team_no_value_3", 0),
#					(try_begin),
#						(store_add, ":value_3", 111, ":number_2"),
#						(team_slot_eq, "$fplayer_team_no", ":value_3", 1),
#						#(call_script, "script_battlegroup_place_around_leader", "$fplayer_team_no", ":number_2"), #Patched to an extent
#						(team_set_slot, "$fplayer_team_no", ":value_3", 1),
#					(else_try),
#						(eq, ":value", 0),
#						(store_add, ":value_3", 93, ":number_2"),
#						(team_get_slot, ":fplayer_team_no_value_3_2", "$fplayer_team_no", ":value_3"),
#						(neq, ":fplayer_team_no_value_3_2", 0),
#						(team_get_movement_order, reg0, "$fplayer_team_no", ":number_2"),
#						(neq, reg0, 11),
#						(call_script, "script_get_formation_position", 1, "$fplayer_team_no", ":number_2"),
#						(store_add, ":value_3", 102, ":number_2"),
#						(team_get_slot, ":fplayer_team_no_value_3_3", "$fplayer_team_no", ":value_3"),
#						(store_add, ":value_3", 84, ":number_2"),
#						(team_get_slot, ":fplayer_team_no_value_3_4", "$fplayer_team_no", ":value_3"),
#						(try_begin),
#							(neq, ":fplayer_team_no_value_3_4", 2),
#							(neq, ":fplayer_team_no_value_3_4", 5),
#							(position_move_y, 1, -2000),
#						(try_end),
#						(call_script, "script_point_y_toward_position", 1, 60),
#						(try_begin),
#							(neq, ":fplayer_team_no_value_3_4", 2),
#							(neq, ":fplayer_team_no_value_3_4", 5),
#							(position_move_y, 1, 2000),
#						(try_end),
#						#(call_script, "script_set_formation_position", "$fplayer_team_no", ":number_2", 1), #Patched to an extent
#						(try_begin),
#							(neq, ":fplayer_team_no_value_3_4", 2),
#							(neq, ":fplayer_team_no_value_3_4", 5),
#							(call_script, "script_get_centering_amount", ":fplayer_team_no_value_3_2", ":fplayer_team_no_value_3", ":fplayer_team_no_value_3_3"),
#							(try_begin),
#								(eq, ":fplayer_team_no_value_3_4", 1),
#								(val_mul, reg0, -1),
#							(try_end),
#							(position_move_x, 1, reg0),
#						(try_end),
#						(try_begin),
#							(eq, ":fplayer_team_no_value_3_4", 1),
#							(call_script, "script_form_archers", "$fplayer_team_no", ":number_2", "$fplayer_agent_no", ":fplayer_team_no_value_3_3", ":fplayer_team_no_value_3_2"),
#						(else_try),
#							(this_or_next|eq, ":fplayer_team_no_value_3_4", 2),
#							(eq, ":fplayer_team_no_value_3_4", 5),
#							(call_script, "script_form_cavalry", "$fplayer_team_no", ":number_2", "$fplayer_agent_no", ":fplayer_team_no_value_3_3"),
#						(else_try),
#							(call_script, "script_form_infantry", "$fplayer_team_no", ":number_2", "$fplayer_agent_no", ":fplayer_team_no_value_3_3", ":fplayer_team_no_value_3_2"),
#						(try_end),
#					(try_end),
#				(try_end),
#				(assign, "$autorotate_at_player", 1),
#			(try_end),
#			(val_add, "$fclock", 1)
#		]),
#		#EMD BUGGED FORMATIONS somewhat patched
#				(-19.0, 0.0, 0.0,
#		[],
#
#		[
#			(assign, "$cur_casualties", 0),
#			(assign, "$prev_casualties", 0),
#			(assign, "$ranged_clock", 1),
#			(assign, "$battle_phase", 1),
#			(assign, "$clock_reset", 0),
#			(try_for_range, ":number", 0, 4),
#				(team_set_slot, ":number", 2, 1),
#			(try_end),
#			(init_position, 41),
#			(init_position, 42),
#			(init_position, 43),
#			(init_position, 44)
#		]),
#
#		(0.0, 0.5, ti_once,
#		[],
#
#		[
#			(try_for_agents, ":var_1"),
#				(agent_set_slot, ":var_1", slot_agent_is_running_away, 0),
#			(try_end),
#			(set_fixed_point_multiplier, 100),
#			(call_script, "script_battlegroup_get_position", 45, 0, 9),
#			(call_script, "script_battlegroup_get_position", 46, 1, 9),
#			(call_script, "script_battlegroup_get_position", 47, 2, 9),
#			(call_script, "script_battlegroup_get_position", 48, 3, 9),
#			(call_script, "script_field_tactics", 1)
#		]),
#####Completly remove option to form formations in MP End Patched to an extent












###Bugged Spawns begin, causes your troops to spawn in other sides
#		(1.0, 0.5, 0.0,
#		[],
#
#		[
#			(try_begin),
#				(call_script, "script_cf_count_casualties"),
#				(assign, "$cur_casualties", reg0),
#				(assign, "$battle_phase", 3),
#			(try_end),
#			(set_fixed_point_multiplier, 100),
#			(call_script, "script_store_battlegroup_data_coop"),
#			(try_begin),
#				(ge, "$battle_phase", 3),
#				(eq, "$clock_reset", 0),
#				(call_script, "script_field_tactics", 1),
#				(assign, "$ranged_clock", 0),
#				(assign, "$clock_reset", 1),
#			(else_try),
#				(ge, "$battle_phase", 2),
#				(store_mod, reg0, "$ranged_clock", 5),
#				(eq, reg0, 0),
#				(call_script, "script_field_tactics", 1),
#				(team_set_slot, 0, 3, "$defender_reinforcement_stage"),
#				(team_set_slot, 1, 3, "$attacker_reinforcement_stage"),
#			(else_try),
#				(call_script, "script_field_tactics", 0),
#			(try_end),
#			(try_begin),
#				(eq, "$battle_phase", 1),
#				(assign, ":value", 0),
#				(try_for_range, ":number", 0, 4),
#					(neq, ":number", "$fplayer_team_no"),
#					(team_slot_ge, ":number", 4, 1),
#					(call_script, "script_battlegroup_get_position", 1, ":number", 1),
#					(team_get_order_position, 0, ":number", 1),
#					(get_distance_between_positions, reg0, 0, 1),
#					(gt, reg0, 500),
#					(assign, ":value", 1),
#					(try_begin),
#						(store_random_in_range, ":random_in_range_0_100", 0, 100),
#						(lt, ":random_in_range_0_100", 15),
#						(play_sound_at_position, "snd_horn", 1),
#					(try_end),
#				(try_end),
#				(eq, ":value", 0),
#				(assign, "$battle_phase", 2),
#			(try_end),
#			(val_add, "$ranged_clock", 1)
#		]),
		###Bugged spawns end
		
				(-25.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(agent_is_human, ":trigger_param_1"),
			(agent_is_non_player, ":trigger_param_1"),
			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
			(lt, ":troop_id_trigger_param_1", "trp_kidnapped_girl"),
			(try_for_range, reg0, 0, 4),
				(agent_get_item_slot, ":item_slot_trigger_param_1_reg0", ":trigger_param_1", reg0),
				(is_between, ":item_slot_trigger_param_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
				(agent_unequip_item, ":trigger_param_1", ":item_slot_trigger_param_1_reg0"),
			(try_end),
			(try_for_range, reg0, 0, 2),
				(agent_get_wielded_item, ":item_slot_trigger_param_1_reg0", ":trigger_param_1", reg0),
				(is_between, ":item_slot_trigger_param_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
				(agent_unequip_item, ":trigger_param_1", ":item_slot_trigger_param_1_reg0"),
			(try_end),
			(assign, ":var_4", 0),
			(assign, ":var_5", 25),
			(assign, ":var_6", 50),
			(assign, ":var_7", 75),
			(assign, ":var_8", 100),
			(assign, ":var_18", 125),
			(assign, ":var_10", 150),
			(assign, ":var_11", 175),
			(assign, ":var_12", 200),
			(assign, ":value", 0),
			(assign, ":value_2", 0),
			(assign, ":value_3", 0),
			(assign, ":value_4", 0),
			(assign, ":value_5", 0),
			(assign, ":value_6", 0),
			(assign, ":value_7", 0),
			(assign, ":value_8", 0),
			(assign, ":value_9", 0),
			(troop_get_inventory_capacity, ":inventory_capacity_troop_id_trigger_param_1", ":troop_id_trigger_param_1"),
			(try_for_range, ":localvariable", 0, ":inventory_capacity_troop_id_trigger_param_1"),
				(troop_get_inventory_slot, ":inventory_slot_troop_id_trigger_param_1_localvariable", ":troop_id_trigger_param_1", ":localvariable"),
				(is_between, ":inventory_slot_troop_id_trigger_param_1_localvariable", 1, "itm_cross_end"), #Previously itm_items_end
				(item_get_type, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
				(try_begin),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 4),
					(val_add, ":var_4", 1),
					(troop_set_slot, "trp_items_array", slot_troop_relations_begin, ":var_4"),
					(troop_set_slot, "trp_items_array", ":var_4", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 2),
					(val_add, ":var_5", 1),
					(troop_set_slot, "trp_items_array", slot_troop_last_quest_betrayed, ":var_5"),
					(troop_set_slot, "trp_items_array", ":var_5", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_2", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 7),
					(val_add, ":var_6", 1),
					(troop_set_slot, "trp_items_array", slot_troop_recruitment_random, ":var_6"),
					(troop_set_slot, "trp_items_array", ":var_6", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_3", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 3),
					(val_add, ":var_7", 1),
					(troop_set_slot, "trp_items_array", slot_troop_personalitymatch_object, ":var_7"),
					(troop_set_slot, "trp_items_array", ":var_7", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_4", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 10),
					(val_add, ":var_8", 1),
					(troop_set_slot, "trp_items_array", 100, ":var_8"),
					(troop_set_slot, "trp_items_array", ":var_8", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_5", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 6),
					(val_add, ":var_18", 1),
					(troop_set_slot, "trp_items_array", slot_troop_rehire_speech, ":var_18"),
					(troop_set_slot, "trp_items_array", ":var_18", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_6", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 5),
					(val_add, ":var_10", 1),
					(troop_set_slot, "trp_items_array", slot_troop_days_on_mission, ":var_10"),
					(troop_set_slot, "trp_items_array", ":var_10", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_7", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 8),
					(val_add, ":var_11", 1),
					(troop_set_slot, "trp_items_array", 175, ":var_11"),
					(troop_set_slot, "trp_items_array", ":var_11", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_8", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 9),
					(val_add, ":var_12", 1),
					(troop_set_slot, "trp_items_array", 200, ":var_12"),
					(troop_set_slot, "trp_items_array", ":var_12", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_9", 1),
				(try_end),
			(try_end),
			(try_begin),
				(eq, ":value", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_relations_begin),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 1, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_2", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_last_quest_betrayed),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 26, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_3", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_recruitment_random),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 51, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_4", 1),
				(try_begin),
					(eq, ":value_2", 1),
					(store_random_in_range, ":random_in_range_0_100", 0, 100),
					(lt, ":random_in_range_0_100", 65),
				(else_try),
					(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_personalitymatch_object),
					(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 76, ":items_array_relations_begin"),
					(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
					(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
				(try_end),
			(try_end),
			(try_begin),
				(eq, ":value_5", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 100),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 101, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_6", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_rehire_speech),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 126, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_7", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_days_on_mission),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 151, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_8", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 175),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 176, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_9", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 200),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 201, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end)
		]),
				(-19.0, 0.0, 0.0,
		[#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),],

		[
			(assign, "$tom_sand_storm", 0),
			(call_script, "script_change_rain_or_snow"),
			(set_fixed_point_multiplier, 100),
						 #####Begin Debug
			 #(display_message, "@Rain change to snow!", 0x006495ed),
			 #####End Debug
			(try_begin),
				(is_currently_night),
				#(set_shader_param_float, "@vFresnelMultiplier", 15),
			(else_try),
				#(set_shader_param_float, "@vFresnelMultiplier", 50),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
		     (gt,  ":player_agent_no", -1), #if snow
			 #####Begin Debug
			 #(display_message, "@Desert Storm incoming!", 0x006495ed),
			 #####End Debug
			(agent_get_position, 0, ":player_agent_no"), 
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
			(val_add, ":position_z_0", 400),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_desert_storm", 0, 2),
			(set_fixed_point_multiplier, 100)
						 #####Begin Debug
			 #(display_message, "@Desert storm finalize!", 0x006495ed),
			 #####End Debug
		]),

#		(300.0, 2.0, 300.0,
#		#(0.0, 2.0, ti_once, #Patched to an extent
#		[
#		(multiplayer_is_server),
#			(eq, "$tom_use_banners", 1)
#		],
#
#		[
#			(call_script, "script_set_flag_carriers")
#		]),

#		(10.0, 0.0, 0.0,
#		[
#		(neg|multiplayer_is_server),
#			(eq, "$tom_use_banners", 1),
#			(eq, "$tom_bonus_banners", 1)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(try_for_range, ":value"),
#				(agent_slot_eq, ":value", 107, 1),
#				(agent_is_alive, ":value"),
#				(agent_is_active, ":value"),
#				(agent_get_team, ":team_value", ":value"),
#				(agent_get_position, 1, ":value"),
#				(try_for_range, ":value_2"),
#					(neq, ":value_2", ":value"),
#					(agent_get_team, ":team_value_2", ":value_2"),
#					(eq, ":team_value", ":team_value_2"),
#					(agent_is_alive, ":value_2"),
#					(agent_is_active, ":value_2"),
#					(agent_is_human, ":value_2"),
#					(agent_get_position, 2, ":value_2"),
#					(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_1_2", 1, 2),
#					(le, ":distance_between_positions_in_meters_1_2", 10),
#					(store_agent_hit_points, ":agent_hit_points_value_2", ":value_2"),
#					(val_add, ":agent_hit_points_value_2", 2),
#					(val_min, ":agent_hit_points_value_2", 101),
#					(agent_set_hit_points, ":value_2", ":agent_hit_points_value_2"),
#					(try_begin),
#						(eq, ":value_2", ":player_agent_no"),
#						(display_message, "@You feel secured standing near the banner, healing some of your HP.", 0x006495ed),
#					(try_end),
#				(try_end),
#			(try_end),
#			(assign, ":value", ":player_agent_no"),
#			(agent_is_alive, ":value"), #Patched to an extent Agent ID -1 error on this opcode and the line below this (the opcode) #Note only error when spectating, maybe re-enable so you can heal near banners?
#			(agent_get_wielded_item, ":wielded_item_value_0", ":value", 0), #Patched to an extent
#			(is_between, ":wielded_item_value_0", 1198, 1202),
#			(agent_get_team, ":team_value", ":value"),
#			(agent_get_position, 1, ":value"),
#			(try_for_range, ":value_2"),
#				(neq, ":value_2", ":value"),
#				(agent_get_team, ":team_value_2", ":value_2"),
#				(eq, ":team_value", ":team_value_2"),
#				(agent_is_alive, ":value_2"),
#				(agent_is_active, ":value_2"),
#				(agent_is_human, ":value_2"),
#				(agent_get_position, 2, ":value_2"),
#				(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_1_2", 1, 2),
#				(le, ":distance_between_positions_in_meters_1_2", 10),
#				(store_agent_hit_points, ":agent_hit_points_value_2", ":value_2"),
#				(try_begin),
#					(eq, ":wielded_item_value_0", 1201),
#					(val_add, ":agent_hit_points_value_2", 1),
#				(try_end),
#				(val_add, ":agent_hit_points_value_2", 5),
#				(val_max, ":agent_hit_points_value_2", 101),
#				(agent_set_hit_points, ":value_2", ":agent_hit_points_value_2"),
#			(try_end)
#		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 3)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
					     (gt,  ":player_agent_no", -1), #if snow
			(agent_get_position, 0, ":player_agent_no"), 
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
						 #####Begin Debug
			 #(display_message, "@Rain start!", 0x006495ed),
			 #####End Debug
			(val_add, ":position_z_0", 2100),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_rain", 0, 1),
						 #####Begin Debug
			 #(display_message, "@Rain finalize!", 0x006495ed),
			 #####End Debug
			(set_fixed_point_multiplier, 100)
			
		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 2)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
					     (gt,  ":player_agent_no", -1), #if snow
			(agent_get_position, 0, ":player_agent_no"), 
						 #####Begin Debug
			# (display_message, "@Blizzard start!", 0x006495ed),
			 #####End Debug
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
			(val_add, ":position_z_0", 2000),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_blizzard", 0, 1),
						 #####Begin Debug
			 #(display_message, "@Blizzard finalize!", 0x006495ed),
			 #####End Debug
			(set_fixed_point_multiplier, 100)
		]),

		(8.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 3)
		],

		[
			(store_random_in_range, ":random_in_range_0_100", 0, 100),
			(try_begin),
						 #####Begin Debug
			 #(display_message, "@Playing thunder sounds begin!", 0x006495ed),
			 #####End Debug
				(ge, ":random_in_range_0_100", 90),
				(play_sound, "snd_thunder"),
			#####Begin Debug
			 #(display_message, "@Playing thunder sounds finalize!", 0x006495ed),
			 #####End Debug
				
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 2)
		],

		[
					 #####Begin Debug
			 #(display_message, "@Playing wind sounds TWO!!", 0x006495ed),
			 #####End Debug
			(play_sound, "snd_wind")
						 #####Begin Debug
			 #(display_message, "@Playing wind sounds TWO Finalize!", 0x006495ed),
			 #####End Debug
		]),

		(0.0, 0.0, ti_once,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 1)
		],

		[
					 #####Begin Debug
			 #(display_message, "@Playing wind sounds!", 0x006495ed),
			 #####End Debug
			(play_sound, "snd_wind")
						 #####Begin Debug
			 #(display_message, "@Playing wind sounds finalize!", 0x006495ed),
			 #####End Debug
		]),
		
		######SP Related things, probably remove to optimize if none of it is actually used
#				(1.0, 0.0, ti_once,
#		[
#			(neq, "$g_battle_result", 0),
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(agent_is_alive, ":player_agent_no"),
#			(agent_get_troop_id, ":troop_id_player_agent_no", ":player_agent_no"),
#			(eq, ":troop_id_player_agent_no", "trp_player")
#		],
#
#		[
#			(call_script, "script_freelancer_keep_field_loot")
#		]),

		(0.0, 1.5, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(key_clicked, key_m),
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_is_alive, ":player_agent_no"),
			(agent_set_animation, ":player_agent_no", "anim_cheer", 1),
			(agent_play_sound, ":player_agent_no", "snd_man_victory")
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_get_team, ":team_player_agent_no", ":player_agent_no"), 
			(agent_get_position, 1, ":player_agent_no"), 
			(try_for_agents, ":var_3"),
				(agent_is_alive, ":var_3"),
				(agent_is_human, ":var_3"),
				(agent_get_team, ":team_var_3", ":var_3"),
				(eq, ":team_var_3", ":team_player_agent_no"),
				(agent_get_position, 0, ":var_3"),
				(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_0_1", 0, 1),
				(lt, ":distance_between_positions_in_meters_0_1", 20),
				(agent_set_animation, ":var_3", "anim_cheer", 1),
				(agent_play_sound, ":var_3", "snd_man_victory"),
				(agent_get_slot, ":var_3_courage_score", ":var_3", slot_agent_courage_score),
				(val_add, ":var_3_courage_score", 5),
				(val_min, ":var_3_courage_score", 9600),
				(agent_set_slot, ":var_3", slot_agent_courage_score, ":var_3_courage_score"),
			(try_end),
			(display_message, "@Huzzah! You encourage your nearby troops.")
		]),

		(0.0, 1.7, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_yell_smelly_peasents", 1)
		],

		[
			(call_script, "script_cf_tom_command_cheer_coop"),
			(assign, "$tom_yell_smelly_peasents", 0)
		]),

		(-26.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(store_trigger_param_2, ":trigger_param_2"),
			(neg|agent_is_ally, ":trigger_param_1"),
			(agent_is_human, ":trigger_param_1"),
			(eq, ":trigger_param_2", "$fplayer_agent_no"),
			(val_add, "$killcount", 1)
		]),

		###########(-19.0, 0.0, 0.0,
		###########[],
        ###########
		###########[
		###########	(call_script, "script_clear_troop_array", "trp_lances_troop_in_combat", 0, "$lance_troop_serving")
		###########]),

#		(-25.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(agent_is_human, ":trigger_param_1"),
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(neq, ":trigger_param_1", ":player_agent_no"),
#			(agent_get_party_id, ":party_id_trigger_param_1", ":trigger_param_1"),
#			(eq, ":party_id_trigger_param_1", "p_main_party"),
#			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#			(call_script, "script_search_for_troop", ":troop_id_trigger_param_1"),
#			(agent_set_slot, ":trigger_param_1", 102, reg0)
#		]),
				(2.0, 0.0, 0.0,
		[
		(multiplayer_is_server),
			(eq, "$g_battle_won", 0)
		],
####Horse archers, use archery in MP, forces them to attack in game start...
		[
			(set_fixed_point_multiplier, 100),
			(try_for_agents, ":var_1"),
				(agent_get_troop_id, ":troop_id_var_1", ":var_1"),
				(try_begin),
					(agent_is_alive, ":var_1"),
					(agent_is_human, ":var_1"),
					(agent_is_non_player, ":var_1"),
					(agent_is_active, ":var_1"),
					(agent_slot_eq, ":var_1", slot_agent_is_running_away, 0),
					(agent_slot_eq, ":var_1", 100, 0),
					#Removedforunassignedstuff#(agent_get_division, ":division_var_1", ":var_1"), #Removedforunassignedstuff#
					(agent_get_horse, ":horse_var_1", ":var_1"),
					(gt, ":horse_var_1", 0),
					(troop_is_guarantee_ranged, ":troop_id_var_1"),
					(agent_get_ammo, ":ammo_var_1", ":var_1"),
					(gt, ":ammo_var_1", 0),
					(agent_get_team, ":team_var_1", ":var_1"),
					#(team_get_hold_fire_order, ":hold_fire_order_team_var_1_division_var_1", ":team_var_1", ":division_var_1"), #PATCHED to an extent
					#Removedforunassignedstuff#(neq, ":hold_fire_order_team_var_1_division_var_1", 1), #Removedforunassignedstuff#
					(try_begin),
						(try_for_range, reg0, 0, 4),
							(agent_get_item_slot, ":item_slot_var_1_reg0", ":var_1", reg0),
							(is_between, ":item_slot_var_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
							(item_get_type, ":type_item_slot_var_1_reg0", ":item_slot_var_1_reg0"),
							(this_or_next|eq, ":type_item_slot_var_1_reg0", 10),
							(eq, ":type_item_slot_var_1_reg0", 8),
							(agent_set_wielded_item, ":var_1", ":item_slot_var_1_reg0"),
							(assign, reg0, -1),
						(try_end),
					(try_end),
					(agent_get_wielded_item, ":item_slot_var_1_reg0", ":var_1", 0),
					(is_between, ":item_slot_var_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
					(item_get_type, ":type_item_slot_var_1_reg0", ":item_slot_var_1_reg0"),
					(this_or_next|eq, ":type_item_slot_var_1_reg0", 10),
					(eq, ":type_item_slot_var_1_reg0", 8),
					(call_script, "script_get_first_closest_enemy_distance", ":var_1", ":team_var_1", 200),
					(assign, ":var_10", reg1),
					(assign, ":var_11", reg4),
					(gt, ":var_11", -1),
					(try_begin),
						(assign, ":value", 8500),
						(assign, ":value_2", 9000),
						(assign, ":var_14", 12),
						(try_begin),
							(eq, ":type_item_slot_var_1_reg0", 10),
							(assign, ":value_2", 3000),
							(assign, ":value", 3500),
							(val_mul, ":var_14", 3),
						(try_end),
						#(team_get_movement_order, reg0, ":team_var_1", ":division_var_1"), #Default patched to an extent
						(eq, reg0, 2),
						(call_script, "script_tom_agent_skirmish", ":var_1", ":var_11", ":var_10", ":value", ":value_2", ":var_14"),
						(try_begin),
							(lt, ":var_10", 9500),
							(store_random_in_range, ":random_in_range_0_10", 0, 10),
							(le, ":random_in_range_0_10", 2),
							(agent_get_attack_action, ":attack_action_var_1", ":var_1"),
							(eq, ":attack_action_var_1", 0),
							(agent_get_combat_state, ":combat_state_var_1", ":var_1"),
							(neq, ":combat_state_var_1", 7),
							(this_or_next|eq, ":type_item_slot_var_1_reg0", 10),
							(eq, ":type_item_slot_var_1_reg0", 8),
							(agent_set_attack_action, ":var_1", 0, 0),
						(try_end),
					(try_end),
				(else_try),
					(agent_slot_eq, ":var_1", 104, 1),
					(agent_set_slot, ":var_1", 104, 0),
					(agent_clear_scripted_mode, ":var_1"),
				(try_end),
			(try_end)
		]),
		#####END SP Stuff
		####Horse archers end
		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_desertv2", 1),
						(display_message, "@DesertV2 generated!", 0x006495ed),

		],

		[

			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_desertv2", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 500),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(position_set_z, 1, ":position_z_1"),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_15_66", 15, 66),
				(store_random_in_range, ":random_in_range_15_66_2", 15, 66),
				(store_random_in_range, ":random_in_range_30_66", 30, 66),
				(store_random_in_range, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a", "spr_valleyRock_flatRounded_small_1", "spr_tree_14_a"),
				(spawn_scene_prop, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a"),
				(prop_instance_set_scale, reg0, ":random_in_range_15_66", ":random_in_range_15_66_2", ":random_in_range_30_66"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 900),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a", "spr_seedy_plant_a", "spr_palm_aa"),
				(spawn_scene_prop, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 250),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a", "spr_palm_aa", "spr_valleyRock_flatRounded_small_1"),
				(spawn_scene_prop, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a"),
			(try_end)
		]),
		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_iberian", 1),
								(display_message, "@Iberian generated!", 0x006495ed),

		],

		[

			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_iberian", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":var_5", 130),
			(val_div, ":var_5", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":var_5"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_40_100", 40, 100),
				(store_random_in_range, ":random_in_range_desert_tree_aa_tree_16_a", "spr_desert_tree_aa", "spr_tree_16_a"),
				(spawn_scene_prop, ":random_in_range_desert_tree_aa_tree_16_a"),
				(prop_instance_set_scale, reg0, ":random_in_range_40_100", ":random_in_range_40_100", ":random_in_range_40_100"),
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_iberian2", 1),
								(display_message, "@Iberian2 generated!", 0x006495ed),

		],

		[

			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_iberian2", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 300),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_tree_16_a_pine_1_b", "spr_tree_16_a", "spr_pine_1_b"),
				(spawn_scene_prop, ":random_in_range_tree_16_a_pine_1_b"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 20),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_tree_16_a_pine_1_b", "spr_pine_1_b", "spr_seedy_plant_a"),
				(spawn_scene_prop, ":random_in_range_tree_16_a_pine_1_b"),
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_desert", 1),
								(display_message, "@Desert generated!", 0x006495ed),

		],

		[

			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_desert", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":var_5", 1300),
			(val_div, ":var_5", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":var_5"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(position_set_z, 1, ":position_z_1"),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_15_56", 15, 56),
				(store_random_in_range, ":random_in_range_15_56_2", 15, 56),
				(store_random_in_range, ":random_in_range_20_56", 20, 56),
				(store_random_in_range, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a", "spr_valleyRock_flatRounded_small_1", "spr_tree_14_a"),
				(spawn_scene_prop, ":random_in_range_valleyRock_flatRounded_small_1_tree_14_a"),
				(prop_instance_set_scale, reg0, ":random_in_range_15_56", ":random_in_range_15_56_2", ":random_in_range_20_56"),
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_swamp", 1),
					(display_message, "@Swamp generated!", 0x006495ed),
		],

		[

			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_swamp", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":var_5", 480),
			(val_div, ":var_5", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":var_5"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_tree_14_a_tree_8_a", "spr_tree_14_a", "spr_tree_8_a"),
				(spawn_scene_prop, ":random_in_range_tree_14_a_tree_8_a"),
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		(multiplayer_is_server),
			(eq, "$coop_generate_euro_hillside", 1),
			(display_message, "@Euro Hillside generated!", 0x006495ed),

		],

		[
					
			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_euro_hillside", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 300),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(lt, ":position_z_1", 1500),
				(position_set_z, 1, ":position_z_1"),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_55_100", 55, 100),
				(store_random_in_range, ":random_in_range_55_100_2", 55, 100),
				(store_random_in_range, ":random_in_range_55_100_3", 55, 100),
				(store_random_in_range, ":random_in_range_rock1_desert_tree_aa", "spr_rock1", "spr_desert_tree_aa"),
				(spawn_scene_prop, ":random_in_range_rock1_desert_tree_aa"),
				(prop_instance_set_scale, reg0, ":random_in_range_55_100", ":random_in_range_55_100_2", ":random_in_range_55_100_3"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 500),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(spawn_scene_prop, "spr_seedy_plant_a"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 300),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(lt, ":position_z_1", 1500),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_rock1_desert_tree_aa", "spr_bushes10_a", "spr_bushes10_c"),
				(spawn_scene_prop, ":random_in_range_rock1_desert_tree_aa"),
							
			(try_end)

		]),

		(0.0, 0.0, ti_once,
		[
			(eq, "$coop_generate_desertv3", 1),
			(multiplayer_is_server),
							(display_message, "@Desertv3 generated!", 0x006495ed),

		],

		[
							
			(set_fixed_point_multiplier, 100),
			(assign, "$coop_generate_desertv3", 0),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 900),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_seedy_plant_a_palm_aa", "spr_seedy_plant_a", "spr_palm_aa"),
				(spawn_scene_prop, ":random_in_range_seedy_plant_a_palm_aa"),
			(try_end),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 400),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(position_get_z, ":position_z_1", 1),
				(ge, ":position_z_1", 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_seedy_plant_a_palm_aa", "spr_palm_aa", "spr_valleyRock_flatRounded_small_1"),
				(spawn_scene_prop, ":random_in_range_seedy_plant_a_palm_aa"),

			(try_end)
			
		]),

		(0.0, 0.0, ti_once,
		[
(multiplayer_is_server),
			(ge, "$coop_generate_snow", 1)
		],

		[
			(set_fixed_point_multiplier, 100),
			(get_scene_boundaries, 1, 0),
			(position_get_x, ":position_x_0", 0),
			(position_get_y, ":position_y_0", 0),
			(position_get_x, ":position_x_1", 1),
			(position_get_y, ":position_y_1", 1),
			(val_div, ":position_x_0", 2),
			(val_div, ":position_y_0", 2),
			(val_max, "$coop_generate_reduction", 1),
			(assign, ":value", 300),
			(display_message, "@Lite Snow generated!", 0x006495ed),
			(try_begin),
			 				(store_random_in_range, ":random_in_range_1_3", 1, 3),
							(try_begin),
				(eq, "$coop_generate_snow", ":random_in_range_1_3"),
				(assign, ":value", 500),
				(display_message, "@Heavy Snow Generated!", 0x006495ed),
			(try_end),
			(try_end),
			(assign, "$coop_generate_snow", 0),
			(val_div, ":value", "$coop_generate_reduction"),
			(try_for_range, reg10, 0, ":value"),
				(store_random_in_range, ":random_in_range_position_x_1_position_x_0", ":position_x_1", ":position_x_0"),
				(store_random_in_range, ":random_in_range_position_y_1_position_y_0", ":position_y_1", ":position_y_0"),
				(val_mul, ":random_in_range_position_x_1_position_x_0", 2),
				(val_mul, ":random_in_range_position_y_1_position_y_0", 2),
				(position_set_x, 1, ":random_in_range_position_x_1_position_x_0"),
				(position_set_y, 1, ":random_in_range_position_y_1_position_y_0"),
				(position_set_z_to_ground_level, 1),
				(store_random_in_range, ":random_in_range_0_360", 0, 360),
				(position_rotate_z, 1, ":random_in_range_0_360"),
				(set_spawn_position, 1),
				(store_random_in_range, ":random_in_range_tree_snowy_a_test_helmet", "spr_tree_snowy_a", "spr_test_helmet"),
				(spawn_scene_prop, ":random_in_range_tree_snowy_a_test_helmet"),
			(try_end)
			#])
			]),
			
			
			#Doghotel Begin
#			    (ti_before_mission_start, 0, 0, 
#    [],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (assign, ":var0", 0),
#      (try_begin),
#        (neq, "$g_doghotel_version_id", 3),
#        (assign, ":var0", 1),
#      (try_end),
#      (call_script, "script_doghotel_initialize_bot_globals", ":var0"),
#    ]),
#
#    (0.5, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_special_actions"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_distance_calculations"),
#      (call_script, "script_doghotel_combat_loop"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (key_clicked, 63),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (try_begin),
#        (neg|is_presentation_active, "prsnt_doghotel_configure"),
#        (try_begin),
#          (neg|game_in_multiplayer_mode),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (else_try),
#          (game_in_multiplayer_mode),
#          (eq, "$g_doghotel_multiplayer_brainy_bots_installed_on_server", 1),
#          (multiplayer_get_my_player, ":var0"),
#          (player_is_admin, ":var0"),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (try_end),
#      (try_end),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (gt, "$g_doghotel_prsnt_configure_close", 0),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (call_script, "script_doghotel_configure_close"),
#    ]),
#			
#			
#	(ti_before_mission_start, 0, ti_once, 
#    [],
#    [
#      (multiplayer_is_server),
#      (call_script, "script_doghotel_initialize_mp_globals", 0),
#    ]),
#
#    (60, 0, 0, 
#    [],
#    [
#      (multiplayer_is_server),
#      (val_add, "$g_doghotel_brainy_message_timer", 1),
#      (try_begin),
#        (gt, "$g_doghotel_brainy_message_interval", 1),
#        (ge, "$g_doghotel_brainy_message_timer", "$g_doghotel_brainy_message_interval"),
#        (assign, "$g_doghotel_brainy_message_timer", 0),
#        (str_store_string, s1, "str_doghotel_brainy_bots_server_message"),
#        (call_script, "script_doghotel_server_message"),
#      (try_end),
#    ]),
#
#    (0.5, 0, 0, 
#    [
#      (eq, "$g_doghotel_anti_autoblock", 1),
#      (server_get_control_block_dir, ":var0"),
#      (eq, ":var0", 1),
#    ],
#    [
#      (multiplayer_is_server),
#      (server_set_control_block_dir, 1),
#    ]),
			
			#Doghotel end
			]# + crouching_triggers
			),

	#END AI Crouching Code
	
#		(-19.0, 0.0, 0.0,
#		[],

#		[
#			(assign, "$enable_deahtcam", 1),
#			(assign, "$auxilary_player_active", 0),
#			(eq, "$use_player_auxiliary", 1),
#			(assign, "$g_move_heroes", 1),
#			(party_clear, "p_temp_casualties_3"),
#			(call_script, "script_party_add_party", "p_temp_casualties_3", "p_main_party"),
#			(set_player_troop, "trp_player"),
#			(assign, "$enable_deahtcam", 0)
#		]),

#		(5.0, 0.0, 0.0,
#		[
#			(eq, "$use_player_auxiliary", 1),
#			(eq, "$enable_deahtcam", 0),
#			(get_player_agent_no, ":player_agent_no"),
#			(neg|agent_is_alive, ":player_agent_no")
#		],

#		[
#			(set_fixed_point_multiplier, 100),
#			(get_player_agent_no, ":player_agent_no"),
#			(agent_get_team, ":team_player_agent_no", ":player_agent_no"),
#			(agent_get_division, ":division_player_agent_no", ":player_agent_no"),
#			(assign, ":value", 0),
#			(try_for_agents, ":var_5"),
#				(eq, ":value", 0),
#				(agent_is_human, ":var_5"),
#				(agent_is_alive, ":var_5"),
#				(agent_get_team, ":team_var_5", ":var_5"),
#				(agent_get_party_id, ":party_id_var_5", ":var_5"),
#				(eq, ":party_id_var_5", "p_main_party"),
#				(agent_get_division, ":division_player_agent_no_2", ":player_agent_no"),
#				(agent_get_group, ":group_player_agent_no", ":player_agent_no"),
#				(eq, ":team_player_agent_no", ":team_var_5"),
#				(eq, ":division_player_agent_no", ":division_player_agent_no_2"),
#				(agent_get_troop_id, ":troop_id_var_5", ":var_5"),
#				(neg|is_between, ":troop_id_var_5", "trp_npc1", "trp_kingdom_2_pretender"),
#				(set_player_troop, ":troop_id_var_5"),
#				(store_agent_hit_points, ":agent_hit_points_var_5_1", ":var_5", 1),
#				(agent_get_position, 1, ":var_5"),
#				(position_set_z, 1, -2000),
#				(position_set_x, 1, 0),
#				(position_set_y, 1, 0),
#				(agent_get_position, 0, ":var_5"),
#				(set_spawn_position, 0),
#				(agent_get_horse, ":horse_var_5", ":var_5"),
#				(try_begin),
#					(gt, ":horse_var_5", 0),
#					(agent_set_position, ":horse_var_5", 1),
#					(remove_agent, ":horse_var_5"),
#				(try_end),
#				(agent_set_position, ":var_5", 1),
#				(agent_set_slot, ":var_5", 100, 1),
#				(agent_get_slot, ":var_5_102", ":var_5", 102),
#				(remove_agent, ":var_5"),
#				(spawn_agent, ":troop_id_var_5"),
#				(assign, ":player_agent_no", reg0),
#				(agent_set_slot, ":player_agent_no", 102, ":var_5_102"),
#				(agent_set_team, ":player_agent_no", ":team_player_agent_no"),
#				(agent_set_hit_points, ":player_agent_no", ":agent_hit_points_var_5_1", 1),
#				(agent_set_group, ":player_agent_no", ":group_player_agent_no"),
#				(agent_set_slot, ":player_agent_no", 100, 2),
#				(agent_set_slot, ":player_agent_no", 101, ":troop_id_var_5"),
#				(try_begin),
#					(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
#					(gt, ":horse_player_agent_no", 0),
#					(lt, ":horse_var_5", 0),
#					(agent_set_position, ":horse_player_agent_no", 1),
#					(remove_agent, ":horse_player_agent_no"),
#				(try_end),
#				(set_player_troop, "trp_player"),
#				(assign, ":value", 1),
#				(assign, "$auxilary_player_active", 1),
#			(try_end),
#			(eq, ":value", 0),
			#BACKUP BEGIN Before Crouching AI V0.999H
#			(assign, "$enable_deahtcam", 1)
#		])
#	]),
#BACKUP BEFORE CROUCHING AI END
#			(assign, "$enable_deahtcam", 1)
#		])
		
		#Begin AI Crouching Code



#################  
#COOP Siege battles simply lack the following: Spear in position, generate terrain, and spearwall compared to the field battles, you may copy almost everything else but these 
#(excluding the new stuff you may add which may not be compatible, please only add things after additional triggers for sieges.)
    (
    "coop_siege",mtf_battle_mode,-1, #siege
    "You lead your men to battle.",
    [
      (0,mtef_visitor_source|mtef_team_1,af_override_horse,aif_start_alarmed,1,[]),
      (1,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (2,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (3,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (4,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (5,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (6,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (7,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),

      (8,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (9,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (10,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (11,mtef_visitor_source|mtef_team_0|mtef_no_auto_reset,af_override_horse,aif_start_alarmed,1,[]),
      (12,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (13,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (14,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (15,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (16,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (17,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (18,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (19,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (20,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (21,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (22,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (23,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (24,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (25,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (26,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (27,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (28,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (29,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (30,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (31,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (32,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (33,mtef_visitor_source|mtef_team_1|mtef_no_auto_reset,0,aif_start_alarmed,1,[]),
      (34,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (35,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (36,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (37,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (38,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (39,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (40,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (41,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (42,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (43,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (44,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (45,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (46,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),
      (47,mtef_visitor_source|mtef_team_0,af_override_horse,aif_start_alarmed,1,[]),

      (48,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (49,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (50,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (51,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (52,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (53,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (54,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (55,mtef_visitor_source,0,aif_start_alarmed,1,[]),

      (56,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (57,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (58,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (59,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (60,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (61,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (62,mtef_visitor_source,0,aif_start_alarmed,1,[]),
      (63,mtef_visitor_source,0,aif_start_alarmed,1,[]),
     ],
    [

      coop_server_check_polls,
      coop_server_reduce_damage,
      coop_respawn_as_bot,
      coop_store_respawn_as_bot,


#mordr does not work in MP = SCRIPT ERROR ON OPCODE 1785: Invalid Group ID: 1;
#      common_battle_order_panel,
#      common_battle_order_panel_tick,


      (ti_server_player_joined, 0, 0, [],
       [
        (store_trigger_param_1, ":player_no"),
       # (call_script, "script_multiplayer_server_player_joined_common", ":player_no"), #dont clear slots

        (call_script, "script_multiplayer_send_initial_information", ":player_no"),
        (call_script, "script_coop_server_player_joined_common", ":player_no"),    #need to call every round

        # Dedicated-server battle bootstrap (mirror of mt_coop_battle's join
        # trigger). The first join after the scene restart into this template
        # loads the siege data and, once loaded, enables agent spawning and
        # marks the battle started. Without this, round 1 never sets
        # ready_for_spawning_agent (trigger below only covers later rounds), so
        # neither bots nor players ever spawn.
        (try_begin),
          (eq, "$coop_battle_state", coop_battle_state_none),
          (call_script, "script_coop_on_admin_panel_load"),
          (try_begin),
            (eq, "$coop_battle_state", coop_battle_state_setup_mp),
            (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
            (assign, "$coop_battle_started", 1),
          (try_end),
        (try_end),

        # Assign each real player (player 0 is the dedicated server) to the
        # attacker team with their campaign troop + persisted character.
        (try_begin),
          (gt, ":player_no", 0),
          (player_set_team_no, ":player_no", "$attacker_team"),
          (store_add, ":troop_no", multiplayer_campaign_player_troops_begin, ":player_no"),
          (player_set_troop_id, ":player_no", ":troop_no"),
          (call_script, "script_coop_load_character", ":player_no"),
        (try_end),
       ]),

      (ti_before_mission_start, 0, 0, [],
       [
         (assign, "$g_multiplayer_game_type", multiplayer_game_type_coop_siege),
     #    (call_script, "script_multiplayer_server_before_mission_start_common"), #dont set time of day, reset commanded troops
     #    (call_script, "script_multiplayer_init_mission_variables"), #dont reset commanded troop type


          (call_script, "script_initialize_banner_info"),
          (call_script, "script_coop_init_mission_variables"),

         (assign, "$g_waiting_for_confirmation_to_terminate", 0),
         (assign, "$g_round_ended", 0),
         (assign, "$coop_winner_team", -1),
         (assign, "$coop_battle_started", 0),
         (assign, "$coop_use_belfry", 0),
         (assign, "$coop_attacker_is_on_wall", 0),

         # Clear per-round spawn flags so players spawn at the start of every
         # siege round (each round is a fresh start_multiplayer_mission).
         # get_max_players returns the engine's full slot capacity, so guard
         # with player_is_active to skip unused/invalid ids.
         (get_max_players, ":num_players"),
         (try_for_range, ":pl_no", 1, ":num_players"),
           (player_is_active, ":pl_no"),
           (player_set_slot, ":pl_no", slot_player_spawned_this_round, 0),
         (try_end),
         (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),

          #set_weather
         (scene_set_day_time, "$coop_time_of_day"),
	       (set_global_cloud_amount, "$coop_cloud"),
	       (set_global_haze_amount, "$coop_haze"),
          #removed set_fog_distance needs correct color in 1.143
         # (try_begin),
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (set_global_haze_amount, 95), #remove sunlight
         # (try_end),

         (assign, ":rain_amount", "$coop_cloud"),
         (assign, ":rain_type", "$coop_rain"),
         (try_begin),
           (lt, ":rain_amount", 75), #less than = no rain
           (assign, ":rain_amount", 0),
           (assign, ":rain_type", 0),
         (try_end),
         (set_rain, ":rain_type" , ":rain_amount"), #1=rain 2=snow

#common_battle_mission_start = 
         (try_begin),
           (gt, "$coop_castle_banner", 0),
           (replace_scene_props, banner_scene_props_begin, "$coop_castle_banner"),
         (else_try),
           (replace_scene_props, banner_scene_props_begin, "spr_empty"),
         (try_end),

         ]),

      (ti_after_mission_start, 0, 0, [], 
       [

        (call_script, "script_initialize_all_scene_prop_slots"),
        (call_script, "script_multiplayer_move_moveable_objects_initial_positions"),
        (assign, "$g_multiplayer_bot_type_1_wanted", 1),#set player wants all troops in party (host will override clients)#this should be optional

       #removed set_fog_distance needs correct color in 1.143
         # (try_begin),#limit fog
           # (gt, "$coop_cloud", 65), #if cloud cover
           # (lt,  "$coop_haze", 91), #not heavy fog
           # (try_begin),
             # (eq,  "$coop_rain", 2), #if snow
             # (set_fog_distance, 200), #set fog closer
           # (else_try),
             # (set_fog_distance, 600),
           # (try_end),
         # (try_end),

        (try_begin),
          (neg|multiplayer_is_server),
          #these lines are done in only clients at start of each new round.
          (call_script, "script_multiplayer_initialize_belfry_wheel_rotations"),
          (call_script, "script_initialize_objects_clients"),
        (try_end),  

        (try_begin),
          (multiplayer_is_server),
          (start_presentation, "prsnt_coop_start_battle"),
        (else_try),
          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          (player_is_admin, ":my_player_no"),
          (start_presentation, "prsnt_coop_start_battle"),
        (try_end),

        (try_begin),
          (multiplayer_is_server),
          (assign, "$coop_reinforce_size", 10), #size of reinforcement wave
          (assign, "$coop_reinforce", 1),
          (assign, "$coop_alive_team1", 0),#store count for reinforcement spawn
          (assign, "$coop_alive_team2", 0),



          (entry_point_get_position, pos26, 10),
          (entry_point_get_position, pos31, 0),

          (try_begin),
            (this_or_next|eq, "$coop_round", coop_round_battle),
            (eq, "$coop_round", coop_round_town_street),

            (assign, ":attacker", 0),
            (try_begin),
              (eq, "$coop_round", coop_round_town_street),
              (assign, ":defender", 23),
            (else_try),
              (assign, ":defender", 15),
            (try_end),
 
            (entry_point_get_position, pos2, ":attacker"),
            (entry_point_get_position, pos3, ":defender"),
            (position_set_z_to_ground_level, pos2),
            (position_set_z_to_ground_level, pos3),

            (set_spawn_position, pos2),
            (spawn_scene_prop, "spr_coop_inventory", 0),   
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_siege_player_attack),
              (assign, "$coop_inventory_box", reg0),
            (try_end),

            (set_spawn_position, pos3),
            (spawn_scene_prop, "spr_coop_inventory", 0),
            (try_begin),
              (eq, "$coop_battle_type", coop_battle_type_siege_player_defend),
              (assign, "$coop_inventory_box", reg0),
            (try_end),
          (try_end),
        (try_end),


          ]),

      #in later rounds delay so clients can join (can use start battle option to skip)
      (5, 10, ti_once,[
       (multiplayer_is_server),
        (this_or_next|eq, "$coop_round", coop_round_town_street),
        (eq, "$coop_round", coop_round_castle_hall),
        ], 
       [
        (eq, "$coop_battle_started", 0),
        (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
        ]),

      # Spawn connected players as attackers (one life per round). Bots are
      # handled by the reinforcement trigger below; players need an explicit
      # spawn on the dedicated server (mirror of mt_coop_battle).
      (1, 0, 0,
       [(multiplayer_is_server),
        (eq, "$coop_battle_started", 1),
       ],
       [
        (get_max_players, ":num_players"),
        (try_for_range, ":player_no", 1, ":num_players"),
          (player_is_active, ":player_no"),
          (neg|player_is_busy_with_menus, ":player_no"),
          (player_slot_eq, ":player_no", slot_player_spawned_this_round, 0),
          (player_get_agent_id, ":agent_id", ":player_no"),
          (lt, ":agent_id", 0),
          (player_get_team_no, ":team", ":player_no"),
          (lt, ":team", multi_team_spectator),
          (player_get_troop_id, ":troop", ":player_no"),
          (ge, ":troop", 0),
          (player_spawn_new_agent, ":player_no", 0),
          (player_set_slot, ":player_no", slot_player_spawned_this_round, 1),
        (try_end),
       ]),


#multiplayer_server_spawn_bots
      (0, 0, 0, [],
       [
        (multiplayer_is_server),
        (eq, "$g_multiplayer_ready_for_spawning_agent", 1),


        #get battle size
        (assign, ":battle_size", "$coop_battle_size"),
        (try_begin), 
          (eq, "$coop_round", coop_round_castle_hall),
          (val_div, ":battle_size", 4),
          (val_max, ":battle_size", coop_min_battle_size),
          (assign, "$coop_reinforce_size",4),
        (try_end),

        #regulate troop spawn
        (store_add, ":total_bots", "$coop_alive_team1", "$coop_alive_team2"),
        (store_sub, ":reinforce_bots", ":battle_size", "$coop_reinforce_size"),#when less troops than battle size
        (try_begin),
          (this_or_next|eq, "$coop_round", coop_round_castle_hall),
          (le, ":total_bots", ":reinforce_bots"), 
          (assign, "$coop_reinforce", 1), #need global var so not cleared
        (try_end),
        (try_begin),
          (ge, ":total_bots", ":battle_size"), 
          (assign, "$coop_reinforce", 0),
        (try_end),


        (try_begin),
          #pick team by size
          (store_add, ":total_req", "$coop_num_bots_team_1", "$coop_num_bots_team_2"),
          (gt, ":total_req", 0),

          (assign, ":alive_team1", "$coop_alive_team1"),
          (assign, ":alive_team2", "$coop_alive_team2"),
          (val_max, ":alive_team1", 1),
          (val_mul, ":alive_team2", 1000),
          (store_div, ":ratio_current", ":alive_team2", ":alive_team1"), 


          (try_begin),
            (this_or_next|eq, "$coop_num_bots_team_2", 0), #skip ratio if other team has no reinforcements
            (ge, ":ratio_current", "$coop_team_ratio"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),#add to team 1
          (else_try),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),#add to team 2
          (try_end),


          #if one team is almost out of troops, choose that team
          (try_begin),
            (le, "$coop_alive_team1", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_1", 0),
            (assign, ":selected_team", 0),
          (else_try),
            (le, "$coop_alive_team2", "$coop_reinforce_size"),
            (gt, "$coop_num_bots_team_2", 0),
            (assign, ":selected_team", 1),
          (try_end),

          (try_begin), #server stop reinforcing and be ready for next scene
            # Single-round dedicated siege: no later stages, so don't hold
            # back street/hall reserves -- the full garrison defends the wall.
            (neg|multiplayer_is_dedicated_server),
            (this_or_next|eq, "$coop_round", coop_round_battle),
            (eq, "$coop_round", coop_round_town_street),


            (try_begin),
              (eq, "$defender_team", 0),
              (assign, ":defender_reserves", "$coop_num_bots_team_1"), 
              (assign, ":defender_original_size", "$coop_team_1_troop_num"), 
            (else_try),
              (eq, "$defender_team", 1),
              (assign, ":defender_reserves", "$coop_num_bots_team_2"),
              (assign, ":defender_original_size", "$coop_team_2_troop_num"),  
            (try_end),

            (assign, ":reserves", coop_reserves_hall), #number to reserve for hall battle
            (try_begin),
              (gt, "$coop_street_scene", 0),
              (eq, "$coop_round", coop_round_battle),
              (assign, ":reserves", coop_reserves_street), #if street battle is comming
            (try_end),
            (ge, ":defender_original_size", ":reserves"),
            (le, ":defender_reserves", ":reserves"),
            (val_add, "$coop_round", 1),

          (try_end), 

          #if defenders withdraw, finish spawning attackers
          (try_begin),
            (this_or_next|eq, "$coop_round", coop_round_stop_reinforcing_wall),
            (eq, "$coop_round", coop_round_stop_reinforcing_street),
            (try_begin),
              (eq, "$attacker_team", 0),
              (gt, "$coop_num_bots_team_1", 0),
              (assign, ":selected_team", 0),
            (else_try),
              (eq, "$attacker_team", 1),
              (gt, "$coop_num_bots_team_2", 0),
              (assign, ":selected_team", 1),
            (try_end),

            (try_begin),
              (eq, "$defender_team", 0),
              (eq, "$coop_alive_team1", 0),
              (assign, "$coop_reinforce", 0),
            (else_try),
              (eq, "$defender_team", 1),
              (eq, "$coop_alive_team2", 0),
              (assign, "$coop_reinforce", 0),
            (try_end),
            (eq, "$defender_team", ":selected_team"),
            (assign, "$coop_reinforce", 0),
          (try_end),


          (eq, "$coop_reinforce", 1), #ready for reinforcements
          (call_script, "script_coop_find_bot_troop_for_spawn", ":selected_team"),
          (assign, ":selected_troop", reg0),
#SPAWN POINTS #######################################

          (try_begin),
            (eq, ":selected_team", "$defender_team"),
            (try_begin),#defender spawn points
              (eq, "$coop_round", coop_round_town_street),
              (store_random_in_range, ":random_point", 23, 29),
              (assign, reg0, ":random_point"),
            (else_try),
              (eq, "$coop_round", coop_round_castle_hall),
              (store_random_in_range, ":random_point", 16, 32),
              (assign, reg0, ":random_point"),
            (else_try),
              (assign, reg0, 15), #defenders are moved to other points after spawning
            (try_end),
          (else_try),#attacker spawn point
            (assign, reg0, 0),
          (try_end),
#############################################
          (store_current_scene, ":cur_scene"),
          (modify_visitors_at_site, ":cur_scene"),
          (add_visitors_to_current_scene, reg0, ":selected_troop", 1, ":selected_team", -1),#don't assign group at spawn
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_begin),
            (eq, ":selected_team", 0),
            (val_sub, "$coop_num_bots_team_1", 1),
          (else_try),
            (eq, ":selected_team", 1),
            (val_sub, "$coop_num_bots_team_2", 1),
          (try_end),

        (try_end),   
        ]),
 

      (ti_on_agent_spawn, 0, 0, [],
       [
        (store_trigger_param_1, ":agent_no"),
        (try_begin),
          (eq, "$coop_battle_started", 0),
          (assign, "$coop_battle_started", 1),
        (try_end),

          (try_begin), #add alive team counts for server and client
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (try_begin),
              (eq, ":agent_team", 0),
              (val_add, "$coop_alive_team1", 1),
            (else_try),
              (eq, ":agent_team", 1),
              (val_add, "$coop_alive_team2", 1),
            (try_end),
          (try_end),

        (try_begin), #move attackers closer to spawn point
          (multiplayer_is_server),
            (agent_is_human, ":agent_no"),
            (agent_get_team, ":agent_team", ":agent_no"),
            (agent_get_class, ":agent_class", ":agent_no"),
        #    (agent_get_troop_id, ":script_param_1", ":agent_no"),

            (try_begin),
              (eq, ":agent_team", "$attacker_team"),
              (try_begin),
                (try_begin),
                  (eq, "$coop_round", coop_round_castle_hall),
                  (assign, ":num_row", 2), #2 per row in castle
                (else_try),
                  (eq, "$coop_round", coop_round_town_street),
                  (assign, ":num_row", 4), #4 per row in street
                (else_try),
                  (assign, ":num_row", 20), #20 per row otherwise
                (try_end),
                (val_mul, ":num_row", 50),

                (entry_point_get_position, pos30, 0),
                (get_distance_between_positions, ":dist",pos31,pos30),
                (ge, ":dist", ":num_row"),
                (entry_point_get_position, pos31, 0),
              (try_end),
              # (position_set_z_to_ground_level, pos31),
              (agent_set_position, ":agent_no", pos31),
              (position_move_x, pos31, 50),
            (else_try),
              (eq, ":agent_team", "$defender_team"),
              (eq, "$coop_round", coop_round_battle),

              (try_begin),
          #      (troop_is_guarantee_ranged, ":script_param_1"),
                (eq, ":agent_class", grc_archers),
                (store_random_in_range, ":random_point", 40, 47),
                (entry_point_get_position, pos27, ":random_point"),
                 (try_begin),
                  (eq, "$coop_attacker_is_on_wall", 0), 
                  (agent_set_scripted_destination, ":agent_no", pos27, 0), 
                (try_end),
                (try_begin),
                  #(eq, "$coop_battle_spawn_formation", 1),#when spawn formation is on,  #Envedit Forcing Sieges to use Spawn Formations for spawn points.
                  (position_move_x, pos27, 200),
                  (agent_set_position, ":agent_no", pos27),
                (try_end),

              (else_try),
                (eq, "$coop_attacker_is_on_wall", 0), #before attackers reach wall, move half of defenders to wall
                (entry_point_get_position, pos25, 10),
                (try_begin),
                  # (eq, "$coop_battle_spawn_formation", 1), #when spawn formation is on, 
                  (store_random_in_range, ":random", 0, 2),
                  (eq, ":random", 0),
                  (try_begin),
                    (get_distance_between_positions, ":dist",pos26,pos25),
                    (ge, ":dist", 600), #12 x 50 per row 
                    (entry_point_get_position, pos26, 10),
                  (try_end),
                  (agent_set_position, ":agent_no", pos26),
                  (position_move_x, pos26, 50),
                (try_end),

                (position_move_y, pos25, 100),
                (agent_set_scripted_destination, ":agent_no", pos25, 0),  #keep defenders in castle until attackers reach wall
              (try_end),
            (try_end),

           #check this script for changes, currently only sets g_multiplayer_ready_for_spawning_agent
          # (call_script, "script_multiplayer_server_on_agent_spawn_common", ":agent_no"),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 1),
          (agent_set_slot, ":agent_no", slot_agent_coop_spawn_party, "$coop_agent_party"), #store party of agent
          (call_script, "script_coop_equip_player_agent", ":agent_no"), #ITEM BUG WORKAROUND
        (try_end),
        (agent_set_slot, ":agent_no", slot_agent_coop_banner, "$coop_agent_banner"), #store banner of agent for clients too

        (try_begin),
          (agent_is_human, ":agent_no"),
          (agent_get_troop_id,":script_param_1", ":agent_no"),

      #common_battle_init_banner 
        (call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":agent_no", ":script_param_1"),

        #when client's chosen troop spawns, request control of it
          (eq, ":script_param_1", "$coop_my_troop_no"),

          (multiplayer_get_my_player, ":my_player_no"),
          (ge, ":my_player_no", 0),
          # (player_get_team_no, ":my_team_no", ":my_player_no"),
          (agent_get_team, ":agent_team", ":agent_no"),
          (eq, ":agent_team","$coop_my_team"),

          #change team
          (player_set_team_no, ":my_player_no", "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_team_no, "$coop_my_team"),
          (multiplayer_send_int_to_server, multiplayer_event_change_troop_id, "$coop_my_troop_no"),
        (try_end),
      

         ]),


      (ti_on_agent_killed_or_wounded, 0, 0, [],
       [
         (store_trigger_param_1, ":dead_agent_no"),
         (store_trigger_param_2, ":killer_agent_no"),
###
         (call_script, "script_coop_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
	       (call_script, "script_multiplayer_server_on_agent_killed_or_wounded_common", ":dead_agent_no", ":killer_agent_no"),
     
         (assign, ":number_of_alive_1", 0),
         (assign, ":number_of_alive_2", 0),
          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team, ":cur_agent_team", ":cur_agent"),
            (try_begin),
              (eq, ":cur_agent_team", 0),
              (val_add, ":number_of_alive_1", 1),
            (else_try),
              (eq, ":cur_agent_team", 1),
              (val_add, ":number_of_alive_2", 1),
            (try_end),
          (try_end),
         (assign, "$coop_alive_team1", ":number_of_alive_1"),
         (assign, "$coop_alive_team2", ":number_of_alive_2"),

        (try_begin), #check round end        
          (this_or_next|eq, ":number_of_alive_1", 0),
          (eq, ":number_of_alive_2", 0),
          (try_begin), #assign my initial team value (only used to set color of multiplayer_message_type_round_result_in_battle_mode)
            (multiplayer_get_my_player, ":my_player_no"),
            (ge, ":my_player_no", 0),
            (player_get_team_no, "$coop_my_team", ":my_player_no"),
            (player_get_team_no, "$my_team_at_start_of_round", ":my_player_no"),
            (player_get_agent_id, ":my_agent_id", ":my_player_no"),
            (ge, ":my_agent_id", 0),
            (agent_get_troop_id, "$coop_my_troop_no", ":my_agent_id"),
          (try_end),     

          (try_begin),
            (eq, "$coop_alive_team1", 0),#if team 1 is dead
            (assign, "$coop_winner_team", 1),
            (try_begin),
              (ge, "$coop_num_bots_team_1", coop_reserves_hall), #if loser has reserves, they retreated
              (display_message, "@The defenders retreat!"),
            (try_end),
          (else_try),
            (eq, "$coop_alive_team2", 0),#if team 2 is dead
            (assign, "$coop_winner_team", 0),
            (try_begin),
              (ge, "$coop_num_bots_team_2", coop_reserves_hall), #if loser has reserves, they retreated
              (display_message, "@The defenders retreat!"),
            (try_end),
          (try_end),

          (call_script, "script_show_multiplayer_message", multiplayer_message_type_round_result_in_battle_mode, "$coop_winner_team"), #team 2 is winner 
          (store_mission_timer_a, "$g_round_finish_time"),
          (assign, "$g_round_ended", 1),
        (try_end),
#END BATTLE ##################	
        ]),




#multiplayer_server_check_end_map =
      (1, 0, 0,   #must check this in separate trigger in case no defenders spawn in battle round
       [
        (multiplayer_is_server),
        # Dedicated siege v1 is single-round: the wall battle decides the siege
        # and the end handler below saves results. No street/hall progression.
        (neg|multiplayer_is_dedicated_server),
        (this_or_next|eq, "$coop_round", coop_round_stop_reinforcing_wall),
        (eq, "$coop_round", coop_round_stop_reinforcing_street),
        ],
       [
        (try_begin),
          (try_begin),
            (eq, "$attacker_team", 0),
            (this_or_next|gt, "$coop_alive_team1", 0), 
            (gt, "$coop_num_bots_team_1", 0),#if attacker is not dead continue
            (eq, "$coop_alive_team2", 0),
            (val_add, "$coop_round", 1),
          (else_try),
            (eq, "$attacker_team", 1),
            (this_or_next|gt, "$coop_alive_team2", 0),
            (gt, "$coop_num_bots_team_2", 0), #if attacker is not dead continue
            (eq, "$coop_alive_team1", 0),
            (val_add, "$coop_round", 1),
          (try_end),

          (this_or_next|eq, "$coop_round", coop_round_town_street),
          (eq, "$coop_round", coop_round_castle_hall),
          (try_begin), 
            (eq, "$coop_street_scene", 0),
            (assign, "$coop_round", coop_round_castle_hall), #if no street scene, skip to castle hall
          (try_end),

          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (try_for_agents, ":cur_agent"),
            (agent_is_human, ":cur_agent"),
            (agent_is_alive, ":cur_agent"),
            (agent_get_team ,":cur_team", ":cur_agent"),
            (agent_get_troop_id, ":agent_troop_id", ":cur_agent"),
            #replace troop in temp spawn party
            (agent_get_slot, ":agent_party",":cur_agent", slot_agent_coop_spawn_party),
            (party_add_members, ":agent_party", ":agent_troop_id", 1),

            (try_begin), #save health for round 2
              (troop_is_hero, ":agent_troop_id"),
              (store_agent_hit_points, ":agent_hit_points", ":cur_agent"),
              (troop_set_health, ":agent_troop_id", ":agent_hit_points"),

              #store items from agents
              (call_script, "script_coop_player_agent_save_items", ":cur_agent"),
            (try_end),

            (try_begin), #replace reserves count
              (eq, ":cur_team", 0),
              (val_add, "$coop_num_bots_team_1", 1),
            (else_try),
              (eq, ":cur_team", 1),
              (val_add, "$coop_num_bots_team_2", 1),
            (try_end),
          (try_end),

          #sort troops of spawn parties
          (store_add, ":last_party", coop_temp_party_enemy_begin, "$coop_no_enemy_parties"), 
          (try_for_range, ":var_6", coop_temp_party_enemy_begin, ":last_party"),
            (call_script, "script_coop_sort_party", ":var_6"),
          (try_end),

          (store_add, ":last_party", coop_temp_party_ally_begin, "$coop_no_ally_parties"), 
          (try_for_range, ":var_6", coop_temp_party_ally_begin, ":last_party"),
            (call_script, "script_coop_sort_party", ":var_6"),
          (try_end),

          (try_begin), 
            (eq, "$coop_round", coop_round_town_street),
            (assign, ":next_scene", "$coop_street_scene"),
          (else_try),
            (eq, "$coop_round", coop_round_castle_hall),
            (assign, ":next_scene", "$coop_castle_scene"),
          (try_end),
          (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
          (start_multiplayer_mission, reg0, ":next_scene", 1),
        (try_end),
        ]),



#delay after battle to quit
      # Listen-server path: save + finish mission after round end.
      # Gated by skip_menu so the host's admin UI opts in. Dedicated servers
      # use the KICK trigger above, which inlines the save before restart.
      (3, 4, ti_once, [(eq, "$g_round_ended", 1)],
       [
        (try_begin),
          (multiplayer_is_server),
          (neg|multiplayer_is_dedicated_server),
          (eq, "$coop_skip_menu", 1),
          (eq, "$coop_battle_started", 1),
          (store_add, ":total_team1", "$coop_alive_team1", "$coop_num_bots_team_1"), #if one team is defeated
          (store_add, ":total_team2", "$coop_alive_team2", "$coop_num_bots_team_2"),
          (this_or_next|eq, ":total_team1", 0),
          (eq, ":total_team2", 0),

          (call_script, "script_coop_copy_parties_to_file_mp"),
          (neg|multiplayer_is_dedicated_server),
		  #####MUSICBOX
		  (play_track, "track_reset_silence", 1), #Simple patch for listen server hosts - stops the music.
		  ##(stop_all_sounds, 1), #Simple patch for listen server hosts - stops the music.
          (finish_mission),
        (try_end),
        ]),

      # Dedicated battle server end-of-siege handler (mirror of the field
      # mt_coop_battle dedicated handler). Single-round siege: the wall battle
      # result decides the siege, so this fires on the first round end (the
      # street/hall round-advance trigger above is disabled on dedicated).
      (10, 0, ti_once, [(eq, "$g_round_ended", 1)],
       [
        (try_begin),
          (multiplayer_is_server),
          (multiplayer_is_dedicated_server),
          (eq, "$coop_battle_started", 1),

          # Save results (writes @coop_battle dict and signals the DLL via
          # $coop_battle_started = -1 after dict_save).
          (call_script, "script_coop_copy_parties_to_file_mp"),

          (get_max_players, ":num_players"),
          (try_for_range, ":player_no", 1, ":num_players"),
            (player_is_active, ":player_no"),
            (kick_player, ":player_no"),
          (try_end),

          (assign, "$g_round_ended", 0),
          (assign, "$coop_battle_state", coop_battle_state_none),
          (assign, "$coop_scene_loaded", 0),
          (assign, "$g_multiplayer_ready_for_spawning_agent", 0),

          (call_script, "script_game_multiplayer_get_game_type_mission_template", "$g_multiplayer_game_type"),
          (start_multiplayer_mission, reg0, "scn_random_multi_plain_medium", 1),
          (display_message, "@Siege complete -- battle server reset for next battle."),
        (try_end),
        ]),

       
      (ti_tab_pressed, 0, 0, [],
       [
         (try_begin),
           (assign, "$g_multiplayer_stats_chart_opened_manually", 1),
           (start_presentation, "prsnt_coop_stats_chart"),
         (try_end),
         ]),


      (ti_escape_pressed, 0, 0, [],
       [
         (neg|is_presentation_active, "prsnt_coop_escape_menu"),
         (neg|is_presentation_active, "prsnt_coop_stats_chart"),
         (eq, "$g_waiting_for_confirmation_to_terminate", 0),
         (start_presentation, "prsnt_coop_escape_menu"),
         ]),

#multiplayer_server_manage_bots
      (3, 0, 0, [], 
       [
        (multiplayer_is_server),
        (try_for_agents, ":cur_agent"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (agent_get_team, ":agent_team", ":cur_agent"),
          (call_script, "script_coop_change_leader_of_bot", ":cur_agent"),

          (try_begin),
            (eq, ":agent_team", "$attacker_team"),
            (eq, "$coop_attacker_is_on_wall", 0),
            (agent_get_position, pos2, ":cur_agent"),
            (entry_point_get_position, pos25, 10),
            (get_distance_between_positions, ":dist",pos2,pos25),
            (lt, ":dist", 500),
            (assign, "$coop_attacker_is_on_wall", 1),
            (display_message, "@The attackers have reached the wall"),
          (try_end),

          (agent_get_group, ":agent_group", ":cur_agent"),
          (try_begin),
            (this_or_next|eq, "$belfry_positioned", 3),#if belfry is positioned
            (eq, "$coop_attacker_is_on_wall", 1),
            (agent_clear_scripted_mode, ":cur_agent"),
          (else_try),
            (this_or_next|eq, "$belfry_positioned", 2),#if belfry is almost positioned
            (ge, ":agent_group", 0),#player commanded
            (eq, ":agent_team", "$attacker_team"),
            (agent_slot_eq,":cur_agent",slot_agent_target_x_pos, 0),
            (agent_clear_scripted_mode, ":cur_agent"),
          (try_end),

#common_siege_attacker_do_not_stall,
          (try_begin),
            (eq, ":agent_team", "$attacker_team"),
            (agent_ai_set_always_attack_in_melee, ":cur_agent", 1),
          (try_end),
        (try_end),

        (get_max_players, ":num_players"),
        (try_for_range, ":player_no", 1, ":num_players"), #0 is server so starting from 1
          (player_is_active, ":player_no"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 1,  "$coop_num_bots_team_1"),
          (multiplayer_send_3_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_event_return_num_reserves, 2,  "$coop_num_bots_team_2"),
        (try_end),

        ]),



#common_siege_refill_ammo = 
      (120, 0, 0, [(multiplayer_is_server)],
      [#refill ammo of defenders every two minutes.
        (try_for_agents,":cur_agent"),
          (agent_is_alive, ":cur_agent"),
          (agent_get_team, ":agent_team", ":cur_agent"),
          (eq, ":agent_team", "$defender_team"),
          (agent_is_non_player, ":cur_agent"),
          (agent_is_human, ":cur_agent"),
          (agent_refill_ammo, ":cur_agent"),
        (try_end),
      ]),



#line up attacking archers (not working) hard to find good position
#      (3, 0, 0,[        
#        (eq, "$coop_round", coop_round_battle),
#        ], 
#        [ 
#        (entry_point_get_position, pos4, 15), #top of ladder
#        (position_move_y, pos4, 5000), 
#        (position_move_x, pos4, -2000), 
#        (call_script, "script_coop_form_line", pos4, "$attacker_team", grc_archers, 200, 100, 3, 0), #(pos, team, dist to row, dist to troop, rows)
#      ]),


#common_siege_init_ai_and_belfry,
      (0, 0, ti_once, [], 
       [
         (try_begin),
           (multiplayer_is_server),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 1),
           (try_end),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 1),
           (try_end),
          #call coop script
           (call_script, "script_coop_move_belfries_to_their_first_entry_point", "spr_belfry_a"),
           (call_script, "script_coop_move_belfries_to_their_first_entry_point", "spr_belfry_b"),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_number_of_agents_pushing, 0),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_next_entry_point_id, 0),
           (try_end),
         
           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_number_of_agents_pushing, 0),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_next_entry_point_id, 0),
           (try_end),

           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_a"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_a", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 0),
             (assign, "$coop_use_belfry", 1), #
           (try_end),

           (scene_prop_get_num_instances, ":num_belfries", "spr_belfry_b"),
           (try_for_range, ":belfry_no", 0, ":num_belfries"),
             (scene_prop_get_instance, ":belfry_scene_prop_id", "spr_belfry_b", ":belfry_no"),
             (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 0),
             (assign, "$coop_use_belfry", 1), #
           (try_end),
           (assign, "$belfry_positioned", 0),

         (try_end),
        ]),


#multiplayer_server_check_belfry_movement
      (0, 0, 0, [ ],
       [
    (multiplayer_is_server),
    (eq, "$coop_use_belfry", 1),
	#(get_max_players, ":num_players"), #New
    (set_fixed_point_multiplier, 100),

    (try_for_range, ":belfry_kind", 0, 2),
      (try_begin),
        (eq, ":belfry_kind", 0),
        (assign, ":belfry_body_scene_prop", "spr_belfry_a"),
      (else_try),
        (assign, ":belfry_body_scene_prop", "spr_belfry_b"),
      (try_end),
    
      (scene_prop_get_num_instances, ":num_belfries", ":belfry_body_scene_prop"),

      (try_for_range, ":belfry_no", 0, ":num_belfries"),
        (scene_prop_get_instance, ":belfry_scene_prop_id", ":belfry_body_scene_prop", ":belfry_no"),
        (prop_instance_get_position, pos1, ":belfry_scene_prop_id"), #pos1 holds position of current belfry 
        (prop_instance_get_starting_position, pos11, ":belfry_scene_prop_id"),

#common_siege_assign_men_to_belfry = 
        (call_script, "script_cf_coop_siege_assign_men_to_belfry",  pos1),

#        (store_add, ":belfry_first_entry_point_id", 11, ":belfry_no"), #belfry entry points are 110..119 and 120..129 and 130..139
        (store_add, ":belfry_first_entry_point_id", 5, ":belfry_no"), #belfry entry points are 50..55 and 60..65 and 70..75
        (try_begin),
          (eq, ":belfry_kind", 1),
          (scene_prop_get_num_instances, ":number_of_belfry_a", "spr_belfry_a"),
          (val_add, ":belfry_first_entry_point_id", ":number_of_belfry_a"),
        (try_end),        
                
        (val_mul, ":belfry_first_entry_point_id", 10),
#        (store_add, ":belfry_last_entry_point_id", ":belfry_first_entry_point_id", 10),#number points for each belfry
        (store_add, ":belfry_last_entry_point_id", ":belfry_first_entry_point_id", 5),#number points for each belfry
    
        (try_for_range, ":entry_point_id", ":belfry_first_entry_point_id", ":belfry_last_entry_point_id"),
          (entry_point_is_auto_generated, ":entry_point_id"),
          (assign, ":belfry_last_entry_point_id", ":entry_point_id"),
        (try_end),
        
        (assign, ":belfry_last_entry_point_id_plus_one", ":belfry_last_entry_point_id"),
        (val_sub, ":belfry_last_entry_point_id", 1),
        (assign, reg0, ":belfry_last_entry_point_id"),
        (neg|entry_point_is_auto_generated, ":belfry_last_entry_point_id"),

        (try_begin),
          (get_sq_distance_between_positions, ":dist_between_belfry_and_its_destination", pos1, pos11),

          (ge, ":dist_between_belfry_and_its_destination", 4), #0.2 * 0.2 * 100 = 4 (if distance between belfry and its destination already less than 20cm no need to move it anymore)
			
          # coop check when belfry is close
          (try_begin),
            (lt, ":dist_between_belfry_and_its_destination", 1000),
            (assign, "$belfry_positioned", 2), 
          (try_end),

          (try_begin),
            (lt, "$belfry_positioned", 2), 
            (copy_position, pos4, pos1),
            (position_move_y, pos4, -2400),
            (position_move_x, pos4, -800),
            (call_script, "script_coop_form_line", pos4, "$attacker_team", grc_everyone, 200, 100, 3, 0), #(pos, team, dist to row, dist to troop, rows)
          (try_end),


          (assign, ":max_dist_between_entry_point_and_belfry_destination", -1), #should be lower than 0 to allow belfry to go last entry point
          (assign, ":belfry_next_entry_point_id", -1),
          (try_for_range, ":entry_point_id", ":belfry_first_entry_point_id", ":belfry_last_entry_point_id_plus_one"),
            (entry_point_get_position, pos4, ":entry_point_id"),
            (get_sq_distance_between_positions, ":dist_between_entry_point_and_belfry_destination", pos11, pos4),
            (lt, ":dist_between_entry_point_and_belfry_destination", ":dist_between_belfry_and_its_destination"),
            (gt, ":dist_between_entry_point_and_belfry_destination", ":max_dist_between_entry_point_and_belfry_destination"),
            (assign, ":max_dist_between_entry_point_and_belfry_destination", ":dist_between_entry_point_and_belfry_destination"),
            (assign, ":belfry_next_entry_point_id", ":entry_point_id"),
          (try_end),

          (try_begin),
            (ge, ":belfry_next_entry_point_id", 0),
            (entry_point_get_position, pos5, ":belfry_next_entry_point_id"), #pos5 holds belfry next entry point target during its path
          (else_try),
            (copy_position, pos5, pos11),    
          (try_end),
        
          (get_distance_between_positions, ":belfry_next_entry_point_distance", pos1, pos5),
        
          #collecting scene prop ids of belfry parts
          (try_begin),
            (eq, ":belfry_kind", 0),
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

          (init_position, pos17),
          (position_move_y, pos17, -225),
          (position_transform_position_to_parent, pos18, pos1, pos17),
          (position_move_y, pos17, -225),
          (position_transform_position_to_parent, pos19, pos1, pos17),

          (assign, ":number_of_agents_around_belfry", 0),
#
#          (get_max_players, ":num_players"),
#          (try_for_range, ":player_no", 0, ":num_players"),
#            (player_is_active, ":player_no"),
#            (player_get_agent_id, ":agent_id", ":player_no"),
#            (ge, ":agent_id", 0),
          (try_for_agents, ":agent_id"),
            (agent_is_human, ":agent_id"),
            (agent_is_alive, ":agent_id"),

            (agent_get_team, ":agent_team", ":agent_id"),
            (eq, ":agent_team", "$attacker_team"),
 
            (agent_get_position, pos2, ":agent_id"),
            (get_sq_distance_between_positions_in_meters, ":dist_between_agent_and_belfry", pos18, pos2),

#            (lt, ":dist_between_agent_and_belfry", multi_distance_sq_to_use_belfry), #must be at most 10m * 10m = 100m away from the player
            (lt, ":dist_between_agent_and_belfry", 140), #must be at most 10m * 10m = 100m away from the player
            (neg|scene_prop_has_agent_on_it, ":belfry_scene_prop_id", ":agent_id"),
            (neg|scene_prop_has_agent_on_it, ":belfry_platform_a_scene_prop_id", ":agent_id"),

            (this_or_next|eq, ":belfry_kind", 1), #there is this_or_next here because belfry_b has no platform_b
            (neg|scene_prop_has_agent_on_it, ":belfry_platform_b_scene_prop_id", ":agent_id"),
    
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_1_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_2_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|scene_prop_has_agent_on_it, ":belfry_wheel_3_scene_prop_id", ":agent_id"),#can be removed to make faster
            (neg|position_is_behind_position, pos2, pos19),
            (position_is_behind_position, pos2, pos1),
            (val_add, ":number_of_agents_around_belfry", 1),        
          (try_end),

          (val_min, ":number_of_agents_around_belfry", 16),

          (try_begin),
            (scene_prop_get_slot, ":pre_number_of_agents_around_belfry", ":belfry_scene_prop_id", slot_scene_prop_number_of_agents_pushing),
            (scene_prop_get_slot, ":next_entry_point_id", ":belfry_scene_prop_id", slot_scene_prop_next_entry_point_id),
            (this_or_next|neq, ":pre_number_of_agents_around_belfry", ":number_of_agents_around_belfry"),
            (neq, ":next_entry_point_id", ":belfry_next_entry_point_id"),

            (try_begin),
              (eq, ":next_entry_point_id", ":belfry_next_entry_point_id"), #if we are still targetting same entry point subtract 
              (prop_instance_is_animating, ":is_animating", ":belfry_scene_prop_id"),
              (eq, ":is_animating", 1),

              (store_mul, ":sqrt_number_of_agents_around_belfry", "$g_last_number_of_agents_around_belfry", 100),
              (store_sqrt, ":sqrt_number_of_agents_around_belfry", ":sqrt_number_of_agents_around_belfry"),
              (val_min, ":sqrt_number_of_agents_around_belfry", 300),
              (assign, ":distance_between_positions_in_meters_0_1", ":belfry_next_entry_point_distance"),
              (val_mul, ":distance_between_positions_in_meters_0_1", ":sqrt_number_of_agents_around_belfry"),
              (val_div, ":distance_between_positions_in_meters_0_1", 100), #100 is because of fixed_point_multiplier
              (val_mul, ":distance_between_positions_in_meters_0_1", 8), #multiplying with 4 to make belfry pushing process slower, 
                                                                 #with 16 agents belfry will go with 4 / 4 = 1 speed (max), with 1 agent belfry will go with 1 / 4 = 0.25 speed (min)    
            (try_end),

            (try_begin),
              (ge, ":belfry_next_entry_point_id", 0),

              #up down rotation of belfry's next entry point
              (init_position, pos9),
              (position_set_y, pos9, -500), #go 5.0 meters back
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), 
              (position_get_distance_to_terrain, ":height_to_terrain_1", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at left part of belfry
      
              (init_position, pos9),
              (position_set_y, pos9, -500), #go 5.0 meters back
              (position_set_x, pos9, 300), #go 3.0 meters right
              (position_transform_position_to_parent, pos10, pos5, pos9), 
              (position_get_distance_to_terrain, ":height_to_terrain_2", pos10), #learn distance between 5 meters back of entry point(pos10) and ground level at right part of belfry

              (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),
              (val_mul, ":height_to_terrain", 100), #because of fixed point multiplier

              (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 2 degrees. #ac sonra
              (init_position, pos20),    
              (position_rotate_x_floating, pos20, ":rotate_angle_of_next_entry_point"),
              (position_transform_position_to_parent, pos23, pos5, pos20),

              #right left rotation of belfry's next entry point
              (init_position, pos9),
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
              (init_position, pos9),
              (position_set_x, pos9, 300), #go 3.0 meters left
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
              (store_sub, ":height_to_terrain_1", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

              (init_position, pos9),
              (position_set_x, pos9, -300), #go 3.0 meters left
              (position_set_y, pos9, -500), #go 5.0 meters forward
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in -x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_left", pos10), #learn distance between 3.0 meters left of entry point(pos10) and ground level
              (init_position, pos9),
              (position_set_x, pos9, 300), #go 3.0 meters left
              (position_set_y, pos9, -500), #go 5.0 meters forward
              (position_transform_position_to_parent, pos10, pos5, pos9), #applying 3.0 meters in x to position of next entry point target, final result is in pos10
              (position_get_distance_to_terrain, ":height_to_terrain_at_right", pos10), #learn distance between 3.0 meters right of entry point(pos10) and ground level
              (store_sub, ":height_to_terrain_2", ":height_to_terrain_at_left", ":height_to_terrain_at_right"),

              (store_add, ":height_to_terrain", ":height_to_terrain_1", ":height_to_terrain_2"),    
              (val_mul, ":height_to_terrain", 100), #100 is because of fixed_point_multiplier
              (store_div, ":rotate_angle_of_next_entry_point", ":height_to_terrain", 24), #if there is 1 meters of distance (100cm) then next target position will rotate by 25 degrees. 
              (val_mul, ":rotate_angle_of_next_entry_point", -1),

              (init_position, pos20),
              (position_rotate_y_floating, pos20, ":rotate_angle_of_next_entry_point"),
              (position_transform_position_to_parent, pos22, pos23, pos20),
            (else_try),
              (copy_position, pos22, pos5),      
            (try_end),
              
            (try_begin),
			

			  
	
			 # (try_begin),
			#  (eq, ":number_of_agents_around_belfry", 0), #if there is no agents near belfry
			#  (eq, "$belfry_sound", 1),
			#  (assign, "$belfry_sound", 0),
			#  #New
			#	(try_for_range, ":player_no", 0, ":num_players"),
			#	(player_is_active, ":player_no"),
			#	(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_sound, "$belfry_sound"), #Step 4 #WORKED!
			#	(try_end),
			#	#New
			#	(neg|multiplayer_is_dedicated_server), #Server should NOT execute this code.
			#  (prop_instance_stop_sound, ":belfry_platform_a_scene_prop_id"), #sf_looping|sf_priority_15|sf_vol_7
			#  #(display_message, "@TESTING BELFRY NO AGENTS", 0x00ff0000),
			# (try_end),
			 
              (ge, ":number_of_agents_around_belfry", 1), #if there is any agents pushing belfry
			  
		#	(try_begin),
		#	(eq, "$belfry_sound", 0),
		#	(assign, "$belfry_sound", 1),
		#	    #New
		#		(try_for_range, ":player_no", 0, ":num_players"),
		#		(player_is_active, ":player_no"),
		#		(multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_sound, "$belfry_sound"), #Step 4 #WORKED!
		#		(try_end),
		#		#New
		#	(neg|multiplayer_is_dedicated_server), #Server should NOT execute this code.
		#	(prop_instance_play_sound, ":belfry_platform_a_scene_prop_id", "snd_belfry_sound"), #sf_looping|sf_priority_15|sf_vol_7
		#	(try_end),
				###
				
              (store_mul, ":sqrt_number_of_agents_around_belfry", ":number_of_agents_around_belfry", 100),
              (store_sqrt, ":sqrt_number_of_agents_around_belfry", ":sqrt_number_of_agents_around_belfry"),
              (val_min, ":sqrt_number_of_agents_around_belfry", 300),
              (val_mul, ":belfry_next_entry_point_distance", 100), #100 is because of fixed_point_multiplier
              (val_mul, ":belfry_next_entry_point_distance", 8), #multiplying with 3 to make belfry pushing process slower, 
                                                                 #with 9 agents belfry will go with 3 / 3 = 1 speed (max), with 1 agent belfry will go with 1 / 3 = 0.33 speed (min)    
              (val_div, ":belfry_next_entry_point_distance", ":sqrt_number_of_agents_around_belfry"),
              #calculating destination coordinates of belfry parts
              #belfry platform_a
              (prop_instance_get_position, pos6, ":belfry_platform_a_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos1, pos6),
              (position_transform_position_to_parent, pos8, pos22, pos7),
              (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos8, ":belfry_next_entry_point_distance"),    
              #belfry platform_b
              (try_begin),
                (eq, ":belfry_kind", 0),
                (prop_instance_get_position, pos6, ":belfry_platform_b_scene_prop_id"),
                (position_transform_position_to_local, pos7, pos1, pos6),
                (position_transform_position_to_parent, pos8, pos22, pos7),
                (prop_instance_animate_to_position, ":belfry_platform_b_scene_prop_id", pos8, ":belfry_next_entry_point_distance"),
              (try_end),
              #wheel rotation
              (store_mul, ":belfry_wheel_rotation", ":belfry_next_entry_point_distance", 25), #-25 fixed bug rotation was reversed
              #(val_add, "$g_belfry_wheel_rotation", ":belfry_wheel_rotation"),
              (assign, "$g_last_number_of_agents_around_belfry", ":number_of_agents_around_belfry"),

              #belfry wheel_1
              #(prop_instance_get_starting_position, pos13, ":belfry_wheel_1_scene_prop_id"),
              (prop_instance_get_position, pos13, ":belfry_wheel_1_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_1_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),
      
              #belfry wheel_2
              #(prop_instance_get_starting_position, pos13, ":belfry_wheel_2_scene_prop_id"),
              (prop_instance_get_position, pos13, ":belfry_wheel_2_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_2_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),
      
              #belfry wheel_3
              (prop_instance_get_position, pos13, ":belfry_wheel_3_scene_prop_id"),
              (prop_instance_get_position, pos20, ":belfry_scene_prop_id"),
              (position_transform_position_to_local, pos7, pos20, pos13),
              (position_transform_position_to_parent, pos21, pos22, pos7),
              (prop_instance_rotate_to_position, ":belfry_wheel_3_scene_prop_id", pos21, ":belfry_next_entry_point_distance", ":belfry_wheel_rotation"),

              #belfry main body
              (prop_instance_animate_to_position, ":belfry_scene_prop_id", pos22, ":belfry_next_entry_point_distance"),    
            (else_try),
              (prop_instance_is_animating, ":is_animating", ":belfry_scene_prop_id"),
              (eq, ":is_animating", 1),

              #belfry platform_a
              (prop_instance_stop_animating, ":belfry_platform_a_scene_prop_id"),
              #belfry platform_b
              (try_begin),
                (eq, ":belfry_kind", 0),
                (prop_instance_stop_animating, ":belfry_platform_b_scene_prop_id"),
              (try_end),
              #belfry wheel_1
              (prop_instance_stop_animating, ":belfry_wheel_1_scene_prop_id"),
              #belfry wheel_2
              (prop_instance_stop_animating, ":belfry_wheel_2_scene_prop_id"),
              #belfry wheel_3
              (prop_instance_stop_animating, ":belfry_wheel_3_scene_prop_id"),
              #belfry main body
              (prop_instance_stop_animating, ":belfry_scene_prop_id"),
            (try_end),
        
            (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_number_of_agents_pushing, ":number_of_agents_around_belfry"),    
            (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_next_entry_point_id, ":belfry_next_entry_point_id"),
          (try_end),
        (else_try),
          (le, ":dist_between_belfry_and_its_destination", 4),
          (scene_prop_slot_eq, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 0),
      
          (scene_prop_set_slot, ":belfry_scene_prop_id", slot_scene_prop_belfry_platform_moved, 1),    

          (try_begin),
            (eq, ":belfry_kind", 0),
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_platform_a", ":belfry_no"),
          (else_try),
            (scene_prop_get_instance, ":belfry_platform_a_scene_prop_id", "spr_belfry_b_platform_a", ":belfry_no"),
          (try_end),
          (assign, "$belfry_positioned", 3),   #
#		  #New
#		  (try_for_range, ":player_no", 0, ":num_players"),
#          (player_is_active, ":player_no"),
#		  (multiplayer_send_2_int_to_player, ":player_no", multiplayer_event_coop_send_to_player, coop_set_belfry_position, "$belfry_positioned"), #Step 4 #WORKED!
#		  (try_end),
#		  #New
		  ####
		  #(assign, "$belfry_sound", 0),
		# #(display_message, "@TESTING BELFRY 2", 0x00ff0000),
		# (try_begin),
		# (neg|multiplayer_is_dedicated_server), #Server should NOT execute this code.
		# (prop_instance_stop_sound, ":belfry_platform_a_scene_prop_id"),
		# (prop_instance_play_sound, ":belfry_platform_a_scene_prop_id", "snd_belfry_sound_end"), #sf_looping|sf_priority_15|sf_vol_7
		# #(display_message, "@TESTING BELFRY 1", 0x00ff0000),
		# (try_end),
		  #(display_message, "@TESTING BELFRY DEDI!!", 0x00ff0000),
          (prop_instance_get_starting_position, pos0, ":belfry_platform_a_scene_prop_id"),
          (prop_instance_animate_to_position, ":belfry_platform_a_scene_prop_id", pos0, 1000),  #400

        (try_end),
      (try_end),
    (try_end),
    ]),
	

	
	#####Camera mode by Rubik Begin Co-Op
(0, 0, 0, [(eq, "$coop_extended_camera", 1)],
 [
 (neg|multiplayer_is_dedicated_server),
   (multiplayer_get_my_player, ":my_player_no"),
   (player_get_agent_id, ":player_agent", ":my_player_no"),
   (gt, ":player_agent", -1),
   (agent_get_look_position, pos1, ":player_agent"),
   (position_move_z, pos1, "$g_camera_z"),
   (position_move_y, pos1, "$g_camera_y"),
   (agent_get_horse, ":horse_agent", ":player_agent"),
   (try_begin),
     (ge, ":horse_agent", 0),
     (position_move_z, pos1, 80),
   (try_end),
   (mission_cam_set_position, pos1),
   (try_begin),
     (key_is_down, key_left_control),
     (assign, ":move_val", 50),
   (else_try),
     (assign, ":move_val", 10),
   (try_end),
   (try_begin),
     (key_clicked, key_up),
     (mission_cam_set_mode, 1),
     (val_add, "$g_camera_z", ":move_val"),
   (else_try),
     (key_clicked, key_down),
     (mission_cam_set_mode, 1),
     (val_sub, "$g_camera_z", ":move_val"),
   (else_try),
     (key_clicked, key_left),
     (mission_cam_set_mode, 1),
     (val_add, "$g_camera_y", ":move_val"),
   (else_try),
     (key_clicked, key_right),
     (mission_cam_set_mode, 1),
     (val_sub, "$g_camera_y", ":move_val"),
   (try_end),
   (try_begin),
     (this_or_next|game_key_clicked, gk_view_char),
     (this_or_next|game_key_clicked, gk_zoom),
     (game_key_clicked, gk_cam_toggle),
     (mission_cam_set_mode, 0),
   (try_end),
  ]),
  #####Camera mode by Rubik End Co-Op
	
	
						#####MUSICBOX SIEGE VARIANT
	(ti_after_mission_start, 0, ti_once, [ #680 #(ti_after_mission_start, 0, 680, [ #680
 #Obtained from Mod Options, affects mission templates, range: ALL SP Hostile music, co-op variant is additional_music_coop.
 (neg|multiplayer_is_dedicated_server), #Dedicateds dont play sound
	],
		
  [
  (display_message, "@You can enable music by holding O, and disable music by holding P."),
    ##(play_track, "track_silence", 1), #Stop current module track
	(music_set_situation, mtf_sit_fight), #Field
   #(music_set_situation, mtf_sit_siege), #Siege probably don't use
	(assign, "$music_timer", 0), #Patch
  #Randomize chance is 1 in a 5 (20%)
  
  #Field related extend to sieges
  #(store_random_in_range, ":randomizer", 0, 5),
  #(try_begin),
  #(eq, ":randomizer", 0),
  (store_random_in_range, ":euro_randomizernext", 1, 11),
  (store_random_in_range, ":medi_randomizer", 1, 6),
  (store_random_in_range, ":arab_randomizer", 1, 8),
  (assign, "$track_count_field_siege", ":euro_randomizernext"),
  (assign, "$track_count_field_medi_siege", ":medi_randomizer"),
  (assign, "$track_count_field_arabs_siege", ":arab_randomizer"),
  #(try_end),
  #Field related extend to sieges
  ]),
	
	(0, 0, 3, [ #680 #(ti_after_mission_start, 0, 680, [ #680
	#(eq, "$additional_music", 1),
	 #Obtained from Mod Options, affects mission templates, range: ALL SP Hostile music, co-op variant is additional_music_coop.
	 	(neg|multiplayer_is_dedicated_server),
	(try_begin),
	(this_or_next|key_is_down, key_o),
	(key_clicked, key_o),
	(eq, "$disallow_music", 1),# Resetting value when track ends.
	(assign, "$disallow_music", 0),# Resetting value when track ends.
	(assign, "$music_timer", 0),# Resetting value when track ends.
	(display_message, "@Music enabled!", 0x006495ed),
	(music_set_situation, mtf_sit_fight), #Field
	(else_try),
	(this_or_next|key_is_down, key_p),
	(key_clicked, key_p),
	(eq, "$disallow_music", 0),# Resetting value when track ends.
	(assign, "$disallow_music", 1),# Resetting value when track ends.
	(play_track, "track_reset_silence", 2),
	(display_message, "@Music disabled!", 0x00ff0000),
	(music_set_situation, mtf_sit_tavern), #Field
	(try_end),
	(eq, "$disallow_music", 0),# Resetting value when track ends.
	],
		
  [
		  #(display_message, "@Executing music code"),
		  (store_mission_timer_b, ":time_msec"),
		  #(assign, reg10, ":time_msec"),
          #(str_clear, s10),
          #(str_store_string, s10, "@Mission timer B for music: {reg10}"),
		  #(display_message, s10),
			#if next action time is lower than current time, play the sound
			(ge, ":time_msec", "$music_timer"),
			(reset_mission_timer_b), #Resetting mission timer, too.
			(assign, "$music_timer", 0),# Resetting value when track ends.
		
  #Euro only
     (try_begin),
      (ge, "$track_count_field_siege", 11),
      (assign, "$track_count_field_siege", 1),
    (else_try),
      (val_add, "$track_count_field_siege", 1),
	  (ge, "$track_count_field_siege", 11),
	  (assign, "$track_count_field_siege", 1),
    (try_end),
  #Euro only
  
  #Mediterrain only
  
       (try_begin),
      (ge, "$track_count_field_medi_siege", 6),
      (assign, "$track_count_field_medi_siege", 1),
    (else_try),
      (val_add, "$track_count_field_medi_siege", 1),
	  (ge, "$track_count_field_medi_siege", 6),
	  (assign, "$track_count_field_medi_siege", 1),
    (try_end),
  #Mediterrain only
  
  
  #Arabs only

       (try_begin),
      (ge, "$track_count_field_arabs_siege", 8),
      (assign, "$track_count_field_arabs_siege", 1),
    (else_try),
      (val_add, "$track_count_field_arabs_siege", 1),
	  (ge, "$track_count_field_arabs_siege", 8),
	  (assign, "$track_count_field_arabs_siege", 1),
    (try_end),
	#Arabs only
  
  #Pause between music length in seconds
  #(val_add, "$music_timer", 2),# 5 seconds added
  #Pause between music length in seconds
  
	(store_current_scene, ":cur_scene_coop_music_siege"),
	#Debug Scene ID
	      #(assign, reg10, ":cur_scene_coop_music_siege"),
          #(str_clear, s10),
          #(str_store_string, s10, "@Scene ID: {reg10}"),
		  #(display_message, s10), #Debug message
	#Debug SCENE ID
	#(party_get_current_terrain, ":current_terrain_main_party", "p_main_party"), #Co-Op variant of this trigger should use scenes in_between rather than terrain because player can't obtain terrain in co-op sessions.
	(try_begin),
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_italy_walls", "scn_town_nordic_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_walls_iberia", "scn_castle_walls_nordic"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_walls_italy", "scn_castle_walls_mongol"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_1_room", "scn_meeting_scene_steppe"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_byzantine_walls_belfry", "scn_player_castle_central_europe_tier1"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_byzantine_castle", "scn_town_house_euro"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_constantinople_center", "scn_town_euro_center_2"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_2_exterior", "scn_castle_42_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_9_exterior", "scn_castle_17_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_17_exterior", "scn_scene_sea"), 
	(eq, ":cur_scene_coop_music_siege", "scn_campside_steppe"), 
	#Begin mediterrain music 5 tracks total
	(try_begin),
	(eq, "$track_count_field_medi_siege", 1), #
	(play_track, "track_medib3", 2),
	(val_add, "$music_timer", 209),# 1 second added
	(else_try),
	
	(eq, "$track_count_field_medi_siege", 2), #
	(play_track, "track_medib4", 2),
	(val_add, "$music_timer", 237),#
	(else_try),
	
	(eq, "$track_count_field_medi_siege", 3), #
	(play_track, "track_medib5", 2),
	(val_add, "$music_timer", 229),#
	(else_try),

	(eq, "$track_count_field_medi_siege", 4), #
	(play_track, "track_medis1", 2),
	(val_add, "$music_timer", 195),#
	(else_try),
	(eq, "$track_count_field_medi_siege", 5), #
	(play_track, "track_medis2", 2),
	(val_add, "$music_timer", 66),#
	(try_end),
	(else_try),
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_euro_center", "scn_town_italy_walls"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_nordic_center", "scn_town_mongol_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_nuernberg_center", "scn_castle_walls_iberia"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_walls_nordic", "scn_castle_walls_eastern"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_kernave", "scn_village_iberia"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_treyden", "scn_acre_walls"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_lublin", "scn_aleppo_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_pskov", "scn_walls_montefort"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_york_center", "scn_constantinople_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_euro_center_2", "scn_walls_krak"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_generic_french", "scn_byzantine_walls_belfry"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_player_castle_central_europe_tier1", "scn_player_castle_desert_tier1"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_player_nordic_1", "scn_scene_sea"), ##Covering all castle interiors & exteriors
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_manor", "scn_campside_steppe"), ##Covering all manors
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_1_exterior", "scn_castle_3_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_3_exterior", "scn_castle_11_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_11_exterior", "scn_castle_2_exterior"), 
	(eq, ":cur_scene_coop_music_siege", "scn_town_house_euro"), 
	#Begin Euro Music
	(try_begin),
	(eq, "$track_count_field_siege", 1), #
	(play_track, "track_euros1", 2),
	(val_add, "$music_timer", 162),#
	(else_try),
	(eq, "$track_count_field_siege", 2), #
	(play_track, "track_euros2", 2),
	(val_add, "$music_timer", 221),#
	(else_try),
	
	(eq, "$track_count_field_siege", 3), #
	(play_track, "track_euros3", 2),
	(val_add, "$music_timer", 190),#
	(else_try),
	
	(eq, "$track_count_field_siege", 4), #
	(play_track, "track_euros4", 2),
	(val_add, "$music_timer", 317),#
	(else_try),
	
	(eq, "$track_count_field_siege", 5), #
	(play_track, "track_euros5", 2),
	(val_add, "$music_timer", 59),#
		(else_try),
	
	(eq, "$track_count_field_siege", 6), #
	(play_track, "track_euros6", 2),
	(val_add, "$music_timer", 59),#
		(else_try),
	
	(eq, "$track_count_field_siege", 7), #
	(play_track, "track_euros7", 2),
	(val_add, "$music_timer", 85),#
		(else_try),
	
	(eq, "$track_count_field_siege", 8), #
	(play_track, "track_euros8", 2),
	(val_add, "$music_timer", 82),#
		(else_try),
	
	(eq, "$track_count_field_siege", 9), #
	(play_track, "track_euros9", 2),
	(val_add, "$music_timer", 199),#
		(else_try),
	
	(eq, "$track_count_field_siege", 10), #
	(play_track, "track_euros10", 2),
	(val_add, "$music_timer", 281),#
	(try_end),
	
	
	
	(else_try),
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_euro_center", "scn_town_italy_walls"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_nordic_center", "scn_town_mongol_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_nuernberg_center", "scn_castle_walls_iberia"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_walls_nordic", "scn_castle_walls_eastern"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_kernave", "scn_village_iberia"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_treyden", "scn_acre_walls"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_lublin", "scn_aleppo_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_pskov", "scn_walls_montefort"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_york_center", "scn_constantinople_center"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_euro_center_2", "scn_walls_krak"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_walls_generic_french", "scn_byzantine_walls_belfry"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_player_castle_central_europe_tier1", "scn_player_castle_desert_tier1"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_player_nordic_1", "scn_scene_sea"), ##Covering all castle interiors & exteriors
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_manor", "scn_campside_steppe"), ##Covering all manors
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_1_exterior", "scn_castle_3_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_3_exterior", "scn_castle_11_exterior"), 
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_11_exterior", "scn_castle_2_exterior"), 
	(eq, ":cur_scene_coop_music_siege", "scn_town_house_euro"), 
	#Begin Euro Music
	(try_begin),
	(eq, "$track_count_field_siege", 1), #
	(play_track, "track_euros1", 2),
	(val_add, "$music_timer", 162),#
	(else_try),
	(eq, "$track_count_field_siege", 2), #
	(play_track, "track_euros2", 2),
	(val_add, "$music_timer", 221),#
	(else_try),
	
	(eq, "$track_count_field_siege", 3), #
	(play_track, "track_euros3", 2),
	(val_add, "$music_timer", 190),#
	(else_try),
	
	(eq, "$track_count_field_siege", 4), #
	(play_track, "track_euros4", 2),
	(val_add, "$music_timer", 317),#
	(else_try),
	
	(eq, "$track_count_field_siege", 5), #
	(play_track, "track_euros5", 2),
	(val_add, "$music_timer", 59),#
		(else_try),
	
	(eq, "$track_count_field_siege", 6), #
	(play_track, "track_euros6", 2),
	(val_add, "$music_timer", 59),#
		(else_try),
	
	(eq, "$track_count_field_siege", 7), #
	(play_track, "track_euros7", 2),
	(val_add, "$music_timer", 85),#
		(else_try),
	
	(eq, "$track_count_field_siege", 8), #
	(play_track, "track_euros8", 2),
	(val_add, "$music_timer", 82),#
		(else_try),
	
	(eq, "$track_count_field_siege", 9), #
	(play_track, "track_euros9", 2),
	(val_add, "$music_timer", 199),#
		(else_try),
	
	(eq, "$track_count_field_siege", 10), #
	(play_track, "track_euros10", 2),
	(val_add, "$music_timer", 281),#
	(try_end),
	
	(else_try),
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_arab_center", "scn_town_euro_center"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_town_mongol_center", "scn_town_eastern_alley"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_interior_eastern", "scn_castle_walls_italy"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_walls_mongol", "scn_walls_kernave"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_acre_walls", "scn_walls_lublin"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_aleppo_center", "scn_walls_pskov"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_player_castle_desert_tier1", "scn_castle_player_nordic_1"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_campside_desert", "scn_byzantine_castle"), ##Desert
	(this_or_next|is_between, ":cur_scene_coop_music_siege", "scn_castle_42_exterior", "scn_castle_9_exterior"), ##Desert
	(this_or_next|eq, ":cur_scene_coop_music_siege", "scn_walls_krak"), 
	(eq, ":cur_scene_coop_music_siege", "scn_walls_montefort"), 
	#Begin arab music
	(try_begin),
	(eq, "$track_count_field_arabs_siege", 1), #
	(play_track, "track_arabs1",  2),
	(val_add, "$music_timer", 198),#
	(else_try),
	(eq, "$track_count_field_arabs_siege", 2), #
	(play_track, "track_arabs2", 2),
	(val_add, "$music_timer", 112),#
	
	(else_try),
	(eq, "$track_count_field_arabs_siege", 3), #
	(play_track, "track_medis1", 2),
	(val_add, "$music_timer", 195),#
	(else_try),
	
	(eq, "$track_count_field_arabs_siege", 4), #
	(play_track, "track_arabs4", 2),
	(val_add, "$music_timer", 79),#
		(else_try),
	
	(eq, "$track_count_field_arabs_siege", 5), #
	(play_track, "track_arabs5", 2),
	(val_add, "$music_timer", 394),#
	
			(else_try),
	(eq, "$track_count_field_arabs_siege", 6), #
	(play_track, "track_arabs3", 2),
	(val_add, "$music_timer", 80),#
			(else_try),
	(eq, "$track_count_field_arabs_siege", 7), #
	(play_track, "track_medis2", 2),
	(val_add, "$music_timer", 66),#
	(try_end),
	(try_end),
	
  ]),
	
	#####MUSICBOX END
	
	###Voice-over for Infantry, archers & Cavalry
		
		(0.0, 0.3, 0.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 29), #Everyone!
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_all")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 30), #Infantry
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_inf")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 31), #Archers
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_archers")
		]),
		
		(0.0, 0.3, 4.0, #Can only fire once every 4 seconds.
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 32), #Cavalry
			(neg|main_hero_fallen),
		],

		[
		(call_script, "script_identify_battle_voices_cav")
		]),
		###Voice-over for Infantry, archers & Cavalry	
	
####Begin Sieges new triggers

		 ###########Torch (Coop Version) by troycall/Envious Arm begin
																	(25.0, 25.0, 120.0, #Repeat checks every 2 minute, delay trigger check by 25 seconds.
																	#(-25.0, 20.0, 60.0, #Repeat checks every 1 minute.
																	#(-25.0, 20.0, 0.0, # Start 25 seconds earlier, delay by 20 seconds if pass, restart every 0 seconds.
																	#(ti_on_agent_spawn, 0, 0, #Enabling this forces random chance to be 100%
																	#(1, 0, ti_once, #Proper one, but reinforcements do not get assigned torches.
																	#(20, 0, ti_once, #Proper one, but reinforcements do not get assigned torches.
        [
		(multiplayer_is_server),
          (mission_tpl_are_all_agents_spawned), 
          #(is_currently_night) #Check if currently night time SP only.
		  
		  #Extension time test for Co-Op
		  #(store_time_of_day, ":hour"),
          #(this_or_next|gt, ":cur_hour", 21), #greater then 9 PM
          #(le, ":cur_hour", 5) #lower then 5 AM
		  #(this_or_next|is_between,":hour",21,25),
		  #(is_between,":hour",1,6)
		  #(is_between, ":cur_hour", 21, 24),
		  #END Extension for Co-Op
		  
        ],
        [

		  ####DEFAULT
		   #(try_for_agents, ":agent"),
            #(agent_get_wielded_item, ":item", ":agent", 1),
            #(gt, ":item", -1),
            #(agent_unequip_item, ":agent", ":item"),
            #(agent_equip_item, ":agent", "itm_torch"),
            #(agent_set_wielded_item, ":agent", "itm_torch"),           
          #(try_end),
		  ####END DEFAULT
		  
		  (try_for_agents, ":agent"), #Try for agents...
		  #Extension
		  (agent_is_alive, ":agent"), #For performance reasons
		  #End
		  (agent_is_human, ":agent"), #Performance
          (agent_is_non_player, ":agent"), #Uncommenting this includes player on spawning with torch, may be necessary to uncomment at module_coop_mission_templates.
		  
		 ##########Default Order
		 #######		  (agent_is_human, ":agent"), #Performance
         #######(agent_is_non_player, ":agent"), #Uncommenting this includes player on spawning with torch, may be necessary to uncomment at module_coop_mission_templates.
		 #######
		 ########Extension
		 #######(agent_is_active, ":agent"), #For performance reasons
		 #######(agent_is_alive, ":agent"), #For performance reasons
		 ########End
		  ############
		  
          #BEGIN DEBUG
          #(assign, reg10, ":agent"),
          #(str_clear, s10),
          #(str_store_string, s10, "@New agent: {reg10}"),
          #END DEBUG
         (agent_get_wielded_item, ":rhanditem", ":agent", 0),  #Obtain right hand item
          (agent_get_wielded_item, ":item", ":agent", 1), # Left hand: shield or -1
          #BEGIN DEBUG
          #(assign, reg10, ":item"),
          #(str_store_string, s10, "@{s10}. LH: {reg10}"),
		  #(display_message, "@Main block Phase A finalized"),
          #END DEBUG

          (try_begin),
		  (neg|is_between, ":rhanditem", "itm_club_with_spike_head", "itm_wooden_shield"),
		  (neg|is_between, ":rhanditem", "itm_lance_banner_jer", "itm_cross_end"), #Update item slots
		    (gt, ":item", -1), #Check if the agent wields any item in the left hand, this or next.
            #(neq, ":item", -1),# Check if the agent wields any item in the left hand
            (neq, ":item", "itm_torch"), #If agent is using torch, ignore him.
            #(display_message, "@PASSED neg tests"), #Debug message
			
            (store_random_in_range, ":chance", 1, 101), # Chance of item being assigned
            (try_begin),
			  (le, ":chance", "$torch_chance_coop"), #25% = 25
				#lt           = neg | ge # less than		-- (lt,<value>,<value>),
				#neq          = neg | eq # not equal to		-- (neq,<value>,<value>),
				#le           = neg | gt # less or equal to	-- (le,<value>,<value>),
              (agent_unequip_item, ":agent", ":item"),
			  
              #BEGIN DEBUG
              #(str_store_item_name, s11, ":item"),
              #(str_store_string, s10, "@{s10}. Removed item: {s11}"),
			  #(display_message, "@(agent_unequip_item, :agent, :item PASSED."),
              #END DEBUG

               
                (agent_equip_item, ":agent", "itm_torch"), #Tell agent to equip the item
                 #(display_message, "@(agent_equip_item, :agent, :item PASSED."),
                  (agent_set_wielded_item, ":agent", "itm_torch"), #Required for infantry only, cavarly can work without it.
                  #(display_message, "@(agent_set_wielded_item, :agent, :item PASSED."),
                 
                 
                  #BEGIN DEBUG
                #(else_try),
                  #(str_store_string, s10, "@{s10}. Failed random chance."),
                (try_end),
               
              #(else_try),
                #(str_store_string, s10, "@{s10}. Invalid agent for torch"),
              (try_end),
             
              #(display_message, s10),
			  (try_end),
              #END DEBUG
      ]),
	  
###########Torch (Coop Version) by troycall/Envious Arm end

#BEgin custom triggers
#		(2.0, 0.0, 0.0,
#		[(multiplayer_is_server),],
#
#		[
#			(call_script, "script_check_friendly_kills")
#			#Nifty little feature where it shows party morale loss per team kill
#		]),
#END
		 ##BEGIN ADDITIONAL TRIGGERS
		 
		 
		 
		 		(0.0, 1.5, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(key_clicked, key_m),
			(get_player_agent_no, ":player_agent_no"),
			  (gt,  ":player_agent_no", -1), #if snow
			(agent_is_alive, ":player_agent_no"),
			(agent_set_animation, ":player_agent_no", "anim_cheer", 1),
			(agent_play_sound, ":player_agent_no", "snd_man_victory")
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_get_team, ":team_player_agent_no", ":player_agent_no"), 
			(agent_get_position, 1, ":player_agent_no"), 
			(try_for_agents, ":var_3"),
				(agent_is_alive, ":var_3"),
				(agent_is_human, ":var_3"),
				(agent_get_team, ":team_var_3", ":var_3"),
				(eq, ":team_var_3", ":team_player_agent_no"),
				(agent_get_position, 0, ":var_3"),
				(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_0_1", 0, 1),
				(lt, ":distance_between_positions_in_meters_0_1", 20),
				(agent_set_animation, ":var_3", "anim_cheer", 1),
				(agent_play_sound, ":var_3", "snd_man_victory"),
				(agent_get_slot, ":var_3_courage_score", ":var_3", slot_agent_courage_score),
				(val_add, ":var_3_courage_score", 5),
				(val_min, ":var_3_courage_score", 9600),
				(agent_set_slot, ":var_3", slot_agent_courage_score, ":var_3_courage_score"),
			(try_end),
			(display_message, "@Huzzah! You encourage your nearby troops.")
		]),

		(0.0, 1.7, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_yell_smelly_peasents", 1)
		],

		[
			(call_script, "script_cf_tom_command_cheer_coop"),
			(assign, "$tom_yell_smelly_peasents", 0)
		]),

		(-26.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(store_trigger_param_2, ":trigger_param_2"),
			(neg|agent_is_ally, ":trigger_param_1"),
			(agent_is_human, ":trigger_param_1"),
			(eq, ":trigger_param_2", "$fplayer_agent_no"),
			(val_add, "$killcount", 1)
		]),

		 		(0.0, 0.3, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 23)
		],

		[
			(eq, "$gk_order", 23),
			(try_begin),
				(game_key_is_down, 23),
				(assign, "$gk_order_hold_over_there", 1),
				(assign, "$gk_order", 0),
				(assign, "$holdit", 0),
			(else_try),
				(eq, "$holdit", 1),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 0), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
				(assign, "$holdit", 0),
			(try_end)
		]),
				(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 23),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 23),
				(assign, "$holdit", 0),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$holdit", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent, if you figure out how to make it work for both teams then this, and spearwalls, and store_battlegroup_Data would all work, even SP formations

			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 5), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),
		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 24),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 24),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 1), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 6), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 25),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(neq, "$gk_order", 23),
				(neq, "$gk_order", 24),
				(neq, "$gk_order", 25),
				(assign, "$gk_order", 25),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
				##Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 2), #Not bugged, disabled for performance. #Patched to an extent #Commented to an extent
				(assign, "$tom_yell_smelly_peasents", 1),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 8), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 26),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(eq, "$gk_order", 0),
				(assign, "$gk_order", 26),
				#(start_presentation, "prsnt_order_display"),
			(else_try),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent group ID issue can be fixed if u figure it out
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 11), #Patched to an extent #Commented to an exten
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 7), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 25),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
	#			(try_for_range, ":number", 0, 9),
	#				(class_is_listening_order, "$fplayer_team_no", ":number"),
	#				(store_add, ":value", 12, ":number"),
	#				(team_slot_ge, "$fplayer_team_no", ":value", 1),
	#				(assign, "$fclock", 1),
	#				#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 2),
	#				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), 
	#			(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),
		
				(0.0, 0.0, 0.0,
		[
			(game_key_clicked, 27),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(try_begin),
				(eq, "$gk_order", 23),
				(assign, "$fclock", 1),
				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #patched to an extent
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 14), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 24),
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
	#			(try_for_range, ":number", 0, 9),
	#				(class_is_listening_order, "$fplayer_team_no", ":number"),
	#				(store_add, ":value", 12, ":number"),
	#				(team_slot_ge, "$fplayer_team_no", ":value", 1),
	#				(assign, "$fclock", 1),
	#				#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 3),
	#				(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #patched to an extent
	#			(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[(neg|multiplayer_is_dedicated_server),
			(game_key_clicked, 28)
		],

		[
			(try_begin),
				(eq, "$gk_order", 24),
				(assign, "$fclock", 1),
				#Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 4), #Patched to an extent #Commented to an extent
				(assign, "$gk_order", 0),
			(else_try),
				(eq, "$gk_order", 26),
				#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
		#		(try_for_range, ":number", 0, 9),
		#			(class_is_listening_order, "$fplayer_team_no", ":number"),
		#			(store_add, ":value", 12, ":number"),
		#			(team_slot_ge, "$fplayer_team_no", ":value", 1),
		#			(assign, "$fclock", 1),
		#			#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 4),
		#			(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
		#		(try_end),
				(assign, "$gk_order", 0),
				#(start_presentation, "prsnt_order_display"),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[(neg|multiplayer_is_dedicated_server),
			(key_clicked, 65)
		],

		[
			(eq, "$gk_order", 26),
			#Notbuggedpatched for performance reasons(call_script, "script_division_reset_places"),
	#		(try_for_range, ":number", 0, 9),
	#			(class_is_listening_order, "$fplayer_team_no", ":number"),
	#			(store_add, ":value", 12, ":number"),
	#			(team_slot_ge, "$fplayer_team_no", ":value", 1),
	#			(assign, "$fclock", 1),
	#			#Not bugged patched for performance reasons(call_script, "script_player_attempt_formation", ":number", 5),
	#			(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
	#		(try_end),
			(assign, "$gk_order", 0),
			#(start_presentation, "prsnt_order_display")
		]),

		(0.0, 0.0, 0.0,
		[
			(key_clicked, 66),
			(neg|multiplayer_is_dedicated_server),
		],

		[
			(eq, "$gk_order", 26),
			(assign, "$fclock", 1),
			##Not bugged disabled for performance##Not bugged patched for performance reasons(call_script, "script_player_order_formations_coop", 2), #Not bugged, disabled for performance. #Patched to an extent #Commented to an extent
			(call_script, "script_cf_cf_first_formation_member_sound_horn_coop"), #Patched to an extent
			(assign, "$gk_order", 0),
			#(start_presentation, "prsnt_order_display")
		]),
		 
##Additional for sieges
		(-28.0, 0.3, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
		],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(store_trigger_param_2, ":trigger_param_2"),
			(store_trigger_param_3, ":trigger_param_3"),
			(assign, ":var_4", reg0),
			(agent_is_human, ":trigger_param_1"),
			(get_player_agent_no, ":player_agent_no"),
#			(try_begin),
#				#(eq, "$tom_weapon_break", 1),
#				(eq, ":trigger_param_1", ":player_agent_no"),
#				(store_random_in_range, ":random_in_range_0_1000", 0, 1000),
#				(eq, ":random_in_range_0_1000", 1),
#				(store_random_in_range, ":random_in_range_4_8", 4, 8),
#				(troop_get_inventory_slot, ":inventory_slot_player_random_in_range_4_8", "trp_player", ":random_in_range_4_8"),
#				(gt, ":inventory_slot_player_random_in_range_4_8", 0),
#				(str_store_item_name, 20, ":inventory_slot_player_random_in_range_4_8"),
#				(troop_get_inventory_slot_modifier, ":inventory_slot_modifier_player_random_in_range_4_8", "trp_player", ":random_in_range_4_8"),
#				(try_begin),
#					(eq, ":inventory_slot_modifier_player_random_in_range_4_8", 6),
#					(display_message, "@Your {s20} is too crapy to fall apart!", 0x00ff0000),
#				(else_try),
#					(troop_add_item, "trp_broken_items", ":inventory_slot_player_random_in_range_4_8", ":inventory_slot_modifier_player_random_in_range_4_8"),
#					(troop_set_inventory_slot_modifier, "trp_player", ":random_in_range_4_8", 6),
#					(display_message, "@Your {s20} cracks!", 0x00ff0000),
#				(try_end),
#			(try_end),
			(try_begin),
				#(eq, "$tom_weapon_break", 1),
				(eq, ":trigger_param_2", ":player_agent_no"),
				(is_between, ":var_4", 1, "itm_cross_end"), #Previously itm_items_end
				(neg|is_between, ":var_4", "itm_light_lance", "itm_wooden_shield"),
				(item_get_type, ":type_var_4", ":var_4"),
				(ge, ":trigger_param_3", 10),
				(neq, ":type_var_4", 10),
				(neq, ":type_var_4", 8),
				(neq, ":type_var_4", 9),
				(neq, ":type_var_4", 5),
				(neq, ":type_var_4", 6),
				(store_random_in_range, ":random_in_range_0_1000", 0, 600),
				(eq, ":random_in_range_0_1000", 1),
				(assign, ":value", -1),
				(try_for_range, ":random_in_range_4_8", 0, 4),
					(troop_get_inventory_slot, ":inventory_slot_player_random_in_range_4_8_2", "trp_player", ":random_in_range_4_8"),
					(eq, ":inventory_slot_player_random_in_range_4_8_2", ":var_4"),
					(assign, ":value", ":random_in_range_4_8"),
				(try_end),
				(gt, ":value", 0),
				(str_store_item_name, 20, ":var_4"),
				(troop_get_inventory_slot_modifier, ":inventory_slot_modifier_player_random_in_range_4_8", "trp_player", ":value"),
				(try_begin),
					(eq, ":inventory_slot_modifier_player_random_in_range_4_8", 6),
					(display_message, "@Your {s20} falls apart!", 0x00ff0000),
					(agent_unequip_item, ":player_agent_no", ":var_4"),
					(troop_remove_item, "trp_player", ":var_4"),
					(troop_remove_item, "trp_broken_items", ":var_4"),
				(else_try),
					(troop_add_item, "trp_broken_items", ":var_4", ":inventory_slot_modifier_player_random_in_range_4_8"),
					(troop_set_inventory_slot_modifier, "trp_player", ":value", 6),
					(display_message, "@Your {s20} cracks!", 0x00ff0000),
				(try_end),
			(try_end),
			(agent_get_horse, ":horse_trigger_param_2", ":trigger_param_2"),
			(try_begin),
				#(eq, "$tom_lance_breaking", 1),
				(gt, ":horse_trigger_param_2", 0),
				(this_or_next|is_between, ":var_4", "itm_light_lance", "itm_spear_a"), #Updated item slots
				(is_between, ":var_4", "itm_lance_banner_jer", "itm_pike_banner_teu"), #Updated item slots
				(ge, ":trigger_param_3", 50),
				(store_random_in_range, ":random_in_range_0_100", 0, 100),
				(gt, ":random_in_range_0_100", 20),
				(try_begin),
					(eq, ":trigger_param_2", ":player_agent_no"),
					(display_message, "@You broke your lance!", 0x00ff0000),
				(try_end),
				########Add effects on weapon break *Lances*
        (agent_get_position, pos1, ":trigger_param_2"),
		(agent_play_sound, ":trigger_param_1", "snd_shield_broken"),
		(particle_system_burst, "psys_lanse", pos1, 10),
        (particle_system_burst, "psys_lanse_straw", pos1, 30),
                ####Extend to Lanse_Blood
		#(particle_system_burst, "psys_lanse_blood", pos1, 10),
        #(particle_system_burst, "psys_lanse_blood", pos1, 30),
		        ########End Effects
				(agent_unequip_item, ":trigger_param_2", ":var_4"),
			(else_try),
				(this_or_next|is_between, ":var_4", "itm_bamboo_spear", "itm_wooden_shield"), #Updated item slots
				(is_between, ":var_4", "itm_pike_banner_teu", "itm_items_end"), #Updated item slots
				(le, ":horse_trigger_param_2", 0),
				(ge, ":trigger_param_3", 8),
				(store_random_in_range, ":random_in_range_0_100", 0, 100),
				(ge, ":random_in_range_0_100", 90),
				(try_begin),
					(eq, ":trigger_param_2", ":player_agent_no"),
					(display_message, "@You broke your spear!", 0x00ff0000),
				(try_end),
				########Add effects on weapon break *Spears*
        (agent_get_position, pos1, ":trigger_param_2"),
		(agent_play_sound, ":trigger_param_1", "snd_shield_broken"),
		(store_random_in_range, ":psys_to_use", "psys_lanse", "psys_lanse_blood"),
		(particle_system_burst, ":psys_to_use", pos1, 7), #Default = 10 (Higher = Bigger Particles)
        (particle_system_burst, ":psys_to_use", pos1, 21), #Default = 30 (Higher = Bigger Particles)
                ####Extend to Lanse_Blood
		#(particle_system_burst, "psys_lanse_blood", pos1, 10),
        #(particle_system_burst, "psys_lanse_blood", pos1, 30),
		        ########End Effects
				(agent_unequip_item, ":trigger_param_2", ":var_4"),
			(try_end),
			###Envfix weapon breaking patch start here
		]),

############		(-25.0, 0.0, 0.0,
############		[
 ###########
 ###########

############			(eq, "$freelancer_state", 1)
############		],
############
############		[
 ###########
 ###########
 ###########
############			(get_player_agent_no, ":player_agent_no"),
############			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
############			(ge, ":player_agent_no", 0),
############			(agent_is_active, ":player_agent_no"),
############			(store_trigger_param_1, ":trigger_param_1"),
############			(eq, ":player_agent_no", ":trigger_param_1"),
############			(agent_get_team, ":team_player_agent_no", ":player_agent_no"),
############			(team_set_order_listener, ":team_player_agent_no", -1),
############			(val_add, ":team_player_agent_no", 2),
############			(agent_set_team, ":player_agent_no", ":team_player_agent_no")
############		]),















#		(-19.0, 0.0, 0.0,
#		[
#(multiplayer_is_server),		
#],
#
#		[
#			(team_set_relation, 0, 2, 1),
#			(team_set_relation, 1, 3, 1),
#			(call_script, "script_change_banners_and_chest")
#		]),
#
#		(-25.0, 0.0, 0.0,
#		[
#		(multiplayer_is_server),
#		],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#			(call_script, "script_troop_agent_set_banner", "tableau_game_troop_label_banner", ":trigger_param_1", ":troop_id_trigger_param_1")
#		]),



		#(0.0, 0.0, ti_once,
		#[],
        #
		#[
		#	(assign, "$g_battle_won", 0),
		#	(assign, "$defender_reinforcement_stage", 0),
		#	(assign, "$attacker_reinforcement_stage", 0),
		#	(assign, "$dmod_current_agent", -1),
		#	(assign, "$dmod_move_camera", -1),
		#	(call_script, "script_music_set_situation_with_culture", 262144)
		#]),

	#	(30.0, 0.0, 0.0,
	#	[],
    #
	#	[]),

	
	
	#Possible bug below
#		(0.0, 0.0, ti_once,
#		[
#			(assign, "$defender_team", 0),
#			(assign, "$attacker_team", 1),
#			(assign, "$defender_team_2", 2),
#			(assign, "$attacker_team_2", 3)
#		],
#
#		[]),

		#Possible bug above
		
		
		
		
		
		
#		(0.0, 0.0, ti_once,
#		[
#			(set_show_messages, 0),
#			(entry_point_get_position, 10, 10),
#			(try_for_range, ":number", 0, 9),
#				(neq, ":number", 1),
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team", ":number", 0),       # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team", ":number", 7),       # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team", ":number", 7),       # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team", ":number", 7),       # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team_2", ":number", 0),     # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team_2", ":number", 7),     # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team_2", ":number", 7),     # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team_2", ":number", 7),     # Patched to an extent
#			(try_end),
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team", 1, 11),              # Patched to an extent
#			(team_set_order_position, "$defender_team", 9, 10),   #patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$defender_team_2", 1, 11),            # Patched to an extent
#			(team_set_order_position, "$defender_team_2", 9, 10), #patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$attacker_team", 9, 2),               # Patched to an extent
#			#Not bugged, disabled for performance#(team_give_order, "$attacker_team_2", 9, 2),             # Patched to an extent
#			(set_show_messages, 1)
#		],
#
#		[]),


##Possible bug below.
#		(0.0, 2.0, ti_once,
#		[],
#
#		[
#			(try_for_agents, ":var_1"),
#				(agent_set_slot, ":var_1", slot_agent_is_not_reinforcement, 1),
#			(try_end)
#		]),
#
#		(3.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_mission_timer_a, ":mission_timer_a"),
#			(ge, ":mission_timer_a", 10),
#			(try_begin),
#				(store_mul, ":value", "$attacker_reinforcement_stage", 2),
#				(this_or_next|lt, "$defender_reinforcement_stage", 14),
#				(le, "$defender_reinforcement_stage", ":value"),
#				(store_normalized_team_count, ":normalized_team_count_0", 0),
#				(lt, ":normalized_team_count_0", 10),
#				(add_reinforcements_to_entry, 4, 7),
#				(val_add, "$defender_reinforcement_stage", 1),
#			(try_end)
#		]),

		(2.0, 0.0, ti_once,
		[
		(multiplayer_is_dedicated_server),
		],
		
		[
		(assign, "$dedicated_messages", 0),
		]),
		
		
		(2.0, 0.0, 10.0,
		[
		(multiplayer_is_server),
		#(gt, "$defender_reinforcement_stage", 0)
		],

		[
		(try_begin),
		(eq, "$experimental_archers", 0),
		(call_script, "script_siege_move_archers_to_archer_positions"),
		(else_try),
		(eq, "$experimental_archers", 1),
		(call_script, "script_siege_move_archers_to_archer_positions_new"),
		(try_end),
		
	
		(try_begin),
		(eq, "$dedicated_messages", 0),
		(val_add, "$dedicated_messages", 1),
		(multiplayer_is_dedicated_server),
		(try_begin),
		(eq, "$experimental_archers", 0),
		(display_message, "@Dedicated server information: - Using Regular stable archer positioning"),
		(else_try),
		(eq, "$experimental_archers", 1),
		(display_message, "@Dedicated server debug - Using Experimental new archer positioning"),
		(try_end),
		(try_end),
		]),

#		(3.0, 0.0, 0.0,
#		[
#			(assign, ":value", 1),
#			(try_begin),
#				(ge, "$attacker_reinforcement_stage", 10),
#				(store_mul, ":value_2", "$defender_reinforcement_stage", 2),
#				(gt, "$attacker_reinforcement_stage", ":value_2"),
#				(assign, ":value", 0),
#			(try_end),
#			(eq, ":value", 1),
#			(store_mission_timer_a, ":mission_timer_a"),
#			(ge, ":mission_timer_a", 10),
#			(store_normalized_team_count, ":normalized_team_count_1", 1),
#			(lt, ":normalized_team_count_1", 6)
#		],
#
#		[
#			(add_reinforcements_to_entry, 1, 8),
#			(val_add, "$attacker_reinforcement_stage", 1)
#		]),
#^^POSSIBLE BUG ABOVE


	#	(2.0, 0.0, ti_once,
	#	[],
    #    
	#	[
	#		(set_show_messages, 0),
	#		(try_for_range, ":number", 0, 3), #THIS IS POTENTIONALLY THE ERROR MAYBE FIXABLE BY REDUCING NUMBER TO 3?
	#			 #Not bugged, disabled for performance#(team_give_order, "$attacker_team", ":number", 12), # Patched to an extent #THIS IS POTENTIONALLY THE ERROR
	#		(try_end),
	#		(try_for_range, ":number", 0, 3), #THIS IS POTENTIONALLY THE ERROR MAYBE FIXABLE BY REDUCING NUMBER TO 3?
	#		 #Not bugged, disabled for performance#(team_give_order, "$attacker_team_2", ":number", 12), 	# Patched to an extent #THIS IS POTENTIONALLY THE ERROR
	#		(try_end),
	#		(set_show_messages, 1)
	#	]),

#		(2.0, 0.0, 0.0,
#		[],
#
#		[
#			(call_script, "script_check_friendly_kills")
#		]),

############		(30.0, 0.0, 0.0,
############		[],

################Patched to an extent, script below is probably unnecessary since units already refill ammo from the co-op script.
############		[

############			(get_player_agent_no, ":player_agent_no"),
############
############
############			(try_for_agents, ":var_2"),
############				(neq, ":var_2", ":player_agent_no"),
############				(agent_is_alive, ":var_2"),
############				(agent_is_human, ":var_2"),
############				(agent_get_team, ":team_var_2", ":var_2"),
############				(this_or_next|eq, ":team_var_2", "$defender_team"),
############				(eq, ":team_var_2", "$defender_team_2"),
############				(agent_refill_ammo, ":var_2"),
############			(try_end),
############			(try_begin),
############				(agent_get_team, ":team_var_2", ":player_agent_no"),
############				(this_or_next|eq, ":team_var_2", "$defender_team"),
############				(eq, ":team_var_2", "$defender_team_2"),
############				(agent_refill_ammo, ":player_agent_no"),
############			(try_end)
############		]),






#		(-26.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(store_trigger_param_2, ":trigger_param_2"), #Unassigned variable #Removedforunassignedstuff#
#			(store_trigger_param_3, ":trigger_param_3"),
#			(try_begin),
#				(ge, ":trigger_param_1", 0),
#				(neg|agent_is_ally, ":trigger_param_1"),
#				(agent_is_human, ":trigger_param_1"),
#				(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#				(party_add_members, "p_total_enemy_casualties", ":troop_id_trigger_param_1", 1),
#				(eq, ":trigger_param_3", 1),
#				(party_wound_members, "p_total_enemy_casualties", ":troop_id_trigger_param_1", 1),
#			(try_end)
#		]),

		(-25.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(call_script, "script_set_matching_sexy_boots", ":trigger_param_1")
		]),

		(0.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$sp_shield_bash_coop", 1),
			(game_key_is_down, 7),
			(game_key_clicked, 6)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_is_active, ":player_agent_no"),
			(agent_is_alive, ":player_agent_no"),
			(neg|agent_slot_ge, ":player_agent_no", 50, 1),
			(agent_get_wielded_item, ":wielded_item_player_agent_no_1", ":player_agent_no", 1),
			(is_between, ":wielded_item_player_agent_no_1", 1, "itm_cross_end"), #Previously itm_items_end
			(item_get_type, ":type_wielded_item_player_agent_no_1", ":wielded_item_player_agent_no_1"),
			(eq, ":type_wielded_item_player_agent_no_1", 7),
			(agent_get_defend_action, ":defend_action_player_agent_no", ":player_agent_no"),
			(eq, ":defend_action_player_agent_no", 2),
			(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
			(eq, ":horse_player_agent_no", -1),
			(agent_set_slot, ":player_agent_no", 50, 3),
			(agent_set_animation, ":player_agent_no", "anim_shield_bash"),
			(agent_get_troop_id, ":troop_id_player_agent_no", ":player_agent_no"),
			(troop_get_type, ":type_wielded_item_player_agent_no_1", ":troop_id_player_agent_no"),
			(try_begin),
				(eq, ":type_wielded_item_player_agent_no_1", 0),
				(agent_play_sound, ":player_agent_no", "snd_man_yell"),
			(else_try),
				(eq, ":type_wielded_item_player_agent_no_1", 1),
				(agent_play_sound, ":player_agent_no", "snd_woman_yell"),
			(try_end),
			(agent_get_position, 1, ":player_agent_no"),
			(assign, ":value", -1),
			(assign, ":value_2", 150),
			(try_for_agents, ":var_18"),
				(agent_is_alive, ":var_18"),
				(agent_is_human, ":var_18"),
				(neg|agent_is_ally, ":var_18"),
				(agent_get_position, 2, ":var_18"),
				(neg|position_is_behind_position, 2, 1),
				(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
				(le, ":distance_between_positions_1_2", ":value_2"),
				(assign, ":value_2", ":distance_between_positions_1_2"),
				(assign, ":value", ":var_18"),
			(try_end),
			(ge, ":value", 0),
			(agent_play_sound, ":value", "snd_wooden_hit_low_armor_high_damage"),
			(agent_get_defend_action, ":defend_action_player_agent_no", ":value"),
			(try_begin),
				(eq, ":defend_action_player_agent_no", 2),
				(neg|position_is_behind_position, 1, 2),
				(agent_get_wielded_item, ":wielded_item_player_agent_no_1", ":value", 1),
				(is_between, ":wielded_item_player_agent_no_1", 1, "itm_cross_end"), #Previously itm_items_end
				(item_get_type, ":type_wielded_item_player_agent_no_1", ":wielded_item_player_agent_no_1"),
				(eq, ":type_wielded_item_player_agent_no_1", 7),
				(agent_set_animation, ":value", "anim_shield_bash"),
			(else_try),
				(agent_set_animation, ":value", "anim_shield_strike"),
			(try_end)
		]),

		(1.0, 0.0, 0.0,
		[
		(neg|multiplayer_is_dedicated_server),
			(eq, "$sp_shield_bash_coop", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(agent_is_active, ":player_agent_no"),
			(agent_is_alive, ":player_agent_no"),
			(agent_get_slot, ":player_agent_no_50", ":player_agent_no", 50),
			(val_sub, ":player_agent_no_50", 1),
			(val_max, ":player_agent_no_50", 0),
			(agent_set_slot, ":player_agent_no", 50, ":player_agent_no_50")
		]),

		(0.25, 0.0, 0.0,
		[
		(multiplayer_is_server),
			(eq, "$sp_shield_bash_ai_coop", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(try_for_agents, ":var_2"),
				(neq, ":var_2", ":player_agent_no"),
				(agent_is_alive, ":var_2"),
				(agent_is_human, ":var_2"),
				(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
				(store_skill_level, ":skill_level_shield_troop_id_var_2", "skl_shield", ":troop_id_var_2"),
				(store_proficiency_level, ":proficiency_level_troop_id_var_2_0", ":troop_id_var_2", 0),
				(ge, ":skill_level_shield_troop_id_var_2", 4),
				(ge, ":proficiency_level_troop_id_var_2_0", 200),
				(agent_get_horse, ":horse_var_2", ":var_2"),
				(le, ":horse_var_2", 0),
				(try_begin),
					(neg|agent_slot_ge, ":var_2", 50, 1),
					(agent_slot_eq, ":var_2", slot_agent_is_running_away, 0),
					(agent_get_wielded_item, ":wielded_item_var_2_1", ":var_2", 1),
					(is_between, ":wielded_item_var_2_1", 1, "itm_cross_end"), #Previously itm_items_end
					(item_get_type, ":type_wielded_item_var_2_1", ":wielded_item_var_2_1"),
					(eq, ":type_wielded_item_var_2_1", 7),
					(agent_get_attack_action, ":attack_action_var_2", ":var_2"),
					(eq, ":attack_action_var_2", 0),
					(agent_get_team, ":team_var_2", ":var_2"), #Patched to an extent opcode 1770 probably
					(agent_get_position, 1, ":var_2"),
					(assign, ":value", -1),
					(assign, ":value_2", 125),
					(try_for_agents, ":var_13"),
						(agent_is_alive, ":var_13"),
						(agent_is_human, ":var_13"),
						(agent_get_position, 2, ":var_13"),
						(neg|position_is_behind_position, 2, 1),
						(agent_get_team, ":team_var_13", ":var_13"),
						(neq, ":team_var_13", ":team_var_2"),
						(try_begin),
							(eq, ":team_var_2", 0),
							(assign, ":value_3", 2),
						(else_try),
							(eq, ":team_var_2", 2),
							(assign, ":value_3", 0),
						(else_try),
							(eq, ":team_var_2", 1),
							(assign, ":value_3", 3),
						(else_try),
							(eq, ":team_var_2", 3),
							(assign, ":value_3", 1),
						(try_end),
						(neq, ":team_var_13", ":value_3"),
						(get_distance_between_positions, ":distance_between_positions_1_2", 1, 2),
						(le, ":distance_between_positions_1_2", ":value_2"),
						(assign, ":value_2", ":distance_between_positions_1_2"),
						(assign, ":value", ":var_13"),
					(try_end),
					(ge, ":value", 0),
					(agent_get_horse, ":horse_var_2", ":value"),
					(eq, ":horse_var_2", -1),
					(store_random_in_range, ":random_in_range_15_26", 15, 26),
					(agent_set_slot, ":var_2", 50, ":random_in_range_15_26"),
					(agent_set_animation, ":var_2", "anim_shield_bash"),
					(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
					(troop_get_type, ":type_wielded_item_var_2_1", ":troop_id_var_2"),
					(try_begin),
						(eq, ":type_wielded_item_var_2_1", 0),
						(agent_play_sound, ":var_2", "snd_man_yell"),
					(else_try),
						(eq, ":type_wielded_item_var_2_1", 1),
						(agent_play_sound, ":var_2", "snd_woman_yell"),
					(try_end),
					(agent_play_sound, ":value", "snd_wooden_hit_low_armor_high_damage"),
					(agent_get_defend_action, ":attack_action_var_2", ":value"),
					(try_begin),
						(eq, ":attack_action_var_2", 2),
						(neg|position_is_behind_position, 1, 2),
						(agent_get_wielded_item, ":wielded_item_var_2_1", ":value", 1),
						(is_between, ":wielded_item_var_2_1", 1, "itm_cross_end"), #Previously itm_items_end
						(item_get_type, ":type_wielded_item_var_2_1", ":wielded_item_var_2_1"),
						(eq, ":type_wielded_item_var_2_1", 7),
						(agent_set_animation, ":value", "anim_shield_bash"),
					(else_try),
						(agent_set_animation, ":value", "anim_shield_strike"),
					(try_end),
				(try_end),
				(agent_get_slot, ":var_2_50", ":var_2", 50),
				(val_sub, ":var_2_50", 1),
				(val_max, ":var_2_50", 0),
				(agent_set_slot, ":var_2", 50, ":var_2_50"),
			(try_end)
		]),

		#Probably unnecessary begin
		(-25.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(store_trigger_param_1, ":trigger_param_1"),
			(agent_is_human, ":trigger_param_1"),
			(agent_is_non_player, ":trigger_param_1"),
			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
			(lt, ":troop_id_trigger_param_1", "trp_kidnapped_girl"),
			(try_for_range, reg0, 0, 4),
				(agent_get_item_slot, ":item_slot_trigger_param_1_reg0", ":trigger_param_1", reg0),
				(is_between, ":item_slot_trigger_param_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
				(agent_unequip_item, ":trigger_param_1", ":item_slot_trigger_param_1_reg0"),
			(try_end),
			(try_for_range, reg0, 0, 2),
				(agent_get_wielded_item, ":item_slot_trigger_param_1_reg0", ":trigger_param_1", reg0),
				(is_between, ":item_slot_trigger_param_1_reg0", 1, "itm_cross_end"), #Previously itm_items_end
				(agent_unequip_item, ":trigger_param_1", ":item_slot_trigger_param_1_reg0"),
			(try_end),
			(assign, ":var_4", 0),
			(assign, ":var_5", 25),
			(assign, ":var_6", 50),
			(assign, ":var_7", 75),
			(assign, ":var_8", 100),
			(assign, ":var_18", 125),
			(assign, ":var_10", 150),
			(assign, ":var_11", 175),
			(assign, ":var_12", 200),
			(assign, ":value", 0),
			(assign, ":value_2", 0),
			(assign, ":value_3", 0),
			(assign, ":value_4", 0),
			(assign, ":value_5", 0),
			(assign, ":value_6", 0),
			(assign, ":value_7", 0),
			(assign, ":value_8", 0),
			(assign, ":value_9", 0),
			(troop_get_inventory_capacity, ":inventory_capacity_troop_id_trigger_param_1", ":troop_id_trigger_param_1"),
			(try_for_range, ":localvariable", 0, ":inventory_capacity_troop_id_trigger_param_1"),
				(troop_get_inventory_slot, ":inventory_slot_troop_id_trigger_param_1_localvariable", ":troop_id_trigger_param_1", ":localvariable"),
				(is_between, ":inventory_slot_troop_id_trigger_param_1_localvariable", 1, "itm_cross_end"), #Previously itm_items_end
				(item_get_type, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
				(try_begin),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 4),
					(val_add, ":var_4", 1),
					(troop_set_slot, "trp_items_array", slot_troop_relations_begin, ":var_4"),
					(troop_set_slot, "trp_items_array", ":var_4", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 2),
					(val_add, ":var_5", 1),
					(troop_set_slot, "trp_items_array", slot_troop_last_quest_betrayed, ":var_5"),
					(troop_set_slot, "trp_items_array", ":var_5", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_2", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 7),
					(val_add, ":var_6", 1),
					(troop_set_slot, "trp_items_array", slot_troop_recruitment_random, ":var_6"),
					(troop_set_slot, "trp_items_array", ":var_6", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_3", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 3),
					(val_add, ":var_7", 1),
					(troop_set_slot, "trp_items_array", slot_troop_personalitymatch_object, ":var_7"),
					(troop_set_slot, "trp_items_array", ":var_7", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_4", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 10),
					(val_add, ":var_8", 1),
					(troop_set_slot, "trp_items_array", 100, ":var_8"),
					(troop_set_slot, "trp_items_array", ":var_8", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_5", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 6),
					(val_add, ":var_18", 1),
					(troop_set_slot, "trp_items_array", slot_troop_rehire_speech, ":var_18"),
					(troop_set_slot, "trp_items_array", ":var_18", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_6", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 5),
					(val_add, ":var_10", 1),
					(troop_set_slot, "trp_items_array", slot_troop_days_on_mission, ":var_10"),
					(troop_set_slot, "trp_items_array", ":var_10", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_7", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 8),
					(val_add, ":var_11", 1),
					(troop_set_slot, "trp_items_array", 175, ":var_11"),
					(troop_set_slot, "trp_items_array", ":var_11", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_8", 1),
				(else_try),
					(eq, ":type_inventory_slot_troop_id_trigger_param_1_localvariable", 9),
					(val_add, ":var_12", 1),
					(troop_set_slot, "trp_items_array", 200, ":var_12"),
					(troop_set_slot, "trp_items_array", ":var_12", ":inventory_slot_troop_id_trigger_param_1_localvariable"),
					(assign, ":value_9", 1),
				(try_end),
			(try_end),
			(try_begin),
				(eq, ":value", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_relations_begin),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 1, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_2", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_last_quest_betrayed),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 26, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_3", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_recruitment_random),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 51, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_4", 1),
				(try_begin),
					(eq, ":value_2", 1),
					(store_random_in_range, ":random_in_range_0_100", 0, 100),
					(lt, ":random_in_range_0_100", 65),
				(else_try),
					(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_personalitymatch_object),
					(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 76, ":items_array_relations_begin"),
					(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
					(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
				(try_end),
			(try_end),
			(try_begin),
				(eq, ":value_5", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 100),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 101, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_6", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_rehire_speech),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 126, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_7", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", slot_troop_days_on_mission),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 151, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_8", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 175),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 176, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end),
			(try_begin),
				(eq, ":value_9", 1),
				(troop_get_slot, ":items_array_relations_begin", "trp_items_array", 200),
				(store_random_in_range, ":random_in_range_1_items_array_relations_begin", 201, ":items_array_relations_begin"),
				(troop_get_slot, ":items_array_random_in_range_1_items_array_relations_begin", "trp_items_array", ":random_in_range_1_items_array_relations_begin"),
				(agent_equip_item, ":trigger_param_1", ":items_array_random_in_range_1_items_array_relations_begin"),
			(try_end)
		]),
##Probably unnecessary end
		
		
				(-19.0, 0.0, 0.0,
		[#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),],

		[
		
			(assign, "$tom_sand_storm", 0),
			(call_script, "script_change_rain_or_snow"),
			(set_fixed_point_multiplier, 100),
			(try_begin),
				(is_currently_night),
				#(set_shader_param_float, "@vFresnelMultiplier", 15),
			(else_try),
				#(set_shader_param_float, "@vFresnelMultiplier", 50),
			(try_end)
		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 1)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
					     (gt,  ":player_agent_no", -1), #if snow
			(agent_get_position, 0, ":player_agent_no"), #
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
			(val_add, ":position_z_0", 400),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_desert_storm", 0, 2),
			(set_fixed_point_multiplier, 100)
		]),
#		(300.0, 2.0, 300.0,
#		#(0.0, 2.0, ti_once, #Patched to an extent
#		[
#		(multiplayer_is_server),
#			(eq, "$tom_use_banners", 1)
#		],
#
#		[
#			(call_script, "script_set_flag_carriers")
#		]),

#		(10.0, 0.0, 10.0,
#		[
#		(neg|multiplayer_is_server),
#			(eq, "$tom_use_banners", 1),
#			(eq, "$tom_bonus_banners", 1)
#		],
#
#		[
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(try_for_range, ":value"),
#				(agent_slot_eq, ":value", 107, 1),
#				(agent_is_alive, ":value"),
#				(agent_is_active, ":value"),
#				(agent_get_team, ":team_value", ":value"),
#				(agent_get_position, 1, ":value"),
#				(try_for_range, ":value_2"),
#					(neq, ":value_2", ":value"),
#					(agent_get_team, ":team_value_2", ":value_2"),
#					(eq, ":team_value", ":team_value_2"),
#					(agent_is_alive, ":value_2"),
#					(agent_is_active, ":value_2"),
#					(agent_is_human, ":value_2"),
#					(agent_get_position, 2, ":value_2"),
#					(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_1_2", 1, 2),
#					(le, ":distance_between_positions_in_meters_1_2", 10),
#					(store_agent_hit_points, ":agent_hit_points_value_2", ":value_2"),
#					(val_add, ":agent_hit_points_value_2", 2),
#					(val_min, ":agent_hit_points_value_2", 101),
#					(agent_set_hit_points, ":value_2", ":agent_hit_points_value_2"),
#					(try_begin),
#						(eq, ":value_2", ":player_agent_no"),
#						(display_message, "@You feel secured standing near the banner, healing some of your HP.", 0x006495ed),
#					(try_end),
#				(try_end),
#			(try_end),
#			(assign, ":value", ":player_agent_no"),
#			(agent_is_alive, ":value"), #Patched to an extent Agent ID -1 error on this opcode and the line below this (the opcode) #Note only error when spectating, maybe re-enable so you can heal near banners?
#			(agent_get_wielded_item, ":wielded_item_value_0", ":value", 0), #Patched to an extent
#			(is_between, ":wielded_item_value_0", 1198, 1202),
#			(agent_get_team, ":team_value", ":value"),
#			(agent_get_position, 1, ":value"),
#			(try_for_range, ":value_2"),
#				(neq, ":value_2", ":value"),
#				(agent_get_team, ":team_value_2", ":value_2"),
#				(eq, ":team_value", ":team_value_2"),
#				(agent_is_alive, ":value_2"),
#				(agent_is_active, ":value_2"),
#				(agent_is_human, ":value_2"),
#				(agent_get_position, 2, ":value_2"),
#				(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_1_2", 1, 2),
#				(le, ":distance_between_positions_in_meters_1_2", 10),
#				(store_agent_hit_points, ":agent_hit_points_value_2", ":value_2"),
#				(try_begin),
#					(eq, ":wielded_item_value_0", 1201),
#					(val_add, ":agent_hit_points_value_2", 1),
#				(try_end),
#				(val_add, ":agent_hit_points_value_2", 5),
#				(val_max, ":agent_hit_points_value_2", 101),
#				(agent_set_hit_points, ":value_2", ":agent_hit_points_value_2"),
#			(try_end)
#		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 3)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
					     (gt,  ":player_agent_no", -1), #if snow
			(agent_get_position, 0, ":player_agent_no"), 
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
			(val_add, ":position_z_0", 2100),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_rain", 0, 1),
			(set_fixed_point_multiplier, 100)
		]),

		(0.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 2)
		],

		[
			(get_player_agent_no, ":player_agent_no"),
					     (gt,  ":player_agent_no", -1), #if snow
			(agent_get_position, 0, ":player_agent_no"), 
			(position_set_z_to_ground_level, 0),
			(position_get_z, ":position_z_0", 0),
			(val_add, ":position_z_0", 2000),
			(position_set_z, 0, ":position_z_0"),
			(particle_system_burst, "psys_blizzard", 0, 1),
			(set_fixed_point_multiplier, 100)
		]),

		(8.0, 0.0, 0.0,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 3)
		],

		[
			(store_random_in_range, ":random_in_range_0_100", 0, 100),
			(try_begin),
				(ge, ":random_in_range_0_100", 90),
				(play_sound, "snd_thunder"),
			(try_end)
		]),

		(0.0, 0.0, ti_once,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 2)
		],

		[
			(play_sound, "snd_wind")
		]),

		(0.0, 0.0, ti_once,
		[
		#(multiplayer_is_server),
		(neg|multiplayer_is_dedicated_server),
			(eq, "$tom_sand_storm", 1)
		],

		[
			(play_sound, "snd_wind")
		]),
		

##########		#(-19.0, 0.0, 0.0,
##########		#[],
##########        #
##########		#[
##########
##########
##########
 #########
 #########
 #########
##########		#	(call_script, "script_clear_troop_array", "trp_lances_troop_in_combat", 0, "$lance_troop_serving")
##########		#]),
##########
##########
##########
##########
##########
##########





#
#		(-25.0, 0.0, 0.0,
#		[],
#
#		[
#			(store_trigger_param_1, ":trigger_param_1"),
#			(agent_is_human, ":trigger_param_1"),
#			(get_player_agent_no, ":player_agent_no"),
#			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(neq, ":trigger_param_1", ":player_agent_no"),
#			(agent_get_party_id, ":party_id_trigger_param_1", ":trigger_param_1"),
#			(eq, ":party_id_trigger_param_1", "p_main_party"),
#			(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
#			(call_script, "script_search_for_troop", ":troop_id_trigger_param_1"),
#			(agent_set_slot, ":trigger_param_1", 102, reg0)
#		]),
#########
 ########

#########		(-19.0, 0.0, 0.0,
#########		[],
#########
#########		[



#########			(assign, "$enable_deahtcam", 1),
#########			(assign, "$auxilary_player_active", 0),
#########			(eq, "$use_player_auxiliary", 1),
#########			(assign, "$g_move_heroes", 1),
#########			(party_clear, "p_temp_casualties_3"),
#########			(call_script, "script_party_add_party", "p_temp_casualties_3", "p_main_party"),
#########			(set_player_troop, "trp_player"),
#########			(assign, "$enable_deahtcam", 0)
#########		]),
 ########


#########		(5.0, 0.0, 0.0,
#########		[

#########			(eq, "$use_player_auxiliary", 1),
#########			(eq, "$enable_deahtcam", 0),
#########			(get_player_agent_no, ":player_agent_no"),
#########			(neg|agent_is_alive, ":player_agent_no")
#########		],
 ########
#########		[



#########			(set_fixed_point_multiplier, 100),
#########			(get_player_agent_no, ":player_agent_no"),
#########			(agent_get_team, ":team_player_agent_no", ":player_agent_no"),
#########			(agent_get_division, ":division_player_agent_no", ":player_agent_no"),
#########			(assign, ":value", 0),
#########			(try_for_agents, ":var_5"),
#########				(eq, ":value", 0),
#########				(agent_is_human, ":var_5"),
#########				(agent_is_alive, ":var_5"),
#########				(agent_get_team, ":team_var_5", ":var_5"),
#########				(agent_get_party_id, ":party_id_var_5", ":var_5"),
#########				(eq, ":party_id_var_5", "p_main_party"),
#########				(agent_get_division, ":division_player_agent_no_2", ":player_agent_no"),
#########				(agent_get_group, ":group_player_agent_no", ":player_agent_no"),
#########				(eq, ":team_player_agent_no", ":team_var_5"),
#########				(eq, ":division_player_agent_no", ":division_player_agent_no_2"),
#########				(agent_get_troop_id, ":troop_id_var_5", ":var_5"),
#########				(neg|is_between, ":troop_id_var_5", "trp_npc1", "trp_kingdom_2_pretender"),
#########				(set_player_troop, ":troop_id_var_5"),
#########				(store_agent_hit_points, ":agent_hit_points_var_5_1", ":var_5", 1),
#########				(agent_get_position, 1, ":var_5"),
#########				(position_set_z, 1, -2000),
#########				(position_set_x, 1, 0),
#########				(position_set_y, 1, 0),
#########				(agent_get_position, 0, ":var_5"),
#########				(set_spawn_position, 0),
#########				(agent_get_horse, ":horse_var_5", ":var_5"),
#########				(try_begin),
#########					(gt, ":horse_var_5", 0),
#########					(agent_set_position, ":horse_var_5", 1),
#########					(remove_agent, ":horse_var_5"),
#########				(try_end),
#########				(agent_set_position, ":var_5", 1),
#########				(agent_set_slot, ":var_5", 100, 1),
#########				(agent_get_slot, ":var_5_102", ":var_5", 102),
#########				(remove_agent, ":var_5"),
#########				(spawn_agent, ":troop_id_var_5"),
#########				(assign, ":player_agent_no", reg0),
#########				(agent_set_slot, ":player_agent_no", 102, ":var_5_102"),
#########				(agent_set_team, ":player_agent_no", ":team_player_agent_no"),
#########				(agent_set_hit_points, ":player_agent_no", ":agent_hit_points_var_5_1", 1),
#########				(agent_set_group, ":player_agent_no", ":group_player_agent_no"),
#########				(agent_set_slot, ":player_agent_no", 100, 2),
#########				(agent_set_slot, ":player_agent_no", 101, ":troop_id_var_5"),
#########				(try_begin),
#########					(agent_get_horse, ":horse_player_agent_no", ":player_agent_no"),
#########					(gt, ":horse_player_agent_no", 0),
#########					(lt, ":horse_var_5", 0),
#########					(agent_set_position, ":horse_player_agent_no", 1),
#########					(remove_agent, ":horse_player_agent_no"),
#########				(try_end),
#########				(set_player_troop, "trp_player"),
#########				(assign, ":value", 1),
#########				(assign, "$auxilary_player_active", 1),
#########			(try_end),
#########			(eq, ":value", 0),
#########			(assign, "$enable_deahtcam", 1)
#########		]),
#########

#Crash is somewhere in the oil code, perhaps because i removed agent_force_rethink, try adding it and see if it fixes the bug, while making sure it do sent affect belfry and ladder sieges
		(1.0, 0.0, 0.0, #(1.0, 0.0, 0.0,
		[
		(multiplayer_is_server), #Probably shouldn't be used
		],

		[
			(val_add, "$do_the_oil", 1),
			(try_begin),
				(gt, "$do_the_oil", 5),
				(assign, "$do_the_oil", 0),
			(try_end),
			(multiplayer_get_my_player, ":player_agent_no"),
			#(get_player_agent_no, ":player_agent_no"),
#			(neq,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(try_for_agents, ":var_2"),
				(agent_is_alive, ":var_2"),
				#(neq, ":var_2", -1), #Lowers chance of CTD
				#(neq, ":var_2", 0), #New
				#(neq, ":player_agent_no", -1), #Lowers chance of CTD
				#(neq, ":player_agent_no", 0),
				#(agent_get_player_id, ":agent_id_player", ":var_2"),
				#(neq, ":agent_id_player", ":var_2"),
				#(agent_is_human, ":var_2"), #New
				#(agent_is_non_player, ":var_2"), #Still crashes if using only this.
				(agent_get_team, ":team_var_2", ":var_2"),
				(this_or_next|eq, ":team_var_2", 1),
				(eq, ":team_var_2", 3),
				
###				(try_begin),
###					(neq, ":var_2", ":player_agent_no"),
###					(agent_clear_scripted_mode, ":var_2"), #Patched  to an extent #THIS BREAKS BELFRY AND LADDER SIEGES I THINK
###					(agent_force_rethink, ":var_2"), #Patched to an extent #THIS BREAKS BELFRY AND LADDER SIEGES I THINK
###				(try_end),

				#Crash is somewhere in here
				(try_begin),
					(le, "$do_the_oil", 5),
					(troop_get_slot, ":oil_array_relations_begin", "trp_oil_array", slot_troop_relations_begin),
					(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
						(troop_get_slot, ":oil_array_localvariable", "trp_oil_array", ":localvariable"),
						(scene_prop_has_agent_on_it, ":oil_array_localvariable", ":var_2"),
						(scene_prop_set_slot, ":oil_array_localvariable", 400, 1),
						(store_agent_hit_points, ":agent_hit_points_var_2_1", ":var_2", 1),
						(val_sub, ":agent_hit_points_var_2_1", 1),
						
						#Crash is somewhere below
						#(try_begin),
						#	(gt, ":agent_hit_points_var_2_1", 1),
						#	(agent_set_hit_points, ":var_2", ":agent_hit_points_var_2_1", 1),
						#(try_begin),
						#	(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100), #This crashes the game.
						#(try_end),
						
						
						##DEF WORKS NO CRASH BEGIN
						#(try_begin),
						#	(gt, ":agent_hit_points_var_2_1", 1),
						#	(agent_set_hit_points, ":var_2", ":agent_hit_points_var_2_1", 1),
						#(else_try),
						#	(agent_deliver_damage_to_agent, ":var_2", ":var_2", 1), #(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100),
						#(try_end),
						##DEFEND WORKS NO CRASH END
						
						#Possibly crashy begin
						
						(try_begin),
							(gt, ":agent_hit_points_var_2_1", 1),
							(agent_set_hit_points, ":var_2", ":agent_hit_points_var_2_1", 1),
						(else_try),
							(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100), #(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100),
						(try_end),
					
						
						#Possibly crashy end
						
						
						#Crash is somewhere above.
						
						#(try_begin),
						#	(eq, ":var_2", ":player_agent_no"),
						#	(display_message, "@You recieve damage from the hot oil spiled by the defenders on you!"),
						#(try_end),
						
					(try_end),
				(try_end),
				#Crash is somewhere in here
				
				#Crash is NOT from below.
				(neq, ":var_2", ":player_agent_no"),
				(agent_get_position, 0, ":var_2"),
				(troop_get_slot, ":oil_array_relations_begin", "trp_temp_array_c", slot_troop_relations_begin),
				(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
					(troop_get_slot, ":oil_array_localvariable", "trp_temp_array_c", ":localvariable"),
					(scene_prop_get_hit_points, ":agent_hit_points_var_2_1", ":oil_array_localvariable"),
					(gt, ":agent_hit_points_var_2_1", 0),
					(prop_instance_get_position, 1, ":oil_array_localvariable"),
					(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_0_1", 0, 1),
					(le, ":distance_between_positions_in_meters_0_1", 1),
					(store_random_in_range, ":random_in_range_0_101", 0, 101),
					(le, ":random_in_range_0_101", 60),
					(agent_set_look_target_position, ":var_2", 1),
					(agent_set_attack_action, ":var_2", 3, 0),
					(val_div, ":random_in_range_0_101", 10),
					(prop_instance_receive_damage, ":oil_array_localvariable", ":var_2", ":random_in_range_0_101"),
				(try_end),
			(try_end),
				#Crash is not from above
			
			(le, "$do_the_oil", 5),
			(troop_get_slot, ":oil_array_relations_begin", "trp_oil_array", slot_troop_relations_begin),
			(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
				(troop_get_slot, ":oil_array_localvariable", "trp_oil_array", ":localvariable"),
				(scene_prop_slot_eq, ":oil_array_localvariable", 400, 1),
				(prop_instance_get_position, 1, ":oil_array_localvariable"),
				(particle_system_burst, "psys_gourd_smoke", 1, 100),
				(position_move_z, 1, 500, 1),
				(particle_system_burst, "psys_oil", 1, 100),
#Add sound to burning oil was here instead of below
				(scene_prop_set_slot, ":oil_array_localvariable", 400, 0),
				#Add sound to burning Oil
				(neg|multiplayer_is_dedicated_server),
				(play_sound_at_position, "snd_oil_noise", 1),
				#(prop_instance_play_sound, ":oil_array_localvariable" "snd_oil_noise"),
				#End add sound to burning oil
			(try_end)
		]),

		#DEF BEgin
#		#Crash is somewhere in the oil code, perhaps because i removed agent_force_rethink, try adding it and see if it fixes the bug, while making sure it do sent affect belfry and ladder sieges
#		(1.0, 0.0, 0.0, #(1.0, 0.0, 0.0,
#		[],
#
#		[
#			(val_add, "$do_the_oil", 1),
#			(try_begin),
#				(gt, "$do_the_oil", 5),
#				(assign, "$do_the_oil", 0),
#			(try_end),
#			(get_player_agent_no, ":player_agent_no"),
##			(neq,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
#			(try_for_agents, ":var_2"),
#				(agent_is_alive, ":var_2"),
#				(agent_get_team, ":team_var_2", ":var_2"),
#				(this_or_next|eq, ":team_var_2", 1),
#				(eq, ":team_var_2", 3),
#				
####				(try_begin),
####					(neq, ":var_2", ":player_agent_no"),
####					(agent_clear_scripted_mode, ":var_2"), #Patched  to an extent #THIS BREAKS BELFRY AND LADDER SIEGES I THINK
####					(agent_force_rethink, ":var_2"), #Patched to an extent #THIS BREAKS BELFRY AND LADDER SIEGES I THINK
####				(try_end),
#
#				#Crash is somewhere in here
#				(try_begin),
#					(le, "$do_the_oil", 5),
#					(troop_get_slot, ":oil_array_relations_begin", "trp_oil_array", slot_troop_relations_begin),
#					(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
#						(troop_get_slot, ":oil_array_localvariable", "trp_oil_array", ":localvariable"),
#						(scene_prop_has_agent_on_it, ":oil_array_localvariable", ":var_2"),
#						(scene_prop_set_slot, ":oil_array_localvariable", 400, 1),
#						(store_agent_hit_points, ":agent_hit_points_var_2_1", ":var_2", 1),
#						(val_sub, ":agent_hit_points_var_2_1", 1),
#						
#						#Crash is somewhere below
#						#(try_begin),
#						#	(gt, ":agent_hit_points_var_2_1", 1),
#						#	(agent_set_hit_points, ":var_2", ":agent_hit_points_var_2_1", 1),
#						#(try_begin),
#						#	(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100), #This crashes the game.
#						#(try_end),
#						
#						
#						#DEF
#						(try_begin),
#							(gt, ":agent_hit_points_var_2_1", 1),
#							(agent_set_hit_points, ":var_2", ":agent_hit_points_var_2_1", 1),
#						(else_try),
#							(agent_deliver_damage_to_agent, ":var_2", ":var_2", 100),
#						(try_end),
#						#DEFEND
#						#Crash is somewhere above.
#						
#						#(try_begin),
#						#	(eq, ":var_2", ":player_agent_no"),
#						#	(display_message, "@You recieve damage from the hot oil spiled by the defenders on you!"),
#						#(try_end),
#						
#					(try_end),
#				(try_end),
#				#Crash is somewhere in here
#				
#				#Crash is NOT from below.
#				(neq, ":var_2", ":player_agent_no"),
#				(agent_get_position, 0, ":var_2"),
#				(troop_get_slot, ":oil_array_relations_begin", "trp_temp_array_c", slot_troop_relations_begin),
#				(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
#					(troop_get_slot, ":oil_array_localvariable", "trp_temp_array_c", ":localvariable"),
#					(scene_prop_get_hit_points, ":agent_hit_points_var_2_1", ":oil_array_localvariable"),
#					(gt, ":agent_hit_points_var_2_1", 0),
#					(prop_instance_get_position, 1, ":oil_array_localvariable"),
#					(get_distance_between_positions_in_meters, ":distance_between_positions_in_meters_0_1", 0, 1),
#					(le, ":distance_between_positions_in_meters_0_1", 1),
#					(store_random_in_range, ":random_in_range_0_101", 0, 101),
#					(le, ":random_in_range_0_101", 60),
#					(agent_set_look_target_position, ":var_2", 1),
#					(agent_set_attack_action, ":var_2", 3, 0),
#					(val_div, ":random_in_range_0_101", 10),
#					(prop_instance_receive_damage, ":oil_array_localvariable", ":var_2", ":random_in_range_0_101"),
#				(try_end),
#			(try_end),
#				#Crash is not from above
#			
#			(le, "$do_the_oil", 5),
#			(troop_get_slot, ":oil_array_relations_begin", "trp_oil_array", slot_troop_relations_begin),
#			(try_for_range, ":localvariable", 1, ":oil_array_relations_begin"),
#				(troop_get_slot, ":oil_array_localvariable", "trp_oil_array", ":localvariable"),
#				(scene_prop_slot_eq, ":oil_array_localvariable", 400, 1),
#				(prop_instance_get_position, 1, ":oil_array_localvariable"),
#				(particle_system_burst, "psys_gourd_smoke", 1, 100),
#				(position_move_z, 1, 500, 1),
#				(particle_system_burst, "psys_oil", 1, 100),
#				#Add sound to burning Oil
#				(play_sound_at_position, "snd_oil_noise", 1),
#				#(prop_instance_play_sound, ":oil_array_localvariable" "snd_oil_noise"),
#				#End add sound to burning oil
#				(scene_prop_set_slot, ":oil_array_localvariable", 400, 0),
#			(try_end)
#		]),
		#Def End
		
		(-19.0, 0.0, 0.0,
		[
		(multiplayer_is_server),
		],

		[
			(assign, ":value", 1),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_earth_gate"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_earth_gate", ":localvariable"),
				(troop_set_slot, "trp_temp_array_c", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_portcullis"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_portcullis", ":localvariable"),
				(troop_set_slot, "trp_temp_array_c", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_tavern_door_a"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_tavern_door_a", ":localvariable"),
				(troop_set_slot, "trp_temp_array_c", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_tavern_door_b"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_tavern_door_b", ":localvariable"),
				(troop_set_slot, "trp_temp_array_c", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_castle_f_door_a"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_castle_f_door_a", ":localvariable"),
				(troop_set_slot, "trp_temp_array_c", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(troop_set_slot, "trp_temp_array_c", slot_troop_relations_begin, ":value"),
			(assign, ":value", 1),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_hit_spot_2m"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_hit_spot_2m", ":localvariable"),
				(troop_set_slot, "trp_oil_array", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(scene_prop_get_num_instances, ":scene_prop_num_instances_1257_earth_gate", "spr_1257_hit_spot_4m"),
			(try_for_range, ":localvariable", 0, ":scene_prop_num_instances_1257_earth_gate"),
				(scene_prop_get_instance, ":scene_prop_instance_1257_earth_gate_localvariable", "spr_1257_hit_spot_4m", ":localvariable"),
				(troop_set_slot, "trp_oil_array", ":value", ":scene_prop_instance_1257_earth_gate_localvariable"),
				(val_add, ":value", 1),
				(scene_prop_set_team, ":scene_prop_instance_1257_earth_gate_localvariable", 2),
			(try_end),
			(troop_set_slot, "trp_oil_array", slot_troop_relations_begin, ":value"),
			(assign, "$do_the_oil", 0)
		]),

		#(-25.0, 0.0, 0.0,
		#[],
        #
		#[
		#	(store_trigger_param_1, ":trigger_param_1"),
		#	(agent_get_team, ":team_trigger_param_1", ":trigger_param_1"),
		#	(agent_get_troop_id, ":troop_id_trigger_param_1", ":trigger_param_1"),
		#	(try_begin),
		#		(troop_is_guarantee_ranged, ":troop_id_trigger_param_1"),
		#		(agent_set_division, ":trigger_param_1", 1),
		#	(else_try),
		#		(agent_set_division, ":trigger_param_1", 0),
		#	(try_end)
		#]),
###########
###########
###########
###########
###########

###########		#(-19.0, 0.0, 0.0,
###########		#[],
###########        #
###########		#[]),
###########
###########
###########
###########
###########
###########
###########
###########
###########
###########




		(2.0, 0.0, 0.0,
		[(multiplayer_is_server),],

		[
			(get_player_agent_no, ":player_agent_no"),
			(gt,  ":player_agent_no", -1), #NEWLY PATCHED CHECK REST OF SCRIPT TO ENSURE THERE ARENT ANY CONTRADICTING COMMENTS.
			(try_for_agents, ":var_2"),
				(agent_is_human, ":var_2"),
				(agent_is_non_player, ":var_2"), ##Added to prevent player from switching weapons
				(neq, ":player_agent_no", ":var_2"),
				(agent_slot_eq, ":var_2", 100, 0),
				(agent_is_alive, ":var_2"),
				(agent_get_ammo, ":ammo_var_2", ":var_2"),
				(gt, ":ammo_var_2", 0),
				(agent_get_team, ":team_var_2", ":var_2"),
				(this_or_next|neq, ":team_var_2", "$attacker_team"),
				(neq, ":team_var_2", "$attacker_team_2"),
				(call_script, "script_get_closest_enemy_distance_new", ":var_2", ":team_var_2", 150),
				(assign, ":var_5", reg1),
				(gt, ":var_5", 150),
				(agent_get_troop_id, ":troop_id_var_2", ":var_2"),
				(troop_is_guarantee_ranged, ":troop_id_var_2"),
				#Removedforunassignedstuff#(agent_get_division, ":division_var_2", ":var_2"), #Removedforunassignedstuff#
				#(team_get_hold_fire_order, ":hold_fire_order_team_var_2_division_var_2", ":team_var_2", ":division_var_2"), #Patched to an extent
				#Removedforunassignedstuff#(neq, ":hold_fire_order_team_var_2_division_var_2", 1), #Removedforunassignedstuff#
				(agent_get_wielded_item, ":wielded_item_var_2_0", ":var_2", 0),
				(is_between, ":wielded_item_var_2_0", 1, "itm_cross_end"), #Previously itm_items_end
				(item_get_type, ":type_wielded_item_var_2_0", ":wielded_item_var_2_0"),
				(this_or_next|neq, ":type_wielded_item_var_2_0", 10),
				(this_or_next|neq, ":type_wielded_item_var_2_0", 9),
				(neq, ":type_wielded_item_var_2_0", 8),
				(assign, ":value", 4),
				(try_for_range, reg0, 0, ":value"),
					(agent_get_item_slot, ":item_slot_var_2_reg0", ":var_2", reg0),
					(is_between, ":item_slot_var_2_reg0", 1, "itm_cross_end"), #Previously itm_items_end
					(item_get_type, ":type_wielded_item_var_2_0", ":item_slot_var_2_reg0"),
					(this_or_next|eq, ":type_wielded_item_var_2_0", 10),
					(this_or_next|eq, ":type_wielded_item_var_2_0", 8),
					(eq, ":type_wielded_item_var_2_0", 9),
					(agent_set_wielded_item, ":var_2", ":item_slot_var_2_reg0"),
					(assign, ":value", -1),
				(try_end),
			(try_end)
		]),
	#Doghotel begin
#		   (ti_before_mission_start, 0, 0, 
#    [],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (assign, ":var0", 0),
#      (try_begin),
#        (neq, "$g_doghotel_version_id", 3),
#        (assign, ":var0", 1),
#      (try_end),
#      (call_script, "script_doghotel_initialize_bot_globals", ":var0"),
#    ]),
#
#    (0.5, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_special_actions"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_distance_calculations"),
#      (call_script, "script_doghotel_combat_loop"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (key_clicked, 63),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (try_begin),
#        (neg|is_presentation_active, "prsnt_doghotel_configure"),
#        (try_begin),
#          (neg|game_in_multiplayer_mode),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (else_try),
#          (game_in_multiplayer_mode),
#          (eq, "$g_doghotel_multiplayer_brainy_bots_installed_on_server", 1),
#          (multiplayer_get_my_player, ":var0"),
#          (player_is_admin, ":var0"),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (try_end),
#      (try_end),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (gt, "$g_doghotel_prsnt_configure_close", 0),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (call_script, "script_doghotel_configure_close"),
#    ]),
		
#			    (ti_before_mission_start, 0, 0, 
#    [],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (assign, ":var0", 0),
#      (try_begin),
#        (neq, "$g_doghotel_version_id", 3),
#        (assign, ":var0", 1),
#      (try_end),
#      (call_script, "script_doghotel_initialize_bot_globals", ":var0"),
#    ]),
#
#    (0.5, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_special_actions"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (eq, "$g_doghotel_enable_brainy_bots", 1),
#    ],
#    [
#      (this_or_next|multiplayer_is_server),
#      (neg|game_in_multiplayer_mode),
#      (call_script, "script_doghotel_distance_calculations"),
#      (call_script, "script_doghotel_combat_loop"),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (key_clicked, 63),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (try_begin),
#        (neg|is_presentation_active, "prsnt_doghotel_configure"),
#        (try_begin),
#          (neg|game_in_multiplayer_mode),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (else_try),
#          (game_in_multiplayer_mode),
#          (eq, "$g_doghotel_multiplayer_brainy_bots_installed_on_server", 1),
#          (multiplayer_get_my_player, ":var0"),
#          (player_is_admin, ":var0"),
#          (omit_key_once, 63),
#          (start_presentation, "prsnt_doghotel_configure"),
#        (try_end),
#      (try_end),
#    ]),
#
#    (0, 0, 0, 
#    [
#      (gt, "$g_doghotel_prsnt_configure_close", 0),
#    ],
#    [
#      (neg|multiplayer_is_dedicated_server),
#      (call_script, "script_doghotel_configure_close"),
#    ]),
#			
#			
#	(ti_before_mission_start, 0, ti_once, 
#    [],
#    [
#      (multiplayer_is_server),
#      (call_script, "script_doghotel_initialize_mp_globals", 0),
#    ]),
#
#    (60, 0, 0, 
#    [],
#    [
#      (multiplayer_is_server),
#      (val_add, "$g_doghotel_brainy_message_timer", 1),
#      (try_begin),
#        (gt, "$g_doghotel_brainy_message_interval", 1),
#        (ge, "$g_doghotel_brainy_message_timer", "$g_doghotel_brainy_message_interval"),
#        (assign, "$g_doghotel_brainy_message_timer", 0),
#        (str_store_string, s1, "str_doghotel_brainy_bots_server_message"),
#        (call_script, "script_doghotel_server_message"),
#      (try_end),
#    ]),
#
#    (0.5, 0, 0, 
#    [
#      (eq, "$g_doghotel_anti_autoblock", 1),
#      (server_get_control_block_dir, ":var0"),
#      (eq, ":var0", 1),
#    ],
#    [
#      (multiplayer_is_server),
#      (server_set_control_block_dir, 1),
#    ]),
#Doghotel end
	]# + crouching_triggers
	),

]