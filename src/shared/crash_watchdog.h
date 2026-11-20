/* crash_watchdog -- when a stalled main thread earns a hang dump.
 *
 * The frame hook beats once per frame (crash_heartbeat) and a watchdog
 * thread looks every CRASH_WATCHDOG_INTERVAL_MS. A hang dump is due once
 * the beat count has not moved for CRASH_WATCHDOG_TIMEOUT_MS. Nothing is
 * due before the first beat: until the frame hook runs (loading) a
 * missing beat is not a hang. After a dump the stall clock restarts, so a
 * hang that lasts gets one dump per timeout.
 */

#ifndef CRASH_WATCHDOG_H
#define CRASH_WATCHDOG_H

#include <windows.h>

#define CRASH_WATCHDOG_INTERVAL_MS 5000
#define CRASH_WATCHDOG_TIMEOUT_MS  10000

typedef struct {
    LONG  last_beat;
    DWORD stale_ms;
} crash_watchdog_t;

/* One look, with the beat count read once. Returns 1 when a hang dump
   is due. */
int crash_watchdog_tick(crash_watchdog_t *w, LONG beat);

/* Restarts the stall clock after a dump, from the beat count read after
   the dump was written. */
void crash_watchdog_rearm(crash_watchdog_t *w, LONG beat);

#endif
