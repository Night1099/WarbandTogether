/* crash_classify -- which exceptions get a crash report, and how an
 * access violation reads in it.
 *
 * The vectored handler sees every exception first-chance, also the ones
 * the engine or the CRT catch and recover from: MSVC C++ throws
 * (0xE06D7363), breakpoints, guard-page stack growth, OutputDebugString.
 * Only the fatal codes of the crash design spec, plus heap corruption,
 * get a report; every other code passes through untouched.
 */

#ifndef CRASH_CLASSIFY_H
#define CRASH_CLASSIFY_H

#include <windows.h>

int crash_is_fatal(DWORD code);

/* An access violation's ExceptionInformation[0]: 0 = "READ",
   1 = "WRITE", 8 = "DEP" (execute of a non-executable page). */
const char *crash_av_op(ULONG_PTR kind);

#endif
