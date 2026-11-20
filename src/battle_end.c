#include "battle_end.h"

extern void coop_log(const char *fmt, ...);

int battle_end_edge_step(battle_end_edge *e, __int64 battle_started) {
    int send = 0;

    if (battle_started == 1 && e->prev != 1) {
        e->sent = 0;
        coop_log("[battle] battle_started -> 1\n");
    }

    if (battle_started == -1 && e->prev != -1 && !e->sent) {
        coop_log("[battle] battle_started -> -1 (module save complete), collecting data...\n");
        send = 1;
        e->sent = 1;
    }

    e->prev = battle_started;
    return send;
}

int battle_hello_build(uint8_t *buf, int slot) {
    battle_hello_t hello;
    hello.slot = (uint8_t)slot;
    return pkt_write(buf, PKT_BATTLE_HELLO, &hello, sizeof(hello));
}

int battle_end_build(uint8_t *buf, int slot, int winner, int player_count) {
    battle_end_signal_t sig;
    memset(&sig, 0, sizeof(sig));
    sig.slot = (uint8_t)slot;
    sig.winner = (uint8_t)winner;
    sig.player_count = player_count;
    return pkt_write(buf, PKT_BATTLE_END, &sig, sizeof(sig));
}
