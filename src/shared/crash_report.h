#pragma once
#include <windows.h>
#include "coop_campaign.h"

/* Initialize crash reporting: installs VEH handler, reserves stack for
   stack-overflow handling. Call from DllMain DLL_PROCESS_ATTACH.
   dll_instance: HINSTANCE from DllMain (used to resolve output directory).
   mode: COOP_HOST or COOP_BATTLE (written into crash reports). */
void crash_init(HINSTANCE dll_instance, coop_mode_t mode);

/* Remove VEH handler. Call from DllMain DLL_PROCESS_DETACH. */
void crash_shutdown(void);

/* Append a pre-formatted string to the ring buffer.
   Called from coop_log after writing to the log file.
   msg must be null-terminated, max 255 chars used. */
void crash_ring_write(const char *msg);

/* Call every frame from coop_on_frame to signal the watchdog thread.
   If no heartbeat for 10 seconds, watchdog writes a hang dump. */
void crash_heartbeat(void);
