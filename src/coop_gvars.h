/* coop_gvars -- the module globals the plugin reads and writes, resolved to
 * their variables.txt indices once per launch (indices shift on every module
 * rebuild). Each one must be ASSIGNED somewhere in module code: a global the
 * module only reads is emitted into variables.txt as "$name" lines, which
 * resolve to -1, and every plugin write to it is dropped.
 */

#ifndef COOP_GVARS_H
#define COOP_GVARS_H

#include "campaign_ipc.h"

typedef struct coop_gvars {
    int round_ended;      /* $g_round_ended */
    int battle_started;   /* $coop_battle_started: 1 battle on, -1 results saved */
    int battle_slot;      /* $coop_battle_slot: the battle server's pool slot */
    int mp_winner;        /* $coop_winner_team */
    int set_xp_go;        /* $g_coop_set_xp_go/_troop/_value: queued XP write */
    int set_xp_troop;
    int set_xp_value;
    ipc_slot_gvars ipc;   /* $g_coop_battle_slots_online, _ended_<s>, _in_progress_<s> */
} coop_gvars;

/* Every field -1 (unresolved). */
#define COOP_GVARS_UNRESOLVED \
    { -1, -1, -1, -1, -1, -1, -1, { -1, { -1, -1, -1, -1 }, { -1, -1, -1, -1 } } }

void coop_gvars_resolve(const char *variables_path, coop_gvars *out);

#endif
