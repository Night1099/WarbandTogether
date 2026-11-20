/* crash_ring -- the recent log lines a crash report ends with.
 *
 * coop_log puts every line here as well as in the log file, so a crash
 * report still shows what the plugin did last when the file was never
 * flushed. The ring keeps the last CRASH_RING_SIZE lines, each cut to
 * CRASH_RING_ENTRY_LEN - 1 characters, and reads them back oldest first.
 * Writers on any thread take a slot with one interlocked increment; a
 * report taken mid-write may show that one line torn.
 */

#ifndef CRASH_RING_H
#define CRASH_RING_H

#include <windows.h>

#define CRASH_RING_SIZE      128   /* power of two: slots wrap by mask */
#define CRASH_RING_ENTRY_LEN 256

typedef struct {
    char          entry[CRASH_RING_SIZE][CRASH_RING_ENTRY_LEN];
    volatile LONG head;   /* lines written so far */
} crash_ring_t;

void crash_ring_put(crash_ring_t *ring, const char *msg);

/* Lines a report shows: every line written, at most CRASH_RING_SIZE. */
int crash_ring_count(const crash_ring_t *ring);

/* Line i of those, 0 = the oldest still kept. */
const char *crash_ring_line(const crash_ring_t *ring, int i);

#endif
