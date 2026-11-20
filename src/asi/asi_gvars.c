#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include "asi_gvars.h"
#include "modglobals.h"

extern void coop_log(const char *fmt, ...);

void asi_gvars_resolve(asi_gvars *g, const char *vars_path) {
    enum { N_FIXED = 13, N_ALL = N_FIXED + 3 * LOCAL_RESULT_MAX_CAS };
    char cas_names[3 * LOCAL_RESULT_MAX_CAS][40];
    const char *names[N_ALL];
    int *dest[N_ALL];
    int idxs[N_ALL];
    int n = 0, ci;

    names[n] = "g_encountered_party";          dest[n] = &g->encountered_party;   n++;
    names[n] = "g_coop_asi_local_mission";     dest[n] = &g->asi_local_mission;   n++;
    names[n] = "g_coop_pending_local_result";  dest[n] = &g->pending.pending;     n++;
    names[n] = "$g_coop_pending_win_loss";     dest[n] = &g->pending.win_loss;    n++;
    names[n] = "$g_coop_pending_xp";           dest[n] = &g->pending.xp;          n++;
    names[n] = "$g_coop_pending_cas_count";    dest[n] = &g->pending.cas_count;   n++;
    names[n] = "g_coop_result_ready";          dest[n] = &g->result.ready;        n++;
    names[n] = "g_coop_result_win_loss";       dest[n] = &g->result.win_loss;     n++;
    names[n] = "g_coop_result_xp";             dest[n] = &g->result.xp;           n++;
    names[n] = "g_coop_result_cas_count";      dest[n] = &g->result.cas_count;    n++;
    names[n] = "g_coop_my_steam_acctid";       dest[n] = &g->my_steam_acctid;     n++;
    names[n] = "g_coop_steam_missing";         dest[n] = &g->steam_missing;       n++;
    names[n] = "g_coop_return_to_campaign";    dest[n] = &g->return_to_campaign;  n++;
    for (ci = 0; ci < LOCAL_RESULT_MAX_CAS; ci++) {
        _snprintf(cas_names[3*ci], sizeof(cas_names[0]),
                  "$g_coop_pending_cas_tid_%d", ci);
        names[n] = cas_names[3*ci];   dest[n] = &g->pending.cas_tid[ci];    n++;
        _snprintf(cas_names[3*ci+1], sizeof(cas_names[0]),
                  "$g_coop_pending_cas_killed_%d", ci);
        names[n] = cas_names[3*ci+1]; dest[n] = &g->pending.cas_killed[ci]; n++;
        _snprintf(cas_names[3*ci+2], sizeof(cas_names[0]),
                  "g_coop_result_cas_%d", ci);
        names[n] = cas_names[3*ci+2]; dest[n] = &g->result.cas[ci];         n++;
    }

    modglobals_resolve(vars_path, names, idxs, n);
    for (ci = 0; ci < n; ci++) *dest[ci] = idxs[ci];
    coop_log("modglobals: resolved %d ids (encountered_party=%d result_ready=%d)\n",
             n, g->encountered_party, g->result.ready);
}
