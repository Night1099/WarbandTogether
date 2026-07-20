#include "hook.h"
#include <string.h>
#include <stdio.h>

extern void coop_log(const char *fmt, ...);

int hook_install(DWORD target_addr, void *detour_func, int bytes_to_copy,
                 BYTE *saved_bytes, DWORD *trampoline_addr) {
    DWORD old_protect;
    BYTE *target = (BYTE *)target_addr;
    BYTE *tramp;
    DWORD rel;
    int i;

    if (bytes_to_copy < 5) return 0;

    memcpy(saved_bytes, target, bytes_to_copy);

    /* Trampoline: original bytes + JMP back to (target + bytes_to_copy) */
    tramp = (BYTE *)VirtualAlloc(NULL, bytes_to_copy + 8,
                                  MEM_COMMIT | MEM_RESERVE,
                                  PAGE_EXECUTE_READWRITE);
    if (!tramp) return 0;

    memcpy(tramp, saved_bytes, bytes_to_copy);
    tramp[bytes_to_copy] = 0xE9;
    rel = (DWORD)(target + bytes_to_copy) - (DWORD)(tramp + bytes_to_copy + 5);
    *(DWORD *)(tramp + bytes_to_copy + 1) = rel;

    *trampoline_addr = (DWORD)tramp;

    {
        MEMORY_BASIC_INFORMATION mbi;
        VirtualQuery(tramp, &mbi, sizeof(mbi));
        coop_log("hook: tramp=%p target=0x%08X detour=%p bytes=%d protect=0x%X\n",
                 tramp, target_addr, detour_func, bytes_to_copy, mbi.Protect);
        coop_log("hook: tramp bytes: %02X %02X %02X %02X %02X | jmp_back_rel=0x%08X -> 0x%08X\n",
                 tramp[0], tramp[1], tramp[2], tramp[3], tramp[4],
                 *(DWORD*)(tramp + bytes_to_copy + 1),
                 (DWORD)(tramp + bytes_to_copy + 5) + *(DWORD*)(tramp + bytes_to_copy + 1));
    }

    /* Overwrite target: JMP detour + NOP padding */
    VirtualProtect(target, bytes_to_copy, PAGE_EXECUTE_READWRITE, &old_protect);
    target[0] = 0xE9;
    rel = (DWORD)detour_func - (DWORD)(target + 5);
    *(DWORD *)(target + 1) = rel;
    for (i = 5; i < bytes_to_copy; i++)
        target[i] = 0x90; /* NOP */
    VirtualProtect(target, bytes_to_copy, old_protect, &old_protect);

    return 1;
}

void hook_remove(DWORD target_addr, const BYTE *saved_bytes, int bytes_to_copy) {
    DWORD old_protect;
    BYTE *target = (BYTE *)target_addr;
    VirtualProtect(target, bytes_to_copy, PAGE_EXECUTE_READWRITE, &old_protect);
    memcpy(target, saved_bytes, bytes_to_copy);
    VirtualProtect(target, bytes_to_copy, old_protect, &old_protect);
}
