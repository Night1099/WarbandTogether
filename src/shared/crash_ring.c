#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "crash_ring.h"

void crash_ring_put(crash_ring_t *ring, const char *msg) {
    LONG slot = InterlockedIncrement(&ring->head) - 1;
    char *dst = ring->entry[slot & (CRASH_RING_SIZE - 1)];
    lstrcpynA(dst, msg, CRASH_RING_ENTRY_LEN);
}

int crash_ring_count(const crash_ring_t *ring) {
    return ring->head < CRASH_RING_SIZE ? ring->head : CRASH_RING_SIZE;
}

const char *crash_ring_line(const crash_ring_t *ring, int i) {
    int start = ring->head - crash_ring_count(ring);
    return ring->entry[(start + i) & (CRASH_RING_SIZE - 1)];
}
