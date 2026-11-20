/* asi_gvars -- the module globals the client ASI reads and writes, resolved
 * to their variables.txt indices once per launch (indices shift on every
 * module rebuild).
 *
 * variables.txt carries a global the module assigns under its bare name,
 * and a global the module only reads as "$name" lines. The ASI resolves
 * each by the form the module build emits: the $g_coop_pending_* results
 * are written only by the ASI, so they are looked up with the "$".
 */

#ifndef COOP_ASI_GVARS_H
#define COOP_ASI_GVARS_H

#include "local_result.h"

typedef struct asi_gvars {
    int encountered_party;    /* $g_encountered_party */
    int asi_local_mission;    /* $g_coop_asi_local_mission: the kind requested before change_screen_mission */
    int my_steam_acctid;      /* $g_coop_my_steam_acctid: republished every 500 ms */
    int return_to_campaign;   /* $g_coop_return_to_campaign: "battle over", arm the return hop */
    int steam_missing;        /* $g_coop_steam_missing: 1 = a Steam role found no Steam */
    local_result_src result;  /* $g_coop_result_*: the debrief's result */
    local_result_dst pending; /* $g_coop_pending_*: the result loaded after a rejoin */
} asi_gvars;

/* Resolves every field; a name missing from the file stays -1. */
void asi_gvars_resolve(asi_gvars *g, const char *vars_path);

#endif
