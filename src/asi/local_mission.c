#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "local_mission.h"
#include "modglobals.h"

extern void coop_log(const char *fmt, ...);

int local_mission_fixup(volatile int *meta, int game_type, int req_idx, int party_idx) {
    int party_no;
    int kind;
    int prev;

    if (game_type != GAME_TYPE_CAMPAIGN_CLIENT) return LOCAL_MISSION_NONE;

    kind = modglobals_get_int(req_idx, LOCAL_MISSION_NONE);
    if (kind != LOCAL_MISSION_BATTLE && kind != LOCAL_MISSION_VISIT) return LOCAL_MISSION_NONE;

    /* One request per mission: clear before validating so a bad request
       cannot linger and arm a later, unrelated mission. */
    modglobals_set(req_idx, LOCAL_MISSION_NONE);

    party_no = modglobals_get_int(party_idx, -1);
    if (party_no < 0) {
        coop_log("metaMission fixup: kind=%d but $g_encountered_party=%d, request dropped\n",
                 kind, party_no);
        return LOCAL_MISSION_NONE;
    }

    /* The request owns the whole record. setParams copies every field from
       here and mbMission::start/frameMove never read it again, so a prior
       encounter left in place would be spawned as this mission's parties. */
    prev = meta[0];
    meta[0] = party_no;                                 /* +0x00 encounteredParties[0] */
    meta[1] = -1;                                       /* +0x04 encounteredParties[1] */
    *(int *)((BYTE *)meta + 0x0C) = 0;                  /* m_type (0 = field)          */
    *(int *)((BYTE *)meta + 0x18) = 0;                  /* m_mainPartySide             */
    /* A hostile encounter puts the encountered party on the opposing side so
       party-sourced entries spawn as enemies. A visit mirrors the record
       mbMetaMission::startMapEvent writes for a peaceful map encounter. */
    *(int *)((BYTE *)meta + 0x24) = (kind == LOCAL_MISSION_BATTLE) ? 1 : 0;  /* m_enemySide */
    *(int *)((BYTE *)meta + 0x30) = 1;                  /* m_inEvent                   */
    *(int *)((BYTE *)meta + 0x44) = 1;                  /* m_enemiesPresent            */

    coop_log("metaMission fixup: kind=%d encountered_party=%d written to 0x%X (prior meta[0]=%d)\n",
             kind, party_no, (unsigned int)(DWORD_PTR)meta, prev);
    return kind;
}

int local_mission_end(volatile int *in_mission, int *kind, int *game_type) {
    int visit;
    if (!*in_mission) return 0;
    *in_mission = 0;
    *game_type = GAME_TYPE_CAMPAIGN_CLIENT;
    coop_log("mission-end transition: gameType restored to 4\n");
    visit = (*kind == LOCAL_MISSION_VISIT);
    *kind = LOCAL_MISSION_NONE;
    return visit;
}

int create_agent_player_no(int game_type, int troop, int player_no,
                           int player_troop, int my_player) {
    if (game_type != GAME_TYPE_CAMPAIGN_CLIENT) return player_no;
    if (player_no != -1) return player_no;
    if (troop != player_troop) return player_no;
    if (my_player < 0) return player_no;  /* no MP player object */
    return my_player;
}
