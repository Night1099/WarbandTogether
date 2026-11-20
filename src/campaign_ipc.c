#include "campaign_ipc.h"
#include "modglobals.h"

extern void coop_log(const char *fmt, ...);

void ipc_slots_publish_mask(ipc_slots *s) {
    int i, mask = 0;
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++)
        if (s->peer[i]) mask |= (1 << i);
    modglobals_set(s->gv->slots_online, mask);
    /* Republished ~1/s from the net thread -- log changes only */
    if (mask != s->last_logged_mask) {
        coop_log("[ipc] slots online mask = 0x%X\n", mask);
        s->last_logged_mask = mask;
    }
}

void ipc_slots_on_event(ipc_slots *s, void *peer, int connected) {
    int i;
    if (connected) return;   /* slot is learned from HELLO, not CONNECT */
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++) {
        if (s->peer[i] == peer) {
            s->peer[i] = NULL;
            coop_log("[ipc] battle slot %d disconnected\n", i);
            if (modglobals_get_int(s->gv->in_progress[i], 0) == 1) {
                modglobals_set(s->gv->ended[i], 1);
                coop_log("[ipc] slot %d was in progress -> flagged ended (abort)\n", i);
            }
        }
    }
    ipc_slots_publish_mask(s);
}

void ipc_slots_on_packet(ipc_slots *s, void *peer, const uint8_t *data, int len) {
    if (len < 1) return;
    switch (data[0]) {
    case PKT_BATTLE_HELLO: {
        battle_hello_t hello;
        if (pkt_read(data, len, &hello, sizeof(hello)) &&
            hello.slot < IPC_MAX_BATTLE_SLOTS) {
            s->peer[hello.slot] = peer;
            coop_log("[ipc] HELLO: battle slot %d online\n", hello.slot);
            ipc_slots_publish_mask(s);
        } else {
            coop_log("[ipc] bad HELLO (len=%d)\n", len);
        }
        break;
    }
    case PKT_BATTLE_END: {
        battle_end_signal_t sig;
        if (pkt_read(data, len, &sig, sizeof(sig)) &&
            sig.slot < IPC_MAX_BATTLE_SLOTS) {
            coop_log("[ipc] PKT_BATTLE_END: slot=%d winner=%d atk_cas=%d def_cas=%d players=%d\n",
                     sig.slot, sig.winner, sig.attacker_casualties,
                     sig.defender_casualties, sig.player_count);
            modglobals_set(s->gv->ended[sig.slot], 1);
            coop_log("[ipc] set $g_coop_battle_ended_%d = 1\n", sig.slot);
        } else {
            coop_log("[ipc] PKT_BATTLE_END bad/short (%d bytes)\n", len);
        }
        break;
    }
    default:
        coop_log("[ipc] unknown packet type=0x%02X len=%d\n", data[0], len);
        break;
    }
}
