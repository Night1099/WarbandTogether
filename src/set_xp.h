/* set_xp -- the plugin's consumer of the module's queued troop XP write.
 *
 * A module script sets $g_coop_set_xp_go = 1 with $g_coop_set_xp_troop and
 * $g_coop_set_xp_value; the plugin consumes it at the start of the next frame
 * (both personalities). It writes the exact XP -- the engine clamps a negative
 * add_xp_to_troop, so lowering XP needs this -- and the level that XP gives,
 * never the per-level points: those come from the saved character dict.
 */

#ifndef COOP_SET_XP_H
#define COOP_SET_XP_H

#include "coop_gvars.h"

typedef struct set_xp_troops {
    char      *arr;           /* mbGame troop array, MBTROOP_STRIDE apart */
    int        count;         /* mbGame::m_numTroops */
    const int *level_table;   /* g_levelTable, LEVEL_TABLE_ENTRIES ints */
    float      boundary_mult;
} set_xp_troops;

/* Fills *out from engine memory; returns 0 when no game exists yet. Called
   only when a request is pending. */
typedef int (*set_xp_troops_fn)(set_xp_troops *out);

void coop_set_xp_consume(const coop_gvars *g, set_xp_troops_fn troops);

#endif
