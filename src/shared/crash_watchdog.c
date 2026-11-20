#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "crash_watchdog.h"

int crash_watchdog_tick(crash_watchdog_t *w, LONG beat) {
    if (beat == 0) return 0;

    if (beat != w->last_beat) {
        w->stale_ms = 0;
        w->last_beat = beat;
        return 0;
    }
    w->stale_ms += CRASH_WATCHDOG_INTERVAL_MS;
    return w->stale_ms >= CRASH_WATCHDOG_TIMEOUT_MS;
}

void crash_watchdog_rearm(crash_watchdog_t *w, LONG beat) {
    w->stale_ms = 0;
    w->last_beat = beat;
}
