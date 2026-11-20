/* battle_end -- the battle server's side of the IPC link.
 *
 * The module sets $coop_battle_started to 1 when a battle starts and to -1
 * once coop_copy_parties_to_file_mp has dict_save'd the battle results, so
 * the -1 edge means "results are on disk": the plugin then sends
 * PKT_BATTLE_END, once per battle. HELLO names this server's pool slot on
 * every (re)connect.
 */

#ifndef COOP_BATTLE_END_H
#define COOP_BATTLE_END_H

#include <stdint.h>
#include "battle_ipc.h"

typedef struct battle_end_edge {
    __int64 prev;   /* last $coop_battle_started seen; start at 0 */
    int     sent;   /* PKT_BATTLE_END already sent for this battle */
} battle_end_edge;

/* Feed one poll's $coop_battle_started. Returns 1 when PKT_BATTLE_END must
   be sent now. */
int battle_end_edge_step(battle_end_edge *e, __int64 battle_started);

/* Packet builders: buf holds PKT_HDR_SIZE + the payload. Return the length. */
int battle_hello_build(uint8_t *buf, int slot);
int battle_end_build(uint8_t *buf, int slot, int winner, int player_count);

#endif
