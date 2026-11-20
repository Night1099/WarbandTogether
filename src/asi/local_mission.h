/* local_mission -- missions a campaign client starts itself.
 *
 * The module sets $g_coop_asi_local_mission to the kind right before
 * change_screen_mission. At mbMission::setParams the ASI writes the whole
 * mbMetaMission record for that kind; while the mission runs gameType is
 * held at 0 (an engine at gameType 4 gives the player no control), and at
 * the mission-end transition it goes back to 4.
 */

#ifndef COOP_LOCAL_MISSION_H
#define COOP_LOCAL_MISSION_H

/* module_constants.py coop_asi_local_mission_* */
#define LOCAL_MISSION_NONE   0
#define LOCAL_MISSION_BATTLE 1
#define LOCAL_MISSION_VISIT  2

#define GAME_TYPE_CAMPAIGN_CLIENT 4

/* At setParams on gameType 4: consumes the request global (cleared before
   it is validated, so a bad request never arms a later mission) and, when
   $g_encountered_party is set, writes the mbMetaMission record (meta =
   its first int). Returns the kind armed, or LOCAL_MISSION_NONE when
   nothing was written. */
int local_mission_fixup(volatile int *meta, int game_type, int req_idx, int party_idx);

/* At the mission-end transition: when a local mission is running, clears
   it, sets *game_type back to 4 and the kind to NONE. Returns 1 when the
   mission was a visit (the caller arms the return hop: a visit has no
   debrief), else 0. */
int local_mission_end(volatile int *in_mission, int *kind, int *game_type);

/* createAgent's playerNo: on gameType 4 an agent created for the player's
   own troop with playerNo -1 gets the local player's number, so the
   engine's MP attach binds it. Every other call keeps player_no. */
int create_agent_player_no(int game_type, int troop, int player_no,
                           int player_troop, int my_player);

#endif
