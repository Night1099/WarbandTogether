#pragma once
#include <windows.h>

/* Install a JMP hook at target_addr, redirecting to detour_func.
   bytes_to_copy: number of prologue bytes to save (>= 5, must be complete instructions).
   saved_bytes: caller buffer, at least bytes_to_copy in size.
   trampoline_addr: receives address of executable trampoline that runs
                    the original prologue then jumps back. */
int hook_install(DWORD target_addr, void *detour_func, int bytes_to_copy,
                 BYTE *saved_bytes, DWORD *trampoline_addr);

void hook_remove(DWORD target_addr, const BYTE *saved_bytes, int bytes_to_copy);
