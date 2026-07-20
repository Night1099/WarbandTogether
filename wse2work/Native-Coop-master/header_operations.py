################################################################################
#                                           header_operations expanded v.1.0.3 #
#                    based on header_operations expanded v.1.0.1 by Lav and    #
#                    based on header_operations for VC v.0.1.0 by Kalarhan and #
#                    based on header_operations expanded v.1.0.2 by Vetrogor   #
#                    integrated new defined operations by Winter               #
################################################################################
# TABLE OF CONTENTS
################################################################################
#
# [ Z00 ] Introduction and Credits.
# [ Z01 ] Operation Modifiers.
# [ Z02 ] Flow Control.
# [ Z03 ] Mathematical Operations.
# [ Z04 ] Script/Trigger Parameters and Results.
# [ Z05 ] Keyboard and Mouse Input.
# [ Z06 ] World Map.
# [ Z07 ] Game Settings.
# [ Z08 ] Factions.
# [ Z09 ] Parties and Party Templates.
# [ Z10 ] Troops.
# [ Z11 ] Quests.
# [ Z12 ] Items.
# [ Z13 ] Sounds and Music Tracks.
# [ Z14 ] Positions.
# [ Z15 ] Game Notes.
# [ Z16 ] Tableaus and Heraldics.
# [ Z17 ] String Operations.
# [ Z18 ] Output And Messages.
# [ Z19 ] Game Control: Screens, Menus, Dialogs and Encounters.
# [ Z20 ] Scenes and Missions.
# [ Z21 ] Scene Props and Prop Instances.
# [ Z22 ] Agents and Teams.
# [ Z23 ] Presentations.
# [ Z24 ] Multiplayer And Networking.
# [ Z25 ] Remaining Esoteric Stuff.
# [ Z26 ] Hardcoded Compiler-Related Code.
#
################################################################################

################################################################################
# [ Z00 ] INTRODUCTION AND CREDITS
################################################################################
   # Everyone who has ever tried to mod Mount&Blade games knows perfectly well,
   # that the documentation for its Module System is severely lacking. Warband
   # Module System, while introducing many new and useful operations, did not
   # improve considerably in the way of documentation. What's worse, a number of
   # outright errors and inconsistencies appeared between what was documented in
   # the comments to the header_operations.py file (which was the root source of
   # all Warband scripting documentation, whether you like it or not), and what
   # was actually implemented in the game engine.

   # Sooner or later someone was bound to dedicate some time and effort to fix
   # this problem by properly documenting the file. It just so happened that I
   # was the first person crazy enough to accept the challenge.

   # I have tried to make this file a self-sufficient source of information on
   # every operation that the Warband scripting engine knows of. Naturally I
   # failed - there are still many operations for which there is simply not
   # enough information, or operations with effects that have not yet been
   # thoroughly tested and confirmed. But as far as I know, there is currently
   # no other reference more exhaustive than this. I tried to make the file
   # useful to both seasoned scripters and complete newbies, and to a certain
   # degree this file can even serve as a tutorial into Warband scripting -
   # though it still won't replace the wealth of tutorials produced by the
   # Warband modding community.

   # I really hope you will find it useful as well.

   #                                    Alexander Lomski AKA Lav. Jan 18th, 2012.

   # And the credits.

   # First of all, I should credit Taleworlds for the creation of this game and
   # its Module System. Without them, I wouldn't be able to work on this file
   # so even though I'm often sceptical about their programming style and quality
   # of their code, they still did a damn good job delivering this game to all
   # of us.

   # And then I should credit many members from the Warband modding community
   # who have shared their knowledge and helped me clear out many uncertainties
   # and inconsistencies. Special credits (in no particular order) go to
   # cmpxchg8b, Caba'drin, SonKidd, MadVader, dunde, Ikaguia, MadocComadrin,
   # Cjkjvfnby, shokkueibu.

   # Original work by Lav for version 1.166 of the game (published in 2015)
   # https://forums.taleworlds.com/index.php?threads/warband-module-system-1-166-with-tweaks-and-giggles.324874/
   #
   # Updated by Vetrogor
   # https://forums.taleworlds.com/index.php?threads/better-ms-scripting-reference-header_operations-expanded.213060/page-3#post-9410628
   #
   # Updated for engine 1.171 by Kalarhan for use with VC mods
   # https://raw.githubusercontent.com/KalarhanWB/VC_Tweaks_Tool/master/app/header_operations.py
   # https://github.com/KalarhanWB/VC_Tweaks_Tool/blob/master/app/header_operations.py

   # Additional credits (in no particular order) go to
   # K700, Vetrogor, Burspa, Winter, fisheye, Hellequin, Veni Vidi Vici

################################################################################
# [ Z01 ] OPERATION MODIFIERS
################################################################################

neg          = 0x80000000  # (neg|<operation_name>, ...),
                           # Used in combination with conditional operations to invert their results.
this_or_next = 0x40000000  # (this_or_next|<operation_name>, ...),
                           # Used in combination with conditional operations to group them into OR blocks.

################################################################################
# [ Z02 ] FLOW CONTROL
################################################################################

call_script             =    1  # (call_script, <script_id>, [<script_param>...]),
                                # Calls specified script with or without parameters. Maximum number of parameters you can pass with the operation is 16.
try_begin               =    4  # (try_begin),
                                # Opens a conditional block.
else_try                =    5  # (else_try),
                                # If conditional operations in the conditional block before fail, this block of code will be executed, given that there are no conditional operations in this block or that they don't fail. Works also within try_for_agents and try_for_range.
else_try_begin          =    5  # (else_try_begin),
                                # Deprecated form of (else_try).
try_end                 =    3  # (try_end),
                                # Concludes a conditional block or a cycle.
end_try                 =    3  # (end_try),
                                # Deprecated form of (try_end),
try_for_range           =    6  # (try_for_range, <destination>, <lower_bound>, <upper_bound>),
                                # Iterates from the <lower bound> to <<upper bound> -1>. <destination> is the variable iterated in the loop, which always increments to the next value at the end of the loop. Break the loop by lowering the upper bound.
try_for_range_backwards =    7  # (try_for_range_backwards, <destination>, <lower_bound>, <upper_bound>),
                                # Iterates from <<upper bound> - 1> to the <lower bound>. <destination> is the variable iterated in the loop, which always decrements to the next value at the end of the loop. Break the loop by increasing the lower bound.
try_for_parties         =   11  # (try_for_parties, <destination>),
                                # Runs a cycle, iterating all parties on the map.
try_for_agents          =   12  # (try_for_agents, <destination>, [<position_no>], [<radius_fixed_point>]),
                                # Runs a cycle, iterating all active agents on the scene. Iteration works for active agents alive and dead, with optional parameters it only checks for those within the radius around the position. Don't use check agent_is_active. It will always return true.
                                # Avoid using pos0. This will pass zero to the second argument and radius and position will be skipped. Like position was ommited.
try_for_prop_instances  =   16  # (try_for_prop_instances, <destination>, [<object_id>], [<object_type>]), 
                                # Version 1.161+. Runs a cycle, iterating all valid scene prop instances on the scene. If <object_id> = <scene_prop_id> and <object_type> is not given, it loops through all instances. For object types see list of "somt_" in module_constants.py 
try_for_players         =   17  # (try_for_players, <destination>, [skip_server]),
                                # Version 1.165+. Iterates through all active players in a multiplayer game. Set optional parameter to 1 to skip server player entry.

################################################################################
# [ Z03 ] MATHEMATICAL OPERATIONS
################################################################################

  # Mathematical operations deal with numbers. Warband Module System can only
  # deal with integers. Floating point numbers are emulated by the so-called
  # "fixed point numbers". Wherever you encounter a fixed point parameter for
  # some Module System operation, keep in mind that it is actually just a
  # regular integer number, HOWEVER it is supposed to represent a floating
  # point number equal to fixed_point_number / fixed_point_multiplier. As you
  # might have guessed, to convert a floating point number to fixed point, you
  # have to multiply it by fixed_point_multiplier. You can change the value of
  # multiplier with the operation (set_fixed_point_multiplier), thus influencing
  # the precision of all operations dealing with fixed point numbers.

  # A notion very important for Warband modding is that you reference all
  # Warband objects by their numeric values. In other words, you can do maths
  # with your items, troops, agents, scenes, parties et cetera. This is used
  # extensively in the code, so don't be surprised to see code looking like
  # (store_add, ":value", "itm_pike", 4). This code is just calculating a
  # reference to an item which is located 4 positions after "itm_pike" inside
  # the module_items.py file.

# Conditional operations

gt                         = 32      # (gt, <value1>, <value2>),
                                     # Checks that value1 > value2
ge                         = 30      # (ge, <value1>, <value2>),
                                     # Checks that value1 >= value2
eq                         = 31      # (eq, <value1>, <value2>),
                                     # Checks that value1 == value2
neq                        = neg|eq  # (neq, <value1>, <value2>),
                                     # Checks that value1 != value2
le                         = neg|gt  # (le, <value1>, <value2>),
                                     # Checks that value1 <= value2
lt                         = neg|ge  # (lt, <value1>, <value2>),
                                     # Checks that value1 < value2
is_between                 = 33      # (is_between, <value>, <lower_bound>, <upper_bound>),
                                     # Checks that lower_bound <= value < upper_bound

# Mathematical and assignment operations

assign                     = 2133    # (assign, <destination>, <value>),
                                     # Directly assigns a value to a variable or register.

store_add                  = 2120    # (store_add, <destination>, <value>, <value>),
                                     # Assigns <destination> := <value> + <value>
store_sub                  = 2121    # (store_sub, <destination>, <value>, <value>),
                                     # Assigns <destination> := <value> - <value>
store_mul                  = 2122    # (store_mul, <destination>, <value>, <value>),
                                     # Assigns <destination> := <value> * <value>
store_div                  = 2123    # (store_div, <destination>, <value>, <value>),
                                     # Assigns <destination> := <value> / <value>
                                     # Fractional part will be truncated. Negative values will be rounded up.
store_mod                  = 2119    # (store_mod, <destination>, <value>, <value>),
                                     # Assigns <destination> := <value> MOD <value>
val_add                    = 2105    # (val_add, <destination>, <value>),
                                     # Assigns <destination> := <destination> + <value>
val_sub                    = 2106    # (val_sub, <destination>, <value>),
                                     # Assigns <destination> := <destination> - <value>
val_mul                    = 2107    # (val_mul, <destination>, <value>),
                                     # Assigns <destination> := <destination> * <value>
val_div                    = 2108    # (val_div, <destination>, <value>),
                                     # Assigns <destination> := <destination> / <value>
                                     # Fractional part will be truncated. Negative values will be rounded up.
val_mod                    = 2109    # (val_mod, <destination>, <value>),
                                     # Assigns <destination> := <destination> MOD <value>

val_min                    = 2110    # (val_min, <destination>, <value>),
                                     # Assigns <destination> := MIN (<destination>, <value>)
val_max                    = 2111    # (val_max, <destination>, <value>),
                                     # Assigns <destination> := MAX (<destination>, <value>)
val_clamp                  = 2112    # (val_clamp, <destination>, <lower_bound>, <upper_bound>),
                                     # Enforces <destination> value to be within <lower_bound>..<upper_bound>-1 range. Whatever value the first argument may have had before, it won't be lower than the second argument (the minimum value) and it will be strictly less than the third argument (the maximum value).
                                     # This is 100% equivalent to calling (val_min, <value>, (<upper_bound> - 1)), then (val_max, <value>, <lower_bound>).
                                     # Instead of maintaining careful "data range integrity" throughout a series of operations, reasoning out by what means it could escape its expected bounds and covering those individually, you can insert this operation and ensure that it will produce an answer within the range you are looking for.
val_abs                    = 2113    # (val_abs, <destination>),
                                     # Assigns <destination> := ABS (<destination>)

store_or                   = 2116    # (store_or, <destination>, <value>, <value>),
                                     # Binary OR
store_and                  = 2117    # (store_and, <destination>, <value>, <value>),
                                     # Binary AND
val_or                     = 2114    # (val_or, <destination>, <value>),
                                     # Binary OR, overwriting first operand.
val_and                    = 2115    # (val_and, <destination>, <value>),
                                     # Binary AND, overwriting first operand.
val_lshift                 = 2100    # (val_lshift, <destination>, <value>),
                                     # Bitwise shift left (dest = dest * 2 ^ value)
val_rshift                 = 2101    # (val_rshift, <destination>, <value>),
                                     # Bitwise shift right (dest = dest / 2 ^ value)

store_sqrt                 = 2125    # (store_sqrt, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := SQRT (value)
store_pow                  = 2126    # (store_pow, <destination_fixed_point>, <value_fixed_point>, <power_fixed_point),
                                     # Assigns dest := value ^ power
store_sin                  = 2127    # (store_sin, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := SIN (value)
store_cos                  = 2128    # (store_cos, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := COS (value)
store_tan                  = 2129    # (store_tan, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := TAN (value)
store_asin                 = 2140    # (store_asin, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := ARCSIN (value)
store_acos                 = 2141    # (store_acos, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := ARCCOS (value)
store_atan                 = 2142    # (store_atan, <destination_fixed_point>, <value_fixed_point>),
                                     # Assigns dest := ARCTAN (value)
store_atan2                = 2143    # (store_atan2, <destination_fixed_point>, <y_fixed_point>, <x_fixed_point>),
                                     # Returns the angle between the x axis and a point with coordinates (X,Y) in degrees. Note the angle is calculated counter-clockwise, i.e. (1,1) will return 45, not -45.

# Random number generation

store_random               = 2135    # (store_random, <destination>, <upper_range>),
                                     # Stores a random value in the range of 0..<upper_range>-1. Deprecated, use (store_random_in_range) instead.
store_random_in_range      = 2136    # (store_random_in_range, <destination>, <range_low>, <range_high>),
                                     # Stores a random value in the range of <range_low>..<range_high>-1.
shuffle_range              = 2134    # (shuffle_range, <reg_no>, <reg_no>),
                                     # Randomly shuffles a range of registers, reordering the values contained in them. Commonly used for list randomization.

# Fixed point values handling

set_fixed_point_multiplier = 2124    # (set_fixed_point_multiplier, <value>),
                                     # Affects all operations dealing with fixed point numbers. Default value is 1.
convert_to_fixed_point     = 2130    # (convert_to_fixed_point, <destination_fixed_point>),
                                     # Converts integer value to fixed point (multiplies by the fixed point multiplier).
convert_from_fixed_point   = 2131    # (convert_from_fixed_point, <destination>),
                                     # Converts fixed point value to integer (divides by the fixed point multiplier).

################################################################################
# [ Z04 ] SCRIPT/TRIGGER PARAMETERS AND RESULTS
################################################################################

  # Many scripts can accept additional parameters, and many triggers have some
  # parameters of their own (as details in header_triggers.py file). You can
  # only pass numeric values as parameters. Since string constants are also
  # Warband objects, you can pass them as well, and you can also pass string
  # or position registers. However you cannot pass quick strings (string
  # defined directly in the code).

  # You can declare your scripts with as many parameters as you wish. Triggers,
  # however, are always called with their predefined parameters. The old restriction
  # that the game engine does not support more than 3 parameters per trigger does not
  # apply anymore as can be seen at ti_on_agent_hit. You might still see some triggers
  # receiving extra information which could not be fit into the old three parameters
  # restriction in numeric, string or position registers.

  # Some triggers and scripts called from the game engine (those have names
  # starting with "game_") expect you to return some value to the game engine.
  # That value may be either a number or a string and is set by special
  # operations listed below. Scripts called from the Module System, however,
  # typically use registers to store their return data.

  # Note that if you call a script from a trigger, you can still use operations
  # to retrieve trigger's calling parameters, and they will retrieve values that
  # have been passed to the trigger, not values that have been passed to the
  # script.

store_script_param_1        =   21  # (store_script_param_1, <destination>),
                                    # Retrieve the value of the first script parameter. If the script was called without this parameter being specified, this operation assigns a zero.
store_script_param_2        =   22  # (store_script_param_2, <destination>),
                                    # Retrieve the value of the second script parameter. If the script was called without this parameter being specified, this operation assigns a zero.
store_script_param          =   23  # (store_script_param, <destination>, <script_param_index>),
                                    # Retrieve the value of arbitrary script parameter (generally used when script accepts more than two). Parameters are enumerated starting from 1. Maximum are 15 parameters (16 operands maximum - 1 operand with script name). If the script was called without this parameter being specified, this operation assigns a zero.
set_result_string           =   60  # (set_result_string, <string>),
                                    # Sets the return value of a game_* script, when a string value is expected by game engine.

store_trigger_param_1       = 2071  # (store_trigger_param_1, <destination>),
                                    # Retrieve the value of the first trigger parameter. Will retrieve trigger's parameters even when called from inside a script, for as long as that script is running within trigger context.
store_trigger_param_2       = 2072  # (store_trigger_param_2, <destination>),
                                    # Retrieve the value of the second trigger parameter. Will retrieve trigger's parameters even when called from inside a script, for as long as that script is running within trigger context.
store_trigger_param_3       = 2073  # (store_trigger_param_3, <destination>),
                                    # Retrieve the value of the third trigger parameter. Will retrieve trigger's parameters even when called from inside a script, for as long as that script is running within trigger context.
store_trigger_param         = 2070  # (store_trigger_param, <destination>, <trigger_param_no>),
                                    # Version 1.153+. Retrieve the value of arbitrary trigger parameter. Parameters are enumerated starting from 1. Will retrieve trigger's parameters even when called from inside a script, for as long as that script is running within trigger context.
get_trigger_object_position =  702  # (get_trigger_object_position, <position>),
                                    # Retrieve the position of an object which caused the trigger to fire (when appropriate).
set_trigger_result          = 2075  # (set_trigger_result, <value>),
                                    # Sets the return value of a trigger or game_* script, when an integer value is expected by game engine.

################################################################################
# [ Z05 ] KEYBOARD AND MOUSE INPUT
################################################################################

  # The game provides modders with limited ability to control keyboard input and
  # mouse movements. It is also possible to tamper with game keys (i.e. keys
  # bound to specific game actions), including the ability to override game's
  # reaction to those keys. Note that mouse buttons are keys too, and can be
  # detected with the corresponding operations.

# Conditional operations

key_is_down                     = 70  # (key_is_down, <key_code>),
                                      # Checks if the specified key is clicked in the current frame, ignoring if it was clicked in the previous frame. Is true in every frame that the key is down. See header_triggers.py for key code reference.
key_clicked                     = 71  # (key_clicked, <key_code>),
                                      # Checks if the specified key is clicked in the current frame and wasn't clicked in the previous frame. Is only true in the one frame where the engine first recognizes that the key is pressed. See header_triggers.py for key code reference. Will work reliably only on mission template triggers that happen on every frame (i.e. check interval 0) as well as on simple_triggers or old form triggers that are check interval 0 too.
game_key_is_down                = 72  # (game_key_is_down, <game_key_code>),
                                      # Checks if the specified key is clicked in the current frame, ignoring if it was clicked in the previous frame. Is true in every frame that the key is down. See header_triggers.py for game key code reference.
game_key_clicked                = 73  # (game_key_clicked, <game_key_code>),
                                      # Checks if the specified key is clicked in the current frame and wasn't clicked in the previous frame. Is only true in the one frame where the engine first recognizes that the key is pressed. See header_triggers.py for game key code reference. Will work reliably only on mission template triggers that happen on every frame (i.e. check interval 0) as well as on simple_triggers or old form triggers that are check interval 0 too.

# Generic operations

omit_key_once                   = 77  # (omit_key_once, <key_code>),
                                      # Forces the game to ignore default bound action for the specified key on next press. Some keys can't be omited. Keys that can be omited:
                                      # gk_everyone_hear, gk_infantry_hear, gk_archers_hear, gk_cavalry_hear, gk_group0_hear = gk_infantry_hear, gk_group1_hear = gk_archers_hear, gk_group2_hear = gk_cavalry_hear
                                      # gk_group3_hear, gk_group4_hear, gk_group5_hear, gk_group6_hear, gk_group7_hear, gk_group8_hear, gk_reverse_order_group, gk_everyone_around_hear
                                      # gk_action (mount, dismount fail, picking weapon from the ground works), gk_kick, gk_toggle_weapon_mode, gk_sheath_weapon, gk_cam_toggle, gk_crouch (need to set can_crouch = 1 in module.ini)
                                      # key_mouse_scroll_up, key_mouse_scroll_down, key_space, key_pad or key_xbox (from 0xF0 to 0xFF - possible works for all),
                                      # You can bypass F1-F8 menu with the operation (close_order_menu),
clear_omitted_keys              = 78  # (clear_omitted_keys),
                                      # Clears all omitted keys.

mouse_get_position              = 75  # (mouse_get_position, <position>),
                                      # Stores mouse x and y coordinates in the specified position.

################################################################################
# [ Z06 ] WORLD MAP
################################################################################

  # Generally, all operations which only make sense on the worldmap and have no
  # specific category have been assembled here. These mostly deal with weather,
  # time and resting.

# Conditional operations

is_currently_night         = 2273  # (is_currently_night),
                                   # Checks that it's currently night in the game.
map_free                   =   37  # (map_free),
                                   # Checks that the player is currently on the global map and no game screens are open.

# Weather-handling operations

get_global_cloud_amount    =   90  # (get_global_cloud_amount, <destination>),
                                   # Returns current cloudiness (a value between 0..100).
set_global_cloud_amount    =   91  # (set_global_cloud_amount, <value>),
                                   # Sets current cloudiness (value is clamped to 0..100).
get_global_haze_amount     =   92  # (get_global_haze_amount, <destination>),
                                   # Returns current fogginess (value between 0..100).
set_global_haze_amount     =   93  # (set_global_haze_amount, <value>),
                                   # Sets current fogginess (value is clamped to 0..100).

# Time-related operations

store_current_hours        = 2270  # (store_current_hours, <destination>),
                                   # Stores number of hours that have passed since beginning of the game. Commonly used to track time when accuracy up to hours is required.
store_time_of_day          = 2271  # (store_time_of_day, <destination>),
                                   # Stores current day hour (value in 0..24 range).
store_current_day          = 2272  # (store_current_day, <destination>),
                                   # Stores number of days that have passed since beginning of the game. Commonly used to track time when high accuracy is not required.

rest_for_hours             = 1030  # (rest_for_hours, <rest_time_in_hours>, [time_speed_multiplier], [remain_attackable]),
                                   # Forces the player party to rest for specified number of hours. Time can be accelerated and player can be made immune or subject to attacks.
rest_for_hours_interactive = 1031  # (rest_for_hours_interactive, <rest_time_in_hours>, [time_speed_multiplier], [remain_attackable]),
                                   # Forces the player party to rest for specified number of hours. Player can break the rest at any moment. Time can be accelerated and player can be made immune or subject to attacks.

################################################################################
# [ Z07 ] GAME SETTINGS AND STATISTICS
################################################################################

  # This group of operations allows you to retrieve some of the game settings
  # as configured by the player on Options page, and change them as necessary
  # (possibly forcing a certain level of difficulty on the player). Operations
  # dealing with achievements (an interesting, but underdeveloped feature of
  # Warband) are also placed in this category.

# Conditional operations

is_trial_version                      =  250  # (is_trial_version),
                                              # Checks if the game is in trial mode (has not been purchased). Player cannot get higher than level 6 in this mode.
is_edit_mode_enabled                  =  255  # (is_edit_mode_enabled),
                                              # Version 1.153+. Checks if Edit Mode is currently enabled in the game. Useful for making additions to the default UI.
is_cheat_mode_enabled                 =   53  # (is_cheat_mode_enabled),
                                              # Checks if Cheat Mode is currently enabled in-game via tick at "Enable Cheats" in the launcher.

# Generic operations

get_operation_set_version             =   55  # (get_operation_set_version, <destination>),
                                              # Version 1.165+. 4research. Apparently returns the current version of Module System operations set, allowing transparent support for multiple Warband engine versions.
set_player_troop                      =   47  # (set_player_troop, <troop_id>),
                                              # Changes the troop player controls. Generally used in quick-battle scenarios to give player a predefined character.
show_object_details_overlay           =  960  # (show_object_details_overlay, <value>),
                                              # Turns various popup tooltips on (value = 1) and off (value = 0). This includes agent names and dropped item names during missions, item stats in inventory on mouse over, etc.
auto_save                             =  985  # (auto_save),
                                              # Version 1.161+. Saves the game to the current save slot.
allow_ironman                         =  988  # (allow_ironman, <value>), 
                                              # 1 = allow, 0 = disallow. Used on new games to disable realistic mode.

# Access to game options

options_get_damage_to_player          =  260  # (options_get_damage_to_player, <destination>),
                                              # 0 = 1/4, 1 = 1/2, 2 = 1/1
options_set_damage_to_player          =  261  # (options_set_damage_to_player, <value>),
                                              # 0 = 1/4, 1 = 1/2, 2 = 1/1
options_get_damage_to_friends         =  262  # (options_get_damage_to_friends, <destination>),
                                              # 0 = 1/2, 1 = 3/4, 2 = 1/1
options_set_damage_to_friends         =  263  # (options_set_damage_to_friends, <value>),
                                              # 0 = 1/2, 1 = 3/4, 2 = 1/1
options_get_combat_ai                 =  264  # (options_get_combat_ai, <destination>),
                                              # 0 = good, 1 = average, 2 = poor
options_set_combat_ai                 =  265  # (options_set_combat_ai, <value>),
                                              # 0 = good, 1 = average, 2 = poor
game_get_reduce_campaign_ai           =  424  # (game_get_reduce_campaign_ai, <destination>),
                                              # Deprecated operation. Use options_get_campaign_ai instead
options_get_campaign_ai               =  266  # (options_get_campaign_ai, <destination>),
                                              # 0 = good, 1 = average, 2 = poor
options_set_campaign_ai               =  267  # (options_set_campaign_ai, <value>),
                                              # 0 = good, 1 = average, 2 = poor
options_get_combat_speed              =  268  # (options_get_combat_speed, <destination>),
                                              # 0 = slowest, 1 = slower, 2 = normal, 3 = faster, 4 = fastest
options_set_combat_speed              =  269  # (options_set_combat_speed, <value>),
                                              # 0 = slowest, 1 = slower, 2 = normal, 3 = faster, 4 = fastest
options_get_battle_size               =  270  # (options_get_battle_size, <destination>),
                                              # Version 1.161+. Retrieves current battle size slider value (in the range of 0..1000). Note that this is the slider value, not the battle size itself.
options_set_battle_size               =  271  # (options_set_battle_size, <value>),
                                              # Version 1.161+. Sets battle size slider to provided value (in the range of 0..1000). Note that this is the slider value, not the battle size itself.
                                              # To change the real battlesize the entry string at the begining of the mission templates needs to get changed. Multiplier start from 1.25 to 5.25 according to options slider.
                                              # (1, mtef_team_0|mtef_defenders, 0, aif_start_alarmed, 40, []),
                                              # Battle reinforcements are half of the start:
                                              #     (store_normalized_team_count, ":num_defenders", 0),
                                              #     (lt, ":num_defenders", 20),                         # if less than 20/40=50%
                                              #     (add_reinforcements_to_entry, 4, 20),               # add new wave 20/40=50%
                                              # To let options show the rigth battle size values change the entries in module.ini accordingly:
                                              #     battle_size_min = 100 # (40+40)*1.25
                                              #     battle_size_max = 420 # (40+40)*5.25
                                              # The battle advantage for player is limited by the game engine. The player can only dominate with 2:1 ratio at max.
get_average_game_difficulty           =  990  # (get_average_game_difficulty, <destination>),
                                              # Returns calculated game difficulty rating (as displayed on the Options page). Commonly used for score calculation when ending the game.

# Achievements and kill stats

get_achievement_stat                  =  370  # (get_achievement_stat, <destination>, <achievement_id>, <stat_index>),
                                              # Retrieves the numeric value associated with an achievement. Used to keep track of player's results before finally unlocking it.
set_achievement_stat                  =  371  # (set_achievement_stat, <achievement_id>, <stat_index>, <value>),
                                              # Sets the new value associated with an achievement. Used to keep track of player's results before finally unlocking it.
unlock_achievement                    =  372  # (unlock_achievement, <achievement_id>),
                                              # Unlocks player's achievement. Apparently doesn't have any game effects.
get_player_agent_kill_count           = 1701  # (get_player_agent_kill_count, <destination>, [get_wounded]),
                                              # Retrieves the total number of enemies killed by the player. Call with non-zero <get_wounded> parameter to retrieve the total number of knocked down enemies. Returns lifetime kill counts.
get_player_agent_own_troop_kill_count = 1705  # (get_player_agent_own_troop_kill_count, <destination>, [get_wounded]),
                                              # Retrieves the total number of allies killed by the player. Call with non-zero <get_wounded> parameter to retrieve the total number of knocked down allies.

################################################################################
# [ Z08 ] FACTIONS
################################################################################

  # Despite the importance of factions to the game, there aren't that many
  # actions to deal with them. Essentially, you can control colors and name of
  # existing game factions, set or retrieve relations between them, and work
  # with faction slots. There's also a number of operations which assign or
  # retrieve the factional allegiance of other game objects, like parties and
  # troops, but these have been placed in the respective sections of the file.

# Slot operations for factions

faction_set_slot                =  502                 # (faction_set_slot, <faction_id>, <slot_no>, <value>),
faction_get_slot                =  522                 # (faction_get_slot, <destination>, <faction_id>, <slot_no>),
faction_slot_eq                 =  542                 # (faction_slot_eq, <faction_id>, <slot_no>, <value>),
faction_slot_ge                 =  562                 # (faction_slot_ge, <faction_id>, <slot_no>, <value>),
faction_slot_lt                 = neg|faction_slot_ge  # (faction_slot_lt, <faction_id>, <slot_no>, <value>),

# Generic operations

set_relation                    = 1270  # (set_relation, <faction_id_1>, <faction_id_2>, <value>),
                                        # Sets relation between two factions. Relation is in -100..100 range.
store_relation                  = 2190  # (store_relation, <destination>, <faction_id_1>, <faction_id_2>),
                                        # Retrieves relation between two factions. Relation is in -100..100 range.
faction_set_name                = 1275  # (faction_set_name, <faction_id>, <string>),
                                        # Sets the name of the faction. See also (str_store_faction_name) in String Operations.
faction_set_color               = 1276  # (faction_set_color, <faction_id>, <color_code>),
                                        # Sets the faction color. All parties and centers belonging to this faction will be displayed with this color on global map.
faction_get_color               = 1277  # (faction_get_color, <destination>, <faction_id>),
                                        # Gets the faction color value.

################################################################################
# [ Z09 ] PARTIES AND PARTY TEMPLATES
################################################################################

  # Parties are extremely important element of single-player modding, because
  # they are the only object which can be present on the world map. Each party
  # is a semi-independent object with its own behavior. Note that you cannot
  # control party's behavior directly, instead you can change various factors
  # which affect party behavior (including party AI settings).

  # There are two things of importance when dealing with parties. First, parties
  # can be attached to each other, this allows you, for example, to stack a
  # number of armies inside a single city. Second, parties may encounter each
  # other. When two AI parties are in encounter, it usually means they are
  # fighting. Player's encounter with an AI party is usually much more complex
  # and may involve pretty much anything, which is why player's encounters are
  # covered in a separate section of the file.

  # Each party consists of troop stacks. Each troop stack is either a single
  # hero (troop defined as tf_hero in module_troops.py file) or a number of
  # regular troops (their number may vary from 1 and above). Each party has two
  # sets of troop stacks: members (or companions) set of stacks, and prisoners
  # set of stacks. Many operations will only affect members, others may only
  # affect prisoners, and there are even operations to switch their roles.

  # Another important concept is a party template. Its definition looks very
  # similar to a party. Templates are used when there's a need to create a
  # number of parties with similar set of members, parameters or flags. Also
  # templates can be easily used to differentiate parties from each other,
  # so they are akin to a "party_type" in the game.

  # Note that parties are the only game object which is persistent (i.e. it
  # will be saved to the savegame file and restored on load), has slots and
  # can be created during runtime. This makes parties ideal candidates for
  # dynamic information storage of unlimited volume, which the game otherwise
  # lacks.

# Conditional operations

hero_can_join                         =  101                # (hero_can_join, [party_id]),
                                                            # Checks if party can accept one hero troop. Player's party is default value.
hero_can_join_as_prisoner             =  102                # (hero_can_join_as_prisoner, [party_id]),
                                                            # Checks if party can accept one hero prisoner troop. Player's party is default value.
party_can_join                        =  103                # (party_can_join),
                                                            # During encounter dialog, checks if encountered party can join player's party.
party_can_join_as_prisoner            =  104                # (party_can_join_as_prisoner),
                                                            # During encounter dialog, checks if encountered party can join player's party as prisoners.
troops_can_join                       =  105                # (troops_can_join, <value>),
                                                            # Checks if player party has enough space for provided number of troops.
troops_can_join_as_prisoner           =  106                # (troops_can_join_as_prisoner, <value>),
                                                            # Checks if player party has enough space for provided number of prisoners..
party_can_join_party                  =  107                # (party_can_join_party, <joiner_party_id>, <host_party_id>, [flip_prisoners]),
                                                            # Checks if first party can join second party (enough space for both troops and prisoners). If flip_prisoners flag is 1, then members and prisoners in the joining party are flipped.
main_party_has_troop                  =  110                # (main_party_has_troop, <troop_id>),
                                                            # Checks if player party has specified troop.
party_is_in_town                      =  130                # (party_is_in_town, <party_id>, <town_party_id>),
                                                            # Checks that the party has successfully reached its destination (after being set to ai_bhvr_travel_to_party) and that its destination is actually the referenced town_party_id.
party_is_in_any_town                  =  131                # (party_is_in_any_town, <party_id>),
                                                            # Checks that the party has successfully reached its destination (after being set to ai_bhvr_travel_to_party).
party_is_active                       =  132                # (party_is_active, <party_id>),
                                                            # Checks that <party_id> is valid and not disabled.
party_is_dead                         = neg|party_is_active # (party_is_dead, <party_id>),

# Slot operations for parties and party templates

party_template_set_slot               =  504                        # (party_template_set_slot, <party_template_id>, <slot_no>, <value>),
party_template_get_slot               =  524                        # (party_template_get_slot, <destination>, <party_template_id>, <slot_no>),
party_template_slot_eq                =  544                        # (party_template_slot_eq, <party_template_id>, <slot_no>, <value>),
party_template_slot_ge                =  564                        # (party_template_slot_ge, <party_template_id>, <slot_no>, <value>),
party_template_slot_lt                = neg|party_template_slot_ge  # (party_template_slot_lt, <party_template_id>, <slot_no>, <value>),

party_set_slot                        =  501                        # (party_set_slot, <party_id>, <slot_no>, <value>),
party_get_slot                        =  521                        # (party_get_slot, <destination>, <party_id>, <slot_no>),
party_slot_eq                         =  541                        # (party_slot_eq, <party_id>, <slot_no>, <value>),
party_slot_ge                         =  561                        # (party_slot_ge, <party_id>, <slot_no>, <value>),
party_slot_lt                         = neg|party_slot_ge           # (party_slot_lt, <party_id>, <slot_no>, <value>),

# Generic operations

set_party_creation_random_limits      = 1080  # (set_party_creation_random_limits, <min_value>, <max_value>),
                                              # Affects party sizes spawned from templates. May be used to spawn larger parties when player is high level. Values should be in 0..100 range.
set_spawn_radius                      = 1103  # (set_spawn_radius, <value>),
                                              # Sets radius for party spawning with subsequent <spawn_around_party> operations.
spawn_around_party                    = 1100  # (spawn_around_party, <party_id>, <party_template_id>),
                                              # Creates a new party from a party template and puts its <party_id> into reg0.
disable_party                         = 1230  # (disable_party, <party_id>),
                                              # Party disappears from the map. Note that (try_for_parties) will still iterate over disabled parties, so you need to make additional checks with (party_is_active). Its slots, members and prisoners will persist, all it does is basically activating pf_disabled mid-game.
enable_party                          = 1231  # (enable_party, <party_id>),
                                              # Reactivates a previously disabled party.
remove_party                          = 1232  # (remove_party, <party_id>),
                                              # Destroys a party completely. Should ONLY be used with dynamically spawned parties, as removing parties pre-defined in module_parties.py file will corrupt the savegame. Non-spawned parties may be disabled...

party_get_current_terrain             = 1608  # (party_get_current_terrain, <destination>, <party_id>),
                                              # Returns a value from header_terrain_types.py
party_relocate_near_party             = 1623  # (party_relocate_near_party, <relocated_party_id>, <target_party_id>, <spawn_radius>),
                                              # Teleports party into vicinity of another party.
party_get_position                    = 1625  # (party_get_position, <dest_position>, <party_id>),
                                              # Stores current position of the party on world map.
party_set_position                    = 1626  # (party_set_position, <party_id>, <position>),
                                              # Teleports party to a specified position on the world map.
set_camera_follow_party               = 1021  # (set_camera_follow_party, <party_id>),
                                              # Self-explanatory. Can be used on world map only. Commonly used to make camera follow a party which has captured player as prisoner.

party_attach_to_party                 = 1660  # (party_attach_to_party, <party_id>, <party_id_to_attach_to>),
                                              # Attach a party to another one (like lord's army staying in a town/castle).
party_detach                          = 1661  # (party_detach, <party_id>),
                                              # Remove a party from attachments and place it on the world map.
party_collect_attachments_to_party    = 1662  # (party_collect_attachments_to_party, <source_party_id>, <collected_party_id>),
                                              # Mostly used in various battle and AI calculations. Will create an aggregate party from all parties attached to the source party.
party_get_cur_town                    = 1665  # (party_get_cur_town, <destination>, <party_id>),
                                              # When a party has reached its destination (using ai_bhvr_travel_to_party), this operation will retrieve the party_id of the destination party.
party_get_attached_to                 = 1694  # (party_get_attached_to, <destination>, <party_id>),
                                              # Retrieves the party that the referenced party is attached to, if any.
party_get_num_attached_parties        = 1695  # (party_get_num_attached_parties, <destination>, <party_id>),
                                              # Retrieves total number of parties attached to referenced party.
party_get_attached_party_with_rank    = 1696  # (party_get_attached_party_with_rank, <destination>, <party_id>, <attached_party_index>),
                                              # Extract party_id of a specified party among attached.

party_set_name                        = 1669  # (party_set_name, <party_id>, <string>),
                                              # Sets party name (will be displayed as label and/or in the party details popup).
party_set_extra_text                  = 1605  # (party_set_extra_text, <party_id>, <string>),
                                              # Allows to put extra text in party details popup. Used in Native to set status for villages or towns (being raided, razed, under siege...).
party_get_icon                        = 1681  # (party_get_icon, <destination>, <party_id>),
                                              # Retrieve map icon used for the party.
party_set_icon                        = 1676  # (party_set_icon, <party_id>, <map_icon_id>),
                                              # Sets what map icon will be used for the party. Will not work outside the 256 range.
party_set_banner_icon                 = 1677  # (party_set_banner_icon, <party_id>, <map_icon_id>),
                                              # Sets what map icon will be used as the party banner. Use 0 to remove banner from a party. Allows for 256+ ranges.
party_set_extra_icon                  = 1682  # (party_set_extra_icon, <party_id>, <map_icon_id>, <vertical_offset_fixed_point>, <up_down_frequency_fixed_point>, <rotate_frequency_fixed_point>, <fade_in_out_frequency_fixed_point>),
                                              # Frequencies are in number of revolutions per second.
                                              # Adds or removes an extra map icon to a party, possibly with some animations. Use (party_set_extra_icon, <party_id>, 0, 0, 0, 0, 0), - (0 as map_icon_id) - to remove extra icon. Allows for 256+ ranges and some animation features too, recommended for people seeking 256+ ranges.
party_add_particle_system             = 1678  # (party_add_particle_system, <party_id>, <particle_system_id>),
                                              # Appends some special visual effects to the party on the map. Used in Native to add fire and smoke over villages.
party_clear_particle_systems          = 1679  # (party_clear_particle_systems, <party_id>),
                                              # Removes all special visual effects from the party on the map.
context_menu_add_item                 =  980  # (context_menu_add_item, <string_id>, <value>),
                                              # Must be called inside script_game_context_menu_get_buttons. Adds context menu option for a party and its respective identifier (will be passed to script_game_event_context_menu_button_clicked).

party_get_template_id                 = 1609  # (party_get_template_id, <destination>, <party_id>),
                                              # Retrieves what party template was used to create the party (if any). Commonly used to identify encountered party type.
party_set_faction                     = 1620  # (party_set_faction, <party_id>, <faction_id>),
                                              # Sets party faction allegiance. Party color is changed appropriately.
store_faction_of_party                = 2204  # (store_faction_of_party, <destination>, <party_id>),
                                              # Retrieves current faction allegiance of the party.

store_random_party_in_range           = 2254                    # (store_random_party_in_range, <destination>, <lower_bound>, <upper_bound>),
                                                                # Retrieves one random party from the range. Generally used only for predefined parties (towns, villages etc).
store01_random_parties_in_range       = 2255                    # (store01_random_parties_in_range, <lower_bound>, <upper_bound>),
store_random_parties_in_range = store01_random_parties_in_range # (store_random_parties_in_range, <lower_bound>, <upper_bound>),
                                                                # Stores two random, different parties in a range to reg0 and reg1. Generally used only for predefined parties (towns, villages etc).
store_distance_to_party_from_party    = 2281                    # (store_distance_to_party_from_party, <destination>, <party_id>, <party_id>),
                                                                # Retrieves distance between two parties on the global map. Extremely unprecise as it does not use a fixed point multiplier at all and 1 distance unit is quite a noticeable distance on the map. Instead of making decisions based on the output of this operation, first use it to measure distances between various parties on the map and print the results with display_message in order to get a feeling for this function.

store_num_parties_of_template         = 2310  # (store_num_parties_of_template, <destination>, <party_template_id>),
                                              # Stores number of active parties which were created using specified party template.
store_random_party_of_template        = 2311  # (store_random_party_of_template, <destination>, <party_template_id>),
                                              # Retrieves one random party which was created using specified party template. Fails if no party exists with provided template. (expensive)

store_num_parties_created             = 2300  # (store_num_parties_created, <destination>, <party_template_id>),
                                              # Stores the total number of created parties of specified type. Not used in Native.
store_num_parties_destroyed           = 2301  # (store_num_parties_destroyed, <destination>, <party_template_id>),
                                              # Stores the total number of destroyed parties of specified type.
store_num_parties_destroyed_by_player = 2302  # (store_num_parties_destroyed_by_player, <destination>, <party_template_id>),
                                              # Stores the total number of parties of specified type which have been destroyed by player.

party_get_morale                      = 1671  # (party_get_morale, <destination>, <party_id>),
                                              # Returns a value in the range of 0..100. Party morale does not affect party behavior on the map, but will be taken in account if the party is engaged in battle (except auto-calc).
party_set_morale                      = 1672  # (party_set_morale, <party_id>, <value>),
                                              # Value should be in the range of 0..100. Party morale does not affect party behavior on the map, but will be taken in account if the party is engaged in battle (except auto-calc).

# Party members manipulation

party_join                            = 1201  # (party_join),
                                              # During encounter, joins encountered party to player's party.
party_join_as_prisoner                = 1202  # (party_join_as_prisoner),
                                              # During encounter, joins encountered party to player's party as prisoners.
troop_join                            = 1203  # (troop_join, <troop_id>),
                                              # Specified hero joins player's party.
troop_join_as_prisoner                = 1204  # (troop_join_as_prisoner, <troop_id>),
                                              # Specified hero joins player's party as prisoner.
add_companion_party                   = 1233  # (add_companion_party, <troop_id_hero>),
                                              # Creates a new empty party with specified hero as party leader and the only member. Party is spawned at the position of player's party.
party_add_members                     = 1610  # (party_add_members, <party_id>, <troop_id>, <number>),
                                              # Adds troop(s) to the party. Returns total number of added troops in reg0.
party_add_prisoners                   = 1611  # (party_add_prisoners, <party_id>, <troop_id>, <number>),
                                              # Adds troop(s) to the party and makes it Prisoner. Returns total number of added prisoners in reg0.
party_add_leader                      = 1612  # (party_add_leader, <party_id>, <troop_id>, [number]),
                                              # Adds troop(s) to the party and makes it party leader.
party_force_add_members               = 1613  # (party_force_add_members, <party_id>, <troop_id>, <number>),
                                              # Adds troops to party ignoring party size limits. Mostly used to add hero troops. Only works if the party does not yet have any troops of the specified type.
party_force_add_prisoners             = 1614  # (party_force_add_prisoners, <party_id>, <troop_id>, <number>),
                                              # Adds prisoners to party ignoring party size limits. Mostly used to add hero prisoners. Doesn't add if troop already exist in the party.
party_add_template                    = 1675  # (party_add_template, <party_id>, <party_template_id>, [reverse_prisoner_status]),
                                              # Reinforces the party using the specified party template. Optional flag switches troop/prisoner status for reinforcements.
distribute_party_among_party_group    = 1698  # (distribute_party_among_party_group, <party_to_be_distributed>, <group_root_party>),
                                              # Distributes troops from first party among all parties attached to the second party. Commonly used to divide prisoners and resqued troops among NPC parties.

remove_member_from_party              = 1210  # (remove_member_from_party, <troop_id>, [party_id]),
                                              # Removes hero member from party. Player party is default value. Will display a message about companion leaving the party. Should not be used with regular troops (it will successfully remove one of them, but will produce some meaningless spam).
remove_regular_prisoners              = 1211  # (remove_regular_prisoners, <party_id>),
                                              # Removes all non-hero prisoners from the party.
remove_troops_from_companions         = 1215  # (remove_troops_from_companions, <troop_id>, <value>),
                                              # Removes troops from player's party, duplicating functionality of (party_remove_members) but providing less flexibility.
remove_troops_from_prisoners          = 1216  # (remove_troops_from_prisoners, <troop_id>, <value>),
                                              # Removes prisoners from player's party.
party_remove_members                  = 1615  # (party_remove_members, <party_id>, <troop_id>, <number>),
                                              # Removes specified number of troops from a party. Stores number of actually removed troops in reg0.
party_remove_prisoners                = 1616  # (party_remove_prisoners, <party_id>, <troop_id>, <number>),
                                              # Removes specified number of prisoners from a party. Stores number of actually removed prisoners in reg0.
party_clear                           = 1617  # (party_clear, <party_id>),
                                              # Removes all members and prisoners from the party.
add_gold_to_party                     = 1070  # (add_gold_to_party, <value>, <party_id>),
                                              # Marks the party as carrying the specified amount of gold, which can be pillaged by player if he destroys it. Operation must not be used to give gold to player's party.

# Calculating party and stack sizes

party_get_num_companions              = 1601  # (party_get_num_companions, <destination>, <party_id>),
                                              # Returns total number of party members, including leader.
party_get_num_prisoners               = 1602  # (party_get_num_prisoners, <destination>, <party_id>),
                                              # Returns total number of party prisoners.
party_count_members_of_type           = 1630  # (party_count_members_of_type, <destination>, <party_id>, <troop_id>),
                                              # Returns total number of party members of specific type.
party_count_companions_of_type        = 1631  # (party_count_companions_of_type, <destination>, <party_id>, <troop_id>),
                                              # Duplicates (party_count_members_of_type).
party_count_prisoners_of_type         = 1632  # (party_count_prisoners_of_type, <destination>, <party_id>, <troop_id>),
                                              # Returns total number of prisoners of specific type.
party_get_free_companions_capacity    = 1633  # (party_get_free_companions_capacity, <destination>, <party_id>),
                                              # Calculates how many members can be added to the party.
party_get_free_prisoners_capacity     = 1634  # (party_get_free_prisoners_capacity, <destination>, <party_id>),
                                              # Calculates how many prisoners can be added to the party.
party_get_num_companion_stacks        = 1650  # (party_get_num_companion_stacks, <destination>, <party_id>),
                                              # Returns total number of troop stacks in the party (including player and heroes).
party_get_num_prisoner_stacks         = 1651  # (party_get_num_prisoner_stacks, <destination>, <party_id>),
                                              # Returns total number of prisoner stacks in the party (including any heroes).
party_stack_get_troop_id              = 1652  # (party_stack_get_troop_id, <destination>, <party_id>, <stack_no>),
                                              # Extracts troop type of the specified troop stack.
party_stack_get_size                  = 1653  # (party_stack_get_size, <destination>, <party_id>, <stack_no>),
                                              # Extracts number of troops in the specified troop stack.
party_stack_get_num_wounded           = 1654  # (party_stack_get_num_wounded, <destination>, <party_id>, <stack_no>),
                                              # Extracts number of wounded troops in the specified troop stack.
party_stack_get_troop_dna             = 1655  # (party_stack_get_troop_dna, <destination>, <party_id>, <stack_no>),
                                              # Extracts DNA from the specified troop stack. Used to properly generate appereance in conversations.
party_prisoner_stack_get_troop_id     = 1656  # (party_prisoner_stack_get_troop_id, <destination>, <party_id>, <stack_no>),
                                              # Extracts troop type of the specified prisoner stack.
party_prisoner_stack_get_size         = 1657  # (party_prisoner_stack_get_size, <destination>, <party_id>, <stack_no>),
                                              # Extracts number of troops in the specified prisoner stack.
party_prisoner_stack_get_troop_dna    = 1658  # (party_prisoner_stack_get_troop_dna, <destination>, <party_id>, <stack_no>),
                                              # Extracts DNA from the specified prisoner stack. Used to properly generate appereance in conversations.
store_num_free_stacks                 = 2154  # (store_num_free_stacks, <destination>, <party_id>),
                                              # Deprecated, as Warband no longer has limits on number of stacks in the party. Always returns 10.
store_num_free_prisoner_stacks        = 2155  # (store_num_free_prisoner_stacks, <destination>, <party_id>),
                                              # Deprecated, as Warband no longer has limits on number of stacks in the party. Always returns 10.
store_party_size                      = 2156  # (store_party_size, <destination>,[party_id]),
                                              # Stores total party size (all members and prisoners).
store_party_size_wo_prisoners         = 2157  # (store_party_size_wo_prisoners, <destination>, [party_id]),
                                              # Stores total number of members in the party (without prisoners), duplicating (party_get_num_companions).
store_troop_kind_count                = 2158  # (store_troop_kind_count, <destination>, <troop_type_id>),
                                              # Counts number of troops of specified type in player's party. Deprecated, use party_count_members_of_type instead.
store_num_regular_prisoners           = 2159  # (store_num_regular_prisoners, <destination>, <party_id>),
                                              # Deprecated and does not work. Do not use.
store_troop_count_companions          = 2160  # (store_troop_count_companions, <destination>, <troop_id>, [party_id]),
                                              # Apparently deprecated, duplicates (party_get_num_companions). Not used in Native.
store_troop_count_prisoners           = 2161  # (store_troop_count_prisoners, <destination>, <troop_id>, [party_id]),
                                              # Apparently deprecated, duplicates (party_get_num_prisoners). Not used in Native.
store_main_party_wounded              = 2180  # (store_main_party_wounded, <destination>),
                                              # Stores number of wounded troops and NPCs in the main player party into <destination>.

# Party experience and skills

party_add_xp_to_stack                 = 1670  # (party_add_xp_to_stack, <party_id>, <stack_no>, <xp_amount>),
                                              # Awards specified number of xp points to a single troop stack in the party.
party_upgrade_with_xp                 = 1673  # (party_upgrade_with_xp, <party_id>, <xp_amount>, <upgrade_path>), #upgrade_path can be:
                                              # Awards specified number of xp points to entire party (split between all stacks) and upgrades all eligible troops. Upgrade direction: (0 = random, 1 = first, 2 = second).
party_add_xp                          = 1674  # (party_add_xp, <party_id>, <xp_amount>),
                                              # Awards specified number of xp points to entire party (split between all stacks).
party_get_skill_level                 = 1685  # (party_get_skill_level, <destination>, <party_id>, <skill_no>),
                                              # Retrieves skill level for the specified party (usually max among the heroes). Makes a callback to (script_game_get_skill_modifier_for_troop).

# Combat related operations

heal_party                            = 1225  # (heal_party, <party_id>),
                                              # Heals all wounded party members.
party_wound_members                   = 1618  # (party_wound_members, <party_id>, <troop_id>, <number>),
                                              # Wounds a specified number of troops in the party.
party_remove_members_wounded_first    = 1619  # (party_remove_members_wounded_first, <party_id>, <troop_id>, <number>),
                                              # Removes a certain number of troops from the party, starting with wounded. Stores total number removed in reg0.
party_quick_attach_to_current_battle  = 1663  # (party_quick_attach_to_current_battle, <party_id>, <side>),
                                              # Adds any party into current encounter at specified side (0 = ally, 1 = enemy, 2 = enemy if (neq, "$g_enemy_party", "$g_encountered_party"),).
party_leave_cur_battle                = 1666  # (party_leave_cur_battle, <party_id>),
                                              # Forces the party to leave its current battle (if it's engaged).
party_set_next_battle_simulation_time = 1667  # (party_set_next_battle_simulation_time, <party_id>, <next_simulation_time_in_hours>),
                                              # Defines the period of time (in hours) after which the battle must be simulated for the specified party for the next time. When a value <= 0 is passed, the combat simulation round is performed immediately.
party_get_battle_opponent             = 1680  # (party_get_battle_opponent, <destination>, <party_id>),
                                              # When a party is engaged in battle with another party, returns its opponent party. Otherwise returns -1.
inflict_casualties_to_party_group     = 1697  # (inflict_casualties_to_party_group, <parent_party_id>, <damage_amount>, <party_id_to_add_causalties_to>),
                                              # Delivers auto-calculated damage to the party (and all other parties attached to it). Killed troops are moved to another party to keep track of.
party_end_battle                      =  108  # (party_end_battle, <party_no>),
                                              # Version 1.153+. UNTESTED. Supposedly ends the battle in which the party is currently participating.

# Party AI

party_set_marshall                    = 1604  # (party_set_marshall, <party_id>, <value>),
party_set_marshal = party_set_marshall        # (party_set_marshal, <party_id>, <value>),
                                              # Sets party as a marshall party or turns it back to normal party. Value is either 1 or 0. This affects party behavior, but exact effects are not known. Alternative operation name spelling added to enable compatibility with Viking Conquest DLC module system.
party_set_flags                       = 1603  # (party_set_flags, <party_id>, <flag>, <clear_or_set>),
                                              # Sets (1) or clears (0) party flags in runtime. See header_parties.py for flags reference.
party_set_aggressiveness              = 1606  # (party_set_aggressiveness, <party_id>, <number>),
                                              # Sets aggressiveness value for the party (range 0..15).
party_set_courage                     = 1607  # (party_set_courage, <party_id>, <number>),
                                              # Sets courage value for the party (range 4..15).
party_get_ai_initiative               = 1638  # (party_get_ai_initiative, <destination>, <party_id>),
                                              # Gets party current AI initiative value (range 0..100).
party_set_ai_initiative               = 1639  # (party_set_ai_initiative, <party_id>, <value>),
                                              # Sets AI initiative value for the party (range 0..100).
party_set_ai_behavior                 = 1640  # (party_set_ai_behavior, <party_id>, <ai_bhvr>),
                                              # Sets AI behavior for the party. See header_parties.py for reference.
party_set_ai_object                   = 1641  # (party_set_ai_object, <party_id>, <object_party_id>),
                                              # Sets another party as the object for current AI behavior (follow that party).
party_set_ai_target_position          = 1642  # (party_set_ai_target_position, <party_id>, <position>),
                                              # Sets a specific world map position as the object for current AI behavior (travel to that point).
party_set_ai_patrol_radius            = 1643  # (party_set_ai_patrol_radius, <party_id>, <radius_in_km>),
                                              # Sets a radius for AI patrolling behavior.
party_ignore_player                   = 1644  # (party_ignore_player, <party_id>, <duration_in_hours>),
                                              # Makes AI party ignore player for the specified time.
party_set_bandit_attraction           = 1645  # (party_set_bandit_attraction, <party_id>, <attaraction>),
                                              # Sets party attractiveness to parties with bandit behavior (range 0..100).
party_get_helpfulness                 = 1646  # (party_get_helpfulness, <destination>, <party_id>),
                                              # Gets party current AI helpfulness value (range 0..100).
party_set_helpfulness                 = 1647  # (party_set_helpfulness, <party_id>, <number>),
                                              # Sets AI helpfulness value for the party (range 0..10000, default 100).
                                              # Official: tendency to help friendly parties under attack.
get_party_ai_behavior                 = 2290  # (get_party_ai_behavior, <destination>, <party_id>),
                                              # Retrieves current AI behavior pattern for the party.
get_party_ai_object                   = 2291  # (get_party_ai_object, <destination>, <party_id>),
                                              # Retrieves what party is currently used as object for AI behavior.
party_get_ai_target_position          = 2292  # (party_get_ai_target_position, <position>, <party_id>),
                                              # Retrieves what position is currently used as object for AI behavior.
get_party_ai_current_behavior         = 2293  # (get_party_ai_current_behavior, <destination>, <party_id>),
                                              # Retrieves current AI behavior pattern when it was overridden by current situation (fleeing from enemy when en route to destination).
get_party_ai_current_object           = 2294  # (get_party_ai_current_object, <destination>, <party_id>),
                                              # Retrieves what party has caused temporary behavior switch.

party_set_ignore_with_player_party    = 1648  # (party_set_ignore_with_player_party, <party_id>, <value>),
                                              # Version 1.161+. Effects uncertain. 4research
party_get_ignore_with_player_party    = 1649  # (party_get_ignore_with_player_party, <party_id>),
                                              # Version 1.161+. Effects uncertain. Documented official syntax is suspicious and probably incorrect. 4research


################################################################################
# [ Z10 ] TROOPS
################################################################################

  # What troops are.

  # There are two major types of troops: heroes and regulars. They are treated
  # very differently by the game, so it's important not to confuse them. At the
  # same time, most Module System operations will not make any differentiation
  # between hero and regular troops.

  # First of all, hero troops do not stack. You cannot have a stack of heroes
  # in a party, each hero will always occupy a separate troop slot. At the same
  # time, you can put any number of regular troops into a single troop slot.

  # Second, the way the game treats equipment of heroes and troops is also
  # different. All heroes' items are treated in the same way as player's (no
  # big surprise, since player is actually a hero troop himself). Meanwhile,
  # items that the troop has are just suggestions for what this troop *might*
  # take into battle. On the battlefield, each agent spawned from the regular
  # troop, will only take a limited number of items from the inventory provided
  # by the troop definition in module_troops.py. Choice is absolutely random and
  # modder has only limited control over it through the use of guarantee flags.
  # There's one more additional caveat: while you can easily change the outfit
  # of a hero troop and your changes will persist through the game, same applies
  # to regular troops. In other words, by changing equipment of some regular
  # troop, you are changing all instances of that troop throughout the entire
  # game. In other words, you cannot re-equip a stack of regulars in a single
  # party - your changes will affect all parties in the world.

  # Third, while all heroes have a single predefined face code, which is used
  # consistently through the game, troops have entire range of face codes. This
  # range is used to randomize each agent's face within those constraints, so a
  # group of 12 pikemen will not look like a bunch of clones.

  # Fourth, hero troops can't be killed in battle. Every time hero's hit points
  # are reduced to zero, hero is always knocked down. For regular troops, chance
  # to be knocked down depends on the number of factors, but their default fate
  # when driven to zero health is death.

# Conditional operators

troop_has_item_equipped                  =  151  # (troop_has_item_equipped, <troop_id>, <item_id>),
                                                 # Checks that the troop has this item equipped (worn or wielded).
troop_is_mounted                         =  152  # (troop_is_mounted, <troop_id>),
                                                 # Checks the troop for tf_mounted flag (see header_troops.py). Does NOT check that the troop has a horse.
troop_is_guarantee_ranged                =  153  # (troop_is_guarantee_ranged, <troop_id>),
                                                 # Checks the troop for tf_guarantee_ranged flag (see header_troops.py). Does not check that troop actually has some ranged weapon.
troop_is_guarantee_horse                 =  154  # (troop_is_guarantee_horse, <troop_id>),
                                                 # Checks the troop for tf_guarantee_horse flag (see header_troops.py). Does not check that troop actually has some horse.
troop_is_hero                            = 1507  # (troop_is_hero, <troop_id>),
                                                 # Checks the troop for tf_hero flag (see header_troops.py). Hero troops are actual characters and do not stack in party window.
troop_is_wounded                         = 1508  # (troop_is_wounded, <troop_id>),
                                                 # Checks that the troop is wounded. Only works for hero troops.
player_has_item                          =  150  # (player_has_item, <item_id>),
                                                 # Checks that player has the specified item.

# Slot operations for troops

troop_set_slot                           =  500               # (troop_set_slot, <troop_id>, <slot_no>, <value>),
troop_get_slot                           =  520               # (troop_get_slot, <destination>, <troop_id>, <slot_no>),
troop_slot_eq                            =  540               # (troop_slot_eq, <troop_id>, <slot_no>, <value>),
troop_slot_ge                            =  560               # (troop_slot_ge, <troop_id>, <slot_no>, <value>),
troop_slot_lt                            = neg|troop_slot_ge  # (troop_slot_lt, <troop_id>, <slot_no>, <value>),

# Troop attributes and skills

troop_set_type                           = 1505  # (troop_set_type, <troop_id>, <skin>),
                                                 # Changes the troop skin. There are two skins in Native: male and female, so in effect this operation sets troop gender. However mods may declare other skins.
troop_get_type                           = 1506  # (troop_get_type, <destination>, <troop_id>),
                                                 # Returns troop current skin (i.e. gender).
troop_set_class                          = 1517  # (troop_set_class, <troop_id>, <value>),
                                                 # Sets troop class (infantry, archers, cavalry or any of custom classes). Accepts values in range 0..8. See grc_* constants in header_mission_templates.py.
troop_get_class                          = 1516  # (troop_get_class, <destination>, <troop_id>),
                                                 # Retrieves troop class. Returns values in range 0..8.
class_set_name                           = 1837  # (class_set_name, <sub_class>, <string_id>),
                                                 # Sets a new name for troop class (aka "Infantry", "Cavalry", "Custom Group 3"...). While manually you can rename class only up to 28 characters via in-game button, the operation is able to assign any string or quick string and even supports multi-line with ^ symbol. However, the game seems to be able to display only up to 291 characters from the feed message, and long class names aren't readable or viable but are definitely possible. Keep in mind that 10 characters are required for ", hear me!" to show up so the actual max length for class name is 281.
add_xp_to_troop                          = 1062  # (add_xp_to_troop, <value>, [troop_id]),
                                                 # Adds some xp points to troop. Only makes sense for player and hero troops. Default troop_id is player. Amount of xp can be negative.
add_xp_as_reward                         = 1064  # (add_xp_as_reward, <value>),
                                                 # Adds the specified amount of xp points to player. Typically used as a quest reward operation.
troop_get_xp                             = 1515  # (troop_get_xp, <destination>, <troop_id>),
                                                 # Retrieves total amount of xp specified troop has.
store_attribute_level                    = 2172  # (store_attribute_level, <destination>, <troop_id>, <attribute_id>),
                                                 # Stores current value of troop attribute. See ca_* constants in header_troops.py for reference.
troop_raise_attribute                    = 1520  # (troop_raise_attribute, <troop_id>, <attribute_id>, <value>),
                                                 # Increases troop attribute by the specified amount. See ca_* constants in header_troops.py for reference. Use negative values to reduce attributes. When used on non-hero troop, will affect all instances of that troop.
store_skill_level                        = 2170  # (store_skill_level, <destination>, <skill_id>, [troop_id]),
                                                 # Stores current value of troop skill. See header_skills.py for reference.
troop_raise_skill                        = 1521  # (troop_raise_skill, <troop_id>, <skill_id>, <value>),
                                                 # Increases troop skill by the specified value. Value can be negative. See header_skills.py for reference. When used on non-hero troop, will affect all instances of that troop.
store_proficiency_level                  = 2176  # (store_proficiency_level, <destination>, <troop_id>, <attribute_id>),
                                                 # Stores current value of troop weapon proficiency. See wpt_* constants in header_troops.py for reference.
troop_raise_proficiency                  = 1522  # (troop_raise_proficiency, <troop_id>, <proficiency_no>, <value>),
                                                 # Increases troop weapon proficiency by the specified value. Increase is subject to limits defined by Weapon Master skill. When used on non-hero troop, will affect all instances of that troop. Will accept and handle negative values.
troop_raise_proficiency_linear           = 1523  # (troop_raise_proficiency_linear, <troop_id>, <proficiency_no>, <value>),
                                                 # Same as (troop_raise_proficiency), but does not take Weapon Master skill into account (i.e. can increase proficiencies indefinitely). Will accept and handle negative values as well.
troop_add_proficiency_points             = 1525  # (troop_add_proficiency_points, <troop_id>, <value>),
                                                 # Adds some proficiency points to a hero troop which can later be distributed by player.
store_troop_health                       = 2175  # (store_troop_health, <destination>, <troop_id>, [absolute]), # set absolute to 1 to get actual health; otherwise this will return percentage health in range (0-100)
                                                 # Retrieves current troop health. Use absolute = 1 to retrieve actual number of hp points left, use absolute = 0 to retrieve a value in 0..100 range (percentage).
troop_set_health                         = 1560  # (troop_set_health, <troop_id>, <relative health (0-100)>),
                                                 # Sets troop health. Accepts value in range 0..100 (percentage).
troop_get_upgrade_troop                  = 1561  # (troop_get_upgrade_troop, <destination>, <troop_id>, <upgrade_path>),
                                                 # Retrieves possible directions for non-hero troop upgrade. Use 0 to retrieve first upgrade path, and 1 to return second. Result of -1 means there's no such upgrade path for this troop.
store_character_level                    = 2171  # (store_character_level, <destination>, [troop_id]),
                                                 # Retrieves character level of the troop. Default troop is the player.
get_level_boundary                       =  991  # (get_level_boundary, <destination>, <level_no>),
                                                 # Returns the amount of experience points required to reach the specified level (will return 0 for 1st level). Maximum possible level in the game is 63.
add_gold_as_xp                           = 1063  # (add_gold_as_xp, <value>, [troop_id]),  # Default troop is player
                                                 # Adds a certain amount of experience points, depending on the amount of gold specified. Conversion rate is unclear and apparently somewhat randomized (three runs with 1000 gold produced values 1091, 804 and 799).

# Troop equipment handling

troop_set_auto_equip                     = 1509  # (troop_set_auto_equip, <troop_id>, <value>),
                                                 # Sets (value = 1) or disables (value = 0) auto-equipping the troop with any items added to its inventory or purchased. Similar to tf_is_merchant flag.
troop_ensure_inventory_space             = 1510  # (troop_ensure_inventory_space, <troop_id>, <value>),
                                                 # Removes items from troop inventory until troop has specified number of free inventory slots. Will free inventory slots starting from the end (items at the bottom of inventory will be removed first if there's not enough free space).
troop_sort_inventory                     = 1511  # (troop_sort_inventory, <troop_id>),
                                                 # Sorts items in troop inventory by their price (expensive first).
troop_add_item                           = 1530  # (troop_add_item, <troop_id>, <item_id>, [modifier]),
                                                 # Adds an item to the troop, optionally with a modifier (see imod_* constants in header_item_modifiers.py).
troop_remove_item                        = 1531  # (troop_remove_item, <troop_id>, <item_id>),
                                                 # Removes an item from the troop equipment or inventory. Operation will remove first matching item it finds.
troop_clear_inventory                    = 1532  # (troop_clear_inventory, <troop_id>),
                                                 # Clears entire troop inventory. Does not affect equipped items.
troop_equip_items                        = 1533  # (troop_equip_items, <troop_id>),
                                                 # Makes the troop reconsider its equipment. If troop has better stuff in its inventory, it will equip it. Note this operation sucks with weapons and may force the troop to equip himself with 4 two-handed swords.
troop_inventory_slot_set_item_amount     = 1534  # (troop_inventory_slot_set_item_amount, <troop_id>, <inventory_slot_no>, <value>),
                                                 # Sets the stack size for a specified equipment or inventory slot. Only makes sense for items like ammo or food (which show stuff like "23/50" in inventory). Equipment slots are in range 0..9, see ek_* constants in header_items.py for reference.
troop_inventory_slot_get_item_amount     = 1537  # (troop_inventory_slot_get_item_amount, <destination>, <troop_id>, <inventory_slot_no>),
                                                 # Retrieves the stack size for a specified equipment or inventory slot (if some Bread is 23/50, this operation will return 23).
troop_inventory_slot_get_item_max_amount = 1538  # (troop_inventory_slot_get_item_max_amount, <destination>, <troop_id>, <inventory_slot_no>),
                                                 # Retrieves the maximum possible stack size for a specified equipment or inventory slot (if some Bread is 23/50, this operation will return 50).
troop_add_items                          = 1535  # (troop_add_items, <troop_id>, <item_id>, <number>),
                                                 # Adds multiple items of specified type to the troop.
troop_remove_items                       = 1536  # (troop_remove_items, <troop_id>, <item_id>, <number>),
                                                 # Removes multiple items of specified type from the troop. Total price of actually removed items will be stored in reg0. Regardless of item modifiers. Will not fail if <troop_id> does not have the required items.
troop_loot_troop                         = 1539  # (troop_loot_troop, <target_troop>, <source_troop_id>, <probability>), 
                                                 # Adds to target_troop's inventory some items from source_troop's equipment and inventory with some probability. If an item is added to the target troop, it is given a random modifier from the item's imod list. Does not actually remove items from source_troop. Commonly used in Native to generate random loot after the battle.
troop_get_inventory_capacity             = 1540  # (troop_get_inventory_capacity, <destination>, <troop_id>),
                                                 # Returns the total inventory capacity (number of inventory slots) for the specified troop. Note that this number will include equipment slots as well. Substract num_equipment_kinds (see header_items.py) to get the number of actual *inventory* slots.
troop_get_inventory_slot                 = 1541  # (troop_get_inventory_slot, <destination>, <troop_id>, <inventory_slot_no>),
                                                 # Retrieves the item_id of a specified equipment or inventory slot. Returns -1 when there's nothing there.
troop_get_inventory_slot_modifier        = 1542  # (troop_get_inventory_slot_modifier, <destination>, <troop_id>, <inventory_slot_no>),
                                                 # Retrieves the modifier value (see imod_* constants in header_items.py) for an item in the specified equipment or inventory slot. Returns 0 when there's nothing there, or if item does not have any modifiers.
troop_set_inventory_slot                 = 1543  # (troop_set_inventory_slot, <troop_id>, <inventory_slot_no>, <item_id>),
                                                 # Puts the specified item into troop's equipment or inventory slot. Be careful with setting equipment slots this way.
troop_set_inventory_slot_modifier        = 1544  # (troop_set_inventory_slot_modifier, <troop_id>, <inventory_slot_no>, <imod_value>),
                                                 # Sets the modifier for the item in the troop's equipment or inventory slot. See imod_* constants in header_items.py for reference.
store_item_kind_count                    = 2165  # (store_item_kind_count, <destination>, <item_id>, [troop_id]),
                                                 # Calculates total number of items of specified type that the troop has. Default troop is player.
store_free_inventory_capacity            = 2167  # (store_free_inventory_capacity, <destination>, [troop_id]),
                                                 # Calculates total number of free inventory slots that the troop has. Default troop is player.

# Merchandise handling

reset_price_rates                   = 1170  # (reset_price_rates),
                                            # Resets customized price rates for merchants.
set_price_rate_for_item             = 1171  # (set_price_rate_for_item, <item_id>, <value_percentage>),
                                            # Sets individual price rate for a single item type. Normal price rate is 100. Deprecated, as Warband uses (game_get_item_[buy/sell]_price_factor) scripts instead.
set_price_rate_for_item_type        = 1172  # (set_price_rate_for_item_type, <item_type_id>, <value_percentage>),
                                            # Sets individual price rate for entire item class (see header_items.py for itp_type_* constants). Normal price rate is 100. Deprecated, as Warband uses (game_get_item_[buy/sell]_price_factor) scripts instead.
set_merchandise_modifier_quality    = 1490  # (set_merchandise_modifier_quality, <value>),
                                            # Affects the probability of items with quality modifiers appearing in merchandise. Value is percentage, standard value is 100. 100 gives completely random items, <100 gives more items with bad imods, and >100 gives more items with good imods.
set_merchandise_max_value           = 1491  # (set_merchandise_max_value, <value>),
                                            # Not used in Native. Apparently prevents items with price higher than listed from being generated as merchandise.
reset_item_probabilities            = 1492  # (reset_item_probabilities, <value>),
                                            # Sets all items probability of being generated as merchandise to the provided value. Use zero with subsequent calls to (set_item_probability_in_merchandise) to only allow generation of certain items.
set_item_probability_in_merchandise = 1493  # (set_item_probability_in_merchandise, <item_id>, <value>),
                                            # Sets item probability of being generated as merchandise to the provided value.
troop_add_merchandise               = 1512  # (troop_add_merchandise, <troop_id>, <item_type_id>, <value>),
                                            # Adds a specified number of random items of certain type (see itp_type_* constants in header_items.py) to troop inventory. Only adds items with itp_merchandise flags.
troop_add_merchandise_with_faction  = 1513  # (troop_add_merchandise_with_faction, <troop_id>, <faction_id>, <item_type_id>, <value>),
                                            # faction_id is given to check if troop is eligible to produce that item.
                                            # Same as (troop_add_merchandise), but with additional filter: only adds items which belong to specified faction, or without any factions at all.

# Miscellaneous troop information

troop_set_name                           = 1501  # (troop_set_name, <troop_id>, <string_no>),
                                                 # Renames the troop, setting a new singular name for it.
troop_set_plural_name                    = 1502  # (troop_set_plural_name, <troop_id>, <string_no>),
                                                 # Renames the troop, setting a new plural name for it.
troop_add_gold                           = 1528  # (troop_add_gold, <troop_id>, <value>),
                                                 # Adds gold to troop. Generally used with player or hero troops.
troop_remove_gold                        = 1529  # (troop_remove_gold, <troop_id>, <value>),
                                                 # Removes gold from troop. Generally used with player or hero troops.
store_troop_gold                         = 2149  # (store_troop_gold, <destination>, <troop_id>),
                                                 # Retrieves total number of gold that the troop has.
troop_set_faction                        = 1550  # (troop_set_faction, <troop_id>, <faction_id>),
                                                 # Sets a new faction for the troop (mostly used to switch lords allegiances in Native).
store_troop_faction                      = 2173  # (store_troop_faction, <destination>, <troop_id>),
                                                 # Retrieves current troop faction allegiance.
store_faction_of_troop                   = 2173  # (store_faction_of_troop, <destination>, <troop_id>),
                                                 # Alternative spelling of the above operation.
troop_set_age                            = 1555  # (troop_set_age, <troop_id>, <age_slider_pos>),
                                                 # Defines a new age for the troop (will be used by the game engine to generate appropriately aged face). Age is in range 0.100. {slot_troop_age} and {slot_troop_age_appearance} will not be set.
store_troop_value                        = 2231  # (store_troop_value, <destination>, <troop_id>),
                                                 # Stores some value which is apparently related to troop's overall fighting value. Swadian infantry line troops from Native produced values 24, 47, 80, 133, 188. Calling on player produced 0.

# Troop face code handling

troop_set_face_key_from_current_profile  = 1503  # (troop_set_face_key_from_current_profile, <troop_id>),
                                                 # Forces the troop to adopt the face from player's currently selected multiplayer profile.
str_store_player_face_keys               = 2747  # (str_store_player_face_keys, <string_no>, <player_id>),
                                                 # Version 1.161+. Stores player's face keys into string register.
player_set_face_keys                     = 2748  # (player_set_face_keys, <player_id>, <string_no>),
                                                 # Version 1.161+. Sets player's face keys from string.
str_store_agent_face_keys                = 2749  # (str_store_agent_face_keys, <string_no>, <agent_id>),
                                                 # Stores agent's face keys into string register. Regular agents have random generated face from within the range of the two face codes at their troop entry.
str_store_troop_face_keys                = 2750  # (str_store_troop_face_keys, <string_no>, <troop_no>, [<alt>]),
                                                 # Version 1.161+. Stores specified troop's face keys into string register. Use optional <alt> parameter to determine what facekey set to retrieve: 0 for first and 1 for second.
troop_set_face_keys                      = 2751  # (troop_set_face_keys, <troop_no>, <string_no>, [<alt>]),
                                                 # Version 1.161+. Sets troop face keys from string. Use optional <alt> parameter to determine what face keys to update: 0 for first and 1 for second.
face_keys_get_hair                       = 2752  # (face_keys_get_hair, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks selected hair mesh from string containing troop/player face keys to <destination>.
face_keys_set_hair                       = 2753  # (face_keys_set_hair, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new hair value. Hair meshes associated with skin (as defined in module_skins) are numbered from 1. Use 0 for no hair.
face_keys_get_beard                      = 2754  # (face_keys_get_beard, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks selected beard mesh from string containing troop/player face keys to <destination>.
face_keys_set_beard                      = 2755  # (face_keys_set_beard, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new beard value. Beard meshes associated with skin (as defined in module_skins) are numbered from 1. Use 0 for no beard.
face_keys_get_face_texture               = 2756  # (face_keys_get_face_texture, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks selected face texture from string containing troop/player face keys to <destination>.
face_keys_set_face_texture               = 2757  # (face_keys_set_face_texture, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new face texture value. Face textures associated with skin (as defined in module_skins) are numbered from 0.
face_keys_get_hair_texture               = 2758  # (face_keys_get_hair_texture, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks selected hair texture from string containing troop/player face keys to <destination>. Apparently hair textures have no effect. 4 research.
face_keys_set_hair_texture               = 2759  # (face_keys_set_hair_texture, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new hair texture value. Doesn't seem to have an effect. 4research.
face_keys_get_hair_color                 = 2760  # (face_keys_get_hair_color, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks hair color slider value from face keys string. Values are in the range of 0..63. Mapping to specific colors depends on the hair color range defined for currently selected skin / face_texture combination.
face_keys_set_hair_color                 = 2761  # (face_keys_set_hair_color, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new hair color slider value. Value should be in the 0..63 range.
face_keys_get_age                        = 2762  # (face_keys_get_age, <destination>, <string_no>),
                                                 # Version 1.161+. Unpacks age slider value from face keys string. Values are in the range of 0..63.
face_keys_set_age                        = 2763  # (face_keys_set_age, <string_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new age slider value. Value should be in the 0..63 range.
face_keys_get_skin_color                 = 2764  # (face_keys_get_skin_color, <destination>, <string_no>),
                                                 # Version 1.161+. Apparently doesn't work. Should retrieve skin color value from face keys string into <destination>.
face_keys_set_skin_color                 = 2765  # (face_keys_set_skin_color, <string_no>, <value>),
                                                 # Version 1.161+. Apparently doesn't work. Should update face keys string with a new skin color value.
face_keys_get_morph_key                  = 2766  # (face_keys_get_morph_key, <destination>, <string_no>, <key_no>),
                                                 # Version 1.161+. Unpacks morph key value from face keys string. See morph key indices in module_skins.py file. Note that only 8 out of 27 morph keys are actually accessible (from 'chin_size' to 'cheeks'). Morph key values are in the 0..7 range.
face_keys_set_morph_key                  = 2767  # (face_keys_set_morph_key, <string_no>, <key_no>, <value>),
                                                 # Version 1.161+. Updates face keys string with a new morph key value. See morph key indices in module_skins.py file. Note that only 8 out of 27 morph keys are actually accessible (from 'chin_size' to 'cheeks'). Morph key values should be in the 0..7 range.
face_keys_store_string                   = 2716  # (face_keys_store_string, <face_key_register>, <string>), Initializes <face_key_register> using <string>
face_keys_init                           = 2700  # (face_keys_init, <face_key_register>), Zeroes <face_key_register>

################################################################################
# [ Z11 ] QUESTS
################################################################################

  # Quests are just that: some tasks that characters in the game world want the
  # player to do. It's interesting to note that in Warband quests can have three
  # possible outcomes: success, failure and conclusion. Generally the last
  # option is used to indicate some "intermediate" quest result, which is
  # neither a full success, nor a total failure.

# Conditional operations

check_quest_active            =  200  # (check_quest_active, <quest_id>),
                                      # Checks that the quest has been started but not yet cancelled or completed. Will not fail for concluded, failed or succeeded quests for as long as they have not yet been completed.
check_quest_finished          =  201  # (check_quest_finished, <quest_id>),
                                      # Checks that the quest has been completed (result does not matter) and not taken again yet.
check_quest_succeeded         =  202  # (check_quest_succeeded, <quest_id>),
                                      # Checks that the quest has succeeded and not taken again yet (check will be successful even after the quest is completed).
check_quest_failed            =  203  # (check_quest_failed, <quest_id>),
                                      # Checks that the quest has failed and not taken again yet (check will be successful even after the quest is completed).
check_quest_concluded         =  204  # (check_quest_concluded, <quest_id>),
                                      # Checks that the quest was concluded with any result and not taken again yet.

# Slot operations for quests

quest_set_slot                =  506               # (quest_set_slot, <quest_id>, <slot_no>, <value>),
quest_get_slot                =  526               # (quest_get_slot, <destination>, <quest_id>, <slot_no>),
quest_slot_eq                 =  546               # (quest_slot_eq, <quest_id>, <slot_no>, <value>),
quest_slot_ge                 =  566               # (quest_slot_ge, <quest_id>, <slot_no>, <value>),
quest_slot_lt                 = neg|quest_slot_ge  # (quest_slot_lt, <quest_id>, <slot_no>, <value>),

# Quest management

start_quest                   = 1280  # (start_quest, <quest_id>, <giver_troop_id>),
                                      # Starts the quest and marks giver_troop as the troop who gave it.
conclude_quest                = 1286  # (conclude_quest, <quest_id>),
                                      # Sets quest status as concluded but keeps it in the list. Frequently used to indicate "uncertain" quest status, when it's neither fully successful nor a total failure.
succeed_quest                 = 1282  # (succeed_quest, <quest_id>), #also concludes the quest
                                      # Sets quest status as successful but keeps it in the list (player must visit quest giver to complete it before he can get another quest of the same type).
fail_quest                    = 1283  # (fail_quest, <quest_id>), #also concludes the quest
                                      # Sets quest status as failed but keeps it in the list (player must visit quest giver to complete it before he can get another quest of the same type).
complete_quest                = 1281  # (complete_quest, <quest_id>),
                                      # Successfully completes specified quest, removing it from the list of active quests.
cancel_quest                  = 1284  # (cancel_quest, <quest_id>),
                                      # Cancels specified quest without completing it, removing it from the list of active quests.

setup_quest_text              = 1290  # (setup_quest_text, <quest_id>),
                                      # Operation will refresh default quest description (as defined in module_quests.py). This is important when quest description contains references to variables and registers which need to be initialized with their current values.

store_partner_quest           = 2240  # (store_partner_quest, <destination>),
                                      # During conversation, if there's a quest given by conversation partner, the operation will return its id.

setup_quest_giver             = 1291  # (setup_quest_giver, <quest_id>, <string_id>),
                                      # Apparently deprecated, as quest giver troop is now defined as a parameter of (start_quest).
store_random_quest_in_range   = 2250  # (store_random_quest_in_range, <destination>, <lower_bound>, <upper_bound>),
                                      # Apparently deprecated as the logic for picking a new quest has been moved to module_scripts.
set_quest_progression         = 1285  # (set_quest_progression, <quest_id>, <value>),
                                      # Deprecated and useless, operation has no game effects and it's impossible to retrieve quest progression status anyway.
store_random_troop_to_raise   = 2251  # (store_random_troop_to_raise, <destination>, <lower_bound>, <upper_bound>),
                                      # Apparently deprecated.
store_random_troop_to_capture = 2252  # (store_random_troop_to_capture, <destination>, <lower_bound>, <upper_bound>),
                                      # Apparently deprecated.
store_quest_number            = 2261  # (store_quest_number, <destination>, <quest_id>),
                                      # Apparently deprecated.
store_quest_item              = 2262  # (store_quest_item, <destination>, <item_id>),
                                      # Apparently deprecated. Native now uses quest slots to keep track of this information.
store_quest_troop             = 2263  # (store_quest_troop, <destination>, <troop_id>),
                                      # Apparently deprecated. Native now uses quest slots to keep track of this information.

################################################################################
# [ Z12 ] ITEMS
################################################################################

  # The title is a bit deceitful here. Items, despite the name, are not actual
  # game items. Rather these are the *definitions* for real game items, and you
  # can frequently see them referenced as "item types". However you should not
  # confuse this with so called itp_type_* constants which define the major item
  # classes existing in the game.

  # Consider this: a Smoked Fish (50/50) in your character's inventory is an
  # item in the game world. Its item type is "itm_smoked_fish" and its basic
  # class is itp_type_food. So take care: operations in this section are dealing
  # with "itm_smoked_fish", not with actual fish in your inventory. The latter
  # is actually just an inventory slot from the Module System's point of view,
  # and operations to work with it are in the troops section of the file.

# Conditional operations

item_has_property                   = 2723  # (item_has_property, <item_kind_no>, <property>),
                                            # Version 1.161+. Check that the item has specified property flag set. See the list of itp_* flags in header_items.py.
item_has_capability                 = 2724  # (item_has_capability, <item_kind_no>, <capability>),
                                            # Version 1.161+. Checks that the item has specified capability flag set. See the list of itcf_* flags in header_items.py
item_has_modifier                   = 2725  # (item_has_modifier, <item_kind_no>, <item_modifier_no>),
                                            # Version 1.161+. Checks that the specified modifiers is valid for the item. See the list of imod_* values in header_item_modifiers.py.
item_has_faction                    = 2726  # (item_has_faction, <item_kind_no>, <faction_no>),
                                            # Version 1.161+. Checks that the item is available for specified faction. Note that an item with no factions set is available to all factions.

# Item slot operations

item_set_slot                       =  507              # (item_set_slot, <item_id>, <slot_no>, <value>),
item_get_slot                       =  527              # (item_get_slot, <destination>, <item_id>, <slot_no>),
item_slot_eq                        =  547              # (item_slot_eq, <item_id>, <slot_no>, <value>),
item_slot_ge                        =  567              # (item_slot_ge, <item_id>, <slot_no>, <value>),
item_slot_lt                        = neg|item_slot_ge  # (item_slot_lt, <item_id>, <slot_no>, <value>),

# Generic item operations

item_get_type                       = 1570  # (item_get_type, <destination>, <item_id>),
                                            # Returns item class (see header_items.py for itp_type_* constants).
store_item_value                    = 2230  # (store_item_value, <destination>, <item_id>),
                                            # Stores item nominal price as listed in module_items.py. Does not take item modifier or quantity (for food items) into account.
store_random_horse                  = 2257  # (store_random_horse, <destination>),
                                            # Deprecated since early M&B days.
store_random_equipment              = 2258  # (store_random_equipment, <destination>),
                                            # Deprecated since early M&B days.
store_random_armor                  = 2259  # (store_random_armor, <destination>),
                                            # Deprecated since early M&B days.

cur_item_add_mesh                   = 1964  # (cur_item_add_mesh, <mesh_name_string>, [<lod_begin>], [<lod_end>], [<vertex-color>]),
                                            # Version 1.161+. Only call inside ti_on_init_item trigger. Adds another mesh to item, allowing the creation of combined items. Note that in Native the operation (or more precisely the trigger it works in) is for helmets and armor only, it will not trigger for horses, gloves and boots (it works for all items in inventory but it doesn't get called in missions). Parameter <mesh_name_string> should contain mesh name itself, NOT a mesh reference. LOD values are optional at single-mesh items and mandatory at multi-mesh items. If <lod_end> is used, it will not be loaded.
cur_item_set_material               = 1978  # (cur_item_set_material, <string_no>, <sub_mesh_no>, [<lod_begin>], [<lod_end>]),
                                            # Version 1.161+. Only call inside ti_on_init_item trigger. Replaces material that will be used to render the item mesh. Works only for main meta-mesh, so not for scabbards, etc., and does not work for horses, gloves and boots. Use 0 for <sub_mesh_no> to replace material for base mesh. LOD values are optional. If <lod_end> is used, it will not be loaded.

item_get_weight                     = 2700  # (item_get_weight, <destination_fixed_point>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item weight as a fixed point value.
item_get_value                      = 2701  # (item_get_value, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item base price. Essentially a duplicate of (store_item_value).
item_get_difficulty                 = 2702  # (item_get_difficulty, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item difficulty value.
item_get_head_armor                 = 2703  # (item_get_head_armor, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item head armor value.
item_get_body_armor                 = 2704  # (item_get_body_armor, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item body armor value.
item_get_leg_armor                  = 2705  # (item_get_leg_armor, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item leg armor value.
item_get_hit_points                 = 2706  # (item_get_hit_points, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item hit points amount.
item_get_weapon_length              = 2707  # (item_get_weapon_length, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item length (for weapons) or shield half-width (for shields). To get actual shield width, multiply this value by 2. Essentially, it is a distance from shield's "center" point to its left, right and top edges (and bottom edge as well if shield height is not defined).
item_get_speed_rating               = 2708  # (item_get_speed_rating, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item speed rating.
item_get_missile_speed              = 2709  # (item_get_missile_speed, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item missile speed rating.
item_get_max_ammo                   = 2710  # (item_get_max_ammo, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item max ammo amount. Ignores large bag modifier.
item_get_accuracy                   = 2711  # (item_get_accuracy, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves item accuracy value. Note that this operation will return 0 for an item with undefined accuracy, even though the item accuracy will actually default to 100.
item_get_shield_height              = 2712  # (item_get_shield_height, <destination_fixed_point>, <item_kind_no>),
                                            # Version 1.161+. Retrieves distance from shield "center" to its bottom edge as a fixed point number. Use (set_fixed_point_multiplier, 100), to retrieve the correct value with this operation. To get actual shield height, use shield_height + weapon_length if this operation returns a non-zero value, otherwise use 2 * weapon_length.
item_get_horse_scale                = 2713  # (item_get_horse_scale, <destination_fixed_point>, <item_kind_no>),
                                            # Version 1.161+. Retrieves horse scale value as fixed point number.
item_get_horse_speed                = 2714  # (item_get_horse_speed, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves horse speed value.
item_get_horse_maneuver             = 2715  # (item_get_horse_maneuver, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves horse maneuverability value.
item_get_food_quality               = 2716  # (item_get_food_quality, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves food quality coefficient (as of Warband 1.165, this coefficient is actually set for many food items, but never used in the code as there was no way to retrieve this coeff before 1.161 patch).
item_get_abundance                  = 2717  # (item_get_abundance, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieve item abundance value. Note that this operation will return 0 for an item with undefined abundance, even though the item abundance will actually default to 100.
item_get_thrust_damage              = 2718  # (item_get_thrust_damage, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves thrust base damage value for item.
item_get_thrust_damage_type         = 2719  # (item_get_thrust_damage_type, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves thrust damage type for item (see definitions for "cut", "pierce" and "blunt" in header_items.py).
item_get_swing_damage               = 2720  # (item_get_swing_damage, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves swing base damage value for item.
item_get_swing_damage_type          = 2721  # (item_get_swing_damage_type, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves swing damage type for item (see definitions for "cut", "pierce" and "blunt" in header_items.py).
item_get_horse_charge_damage        = 2722  # (item_get_horse_charge_damage, <destination>, <item_kind_no>),
                                            # Version 1.161+. Retrieves horse charge base damage.

################################################################################
# [ Z13 ] SOUNDS AND MUSIC TRACKS
################################################################################

  # There are two types of sound in the game: sounds and tracks. Sounds are just
  # short sound effects. They can be positional (i.e. emitted by some object on
  # the scene or by player's opponent during the dialog). They can be generic
  # sound effects, like playing some drums when player meets mountain bandits.

  # Tracks are the background music. The game works as a kind of a musuc box,
  # cycling the available melodies according to the situation. It is up to the
  # Module System developer, however, to tell the game what the situation is.
  # There are two factors which you can tell the game: situation and culture.
  # So you can tell the game that the situation is "ambush" and the culture is
  # "khergits", and the game will select the musuc tracks which fit this
  # combination of situation and culture and will rotate them randomly. And of
  # course, you can also tell the game to play one specific track if you want.

play_sound_at_position   =  599  # (play_sound_at_position, <sound_id>, <position>, [options]),
                                 # Plays a sound in specified scene position. See sf_* flags in header_sounds.py for reference on possible options.
play_sound               =  600  # (play_sound, <sound_id>, [options]),
                                 # Plays a sound. If the operation is called from agent, scene_prop or item trigger, then the sound will be positional and 3D. See sf_* flags in header_sounds.py for reference on possible options.
play_track               =  601  # (play_track, <track_id>, [options]),
                                 # Plays specified music track. Possible options: 0 = finish current then play this, 1 = fade out current and start this, 2 = stop current abruptly and start this
play_cue_track           =  602  # (play_cue_track, <track_id>),
                                 # Plays specified music track OVER any currently played music track (so you can get two music tracks playing simultaneously). Hardly useful.
music_set_situation      =  603  # (music_set_situation, <situation_type>),
                                 # Sets current situation(s) in the game (see mtf_* flags in header_music.py for reference) so the game engine can pick matching tracks from module_music.py. Use 0 to stop any currently playing music (it will resume when situation is later set to something).
music_set_culture        =  604  # (music_set_culture, <culture_type>),
                                 # Sets current culture(s) in the game (see mtf_* flags in header_music.py for reference) so the game engine can pick matching tracks from module_music.py. Use 0 to stop any currently playing music (it will resume when cultures are later set to something).
stop_all_sounds          =  609  # (stop_all_sounds, [options]),
                                 # Stops all playing sounds. Version 1.153 options: 0 = stop only looping sounds, 1 = stop all sounds. Version 1.143 options: 0 = let current track finish, 1 = fade it out, 2 = stop it abruptly.
store_last_sound_channel =  615  # (store_last_sound_channel, <destination>),
                                 # Version 1.153+. UNTESTED. Stores the sound channel used for the last sound operation.
                                 # Can fail. Returns -1 as value. For agent_play_sound; play_sound - if called from item, scene_prop trigger. (up4research)
stop_sound_channel       =  616  # (stop_sound_channel, <sound_channel_no>),
                                 # Version 1.153+.  Used to fix bug with looping sounds in Viking Conquest.
                                 # There are 256 sound channels. The closest agent has 0 channel. The farthest agents will rewrite last 10 channels.

################################################################################
# [ Z14 ] POSITIONS
################################################################################

  # Positions are the 3D math of the game. If you want to handle objects in
  # space, you will inevitably have to deal with positions. Note that while most
  # position-handling operations work both on global map and on the scenes,
  # there are operations which will only work in one or another mode.

  # Each position consists of three parts: coordinates, rotation and scale.

  # Coordinates are three numbers - (X,Y,Z) - which define a certain point in
  # space relative to the base of coordinates. Most of the time, the base of
  # coordinates is either the center of the global map, or the center of the
  # scene, but there may be exceptions. Note that all operations with
  # coordinates nearly always use fixed point numbers.

  # Position rotation determines just that - rotation around corresponding
  # world axis. So rotation around Z axis means rotation around vertical axis,
  # in other words - turning right and left. Rotation around X and Y axis will
  # tilt the position forward/backwards and right/left respectively.

  # It is common game convention that X world axis points to the East, Y world
  # axis points to the North and Z world axis points straight up. However this
  # is so-called global coordinates system, and more often than not you'll be
  # dealing with local coordinates. Local coordinates are the coordinate system
  # defined by the object's current position. For the object, his X axis is to
  # the right, Y axis is forward, and Z axis is up. This is simple enough, but
  # consider what happens if that object is turned upside down in world space?
  # Object's Z axis will point upwards *from the object's point of view*, in
  # other words, in global space it will be pointing *downwards*. And if the
  # object is moving, then its local coordinates system is moving with it...
  # you get the idea.

  # Imagine the position as a small point with an arrow somewhere in space.
  # Position's coordinates are the point's position. Arrow points horizontally
  # to the North by default, and position's rotation determines how much was
  # it turned in the each of three directions.

  # Final element of position is scale. It is of no direct relevance to the
  # position itself, and it does not participate in any calculations. However
  # it is important when you retrieve or set positions of objects. In this
  # case, position's scale is object's scale - so you can shrink that wall
  # or quite the opposite, make it grow to the sky, depending on your whim.

# Generic position operations

init_position                               =  701  # (init_position, <position>),
                                                    # Sets position coordinates to [0,0,0], without any rotation and default scale.
                                                    # A not initialized position has the values (-1000,-1000,0, 0,0,0); fpm=1 (x,y,z, x-rot,y-rot,z-rot).
copy_position                               =  700  # (copy_position, <position_target>, <position_source>),
                                                    # Makes a duplicate of position_source.
position_copy_origin                        =  719  # (position_copy_origin, <position_target>, <position_source>),
                                                    # Copies coordinates from source position to target position, without changing rotation or scale.
position_copy_rotation                      =  718  # (position_copy_rotation, <position_target>, <position_source>),
                                                    # Copies rotation from source position to target position, without changing coordinates or scale.

position_transform_position_to_parent       =  716  # (position_transform_position_to_parent, <position_dest>, <position_anchor>, <position_relative_to_anchor>),
                                                    # Converts position from local coordinate space to parent coordinate space. In other words, if you have some position on the scene (anchor) and a position describing some place *relative* to anchor (for example [10,20,0] means "20 meters forward and 10 meters to the right"), after calling this operation you will get that position coordinates on the scene in <position_dest>. Rotation and scale is also taken care of, so you can use relative angles.
position_transform_position_to_local        =  717  # (position_transform_position_to_local, <position_dest>, <position_anchor>, <position_source>),
                                                    # The opposite to (position_transform_position_to_parent), this operation allows you to get source's *relative* position to your anchor. Suppose you want to run some decision making for your bot agent depending on player's position. In order to know where player is located relative to your bot you call (position_transform_position_to_local, <position_dest>, <bot_position>, <player_position>). Then we check position_dest's Y coordinate - if it's negative, then the player is behind our bot's back.

# Position (X,Y,Z) coordinates

position_get_x                              =  726  # (position_get_x, <destination_fixed_point>, <position>),
                                                    # Return position X coordinate (to the east, or to the right). Base unit is meters. Use (set_fixed_point_multiplier) to set another measurement unit (100 will get you centimeters, 1000 will get you millimeters, etc).
position_get_y                              =  727  # (position_get_y, <destination_fixed_point>, <position>),
                                                    # Return position Y coordinate (to the north, or forward). Base unit is meters. Use (set_fixed_point_multiplier) to set another measurement unit (100 will get you centimeters, 1000 will get you millimeters, etc).
position_get_z                              =  728  # (position_get_z, <destination_fixed_point>, <position>),
                                                    # Return position Z coordinate (to the top). Base unit is meters. Use (set_fixed_point_multiplier) to set another measurement unit (100 will get you centimeters, 1000 will get you millimeters, etc).

position_set_x                              =  729  # (position_set_x, <position>, <value_fixed_point>),
                                                    # Set position X coordinate.
position_set_y                              =  730  # (position_set_y, <position>, <value_fixed_point>),
                                                    # Set position Y coordinate.
position_set_z                              =  731  # (position_set_z, <position>, <value_fixed_point>),
                                                    # Set position Z coordinate.

position_move_x                             =  720  # (position_move_x, <position>, <movement>, [value]),
                                                    # Moves position along X axis. Movement distance is in cms. Optional parameter determines whether the position is moved along the local (value=0) or global (value=1) X axis (i.e. whether the position will be moved to its right/left, or to the global east/west).
position_move_y                             =  721  # (position_move_y, <position>, <movement>,[value]),
                                                    # Moves position along Y axis. Movement distance is in cms. Optional parameter determines whether the position is moved along the local (value=0) or global (value=1) Y axis (i.e. whether the position will be moved forward/backwards, or to the global north/south).
position_move_z                             =  722  # (position_move_z, <position>, <movement>,[value]),
                                                    # Moves position along Z axis. Movement distance is in cms. Optional parameter determines whether the position is moved along the local (value=0) or global (value=1) Z axis (i.e. whether the position will be moved to its above/below, or to the global above/below - these directions will be different if the position is tilted).

position_set_z_to_ground_level              =  791  # (position_set_z_to_ground_level, <position>),
                                                    # This will bring the position Z coordinate so it rests on the ground level (i.e. an agent could stand on that position). This takes scene props with their collision meshes into account. Only works during a mission, so you can't measure global map height using this.
position_get_distance_to_terrain            =  792  # (position_get_distance_to_terrain, <destination_fixed_point>, <position>),
                                                    # This will measure the distance (in a fixed point value) between position and terrain below, ignoring all scene props and their collision meshes. Retrieves a negative value if underground. Operation only works on the scenes and cannot be used on the global map.
position_get_distance_to_ground_level       =  793  # (position_get_distance_to_ground_level, <destination_fixed_point>, <position>),
                                                    # This will measure the distance (in a fixed point value) between position and the ground level, taking scene props and their collision meshes into account. Retrieves a negative value if underground. Operation only works on the scenes and cannot be used on the global map.

# Position rotation

position_get_rotation_around_x              =  742  # (position_get_rotation_around_x, <destination>, <position>),
                                                    # Returns angle (in degrees) that the position is rotated around X axis (tilt forward/backwards).
position_get_rotation_around_y              =  743  # (position_get_rotation_around_y, <destination>, <position>),
                                                    # Returns angle (in degrees) that the position is rotated around Y axis (tilt right/left).
position_get_rotation_around_z              =  740  # (position_get_rotation_around_z, <destination>, <position>),
                                                    # Returns angle (in degrees) that the position is rotated around Z axis (turning right/left).

position_rotate_x                           =  723  # (position_rotate_x, <position>, <angle>),
                                                    # Rotates position around its X axis (tilt forward/backwards).
position_rotate_y                           =  724  # (position_rotate_y, <position>, <angle>),
                                                    # Rotates position around Y axis (tilt right/left).
position_rotate_z                           =  725  # (position_rotate_z, <position>, <angle>, [use_global_z_axis]),
                                                    # Rotates position around Z axis (rotate right/left). Pass 1 for use_global_z_axis to rotate the position around global axis instead.

position_rotate_x_floating                  =  738  # (position_rotate_x_floating, <position>, <angle_fixed_point>),
                                                    # Same as (position_rotate_x), but takes fixed point value as parameter, allowing for more precise rotation.
position_rotate_y_floating                  =  739  # (position_rotate_y_floating, <position>, <angle_fixed_point>),
                                                    # Same as (position_rotate_y), but takes fixed point value as parameter, allowing for more precise rotation.
position_rotate_z_floating                  =  734  # (position_rotate_z_floating, <position_no>, <angle_fixed_point>, [use_global_z_axis]),
                                                    # Version 1.161+. Same as (position_rotate_z), but takes fixed point value as parameter, allowing for more precise rotation.
                                                    # Pass 1 for use_global_z_axis to rotate the position around global axis instead.

# Position scale

position_get_scale_x                        =  735  # (position_get_scale_x, <destination_fixed_point>, <position>),
                                                    # Retrieves position scaling along X axis.
position_get_scale_y                        =  736  # (position_get_scale_y, <destination_fixed_point>, <position>),
                                                    # Retrieves position scaling along Y axis.
position_get_scale_z                        =  737  # (position_get_scale_z, <destination_fixed_point>, <position>),
                                                    # Retrieves position scaling along Z axis.

position_set_scale_x                        =  744  # (position_set_scale_x, <position>, <value_fixed_point>),
                                                    # Sets position scaling along X axis.
position_set_scale_y                        =  745  # (position_set_scale_y, <position>, <value_fixed_point>),
                                                    # Sets position scaling along Y axis.
position_set_scale_z                        =  746  # (position_set_scale_z, <position>, <value_fixed_point>),
                                                    # Sets position scaling along Z axis.

# Measurement of distances and angles

get_angle_between_positions                 =  705  # (get_angle_between_positions, <destination_fixed_point>, <position_no_1>, <position_no_2>),
                                                    # Calculates angle between positions, using positions as vectors. Only rotation around Z axis is used. In other words, the function returns the difference between Z rotations of both positions.
position_has_line_of_sight_to_position      =  707  # (position_has_line_of_sight_to_position, <position_no_1>, <position_no_2>),
                                                    # Checks that you can see one position from another. This obviously implies that both positions must be in global space. Note this is computationally expensive, so try to keep number of these to a minimum.
get_distance_between_positions              =  710  # (get_distance_between_positions, <destination>, <position_no_1>, <position_no_2>),
                                                    # Returns distance between positions in centimeters.
get_distance_between_positions_in_meters    =  711  # (get_distance_between_positions_in_meters, <destination>, <position_no_1>, <position_no_2>),
                                                    # Returns distance between positions in meters.
get_sq_distance_between_positions           =  712  # (get_sq_distance_between_positions, <destination>, <position_no_1>, <position_no_2>),
                                                    # Returns squared distance between two positions in centimeters.
get_sq_distance_between_positions_in_meters =  713  # (get_sq_distance_between_positions_in_meters, <destination>, <position_no_1>, <position_no_2>),
                                                    # Returns squared distance between two positions in meters.
position_is_behind_position                 =  714  # (position_is_behind_position, <position_base>, <position_to_check>),
                                                    # Checks if the second position is behind the first.
get_sq_distance_between_position_heights    =  715  # (get_sq_distance_between_position_heights, <destination>, <position_no_1>, <position_no_2>),
                                                    # Returns squared distance between position *heights* in centimeters.
position_normalize_origin                   =  741  # (position_normalize_origin, <destination_fixed_point>, <position>),
                                                    # What this operation seems to do is calculate the distance between the zero point [0,0,0] and the point with position's coordinates. Can be used to quickly calculate distance to relative positions.
position_get_screen_projection              =  750  # (position_get_screen_projection, <position_screen>, <position_world>),
                                                    # Calculates the screen coordinates of the position and stores it as position_screen's X and Y coordinates. Works in missions. Not shure if it works on global map.
                                                    # <position> coordinates transform so distance becomes 1 meter. Then x,y coordinates can be multiplied, for example, by 10 and new position will be 10 meters in that direction.

# Global map positions

map_get_random_position_around_position     = 1627  # (map_get_random_position_around_position, <dest_position_no>, <source_position_no>, <radius>),
                                                    # Returns a random position on the global map in the vicinity of the source_position.
map_get_land_position_around_position       = 1628  # (map_get_land_position_around_position, <dest_position_no>, <source_position_no>, <radius>),
                                                    # Returns a random position on the global map in the vicinity of the source_position. Will always return a land position (i.e. some place you can walk to).
map_get_water_position_around_position      = 1629  # (map_get_water_position_around_position, <dest_position_no>, <source_position_no>, <radius>),
                                                    # Returns a random position on the global map in the vicinity of the source_position. Will always return a water position (i.e. sea, lake or river).

################################################################################
# [ Z15 ] GAME NOTES
################################################################################

  # The game provides the player with the Notes screen, where there are several
  # sections: Troops, Factions, Parties, Quests and Information. This is the
  # player's "diary", where all information player knows is supposed to be
  # stored. With the operations from this section, modder can control what
  # objects the player will be able to see in their corresponding sections of
  # the Notes screen, and what information will be displayed on each object.

  # Note that there's a number of engine-called scripts which take priority to
  # text notes created by these operations. Any information in these notes will
  # only be visible to the player if those scripts "refuse" to generate the note
  # page dynamically. The following scripts can override these notes:
  #   script_game_get_troop_note
  #   script_game_get_center_note
  #   script_game_get_faction_note
  #   script_game_get_quest_note
  #   script_game_get_info_page_note

troop_set_note_available        = 1095 # (troop_set_note_available, <troop_id>, <value>),
                                       # Enables (value = 1) or disables (value = 0) troop's page in the Notes / Characters section.
add_troop_note_tableau_mesh     = 1108 # (add_troop_note_tableau_mesh, <troop_id>, <tableau_material_id>),
                                       # Adds graphical elements to the troop's information page (usually banner and portrait).
add_troop_note_from_dialog      = 1114 # (add_troop_note_from_dialog, <troop_id>, <note_slot_no>, <expires_with_time>),
                                       # Adds current dialog text to troop notes. Each troop has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_troop_note_from_dialog,<troop_id>,<note_slot_no>, <value>), #There are maximum of 8 slots. value = 1 -> shows when the note is added
add_troop_note_from_sreg        = 1117 # (add_troop_note_from_sreg, <troop_id>, <note_slot_no>, <string_id>, <expires_with_time>),
                                       # Adds any text stored in string register to troop notes. Each troop has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_troop_note_from_sreg,<troop_id>,<note_slot_no>,<string_id>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added

faction_set_note_available      = 1096 # (faction_set_note_available, <faction_id>, <value>), #1 = available, 0 = not available
                                       # Enables (value = 1) or disables (value = 0) faction's page in the Notes / Characters section.
add_faction_note_tableau_mesh   = 1109 # (add_faction_note_tableau_mesh, <faction_id>, <tableau_material_id>),
                                       # Adds graphical elements to the faction's information page (usually graphical collage).
add_faction_note_from_dialog    = 1115 # (add_faction_note_from_dialog, <faction_id>, <note_slot_no>, <expires_with_time>),
                                       # Adds current dialog text to faction notes. Each faction has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_faction_note_from_dialog,<faction_id>,<note_slot_no>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added
add_faction_note_from_sreg      = 1118 # (add_faction_note_from_sreg, <faction_id>, <note_slot_no>, <string_id>, <expires_with_time>),
                                       # Adds any text stored in string register to faction notes. Each faction has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_faction_note_from_sreg,<faction_id>,<note_slot_no>,<string_id>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added

party_set_note_available        = 1097 # (party_set_note_available, <party_id>, <value>), #1 = available, 0 = not available
                                       # Enables (value = 1) or disables (value = 0) party's page in the Notes / Characters section.
add_party_note_tableau_mesh     = 1110 # (add_party_note_tableau_mesh, <party_id>, <tableau_material_id>),
                                       # Adds graphical elements to the party's information page (usually map icon).
add_party_note_from_dialog      = 1116 # (add_party_note_from_dialog, <party_id>, <note_slot_no>, <expires_with_time>),
                                       # Adds current dialog text to party notes. Each party has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_party_note_from_dialog,<party_id>,<note_slot_no>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added
add_party_note_from_sreg        = 1119 # (add_party_note_from_sreg, <party_id>, <note_slot_no>, <string_id>, <expires_with_time>),
                                       # Adds any text stored in string register to party notes. Each party has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_party_note_from_sreg,<party_id>,<note_slot_no>,<string_id>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added

quest_set_note_available        = 1098 # (quest_set_note_available, <quest_id>, <value>), #1 = available, 0 = not available
                                       # Enables (value = 1) or disables (value = 0) quest's page in the Notes / Characters section.
add_quest_note_tableau_mesh     = 1111 # (add_quest_note_tableau_mesh, <quest_id>, <tableau_material_id>),
                                       # Adds graphical elements to the quest's information page (not used in Native).
add_quest_note_from_dialog      = 1112 # (add_quest_note_from_dialog, <quest_id>, <note_slot_no>, <expires_with_time>),
                                       # Adds current dialog text to quest notes. Each quest has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_quest_note_from_dialog,<quest_id>,<note_slot_no>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added
add_quest_note_from_sreg        = 1113 # (add_quest_note_from_sreg, <quest_id>, <note_slot_no>, <string_id>, <expires_with_time>),
                                       # Adds any text stored in string register to quest notes. Each quest has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_quest_note_from_sreg,<quest_id>,<note_slot_no>,<string_id>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added

add_info_page_note_tableau_mesh = 1090 # (add_info_page_note_tableau_mesh, <info_page_id>, <tableau_material_id>),
                                       # Adds graphical elements to the info page (not used in Native).
add_info_page_note_from_dialog  = 1091 # (add_info_page_note_from_dialog, <info_page_id>, <note_slot_no>, <expires_with_time>),
                                       # Adds current dialog text to info page notes. Each info page has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_info_page_note_from_dialog,<info_page_id>,<note_slot_no>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added
add_info_page_note_from_sreg    = 1092 # (add_info_page_note_from_sreg, <info_page_id>, <note_slot_no>, <string_id>, <expires_with_time>),
                                       # Adds any text stored in string register to info page notes. Each info page has 16 note slots. Last parameter is used to mark the note as time-dependent, if its value is 1, then the note will be marked ("Report is current") and will be updated appropriately as the game progresses ("Report is X days old").
                                       # Official: (add_info_page_note_from_sreg,<info_page_id>,<note_slot_no>,<string_id>, <value>), #There are maximum of 8 slots value = 1 -> shows when the note is added

################################################################################
# [ Z16 ] TABLEAUS AND HERALDICS
################################################################################

  # Tableaus are the tool that gives you limited access to the game graphical
  # renderer. If you know 3D graphics, you know that all 3D objects consist of
  # a mesh (which defines its form) and the material (which defines how this
  # mesh is "painted"). With tableau functions you can do two things. First, you
  # can replace or alter the materials used to render the game objects (with
  # many restrictions). If this sounds esoteric to you, have a look at the game
  # heraldry - it is implemented using tableaus. Second, you can render images
  # of various game objects and place them on the game menus, presentations and
  # so on. For example, if you open the game Inventory window, you can see your
  # character in his current equipment. This character is rendered using tableau
  # operations. Similarly, if you open the Notes screen and select some kingdom
  # lord on the Troops section, you will see that lord's face and banner. Both
  # face and banner are drawn using tableaus.

cur_item_set_tableau_material                    = 1981  # (cur_item_set_tableu_material, <tableau_material_id>, <instance_code>),
                                                         # Can only be used inside ti_on_init_item trigger in module_items.py. Assigns tableau to the item instance. Value of <instance_code> will be passed to tableau code. Commonly used for heraldic armors and shields.
cur_scene_prop_set_tableau_material              = 1982  # (cur_scene_prop_set_tableau_material, <tableau_material_id>, <instance_code>),
                                                         # Can only be used inside ti_on_init_scene_prop trigger in module_scene_props.py. Assigns tableau to the scene prop instance. Value of <instance_code> will be passed to tableau code. Commonly used for static banners.
cur_map_icon_set_tableau_material                = 1983  # (cur_map_icon_set_tableau_material, <tableau_material_id>, <instance_code>),
                                                         # Can only be used inside ti_on_init_map_icon trigger in module_map_icons.py. Assigns tableau to the icon prop instance. Value of <instance_code> will be passed to tableau code. Commonly used for player/lord party banners.
cur_agent_set_banner_tableau_material            = 1986  # (cur_agent_set_banner_tableau_material, <tableau_material_id>),
                                                         # Can only be used inside ti_on_agent_spawn trigger in module_mission_templates. Assigns heraldry.

# Operations used in module_tableau_materials.py module

cur_tableau_add_tableau_mesh                     = 1980  # (cur_tableau_add_tableau_mesh, <tableau_material_id>, <value>, <position_register_no>),
                                                         # Used in module_tableau_materials.py to add one tableau to another. Value parameter is passed to tableau_material as is.
cur_tableau_render_as_alpha_mask                 = 1984  # (cur_tableau_render_as_alpha_mask)
                                                         # Tells the engine to treat the tableau as an alpha (transparency) mask.
cur_tableau_set_background_color                 = 1985  # (cur_tableau_set_background_color, <value>),
                                                         # Defines solid background color for the current tableau.
cur_tableau_set_ambient_light                    = 1987  # (cur_tableau_set_ambient_light, <red_fixed_point>, <green_fixed_point>, <blue_fixed_point>),
                                                         # Not documented. Used for tableaus rendered from 3D objects to provide uniform tinted lighting.
cur_tableau_set_camera_position                  = 1988  # (cur_tableau_set_camera_position, <position>),
                                                         # Not documented. Used for tableaus rendered from 3D objects to position camera as necessary (usually with a perspective camera).
cur_tableau_set_camera_parameters                = 1989  # (cur_tableau_set_camera_parameters, <is_perspective>, <camera_width_times_1000>, <camera_height_times_1000>, <camera_near_times_1000>, <camera_far_times_1000>),
                                                         # Not documented. Used to define camera parameters for tableau rendering. Perspective camera is generally used to render 3D objects for tableaus, while non-perspective camera is used to modify tableau texture meshes.
cur_tableau_add_point_light                      = 1990  # (cur_tableau_add_point_light, <position>, <red_fixed_point>, <green_fixed_point>, <blue_fixed_point>),
                                                         # Not documented. Typically used for tableaus rendered from 3D objects to add a point light source.
cur_tableau_add_sun_light                        = 1991  # (cur_tableau_add_sun_light, <position>, <red_fixed_point>, <green_fixed_point>, <blue_fixed_point>),
                                                         # Not documented. Typically used for tableaus rendered from 3D objects to add a directional light source. Note that position coordinates do not matter, only rotation (i.e. light rays direction) does.
cur_tableau_add_mesh                             = 1992  # (cur_tableau_add_mesh, <mesh_id>, <position>, <value_fixed_point>, <value_fixed_point>),
                                                         # Adds a static mesh to the tableau with specified offset, scale and alpha. First value fixed point is the scale factor, second value fixed point is alpha. use 0 for default values.
cur_tableau_add_mesh_with_vertex_color           = 1993  # (cur_tableau_add_mesh_with_vertex_color, <mesh_id>, <position>, <value_fixed_point>, <value_fixed_point>, <value>),
                                                         # Adds a static mesh to the tableau with specified offset, scale, alpha and vertex color. First value fixed point is the scale factor, second value fixed point is alpha. Value is vertex color.
cur_tableau_add_mesh_with_scale_and_vertex_color = 2000  # (cur_tableau_add_mesh_with_scale_and_vertex_color, <mesh_id>, <position>, <scale_position>, <value_fixed_point>, <value>),
                                                         # Similar to (cur_tableau_add_mesh_with_vertex_color), but allows non-uniform scaling. Scale factors are stored as (x,y,z) position properties with fixed point values.
cur_tableau_add_map_icon                         = 1994  # (cur_tableau_add_map_icon, <map_icon_id>, <position>, <value_fixed_point>),
                                                         # Adds a rendered image of a map icon to current tableau. Last parameter is the scale factor for the model.
cur_tableau_add_troop                            = 1995  # (cur_tableau_add_troop, <troop_id>, <position>, <animation_id>, <instance_no>),
                                                         # Adds a rendered image of the troop in a specified animation to current tableau. If instance_no is 0 or less, then the face is not generated randomly (important for heroes).
cur_tableau_add_horse                            = 1996  # (cur_tableau_add_horse, <item_id>, <position>, <animation_id>),
                                                         # Adds a rendered image of a horse in a specified animation to current tableau.
cur_tableau_set_override_flags                   = 1997  # (cur_tableau_set_override_flags, <value>),
                                                         # When creating a troop image for current tableau, this operation allows to override troop's inventory partially or completely. See af_* flags in header_mission_templates.py for reference.
cur_tableau_clear_override_items                 = 1998  # (cur_tableau_clear_override_items),
                                                         # Removes and previously defined equipment overrides for the troop, allowing to start from scratch.
cur_tableau_add_override_item                    = 1999  # (cur_tableau_add_override_item, <item_kind_id>),
                                                         # When creating a troop image for current tableau, the operation will add a new item to troop's equipment.

################################################################################
# [ Z17 ] STRING OPERATIONS
################################################################################

  # The game provides you only limited control over string information. Most
  # operations will either retrieve some string (usually the name) from the game
  # object, or set that object's name to a string.

  # Two important functions are str_store_string and str_store_string_reg. They
  # are different from all others because they not only assign the string to a
  # string register, they *process* it. For example, if source string contains
  # "{reg3}", then the resulting string will have the register name and its
  # surrounding brackets replaced with the value currently stored in that
  # register. Other strings can be substituted as well, and even some limited
  # logic can be implemented using this mechanism. You can try to read through
  # the module_strings.py file and try to deduce what each particular
  # substitution does.

# Conditional operations

str_is_empty                    = 2318  # (str_is_empty, <string_register>),
                                        # Checks that referenced string register is empty.

# Other string operations

str_clear                       = 2319  # (str_clear, <string_register>),
                                        # Clears the contents of the referenced string register.
str_store_string                = 2320  # (str_store_string, <string_register>, <string_id>),
                                        # Stores a string value in the referenced string register. Only string constants and quick strings can be stored this way.
str_store_string_reg            = 2321  # (str_store_string_reg, <string_register>, <string_no>),
                                        # Copies the contents of one string register from another.
str_store_troop_name            = 2322  # (str_store_troop_name, <string_register>, <troop_id>),
                                        # Stores singular troop name in referenced string register.
str_store_troop_name_plural     = 2323  # (str_store_troop_name_plural, <string_register>, <troop_id>),
                                        # Stores plural troop name in referenced string register.
str_store_troop_name_by_count   = 2324  # (str_store_troop_name_by_count, <string_register>, <troop_id>, <number>),
                                        # Stores singular or plural troop name with number of troops ("29 Archers", "1 Bandit").
str_store_item_name             = 2325  # (str_store_item_name, <string_register>, <item_id>),
                                        # Stores singular item name in referenced string register.
str_store_item_name_plural      = 2326  # (str_store_item_name_plural, <string_register>, <item_id>),
                                        # Stores plural item name in referenced string register. Plural names need first to be activated (altering process_items.py and setting up plural names at module_items).
str_store_item_name_by_count    = 2327  # (str_store_item_name_by_count, <string_register>, <item_id>),
                                        # Stores singular or plural item name with number of items ("11 Swords", "1 Bottle of Wine"). Counting does always work, plural names need first to be activated (altering process_items.py and setting up plural names at module_items).
str_store_party_name            = 2330  # (str_store_party_name, <string_register>, <party_id>),
                                        # Stores party name in referenced string register.
str_store_agent_name            = 2332  # (str_store_agent_name, <string_register>, <agent_id>),
                                        # Stores agent name in referenced string register.
str_store_faction_name          = 2335  # (str_store_faction_name, <string_register>, <faction_id>),
                                        # Stores faction name in referenced string register.
str_store_quest_name            = 2336  # (str_store_quest_name, <string_register>, <quest_id>),
                                        # Stores quest name (as defined in module_quests.py) in referenced string register.
str_store_info_page_name        = 2337  # (str_store_info_page_name, <string_register>, <info_page_id>),
                                        # Stores info page title (as defined in module_info_pages.py) in referenced string register.
str_store_date                  = 2340  # (str_store_date, <string_register>, <number_of_hours_to_add_to_the_current_date>),
                                        # Stores formatted date string, using the number of hours since start of the game (can be retrieved by a call to store_current_hours).
str_store_troop_name_link       = 2341  # (str_store_troop_name_link, <string_register>, <troop_id>),
                                        # Stores troop name as an internal game link. Resulting string can be used in game notes, will be highlighted, and clicking on it will redirect the player to the details page of the referenced troop.
str_store_party_name_link       = 2342  # (str_store_party_name_link, <string_register>, <party_id>),
                                        # Stores party name as an internal game link. Resulting string can be used in game notes, will be highlighted, and clicking on it will redirect the player to the details page of the referenced party.
str_store_faction_name_link     = 2343  # (str_store_faction_name_link, <string_register>, <faction_id>),
                                        # Stores faction name as an internal game link. Resulting string can be used in game notes, will be highlighted, and clicking on it will redirect the player to the details page of the referenced faction.
str_store_quest_name_link       = 2344  # (str_store_quest_name_link, <string_register>, <quest_id>),
                                        # Stores quest name as an internal game link. Resulting string can be used in game notes, will be highlighted, and clicking on it will redirect the player to the details page of the referenced quest.
str_store_info_page_name_link   = 2345  # (str_store_info_page_name_link, <string_register>, <info_page_id>),
                                        # Stores info page title as an internal game link. Resulting string can be used in game notes, will be highlighted, and clicking on it will redirect the player to the details page of the referenced info page.
str_store_class_name            = 2346  # (str_store_class_name, <string_register>, <class_id>),
                                        # Stores name of the selected troop class (Infantry, Archers, Cavalry or any of the custom class names) in referenced string register.
game_key_get_mapped_key_name    =   65  # (game_key_get_mapped_key_name, <string_register>, <game_key>),
                                        # Version 1.161+. Stores human-readable key name that's currently assigned to the provided game key. May store "unknown" and "No key assigned" strings (the latter is defined in languages/en/ui.csv, the former seems to be hardcoded).

# Network/multiplayer-related string operations

str_store_player_username       = 2350  # (str_store_player_username, <string_register>, <player_id>),
                                        # Stores player's multiplayer username in referenced string register. Can be used in multiplayer mode only.
str_store_server_password       = 2351  # (str_store_server_password, <string_register>),
                                        # Stores server's password in referenced string register.
str_store_server_name           = 2352  # (str_store_server_name, <string_register>),
                                        # Stores server's name (as displayed to clients in server's list window) in referenced string register.
str_store_welcome_message       = 2353  # (str_store_welcome_message, <string_register>),
                                        # Stores server's welcome message in referenced string register.
str_encode_url                  = 2355  # (str_encode_url, <string_register>),
                                        # This operation will "sanitize" a string to be used as part of network URL, replacing any non-standard characters with their '%'-codes.

################################################################################
# [ Z18 ] OUTPUT AND MESSAGES
################################################################################

  # These operations will provide some textual information to the player during
  # the game. There are three operations which will generate a game message
  # (displayed as a chat-like series of text strings in the bottom-left part of
  # the screen), while most others will be displaying various types of dialog
  # boxes. You can also ask a question to player using these operations.
  # You can clear message list in right bottom corner by dislpaing an empty string. Also when spaming messages shut down the display log it will be visible again.
  # (display_message, "@{!}"),
  # This will create a quick string. Another approach is to display an empty string register.
  # (str_clear, s0), (display_message),
  # (display_message), without parameters displays the s0 string register. It should be initialisized, i.e. it is necessary to (str_clear, s0), even at the begining of the game.

display_debug_message               = 1104  # (display_debug_message, <string_id>, [hex_colour_code]),
                                            # Displays a string message, but only in debug mode, using provided color (hex-coded 0xRRGGBB). The message is additionally written to rgl_log.txt file in both release and debug modes when edit mode is enabled.
display_log_message                 = 1105  # (display_log_message, <string_id>, [hex_colour_code]),
                                            # Display a string message using provided color (hex-coded 0xRRGGBB). The message will also be written to game log (accessible through Notes / Game Log), and will persist between sessions (i.e. it will be stored as part of the savegame).
display_message                     = 1106  # (display_message, <string_id>,[hex_colour_code]),
                                            # Display a string message using provided color (hex-coded 0xRRGGBB).
                                            # When edit mode is enabled it also writes to rgl_log.
set_show_messages                   = 1107  # (set_show_messages, <value>),
                                            # Suppresses (value = 0) or enables (value = 1) game messages, including those generated by the game engine.
tutorial_box                        = 1120  # (tutorial_box, <string_id>, <string_id>),
                                            # This operation is deprecated but is still used in Native.
dialog_box                          = 1120  # (dialog_box, <text_string_id>, [title_string_id]),
                                            # Displays a popup window with the text message and an optional caption.
question_box                        = 1121  # (question_box, <string_id>, [<yes_string_id>], [<no_string_id>]),
                                            # Displays a popup window with the text of the question and two buttons (Yes and No by default, but can be overridden). When the player selects one of possible responses, a ti_question_answered trigger will be executed. Works inside a mission template and in the map window, presentations cannot be used at the same time.
tutorial_message                    = 1122  # (tutorial_message, <string_id>, [color], [auto_close_time]),
                                            # Displays a popup window with tutorial text stored in referenced string or string register. Use -1 to close any currently open tutorial box. Optional parameters allow you to define text color and time period after which the tutorial box will close automatically. Works also at the world map.
tutorial_message_set_position       = 1123  # (tutorial_message_set_position, <position_x>, <position_y>), 
                                            # Defines screen position for the tutorial box. Assumes screen size is 1000*750.
tutorial_message_set_size           = 1124  # (tutorial_message_set_size, <size_x>, <size_y>), 
                                            # Defines the font size of the tutorial box. Assumes screen size is 1000*750. The size of the tutorial box is always the same, depending how much text it has (one can see it with background on 1, it has always full width).
tutorial_message_set_center_justify = 1125  # (tutorial_message_set_center_justify, <value>),
                                            # Sets tutorial box to be center justified (value = 1), or use positioning dictated by tutorial_message_set_position (value = 0).
tutorial_message_set_background     = 1126  # (tutorial_message_set_background, <value>),
                                            # Defines whether the tutorial box will have a background or not (1 or 0). Default is off.

################################################################################
# [ Z19 ] GAME CONTROL: SCREENS, MENUS, DIALOGS AND ENCOUNTERS
################################################################################

  # An encounter is what happens when player's party meets another party on the
  # world map. While most operations in the game can be performed outside of
  # encounter, there's one thing you can only do when in encounter context -
  # standard game battle. When you are initiating the battle from an encounter,
  # the game engine will do most of the grunt work for you. You can order the
  # engine to add some parties to the battle on this or that side, and the
  # soldiers from those parties will spawn on the battlefield, in the numbers
  # proportional to the party sizes, and the agents will maintain links with
  # their parties. If agents earn experience, this will be reflected on the
  # world map, and if some agents die, party sizes will be decreased. All this
  # stuff can potentially be emulated by the Module System code, but it's tons
  # of work and is still much less efficient than the tool the game engine
  # already provides to you.

  # An important notice: when player encounters an AI party on the map, the game
  # calls "game_event_party_encounter" script in the module_scripts.py. So if
  # you want to implement some non-standard processing of game encounters, this
  # is the place you should start from. Also note that the game implements the
  # Camp menu as an encounter with a hardcoded party "p_camp_bandits".

  # Also you can find many operations in this section dealing with game screens,
  # game menus and game dialogs. Keep in mind that some screens only make sense
  # in certain contexts, and game menus are only available on the world map, you
  # cannot use game menus during the mission.

# Conditional operations

entering_town                         =   36  # (entering_town, <town_id>),
                                              # Apparently deprecated.
encountered_party_is_attacker         =   39  # (encountered_party_is_attacker),
                                              # Checks that the party encountered on the world map was following player (i.e. either player was trying to run away or at the very least this is a head-on clash).
conversation_screen_is_active         =   42  # (conversation_screen_is_active),
                                              # Checks that the player is currently in dialogue with some agent. Can only be used in triggers of module_mission_templates.py file.
in_meta_mission                       =   44  # (in_meta_mission),
                                              # Works only in conversations. Indicates whether dialogue is taking place in meta mission or in current scene.

# Game hardcoded windows and related operations

change_screen_return                  = 2040  # (change_screen_return),
                                              # Closes any current screen and returns the player to world map. In missions nothing happens.
change_screen_loot                    = 2041  # (change_screen_loot, <troop_id>),
                                              # Opens the Looting interface, using the provided troop as loot storage. Player has full access to troop inventory.
change_screen_trade                   = 2042  # (change_screen_trade, [troop_id]),
                                              # Opens the Trade screen, using the provided troop as the trading partner. When called from module_dialogs, troop_id is optional and defaults to current dialogue partner.
change_screen_exchange_members        = 2043  # (change_screen_exchange_members, [exchange_leader], [party_id]),
                                              # Opens the Exchange Members With Party interface, using the specified party_id. If called during an encounter, party_id is optional and defaults to the encountered party. Second parameter determines whether the party leader [0, 1] is exchangeable (useful when managing the castle garrison).
change_screen_trade_prisoners         = 2044  # (change_screen_trade_prisoners),
                                              # Opens the Sell Prisoners interface. Script "script_game_get_prisoner_price" will be used to determine prisoner price.
change_screen_buy_mercenaries         = 2045  # (change_screen_buy_mercenaries),
                                              # Opens the Buy Mercenaries interface, where player can hire troops from the party specified with (set_mercenary_source_party) operation. Only works from the dialog.
change_screen_view_character          = 2046  # (change_screen_view_character),
                                              # Opens the character screen of another troop. Can only be used in dialogs.
change_screen_training                = 2047  # (change_screen_training),
                                              # Opens the character screen for the troop that player is currently talking to. Only works in dialogs. Deprecated, use (change_screen_view_character) instead.
change_screen_mission                 = 2048  # (change_screen_mission),
                                              # Starts the mission, using previously defined scene and mission template.
change_screen_map_conversation        = 2049  # (change_screen_map_conversation, <troop_id>),
                                              # Starts the mission, same as (change_screen_mission). However once the mission starts, player will get into dialog with the specified troop, and once the dialog ends, the mission will automatically end.
change_screen_exchange_with_party     = 2050  # (change_screen_exchange_with_party, <party_id>),
                                              # Effectively duplicates (change_screen_exchange_members), but party_id parameter is obligatory and the operation doesn't have an option to prevent party leader from being exchanged.
change_screen_equip_other             = 2051  # (change_screen_equip_other, [troop_id]),
                                              # Opens the Equip Companion interface. When calling from a dialog, it is not necessary to specify troop_id.
change_screen_map                     = 2052  # (change_screen_map),
                                              # Changes the screen to global map, closing any currently running game menu, dialog or mission.
change_screen_notes                   = 2053  # (change_screen_notes, <note_type>, <object_id>),
                                              # Opens the Notes screen, in the selected category (note_type: 1=troops, 2=factions, 3=parties, 4=quests, 5=info_pages) and for the specified object in that category.
change_screen_quit                    = 2055  # (change_screen_quit),
                                              # Quits the game to the main menu. Most probably needs to be called from module_game_menus.
change_screen_give_members            = 2056  # (change_screen_give_members, [party_id]),
                                              # Opens the Give Troops to Another Party interface. Party_id parameter is optional during an encounter and will use encountered party as default value.
change_screen_controls                = 2057  # (change_screen_controls),
                                              # Opens the standard Configure Controls screen, pausing the game.
change_screen_options                 = 2058  # (change_screen_options),
                                              # Opens the standard Game Options screen, pausing the game.

set_mercenary_source_party            = 1320  # (set_mercenary_source_party, <party_id>),
                                              # Defines the party from which the player will buy mercenaries with (change_screen_buy_mercenaries).
start_map_conversation                = 1025  # (start_map_conversation,<troop_id>),
                                              # Old syntax: (start_map_conversation, <troop_id>, [troop_dna]),
                                              # Starts a conversation with the selected troop. Can be called directly from global map or game menus. Troop DNA parameter allows you to randomize non-hero troop appearances.

# Game menus

set_background_mesh                   = 2031  # (set_background_mesh, <mesh_id>),
                                              # Sets the specified mesh as the background for the current menu. Not working for presentations, not tested yet for dialogs.
set_game_menu_tableau_mesh            = 2032  # (set_game_menu_tableau_mesh, <tableau_material_id>, <value>, <position_register_no>),
                                              # Adds a tableau to the current game menu screen. Position (X,Y) coordinates define mesh position, Z coordinate defines scaling. Parameter <value> will be passed as tableau_material script parameter.
jump_to_menu                          = 2060  # (jump_to_menu, <menu_id>),
                                              # Opens the specified game menu. Note this only happens after the current block of code completes execution.
disable_menu_option                   = 2061  # (disable_menu_option),
                                              # Never used in native. Apparently deprecated as menu options have prerequisite code blocks now.

# Game encounter handling operations

set_party_battle_mode                 = 1020  # (set_party_battle_mode),
                                              # Used before or during the mission to start battle mode. Enables that any party you encouter will permanently take away player's health, can loot the defeated player and various things like that. Basically makes a party encounter like a proper battle (and apparently lets agents use appropriate AI), not just a training run where the player gains back again all his health after the battle.
finish_party_battle_mode              = 1019  # (finish_party_battle_mode),
                                              # Used during the mission to stop battle mode.

start_encounter                       = 1300  # (start_encounter, <party_id>),
                                              # Forces the player party to initiate encounter with the specified party. Distance does not matter in this situation.
leave_encounter                       = 1301  # (leave_encounter),
                                              # Leaves encounter mode.
encounter_attack                      = 1302  # (encounter_attack),
                                              # Apparently starts the standard battle with the encountered party. 4research.
select_enemy                          = 1303  # (select_enemy, <value>),
                                              # When joining a battle, this determines what side player will be helping. Defending party is always 0, and attacking party is always 1. Player can support either attackers (value = 0, i.e. defenders are the enemy) or defenders (value = 1).
set_passage_menu                      = 1304  # (set_passage_menu, <value>),
                                              # When setting up a mission, this allows you to determine what game menu will be used for that mission passages instead of "mnu_town". Passage menu item number will determine what menu option (in sequential order, starting from 0) will be executed when the player activates that passage on the scene. Note that menu option condition code block will be ignored.
start_mission_conversation            = 1920  # (start_mission_conversation, <troop_id>),
                                              # During the mission, initiates the dialog with specified troop.

set_conversation_speaker_troop        = 2197  # (set_conversation_speaker_troop, <troop_id>),
                                              # Allows to dynamically switch speaking troops during the dialog when developer doesn't know in advance who will be doing the speaking. Should be placed in post-talk code section of dialog entry.
set_conversation_speaker_agent        = 2198  # (set_conversation_speaker_agent, <agent_id>),
                                              # Allows to dynamically switch speaking agents during the dialog when developer doesn't know in advance who will be doing the speaking. Should be placed in post-talk code section of dialog entry.
store_conversation_agent              = 2199  # (store_conversation_agent, <destination>),
                                              # Stores identifier of agent who is currently speaking.
store_conversation_troop              = 2200  # (store_conversation_troop, <destination>),
                                              # Stores identifier of troop who is currently speaking.
store_partner_faction                 = 2201  # (store_partner_faction, <destination>),
                                              # Stores faction of the troop player is speaking to.
store_encountered_party               = 2202  # (store_encountered_party, <destination>),
                                              # Stores identifier of the encountered party.
store_encountered_party2              = 2203  # (store_encountered_party2, <destination>),
                                              # Stores the identifier of the second encountered party (when first party is in battle, this one will return its battle opponent).
set_encountered_party                 = 2205  # (set_encountered_party, <party_no>),
                                              # Sets the specified party as encountered by player, but does not run the entire encounter routine. Used in Native during chargen to set up the starting town and then immediately throw the player into street fight without showing him the town menu.

end_current_battle                    = 1307  # (end_current_battle),
                                              # Apparently ends the battle between player's party and its opponent. Exact effects not clear. 4research.

# Operations specific to dialogs

store_repeat_object                   =   50  # (store_repeat_object, <destination>),
                                              # Used in the dialogs code in combination with repeat_for_* dialog parameters, when creating dynamical player responses. Stores the value for the current iteration (i.e. a faction ID when repeat_for_factions is used, etc).
talk_info_show                        = 2020  # (talk_info_show, <hide_or_show>),
                                              # Used in the dialogs code to display relations bar on opponent's portrait when mouse is hovering over it (value = 1) or disable this functionality (value = 0)
talk_info_set_relation_bar            = 2021  # (talk_info_set_relation_bar, <value>),
                                              # Sets the relations value for relationship bar in the dialog. Value should be in range -100..100. Enter an invalid value to hide the bar.
talk_info_set_line                    = 2022  # (talk_info_set_line, <line_no>, <string_no>)
                                              # Sets the additional text information (usually troop name) to be displayed together with the relations bar.

################################################################################
# [ Z20 ] SCENES AND MISSIONS
################################################################################

  # To put the player into a 3D scene, you need two things. First is the scene
  # itself. All scenes are defined in module_scenes.py file. The second element
  # is no less important, and it's called mission template. Mission template
  # will determine the context of the events on the scene - who will spawn
  # where, who will be hostile or friendly to player or to each other, etc.
  # Because of all this, when player is put on the 3D scene in the game, it is
  # commonly said that player is "in a mission".

# Conditional operations

all_enemies_defeated                  = 1003                     # (all_enemies_defeated, [<time-value>]),
                                                                 # Checks if all agents from the enemy are defeated. When a time value x (in seconds) is given the operation only succeeds if the last status change (dead, alive, wounded...) happened more than (or exactly) x seconds ago.
race_completed_by_player              = 1004                     # (race_completed_by_player),
                                                                 # Not used in Native. Deprecated. Doesn't do anything, only returns true.
num_active_teams_le                   = 1005                     # (num_active_teams_le, <value>),
                                                                 # Checks if the number of active teams (i.e. teams with at least one active agent) is less than or equal to given value.
num_active_teams_gt                   = neg|num_active_teams_le  # (num_active_teams_gt, <value>),
                                                                 # Checks if the number of active teams is bigger than given value.
main_hero_fallen                      = 1006                     # (main_hero_fallen),
                                                                 # Checks if the player has been knocked out.
main_hero_alive                       = neg|main_hero_fallen     # (main_hero_alive),
                                                                 # Checks if the player is alive and not knocked out.
scene_allows_mounted_units            = 1834                     # (scene_allows_mounted_units),
                                                                 # Checks if scene entry has the flag sf_no_horses.
is_zoom_disabled                      = 2222                     # (is_zoom_disabled),
                                                                 # Version 1.153+. Checks that the zoom is currently disabled in the module.ini by setting the parameter disable_zoom = 1.

# Scene slot operations

scene_set_slot                               =  503               # (scene_set_slot, <scene_id>, <slot_no>, <value>),
scene_get_slot                               =  523               # (scene_get_slot, <destination>, <scene_id>, <slot_no>),
scene_slot_eq                                =  543               # (scene_slot_eq, <scene_id>, <slot_no>, <value>),
scene_slot_ge                                =  563               # (scene_slot_ge, <scene_id>, <slot_no>, <value>),
scene_slot_lt                                = neg|scene_slot_ge  # (scene_slot_lt, <scene_id>, <slot_no>, <value>),

# Scene visitors handling operations

add_troop_to_site                            = 1250  # (add_troop_to_site, <troop_id>, <scene_id>, <entry_no>),
                                                     # Set troop's position in the world to the specified scene and entry point. Entry point must have mtef_scene_source type. Agent will always appear at that entry when entering that scene. No longer used in Native.
remove_troop_from_site                       = 1251  # (remove_troop_from_site, <troop_id>, <scene_id>),
                                                     # Removes the troop from the specified scene. No longer used in Native.
modify_visitors_at_site                      = 1261  # (modify_visitors_at_site, <scene_id>),
                                                     # Declares the scene which visitors will be modified from that moment on.
reset_visitors                               = 1262  # (reset_visitors),
                                                     # Resets all visitors to the scene.
set_visitor                                  = 1263  # (set_visitor, <mission_template_spawn_record>, <troop_id>, [<dna>]),
                                                     # Adds the specified troop as the visitor to the specified spawn record (not the entry point) of the scene defined with (modify_visitors_at_site). Entry point must have mtef_visitor_source type. Optional DNA parameter allows for randomization of agent looks (only applies to non-hero troops).
set_visitors                                 = 1264  # (set_visitors, <mission_template_spawn_record>, <troop_id>, <number_of_troops>),
                                                     # Same as (set_visitors), but spawns an entire group of some troop type.
add_visitors_to_current_scene                = 1265  # (add_visitors_to_current_scene, <mission_template_spawn_record>, <troop_id>, <number_of_troops>, <team_no>, <group_no>),
                                                     # Adds a number of troops to the specified spawn record (not the entry point) when the scene is already loaded. Requires the entry point to have the flag mtef_visitor_source. Team and group parameters are used in multiplayer mode only, singleplayer mode uses team settings for selected entry point as defined in module_mission_templates.py.

mission_tpl_entry_set_override_flags         = 1940  # (mission_tpl_entry_set_override_flags, <mission_template_id>, <entry_no>, <value>),
                                                     # Allows modder to use a different set of equipment override flags (see af_* constants in header_mission_templates.py) for the selected entry point.
mission_tpl_entry_clear_override_items       = 1941  # (mission_tpl_entry_clear_override_items, <mission_template_id>, <entry_no>),
                                                     # Clears the list of override equipment provided by the entry point definition in module_mission_templates.py.
mission_tpl_entry_add_override_item          = 1942  # (mission_tpl_entry_add_override_item, <mission_template_id>, <entry_no>, <item_kind_id>),
                                                     # Specified item will be added to any agent spawning on specified entry point. Must be used after using the set_jump_mission to define the context, otherwise it won't work properly.
mission_tpl_are_all_agents_spawned           = 1943  # (mission_tpl_are_all_agents_spawned), 
                                                     # Agents >300 may keep spawning after ti_after_mission_start (fires .1 second too early) if there is not enough space to spawn for agents.

# Mission/scene general operations

set_mission_result                           = 1906  # (set_mission_result, <value>),
                                                     # Sets the result of the current mission (1 for victory, -1 for defeat).
finish_mission                               = 1907  # (finish_mission, <delay_in_seconds>),
                                                     # Exits the scene after the specified delay.
set_jump_mission                             = 1911  # (set_jump_mission, <mission_template_id>),
                                                     # Tells the game to use the specified mission template for the next mission. Apparently should precede the call to (jump_to_scene).
jump_to_scene                                = 1910  # Official: (jump_to_scene,<scene_id>,<entry_no>),
                                                     # (jump_to_scene, <scene_id>, [entry_no]),
                                                     # Tells the game to use the specified scene for the next mission. Usually followed by (change_screen_mission) call. Parameter entry_no does not seem to have any effect.
set_jump_entry                               = 1912  # (set_jump_entry, <entry_no>),
                                                     # Defines what entry point the player will appear at when the mission starts.

store_current_scene                          = 2211  # (store_current_scene, <destination>),
                                                     # Retrieves the identifier of the current scene. Note that the operation will return the scene id even after the mission is completed and the player is already on global map.
close_order_menu                             = 1789  # (close_order_menu),
                                                     # Version 1.161+. If orders menu is currently open, it will be closed.

entry_point_get_position                     = 1780  # (entry_point_get_position, <position>, <entry_no>),
                                                     # Retrieves the position of the entry point on the scene.
entry_point_set_position                     = 1781  # (entry_point_set_position, <entry_no>, <position>),
                                                     # Moves the entry point to the specified position on the scene.
entry_point_is_auto_generated                = 1782  # (entry_point_is_auto_generated, <entry_no>),
                                                     # Checks that the entry point is auto-generated (in other words, there was no such entry point placed in the scene file).

# Scene parameters handling

scene_set_day_time                           = 1266  # (scene_set_day_time, <value>),
                                                     # Defines the time for the scene to force the engine to select a different skybox than the one dictated by current game time. Must be called within ti_before_mission_start trigger in module_mission_templates.py. Value should be in range 0..23.
set_rain                                     = 1797  # (set_rain, <rain-type>, <strength>),
                                                     # Sets a new weather for the mission. Rain_type values: 0 = clear, 1 = rain, 2 = snow. Strength is typically used in range 0..100 but is actually unlimited. Affects number of particles and fog density.
set_fog_distance                             = 1798  # (set_fog_distance, <distance_in_meters>, [fog_color]),
                                                     # Sets the density (and optionally color) of the fog for the mission.

set_skybox                                   = 2389  # (set_skybox, <non_hdr_skybox_index>, <hdr_skybox_index>),
                                                     # Version 1.153+. Forces the scene to be rendered with specified skybox. Index of -1 will disable.
set_startup_sun_light                        = 2390  # (set_startup_sun_light, <r>, <g>, <b>),
                                                     # Version 1.153+. Defines the sunlight color for the scene.
set_startup_ambient_light                    = 2391  # (set_startup_ambient_light, <r>, <g>, <b>),
                                                     # Version 1.153+. Defines the ambient light level and colour for the scene. Expects Fixed Point values between 0 and 1.
set_startup_ground_ambient_light             = 2392  # (set_startup_ground_ambient_light, <r>, <g>, <b>),
                                                     # Version 1.153+. Defines the ambient light color for the ground.
get_startup_sun_light                        = 2394  # (get_startup_sun_light, <position_no>),
                                                     # Version 1.165+. Returns startup sunlight color in (x, y, z) coordinates of position register.
get_startup_ambient_light                    = 2395  # (get_startup_ambient_light, <position_no>),
                                                     # Version 1.165+. Returns startup ambient light color in (x, y, z) coordinates of position register.
get_startup_ground_ambient_light             = 2396  # (get_startup_ground_ambient_light, <position_no>),
                                                     # Version 1.165+. Returns startup ambient ground lighting color in (x, y, z) coordinates of position register.

get_battle_advantage                         = 1690  # (get_battle_advantage, <destination>),
                                                     # Retrieves the calculated battle advantage.
set_battle_advantage                         = 1691  # (set_battle_advantage, <value>),
                                                     # Sets a new value for battle advantage.

get_scene_boundaries                         = 1799  # (get_scene_boundaries, <position_min>, <position_max>),
                                                     # Retrieves the coordinates of the top-left and bottom-right corner of the scene to the provided position registers.

mission_enable_talk                          = 1935  # (mission_enable_talk),
                                                     # Allows dialogue with agents on the scene.
mission_disable_talk                         = 1936  # (mission_disable_talk),
                                                     # Disables dialogue with agents on the scene.

mission_get_time_speed                       = 2002  # (mission_get_time_speed, <destination_fixed_point>),
                                                     # Retrieves current time speed factor for the mission.
mission_set_time_speed                       = 2003  # (mission_set_time_speed, <value_fixed_point>),
                                                     # Instantly changes the speed of time during the mission. Speed of time cannot be set to zero or below. Operation only works when cheat mode is enabled.
mission_time_speed_move_to_value             = 2004  # (mission_time_speed_move_to_value, <value_fixed_point>, <duration-in-1/1000-seconds>),
                                                     # Changes the speed of time during the mission gradually, within the specified duration period. Speed of time cannot be set to zero or below. Operation only works when cheat mode is enabled.
mission_set_duel_mode                        = 2006  # (mission_set_duel_mode, <value>),
                                                     # Sets duel mode for the multiplayer mission. Values: 0 = off, 1 = on.

store_zoom_amount                            = 2220  # (store_zoom_amount, <destination_fixed_point>),
                                                     # Version 1.153+. Stores current zoom rate.
                                                     # Works only if native shift zoom is disabled via module.ini parameter disable_zoom = 1.
set_zoom_amount                              = 2221  # (set_zoom_amount, <value_fixed_point>),
                                                     # Version 1.153+. Sets new zoom rate.
                                                     # Works only if native shift zoom is disabled via module.ini parameter disable_zoom = 1.

# Mission timers

reset_mission_timer_a                        = 2375  # (reset_mission_timer_a),
                                                     # Resets the value of first mission timer and starts it from zero.
reset_mission_timer_b                        = 2376  # (reset_mission_timer_b),
                                                     # Resets the value of second mission timer and starts it from zero.
reset_mission_timer_c                        = 2377  # (reset_mission_timer_c),
                                                     # Resets the value of third mission timer and starts it from zero.

store_mission_timer_a                        = 2370  # (store_mission_timer_a, <destination>),
                                                     # Retrieves current value of first mission timer, in seconds.
store_mission_timer_b                        = 2371  # (store_mission_timer_b, <destination>),
                                                     # Retrieves current value of second mission timer, in seconds.
store_mission_timer_c                        = 2372  # (store_mission_timer_c, <destination>),
                                                     # Retrieves current value of third mission timer, in seconds.

store_mission_timer_a_msec                   = 2365  # (store_mission_timer_a_msec, <destination>),
                                                     # Retrieves current value of first mission timer, in milliseconds.
store_mission_timer_b_msec                   = 2366  # (store_mission_timer_b_msec, <destination>),
                                                     # Retrieves current value of second mission timer, in milliseconds.
store_mission_timer_c_msec                   = 2367  # (store_mission_timer_c_msec, <destination>),
                                                     # Retrieves current value of third mission timer, in milliseconds.

# Camera and rendering operations

is_camera_in_first_person                    = 61    # (is_camera_in_first_person),
set_camera_in_first_person                   = 62    # (set_camera_in_first_person, <value>),
                                                     # 1 = first, 0 = third person

mission_cam_set_mode                         = 2001  # (mission_cam_set_mode, <mission_cam_mode>, <duration-in-1/1000-seconds>, <value>),
                                                     # Not documented. Changes main camera mode. Camera mode is 0 for automatic and 1 for manual (controlled by code). Duration parameter is used when switching from manual to auto, to determine how long will camera move to its new position.
                                                     # if value = 0, then camera velocity will be linear, else it will be non-linear. Otherwise the third parameter is not documented.
mission_cam_set_screen_color                 = 2008  # (mission_cam_set_screen_color, <value>),
                                                     # Not documented. Paints the screen with solid color. Parameter <value> contains color code with alpha component. Can be used to block screen entirely, add tint etc.
mission_cam_animate_to_screen_color          = 2009  #(mission_cam_animate_to_screen_color, <value>, <duration-in-1/1000-seconds>),
                                                     # Not documented. Same as above, but color change is gradual. Used in Native to fill the screen with white before the end of marriage scene.

mission_cam_get_position                     = 2010  # (mission_cam_get_position, <position_register_no>),
                                                     # Retrieves the current position of camera during the mission (i.e. the point from which the player is observing the game).
mission_cam_set_position                     = 2011  # (mission_cam_set_position, <position_register_no>),
                                                     # Moves the camera to the specified position during the mission.
mission_cam_animate_to_position              = 2012  # (mission_cam_animate_to_position, <position_register_no>, <duration-in-1/1000-seconds>, <value>),
                                                     # Moves the camera to the specified position smoothly. Second parameter determines how long it will take camera to move to destination, third parameter determines whether camera velocity will be linear (value = 0) or non-linear (value = 1).
mission_cam_get_aperture                     = 2013  # (mission_cam_get_aperture, <destination>),
                                                     # If player is holding shift for zooming aperture = 37, normal aperture = 75. When player dies with shift holding mission cam aperture don't return to normal.
mission_cam_set_aperture                     = 2014  # (mission_cam_set_aperture, <value>),
                                                     # Set aperture for cam.
mission_cam_animate_to_aperture              = 2015  # (mission_cam_animate_to_aperture, <value>, <duration-in-1/1000-seconds>, <value>),
                                                     # Not documented. if value = 0, then camera velocity will be linear. else it will be non-linear
mission_cam_animate_to_position_and_aperture = 2016  # (mission_cam_animate_to_position_and_aperture, <position_register_no>, <value>, <duration-in-1/1000-seconds>, <value>),
                                                     # Not documented. if value = 0, then camera velocity will be linear. else it will be non-linear
mission_cam_set_target_agent                 = 2017  # (mission_cam_set_target_agent, <agent_id>, <value>),
                                                     # Not documented. if value = 0 then do not use agent's rotation, else use agent's rotation
mission_cam_clear_target_agent               = 2018  # (mission_cam_clear_target_agent),
                                                     # Not documented.
mission_cam_set_animation                    = 2019  # (mission_cam_set_animation, <anim_id>),
                                                     # Plays any bone animation from animations.py, taking the coordinates from the first bone in the hierarchy. The name and number of bones does not matter.

mouse_get_world_projection                   =  751  # (mouse_get_world_projection, <position_no_1>, <position_no_2>),
                                                     # Version 1.161+. Returns current camera coordinates (first position) and mouse projection to the back of the world (second position). Rotation data of resulting positions seems unreliable.
cast_ray                                     = 1900  # (cast_ray, <destination>, <hit_position_register>, <ray_position_register>, [<ray_length_fixed_point>]),
                                                     # Version 1.161+. Casts a ray starting from <ray_position_register> and stores the closest hit position into <hit_position_register> (fails if no hits). Rotations of hit position will be normal to the surface, i.e. perpendicular. If the body hit is a scene prop, its instance id will be stored into <destination>, otherwise it will be -1. Optional <ray_length> parameter seems to have no effect.
                                                     # Y-axis points to obstacle.

set_postfx                                   = 2386  # (set_postfx, <postfx_params-ID>)
                                                     # Sets the respective postfx effect for the current scene. Count through your post_fx-settings beginning from 0 to get the ID for the effect or put the line 'ID_postfx_params import *' at the top to use directly the ID-name. Not used in Native. Can get called with all mission triggers, even when already in the scene. However, in latter case a delay can be noticed when the postfx switches. Appearantly a manually set postfx disappears if HDR gets toggled on/off in the graphic options.
set_river_shader_to_mud                      = 2387  # (set_river_shader_to_mud, ???)
                                                     # Changes river material for muddy env. This operation is not documented nor any examples of its use could be found. Parameters are unknown.
                                                     # [?] Makes the engine to change the water shading effect _in the current scene_ to one drastically darker.
rebuild_shadow_map                           = 2393  # (rebuild_shadow_map),
                                                     # Version 1.153+. Rebuilds shadow map for the current scene to match props' new positions. When you move the prop and don't use this operation, its shadow will still fall on its old position.

set_shader_param_int                         = 2400  # (set_shader_param_int, <parameter_name>, <value>), #Sets the int shader parameter <parameter_name> to <value>
                                                     # Version 1.153+. UNTESTED. Allows direct manupulation of shader parameters. Operation scope is unknown, possibly global. Parameter is an int value.
set_shader_param_float                       = 2401  # (set_shader_param_float, <parameter_name>, <value_fixed_point>), #Sets the float shader parameter <parameter_name> to <value>
                                                     # Version 1.153+. Allows direct manupulation of shader parameters. Operation scope is unknown, possibly global. Parameter is a float value.
set_shader_param_float4                      = 2402  # (set_shader_param_float4, <parameter_name>, <valuex>, <valuey>, <valuez>, <valuew>),
                                                     # Version 1.153+. Allows direct manupulation of shader parameters. Operation scope is unknown, possibly global. Parameter is a set of 4 float values.
set_shader_param_float4x4                    = 2403  # (set_shader_param_float4x4, <parameter_name>, [0][0], [0][1], [0][2], [1][0], [1][1], [1][2], [2][0], [2][1], [2][2], [3][0], [3][1], [3][2]), Sets the float4x4 shader parameter <parameter_name> to the given values .w components are 0001 by default
                                                     # Version 1.153+. Allows direct manupulation of shader parameters. Operation scope is unknown, possibly global. Parameter is a set of 4x4 float values.

################################################################################
# [ Z21 ] SCENE PROPS, SCENE ITEMS, LIGHT SOURCES AND PARTICLE SYSTEMS
################################################################################

  # On each scene in the game you can find scene props and scene items.

  # Scene props are the building bricks of the scene. Nearly every 3D object you
  # will see on any scene in the game is a scene prop, with the exception of
  # terrain and flora (on some scenes flora elements are actually scene props
  # as well though).

  # Just like with troops and agents, it is important to differentiate between
  # scene props and scene prop instances. You can have a dozen archer agents on
  # the scene, and each of them will be an instance of the archer troop. Scene
  # props are the same - there can be many castle wall sections on the scene,
  # and these are instances of the same castle wall scene prop.

  # It is also possible to use game items as elements of the scene. These are
  # the scene items, and they behave just like normal scene props. However all
  # operations will affect either scene prop instances, or scene items, but
  # not both.

  # Finally, there are spawned items. These are the "dropped" items which the
  # player can pick up during the mission.

# Conditional operations

prop_instance_is_valid                      = 1838  # (prop_instance_is_valid, <scene_prop_instance_id>),
                                                    # Checks that the reference to a scene prop instance is valid (i.e. it was not removed).
prop_instance_is_animating                  = 1862  # (prop_instance_is_animating, <destination>, <scene_prop_id>),
                                                    # Checks that the scene prop instance is currently animating.
prop_instance_intersects_with_prop_instance = 1880  # (prop_instance_intersects_with_prop_instance, <checked_scene_prop_id>, <scene_prop_id>),
                                                    # Checks if two scene props are intersecting (i.e. collided). Useful when animating scene props movement. Pass -1 for second parameter to check the prop against all other props on the scene. Scene props must have active collision meshes.
                                                    # Official: cannot check polygon-to-polygon physics models, but can check any other combinations between sphere, capsule and polygon physics models.
scene_prop_has_agent_on_it                  = 1801  # (scene_prop_has_agent_on_it, <scene_prop_instance_id>, <agent_id>),
                                                    # Checks that the specified agent is above the scene prop instance. scene_prop_has_agent_over_it would be a more appropriate name for the operation.

# Scene prop instance slot operations

scene_prop_set_slot                         =  510  # (scene_prop_set_slot, <scene_prop_instance_id>, <slot_no>, <value>),
scene_prop_get_slot                         =  530  # (scene_prop_get_slot, <destination>, <scene_prop_instance_id>, <slot_no>),
scene_prop_slot_eq                          =  550  # (scene_prop_slot_eq, <scene_prop_instance_id>, <slot_no>, <value>),
scene_prop_slot_ge                          =  570  # (scene_prop_slot_ge, <scene_prop_instance_id>, <slot_no>, <value>),

# Scene prop general operations

prop_instance_get_scene_prop_kind           = 1853  # (prop_instance_get_scene_prop_kind, <destination>, <scene_prop_id>),
                                                    # Retrieves the scene prop for the specified prop instance.
scene_prop_get_num_instances                = 1810  # (scene_prop_get_num_instances, <destination>, <scene_prop_id>),
                                                    # Retrieves the total number of instances of a specified scene prop on the current scene.
scene_prop_get_instance                     = 1811  # (scene_prop_get_instance, <destination>, <scene_prop_id>, <instance_no>),
                                                    # Retrieves the reference to a scene prop instance by its number.

scene_prop_enable_after_time                = 1800  # (scene_prop_enable_after_time, <scene_prop_id>, <time_period>),
                                                    # Prevents usable scene prop from being used for the specified time period in 1/100th of second. Commonly used to implement "cooldown" periods.

set_spawn_position                          = 1970  # (set_spawn_position, <position>),
                                                    # Defines the position which will later be used by (spawn_scene_prop), (spawn_scene_item), (spawn_agent) and (spawn_horse) operations.
spawn_scene_prop                            = 1974  # (spawn_scene_prop, <scene_prop_id>),
                                                    # Spawns a new scene prop instance of the specified type at the position defined by the last call to (set_spawn_position). Operation stores the prop_instance_id of the spawned position in reg0. Be aware: it is not possible to unspawn a scene prop while a mission is running.

prop_instance_get_variation_id              = 1840  # (prop_instance_get_variation_id, <destination>, <scene_prop_id>),
                                                    # Retrieves the first variation ID number for the specified scene prop instance.
prop_instance_get_variation_id_2            = 1841  # (prop_instance_get_variation_id_2, <destination>, <scene_prop_id>),
                                                    # Retrieves the second variation ID number for the specified scene prop instance.

replace_prop_instance                       = 1889  # (replace_prop_instance, <scene_prop_id>, <new_scene_prop_id>),
                                                    # Replaces a single scene prop instance with an instance of another scene prop (usually with the same dimensions, but not necessarily so). Can only be called in ti_before_mission_start trigger in module_mission_templates.py.
replace_scene_props                         = 1890  # (replace_scene_props, <old_scene_prop_id>, <new_scene_prop_id>),
                                                    # Replaces all instances of specified scene prop type with another scene prop type. Commonly used to replace damaged walls with their intact versions during normal visits to castle scenes. Can only be called in ti_before_mission_start trigger in module_mission_templates.py.
scene_prop_fade_out                         = 1822  # (scene_prop_fade_out, <prop_instance_id>, <fade_out_time>, [meta_mesh]),
                                                    # Version 1.153+. Makes the scene prop instance disappear within specified time. Leaving meta_mesh blank will have the operation only affect the main mesh, setting it to -1 will affect all submeshes.
scene_prop_fade_in                          = 1823  # (scene_prop_fade_in, <scene_prop_id>, <fade_in_time>),
                                                    # Version 1.153+. Makes the scene prop instance reappear within specified time.

prop_instance_set_material                  = 2617  # (prop_instance_set_material, <prop_instance_no>, <sub_mesh_no>, <string_register>),
                                                    # Version 1.161+. 4research. give sub mesh as -1 to change all meshes' materials.

# Scene prop manipulation

scene_prop_get_visibility                   = 1812  # (scene_prop_get_visibility, <destination>, <scene_prop_id>),
                                                    # Retrieves the current visibility state of the scene prop instance (1 = visible, 0 = invisible).
scene_prop_set_visibility                   = 1813  # (scene_prop_set_visibility, <scene_prop_id>, <value>),
                                                    # Shows (value = 1) or hides (value = 0) the scene prop instance. The collision mesh remains, so you need to always run a seperate operation (prop_instance_enable_physics) to turn on and off to match the collision mesh. Use (rebuild_shadow_map), afterwards to remove prop shadows (Will stutter for a frame)
scene_prop_get_hit_points                   = 1815  # (scene_prop_get_hit_points, <destination>, <scene_prop_id>),
                                                    # Retrieves current number of hit points that the scene prop instance has.
scene_prop_get_max_hit_points               = 1816  # (scene_prop_get_max_hit_points, <destination>, <scene_prop_id>),
                                                    # Retrieves the maximum number of hit points that the scene prop instance has (useful to calculate the percent of damage).
scene_prop_set_hit_points                   = 1814  # (scene_prop_set_hit_points, <scene_prop_id>, <value>),
                                                    # Sets the number of hit points that the scene prop has. Both current and max hit points are affected. Only makes sense for sokf_destructible scene props.
scene_prop_set_cur_hit_points               = 1820  # (scene_prop_set_cur_hit_points, <scene_prop_id>, <value>),
                                                    # Version 1.153+. Sets current HP amount for scene prop.
prop_instance_receive_damage                = 1877  # (prop_instance_receive_damage, <scene_prop_id>, <agent_id>, <damage_value>),
                                                    # Makes scene prop instance receive specified amount of damage from any arbitrary agent. Agent reference is apparently necessary to properly initialize ti_on_scene_prop_hit trigger parameters.
prop_instance_refill_hit_points             = 1870  # (prop_instance_refill_hit_points, <scene_prop_id>),
                                                    # Restores hit points of a scene prop instance to their maximum value.
scene_prop_get_team                         = 1817  # (scene_prop_get_team, <value>, <scene_prop_id>),
                                                    # Retrieves the team controlling the scene prop instance.
scene_prop_set_team                         = 1818  # (scene_prop_set_team, <scene_prop_id>, <value>),
                                                    # Assigns the scene prop instance to a certain team.
scene_prop_set_prune_time                   = 1819  # (scene_prop_set_prune_time, <scene_prop_id>, <value>),
                                                    # Not documented. Not used in Native. Taleworlds comment: Prune time can only be set to objects that are already on the prune queue. Static objects are not affected by this operation.

prop_instance_get_position                  = 1850  # (prop_instance_get_position, <position>, <scene_prop_id>),
                                                    # Retrieves the prop instance current position on the scene.
prop_instance_get_starting_position         = 1851  # (prop_instance_get_starting_position, <position>, <scene_prop_id>),
                                                    # Retrieves the prop instance starting position on the scene (i.e. the place where it was positioned when initialized).
prop_instance_set_position                  = 1855  # (prop_instance_set_position, <scene_prop_id>, <position>, [dont_send_to_clients]),
                                                    # Teleports prop instance to another position. Optional flag dont_send_to_clients can be used on the server to prevent position change from being replicated to client machines (useful when doing some calculations which require to move the prop temporarily to another place). Gets synchronized by game engine automatically if called on server. Each time you call this operation the game sends a network event to all clients. Too many calls will fresh or mess up the client completely, so the only solution is not calling them 20 times per frame.
prop_instance_animate_to_position           = 1860  # (prop_instance_animate_to_position, <scene_prop_id>, position, <duration-in-1/100-seconds>),
                                                    # Moves prop instance to another position during the specified time frame (i.e. animates). Time is specified in 1/100th of second.
prop_instance_get_animation_target_position = 1863  # (prop_instance_get_animation_target_position, <pos>, <scene_prop_id>),
                                                    # Retrieves the position that the prop instance is currently animating to.
prop_instance_stop_animating                = 1861  # (prop_instance_stop_animating, <scene_prop_id>),
                                                    # Stops animating of the prop instance in the current position.
prop_instance_get_scale                     = 1852  # (prop_instance_get_scale, <position>, <scene_prop_id>),
                                                    # Retrieves the current scaling factors of the prop instance.
prop_instance_set_scale                     = 1854  # (prop_instance_set_scale, <scene_prop_id>, <value_x_fixed_point>, <value_y_fixed_point>, <value_z_fixed_point>),
                                                    # Sets new scaling factors for the scene prop.
prop_instance_enable_physics                = 1864  # (prop_instance_enable_physics, <scene_prop_id>, <value>),
                                                    # Enables (value = 1) or disables (value = 0) physics calculation (gravity, collision checks and objects) for the scene prop instance.
prop_instance_initialize_rotation_angles    = 1866  # (prop_instance_initialize_rotation_angles, <scene_prop_id>),
                                                    # Should be called to initialize the scene prop instance prior to any calls to (prop_instance_rotate_to_position).
prop_instance_rotate_to_position            = 1865  # (prop_instance_rotate_to_position, <scene_prop_id>, <position>, <duration-in-1/100-seconds>, <total_rotate_angle_fixed_point>),
                                                    # Specified prop instance will move to the target position within the specified duration of time, and within the same time it will rotate for the specified angle. Used in Native code to simulate behavior of belfry wheels and rotating winches.
prop_instance_clear_attached_missiles       = 1885  # (prop_instance_clear_attached_missiles, <scene_prop_id>),
                                                    # Version 1.153+. Removes all missiles currently attached to the scene prop. Only works with dynamic scene props (non-retrievable missiles).

prop_instance_dynamics_set_properties       = 1871  # (prop_instance_dynamics_set_properties, <scene_prop_id>, <position>),
                                                    # Initializes physical parameters of a scene prop. Position (X,Y) coordinates are used to store object's mass and friction coefficient. Coordinate Z is reserved (set it to zero just in case). Scene prop must be defined as sokf_moveable|sokf_dynamic_physics, and a call to (prop_instance_enable_physics) must be previously made.
                                                    # Official: (prop_instance_dynamics_set_properties,<scene_prop_id>,mass_friction),
prop_instance_dynamics_set_velocity         = 1872  # (prop_instance_dynamics_set_velocity, <scene_prop_id>, <position>),
                                                    # Sets current movement speed for a scene prop. Position's coordinates define velocity along corresponding axis. Same comments as for (prop_instance_dynamics_set_properties).
                                                    # Official: (prop_instance_dynamics_set_velocity,<scene_prop_id>,linear_velocity),
prop_instance_dynamics_set_omega            = 1873  # (prop_instance_dynamics_set_omega, <scene_prop_id>, <position>),
                                                    # Sets current rotation speed for a scene prop. Position's coordinates define rotational speed around corresponding axis. Same comments as for (prop_instance_dynamics_set_properties).
                                                    # Official: (prop_instance_dynamics_set_omega,<scene_prop_id>,angular_velocity),
prop_instance_dynamics_apply_impulse        = 1874  # (prop_instance_dynamics_apply_impulse, <scene_prop_id>, <position>),
                                                    # Applies an impulse of specified scale to the scene prop. Position's coordinates define instant change in movement speed along corresponding axis. Same comments as for (prop_instance_dynamics_set_properties).
                                                    # Official: (prop_instance_dynamics_apply_impulse,<scene_prop_id>,impulse_force),

prop_instance_deform_to_time                = 2610  # (prop_instance_deform_to_time, <prop_instance_no>, <value>),
                                                    # Version 1.161+. Deforms a vertex-animated scene prop to specified vertex time. If you open the mesh in OpenBrf, right one of "Time of frame" boxes contains the relevant value.
prop_instance_deform_in_range               = 2611  # (prop_instance_deform_in_range, <prop_instance_no>, <start_frame>, <end_frame>, <duration-in-1/1000-seconds>),
                                                    # Version 1.161+. Animate vertex-animated scene prop from start frame to end frame within the specified time period (in milliseconds). If you open the mesh in OpenBrf, right one of "Time of frame" boxes contains the relevant values for frame parameters.
prop_instance_deform_in_cycle_loop          = 2612  # (prop_instance_deform_in_cycle_loop, <prop_instance_no>, <start_frame>, <end_frame>, <duration-in-1/1000-seconds>),
                                                    # Version 1.161+. Performs looping animation of vertex-animated scene prop within the specified vertex frame ranges and within specified time (in milliseconds). If you open the mesh in OpenBrf, right one of "Time of frame" boxes contains the relevant values for frame parameters.
prop_instance_get_current_deform_progress   = 2615  # (prop_instance_get_current_deform_progress, <destination>, <prop_instance_no>),
                                                    # Version 1.161+. Returns a percentage value between 0 and 100 if animation is still in progress. Returns 100 otherwise.
prop_instance_get_current_deform_frame      = 2616  # (prop_instance_get_current_deform_frame, <destination>, <prop_instance_no>),
                                                    # Version 1.161+. Returns current frame of a vertex-animated scene prop, rounded to nearest integer value.

prop_instance_play_sound                    = 1881  # (prop_instance_play_sound, <scene_prop_id>, <sound_id>, [flags]),
                                                    # Version 1.153+. Makes the scene prop play a specified sound. See sf_* flags in header_sounds.py for reference on possible options.
prop_instance_stop_sound                    = 1882  # (prop_instance_stop_sound, <scene_prop_id>),
                                                    # Version 1.153+. Stops any sound currently played by the scene prop instance.

# Scene items operations

scene_item_get_num_instances                = 1830  # (scene_item_get_num_instances, <destination>, <item_id>),
                                                    # Gets the number of specified scene items present on the scene. Scene items behave exactly like scene props (i.e. cannot be picked).
scene_item_get_instance                     = 1831  # (scene_item_get_instance, <destination>, <item_id>, <instance_no>),
                                                    # Retrieves the reference to a single instance of a scene item by its sequential number.
scene_spawned_item_get_num_instances        = 1832  # (scene_spawned_item_get_num_instances, <destination>, <item_id>),
                                                    # Retrieves the number of specified spawned items present on the scene. Spawned items are actual items, i.e. they can be picked by player.
scene_spawned_item_get_instance             = 1833  # (scene_spawned_item_get_instance, <destination>, <item_id>, <instance_no>),
                                                    # Retrieves the reference to a single instance of a spawned item by its sequential number.

replace_scene_items_with_scene_props        = 1891  # (replace_scene_items_with_scene_props, <old_item_id>, <new_scene_prop_id>),
                                                    # Replaces all instances of specified scene item with scene props. Can only be called in ti_before_mission_start trigger in module_mission_templates.py.

set_spawn_position                          = 1970  # (set_spawn_position, <position>), ## DUPLICATE ENTRY
                                                    # Defines the position which will later be used by (spawn_scene_prop), (spawn_scene_item), (spawn_agent) and (spawn_horse) operations.
spawn_item                                  = 1971  # (spawn_item, <item_kind_id>, <item_modifier>, [seconds_before_pruning]),
                                                    # Spawns a new item, possibly with modifier, on the scene in the position specified by previous call to (set_spawn_position). Optional parameter determines time period (in second) after which the item will disappear. Using 0 will prevent the item from disappearing.
spawn_item_without_refill                   = 1976  # (spawn_item_without_refill, <item_kind_id>, <item_modifier>, [seconds_before_pruning]),
                                                    # Version 1.153+. UNTESTED. It is unclear how this is different from standard (spawn_item).

# Light sources and particle systems

set_current_color                           = 1950  # (set_current_color, <red_value>, <green_value>, <blue_value>),
                                                    # Sets color for subsequent calls to (add_point_light) etc. Color component ranges are 0..255.
set_position_delta                          = 1955  # (set_position_delta, <value>, <value>, <value>),
                                                    # Can only be called inside item or scene prop triggers. Sets (X,Y,Z) offsets from the item/prop current position for subsequent calls to (add_point_light) etc. Offsets are apparently in centimeters.
add_point_light                             = 1960  # (add_point_light, [flicker_magnitude], [flicker_interval]),
                                                    # Adds a point light source to an object with optional flickering magnitude (range 0..100) and flickering interval (in 1/100th of second). Uses position offset and color provided to previous calls to (set_position_delta) and (set_current_color). Can only be used in item triggers.
add_point_light_to_entity                   = 1961  # (add_point_light_to_entity, [flicker_magnitude], [flicker_interval]),
                                                    # Adds a point light source to an object with optional flickering magnitude (range 0..100) and flickering interval (in 1/100th of second). Uses position offset and color provided to previous calls to (set_position_delta) and (set_current_color). Can only be used in scene prop triggers.
                                                    # [?] Attaches an emissive into any [Item] or [Scene Prop] when putting this into their functions. Doesn't work on the Original Game.
particle_system_add_new                     = 1965  # (particle_system_add_new, <par_sys_id>,[position]),
                                                    # Adds a new particle system to an object. Uses position offset and color provided to previous calls to (set_position_delta) and (set_current_color). Can only be used in item/prop triggers.
particle_system_emit                        = 1968  # (particle_system_emit, <par_sys_id>, <value_num_particles>, <value_period>),
                                                    # Adds a particle system in some fancy way. Uses position offset and color provided to previous calls to (set_position_delta) and (set_current_color). Can only be used in item/prop triggers.
particle_system_burst                       = 1969  # (particle_system_burst, <par_sys_id>, <position>, [percentage_burst_strength]),
                                                    # Bursts a particle system in specified position.
particle_system_burst_no_sync               = 1975  # (particle_system_burst_without_sync,<par_sys_id>,<position_no>,[percentage_burst_strength]),
                                                    # Version 1.153+. Same as above, but apparently does not synchronize this between server and client.
prop_instance_add_particle_system           = 1886  # (prop_instance_add_particle_system, <scene_prop_id>, <par_sys_id>, <position_no>),
                                                    # Version 1.153+. Adds a new particle system to the scene prop. Note that <position_no> is local, i.e. in relation to scene prop's coordinates and rotation.
prop_instance_stop_all_particle_systems     = 1887  # (prop_instance_stop_all_particle_systems, <scene_prop_id>),
                                                    # Version 1.153+. Removes all particle systems currently associated with scene prop instance.

################################################################################
# [ Z22 ] AGENTS AND TEAMS
################################################################################

  # An agent represents of a single soldier on the 3D scene. Always keep this in
  # mind when dealing with regular troops. A party may have 30 Swadian Knights.
  # They will form a single troop stack in the party, and they will all be
  # copies of the one and only Swadian Knight troop. However when the battle
  # starts, this stack will spawn 30 distinct Agents.

  # Agents do not persist - they only exist in the game for the duration of the
  # mission. As soon as the player returns to the world map, all agents who were
  # present on the scene immediately disappear. If this was a battle during a
  # normal game encounter, then the game will keep track of the battle results,
  # and depending on the number of agents killed from all sides the engine will
  # kill or wound some troops in the troop stacks of the parties who were
  # participating in the battle.

  # During the mission, all agents are split into teams. By default player and
  # his companions are placed into Team 0, but this may be changed in the
  # mission template or by code. Player's enemies are usually team 1 (though
  # again, this is not set in stone). Module System provides the modder with
  # a great degree of control over teams composition, relation to each other
  # (you can make hostile, allied or neutral teams, and you can have more than
  # one team on the scene).

# Conditional operations

agent_is_in_special_mode                 = 1693                   # (agent_is_in_special_mode, <agent_id>),
                                                                  # Checks if the agent is currently in scripted mode. It's set after executing agent_set_scripted_destination or agent_set_scripted_destination_no_attack and is cleared with agent_clear_scripted_mode.
agent_is_routed                          = 1699                   # (agent_is_routed, <agent_id>),
                                                                  # Checks if the agent has fled from the map (i.e. reached the edge of the map in fleeing mode and then faded).
agent_is_alive                           = 1702                   # (agent_is_alive, <agent_id>),
                                                                  # Checks if the agent is alive. Only succeeds if agent is not down.
agent_is_wounded                         = 1703                   # (agent_is_wounded, <agent_id>),
                                                                  # Checks if the agent has been knocked unconscious. Fails for dead agents.
agent_is_down                            = neg|agent_is_alive     # (agent_is_down, <agent_id>),
                                                                  # Checks if the agent is dead or unconscious.
agent_is_human                           = 1704                   # (agent_is_human, <agent_id>),
                                                                  # Checks if the agent is human (i.e. not horse).
agent_is_horse                           = neg|agent_is_human     # (agent_is_horse, <agent_id>),
                                                                  # Checks if the agent is a horse.
agent_is_ally                            = 1706                   # (agent_is_ally, <agent_id>),
                                                                  # Checks if the agent is allied to the player (belongs to player's party or allied party in current encounter).
agent_is_enemy                           = neg|agent_is_ally      # (agent_is_enemy, <agent_id>),
                                                                  # Checks if the agent is hostile to the player.
agent_is_non_player                      = 1707                   # (agent_is_non_player, <agent_id>),
                                                                  # Checks if the agent is not a player. Working in MP?
agent_is_defender                        = 1708                   # (agent_is_defender, <agent_id>),
                                                                  # Checks if the agent belongs to the defending side (see encounter operations for details).
agent_is_attacker                        = neg|agent_is_defender  # (agent_is_attacker, <agent_id>),
                                                                  # Checks if the agent belongs to the attacking side.
agent_is_active                          = 1712                   # (agent_is_active, <agent_id>),
                                                                  # Checks if the agent reference is active. This will succeed for dead or routed agents, for as long as the agent reference itself is valid. Engine will delete agent reference aproximatly 30 sec after his death.
agent_has_item_equipped                  = 1729                   # (agent_has_item_equipped, <agent_id>, <item_id>),
                                                                  # Checks if the agent has a specific item equipped.
agent_is_in_parried_animation            = 1769                   # (agent_is_in_parried_animation, <agent_id>),
                                                                  # Checks if the agent is currently in parrying animation (defending from some attack).
agent_is_alarmed                         = 1806                   # (agent_is_alarmed, <agent_id>),
                                                                  # Checks if the agent is alarmed (in combat mode with weapon drawn).
class_is_listening_order                 = 1775                   # (class_is_listening_order, <team_no>, <sub_class>),
                                                                  # Checks if the specified group of specified team is listening to player's orders.
teams_are_enemies                        = 1788                   # (teams_are_enemies, <team_no>, <team_no_2>),
                                                                  # Checks if the two teams are hostile to each other.
agent_is_in_line_of_sight                = 1826                   # (agent_is_in_line_of_sight, <agent_id>, <position_no>),
                                                                  # Version 1.153+. Checks if the agent can be seen from specified position. Rotation of position register is not used (i.e. agent will be seen even if position is "looking" the other way).

# Team and agent slot operations
# Team and agent slots reset every mission.

team_set_slot                            =  509               # (team_set_slot, <team_id>, <slot_no>, <value>),
team_get_slot                            =  529               # (team_get_slot, <destination>, <player_id>, <slot_no>),
team_slot_eq                             =  549               # (team_slot_eq, <team_id>, <slot_no>, <value>),
team_slot_ge                             =  569               # (team_slot_ge, <team_id>, <slot_no>, <value>),
team_slot_lt                             = neg|team_slot_ge   # (team_slot_lt, <team_id>, <slot_no>, <value>),

agent_set_slot                           =  505               # (agent_set_slot, <agent_id>, <slot_no>, <value>),
agent_get_slot                           =  525               # (agent_get_slot, <destination>, <agent_id>, <slot_no>),
agent_slot_eq                            =  545               # (agent_slot_eq, <agent_id>, <slot_no>, <value>),
agent_slot_ge                            =  565               # (agent_slot_ge, <agent_id>, <slot_no>, <value>),
agent_slot_lt                            = neg|agent_slot_ge  # (agent_slot_lt, <agent_id>, <slot_no>, <value>),

# Agent spawning, removal and general operations

add_reinforcements_to_entry              = 1930  # (add_reinforcements_to_entry, <mission_template_spawn_record>, <wave_size>),
                                                 # For battle missions, adds reinforcement wave to the specified spawn record (not the entry point). Additional parameter determines relative wave size. Agents in reinforcement wave are taken from all parties of the side that the entry point belongs to due to mtef_team_* flags.
set_spawn_position                       = 1970  # (set_spawn_position, <position>), ## DUPLICATE ENTRY
                                                 # Defines the position which will later be used by (spawn_scene_prop), (spawn_scene_item), (spawn_agent) and (spawn_horse) operations.
spawn_agent                              = 1972  # (spawn_agent, <troop_id>),
                                                 # Spawns a new troop in the specified position and saves the reference to the new agent in reg0.
spawn_horse                              = 1973  # (spawn_horse, <item_kind_id>, <item_modifier>),
                                                 # Spawns a new horse (with any modifier) in the specified position and saves the reference to the new agent in reg0.
remove_agent                             = 1755  # (remove_agent, <agent_id>),
                                                 # Instantly kills or wounds an agent (will emit dying sound). Dead agents can't be removed of the game, they have to be alive.
agent_fade_out                           = 1749  # (agent_fade_out, <agent_id>),
                                                 # Fades out the agent from the scene (same effect as fleeing enemies when they get to the edge of map). They will be counted as alive for battle missions. Dead agents can't be faded out of the game, they have to be alive.
agent_play_sound                         = 1750  # (agent_play_sound, <agent_id>, <sound_id>),
                                                 # Makes the agent emit the specified sound. Gets synchronized by game engine automatically if called on server. Works appearantly the same way as with particle effects, it's getting cut off at a specific distance, up4research.
agent_stop_sound                         = 1808  # (agent_stop_sound, <agent_id>),
                                                 # Stops whatever sound agent is currently performing. Only the reference to the last used sound channel is stored, it is impossible to know which ones were used before for a certain agent.
agent_set_visibility                     = 2096  # (agent_set_visibility, <agent_id>, <value>),
                                                 # Version 1.153+. Sets agent visibility. 0 for invisible, 1 for visible.

get_player_agent_no                      = 1700  # (get_player_agent_no, <destination>),
                                                 # Retrieves the reference to the player-controlled agent. Singleplayer mode only.
agent_get_kill_count                     = 1723  # (agent_get_kill_count, <destination>, <agent_id>, [get_wounded]),
                                                 # Retrieves the total number of kills by the specified agent during this battle. Call with non-zero <get_wounded> parameter to retrieve the total number of enemies the agent has knocked down.

agent_get_position                       = 1710  # (agent_get_position, <position>, <agent_id>),
                                                 # Retrieves the position of the specified agent on the scene.
                                                 # X, Y, Z - fixed point values, rotation - integer values in degrees from 0 to 359.
                                                 # Position is at ground level even when agent is jumping.
                                                 # Sets X-rotation = 0, Y-rotation = 0. Y-rotation can change from 340 to 20 (aproximately) when turning mounted.
                                                 # Horse and rider have the same position and speed-position.
agent_set_position                       = 1711  # (agent_set_position, <agent_id>, <position>),
                                                 # Teleports the agent to specified position on the scene, sets to ground level automatically if dynamics are not turned off before setting agent position (agent_set_no_dynamics). Be careful with riders - you must teleport the horse, not the rider for the operation to work correctly! Does not properly set the rotation of players in MP Warband as their mouse-look direction overrides it. Gets synchronized by game engine automatically if called on server. Each time you call this operation the game sends a network event to all clients. Too many calls will fresh or mess up the client completely, so the only solution is not calling them 20 times per frame.
agent_get_horse                          = 1714  # (agent_get_horse, <destination>, <agent_id>),
                                                 # Retrieves the reference to the horse agent that the specified agent is riding, or -1 if he's not riding a horse (or is a horse himself).
agent_get_rider                          = 1715  # (agent_get_rider, <destination>, <horse_agent_id>),
                                                 # Retrieves the reference to the rider agent who is riding the specified horse, or -1 if there's no rider or the specified agent is not a horse.
agent_get_party_id                       = 1716  # (agent_get_party_id, <destination>, <agent_id>),
                                                 # Retrieves the party that the specified agent belongs to (supposedly should only work in battle missions for agents spawned as starting/reinforcement waves).
agent_get_entry_no                       = 1717  # (agent_get_entry_no, <destination>, <agent_id>),
                                                 # Retrieves the entry point number where this agent has spawned. What does this return for agents spawned with (spawn_agent)? 4research.
agent_get_troop_id                       = 1718  # (agent_get_troop_id, <destination>, <agent_id>),
                                                 # Retrieves the troop type of the specified agent. Returns -1 for horses (because horses are items, not troops).
agent_get_item_id                        = 1719  # (agent_get_item_id, <destination>, <horse_agent_id>),
                                                 # Retrieves the item type of the specified horse agent. Returns -1 for humans.

# Agent combat parameters and stats

store_agent_hit_points                   = 1720  # (store_agent_hit_points, <destination>, <agent_id>, [absolute]),
                                                 # Retrieves current agent health. Optional last parameter determines whether actual health (absolute = 1) or relative percentile health (absolute = 0) is returned. Default is relative.
agent_set_hit_points                     = 1721  # (agent_set_hit_points, <agent_id>, <value>,[absolute]),
                                                 # Sets new value for agent health. Optional last parameter determines whether the value is interpreted as actual health (absolute = 1) or relative percentile health (absolute = 0). Default is relative. Gets synchronized by game engine automatically if called on server.
agent_set_max_hit_points                 = 2090  # (agent_set_max_hit_points, <agent_id>, <value>, [absolute]),
                                                 # Version 1.153+. Changes agent's max hit points. Optional flag [absolute] determines if <value> is an absolute number of his points, or relative percentage (0..1000) of default value. Treated as percentage by default.
                                                 # Official: range [0..100], can be exceeded when using absolute values(?)
agent_deliver_damage_to_agent            = 1722  # (agent_deliver_damage_to_agent, <agent_id_deliverer>, <agent_id>, [damage_amount], [weapon_item_id]),
                                                 # damage value was optional?
                                                 # Official: (agent_deliver_damage_to_agent, <agent_id_deliverer>, <agent_id>, <value>, [item_id]),
                                                 # Makes one agent deal damage to another. Parameter damage_amount is optional, if it is skipped or <= 0, then damage will be calculated using attacker's weapon item and stats (like a normal weapon attack). Optional parameter weapon_item_id was added in 1.153 and will force the game the calculate the damage using this weapon.
agent_deliver_damage_to_agent_advanced   = 1827  # (agent_deliver_damage_to_agent_advanced, <destination>, <attacker_agent_id>, <agent_id>, <value>, [weapon_item_id]),
                                                 # Version 1.153+. Same as (agent_deliver_damage_to_agent), but resulting damage is returned. Also operation takes relations between agents into account, which may result in no damage, or even damage to attacker due to friendly fire rules.
                                                 # Official: (agent_deliver_damage_to_agent_advanced, <destination>, <agent_id_deliverer>, <agent_id>, <value>, [item_id]), #if value <= 0, then damage will be calculated using the weapon item. # item_id is the item that the damage is delivered. can be ignored. #this advanced mode of agent_deliver_damage_to_agent has 2 differences. 1- the delivered damage is returned. 2- the damage delivery is done after checking the relationship between agents. this might cause no damage, or even damage to the shooter agent because of a friendly fire.
add_missile                              = 1829  # (add_missile, <agent_id>, <starting_position>, <starting_speed_fixed_point>, <weapon_item_id>, <weapon_item_modifier>, <missile_item_id>, <missile_item_modifier>),
                                                 # Version 1.153+. Creates a missile with specified parameters. Note that <starting_position> parameter also determines the direction in which missile flies.
                                                 # Gets probably pos1 of wielded item after being called.

agent_get_speed                          = 1689  # (agent_get_speed, <position>, <agent_id>),
                                                 # Retrieves agent speed to (X,Y) coordinates of the position register. Speed is local position to agent.
                                                 # X, Y - fixed point values. Sets Z = 0, rotation of <position> doesn't affected. Cavalry don't have x-coordinate. Their position-y-rotation leans to left or right.
agent_set_no_death_knock_down_only       = 1733  # (agent_set_no_death_knock_down_only, <agent_id>, <value>),
                                                 # Sets the agent as unkillable (value = 1) or normal (value = 0). Unkillable agents will drop on the ground instead of dying and will stand up afterwards.
agent_set_horse_speed_factor             = 1734  # (agent_set_horse_speed_factor, <agent_id>, <speed_multiplier-in-1/100>),
                                                 # Multiplies agent's horse speed (and maneuverability?) by the specified percentile value (using 100 will make the horse). Note that this is called on the rider, not on the horse! Supposedly will persist even if the agent changes horses. 4research.
agent_set_speed_limit                    = 1736  # (agent_set_speed_limit, <agent_id>, <speed_limit(kilometers/hour)>),
                                                 # Limits agent speed by the specified value in kph. Use 5 for average walking speed. Affects only AI agents.
agent_get_damage_modifier                = 2065  # (agent_get_damage_modifier, <destination>, <agent_id>),
                                                 # Output value is in percentage, 100 is default
agent_set_damage_modifier                = 2091  # (agent_set_damage_modifier, <agent_id>, <value>),
                                                 # Version 1.153+. Changes the damage delivered by this agent. Value is in percentage, 100 is default, 1000 is max possible value.
agent_get_accuracy_modifier              = 2066  # (agent_get_accuracy_modifier, <destination>, <agent_id>),
                                                 # Output value is in percentage, 100 is default, value can be between [0..1000]
agent_set_accuracy_modifier              = 2092  # (agent_set_accuracy_modifier, <agent_id>, <value>),
                                                 # Version 1.153+. Changes agent's accuracy (with ranged weapons?). Value is in percentage, 100 is default, value can be between [0..1000]
agent_get_speed_modifier                 = 2067  # (agent_get_speed_modifier, <destination>, <agent_id>),
                                                 # Output value is in percentage, 100 is default, value can be between [0..1000]
agent_set_speed_modifier                 = 2093  # (agent_set_speed_modifier, <agent_id>, <value>),
                                                 # Version 1.153+. Changes agent's speed. Value is in percentage, 100 is default, value can be between [0..1000]
agent_get_reload_speed_modifier          = 2068  # (agent_get_reload_speed_modifier, <destination>, <agent_id>),
                                                 # Output value is in percentage, 100 is default, value can be between [0..1000]
agent_set_reload_speed_modifier          = 2094  # (agent_set_reload_speed_modifier, <agent_id>, <value>),
                                                 # Version 1.153+. Changes agent's reload speed. Value is in percentage, 100 is default, value can be between [0..1000]
agent_get_use_speed_modifier             = 2069  # (agent_get_use_speed_modifier, <destination>, <agent_id>),
                                                 # Output value is in percentage, 100 is default, value can be between [0..1000]
agent_set_use_speed_modifier             = 2095  # (agent_set_use_speed_modifier, <agent_id>, <value>),
                                                 # Version 1.153+. Changes agent's speed with using various scene props. Value is in percentage, 100 is default, value can be between [0..1000]
agent_set_ranged_damage_modifier         = 2099  # (agent_set_ranged_damage_modifier, <agent_id>, <value>),
                                                 # Version 1.157+. Changes agent's damage with ranged weapons. Value is in percentage, 100 is default, value can be between [0..1000]
agent_get_time_elapsed_since_removed     = 1760  # (agent_get_time_elapsed_since_removed, <destination>, <agent_id>),
                                                 # Retrieves the number of seconds that have passed since agent's death. Native uses this only for multiplayer to track player's respawns. Can it be used in singleplayer too? 4research.

# Agent equipment

agent_refill_wielded_shield_hit_points   = 1692  # (agent_refill_wielded_shield_hit_points, <agent_id>),
                                                 # Restores all hit points for the shield the agent is currently wielding.
agent_set_invulnerable_shield            = 1725  # (agent_set_invulnerable_shield, <agent_id>, <value>),
                                                 # Makes the agent shield invulnerable to any damage (value = 1) or makes it vulnerable again (value = 0).
agent_get_wielded_item                   = 1726  # (agent_get_wielded_item, <destination>, <agent_id>, <hand_no>),
                                                 # Retrieves the item reference that the agent is currently wielding in his right hand (hand_no = 0) or left hand (hand_no = 1). Note that weapons are always wielded in right hand, and shield in left hand. When wielding a two-handed weapon (including bows and crossbows), this operation will return -1 for left hand.
agent_get_ammo                           = 1727  # (agent_get_ammo, <destination>, <agent_id>, <value>),
                                                 # Retrieves the current ammo amount agent has for his wielded item (value = 1) or all his items (value = 0).
agent_get_item_cur_ammo                  = 1977  # (agent_get_item_cur_ammo, <destination>, <agent_id>, <slot_no>),
                                                 # Version 1.153+. Returns remaining ammo for specified agent's item.
agent_refill_ammo                        = 1728  # (agent_refill_ammo, <agent_id>),
                                                 # Refills all ammo and throwing weapon stacks that the agent has in his equipment. Doesn't work at items with the flag itp_remove_item_on_use.
agent_set_wielded_item                   = 1747  # (agent_set_wielded_item, <agent_id>, <item_id>),
                                                 # Forces the agent to wield the specified item. Agent must have that item in his equipment for this to work. Use item_id = -1 to unwield any currently wielded item.
agent_equip_item                         = 1779  # (agent_equip_item, <agent_id>, <item_id>, [weapon_slot_no], [modifier]),
                                                 # Adds the specified item to agent and forces him to equip it. Optional weapon_slot_no parameter is only used with weapons and will put the newly added item to that slot (range 1..4) and with optional modifier. If it is omitted with a weapon item, then the agent must have an empty weapon slot for the operation to succeed. Gets synchronized (for weapons, not for armor) by game engine automatically if called on server. Weapons and shields should only be equipped on the server but armor should be equipped on the server for the damage calculations and also on all the clients for the visible meshes.
agent_unequip_item                       = 1774  # (agent_unequip_item, <agent_id>, <item_id>, [weapon_slot_no]),
                                                 # Removes the specified item from the agent. Optional parameter weapon_slot_no is in range 1..4 and determines what weapon slot to remove (item_id must still be set correctly).
agent_set_ammo                           = 1776  # (agent_set_ammo, <agent_id>, <item_id>, <value>),
                                                 # Sets current agent ammo amount to the specified value between 0 and maximum ammo. <item_id> means - ammo item (arrows, bullets, grenades).
                                                 # When you have more than one "quiver" of the same type you must add the total value of all in order to set the correct ammo amount.
agent_get_item_slot                      = 1804  # (agent_get_item_slot, <destination>, <agent_id>, <value>),
                                                 # Retrieves item_id for specified agent's slot Possible slot values range in 0..7, order is weapon1, weapon2, weapon3, weapon4, head_armor, body_armor, leg_armor, hand_armor.
agent_get_ammo_for_slot                  = 1825  # (agent_get_ammo_for_slot, <destination>, <agent_id>, <slot_no>),
                                                 # Retrieves the amount of ammo agent has in the referenced slot (range 0..3).

# Agent animations

agent_set_no_dynamics                    = 1762  # (agent_set_no_dynamics, <agent_id>, <value>),
                                                 # Makes the agent stand on the spot (value = 1) or move normally (value = 0). When frozen on the spot the agent can still turn around and fight if necessary. Used in Native for the wedding scene (required for cut-scenes). Agent will have collision and physics disabled on it if dynamics are turned off, allowing for (agent_set_position) to teleport them to any location, as well as allowing for a scripted no clipping flight mode ala Half-Life.
agent_get_animation                      = 1768  # (agent_get_animation, <destination>, <agent_id>, <body_part>),
                                                 # Retrieves current agent animation for specified body part (0 = lower, 1 = upper).
agent_set_animation                      = 1740  # (agent_set_animation, <agent_id>, <anim_id>, [channel_no]),
                                                 # Forces the agent to perform the specified animation. Optional channel_no parameter determines whether upper body (value = 1) or lower body (value = 0, default) is affected by animation. Gets synchronized by game engine automatically if called on server and if the animation doesn't have the amf_client_prediction flag. Some animations might still need a server event, might be influenced by the flags amf_client_owner_prediction and amf_client_prediction, up4research.
agent_set_stand_animation                = 1741  # (agent_set_stand_animation, <agent_id>, <anim_id>),
                                                 # Defines the animation that this agent will use when standing still. Does not force the agent into actually doing this animation.
agent_set_walk_forward_animation         = 1742  # (agent_set_walk_forward_animation, <agent_id>, <anim_id>),
                                                 # Defines the animation that this agent will use when walking forward. Only works for NPC agents.
agent_set_animation_progress             = 1743  # (agent_set_animation_progress, <agent_id>, <value_fixed_point>),
                                                 # Allows to skip the agent to a certain point in the animation cycle, as specified by the fixed point value (0..fixed_point_multiplier).
agent_ai_set_can_crouch                  = 2083  # (agent_ai_set_can_crouch, <agent_id>, <value>),
                                                 # Version 1.153+. Allows or forbids the agent to crouch. 0 to forbid, 1 to allow.
agent_get_crouch_mode                    = 2097  # (agent_get_crouch_mode, <destination>, <agent_id>),
                                                 # Version 1.153+. Retrieves agent's crouch status (1 = crouching, 0 = standing).
agent_set_crouch_mode                    = 2098  # (agent_set_crouch_mode, <agent_id>, <value>),
                                                 # Version 1.153+. Sets agent's crouch status (1 = crouch, 0 = stand up).

agent_get_attached_scene_prop            = 1756  # (agent_get_attached_scene_prop, <destination>, <agent_id>),
                                                 # Retrieves the reference to scene prop instance which is attached to the agent, or -1 if there isn't any.
agent_set_attached_scene_prop            = 1757  # (agent_set_attached_scene_prop, <agent_id>, <scene_prop_id>),
                                                 # Attaches the specified prop instance to the agent. Used in multiplayer CTF missions to attach flags to players. Does not get synchronized by game engine automatically if called on server. The scale factor at the skin entry gets applied to the scene prop.
agent_set_attached_scene_prop_x          = 1758  # (agent_set_attached_scene_prop_x, <agent_id>, <value>),
                                                 # Offsets the position of the attached scene prop in relation to agent, in centimeters, along the X axis (left/right).
agent_set_attached_scene_prop_y          = 1809  # (agent_set_attached_scene_prop_y, <agent_id>, <value>),
                                                 # Offsets the position of the attached scene prop in relation to agent, in centimeters, along the Y axis (backwards/forward).
agent_set_attached_scene_prop_z          = 1759  # (agent_set_attached_scene_prop_z, <agent_id>, <value>),
                                                 # Offsets the position of the attached scene prop in relation to agent, in centimeters, along the Z axis (down/up).

agent_get_bone_position                  = 2076  # (agent_get_bone_position, <position_no>, <agent_no>, <bone_no>, [<local_or_global>]),
                                                 # Version 1.161+. Returns current position for agent's bone. Examine skeletons.brf and horse_skeleton.brf in CommonRes folder to see hitboxes of these bones and their <bone_no>.
                                                 # Pass 1 as optional <local_or_global> parameter to retrieve global bone coordinates.

# Agent AI and scripted behavior

agent_ai_set_interact_with_player        = 2077  # (agent_ai_set_interact_with_player, <agent_no>, <value>),
                                                 # Version 1.165+. Enables or disables agent AI interation with player. Dialog? Combat? 4research.
agent_set_is_alarmed                     = 1807  # (agent_set_is_alarmed, <agent_id>, <value>),
                                                 # Sets agent's status as alarmed (value = 1) or peaceful (value = 0).
agent_clear_relations_with_agents        = 1802  # (agent_clear_relations_with_agents, <agent_id>),
                                                 # Clears any agent-to-agent relations for specified agent.
agent_add_relation_with_agent            = 1803  # (agent_add_relation_with_agent, <agent_id>, <agent_id>, <value>),
                                                 # Changes relations between two agents on the scene to enemy (value = -1), neutral (value = 0), ally (value = 1). Note that neutral agents are immune to friendly fire.

agent_get_number_of_enemies_following    = 1761  # (agent_get_number_of_enemies_following, <destination>, <agent_id>),
                                                 # Retrieves the total number of enemies who are currently attacking the specified agents. May be used for AI decision-making.
agent_ai_get_num_cached_enemies          = 2670  # (agent_ai_get_num_cached_enemies, <destination>, <agent_no>),
                                                 # Version 1.165+. Returns total number of nearby enemies as has been cached by agent AI. Enemies are numbered from nearest to farthest.
agent_ai_get_cached_enemy                = 2671  # (agent_ai_get_cached_enemy, <destination>, <agent_no>, <cache_index>),
                                                 # Version 1.165+. Return agent reference from AI's list of cached enemies, from nearest to farthest. Returns -1 if the cached enemy is not active anymore.
                                                 # Max slots are 16. Every 2 seconds renew cashed enemies in order from nearest to farthest.


agent_get_attack_action                  = 1763  # (agent_get_attack_action, <destination>, <agent_id>),
                                                 # Retrieves agent's current attack action. Possible values: free = 0, readying_attack = 1, releasing_attack = 2, completing_attack_after_hit = 3, attack_parried = 4, reloading = 5, after_release = 6, cancelling_attack = 7.
agent_get_defend_action                  = 1764  # (agent_get_defend_action, <destination>, <agent_id>),
                                                 # Retrieves agent's current defend action. Possible values: free = 0, parrying = 1, blocking = 2.
agent_get_action_dir                     = 1767  # (agent_get_action_dir, <destination>, <agent_id>),
                                                 # Retrieves the direction of current agent's action.
                                                 # Possible values at attacking: invalid = -1, ranged/thrust = 0, right swing = 1, left swing = 2, overswing = 3.
                                                 # Possible values at defending: invalid = -1, forward/down = 0, right = 1, left = 2, up = 3, global/blocking with shield = 5.
agent_set_attack_action                  = 1745  # (agent_set_attack_action, <agent_id>, <direction_value>, <action_value>),
                                                 # Forces the agent to perform an attack action. Direction value: -2 = cancel any action (1.153+), 0 = thrust, 1 = slashright, 2 = slashleft, 3 = overswing. Action value: 0 = ready and release, 1 = ready and hold.
agent_set_defend_action                  = 1746  # (agent_set_defend_action, <agent_id>, <value>, <duration-in-1/1000-seconds>),
                                                 # Forces the agent to perform a defend action. Possible values: -2 = cancel any action (1.153+), 0 = defend_down, 1 = defend_right, 2 = defend_left, 3 = defend_up. Does time value determine delay, speed or duration? 4research.

agent_set_scripted_destination           = 1730  # (agent_set_scripted_destination, <agent_id>, <position>, [auto_set_z_to_ground_level], [no_rethink]),
                                                 # Official: (agent_set_scripted_destination, <agent_id>, <position_no>, <auto_set_z_to_ground_level>, <no_rethink>),
                                                 # Forces the agent to travel to specified position and stay there until new behavior is set or scripted mode cleared. First optional parameter determines whether the position Z coordinate will be automatically set to ground level (value = 1) or not (value = 0). Second optional parameter added in 1.165 patch, set it to 1 to save resources. It works also for AI cavalry riders and riderless horses.
agent_set_scripted_destination_no_attack = 1748  # (agent_set_scripted_destination_no_attack, <agent_id>, <position>, <auto_set_z_to_ground_level>),
                                                 # Same as above, but the agent will not attack his enemies.
agent_get_scripted_destination           = 1731  # (agent_get_scripted_destination, <position>, <agent_id>),
                                                 # Retrieves the position which is defined as agent's scripted destination, if any.
agent_force_rethink                      = 1732  # (agent_force_rethink, <agent_id>),
                                                 # Forces the agent to recalculate his current actions after setting him a new scripted destination or changing other factors affecting his behavior.
agent_clear_scripted_mode                = 1735  # (agent_clear_scripted_mode, <agent_id>),
                                                 # Clears scripting mode from the agent, making him behave as usual again.
agent_ai_set_always_attack_in_melee      = 1737  # (agent_ai_set_always_attack_in_melee, <agent_id>, <value>),
                                                 # Forces the agent to continuously attack in melee combat, instead of defending. Used in Native to prevent stalling at the top of the siege ladder. Use value = 0 to clear this mode.
agent_get_simple_behavior                = 1738  # (agent_get_simple_behavior, <destination>, <agent_id>),
                                                 # Retrieves agent's current simple behavior (see aisb_* constants in header_mission_templates.py for details).
agent_ai_get_behavior_target             = 2082  # (agent_ai_get_behavior_target, <destination>, <agent_id>),
                                                 # Version 1.153+. UNTESTED. Supposedly returns agent_id which is the target of current agent's behavior.
agent_get_combat_state                   = 1739  # (agent_get_combat_state, <destination>, <agent_id>),
                                                 # Retrieves agent's current combat state:
                                                 #   0 = nothing special, this value is also always returned for player and for dead agents.
                                                 #   1 = target in sight (for ranged units)
                                                 #   2 = guarding (without a shield)
                                                 #   3 = preparing a melee attack or firing a ranged weapon
                                                 #   4 = releasing a melee attack or reloading a crossbow
                                                 #   7 = recovering after being hit in melee OR blocking with a shield. Contradictory information, 4research.
                                                 #   8 = target to the right (horse archers) OR no target in sight (ranged units). Contradictory information, 4research.

agent_ai_get_move_target                 = 2081  # (agent_ai_get_move_target, <destination>, <agent_id>),
                                                 # Version 1.153+. UNTESTED. Supposedly returns the enemy agent to whom the agent is currently moving to.
agent_get_look_position                  = 1709  # (agent_get_look_position, <position>, <agent_id>),
                                                 # Retrieves the coordinates of the agent position and currently looking angles. It is a position that is located centrally horizontally and vertically on the bottom of the model. Basically, it is a position rotated with the agents direction but located underneath the feet.
agent_set_look_target_position           = 1744  # (agent_set_look_target_position, <agent_id>, <position>),
                                                 # Forces the agent to look at specified position (turn his head as necessary). Alarmed agents will ignore this. Agents will only look for a short amount of time.
agent_ai_get_look_target                 = 2080  # (agent_ai_get_look_target, <destination>, <agent_id>),
                                                 # Version 1.153+. UNTESTED. Supposedly returns agent_id that the agent is currently looking at.
agent_set_look_target_agent              = 1713  # (agent_set_look_target_agent, <watcher_agent_id>, <observed_agent_id>),
                                                 # Forces the agent to look at specified agent (track his movements). Alarmed agents will ignore this.
agent_start_running_away                 = 1751  # (agent_start_running_away, <agent_id>, [<position_no>]),
                                                 # Makes the agent flee the battlefield, ignoring everything else and not attacking. If the agent reaches the edge of map in this mode, he will fade out. Optional position_no parameter added in 1.153 and will make the agent flee to specified position instead (pos0 is not allowed and will be ignored).  When used on a mounted horse makes the agent 'fall off' instantly and the horse will run away (works for player too).
agent_stop_running_away                  = 1752  # (agent_stop_run_away, <agent_id>),
                                                 # Cancels fleeing behavior for the agent, turning him back to combat state.
agent_ai_set_aggressiveness              = 1753  # (agent_ai_set_aggressiveness, <agent_id>, <value>),
                                                 # Sets the aggressiveness parameter for agent AI to use. Default value is 100. Higher values make agent more aggressive. Actual game effects are not obvious, apparently used to speed up mob aggravation when previously neutral.
agent_set_kick_allowed                   = 1754  # (agent_set_kick_allowed, <agent_id>, <value>),
                                                 # Enables (value = 1) or disables (value = 0) kicking for the specified agent. Only makes sense for player-controlled agents as bots don't know how to kick anyway (if not scripted into the mod, kicking AI).
set_cheer_at_no_enemy                    = 2379  # (set_cheer_at_no_enemy, <value>),
                                                 # Version 1.153+. Determines whether the agents will cheer when no enemy remain on the map. 0 = do not cheer, 1 = cheer. A voice_victory sound entry at the skin entry is required for it to work.

agent_add_offer_with_timeout             = 1777  # (agent_add_offer_with_timeout, <agent_id>, <offerer_agent_id>, <duration-in-1/1000-seconds>),
                                                 # Esoteric stuff. Used in multiplayer duels. Second agent_id is offerer, 0 value for duration is an infinite offer.
agent_check_offer_from_agent             = 1778  # (agent_check_offer_from_agent, <agent_id>, <offerer_agent_id>), #second agent_id is offerer
                                                 # Esoteric stuff. Used in multiplayer duels. Second agent_id is offerer.

# Team operations

agent_get_group                          = 1765  # (agent_get_group, <destination>, <agent_id>),
                                                 # In multiplayer: Retrieves reference to player who is currently the leader of specified bot agent.
                                                 # In singleplayer: Retrieves agent group wich is the same as agent team.
agent_set_group                          = 1766  # (agent_set_group, <agent_id>, <player_leader_id>),
                                                 # In multiplayer: Puts the bot agent under command of specified player.
                                                 # In singleplayer: Change the group. Agent team is not changed. Use agent_set_team.

agent_get_team                           = 1770  # (agent_get_team, <destination>, <agent_id>),
                                                 # Retrieves the team that the agent belongs to.
agent_set_team                           = 1771  # (agent_set_team, <agent_id>, <value>),
                                                 # Puts the agent to specified team number. Also copies "value" to agent group.
agent_get_class                          = 1772  # (agent_get_class , <destination>, <agent_id>),
                                                 # Retrieves the agent class (see grc_* constants in header_mission_templates.py for reference). Note this operation returns the troop class that the game divines from troop equipment and flags, ignoring any custom troop class settings.
agent_get_division                       = 1773  # (agent_get_division , <destination>, <agent_id>),
                                                 # Retrieves the agent division (custom troop class number in 0..8 range).
agent_set_division                       = 1783  # (agent_set_division, <agent_id>, <value>),
                                                 # Puts the agent into the specified division. This does not affect agent's troop class. Note that there's a bug in Warband: if an order is issued to agent's original division, the agent will immediately switch back to its original division number. Therefore, if you want to manipulate agent divisions dynamically during the battle, you need to implement some workarounds for this bug.

team_get_hold_fire_order                 = 1784  # (team_get_hold_fire_order, <destination>, <team_no>, <division>),
                                                 # Retrieves current status of hold fire order for specified team/division (see aordr_* constants in header_mission_templates.py for reference).
team_get_movement_order                  = 1785  # (team_get_movement_order, <destination>, <team_no>, <division>),
                                                 # Retrieves current movement orders for specified team/division (see mordr_* constants in header_mission_templates.py for reference).
team_get_riding_order                    = 1786  # (team_get_riding_order, <destination>, <team_no>, <division>),
                                                 # Retrieves current status of riding order for specified team/division (see rordr_* constants in header_mission_templates.py for reference).
team_get_weapon_usage_order              = 1787  # (team_get_weapon_usage_order, <destination>, <team_no>, <division>),
                                                 # Retrieves current status of weapon usage order for specified team/division (see wordr_* constants in header_mission_templates.py for reference).
team_give_order                          = 1790  # (team_give_order, <team_no>, <division>, <order_id>),
                                                 # Issues an order to specified team/division.
team_set_order_position                  = 1791  # (team_set_order_position, <team_no>, <division>, <position>),
                                                 # Defines the position for specified team/division when currently issued order requires one.
team_get_leader                          = 1792  # (team_get_leader, <destination>, <team_no>),
                                                 # Retrieves the reference to the agent who is the leader of specified team.
team_set_leader                          = 1793  # (team_set_leader, <team_no>, <new_leader_agent_id>),
                                                 # Sets the agent as the new leader of specified team.
team_get_order_position                  = 1794  # (team_get_order_position, <position>, <team_no>, <division>),
                                                 # Retrieves position which is used for specified team/division current orders.
team_set_order_listener                  = 1795  # (team_set_order_listener, <team_no>, <division>, [add_to_listeners]),
                                                 # Official: (team_set_order_listener, <team_no>, <sub_class>, <value>), #merge with old listeners if value is non-zero #clear listeners if sub_class is less than zero
                                                 # Set the specified division as the one which will be following orders issued by the player (assuming the player is on the same team). If optional parameter add_to_listeners is greater than 0, then the operation will instead *add* specified division to order listeners. If division number is -1, then list of order listeners is cleared. If division number is 9, then all divisions will listen to player's orders.
team_set_relation                        = 1796  # (team_set_relation, <team_no>, <team_no_2>, <value>),
                                                 # Sets relations between two teams. Possible values: enemy (-1), neutral (0) and friendly (1).
store_remaining_team_no                  = 2360  # (store_remaining_team_no, <destination>),
                                                 # Retrieves the number of the last remaining team. Currently not used in Native, possibly deprecated.
team_get_gap_distance                    = 1828  # (team_get_gap_distance, <destination>, <team_no>, <sub_class>),
                                                 # Version 1.153+. UNTESTED. Supposedly returns average gap between troops of a specified team/class (depends on how many Stand Closer/Spread Out orders were given).

# Combat statistics

store_enemy_count                        = 2380  # (store_enemy_count, <destination>),
                                                 # No longer used in Native. Apparently stores total number of active enemy agents. Possibly deprecated. 4research.
store_friend_count                       = 2381  # (store_friend_count, <destination>),
                                                 # No longer used in Native. Apparently stores total number of active friendly agents. Possibly deprecated. 4research.
store_ally_count                         = 2382  # (store_ally_count, <destination>),
                                                 # No longer used in Native. Apparently stores total number of active allied agents (how is it different from friends?). Possibly deprecated. 4research.
store_defender_count                     = 2383  # (store_defender_count, <destination>),
                                                 # No longer used in Native. Apparently stores total number of active agents on defender's side. Possibly deprecated. 4research.
store_attacker_count                     = 2384  # (store_attacker_count, <destination>),
                                                 # No longer used in Native. Apparently stores total number of active agents on attacker's side. Possibly deprecated. 4research.
store_normalized_team_count              = 2385  # (store_normalized_team_count, <destination>, <team_no>),
                                                 # Stores the number of agents belonging to specified team, normalized according to battle_size and advantage. Commonly used to calculate advantage and possibly reinforcement wave sizes.
                                                 # 100% is equal to relative spawn agents count on mission start. For example if spawn point have 40 then 50% will be 20.

################################################################################
# [ Z23 ] PRESENTATIONS
################################################################################

  # Presentations are a complex subject, because of their flexibility. Each
  # presentation is nothing more but a number of screen control elements, called
  # overlays. There are many types of overlays, each coming with its own
  # behavior and looks. For as long as the presentation is running, you can
  # monitor the status of those overlays and change their looks, contents and
  # position on the screen.

  # Presentation is nothing but a set of triggers. There are only five triggers
  # that the presentation can have, but skillful control of them allows you to
  # do nearly everything you can think of.

  # ti_on_presentation_load fires only once when the presentation is started.
  # This is the place where you will usually create all overlays that your
  # presentation needs, initialize their looks and contents and put them to
  # their positions on the screen.

  # ti_on_presentation_event_state_change is probably the most important and
  # easy one. It fires every time some overlay in your presentation changes
  # state. For each type of overlay this means something. For a button overlay,
  # this means that the user has clicked the button. In this case, you will want
  # to run the code responsible for that button effects. So you can put a "Win"
  # button on your presentation, and when it's clicked, you can run the code
  # which will give all castles and towns in the game to you. :-)

  # ti_on_presentation_mouse_press trigger fires every time user clicks a mouse
  # button on one of presentation overlays, even if the overlay did not change
  # its state as the result.

  # ti_on_presentation_mouse_enter_leave trigger fires when the mouse pointer
  # moves over one of presentation's overlays, or moves out of it. This might
  # be useful if you want your presentation to react to user's mouse movements,
  # not only clicks.

  # ti_on_presentation_run trigger will fire every frame (in other words, with
  # the frequency of your game FPS). You can put some code in this trigger if
  # you want your presentation to constantly do something even if the user is
  # passive.

  # Note that while a running presentation will usually pause your game until
  # you stop it, it is also possible to write presentations which will not stop
  # the game, but will run as the time goes. To see an example, go into any
  # battle in Warband and press Backspace. You will see the interface which
  # displays the mini-map of the battle, positions of all troops, and elements
  # that you can use to issue orders to your companions (if you have any). All
  # this is a presentation as well, called "prsnt_battle". And if you have
  # played multiplayer, then you might be interested to know that all menus,
  # including equipment selection for your character, are presentations as well.

# Conditional operations

is_presentation_active                            =  903  # (is_presentation_active, <presentation_id),
                                                          # Checks if the specified presentation is currently running.

# General presentation operations

start_presentation                                =  900  # (start_presentation, <presentation_id>),
                                                          # Starts the specified presentation.
start_background_presentation                     =  901  # (start_background_presentation, <presentation_id>),
                                                          # Apparently allows you to start a presentation in background but stay in the menu. 4research.
                                                          # Official: can only be used in game menus
presentation_set_duration                         =  902  # (presentation_set_duration, <duration-in-1/100-seconds>),
                                                          # Sets presentation duration time, in 1/100th of second. Must be called when a presentation is active. If several presentations are active, duration will be set for all of them.

# Creating overlays

create_text_overlay                               =  910  # (create_text_overlay, <destination>, <string_id>),
                                                          # Creates a text label overlay and returns its overlay_id.
create_mesh_overlay                               =  911  # (create_mesh_overlay, <destination>, <mesh_id>),
                                                          # Creates a mesh overlay and returns its overlay_id.
create_mesh_overlay_with_item_id                  =  944  # (create_mesh_overlay_with_item_id, <destination>, <item_id>),
                                                          # Creates a mesh overlay, using the specified item mesh. Returns overlay_id.
create_mesh_overlay_with_tableau_material         =  939  # (create_mesh_overlay_with_tableau_material, <destination>, <mesh_id>, <tableau_material_id>, <value>),
                                                          # Creates a mesh overlay, using the specified tableau_material. When mesh_id = -1, it is generated automatically. Value is passed as the parameter for tableau_material script. Returns overlay_id.
create_button_overlay                             =  912  # (create_button_overlay, <destination>, <string_id>),
                                                          # Creates a generic button overlay and returns its overlay_id. The only difference between this and subsequent two operations is that they use different button meshes.
create_game_button_overlay                        =  940  # (create_game_button_overlay, <destination>, <string_id>),
                                                          # Creates a game button overlay and returns its overlay_id.
create_in_game_button_overlay                     =  941  # (create_in_game_button_overlay, <destination>, <string_id>),
                                                          # Creates an in-game button overlay and returns its overlay_id.
create_image_button_overlay                       =  913  # (create_image_button_overlay, <destination>, <mesh_id>, <mesh_id>),
                                                          # Creates an image button, using two meshes for normal (1st mesh) and pressed (2nd mesh) status. Button does not have a textual label. Returns button overlay_id.
create_image_button_overlay_with_tableau_material =  938  # (create_image_button_overlay_with_tableau_material, <destination>, <mesh_id>, <tableau_material_id>, <value>),
                                                          # Creates an image button from the specified mesh, using tableau_material as the image. When mesh = -1, it is generated automatically. Value is passed as the parameter to the tableau_material script. Returns overlay_id.
create_slider_overlay                             =  914  # (create_slider_overlay, <destination>, <min_value>, <max_value>),
                                                          # Creates horizontal slider overlay, with positions of the slider varying between min and max values. Current value of the slider can be changed with (overlay_set_val). Returns slider's overlay_id.
create_progress_overlay                           =  915  # (create_progress_overlay, <destination>, <min_value>, <max_value>),
                                                          # Creates progress bar overlay, with positions of the bar varying between min and max values. Current value of the progress bar can be changed with (overlay_set_val). Returns bar's overlay_id.
create_number_box_overlay                         =  942  # (create_number_box_overlay, <destination>, <min_value>, <max_value>),
                                                          # Creates a number box overlay (a small field for numeric value and small increase/decrease buttons to the right) with specified min and max values. Returns number box overlay_id.
create_text_box_overlay                           =  917  # (create_text_box_overlay, <destination>),
                                                          # Apparently deprecated. No longer used in Native.
create_simple_text_box_overlay                    =  919  # (create_simple_text_box_overlay, <destination>),
                                                          # Creates a text field overlay, where user can enter any text. Returns text field's overlay_id. Text contents of the field can be retrieved from s0 trigger in ti_on_presentation_event_state_change event for the text field.
create_check_box_overlay                          =  918  # (create_check_box_overlay, <destination>, <checkbox_off_mesh>, <checkbox_on_mesh>),
                                                          # Creates a checkbox overlay. Returns checkbox overlay_id.
create_listbox_overlay                            =  943  # (create_list_box_overlay, <destination>),
                                                          # Creates a listbox overlay. Individual items can be added with (overlay_add_item) and index of currently selected item can be set with (overlay_set_val). Returns listbox overlay_id. Importance of later two parameters unclear (default text&value?). 4research.
                                                          # Old syntax (has it changed?): (create_list_box_overlay, <destination>, <string>, <value>),
create_combo_label_overlay                        =  948  # (create_combo_label_overlay, <destination>),
                                                          # Creates a combo label overlay. Looks like plain text label. Individual items can be added with (overlay_add_item) and currently selected item can be set with (overlay_set_val). Returns combo block's overlay_id.
create_combo_button_overlay                       =  916  # (create_combo_button_overlay, <destination>),
                                                          # Creates a combo button overlay. For example see "Screen Resolution" dropdown in Settings menu. Individual items can be added with (overlay_add_item) and currently selected item can be set with (overlay_set_val). Returns combo block's overlay_id.
overlay_add_item                                  =  931  # (overlay_add_item, <overlay_id>, <string_id>),
                                                          # Adds an item to the listbox or combobox. Items are indexed from 0. Note the order in which items appear in the dropdown is reverse to the order in which they're added.

# Overlays hierarchy manipulation

set_container_overlay                             =  945  # (set_container_overlay, <overlay_id>),
                                                          # Defines the specified overlay as the container. All subsequently created overlays will be placed inside the container, and their coordinates will be based on container's position. All containers with their contents will be displayed *above* any non-container overlays. Use -1 to stop placing overlays to current container and resume normal behavior.
overlay_set_container_overlay                     =  951  # (overlay_set_container_overlay, <overlay_id>, <container_overlay_id>),
                                                          # Allows you to put one overlay into a container, or remove it from container (if container_overlay_id = -1) without setting current overlay. May be unreliable.

# Overlay manipulation

overlay_get_position                              =  946  # (overlay_get_position, <position>, <overlay_id>),
                                                          # Retrieves overlay current position to specified position trigger, using position's X and Y coordinates. Note that the screen size in Warband is (1.00,0.75), further modified by fixed point multiplier.
overlay_set_val                                   =  927  # (overlay_set_val, <overlay_id>, <value>),
                                                          # Sets the value of the overlays which have numeric values.
                                                          # Official: can be used for sliders, combo buttons and check boxes
overlay_set_text                                  =  920  # (overlay_set_text, <overlay_id>, <string_id>),
                                                          # Changes the overlay text (if it has any). Works for labels, text fields, buttons with text labels...
overlay_set_boundaries                            =  928  # (overlay_set_boundaries, <overlay_id>, <min_value>, <max_value>),
                                                          # Changes the value boundaries for the overlays that have them.
overlay_set_position                              =  926  # (overlay_set_position, <overlay_id>, <position>),
                                                          # Sets the overlay position on the screen, using position's X and Y coordinates. Note that the screen size in Warband is (1.00,0.75), further modified by fixed point multiplier.
overlay_set_size                                  =  925  # (overlay_set_size, <overlay_id>, <position>),
                                                          # Sets the overlay size, using position's X and Y coordinates. For meshes, button overlays, etc. the operation will modify the actual size of the overlay, whereas for text overlays it will dictate the font size the overlay will use. The default font size is X = 1000, Y = 1000 (with a fixed_point_multiplier of 1000). Note that the screen size in Warband is (1.00,0.75), further modified by fixed point multiplier. Also see (overlay_set_area_size).
overlay_set_area_size                             =  929  # (overlay_set_area_size, <overlay_id>, <position>),
                                                          # Defines the actual area on the screen used to display the overlay. If its size is greater than area size, it will create a scrollable area with appropriate scrollbars. Can be used to create scrollable areas for large text, or scrollable containers with many children elements (see Host Game screen for a typical example).
overlay_set_additional_render_height              =  952  # (overlay_set_additional_render_height, <overlay_id>, <height_adder>),
                                                          # Version 1.153+. Effects uncertain. 4research.
overlay_animate_to_position                       =  937  # (overlay_animate_to_position, <overlay_id>, <duration-in-1/1000-seconds>, <position>),
                                                          # Moves overlay to specified position during a specified timeframe, specified in 1/1000th of second.
overlay_animate_to_size                           =  936  # (overlay_animate_to_size, <overlay_id>, <duration-in-1/1000-seconds>, <position>),
                                                          # Changes overlay size to specified value during a specified timeframe, specified in 1/1000th of second.
overlay_set_mesh_rotation                         =  930  # (overlay_set_mesh_rotation, <overlay_id>, <position>),
                                                          # Despite the name, works with any overlay, allowing you to put it on the screen in rotated position. To determine the angles, position's rotation values are used (not coordinates!). Usually you will want to only use rotation around Z axis (which results in clockwise or anti-clockwise rotation as seen by user). Note that rotating overlays which are placed inside a container may cause strange results, so some trial and error will be necessary in such situation.
overlay_set_material                              =  956  # (overlay_set_material, <overlay_id>, <string_no>),
                                                          # Version 1.161+. Replaces the material used for rendering specified overlay.
overlay_set_color                                 =  921  # (overlay_set_color, <overlay_id>, <color>),
                                                          # Changes the overlay color (hexadecimal value 0xRRGGBB). May not work with some overlay types.
overlay_set_alpha                                 =  922  # (overlay_set_alpha, <overlay_id>, <alpha>),
                                                          # Changes the overlay alpha (hexadecimal value in 0x00..0xFF range). May not work with some overlay types.
overlay_set_hilight_color                         =  923  # (overlay_set_hilight_color, <overlay_id>, <color>),
                                                          # Highlights the overlay with specified color. May not work with some overlay types.
overlay_set_hilight_alpha                         =  924  # (overlay_set_hilight_alpha, <overlay_id>, <alpha>),
                                                          # Highlights the overlay with specified alpha. May not work with some overlay types.
overlay_animate_to_color                          =  932  # (overlay_animate_to_color, <overlay_id>, <duration-in-1/1000-seconds>, <color>),
                                                          # Changes overlay's color during a specified timeframe, specified in 1/000th of second.
overlay_animate_to_alpha                          =  933  # (overlay_animate_to_alpha, <overlay_id>, <duration-in-1/1000-seconds>, <color>),
                                                          # Changes overlay's alpha during a specified timeframe, specified in 1/000th of second.
                                                          # Doesn't work with text overlays using <tf_with_outline>.
                                                          # overlay_set_alpha doesn't work when animating is processed. Use overlay_animate_to_alpha with 0 msec.
overlay_animate_to_highlight_color                =  934  # (overlay_animate_to_highlight_color, <overlay_id>, <duration-in-1/1000-seconds>, <color>),
                                                          # Highlights overlay to specified color during a specified timeframe, specified in 1/000th of second.
overlay_animate_to_highlight_alpha                =  935  # (overlay_animate_to_highlight_alpha, <overlay_id>, <duration-in-1/1000-seconds>, <color>),
                                                          # Highlights overlay to specified alpha during a specified timeframe, specified in 1/000th of second.
overlay_set_display                               =  947  # (overlay_set_display, <overlay_id>, <value>),
                                                          # Shows (value = 1) or hides (value = 0) the specified overlay.
overlay_obtain_focus                              =  949  # (overlay_obtain_focus, <overlay_id>),
                                                          # Makes the specified overlay obtain input focus. Only works for textboxes.

overlay_set_tooltip                               =  950  # (overlay_set_tooltip, <overlay_id>, <string_id>),
                                                          # Defines a text which will be displayed as a tooltip when mouse pointer will hover over the specified overlay. Unreliable, always test how it works.

# Popups and some esoteric stuff

show_item_details                                 =  970  # (show_item_details, <item_id>, <position>, <price_multiplier_percentile>),
                                                          # Shows a popup box at the specified position, containing standard game information for the specified item. Last parameter determines price percentile multiplier. Multiplier value of 100 will display item standard price, value of 0 will display "Default Item" instead of price (used in multiplayer equipment selection presentation).
                                                          # Official: price_multiplier is percent, usually returned by script_game_get_item_[buy/sell]_price_factor
show_item_details_with_modifier                   =  972  # (show_item_details_with_modifier, <item_id>, <item_modifier>, <position>, <price_multiplier_percentile>),
                                                          # Same as above, but displays stats and price information for an item with a modifier.
close_item_details                                =  971  # (close_item_details),
                                                          # Closes the item details popup box.
show_troop_details                                = 2388  # (show_troop_details, <troop_id>, <position>, <troop_price>),
                                                          # Version 1.153+. Supposedly displays a popup with troop information at specified place. 4research.

################################################################################
# [ Z24 ] MULTIPLAYER AND NETWORKING (LEFT FOR SOMEONE MORE FAMILIAR WITH THIS)
################################################################################

  # This section is eagerly waiting for someone to write documentation comments.
  # Regarding the player ID: The singleplayer does not have player ids, it has 
  # agents IDs instead of player IDs. Therefore get_player_agent_no is the operation
  # to go with there. All player related operations won't work in singleplayer,
  # the operations will display a script warning and do nothing.

# Conditional operations

player_is_active                             =  401  # (player_is_active, <player_id>),
                                                     # Checks that the specified player is active (i.e. connected to server).
                                                     # Checks that the player reference corresponds to active player. Players are assigned a free ID after connection and on disconnection it becomes free/invalid until taken by another connecting player.
multiplayer_is_server                        =  417  # (multiplayer_is_server),
                                                     # Checks that the code is running on multiplayer server. Operation will fail on client machines or in singleplayer mode. This will succeed for listen and dedicated servers and will only fail on clients.
multiplayer_is_dedicated_server              =  418  # (multiplayer_is_dedicated_server),
                                                     # Checks that the game running is a dedicated server. This will only succeed for dedicated servers and will fail on listen servers and clients.
game_in_multiplayer_mode                     =  419  # (game_in_multiplayer_mode),
                                                     # Checks that the game is running in multiplayer mode.
player_is_admin                              =  430  # (player_is_admin, <player_id>),
                                                     # Checks that the player used the admin password to join the server.
player_is_busy_with_menus                    =  438  # (player_is_busy_with_menus, <player_id>),
                                                     # Undocumented. Educated guess is it's true when player is running a presentation without prsntf_read_only flag.
                                                     # This one is used when a player presses a hotkey like TAB or ESC to check if he doesn't have any kind of presentation open, however, it works strangely and is almost always accompannied by some sort of (neg|is_presentation_active, "prst"), in native
                                                     # Research: Is actually not getting used together with (neg|is_presentation_active, "prst"). It is getting called on the server and isn't synched with clients. Used in multiplayer to prevent the spawning of a player agent if the player is still busy with the menus (and might still change the loadout of the agent).
player_item_slot_is_picked_up                =  461  # (player_item_slot_is_picked_up, <player_id>, <item_slot_no>),
                                                     # Checks that the provided item slot for the referenced player was picked up from the battlefield instead of bought.

# Player slot operations

player_set_slot                              =  508  # (player_set_slot, <player_id>, <slot_no>, <value>),
player_get_slot                              =  528  # (player_get_slot, <destination>, <player_id>, <slot_no>),
player_slot_eq                               =  548  # (player_slot_eq, <player_id>, <slot_no>, <value>),
player_slot_ge                               =  568  # (player_slot_ge, <player_id>, <slot_no>, <value>),

# Network communication operations

send_message_to_url                          =  380  # (send_message_to_url, <string_id>, <encode_url>),
                                                     # Sends an HTTP request. Response from that URL will be returned to "script_game_receive_url_response". Parameter <encode_url> is optional and effects are unclear. Supposedly its equivalent of calling (str_encode_url) on the first parameter which doesn't make sense for me.
                                                     # Accesses the the URL in the provided string. The result will be returned to script_game_receive_url_response.

multiplayer_send_message_to_server           =  388  # (multiplayer_send_message_to_server, <message_type>),
                                                     # Multiplayer client operation. Send a simple message (only message code, no data) to game server.
multiplayer_send_int_to_server               =  389  # (multiplayer_send_int_to_server, <message_type>, <value>),
                                                     # Multiplayer client operation. Send a message with a single extra integer value to game server.
multiplayer_send_2_int_to_server             =  390  # (multiplayer_send_2_int_to_server, <message_type>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_server), but two integer values are sent.
multiplayer_send_3_int_to_server             =  391  # (multiplayer_send_3_int_to_server, <message_type>, <value>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_server), but three integer values are sent.
multiplayer_send_4_int_to_server             =  392  # (multiplayer_send_4_int_to_server, <message_type>, <value>, <value>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_server), but four integer values are sent.
multiplayer_send_string_to_server            =  393  # (multiplayer_send_string_to_server, <message_type>, <string_id>),
                                                     # Multiplayer client operation. Send a message with a string value to game server.

# <message_type> parameter must be between 0 and 127 or it will be truncated. In the case of Native they can be found on header_common.py as client and server events.
# These are handled in script_game_receive_network_message and are used for server events. As for strings, the input is s0 (in the script).
# The other 6 operations (multiplayer_send_*_to_player) have the same functionality but are called on the server and send the message to the player referenced by <player_id>. Also handled by script_game_receive_network_message.

multiplayer_send_message_to_player           =  394  # (multiplayer_send_message_to_player, <player_id>, <message_type>),
                                                     # Multiplayer server operation. Send a simple message (only message code, no data) to one of connected players.
multiplayer_send_int_to_player               =  395  # (multiplayer_send_int_to_player, <player_id>, <message_type>, <value>),
                                                     # Multiplayer server operation. Send a message with a single extra integer value to one of connected players.
multiplayer_send_2_int_to_player             =  396  # (multiplayer_send_2_int_to_player, <player_id>, <message_type>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_player), but two integer values are sent.
multiplayer_send_3_int_to_player             =  397  # (multiplayer_send_3_int_to_player, <player_id>, <message_type>, <value>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_player), but three integer values are sent.
multiplayer_send_4_int_to_player             =  398  # (multiplayer_send_4_int_to_player, <player_id>, <message_type>, <value>, <value>, <value>, <value>),
                                                     # Same as (multiplayer_send_int_to_player), but four integer values are sent.
multiplayer_send_string_to_player            =  399  # (multiplayer_send_string_to_player, <player_id>, <message_type>, <string_id>),
                                                     # Multiplayer server operation. Send a message with a string value to one of connected players.

# Player handling operations

get_max_players                              =  400  # (get_max_players, <destination>),
                                                     # Returns maximum possible number of connected players. Apparently always returns a constant value, however its return value can change as maximum increases with new patches.
player_get_team_no                           =  402  # (player_get_team_no, <destination>, <player_id>),
                                                     # Retrieves the team that the player belongs to.
player_set_team_no                           =  403  # (player_set_team_no, <player_id>, <team_id>),
                                                     # Assigns a player to the specified team.
player_get_troop_id                          =  404  # (player_get_troop_id, <destination>, <player_id>),
                                                     # Retrieves player's selected troop reference.
player_set_troop_id                          =  405  # (player_set_troop_id, <player_id>, <troop_id>),
                                                     # Assigns the selected troop reference to a player.
player_get_agent_id                          =  406  # (player_get_agent_id, <destination>, <player_id>),
                                                     # Retrieves player's current agent reference. Returns a negative value if player has no agent.
agent_get_player_id                          = 1724  # (agent_get_player_id, <destination>, <agent_id>),
                                                     # Retrieves player reference that is currently controlling the specified agent.
player_get_gold                              =  407  # (player_get_gold, <destination>, <player_id>),
                                                     # Retrieves player's current gold amount.
player_set_gold                              =  408  # (player_set_gold, <player_id>, <value>, <max_value>),
                                                     # Sets player's new gold amount and maximum allowed gold amount. Use 0 for <max_value> to remove gold limit.
player_spawn_new_agent                       =  409  # (player_spawn_new_agent, <player_id>, <entry_point>),
                                                     # Spawns a new agent for the specified player. Essentially a combination of (spawn_agent) and (player_control_agent) operations.
player_add_spawn_item                        =  410  # (player_add_spawn_item, <player_id>, <item_slot_no>, <item_id>),
                                                     # Adds the specified item to the specified player. Will take effect after the next player_spawn_new_agent. Available item slots are: ek_item_0, ek_item_1, ek_item_2, ek_item_3, ek_head, ek_body, ek_foot, ek_gloves, ek_horse. Unsure if ek_food is used in multiplayer; Taken from header_items.py
multiplayer_get_my_team                      =  411  # (multiplayer_get_my_team, <destination>),
                                                     # Client operation. Retrieves player's currently selected team.
multiplayer_get_my_troop                     =  412  # (multiplayer_get_my_troop, <destination>),
                                                     # Client operation. Retrieves player's currently selected troop.
multiplayer_set_my_troop                     =  413  # (multiplayer_set_my_troop, <destination>),
                                                     # Client operation. Selects a new troop for the player.
multiplayer_get_my_gold                      =  414  # (multiplayer_get_my_gold, <destination>),
                                                     # Client operation. Retrieves current player's gold amount.
multiplayer_get_my_player                    =  415  # (multiplayer_get_my_player, <destination>),
                                                     # Client operation. Retrieves current player's player_id reference.

multiplayer_make_everyone_enemy              =  420  # (multiplayer_make_everyone_enemy),
                                                     # Used in deathmatch mode to make everyone hostile to all other agents.
player_control_agent                         =  421  # (player_control_agent, <player_id>, <agent_id>),
                                                     # Server operation. Puts the agent under specified player's control. Operation will change agent's face code and banner to those of player.
player_get_item_id                           =  422  # (player_get_item_id, <destination>, <player_id>, <item_slot_no>),
                                                     # Server operation. Retrieves item that's currently equipped by specified player in <item_slot_no> equipment slot.
player_get_banner_id                         =  423  # (player_get_banner_id, <destination>, <player_id>),
                                                     # Server operation. Retrieves banner_id reference used by the specified player. Note that in MP banners are enumerated starting from 0 (unlike single-player where they're enumeration depends on scene prop banners' reference range).

player_set_is_admin                          =  429  # (player_set_is_admin, <player_id>, <value>),
                                                     # Server operation. Set the current player as admin (value = 1) or not (value = 0).
player_get_score                             =  431  # (player_get_score, <destination>, <player_id>),
                                                     # Gets the current score of the player.
player_set_score                             =  432  # (player_set_score, <player_id>, <value>),
                                                     # Sets the score of the player.
player_get_kill_count                        =  433  # (player_get_kill_count, <destination>, <player_id>),
                                                     # Gets the current kill count of the player.
player_set_kill_count                        =  434  # (player_set_kill_count, <player_id>, <value>),
                                                     # Sets the kill count of the player.
player_get_death_count                       =  435  # (player_get_death_count, <destination>, <player_id>),
                                                     # Gets the current death count of the player.
player_set_death_count                       =  436  # (player_set_death_count, <player_id>, <value>),
                                                     # Sets the death count of the player.
player_get_ping                              =  437  # (player_get_ping, <destination>, <player_id>),
                                                     # Gets the current ping of the player.
player_get_is_muted                          =  439  # (player_get_is_muted, <destination>, <player_id>),
                                                     # Checks if a player is currently muted (1) or not (0).
player_set_is_muted                          =  440  # (player_set_is_muted, <player_id>, <value>, [mute_for_everyone]),
                                                     # Sets if a player gets muted (1) or unmuted (0). mute_for_everyone is an optional parameter and should be set to 1 if player is muted for everyone (this works only on server).
player_get_unique_id                         =  441  # (player_get_unique_id, <destination>, <player_id>), #can only bew used on server side
                                                     # Server operation. Retrieves player's unique identifier which is determined by player's game license code. This number is supposed to be unique for each license, allowing reliable player identification across servers.
player_get_gender                            =  442  # (player_get_gender, <destination>, <player_id>),
                                                     # Gets the current player gender/skin, in Native 0 for the male and 1 for the female skin. Take note that Native can only process two genders/skins in multiplayer.

player_save_picked_up_items_for_next_spawn   =  459  # (player_save_picked_up_items_for_next_spawn, <player_id>),
                                                     # Allows the player to keep the stuff he/she picked up during current round.
player_get_value_of_original_items           =  460  # (player_get_value_of_original_items, <destination>, <player_id>),
                                                     # Official docs: this operation returns values of the items, but default troop items will be counted as zero (except horse)

profile_get_banner_id                        =  350  # (profile_get_banner_id, <destination>),
                                                     # Client operation. Retrieves banner_id reference used by the game for multiplayer. Note that in MP banners are enumerated starting from 0 (unlike single-player where they're enumeration depends on scene prop banners' reference range).
profile_set_banner_id                        =  351  # (profile_set_banner_id, <value>),
                                                     # Client operation. Assigns a new banner_id to be used for multiplayer. Note that in MP banners are enumerated starting from 0 (unlike single-player where they're enumeration depends on scene prop banners' reference range).

# Team handling operations

team_get_bot_kill_count                      =  450  # (team_get_bot_kill_count, <destination>, <team_id>),
                                                     # Gets the current kill count of the bots being part of the team.
team_set_bot_kill_count                      =  451  # (team_get_bot_kill_count, <destination>, <team_id>),
                                                     # Sets the kill count of the bots being part of the team.
team_get_bot_death_count                     =  452  # (team_get_bot_death_count, <destination>, <team_id>),
                                                     # Gets the current death count of the bots being part of the team.
team_set_bot_death_count                     =  453  # (team_get_bot_death_count, <destination>, <team_id>),
                                                     # Sets the death count of the bots being part of the team.
team_get_kill_count                          =  454  # (team_get_kill_count, <destination>, <team_id>),
                                                     # Get the current kill count of the team.
team_get_score                               =  455  # (team_get_score, <destination>, <team_id>),
                                                     # Get the current score of the team.
team_set_score                               =  456  # (team_set_score, <team_id>, <value>),
                                                     # Set the current score of the team.
team_set_faction                             =  457  # (team_set_faction, <team_id>, <faction_id>),
                                                     # Set the faction of the team.
team_get_faction                             =  458  # (team_get_faction, <destination>, <team_id>),
                                                     # Gets the current faction of the team.

# General scene and mission handling operations

multiplayer_clear_scene                      =  416  # (multiplayer_clear_scene),
                                                     # Restarts the game mode from the beginning (respawns all players and the 3...2...1... countdown), removing all items on the ground.
multiplayer_find_spawn_point                 =  425  # (multiplayer_find_spawn_point, <destination>, <team_no>, <examine_all_spawn_points>, <is_horseman>), 
                                                     #

# set_spawn_effector_scene_prop_kind, set_spawn_effector_scene_prop_id - this two are used in capture the flag and similar game modes to make players of a certain team tend to spawn nearer to those scene props                                                     
set_spawn_effector_scene_prop_kind           =  426  # (set_spawn_effector_scene_prop_kind, <team_no>, <scene_prop_kind_no>),
                                                     # Specifies some scene prop kind as one of the teams' spawn effector, making players of that team more likely to spawn closer to the specified effector prop instances. Use -1 to disable spawn effector for a team.
set_spawn_effector_scene_prop_id             =  427  # (set_spawn_effector_scene_prop_id, <team_no>, <scene_prop_id>),
                                                     # Specifies a single prop instance as a team's spawn effector. Different from (set_spawn_effector_scene_prop_kind) as other instances of the same scene prop will not affect player spawning.

start_multiplayer_mission                    =  470  # (start_multiplayer_mission, <mission_template_id>, <scene_id>, <started_manually>),
                                                     #

# Administrative operations and settings

kick_player                                  =  465  # (kick_player, <player_id>),
                                                     #
ban_player                                   =  466  # (ban_player, <player_id>, <value>, <player_id>),
                                                     # Official docs: set value = 1 for banning temporarily, assign 2nd player id as the administrator player id if banning is permanent
                                                     # Those values are saved into a text file
save_ban_info_of_player                      =  467  # (save_ban_info_of_player, <player_id>),
                                                     #
ban_player_using_saved_ban_info              =  468  # (ban_player_using_saved_ban_info),
                                                     #

server_add_message_to_log                    =  473  # (server_add_message_to_log, <string_id>),
                                                     #

# server_get_renaming_server_allowed, server_get_changing_game_type_allowed - both of these get the values for dedicated servers which have commands to run on the console to (dis)allowing them
server_get_renaming_server_allowed           =  475  # (server_get_renaming_server_allowed, <destination>),
                                                     # Official docs: 0-1
server_get_changing_game_type_allowed        =  476  # (server_get_changing_game_type_allowed, <destination>),
                                                     # Official docs: 0-1

server_get_combat_speed                      =  478  # (server_get_combat_speed, <destination>),
                                                     # Official docs: 0-2
                                                     # Gets the current combat speed at the server.
server_set_combat_speed                      =  479  # (server_set_combat_speed, <value>),
                                                     # Official docs: 0-2
                                                     # Unofficial: <value> is actually 0-4, going from slowest to fastest, you can see its use in module_presentations from 0 to 4
                                                     # Sets the combat speed at the server.
server_get_friendly_fire                     =  480  # (server_get_friendly_fire, <destination>),
                                                     # Gets if friendly fire is enabled (1) or not (0).
server_set_friendly_fire                     =  481  # (server_set_friendly_fire, <value>),
                                                     # Official docs: 0 = off, 1 = on
                                                     # Sets if friendly fire is enabled (1) or not (0).
server_get_control_block_dir                 =  482  # (server_get_control_block_dir, <destination>),
                                                     # Gets if control block direction at the server are 'automatic' (0) or 'by mouse movement' (1).
server_set_control_block_dir                 =  483  # (server_set_control_block_dir, <value>),
                                                     # Official docs: 0 = automatic, 1 = by mouse movement
                                                     # Sets if control block direction at the server are 'automatic' (0) or 'by mouse movement' (1).
server_set_password                          =  484  # (server_set_password, <string_id>),
                                                     # Sets the password for the server.
server_get_add_to_game_servers_list          =  485  # (server_get_add_to_game_servers_list, <destination>),
                                                     # Gets if server is added to game servers list (1) or not (0).
server_set_add_to_game_servers_list          =  486  # (server_set_add_to_game_servers_list, <value>),
                                                     # Sets if server is added to game servers list (1) or not (0).
server_get_ghost_mode                        =  487  # (server_get_ghost_mode, <destination>),
                                                     # Gets if dead players are allowed to move their camera freely (0), sticked to any player (1), sticked to team members (2), sticked to team members' view (3).
server_set_ghost_mode                        =  488  # (server_set_ghost_mode, <value>),
                                                     # Sets if dead players are allowed to move their camera freely (0), sticked to any player (1), sticked to team members (2), sticked to team members' view (3).
server_set_name                              =  489  # (server_set_name, <string_id>),
                                                     # Sets the name of the server.
server_get_max_num_players                   =  490  # (server_get_max_num_players, <destination>),
                                                     # Gets the maximum number of players allowed on the server.
server_set_max_num_players                   =  491  # (server_set_max_num_players, <value>),
                                                     # Sets the maximum number of players allowed on the server.
server_set_welcome_message                   =  492  # (server_set_welcome_message, <string_id>),
                                                     # Sets the welcome message which players can see when they join the server.
server_get_melee_friendly_fire               =  493  # (server_get_melee_friendly_fire, <destination>),
                                                     # Gets if melee friendly fire is enabled (1) or not (0).
server_set_melee_friendly_fire               =  494  # (server_set_melee_friendly_fire, <value>),
                                                     # Official docs: 0 = off, 1 = on
                                                     # Sets if melee friendly fire is enabled (1) or not (0).
server_get_friendly_fire_damage_self_ratio   =  495  # (server_get_friendly_fire_damage_self_ratio, <destination>),
                                                     # Gets the percentage of damage received by self when player hits a friend (0-100).
server_set_friendly_fire_damage_self_ratio   =  496  # (server_set_friendly_fire_damage_self_ratio, <value>),
                                                     # Official docs: 0-100
                                                     # Sets the percentage of damage received by self when player hits a friend (0-100).
server_get_friendly_fire_damage_friend_ratio =  497  # (server_get_friendly_fire_damage_friend_ratio, <destination>),
                                                     # Gets the percentage of damage received by friend when player hits a friend (0-100).
server_set_friendly_fire_damage_friend_ratio =  498  # (server_set_friendly_fire_damage_friend_ratio, <value>),
                                                     # Official docs: 0-100
                                                     # Sets the percentage of damage received by friend when player hits a friend (0-100).
server_get_anti_cheat                        =  499  # (server_get_anti_cheat, <destination>),
                                                     # Gets if valve anti cheat is enabled (1) or not (0).
server_set_anti_cheat                        =  477  # (server_set_anti_cheat, <value>),
                                                     # Official docs: 0 = off, 1 = on
                                                     # Sets if valve anti cheat is enabled (1) or not (0).

################################################################################
# [ Z25 ] REMAINING ESOTERIC STUFF (NO IDEA WHAT IT DOES)
################################################################################

  # Honestly, I have no idea what these functions could be used for. If you
  # know, please let me know ASAP! :-)

set_physics_delta_time                = 58    # (set_physics_delta_time, <fixed_value>),
                                              # Default is 0.025 (40 fps). Was deprecated on VC.
set_tooltip_text                      = 1130  # (set_tooltip_text, <string_id>),
                                              # Assigns the output text for the selected item?
ai_mesh_face_group_show_hide          = 1805  # (ai_mesh_face_group_show_hide, <group_no>, <value>), # 1 for enable, 0 for disable
                                              # Debug -- Draws the selected index of triangles/quads from the navigation graph on-screen.
auto_set_meta_mission_at_end_commited = 1305  # (auto_set_meta_mission_at_end_commited),
                                              # Returns the mission as successful by the game. Used in campaign.

################################################################################
# [ Z26 ] HARDCODED COMPILER-RELATED CODE
################################################################################

  # Do not touch this stuff unless necessary. Module System compiler needs this
  # code to correctly compile your module into format that Warband understands.

lhs_operations = [try_for_range, try_for_range_backwards, try_for_parties, try_for_agents, try_for_prop_instances, try_for_players, store_script_param_1, store_script_param_2, store_script_param, store_repeat_object, get_operation_set_version, get_global_cloud_amount, get_global_haze_amount, options_get_damage_to_player, options_get_damage_to_friends, options_get_combat_ai, options_get_campaign_ai, options_get_combat_speed, options_get_battle_size, profile_get_banner_id, get_achievement_stat, get_max_players, player_get_team_no, player_get_troop_id, player_get_agent_id, player_get_gold, multiplayer_get_my_team, multiplayer_get_my_troop, multiplayer_get_my_gold, multiplayer_get_my_player, player_get_score, player_get_kill_count, player_get_death_count, player_get_ping, player_get_is_muted, player_get_unique_id, player_get_gender, player_get_item_id, player_get_banner_id, game_get_reduce_campaign_ai, multiplayer_find_spawn_point, team_get_bot_kill_count, team_get_bot_death_count, team_get_kill_count, team_get_score, team_get_faction, player_get_value_of_original_items, server_get_renaming_server_allowed, server_get_changing_game_type_allowed, server_get_friendly_fire, server_get_control_block_dir, server_get_combat_speed, server_get_add_to_game_servers_list, server_get_ghost_mode, server_get_max_num_players, server_get_melee_friendly_fire, server_get_friendly_fire_damage_self_ratio, server_get_friendly_fire_damage_friend_ratio, server_get_anti_cheat, troop_get_slot, party_get_slot, faction_get_slot, scene_get_slot, party_template_get_slot, agent_get_slot, quest_get_slot, item_get_slot, player_get_slot, team_get_slot, scene_prop_get_slot, store_last_sound_channel, get_angle_between_positions, get_distance_between_positions, get_distance_between_positions_in_meters, get_sq_distance_between_positions, get_sq_distance_between_positions_in_meters, get_sq_distance_between_position_heights, position_get_x, position_get_y, position_get_z, position_get_scale_x, position_get_scale_y, position_get_scale_z, position_get_rotation_around_z, position_normalize_origin, position_get_rotation_around_x, position_get_rotation_around_y, position_get_distance_to_terrain, position_get_distance_to_ground_level, create_text_overlay, create_mesh_overlay, create_button_overlay, create_image_button_overlay, create_slider_overlay, create_progress_overlay, create_combo_button_overlay, create_text_box_overlay, create_check_box_overlay, create_simple_text_box_overlay, create_image_button_overlay_with_tableau_material, create_mesh_overlay_with_tableau_material, create_game_button_overlay, create_in_game_button_overlay, create_number_box_overlay, create_listbox_overlay, create_mesh_overlay_with_item_id, overlay_get_position, create_combo_label_overlay, get_average_game_difficulty, get_level_boundary, faction_get_color, troop_get_type, troop_get_xp, troop_get_class, troop_inventory_slot_get_item_amount, troop_inventory_slot_get_item_max_amount, troop_get_inventory_capacity, troop_get_inventory_slot, troop_get_inventory_slot_modifier, troop_get_upgrade_troop, item_get_type, party_get_num_companions, party_get_num_prisoners, party_get_current_terrain, party_get_template_id, party_count_members_of_type, party_count_companions_of_type, party_count_prisoners_of_type, party_get_free_companions_capacity, party_get_free_prisoners_capacity, party_get_helpfulness, party_get_ignore_with_player_party, party_get_ai_initiative, party_get_num_companion_stacks, party_get_num_prisoner_stacks, party_stack_get_troop_id, party_stack_get_size, party_stack_get_num_wounded, party_stack_get_troop_dna, party_prisoner_stack_get_troop_id, party_prisoner_stack_get_size, party_prisoner_stack_get_troop_dna, party_get_cur_town, party_get_morale, party_get_battle_opponent, party_get_icon, party_get_skill_level, get_battle_advantage, party_get_attached_to, party_get_num_attached_parties, party_get_attached_party_with_rank, get_player_agent_no, get_player_agent_kill_count, get_player_agent_own_troop_kill_count, agent_get_horse, agent_get_rider, agent_get_party_id, agent_get_entry_no, agent_get_troop_id, agent_get_item_id, store_agent_hit_points, agent_get_kill_count, agent_get_player_id, agent_get_wielded_item, agent_get_ammo, agent_get_simple_behavior, agent_get_combat_state, agent_get_attached_scene_prop, agent_get_time_elapsed_since_removed, agent_get_number_of_enemies_following, agent_get_attack_action, agent_get_defend_action, agent_get_group, agent_get_action_dir, agent_get_animation, agent_get_team, agent_get_class, agent_get_division, team_get_hold_fire_order, team_get_movement_order, team_get_riding_order, team_get_weapon_usage_order, team_get_leader, agent_get_item_slot, scene_prop_get_num_instances, scene_prop_get_instance, scene_prop_get_visibility, scene_prop_get_hit_points, scene_prop_get_max_hit_points, scene_prop_get_team, agent_get_ammo_for_slot, agent_deliver_damage_to_agent_advanced, team_get_gap_distance, scene_item_get_num_instances, scene_item_get_instance, scene_spawned_item_get_num_instances, scene_spawned_item_get_instance, prop_instance_get_variation_id, prop_instance_get_variation_id_2, prop_instance_get_position, prop_instance_get_starting_position, prop_instance_get_scale, prop_instance_get_scene_prop_kind, prop_instance_is_animating, prop_instance_get_animation_target_position, cast_ray, agent_get_item_cur_ammo, mission_get_time_speed, mission_cam_get_aperture, agent_get_damage_modifier, agent_get_accuracy_modifier, agent_get_speed_modifier, agent_get_reload_speed_modifier, agent_get_use_speed_modifier, store_trigger_param, store_trigger_param_1, store_trigger_param_2, store_trigger_param_3, agent_ai_get_look_target, agent_ai_get_move_target, agent_ai_get_behavior_target, agent_get_crouch_mode, store_or, store_and, store_mod, store_add, store_sub, store_mul, store_div, store_sqrt, store_pow, store_sin, store_cos, store_tan, assign, store_random, store_random_in_range, store_asin, store_acos, store_atan, store_atan2, store_troop_gold, store_num_free_stacks, store_num_free_prisoner_stacks, store_party_size, store_party_size_wo_prisoners, store_troop_kind_count, store_num_regular_prisoners, store_troop_count_companions, store_troop_count_prisoners, store_main_party_wounded, store_item_kind_count, store_free_inventory_capacity, store_skill_level, store_character_level, store_attribute_level, store_troop_faction, store_troop_health, store_proficiency_level, store_relation, store_conversation_agent, store_conversation_troop, store_partner_faction, store_encountered_party, store_encountered_party2, store_faction_of_party, store_current_scene, store_zoom_amount, store_item_value, store_troop_value, store_partner_quest, store_random_quest_in_range, store_random_troop_to_raise, store_random_troop_to_capture, store_random_party_in_range, store_random_horse, store_random_equipment, store_random_armor, store_quest_number, store_quest_item, store_quest_troop, store_current_hours, store_time_of_day, store_current_day, store_distance_to_party_from_party, get_party_ai_behavior, get_party_ai_object, get_party_ai_current_behavior, get_party_ai_current_object, store_num_parties_created, store_num_parties_destroyed, store_num_parties_destroyed_by_player, store_num_parties_of_template, store_random_party_of_template, store_remaining_team_no, store_mission_timer_a_msec, store_mission_timer_b_msec, store_mission_timer_c_msec, store_mission_timer_a, store_mission_timer_b, store_mission_timer_c, store_enemy_count, store_friend_count, store_ally_count, store_defender_count, store_attacker_count, store_normalized_team_count, prop_instance_get_current_deform_progress, prop_instance_get_current_deform_frame, agent_ai_get_num_cached_enemies, agent_ai_get_cached_enemy, item_get_weight, item_get_value, item_get_difficulty, item_get_head_armor, item_get_body_armor, item_get_leg_armor, item_get_hit_points, item_get_weapon_length, item_get_speed_rating, item_get_missile_speed, item_get_max_ammo, item_get_accuracy, item_get_shield_height, item_get_horse_scale, item_get_horse_speed, item_get_horse_maneuver, item_get_food_quality, item_get_abundance, item_get_thrust_damage, item_get_thrust_damage_type, item_get_swing_damage, item_get_swing_damage_type, item_get_horse_charge_damage, get_startup_sun_light, get_startup_ambient_light, get_startup_ground_ambient_light, face_keys_get_hair, face_keys_get_beard, face_keys_get_face_texture, face_keys_get_hair_texture, face_keys_get_hair_color, face_keys_get_age, face_keys_get_skin_color, face_keys_get_morph_key
# add_missile, MOTO causes local variable unused warnings? 
]

global_lhs_operations = [val_lshift, val_rshift, val_add, val_sub, val_mul, val_div, val_max, val_min, val_mod ]

can_fail_operations = [ge, eq, gt, is_between, entering_town, map_free, encountered_party_is_attacker, conversation_screen_is_active, in_meta_mission, troop_is_hero, troop_is_wounded, key_is_down, key_clicked, game_key_is_down, game_key_clicked, hero_can_join, hero_can_join_as_prisoner, party_can_join, party_can_join_as_prisoner, troops_can_join, troops_can_join_as_prisoner, party_can_join_party, main_party_has_troop, party_is_in_town, party_is_in_any_town, party_is_active, player_has_item, troop_has_item_equipped, troop_is_mounted, troop_is_guarantee_ranged, troop_is_guarantee_horse, player_is_active, multiplayer_is_server, multiplayer_is_dedicated_server, game_in_multiplayer_mode, player_is_admin, player_is_busy_with_menus, player_item_slot_is_picked_up, check_quest_active, check_quest_finished, check_quest_succeeded, check_quest_failed, check_quest_concluded, is_trial_version, is_edit_mode_enabled, is_cheat_mode_enabled, troop_slot_eq, party_slot_eq, faction_slot_eq, scene_slot_eq, party_template_slot_eq, agent_slot_eq, quest_slot_eq, item_slot_eq, player_slot_eq, team_slot_eq, scene_prop_slot_eq, troop_slot_ge, party_slot_ge, faction_slot_ge, scene_slot_ge, party_template_slot_ge, agent_slot_ge, quest_slot_ge, item_slot_ge, player_slot_ge, team_slot_ge, scene_prop_slot_ge, position_has_line_of_sight_to_position, position_is_behind_position, is_presentation_active, all_enemies_defeated, race_completed_by_player, num_active_teams_le, main_hero_fallen, lt, neq, le, teams_are_enemies, agent_is_alive, agent_is_wounded, agent_is_human, agent_is_ally, agent_is_non_player, agent_is_defender, agent_is_active, agent_is_routed, agent_is_in_special_mode, agent_is_in_parried_animation, class_is_listening_order, agent_check_offer_from_agent, entry_point_is_auto_generated, scene_prop_has_agent_on_it, agent_is_alarmed, agent_is_in_line_of_sight, scene_prop_get_instance, scene_item_get_instance, scene_allows_mounted_units, prop_instance_is_valid, cast_ray, prop_instance_intersects_with_prop_instance, agent_has_item_equipped, map_get_land_position_around_position, map_get_water_position_around_position, mission_tpl_are_all_agents_spawned, is_zoom_disabled, is_currently_night, store_random_party_of_template, str_is_empty, item_has_property, item_has_capability, item_has_modifier, item_has_faction ] 


#Add the following definitions to the end (!) of header_operations.py
break_loop                   = 8 #(break_loop), #Break out of a loop, no matter how deeply nested in try_begin blocks
continue_loop                = 9 #(continue_loop), #Continue to the next iteration of a loop, no matter how deeply nested in try_begin blocks
try_for_agents               = 12 #(try_for_agents, <cur_agent_no>, [<position_no>], [<radius_fixed_point>], [<use_mission_grid>]), #Loops through agents in the scene. If [<position_no>] and [<radius_fixed_point>] are defined, it will only loop through agents in the chosen area. If [<use_mission_grid>] is non-zero, it will use mission grid iterator instead of searching through all agents. This is better in performance, but does not take into account the height of positions
try_for_dict_keys            = 18 #(try_for_dict_keys, <cur_key_string_register>, <dict>), #Loops through keys of <2>
key_is_down                  = 70 #(key_is_down, <key>, [<bypass_console_check>]), #Fails if <key> is not currently down
key_clicked                  = 71 #(key_clicked, <key>, [<bypass_console_check>]), #Fails if <key> is not clicked on the specific frame
game_key_is_down             = 72 #(game_key_is_down, <game_key_no>, [<bypass_console_check>]), #Fails if <game_key_no> is not currently down
game_key_clicked             = 73 #(game_key_clicked, <game_key_no>, [<bypass_console_check>]), #Fails if <game_key_no> is not clicked on the specific frame
server_set_max_num_players   = 491 #(server_set_max_num_players, <max_players>, [<max_private_players>]), #Sets maximum players to <max_players> and maximum private players to [<max_private_players>] (default = same as <max_players>). Both values must be in the range 2-250, [<max_private_players>] can't be lower than <max_players>
position_rotate_x            = 723 #(position_rotate_x, <position_register>, <angle>, [<use_global_axis>]), #Rotates <position_register> around the x-axis by <angle> degrees
position_rotate_y            = 724 #(position_rotate_y, <position_register>, <angle>, [<use_global_axis>]), #Rotates <position_register> around the y-axis by <angle> degrees
position_rotate_z            = 725 #(position_rotate_z, <position_register>, <angle>, [<use_global_axis>]), #Rotates <position_register> around the z-axis by <angle> degrees
position_rotate_z_floating   = 734 #(position_rotate_z_floating, <position_register>, <angle_fixed_point>, [<use_global_axis>]), #Rotates <position_register> around the z-axis by <angle_fixed_point> degrees
position_rotate_x_floating   = 738 #(position_rotate_x_floating, <position_register>, <angle_fixed_point>, [<use_global_axis>]), #Rotates <position_register> around the x-axis by <angle_fixed_point> degrees
position_rotate_y_floating   = 739 #(position_rotate_y_floating, <position_register>, <angle_fixed_point>, [<use_global_axis>]), #Rotates <position_register> around the y-axis by <angle_fixed_point> degrees
is_vanilla_warband           = 1004 #(is_vanilla_warband), #Fails only when WSE is running
start_map_conversation       = 1025 #(start_map_conversation, <troop_id>, [<troop_dna>], [<set_dialog_state>], [<dialog_state>]), #Starts a conversation with the selected <troop_id>. Can be called directly from global map or game menus. [<troop_dna>] parameter allows you to randomize non-hero troop appearances. If [<set_dialog_state>] sets, then [<dialog_state>] used instead dlg_event_triggered
agent_set_animation_progress = 1743 #(agent_set_animation_progress, <agent_no>, <value_fixed_point>, [<channel_no>]), #Sets <agent_no>'s channel [<channel_no>] animation progress to <value_fixed_point>
prop_instance_receive_damage = 1877 #(prop_instance_receive_damage, <prop_instance_no>, <agent_no>, <damage>, [<advanced>]), #<prop_instance_no> received <damage> damage from <agent_no>. If [<advanced>] is non-zero ti_on_scene_prop_hit will be called and the damage dealt will be sent to clients.
add_point_light              = 1960 #(add_point_light, [<flicker_magnitude>], [<flicker_interval>], [<range>]), #Adds a point light with [<flicker_magnitude>] and [<flicker_interval>] ([<range>] if set - in meters)
add_point_light_to_entity    = 1961 #(add_point_light_to_entity, [<flicker_magnitude>], [<flicker_interval>], [<range>]), #Adds a point light to entity with [<flicker_magnitude>] and [<flicker_interval>] ([<range>] if set - in meters)

val_shr    = 2800 #(val_shr, <value>, <shift>), #Performs an arithmetic right bit shift by <shift> on <value>
store_shr  = 2801 #(store_shr, <destination>, <value>, <shift>), #Performs an arithmetic right bit shift by <shift> on <value> and stores the result into <destination>
val_lshr   = 2802 #(val_lshr, <value>, <shift>), #Performs a logical right bit shift by <shift> on <value>
store_lshr = 2803 #(store_lshr, <destination>, <value>, <shift>), #Performs a logical right bit shift by <shift> on <value> and stores the result into <destination>
val_shl    = 2804 #(val_shl, <value>, <shift>), #Performs a left bit shift by <shift> on <value>
store_shl  = 2805 #(store_shl, <destination>, <value>, <shift>), #Performs a left bit shift by <shift> on <value> and stores the result into <destination>
val_xor    = 2806 #(val_xor, <value1>, <value2>), #Performs a bitwise exclusive or between <value1> and <value2>
store_xor  = 2807 #(store_xor, <destination>, <value1>, <value2>), #Performs a bitwise exclusive or between <value1> and <value2> and stores the result into <destination>
val_not    = 2808 #(val_not, <value>), #Performs a bitwise complement on <value>
store_not  = 2809 #(store_not, <destination>, <value>), #Performs a bitwise complement on <value> and stores the result into <destination>

player_set_skin               = 2900 #(player_set_skin, <player_no>, <skin_no>), #Sets <player_no>'s skin (gender) to <skin_no> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
player_stop_controlling_agent = 2901 #(player_stop_controlling_agent, <player_no>), #Gives <player_no>'s agent back to AI control (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
player_set_banner_id          = 2902 #(player_set_banner_id, <player_no>, <banner_no>), #Sets <player_no>'s banner to <banner_no>
player_set_username           = 2903 #(player_set_username, <player_no>, <string_no>), #Sets <player_no>'s username to <string_no>
player_temp_ban               = 2904 #(player_temp_ban, <player_no>, <ban_time>), #Bans <player_no> temporarily for <ban_time> seconds
player_get_wse2_version       = 2905 #(player_get_wse2_version, <destination>, <player_no>), #Stores <player_no>'s WSE2 version into <destination>. Works only on servers. 0 - vanilla Warband engine (requires WSE2)
player_get_party_id           = 2906 #(player_get_party_id, <destination>, <player_no>), #Stores <player_no>'s party reference into <destination>. For multiplayer campaign mode (requires WSE2)
player_set_party_id           = 2907 #(player_set_party_id, <player_no>, <party_no>), #Sets <player_no>'s party to <party_no>. For multiplayer campaign mode (requires WSE2)

register_get                      = 3000 #(register_get, <destination>, <index>), #Stores the value of register <index> into <destination>
register_set                      = 3001 #(register_set, <index>, <value>), #Sets the value of register <index> to <value>
store_wse_version                 = 3002 #(store_wse_version, <destination>, <component>), #Stores <component> of the WSE version (0: major, 1: minor, 2: build) version into <destination>
item_slot_gt                      = 3003 #(item_slot_gt, <item_kind_no>, <slot_no>, <value>), #Fails if <item_kind_no>'s <slot_no> is not greater than <value>
party_template_slot_gt            = 3004 #(party_template_slot_gt, <party_template_no>, <slot_no>, <value>), #Fails if <party_template_no>'s <slot_no> is not greater than <value>
troop_slot_gt                     = 3005 #(troop_slot_gt, <troop_no>, <slot_no>, <value>), #Fails if <troop_no>'s <slot_no> is not greater than <value>
faction_slot_gt                   = 3006 #(faction_slot_gt, <faction_no>, <slot_no>, <value>), #Fails if <faction_no>'s <slot_no> is not greater than <value>
quest_slot_gt                     = 3007 #(quest_slot_gt, <quest_no>, <slot_no>, <value>), #Fails if <quest_no>'s <slot_no> is not greater than <value>
scene_slot_gt                     = 3008 #(scene_slot_gt, <site_no>, <slot_no>, <value>), #Fails if <site_no>'s <slot_no> is not greater than <value>
party_slot_gt                     = 3009 #(party_slot_gt, <party_no>, <slot_no>, <value>), #Fails if <party_no>'s <slot_no> is not greater than <value>
player_slot_gt                    = 3010 #(player_slot_gt, <player_no>, <slot_no>, <value>), #Fails if <player_no>'s <slot_no> is not greater than <value>
team_slot_gt                      = 3011 #(team_slot_gt, <team_no>, <slot_no>, <value>), #Fails if <team_no>'s <slot_no> is not greater than <value>
agent_slot_gt                     = 3012 #(agent_slot_gt, <agent_no>, <slot_no>, <value>), #Fails if <agent_no>'s <slot_no> is not greater than <value>
scene_prop_slot_gt                = 3013 #(scene_prop_slot_gt, <prop_instance_no>, <slot_no>, <value>), #Fails if <prop_instance_no>'s <slot_no> is not greater than <value>
store_current_trigger             = 3014 #(store_current_trigger, <destination>), #Stores the current trigger into <destination> (0 if not in a trigger)
return_values                     = 3015 #(return_values, [<value_1>], [<value_2>], [<value_3>], [<value_4>], [<value_5>], [<value_6>], [<value_7>], [<value_8>], [<value_9>], [<value_10>], [<value_11>], [<value_12>], [<value_13>], [<value_14>], [<value_15>], [<value_16>]), #Stores up to 16 return values
store_num_return_values           = 3016 #(store_num_return_values, <destination>), #Stores the amount of return values available into <destination>
store_return_value                = 3017 #(store_return_value, <destination>, [<value>]), #Stores return value no. [<value>] into <destination>
set_forced_lod                    = 3018 #(set_forced_lod, <lod_level>), #Forces the current trigger entity's LOD level to <lod_level> (0 = auto)
send_message_to_url_advanced      = 3019 #(send_message_to_url_advanced, <url_string>, <user_agent_string>, [<success_callback_script_no>], [<failure_callback_script_no>], [<skip_parsing>], [<timeout>]), #Sends a HTTP request to <url_string> with <user_agent_string>. If the request succeeds, [<success_callback_script_no>] will be called. The script will behave like game_receive_url_response, unless [<skip_parsing>] is non-zero, in which case the script will receive no arguments and s0 will contain the full response. If the request fails, [<failure_callback_script_no>] will be called.
mtsrand                           = 3020 #(mtsrand, <value>), #Seeds the MT19937 random generator with <value>
mtrand                            = 3021 #(mtrand, <destination>, <min>, <max>), #Stores a random value between <min> and <max> into <destination> using the MT19937 random generator
get_time                          = 3022 #(get_time, <destination>, [<local>]), #Stores the current UNIX time into <destination>. If [<local>] is non-zero, it will store local time instead of universal time.
order_flag_is_active              = 3023 #(order_flag_is_active), #Fails if the order flag is not being placed
play_bink_file                    = 3024 #(play_bink_file, <path_from_module_directory>, [<duration_in_ms>]), #Plays a .bik file located at <path_from_module_directory>. If [<duration_in_ms>] is not set the full movie will be played
process_advanced_url_messages     = 3025 #(process_advanced_url_messages), #Forces processing of URL messages sent with send_message_to_url_advanced
sleep_ms                          = 3026 #(sleep_ms, <time>), #Sleeps (blocking the game) for <time> ms
timer_reset                       = 3027 #(timer_reset, <timer_register_no>, [<use_game_time>]), #Resets <timer_register_no>. If [<use_game_time>] is non-zero the timer will count game time rather than mission time
timer_get_elapsed_time            = 3028 #(timer_get_elapsed_time, <destination>, <timer_register_no>), #Stores <timer_register_no>'s elapsed time into <destination>
shell_open_url                    = 3029 #(shell_open_url, <url>), #Opens <url> in default browser. Support only http://, https://, ftp:// and ts3server:// urls.
set_main_party                    = 3030 #(set_main_party, <party_no>), #Sets player's main party to <party_no>. Dynamic spawned party (not listed in module_parties.py) will corrupt the savegame!
get_main_party                    = 3031 #(get_main_party, <destination>), #Stores player's main party to <destination>
make_screenshot                   = 3032 #(make_screenshot, <format>, <file>), #Make game screenshot. For security reasons, <file> will be saved into a Screenshots directory. Supported <format>s: BMP - 0, JPG - 1, TGA - 2, PNG - 3.
send_post_message_to_url_advanced = 3033 #(send_post_message_to_url_advanced, <url_string>, <user_agent_string>, <post_data>, [<success_callback_script_no>], [<failure_callback_script_no>], [<skip_parsing>], [<timeout>]), #Sends a HTTP POST (application/x-www-form-urlencoded) request to <url_string> with <user_agent_string> and <post_data>. If the request succeeds, [<success_callback_script_no>] will be called. The script will behave like game_receive_url_response, unless [<skip_parsing>] is non-zero, in which case the script will receive no arguments and s0 will contain the full response. If the request fails, [<failure_callback_script_no>] will be called.
set_random_seed                   = 3034 #(set_random_seed, <value>), #Seeds the random generator with <value>
store_application_time            = 3035 #(store_application_time, <destination>), #Stores application time into <destination> in milliseconds
is_party_skill                    = 3036 #(is_party_skill, <skill_no>), #Fails if <skill_no> is not effects party
get_campaign_time                 = 3037 #(get_campaign_time, <destination>), #Stores campaign time into <destination>. 100000 = 1 game hour
set_campaign_time                 = 3038 #(set_campaign_time, <value>), #Sets campaign time to <value>. 100000 = 1 game hour
get_mouse_map_coordinates         = 3039 #(get_mouse_map_coordinates, <position_register>), #Stores mouse map coordinates into <position_register> (requires WSE2)
profiler_start                    = 3040 #(profiler_start), #Start the profiler
profiler_stop                     = 3041 #(profiler_stop), #Stop the profiler
profiler_is_recording             = 3042 #(profiler_is_recording), #Fails if profiler isn't recording
profiler_mark                     = 3043 #(profiler_mark, <string_1>), #Add a marker at this point in time with name <string_1>. Good for analyzing individual parts of a script.

game_key_get_key  = 3100 #(game_key_get_key, <destination>, <game_key_no>), #Stores the key mapped to <game_key_no> into <destination>
key_released      = 3101 #(key_released, <key>, [<bypass_console_check>]), #Fails if <key> wasn't released in the current frame
game_key_released = 3102 #(game_key_released, <game_key_no>, [<bypass_console_check>]), #Fails if <game_key_no> wasn't released in the current frame

dict_create                = 3200 #(dict_create, <destination>), #Creates an empty dictionary object and stores it into <destination>
dict_free                  = 3201 #(dict_free, <dict>), #Frees the dictionary object <dict>. A dictionary can't be used after freeing it
dict_load_file             = 3202 #(dict_load_file, <dict>, <file>, [<mode>], [<ini>]), #Loads a dictionary file into <dict>. Setting [<mode>] to 0 (default) clears <dict> and then loads the file, setting [<mode>] to 1 doesn't clear <dict> but overrides any key that's already present, [<mode>] to 2 doesn't clear <dict> and doesn't overwrite keys that are already present. Set [<ini>] to 1 to use ini file instead of binary
dict_load_dict             = 3203 #(dict_load_dict, <dict_1>, <dict_2>, [<mode>]), #Loads <dict_2> into <dict_1>. [<mode>]: see above
dict_save                  = 3204 #(dict_save, <dict>, <file>, [<ini>]), #Saves <dict> into a file. For security reasons, <file> is just a name, not a full path, and will be stored into a WSE managed directory. Set [<ini>] to 1 to use ini file instead of binary
dict_clear                 = 3205 #(dict_clear, <dict>), #Clears all key-value pairs from <dict>
dict_is_empty              = 3206 #(dict_is_empty, <dict>), #Fails if <dict> is not empty
dict_has_key               = 3207 #(dict_has_key, <dict>, <key>), #Fails if <key> is not present in <dict>
dict_get_size              = 3208 #(dict_get_size, <destination>, <dict>), #Stores the count of key-value pairs in <dict> into <destination>
dict_delete_file           = 3209 #(dict_delete_file, <file>, [<ini>]), #Deletes dictionary file <file> from disk. Set [<ini>] to 1 to use ini file instead of binary
dict_get_str               = 3210 #(dict_get_str, <string_register>, <dict>, <key>, [<default>]), #Stores the string value paired to <key> into <string_register>. If the key is not found and [<default>] is set, [<default>] will be stored instead. If [<default>] is not set, an empty string will be stored
dict_get_int               = 3211 #(dict_get_int, <destination>, <dict>, <key>, [<default>]), #Stores the numeric value paired to <key> into <destination>. If the key is not found and [<default>] is set, [<default>] will be stored instead. If [<default>] is not set, 0 will be stored
dict_set_str               = 3212 #(dict_set_str, <dict>, <key>, <string_no>), #Adds (or changes) <string_no> as the string value paired to <key>
dict_set_int               = 3213 #(dict_set_int, <dict>, <key>, <value>), #Adds (or changes) <value> as the numeric value paired to <key>
dict_get_key_by_iterator   = 3214 #(dict_get_key_by_iterator, <string_register>, <dict>, <iterator>), #Stores the key <string_register> by iterator <iterator>
dict_get_pos               = 3215 #(dict_get_pos, <position_register>, <dict>, <key>, [<default_position_register>]), #Stores the position paired to <key> into <position_register>. If the key is not found and [<default_position_register>] is set, [<default_position_register>] will be stored instead. If [<default_position_register>] is not set, (x:0,y:0,z:0,rotX:0,rotY:0,rotZ:0) will be stored
dict_set_pos               = 3216 #(dict_set_pos, <dict>, <key>, <position_register>), #Adds (or changes) <position_register> as the position value paired to <key>
dict_load_file_json        = 3217 #(dict_load_file_json, <dict>, <file>, [<mode>]), #Loads a dictionary json file into <dict>. [<mode>]: see above
dict_save_json             = 3218 #(dict_save_json, <dict>, <file>), #Saves <dict> into a json file. For security reasons, <file> is just a name, not a full path, and will be stored into a WSE managed directory
dict_from_url_encoded_json = 3219 #(dict_from_url_encoded_json, <dict>, <string>, [<mode>]), #Loads a url encoded json <string> into <dict>. [<mode>]: see above
dict_to_url_encoded_json   = 3220 #(dict_to_url_encoded_json, <string_register>, <dict>), #Saves <dict> into a url encoded json and stores into <string_register>
dict_erase                 = 3221 #(dict_erase, <dict>, <key>), #Removes value from <dict> paired to <key>
dict_delete_file_json      = 3222 #(dict_delete_file_json, <file>), #Deletes dictionary json file <file> from disk

agent_get_item_modifier                          = 3300 #(agent_get_item_modifier, <destination>, <agent_no>), #Stores <agent_no>'s horse item modifier (-1 if agent is not a horse) into <destination>
agent_get_item_slot_modifier                     = 3301 #(agent_get_item_slot_modifier, <destination>, <agent_no>, <item_slot_no>), #Stores <agent_no>'s <item_slot_no> modifier into <destination>
agent_get_animation_progress                     = 3302 #(agent_get_animation_progress, <destination>, <agent_no>, [<channel_no>]), #Stores <agent_no>'s channel [<channel_no>] animation progress (in %%) into <destination>
agent_get_dna                                    = 3303 #(agent_get_dna, <destination>, <agent_no>), #Stores <agent_no>'s dna into <destination>
agent_get_ground_scene_prop                      = 3304 #(agent_get_ground_scene_prop, <destination>, <agent_no>), #Stores the prop instance on which <agent_no> is standing into <destination>
agent_set_item_slot_ammo                         = 3305 #(agent_set_item_slot_ammo, <agent_no>, <item_slot_no>, <value>), #Sets <agent_no>'s <item_slot_no> ammo count to <value>
agent_get_item_slot_hit_points                   = 3306 #(agent_get_item_slot_hit_points, <destination>, <agent_no>, <item_slot_no>), #Stores <agent_no>'s <item_slot_no> shield hitpoints into <destination>
agent_set_item_slot_hit_points                   = 3307 #(agent_set_item_slot_hit_points, <agent_no>, <item_slot_no>, <value>), #Sets <agent_no>'s <item_slot_no> shield hitpoints to <value>
agent_get_wielded_item_slot_no                   = 3308 #(agent_get_wielded_item_slot_no, <destination>, <agent_no>, [<hand_no>]), #Stores <agent_no>'s wielded item slot for [<hand_no>] into <destination>
agent_get_scale                                  = 3309 #(agent_get_scale, <destination_fixed_point>, <agent_no>), #Stores <agent_no>'s scale into <destination_fixed_point>
agent_set_forced_lod                             = 3310 #(agent_set_forced_lod, <agent_no>, <lod_level>), #Forces <agent_no>'s LOD level to <lod_level> (0 = auto)
agent_get_item_slot_flags                        = 3311 #(agent_get_item_slot_flags, <destination>, <agent_no>, <item_slot_no>), #Stores <agent_no>'s <item_slot_no> item slot flags into <destination>
agent_ai_get_move_target_position                = 3312 #(agent_ai_get_move_target_position, <position_register>, <agent_no>), #Stores <agent_no>'s move target position agent into <position_register>
agent_set_horse                                  = 3313 #(agent_set_horse, <agent_no>, <horse_agent_no>), #Sets <agent_no>'s horse to <horse_agent_no> (-1 for no horse)
agent_ai_set_simple_behavior                     = 3314 #(agent_ai_set_simple_behavior, <agent_no>, <simple_behavior>, [<guaranteed_time>]), #Sets <agent_no>'s behavior to <simple_behavior> and guarantees it won't be changed for [<guaranteed_time>] seconds. If [<guaranteed_time>] is not specified or <= 0, it won't be changed until agent_force_rethink is called
agent_accelerate                                 = 3315 #(agent_accelerate, <agent_no>, <position_register_no>, [<movement_timer_fixed_point>]), #Uses x, y, z components of <position_register_no> to apply acceleration to <agent_no>. Specify [<movement_timer_fixed_point>] for ghosting time
agent_set_item_slot_modifier                     = 3316 #(agent_set_item_slot_modifier, <agent_no>, <item_slot_no>, <item_modifier_no>), #Sets <agent_no>'s <item_slot_no> modifier to <item_modifier_no>
agent_body_meta_mesh_set_vertex_keys_time_point  = 3317 #(agent_body_meta_mesh_set_vertex_keys_time_point, <agent_no>, <body_meta_mesh>, <time_point>), #Sets <agent_no>'s <body_meta_mesh> vertex keys time point to <time_point>
agent_body_meta_mesh_set_visibility              = 3318 #(agent_body_meta_mesh_set_visibility, <agent_no>, <body_meta_mesh>, <value>), #Shows (<value> = 1) or hides (<value> = 0) <agent_no>'s <body_meta_mesh>
agent_set_personal_animation                     = 3319 #(agent_set_personal_animation, <agent_no>, <anim_no>, <anim_no>), #Replaces <agent_no>'s default <anim_no> to personal <anim_no>
agent_get_personal_animation                     = 3320 #(agent_get_personal_animation, <destination>, <agent_no>, <anim_no>), #Stores <agent_no>'s personal <anim_no> into <destination>
agent_set_default_animations                     = 3321 #(agent_set_default_animations, <agent_no>), #Removes <agent_no>'s personal animations
agent_cancel_current_animation                   = 3322 #(agent_cancel_current_animation, <agent_no>, <channel_no>), #Cancels <agent_no>'s channel <2> animation
agent_get_ranged_damage_modifier                 = 3323 #(agent_get_ranged_damage_modifier, <destination>, <agent_no>), #Stores <agent_no>'s ranged damage modifier into <destination>
agent_add_stun                                   = 3324 #(agent_add_stun, <agent_no>, <duration>), #Adds stun to <agent_no> for <duration> milliseconds
agent_body_meta_mesh_deform_in_range             = 3325 #(agent_body_meta_mesh_deform_in_range, <agent_no>, <body_meta_mesh>, <start_frame>, <end_frame>, <time_period>), #Animates <agent_no>'s <body_meta_mesh> from <start_frame> to <end_frame> within the specified <time_period> (in milliseconds)
agent_body_meta_mesh_deform_in_cycle_loop        = 3326 #(agent_body_meta_mesh_deform_in_cycle_loop, <agent_no>, <body_meta_mesh>, <start_frame>, <end_frame>, <time_period>), #Performs looping animation of  <agent_no>'s <body_meta_mesh> from <start_frame> to <end_frame> and within the specified <time_period> (in milliseconds)
agent_body_meta_mesh_get_current_deform_progress = 3327 #(agent_body_meta_mesh_get_current_deform_progress, <destination>, <agent_no>, <body_meta_mesh>), #Stores <agent_no>'s <body_meta_mesh> deform progress percentage value between 0 and 100 if animation is still in progress into <destination>. Returns 100 otherwise
agent_body_meta_mesh_get_current_deform_frame    = 3328 #(agent_body_meta_mesh_get_current_deform_frame, <destination>, <agent_no>, <body_meta_mesh>), #Stores <agent_no>'s <body_meta_mesh> current deform frame, rounded to nearest integer value, into <destination>
agent_set_footstep_sound                         = 3329 #(agent_set_footstep_sound, <agent_no>, <type>, <sound_no>), #Sets <agent_no>'s footstep <sound_no> for <type>. For human type: 0 - water, 1 - indoors, 2 - outdoors. For horse type: 0 - water, 1 - walk, 2 - trot, 3 - canter, 4 - gallop. For mute use sound_no = -1
agent_get_horse_rotation_velocity                = 3330 #(agent_get_horse_rotation_velocity, <destination_fixed_point>, <agent_no>), #Stores <agent_no>'s horse rotation velocity into <destination_fixed_point>
agent_get_current_vertical_speed                 = 3331 #(agent_get_current_vertical_speed, <destination>, <agent_no>), #Stores <agent_no>'s current vertical speed into <destination> (in centimeters per second)
agent_set_current_vertical_speed                 = 3332 #(agent_set_current_vertical_speed, <agent_no>, <value>), #Sets <agent_no>'s current vertical speed to <value> (in centimeters per second)
agent_get_position_in_group                      = 3333 #(agent_get_position_in_group, <position_register>, <agent_no>), #Stores <agent_no>'s position in group into <position_register> (requires WSE2)
agent_get_current_ai_mesh_face_group             = 3334 #(agent_get_current_ai_mesh_face_group, <destination>, <agent_no>), #Stores <agent_no>'s current ai mesh face group into <destination> (requires WSE2)
agent_set_time_speed_multiplier                  = 3335 #(agent_set_time_speed_multiplier, <agent_no>, <value_fixed_point>), #Sets <agent_no>'s time speed multiplier to <value_fixed_point> (requires WSE2)
agent_get_time_speed_multiplier                  = 3336 #(agent_get_time_speed_multiplier, <destination_fixed_point>, <agent_no>), #Stores <agent_no>'s time speed multiplier into <destination_fixed_point> (requires WSE2)
agent_kick                                       = 3337 #(agent_kick, <agent_no>), #AI <agent_no> performs kick (requires WSE2)
agent_set_dropped_items_prune_time               = 3338 #(agent_set_dropped_items_prune_time, <agent_no>, <value>), #Sets <agent_no>'s dropped items prune time to <value> (requires WSE2)
agent_set_missile_items_prune_time               = 3339 #(agent_set_missile_items_prune_time, <agent_no>, <value>), #Sets <agent_no>'s missile items prune time to <value> (requires WSE2)
agent_set_action_speed_modifier                  = 3340 #(agent_set_action_speed_modifier, <agent_no>, <value>), #Sets <agent_no>'s action speed modifier to <value> (requires WSE2)
agent_get_action_speed_modifier                  = 3341 #(agent_get_action_speed_modifier, <destination>, <agent_no>), #Stores <agent_no>'s action speed modifier into <destination> (requires WSE2)
agent_set_left_hand_weapon_collision             = 3342 #(agent_set_left_hand_weapon_collision, <agent_no>, <value>), #Enables or disables <agent_no>'s left hand weapon collision (requires WSE2)

multiplayer_send_chat_message_to_player      = 3400 #(multiplayer_send_chat_message_to_player, <player_no>, <sender_player_no>, <text>, [<type>]), #Sends <text> to <player_no> as a (native compatible) chat message by <sender_player_no>. Works only on servers. [<type>]: 0 = chat, 1 = team chat
multiplayer_send_composite_message_to_player = 3401 #(multiplayer_send_composite_message_to_player, <player_no>, <message_type>, <message_register>), #Sends <message_register> with <message_type> to <player_no> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_send_composite_message_to_server = 3402 #(multiplayer_send_composite_message_to_server, <message_type>, <message_register>), #Sends <message_register> with <message_type> to the server (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_get_cur_profile                  = 3403 #(multiplayer_get_cur_profile, <destination>), #Stores the current multiplayer profile into <destination>
multiplayer_get_num_profiles                 = 3404 #(multiplayer_get_num_profiles, <destination>), #Stores the number of multiplayer profiles into <destination>
multiplayer_message_init                     = 3405 #(multiplayer_message_init, <message_register>), #Initializes (empties) <message_register> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_message_put_string               = 3406 #(multiplayer_message_put_string, <message_register>, <string>), #Puts <string> into <message_register> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_message_put_int                  = 3407 #(multiplayer_message_put_int, <message_register>, <value>, [<num_bits>]), #Puts [<num_bits>] of <value> into <message_register> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_message_put_position             = 3408 #(multiplayer_message_put_position, <message_register>, <position_register>, [<local>]), #Puts <position_register> into <9>. Set [<local>] to non-zero for small, relative positions (default: scene positions) (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_message_put_coordinate           = 3409 #(multiplayer_message_put_coordinate, <message_register>, <position_register>, [<local>]), #Puts x, y, z coordinates from <position_register> into <message_register>. Set [<local>] to non-zero for small, relative positions (default: scene positions) (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_cur_message_get_string           = 3410 #(multiplayer_cur_message_get_string, <string_register>), #Stores a string from the current message register into <string_register> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_cur_message_get_int              = 3411 #(multiplayer_cur_message_get_int, <destination>, [<num_bits>]), #Stores [<num_bits>] of an int from the current message register into <destination>. [<num_bits>] MUST match the number of bits sent (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_cur_message_get_position         = 3412 #(multiplayer_cur_message_get_position, <position_register>, [<local>]), #Stores a position from the current message register into <position_register>. [<local>] MUST match the type sent (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_cur_message_get_coordinate       = 3413 #(multiplayer_cur_message_get_coordinate, <position_register>, [<local>]), #Stores x, y, z coordinates from the current message register into <position_register>. [<local>] MUST match the type sent (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
multiplayer_cur_profile_get_skin             = 3414 #(multiplayer_cur_profile_get_skin, <destination>), #Stores current profile's skin into <destination>
multiplayer_connect_to_server                = 3415 #(multiplayer_connect_to_server, <address>, <password>, [<campaign>]), #Connect to server with <address> and <password>. Set [<campaign>] to non-zero for connect to multiplayer campaign server. (requires WSE2)
multiplayer_is_campaign                      = 3416 #(multiplayer_is_campaign), #Checks that the code is running on multiplayer campaign mode. (requires WSE2)

server_set_password_admin      = 3500 #(server_set_password_admin, <password>), #Sets <password> as server administrator password
server_set_password_private    = 3501 #(server_set_password_private, <password>), #Sets <password> as server private player password
server_map_rotation_get_count  = 3502 #(server_map_rotation_get_count, <destination>), #Stores the number of maps in rotation into <destination>
server_map_rotation_get_index  = 3503 #(server_map_rotation_get_index, <destination>), #Stores the current map rotation index into <destination>
server_map_rotation_set_index  = 3504 #(server_map_rotation_set_index, <index>), #Sets the current rotation index to <index>
server_map_rotation_get_map    = 3505 #(server_map_rotation_get_map, <destination>, <index>), #Stores the map at <index> into <destination>
server_map_rotation_add_map    = 3506 #(server_map_rotation_add_map, <site_no>, [<index>]), #Adds <site_no> to the map rotation at [<index>]
server_map_rotation_remove_map = 3507 #(server_map_rotation_remove_map, [<index>]), #Removes the map at [<index>] from the map rotation (does not work when only one left)
server_get_horse_friendly_fire = 3508 #(server_get_horse_friendly_fire, <destination>), #Stores horse friendly fire status into <destination> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
server_set_horse_friendly_fire = 3509 #(server_set_horse_friendly_fire, <value>), #Enables or disables horse friendly fire (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
server_get_show_crosshair      = 3510 #(server_get_show_crosshair, <destination>), #Stores crosshair visibility status into <destination> (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
server_set_show_crosshair      = 3511 #(server_set_show_crosshair, <value>), #Enables or disables the crosshair (requires, for WSE: network_compatible = 0 in wse_settings.ini, for WSE2: bBreakWarbandCompatibility=true in rgl_config.ini)
get_server_option_at_connect   = 3512 #(get_server_option_at_connect, <destination>, [<index>]), #Stores option [<index>] into <destination>
server_set_password_rcon       = 3513 #(server_set_password_rcon, <password>), #Sets <password> as server RCON password
execute_server_console_command = 3514 #(execute_server_console_command, <string_register>, <command>), #Executes dedicated server console command <command> and stores result string into <string_register>
add_anonymous_player           = 3515 #(add_anonymous_player, <unique_id>, <name>), #Sets <name> pseudonym for multiplayer player <unique_id> (requires WSE2)
remove_anonymous_player        = 3516 #(remove_anonymous_player, <unique_id>), #Removes pseudonym for multiplayer player <unique_id> (requires WSE2)
clear_anonymous_players        = 3517 #(clear_anonymous_players), #Clears pseudonyms for multiplayer players (requires WSE2)
server_set_ghost_mode_advanced = 3518 #(server_set_ghost_mode_advanced, <value>, <can't_be_free>, <team>, <lock_to_view>, <only_players>), #Sets settings for advanced ghost mode. Works only for WSE2 clients. <value>: 0 - disable, 1 - enable, <can't_be_free>: 0 - camera can move, 1 - camera can't move, <team>: 0 - any team, 1 - player's team only, <lock_to_view>: 0 - freely rotate camera, 1 - lock to agent's view, <only_players>: 0 - any agents, 1 - only players (requires WSE2)

store_cur_mission_template_no        = 3600 #(store_cur_mission_template_no, <destination>), #Stores the current mission template into <destination>
set_show_use_tooltip                 = 3601 #(set_show_use_tooltip, <tooltip_type>, [<value>]), #Enables or disables use tooltips. See header_common_addon.py for possible types
set_ally_collision_threshold         = 3602 #(set_ally_collision_threshold, <low_boundary>, <high_boundary>), #Changes the animation progress boundaries (in percents) that determine if attacks on allies will collide (default: 45% <= x <= 60%)
particle_system_remove               = 3603 #(particle_system_remove, [<particle_system_no>]), #Removes [<particle_system_no>] (all particle systems if not set or -1) from the current entity (can be used in several in triggers)
get_spectated_agent_no               = 3604 #(get_spectated_agent_no, <destination>), #Stores spectated agent no into <destination>
prop_instance_set_forced_lod         = 3605 #(prop_instance_set_forced_lod, <prop_instance_no>, <lod_level>), #Forces <prop_instance_no>'s LOD level to <lod_level> (0 = auto)
prop_instance_set_variation_id       = 3606 #(prop_instance_set_variation_id, <prop_instance_no>, <value>), #Sets <prop_instance_no>'s variation id to <value>
prop_instance_set_variation_id_2     = 3607 #(prop_instance_set_variation_id_2, <prop_instance_no>, <value>), #Sets <prop_instance_no>'s variation id 2 to <value>
stop_time                            = 3608 #(stop_time, <value>), #Stops/resumes the mission. Works only in singleplayer with cheat mode enabled.
missile_get_path_point_position      = 3609 #(missile_get_path_point_position, <position_register>, <path_point_no>, <missile_no>), #Stores the position of the <missile_no>'s <path_point_no> (0-499) into <position_register>
get_water_level                      = 3610 #(get_water_level, <destination_fixed_point>), #Stores the water level into <destination_fixed_point>
missile_remove_on_hit                = 3611 #(missile_remove_on_hit), #Causes a missile item not to spawn on hit (can be only used inside ti_on_missile_hit)
missile_is_valid                     = 3612 #(missile_is_valid, <missile_no>), #Fails if <missile_no> is not valid
missile_get_cur_position             = 3613 #(missile_get_cur_position, <position_register>, <missile_no>), #Stores <missile_no>'s current position into <position_register>
set_prop_collision_threshold         = 3614 #(set_prop_collision_threshold, <attack_direction>, <low_boundary>, <high_boundary>), #Changes the animation progress boundaries (in percents) that determine if swing attacks on props will collide (default: 40% <= x <= 80% (75% for overheads))
get_camera_position                  = 3615 #(get_camera_position, <position_register>), #Stores camera position and rotation into <position_register>
prop_instance_remove_particle_system = 3616 #(prop_instance_remove_particle_system, <prop_instance_no>, [<particle_system_no>]), #Removes [<particle_system_no>] (all particle systems if not set or -1) from <prop_instance_no>
prop_instance_remove_light           = 3617 #(prop_instance_remove_light, <prop_instance_no>), #Removes light from <prop_instance_no>
prop_instance_get_sound_progress     = 3618 #(prop_instance_get_sound_progress, <destination>, <scene_prop_id>), #Stores <scene_prop_id>'s sound_progress into <destination>. Returned value can be between 0-100, or -1 if nothing is being played. (requires WSE2)
set_horse_friendly_fire              = 3619 #(set_horse_friendly_fire, <value>), #Enables or disables horse friendly fire for singleplayer
cast_ray_agents                      = 3620 #(cast_ray_agents, <destination>, <hit_position_register>, <ray_position_register>, [<ray_length_fixed_point>]), #Casts a ray of length [<ray_length_fixed_point>] starting from <ray_position_register> and stores the closest agent's hit position into <hit_position_register> (fails if no hits). Agent's id will be stored into <destination> and bone no will be stored into reg0 (requires WSE2)
ai_mesh_face_group_translate         = 3621 #(ai_mesh_face_group_translate, <group_no>, <position_register>), #Translates the ai mesh face <group_no> by distance given in <position_register> (requires WSE2)
set_show_crosshair                   = 3622 #(set_show_crosshair, <value>), #Enables or disables the crosshair for singleplayer
shift_entry_point                    = 3623 #(shift_entry_point, <entry_no>), #Shift <entry_no> same way game does to spawn visitors (requires WSE2)

troop_get_skill_points       = 3700 #(troop_get_skill_points, <destination>, <troop_no>), #Stores <troop_no>'s unused skill points into <destination>
troop_set_skill_points       = 3701 #(troop_set_skill_points, <troop_no>, <value>), #Sets <troop_no>'s unused skill points to <value>
troop_get_attribute_points   = 3702 #(troop_get_attribute_points, <destination>, <troop_no>), #Stores <troop_no>'s unused attribute points into <destination>
troop_set_attribute_points   = 3703 #(troop_set_attribute_points, <troop_no>, <value>), #Sets <troop_no>'s unused attribute points to <value>
troop_get_proficiency_points = 3704 #(troop_get_proficiency_points, <destination>, <troop_no>), #Stores <troop_no>'s unused proficiency points into <destination>
troop_set_proficiency_points = 3705 #(troop_set_proficiency_points, <troop_no>, <value>), #Sets <troop_no>'s unused proficiency points to <value>
troop_has_flag               = 3706 #(troop_has_flag, <troop_no>, <flag>), #Fails if <troop_no> doesn't have <flag>
troop_set_skill              = 3707 #(troop_set_skill, <troop_no>, <skill_no>, <value>), #Sets <troop_no>'s <skill_no> to <value>
troop_set_attribute          = 3708 #(troop_set_attribute, <troop_no>, <attribute>, <value>), #Sets <troop_no>'s <attribute> to <value>
troop_set_proficiency        = 3709 #(troop_set_proficiency, <troop_no>, <proficiency>, <value>), #Sets <troop_no>'s <proficiency> to <value>

item_set_thrust_damage          = 3800 #(item_set_thrust_damage, <item_kind_no>, <value>), #Sets <item_kind_no>'s thrust damage to <value>
item_set_thrust_damage_type     = 3801 #(item_set_thrust_damage_type, <item_kind_no>, <value>), #Sets <item_kind_no>'s thrust damage type to <value>
item_set_swing_damage           = 3802 #(item_set_swing_damage, <item_kind_no>, <value>), #Sets <item_kind_no>'s thrust damage to <value>
item_set_swing_damage_type      = 3803 #(item_set_swing_damage_type, <item_kind_no>, <value>), #Sets <item_kind_no>'s thrust damage type to <value>
item_set_head_armor             = 3804 #(item_set_head_armor, <item_kind_no>, <value>), #Sets <item_kind_no>'s head armor to <value>
item_set_body_armor             = 3805 #(item_set_body_armor, <item_kind_no>, <value>), #Sets <item_kind_no>'s body armor to <value>
item_set_leg_armor              = 3806 #(item_set_leg_armor, <item_kind_no>, <value>), #Sets <item_kind_no>'s leg armor to <value>
item_set_speed_rating           = 3807 #(item_set_speed_rating, <item_kind_no>, <value>), #Sets <item_kind_no>'s speed rating to <value>
item_set_missile_speed          = 3808 #(item_set_missile_speed, <item_kind_no>, <value>), #Sets <item_kind_no>'s missile speed to <value>
item_set_horse_blood_particles  = 3809 #(item_set_horse_blood_particles, <item_kind_no>, <particle_1_no>, <particle_2_no>), #Sets <item_kind_no>'s horse blood <particle_1_no> and <particle_2_no>
item_set_horse_blood_color      = 3810 #(item_set_horse_blood_color, <item_kind_no>, <color>), #Sets <item_kind_no>'s horse blood <color> (requires WSE2)
cur_item_mesh_set_color         = 3811 #(cur_item_mesh_set_color, <mesh_no>, <color>), #Sets item <mesh_no> color to <color>. Only call inside ti_on_init_item in module_items.
cur_item_add_mesh_with_material = 3812 #(cur_item_add_mesh_with_material, <mesh_name_string_no>, <material_name_string_no>, [<lod_begin>], [<lod_end>], [<color>]), #Adds another <mesh_name_string_no> to item. Replaces item material to <material_name_string_no>. Sets item color to [<color>]. Only call inside ti_on_init_item in module_items.
item_set_horse_skeleton_model   = 3813 #(item_set_horse_skeleton_model, <item_kind_no>, <skeleton_model_name>), #Sets <item_kind_no>'s horse <skeleton_model_name>. Use skeleton_model_clean_body_sections and skeleton_model_set_bone_body_section operations to configure sections for new horses skeleton models (requires WSE2)

party_stack_get_experience      = 3900 #(party_stack_get_experience, <destination>, <party_no>, <party_stack_no>), #Stores the experience of <party_no>'s <party_stack_no> into <destination>
party_stack_get_num_upgradeable = 3901 #(party_stack_get_num_upgradeable, <destination>, <party_no>, <party_stack_no>), #Stores the amount of upgradeable troops in <party_no>'s <party_stack_no> into <destination>
party_has_flag                  = 3902 #(party_has_flag, <party_no>, <flag>), #Fails if <party_no> doesn't have <flag>
party_heal_members              = 3903 #(party_heal_members, <party_no>, <troop_no>, <number>), #Heals <number> <troop_no> of <party_no>
party_switch_stacks             = 3904 #(party_switch_stacks, <party_no>, <party_stack_no_1>, <party_stack_no_2>), #Switches <party_no>'s <party_stack_no_1> and <party_stack_no_2>
party_stack_upgrade             = 3905 #(party_stack_upgrade, <party_no>, <party_stack_no>, <amount>, <upgrade_path>), #Upgrades <party_no>'s <party_stack_no>'s <amount> of troops (<upgrade_path> can be 0 or 1) (requires WSE2)
party_stack_set_num_upgradeable = 3906 #(party_stack_set_num_upgradeable, <party_no>, <party_stack_no>, <value>), #Sets <party_no>'s <party_stack_no>'s amount of upgradeable troops to <value>
party_get_banner_icon           = 3907 #(party_get_banner_icon, <destination>, <party_no>), #Stores <party_no>'s banner icon into <destination>
party_get_extra_icon            = 3908 #(party_get_extra_icon, <destination>, <party_no>), #Stores <party_no>'s extra icon into <destination>
party_get_player_id             = 3909 #(party_get_player_id, <destination>, <party_no>), #Stores <party_no>'s player reference into <destination>. For multiplayer campaign mode (requires WSE2)
party_is_non_player             = 3910 #(party_is_non_player, <party_no>), #Fails if <party_no> is player. For multiplayer campaign mode (requires WSE2)

position_get_vector_to_position = 4100 #(position_get_vector_to_position, <destination_fixed_point>, <dest_position_register>, <position_register_1>, <position_register_2>), #Stores the vector from <position_register_1> to <position_register_2> into <dest_position_register> and its length into <destination_fixed_point>
position_align_to_ground        = 4101 #(position_align_to_ground, <position_register>, [<point_up>], [<set_z_to_ground_level>]), #Aligns <position_register> to the ground (or to the ground normal if [<point_up>] is set)
position_get_length             = 4102 #(position_get_length, <destination_fixed_point>, <position_register>), #Stores <position_register> length into <destination_fixed_point>
get_dot_product_of_positions    = 4103 #(get_dot_product_of_positions, <destination_fixed_point>, <position_register_1>, <position_register_2>), #Stores <position_register_1> and <position_register_2> dot product into <destination_fixed_point>
get_cross_product_of_positions  = 4104 #(get_cross_product_of_positions, <dest_position_register>, <position_register_1>, <position_register_2>), #Stores <position_register_1> and <position_register_2> cross product into <dest_position_register>

str_equals                                = 4200 #(str_equals, <string_1>, <string_2>, [<case_insensitive>]), #Fails if <string_1> is not equal to <string_2>
str_contains                              = 4201 #(str_contains, <string_1>, <string_2>, [<case_insensitive>]), #Fails if <string_1> doesn't contain <string_2>
str_starts_with                           = 4202 #(str_starts_with, <string_1>, <string_2>, [<case_insensitive>]), #Fails if <string_1> doesn't start with <string_2>
str_ends_with                             = 4203 #(str_ends_with, <string_1>, <string_2>, [<case_insensitive>]), #Fails if <string_1> doesn't end with <string_2>
str_is_alpha                              = 4204 #(str_is_alpha, <string_1>, [<index>]), #Fails if character [<index>] of <string_1> isn't alphabetic. If [<index>] is not defined or is -1, the entire string is checked
str_is_digit                              = 4205 #(str_is_digit, <string_1>, [<index>]), #Fails if character [<index>] of <string_1> isn't a digit. If [<index>] is not defined or is -1, the entire string is checked
str_is_whitespace                         = 4206 #(str_is_whitespace, <string_1>, [<index>]), #Fails if character [<index>] of <string_1> isn't whitespace. If [<index>] is not defined or is -1, the entire string is checked
str_length                                = 4207 #(str_length, <destination>, <string_1>), #Stores the length of <string_1> into <destination>
str_index_of                              = 4208 #(str_index_of, <destination>, <string_1>, <string_2>, [<start>], [<end>]), #Stores the index of the first occurrence of <string_2> in <string_1> into <destination>. Search bounds can be specified with [<start>] and [<end>]
str_last_index_of                         = 4209 #(str_last_index_of, <destination>, <string_1>, <string_2>, [<start>], [<end>]), #Stores the index of the last occurrence of <string_2> in <string_1> into <destination>. Search bounds can be specified with [<start>] and [<end>]
str_get_char                              = 4210 #(str_get_char, <destination>, <string_1>, [<index>]), #Stores the numeric value of the [<index>]th character in <string_1> into <destination>
str_to_num                                = 4211 #(str_to_num, <destination_fixed_point>, <string_1>, [<use_fixed_point_multiplier>]), #Stores the numeric value of <string_1> into <destination_fixed_point>. Decimal values will be rounded to integers, for more precision set [<use_fixed_point_multiplier>] to non-zero
str_compare                               = 4212 #(str_compare, <destination>, <string_1>, <string_2>, [<case_insensitive>]), #Stores the relationship between <string_1> and <string_2> into <destination> (-1: s1 < s2, 0: s1 = s2, 1: s1 > s2)
str_split                                 = 4213 #(str_split, <destination>, <string_register>, <string_1>, <delimiter>, [<skip_empty>], [<max>]), #Splits <string_1> using <delimiter> into a range of string registers, starting from <string_register>, storing [<max>] substrings at most (default = unlimited), ignoring empty (zero length) substrings if [<skip_empty>] (default = false). Stores the amount of substrings split into <destination>
str_sort                                  = 4214 #(str_sort, <string_register>, [<count>], [<case_insensitive>], [<descending>]), #Sorts a range of [<count>] string registers starting from <string_register>
str_store_lower                           = 4215 #(str_store_lower, <string_register>, <string_1>), #Stores the lowercase version of <string_1> into <string_register>
str_store_upper                           = 4216 #(str_store_upper, <string_register>, <string_1>), #Stores the uppercase version of <string_1> into <string_register>
str_store_trim                            = 4217 #(str_store_trim, <string_register>, <string_1>, [<trim_mode>]), #Stores the whitespace trimmed version of <string_1> into <string_register>. [<trim_mode>]: 0 (default) = trim leading and trailing, 1 = trim leading, 2 = trim trailing
str_store_replace                         = 4218 #(str_store_replace, <string_register>, <string_1>, <string_2>, <string_3>), #Stores <string_1> into <string_register>, replacing occurrences of <string_2> with <string_3>
str_store_md5                             = 4219 #(str_store_md5, <string_register>, <string_1>), #MD5 encrypts <string_1> and stores it into <string_register>
str_store_substring                       = 4220 #(str_store_substring, <string_register>, <string_1>, [<start>], [<length>]), #Stores a substring of <string_1> into <string_register>, starting from [<start>]. If [<length>] is not specified, everything on the right of <start> will be used
str_store_reverse                         = 4221 #(str_store_reverse, <string_register>, <string_1>), #Stores the reverse of <string_register> into <string_1>
str_store_join                            = 4222 #(str_store_join, <string_register>, <start_string_register>, <count>, [<delimiter>]), #Joins <count> string registers starting from string register <start_string_register>, using [<delimiter>] (default = empty string) and stores them into <string_register>
str_store_replace_spaces_with_underscores = 4223 #(str_store_replace_spaces_with_underscores, <string_register>, <string_1>), #Stores <string_1> into <string_register>, replacing all spaces with underscores
str_store_replace_underscores_with_spaces = 4224 #(str_store_replace_underscores_with_spaces, <string_register>, <string_1>), #Stores <string_1> into <string_register>, replacing all underscores with spaces
str_store_multiplayer_profile_name        = 4225 #(str_store_multiplayer_profile_name, <string_register>, <profile_no>), #Stores <profile_no>'s name into <string_register>
str_store_module_setting                  = 4226 #(str_store_module_setting, <string_register>, <setting>), #Stores the string value (empty if not found) of <setting> in module.ini into <string_register>
str_store_server_password_admin           = 4227 #(str_store_server_password_admin, <string_register>), #Stores the server administrator password into <string_register>
str_store_server_password_private         = 4228 #(str_store_server_password_private, <string_register>), #Stores the server private player password into <string_register>
str_store_overlay_text                    = 4229 #(str_store_overlay_text, <string_register>, <overlay_no>), #Stores <overlay_no>'s text into <string_register>
str_store_player_ip                       = 4230 #(str_store_player_ip, <string_register>, <player_no>), #Stores <player_no>'s IP address into <string_register> (works only on servers)
str_store_game_variable                   = 4231 #(str_store_game_variable, <string_register>, <variable>), #Stores the string value (empty if not found) of <variable> in game_variables.txt into <string_register>
str_store_skill_name                      = 4232 #(str_store_skill_name, <string_register>, <skill_no>), #Stores the name of <skill_no> into <string_register>
str_store_float                           = 4233 #(str_store_float, <string_register>, <fp_register>, [<precision>]), #Stores the string representation of <fp_register> into <string_register> showing [<precision>] decimal digits at most
str_sanitize                              = 4234 #(str_sanitize, <string_register>), #Removes invalid characters from <string_register>
str_store_item_id                         = 4235 #(str_store_item_id, <string_register>, <item_no>), #Stores the id of <item_no> into <string_register>
str_is_integer                            = 4236 #(str_is_integer, <string_1>), #Fails if <string_1> isn't a valid integer
str_store_multiplayer_profile_face_keys   = 4237 #(str_store_multiplayer_profile_face_keys, <string_register>, <profile_no>), #Stores <profile_no>'s face keys into <string_register>
str_store_server_password_rcon            = 4238 #(str_store_server_password_rcon, <string_register>), #Stores the server RCON password into <string_register>
str_store_item_mesh_name                  = 4239 #(str_store_item_mesh_name, <string_register>, <item_no>), #Stores the mesh name of <item_no> into <string_register>
str_regex_match                           = 4240 #(str_regex_match, <string_1>, <string_regex>), #Fails if <string_1> does not match <string_regex>
str_regex_search                          = 4241 #(str_regex_search, <string_1>, <string_regex>), #Fails if <string_1> does not contain <string_regex>
str_regex_get_matches                     = 4242 #(str_regex_get_matches, <destination>, <string_register>, <string_1>, <string_regex>, [<max>]), #Stores all matches of <string_regex> that occur in <string_1> into a range of string registers, starting from <string_register>, storing [[<max>]] substrings at most (default = unlimited). Stores the amount of matches into <destination>
str_store_regex_replace                   = 4243 #(str_store_regex_replace, <string_register>, <string_1>, <string_regex>, <string_2>), #Stores <string_1> into <string_register>, replacing occurrences of <string_regex> with <string_2>
str_decode_url                            = 4244 #(str_decode_url, <string_register>, <string_1>), #Decode url encoded <string_1> and stores it into <string_register>. Note that it doesn't convert +'s to spaces(as per the spec)
str_store_skill_desc                      = 4245 #(str_store_skill_desc, <string_register>, <skill_no>), #Stores the description of <skill_no> into <string_register>

options_get_verbose_casualties  = 4300 #(options_get_verbose_casualties, <destination>), #Stores verbose casualties enabled/disabled into <destination>
options_set_verbose_casualties  = 4301 #(options_set_verbose_casualties, <value>), #Enables or disables verbose casualties
options_get_cheat_mode          = 4302 #(options_get_cheat_mode, <destination>), #Stores cheat mode enabled/disabled into <destination>
options_set_cheat_mode          = 4303 #(options_set_cheat_mode, <value>), #Enables or disables cheat mode
options_get_realistic_headshots = 4304 #(options_get_realistic_headshots, <destination>), #Stores "realistic" headshots enabled/disabled into <destination>
options_set_realistic_headshots = 4305 #(options_set_realistic_headshots, <value>), #Enables or disables "realistic" headshots

fld       = 4400 #(fld, <fp_register>, <value_fixed_point>), #Loads <value_fixed_point> into <fp_register>
fld_str   = 4401 #(fld_str, <fp_register>, <string>), #Parses <string> and loads it into <fp_register>
fld_pos_x = 4402 #(fld_pos_x, <fp_register>, <position_register_no>), #Loads the x component of <position_register_no> into <fp_register>
fld_pos_y = 4403 #(fld_pos_y, <fp_register>, <position_register_no>), #Loads the y component of <position_register_no> into <fp_register>
fld_pos_z = 4404 #(fld_pos_z, <fp_register>, <position_register_no>), #Loads the z component of <position_register_no> into <fp_register>
fst       = 4405 #(fst, <destination_fixed_point>, <fp_register>), #Stores <fp_register> into <destination_fixed_point>
fcpy      = 4406 #(fcpy, <fp_register_1>, <fp_register_2>), #Copies <fp_register_2> into <fp_register_1>
feq       = 4407 #(feq, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Fails if <fp_register_1> isn't approximately equal to <fp_register_2>
fgt       = 4408 #(fgt, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Fails if <fp_register_1> isn't greater than <fp_register_2>
flt       = 4409 #(flt, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Fails if <fp_register_1> isn't less than <fp_register_2>
fge       = 4410 #(fge, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Fails if <fp_register_1> isn't greater or approximately equal to <fp_register_2>
fle       = 4411 #(fle, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Fails if <fp_register_1> isn't less or approximately equal to <fp_register_2>
fsub      = 4412 #(fsub, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Subtracts <fp_register_2> from <fp_register_1> and stores the result into <destination_fp_register>
fmul      = 4413 #(fmul, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Multiplies <fp_register_1> by <fp_register_2> and stores the result into <destination_fp_register>
fdiv      = 4414 #(fdiv, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Divides <fp_register_1> by <fp_register_2> and stores the result into <destination_fp_register>
fmin      = 4415 #(fmin, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Stores the smaller value between <fp_register_1> and <fp_register_2> into <destination_fp_register>
fmax      = 4416 #(fmax, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Stores the larger value between <fp_register_1> and <fp_register_2> into <destination_fp_register>
fclamp    = 4417 #(fclamp, <destination_fp_register>, <fp_register_1>, <fp_register_2>, <fp_register_3>), #Clamps <fp_register_1> between <fp_register_2> and <fp_register_3> and stores the result into <destination_fp_register>
fsqrt     = 4418 #(fsqrt, <destination_fp_register>, <fp_register>), #Stores the square root of <fp_register> into <destination_fp_register>
fabs      = 4419 #(fabs, <destination_fp_register>, <fp_register>), #Stores the absolute value of <fp_register> into <destination_fp_register>
fceil     = 4420 #(fceil, <destination_fp_register>, <fp_register>), #Stores the ceiling of <fp_register> into <destination_fp_register>
ffloor    = 4421 #(ffloor, <destination_fp_register>, <fp_register>), #Stores the floor of <fp_register> into <destination_fp_register>
fexp      = 4422 #(fexp, <destination_fp_register>, <fp_register>), #Stores e raised to the power of <fp_register> into <destination_fp_register>
fpow      = 4423 #(fpow, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Stores <fp_register_1> raised to the power of <fp_register_2> into <destination_fp_register>
fln       = 4424 #(fln, <destination_fp_register>, <fp_register>), #Stores the natural logarithm of <fp_register> into <destination_fp_register>
flog      = 4425 #(flog, <destination_fp_register>, <fp_register>, [<base>]), #Stores the base-[<base>] (default: base-10) logarithm of <fp_register> into <destination_fp_register>
fmod      = 4426 #(fmod, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Stores the remainder of <fp_register_1>/<fp_register_2> into <destination_fp_register>
fsin      = 4427 #(fsin, <destination_fp_register>, <fp_register>), #Stores the sine of <fp_register> into <destination_fp_register>
fcos      = 4428 #(fcos, <destination_fp_register>, <fp_register>), #Stores the cosine of <fp_register> into <destination_fp_register>
ftan      = 4429 #(ftan, <destination_fp_register>, <fp_register>), #Stores the tangent of <fp_register> into <destination_fp_register>
fsinh     = 4430 #(fsinh, <destination_fp_register>, <fp_register>), #Stores the hyperbolic sine of <fp_register> into <destination_fp_register>
fcosh     = 4431 #(fcosh, <destination_fp_register>, <fp_register>), #Stores the hyperbolic cosine of <fp_register> into <destination_fp_register>
ftanh     = 4432 #(ftanh, <destination_fp_register>, <fp_register>), #Stores the hyperbolic tangent of <fp_register> into <destination_fp_register>
fasin     = 4433 #(fasin, <destination_fp_register>, <fp_register>), #Stores the arc sine of <fp_register> into <destination_fp_register>
facos     = 4434 #(facos, <destination_fp_register>, <fp_register>), #Stores the arc cosine of <fp_register> into <destination_fp_register>
fatan     = 4435 #(fatan, <destination_fp_register>, <fp_register>), #Stores the arc tangent of <fp_register> into <destination_fp_register>
fatan2    = 4436 #(fatan2, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Stores the arc cosine of <fp_register_1>/<fp_register_2> into <destination_fp_register>
feval     = 4437 #(feval, <expression_string>), #Evaluates <expression_string>. See EVAL_README.txt in WSESDK for more information
fadd      = 4438 #(fadd, <destination_fp_register>, <fp_register_1>, <fp_register_2>), #Adds <fp_register_2> to <fp_register_1> and stores the result into <destination_fp_register>

scene_set_flags         = 4500 #(scene_set_flags, <scene_no>, <flags>), #Sets <scene_no>'s flags to <flags>
scene_set_water_level   = 4501 #(scene_set_water_level, <scene_no>, <water_level_fixed_point>), #Sets <scene_no>'s water level to <water_level_fixed_point>
scene_set_bounds        = 4502 #(scene_set_bounds, <scene_no>, <min_x_fixed_point>, <min_y_fixed_point>, <max_x_fixed_point>, <max_y_fixed_point>), #Sets <scene_no>'s bounds to (<min_x_fixed_point>, <min_y_fixed_point>) and (<max_x_fixed_point>, <max_y_fixed_point>)
scene_set_outer_terrain = 4503 #(scene_set_outer_terrain, <scene_no>, <outer_terrain_mesh_name>), #Sets <scene_no>'s outer terrain to <outer_terrain_mesh_name>
scene_set_terrain_seed  = 4504 #(scene_set_terrain_seed, <scene_no>, <value>), #Sets <scene_no>'s terrain generator terrain seed to <value>
scene_set_river_seed    = 4505 #(scene_set_river_seed, <scene_no>, <value>), #Sets <scene_no>'s terrain generator river seed to <value>
scene_set_flora_seed    = 4506 #(scene_set_flora_seed, <scene_no>, <value>), #Sets <scene_no>'s terrain generator flora seed to <value>
scene_set_deep_water    = 4507 #(scene_set_deep_water, <scene_no>, <value>), #Enables or disables terrain generator deep water for <scene_no>
scene_set_place_river   = 4508 #(scene_set_place_river, <scene_no>, <value>), #Enables or disables terrain generator river placement for <scene_no>
scene_set_disable_grass = 4509 #(scene_set_disable_grass, <scene_no>, <value>), #Enables or disables terrain generator grass placement for <scene_no>
scene_set_valley_size   = 4510 #(scene_set_valley_size, <scene_no>, <value>), #Sets <scene_no>'s terrain generator valley size to <value> (0-127)
scene_set_hill_height   = 4511 #(scene_set_hill_height, <scene_no>, <value>), #Sets <scene_no>'s terrain generator hill height to <value> (0-127)
scene_set_ruggedness    = 4512 #(scene_set_ruggedness, <scene_no>, <value>), #Sets <scene_no>'s terrain generator ruggedness to <value> (0-127)
scene_set_vegetation    = 4513 #(scene_set_vegetation, <scene_no>, <value>), #Sets <scene_no>'s terrain generator vegetation to <value> (0-127)
scene_set_size          = 4514 #(scene_set_size, <scene_no>, <x>, <y>), #Sets <scene_no>'s terrain generator map size to (<x>, <y>) (0-1023)
scene_set_region_type   = 4515 #(scene_set_region_type, <scene_no>, <value>), #Sets <scene_no>'s terrain generator region type to <value> (0-15)
scene_set_region_detail = 4516 #(scene_set_region_detail, <scene_no>, <value>), #Sets <scene_no>'s terrain generator region detail to <value> (0-3)

edit_mode_get_num_selected_prop_instances = 4600 #(edit_mode_get_num_selected_prop_instances, <destination>), #Stores the number of selected prop instances into <destination>
edit_mode_get_selected_prop_instance      = 4601 #(edit_mode_get_selected_prop_instance, <destination>, <index>), #Stores the <index>th selected prop instance into instance no into <destination>
edit_mode_select_prop_instance            = 4602 #(edit_mode_select_prop_instance, <prop_instance_no>), #Stores the <1>th selected prop instance into instance no into <prop_instance_no>
edit_mode_deselect_prop_instance          = 4603 #(edit_mode_deselect_prop_instance, <prop_instance_no>), #Stores the <1>th selected prop instance into instance no into <prop_instance_no>
edit_mode_get_highlighted_prop_instance   = 4604 #(edit_mode_get_highlighted_prop_instance, <destination>), #Stores the highlighted prop instance into <destination>
edit_mode_set_highlighted_prop_instance   = 4605 #(edit_mode_set_highlighted_prop_instance, [<prop_instance_no>]), #Stores the <1>th selected prop instance into instance no into [<prop_instance_no>]
edit_mode_set_enabled                     = 4606 #(edit_mode_set_enabled, <value>), #Enables or disables edit mode
edit_mode_in_edit_objects_mode            = 4607 #(edit_mode_in_edit_objects_mode), #Fails if the game is not in edit objects mode

update_material   = 4700 #(update_material, <material_name>, <new_material_name>), #Updates <material_name> with <new_material_name>
reload_item_kinds = 4701 #(reload_item_kinds, [<change_file>], [<file_name>]), #Reload item kinds. If [<change_file>] sets, then [<file_name>] loaded instead default file (requires WSE2)
reload_troops     = 4702 #(reload_troops, [<change_file>], [<file_name>]), #Reload troops. If [<change_file>] sets, then [<file_name>] loaded instead default file (requires WSE2)
reload_parties    = 4703 #(reload_parties, [<change_file>], [<file_name>]), #Reload parties. If [<change_file>] sets, then [<file_name>] loaded instead default file (requires WSE2)

menu_create_new      = 4800 #(menu_create_new, <destination>, <text>, [<mesh_name>], [<flags>], [<script_no>], [<script_param>]), #Creates a dynamic menu and stores its id into <destination>. [<script_no>] (-1 for no script) will be called with params 1 = menu_no, 2 = [<script_param>] when the operations block is executed
menu_add_item        = 4801 #(menu_add_item, <menu_no>, <text>, [<conditions_script_no>], [<consequences_script_no>], [<script_param>]), #Adds a new menu item to <menu_no>. [<conditions_script_no>] and [<consequences_script_no>] (-1 for no script) will be called with params 1 = <menu_no>, 2 = [<script_param>] when the conditions/consequences blocks are executed
menu_clear_items     = 4802 #(menu_clear_items, <menu_no>), #Removes all menu items from <menu_no>
menu_clear_generated = 4803 #(menu_clear_generated), #Removes all dynamic menus

overlay_get_val         = 4900 #(overlay_get_val, <destination>, <overlay_no>), #Stores <overlay_no>'s value into <destination>
presentation_activate   = 4901 #(presentation_activate, <presentation_no>), #Activates <presentation_no>. Fails if <presentation_no> is not running
overlay_button_set_type = 4902 #(overlay_button_set_type, <overlay_no>, <toggle_or_not>, <deselectable_or_not>), #Sets <overlay_no>'s <toggle_or_not> and <deselectable_or_not>
overlay_get_scroll_pos  = 4903 #(overlay_get_scroll_pos, <destination_fixed_point>, <overlay_no>), #Stores <overlay_no>'s scroll pos into <destination_fixed_point>
overlay_set_scroll_pos  = 4904 #(overlay_set_scroll_pos, <overlay_no>, <value_fixed_point>), #Sets <overlay_no>'s scroll pos <value_fixed_point>
overlay_enable          = 4905 #(overlay_enable, <overlay_no>, <enable_or_disable>), #Sets <overlay_no>'s <enable_or_disable>
overlay_item_set_text   = 4906 #(overlay_item_set_text, <overlay_no>, <item_no>, <text>), #Changes the <overlay_no>'s <item_no>'s <text>. Items are indexed from 0 (requires WSE2)

array_create        = 5000 #(array_create, <destination>, <type_id>, <Dim 0>, [<Dim 1>], [<Dim 2>], [<Dim 3>], [<Dim 4>], [<Dim 5>], [<Dim 6>], [<Dim 7>], [<Dim 8>], [<Dim 9>], [<Dim 10>], [<Dim 11>], [<Dim 12>], [<Dim 13>]), #Creates an array object of <type_id> (0: Integer, 1: String, 2: Position) and stores its ID into <destination>. You can specify up to 14 dimensions, from <Dim 0> to [<Dim 13>]. The array will be initialized by default with 0 / empty string / 0-position.
array_free          = 5001 #(array_free, <arrayID>), #Frees array with <arrayID>.
array_copy          = 5002 #(array_copy, <destination>, <source arrayID>), #Copys array with <source arrayID> and stores the new array id into <destination>.
array_save_file     = 5003 #(array_save_file, <arrayID>, <file>), #Saves <arrayID> into a file. For security reasons, <file> is just a name, not a full path, and will be stored into a WSE managed directory.
array_load_file     = 5004 #(array_load_file, <destination>, <file>), #Loads <file> as an array and stores the newly created array's ID into <destination>.
array_delete_file   = 5005 #(array_delete_file, <file>), #Deletes array <file>.
array_set_val       = 5006 #(array_set_val, <arrayID>, <value>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Writes <value> to the array with <arrayID> at the specified index. <value> can be an integer, a position register or a string register and must match the type of the array.
array_set_val_all   = 5007 #(array_set_val_all, <arrayID>, <value>), #Writes <value> to all indices of the array with <arrayID>. <value> can be an integer, a position register or a string register and must match the type of the array.
array_get_val       = 5008 #(array_get_val, <destination>, <arrayID>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Gets a value from the array with <arrayID> at the specified index and writes it to <destination>. <destination> can be a variable, a position register or a string register and must match the type of the array.
array_push          = 5009 #(array_push, <destination arrayID>, <source>), #Pushes <source> on the array with <destination arrayID>. If <destination arrayID> is a 1D array, <source> can be an int, string, or position register and must match the type of <destination arrayID>. If <destination arrayID> is multidimensional, <source> must be the id of an array with matching type, src dimension count = dest dimension count - 1, and dimension sizes src_dim_0_size = dest_dim_1_size ... src_dim_n_size = dest_dim_n+1_size.
array_pop           = 5010 #(array_pop, <destination>, <arrayID>), #Pops the last value  from the array with <arrayID>. If <arrayID> is a 1D array, <destination> must be a variable, string, or position register and must match the type of <arrayID>. If <arrayID> is multidimensional, a new array with dimension count = src dimension count - 1, dimensions dim_0 = src_dim_1 ... dim_n = src_dim_n+1 will be created and its ID will be stored in <destination>
array_resize_dim    = 5011 #(array_resize_dim, <arrayID>, <dimIndex>, <size>), #Changes the size of the dimension with <dimIndex> of the array with <arrayID> to <size>.
array_get_dim_size  = 5012 #(array_get_dim_size, <destination>, <arrayID>, <dimIndex>), #Gets the size of the dimension with <dimIndex> of the array with <arrayID> and stores it into <destination>.
array_get_dim_count = 5013 #(array_get_dim_count, <destination>, <arrayID>), #Gets the the amount of dimensions of the array with <arrayID> and stores it into <destination>.
array_get_type_id   = 5014 #(array_get_type_id, <destination>, <arrayID>), #Gets the the type id of the array with <arrayID> and stores it into <destination>.
array_sort          = 5015 #(array_sort, <arrayID>, <sortMode>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Sorts the array with <arrayID> using a stable natural-mergesort algorithm. <sortMode> can be: [sort_m_int_asc or sort_m_int_desc] for int, [sort_m_str_cs_asc, sort_m_str_cs_desc, sort_m_str_ci_asc, sort_m_str_ci_desc] for str (asc=ascending, desc=descending, cs=case sensitive, ci=case insensitive, strings are compared alphabetically, upper before lower case). If the array is multidimensional, only the first dimension will be sorted and you must specify (dim_count - 1) fixed indices that will be used for access.
array_sort_custom   = 5016 #(array_sort_custom, <arrayID>, <cmpScript>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Sorts the array with <arrayID> using a stable natural-mergesort algorithm. <cmpScript> must compare its two input values (reg0 and reg1 / s0 and s1 / pos0 and pos1) and use (return_values, x) where x is nonzero if the first value goes before or is equal to the second, and zero otherwise. If the array is multidimensional, only the first dimension will be sorted and you must specify (dim_count - 1) fixed indices that will be used for access. The sorting won't be successful if the compare script does not work properly. The algorithm will abort at some point and not go into an infinite loop, it may however take extremely long to finish on big arrays.
array_eq            = 5017 #(array_eq, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is not equal to <value_1>. Works for int, str and pos.
array_neq           = 5018 #(array_neq, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is equal to <value_1>. Works for int, str and pos.
array_gt            = 5019 #(array_gt, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is not greater than <value_1>. Works for int and str. Strings are compared alphabetically, upper before lower case.
array_ge            = 5020 #(array_ge, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is not greater or equal to <value_1>. Works for int and str. Strings are compared alphabetically, upper before lower case.
array_lt            = 5021 #(array_lt, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is not lower than <value_1>. Works for int and str. Strings are compared alphabetically, upper before lower case.
array_le            = 5022 #(array_le, <arrayID>, <value_1>, <Index 0>, [<Index 1>], [<Index 2>], [<Index 3>], [<Index 4>], [<Index 5>], [<Index 6>], [<Index 7>], [<Index 8>], [<Index 9>], [<Index 10>], [<Index 11>], [<Index 12>], [<Index 13>]), #Fails if the specified value in the array with <arrayID> is not lower or equal to <value_1>. Works for int and str. Strings are compared alphabetically, upper before lower case.

lua_get_top         = 5100 #(lua_get_top, <destination>), #Stores the index of the top element in the lua stack into <destination>. The result also is equal to the number of elements in the stack.
lua_set_top         = 5101 #(lua_set_top, <index>), #Sets the top of the stack to <index>. Setting it to 0 just clears the entire stack.
lua_insert          = 5102 #(lua_insert, <index>), #Moves the stacks top element into <index>, shifting up the elements above <index> to open space.
lua_remove          = 5103 #(lua_remove, <index>), #Removes the element at the given <index>, shifting down the elements above <index> to fill the gap.
lua_pop             = 5104 #(lua_pop, <value>), #Pops <value> values from the lua stack.
lua_to_int          = 5105 #(lua_to_int, <destination>, <index>), #Retrieves the value at <index> from the lua stack and stores it in <destination>
lua_to_str          = 5106 #(lua_to_str, <string_register>, <index>), #Retrieves the string at <index> from the lua stack and stores it in <string_register>
lua_to_pos          = 5107 #(lua_to_pos, <pos_register>, <index>), #Retrieves the position at <index> from the lua stack and stores it in <pos_register>
lua_push_int        = 5108 #(lua_push_int, <value>), #Pushes <value> onto the lua stack.
lua_push_str        = 5109 #(lua_push_str, <string_1>), #Pushes <string_1> onto the lua stack.
lua_push_pos        = 5110 #(lua_push_pos, <pos_register>), #Pushes the position in <pos_register> onto the lua stack.
lua_get_type        = 5111 #(lua_get_type, <destination>, <index>), #Stores the type of the value at <index> in the stack into <destination>. Return types can be found in header_common(_addon).py (LUA_T*)
lua_call            = 5112 #(lua_call, <func_name>, <num_args>), #Calls the lua function with name <func_name>, using the lua stack to pass <num_args> arguments and to return values. The first argument is pushed first. All arguments get removed from the stack automatically. The last return value will be at the top of the stack.
lua_triggerCallback = 5113 #(lua_triggerCallback, <reference>, <triggerPart>, [<context>]), #Calls the lua trigger callback with <reference>. This operation is utilized internally and should not be used, unless you know what you are doing.

skin_set_blood_color                 = 5200 #(skin_set_blood_color, <skin_no>, <color>), #Sets <skin_no>'s blood <color> (requires WSE2)
skeleton_model_set_bone_body_section = 5201 #(skeleton_model_set_bone_body_section, <skeleton_model_name>, <bone_no>, <body_section>), #Sets <skeleton_model_name>'s <bone_no> <body_section>. 0 - none, 1 - lowerbody, 2 - rightside (included lowerbody), 3 - all (included lowerbody and rightside). Check acf_enforce animations flags (requires WSE2)
skeleton_model_clean_body_sections   = 5202 #(skeleton_model_clean_body_sections, <skeleton_model_name>), #Cleans <skeleton_model_name>'s body sections. Use to clean default body sections before set new (requires WSE2)

#WSE2 extended operations
game_key_get_mapped_key_name                = 65 #(game_key_get_mapped_key_name, <string_register>, <game_key_no>, [<alternative>]), #Stores human-readable key name that's currently assigned to the provided <game_key_no> into <string_register> (requires WSE2)
options_get_damage_to_player                = 260 #(options_get_damage_to_player, <destination>, [<percentage>]), #Stores damage to player for singleplayer into <destination>. If set [<percentage>], uses 0-100% range instead default values (0 = 1/4, 1 = 1/2, 2 = 1/1) (requires WSE2)
options_set_damage_to_player                = 261 #(options_set_damage_to_player, <value>, [<percentage>]), #Sets damage to player for singleplayer. If set [<percentage>], uses 0-100% range instead default values (0 = 1/4, 1 = 1/2, 2 = 1/1) (requires WSE2)
options_get_damage_to_friends               = 262 #(options_get_damage_to_friends, <destination>, [<percentage>]), #Stores damage to friends for singleplayer into <destination>. If set [<percentage>], uses 0-100% range instead default values (0 = 1/2, 1 = 3/4, 2 = 1/1) (requires WSE2)
options_set_damage_to_friends               = 263 #(options_set_damage_to_friends, <value>, [<percentage>]), #Sets damage to friends for singleplayer. If set [<percentage>], uses 0-100% range instead default values (0 = 1/2, 1 = 3/4, 2 = 1/1) (requires WSE2)
start_map_conversation                      = 1025 #(start_map_conversation, <troop_id>, [<troop_dna>], [<set_dialog_state>], [<dialog_state>], [<from_presentation>]), #Starts a conversation with the selected <troop_id>. Can be called directly from global map or game menus. [<troop_dna>] parameter allows you to randomize non-hero troop appearances. If [<set_dialog_state>] sets, then [<dialog_state>] used instead dlg_event_triggered. If [<from_presentation>] sets, then conversation called directly from the presentation. (requires WSE2)
agent_get_attached_scene_prop               = 1756 #(agent_get_attached_scene_prop, <destination>, <agent_no>, [<attached_prop_index>]), #Stores scene prop instance which is attached to the <agent_no>, or -1 if there isn't any into <destination>. ([<attached_prop_index>]: 0-3) (requires WSE2)
agent_set_attached_scene_prop               = 1757 #(agent_set_attached_scene_prop, <agent_no>, <prop_instance_no>, [<attached_prop_index>], [<bone_no>], [<use_bone_rotation>]), #Attaches the specified <prop_instance_no> to the <agent_no>. ([<attached_prop_index>]: 0-3) (requires WSE2)
agent_set_attached_scene_prop_x             = 1758 #(agent_set_attached_scene_prop_x, <agent_no>, <value>, [<attached_prop_index>]), #Offsets the position of the attached scene prop in relation to <agent_no>, in centimeters, along the X axis (left/right). ([<attached_prop_index>]: 0-3) (requires WSE2)
agent_set_attached_scene_prop_z             = 1759 #(agent_set_attached_scene_prop_z, <agent_no>, <value>, [<attached_prop_index>]), #Offsets the position of the attached scene prop in relation to <agent_no>, in centimeters, along the Z axis (down/up). ([<attached_prop_index>]: 0-3) (requires WSE2)
entry_point_get_position                    = 1780 #(entry_point_get_position, <position_register>, <entry_no>, [<shifted>]), #Stores <entry_no>'s position into <position_register>. If [<shifted>] is non-zero stores shifted position (requires WSE2)
agent_set_attached_scene_prop_y             = 1809 #(agent_set_attached_scene_prop_y, <agent_no>, <value>, [<attached_prop_index>]), #Offsets the position of the attached scene prop in relation to <agent_no>, in centimeters, along the Y axis (backwards/forward). ([<attached_prop_index>]: 0-3) (requires WSE2)
prop_instance_intersects_with_prop_instance = 1880 #(prop_instance_intersects_with_prop_instance, <checked_scene_prop_no>, <prop_instance_no>, [<check_polygon_to_polygon>]), #Checks if two scene props are intersecting (i.e. collided). Useful when animating scene props movement. Pass -1 for <prop_instance_no> to check the prop against all other props on the scene. Scene props must have active collision meshes. If [<check_polygon_to_polygon>] is non-zero also checks polygon-to-polygon physics models, this is may reduce performance. (requires WSE2)
str_store_player_username                   = 2350 #(str_store_player_username, <string_register>, <player_no>, [<force_real>]), #Stores <player_no>'s multiplayer username into <string_register>. [<force_real>] uses for real name instead anonymous pseudonym (requires WSE2)

game_key_get_key = 3100 #(game_key_get_key, <destination>, <game_key_no>, [<alternative>], [<modifier>]), #Stores the key mapped to <game_key_no> into <destination> (requires WSE2)

str_store_module_setting = 4226 #(str_store_module_setting, <string_register>, <setting>, <section>), #Stores the string value (empty if not found) of <section>'s <setting> in rgl_config.ini into <string_register> (requires WSE2)

overlay_get_scroll_pos = 4903 #(overlay_get_scroll_pos, <destination_fixed_point>, <overlay_no>, [<horizontal>]), #Stores <overlay_no>'s scroll pos into <destination_fixed_point> (requires WSE2)
overlay_set_scroll_pos = 4904 #(overlay_set_scroll_pos, <overlay_no>, <value_fixed_point>, [<horizontal>]), #Sets <overlay_no>'s scroll pos <value_fixed_point> (requires WSE2)

lhs_operations += [
	try_for_agents,
	agent_get_ammo_for_slot,
	agent_get_item_cur_ammo,
	agent_get_damage_modifier,
	agent_get_accuracy_modifier,
	agent_get_speed_modifier,
	agent_get_reload_speed_modifier,
	agent_get_use_speed_modifier,
	store_trigger_param,
	store_random,
	store_random_in_range,
	face_keys_get_morph_key,
	val_shr,
	store_shr,
	val_lshr,
	store_lshr,
	val_shl,
	store_shl,
	val_xor,
	store_xor,
	val_not,
	store_not,
	player_get_wse2_version,
	player_get_party_id,
	register_get,
	store_wse_version,
	store_current_trigger,
	store_num_return_values,
	store_return_value,
	mtrand,
	get_time,
	timer_get_elapsed_time,
	get_main_party,
	store_application_time,
	get_campaign_time,
	game_key_get_key,
	dict_create,
	dict_get_size,
	dict_get_int,
	agent_get_item_modifier,
	agent_get_item_slot_modifier,
	agent_get_animation_progress,
	agent_get_dna,
	agent_get_ground_scene_prop,
	agent_get_item_slot_hit_points,
	agent_get_wielded_item_slot_no,
	agent_get_scale,
	agent_get_item_slot_flags,
	agent_get_personal_animation,
	agent_get_ranged_damage_modifier,
	agent_body_meta_mesh_get_current_deform_progress,
	agent_body_meta_mesh_get_current_deform_frame,
	agent_get_horse_rotation_velocity,
	agent_get_current_vertical_speed,
	agent_get_current_ai_mesh_face_group,
	agent_get_time_speed_multiplier,
	agent_get_action_speed_modifier,
	multiplayer_get_cur_profile,
	multiplayer_get_num_profiles,
	multiplayer_cur_message_get_int,
	multiplayer_cur_profile_get_skin,
	server_map_rotation_get_count,
	server_map_rotation_get_index,
	server_map_rotation_get_map,
	server_get_horse_friendly_fire,
	server_get_show_crosshair,
	get_server_option_at_connect,
	store_cur_mission_template_no,
	get_spectated_agent_no,
	get_water_level,
	prop_instance_get_sound_progress,
	cast_ray_agents,
	troop_get_skill_points,
	troop_get_attribute_points,
	troop_get_proficiency_points,
	party_stack_get_experience,
	party_stack_get_num_upgradeable,
	party_get_banner_icon,
	party_get_extra_icon,
	party_get_player_id,
	position_get_vector_to_position,
	position_get_length,
	get_dot_product_of_positions,
	str_length,
	str_index_of,
	str_last_index_of,
	str_get_char,
	str_to_num,
	str_compare,
	str_split,
	str_regex_get_matches,
	options_get_verbose_casualties,
	options_get_cheat_mode,
	options_get_realistic_headshots,
	fst,
	edit_mode_get_num_selected_prop_instances,
	edit_mode_get_selected_prop_instance,
	edit_mode_get_highlighted_prop_instance,
	menu_create_new,
	overlay_get_val,
	overlay_get_scroll_pos,
	array_create,
	array_copy,
	array_load_file,
	array_get_val,
	array_pop,
	array_get_dim_size,
	array_get_dim_count,
	array_get_type_id,
	lua_get_top,
	lua_to_int,
	lua_get_type,
]

can_fail_operations += [
	key_is_down,
	key_clicked,
	game_key_is_down,
	game_key_clicked,
	is_vanilla_warband,
	item_slot_gt,
	party_template_slot_gt,
	troop_slot_gt,
	faction_slot_gt,
	quest_slot_gt,
	scene_slot_gt,
	party_slot_gt,
	player_slot_gt,
	team_slot_gt,
	agent_slot_gt,
	scene_prop_slot_gt,
	order_flag_is_active,
	is_party_skill,
	profiler_is_recording,
	key_released,
	game_key_released,
	dict_is_empty,
	dict_has_key,
	multiplayer_is_campaign,
	missile_is_valid,
	cast_ray_agents,
	troop_has_flag,
	party_has_flag,
	party_is_non_player,
	str_equals,
	str_contains,
	str_starts_with,
	str_ends_with,
	str_is_alpha,
	str_is_digit,
	str_is_whitespace,
	str_is_integer,
	str_regex_match,
	str_regex_search,
	feq,
	fgt,
	flt,
	fge,
	fle,
	edit_mode_in_edit_objects_mode,
	presentation_activate,
	array_eq,
	array_neq,
	array_gt,
	array_ge,
	array_lt,
	array_le,
	lua_call,
	lua_triggerCallback,
]
