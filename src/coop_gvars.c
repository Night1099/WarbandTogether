#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

#include "coop_gvars.h"
#include "modglobals.h"

extern void coop_log(const char *fmt, ...);

void coop_gvars_resolve(const char *variables_path, coop_gvars *out) {
    enum { N_FIXED = 8, N_ALL = N_FIXED + 2 * IPC_MAX_BATTLE_SLOTS };
    char slot_names[2 * IPC_MAX_BATTLE_SLOTS][40];
    const char *names[N_ALL];
    int *dest[N_ALL];
    int idx[N_ALL];
    int n = 0, i;

    names[n] = "g_round_ended";              dest[n] = &out->round_ended;      n++;
    names[n] = "coop_battle_started";        dest[n] = &out->battle_started;   n++;
    names[n] = "coop_battle_slot";           dest[n] = &out->battle_slot;      n++;
    names[n] = "g_coop_battle_slots_online"; dest[n] = &out->ipc.slots_online; n++;
    names[n] = "coop_winner_team";           dest[n] = &out->mp_winner;        n++;
    names[n] = "g_coop_set_xp_go";           dest[n] = &out->set_xp_go;        n++;
    names[n] = "g_coop_set_xp_troop";        dest[n] = &out->set_xp_troop;     n++;
    names[n] = "g_coop_set_xp_value";        dest[n] = &out->set_xp_value;     n++;
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++) {
        _snprintf(slot_names[2*i], sizeof(slot_names[0]),
                  "g_coop_battle_ended_%d", i);
        names[n] = slot_names[2*i];   dest[n] = &out->ipc.ended[i];       n++;
        _snprintf(slot_names[2*i+1], sizeof(slot_names[0]),
                  "g_coop_battle_in_progress_%d", i);
        names[n] = slot_names[2*i+1]; dest[n] = &out->ipc.in_progress[i]; n++;
    }

    modglobals_resolve(variables_path, names, idx, n);
    for (i = 0; i < n; i++) *dest[i] = idx[i];

    coop_log("battle globals: round_ended=%d battle_started=%d mp_winner=%d battle_slot=%d slots_online=%d\n",
             out->round_ended, out->battle_started, out->mp_winner,
             out->battle_slot, out->ipc.slots_online);
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++)
        coop_log("slot %d: battle_ended=%d in_progress=%d\n",
                 i, out->ipc.ended[i], out->ipc.in_progress[i]);
    coop_log("set_xp globals: go=%d troop=%d value=%d\n",
             out->set_xp_go, out->set_xp_troop, out->set_xp_value);
}
