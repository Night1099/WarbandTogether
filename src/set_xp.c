#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "set_xp.h"
#include "modglobals.h"
#include "warband_addrs_wse2.h"
#include "xp.h"

extern void coop_log(const char *fmt, ...);

void coop_set_xp_consume(const coop_gvars *g, set_xp_troops_fn troops) {
    int go, troop_id, xp_value;
    set_xp_troops t;

    if (g->set_xp_go < 0) return;
    go = modglobals_get_int(g->set_xp_go, 0);
    if (go != 1) return;

    troop_id = modglobals_get_int(g->set_xp_troop, 0);
    xp_value = modglobals_get_int(g->set_xp_value, 0);
    if (troops(&t)) {
        /* m_experience at +0x164, m_level at +0x178 (same as client). */
        if (t.arr && troop_id >= 0 && troop_id < t.count) {
            char *troop = t.arr + (unsigned)troop_id * MBTROOP_STRIDE;
            int old_xp = *(int *)(troop + 0x164);
            *(int *)(troop + 0x164) = xp_value;
            /* Level only -- per-level point awards intentionally NOT granted here:
               points come from the saved character dict, not from this write. */
            *(int *)(troop + 0x178) = coop_level_from_xp(t.level_table,
                                                         LEVEL_TABLE_ENTRIES,
                                                         t.boundary_mult, xp_value);
            coop_log("[set_xp] troop=%d old_xp=%d new_xp=%d level=%d\n",
                     troop_id, old_xp, xp_value, *(int *)(troop + 0x178));
        } else if (t.arr) {
            coop_log("[set_xp] REJECT troop=%d out of range (num_troops=%d)\n",
                     troop_id, t.count);
        }
    }
    modglobals_set(g->set_xp_go, 0);
}
