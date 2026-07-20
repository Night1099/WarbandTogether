#pragma once
#include <stdint.h>
#include <string.h>

#define IPC_PORT              7242
#define IPC_MAX_BATTLE_SLOTS  4

/* The battle-server <-> campaign-server ENet IPC link (battle_net.c) is
   the only C-layer wire protocol. Framing: [0]=type, payload at
   +PKT_HDR_SIZE, fixed-struct payloads via pkt_write/pkt_read. */

#define PKT_BATTLE_HELLO      0x26  /* battle -> campaign: on IPC connect */
#define PKT_BATTLE_END        0x27  /* battle -> campaign: results on disk */

#define PKT_HDR_SIZE 1

static __inline int pkt_write(unsigned char *buf, unsigned char type,
                              const void *payload, int size) {
    buf[0] = type;
    if (payload && size > 0) memcpy(buf + PKT_HDR_SIZE, payload, size);
    return PKT_HDR_SIZE + size;
}

/* Returns 1 and fills out if the packet carries at least size bytes. */
static __inline int pkt_read(const unsigned char *data, int len,
                             void *out, int size) {
    if (len < PKT_HDR_SIZE + size) return 0;
    memcpy(out, data + PKT_HDR_SIZE, size);
    return 1;
}

#pragma pack(push, 1)
typedef struct {
    uint8_t slot;             /* this battle server's pool slot (0..3) */
} battle_hello_t;

/* PKT_BATTLE_END payload */
typedef struct {
    uint8_t  slot;            /* pool slot the battle ran on */
    uint8_t  winner;
    int32_t  attacker_casualties;
    int32_t  defender_casualties;
    int32_t  player_count;
} battle_end_signal_t;
#pragma pack(pop)
