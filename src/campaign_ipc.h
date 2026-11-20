/* campaign_ipc -- the campaign server's battle-slot bookkeeping.
 *
 * Each battle server holds one IPC peer and names its pool slot with
 * PKT_BATTLE_HELLO. The campaign side keeps the peer -> slot table and
 * publishes it to the module:
 *   $g_coop_battle_slots_online   bit s set while slot s's peer is connected
 *   $g_coop_battle_ended_<s>      set to 1 on PKT_BATTLE_END for slot s, or
 *                                 when slot s's peer drops while the module's
 *                                 $g_coop_battle_in_progress_<s> is 1 (abort)
 * The module owns in_progress and consumes/clears ended.
 */

#ifndef COOP_CAMPAIGN_IPC_H
#define COOP_CAMPAIGN_IPC_H

#include <stdint.h>
#include "battle_ipc.h"

/* Resolved module-global indices (modglobals); -1 = unresolved. */
typedef struct ipc_slot_gvars {
    int slots_online;
    int ended[IPC_MAX_BATTLE_SLOTS];
    int in_progress[IPC_MAX_BATTLE_SLOTS];
} ipc_slot_gvars;

typedef struct ipc_slots {
    void          *peer[IPC_MAX_BATTLE_SLOTS];   /* NULL = slot offline */
    const ipc_slot_gvars *gv;                  /* resolved indices, owned by the caller */
    int            last_logged_mask;             /* start at -1 */
} ipc_slots;

/* A packet from a battle-server peer (HELLO or BATTLE_END). */
void ipc_slots_on_packet(ipc_slots *s, void *peer, const uint8_t *data, int len);

/* Peer connect/disconnect. A connect alone maps nothing: the slot is
   learned from HELLO. */
void ipc_slots_on_event(ipc_slots *s, void *peer, int connected);

/* Write the online mask to the module. Also called periodically: the
   module's startup zeroes the global after load. */
void ipc_slots_publish_mask(ipc_slots *s);

#endif
