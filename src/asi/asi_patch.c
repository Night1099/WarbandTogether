#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>
#include "asi_patch.h"

int asi_patch_verified(unsigned char *addr, const unsigned char *expect, int n_expect,
                       const unsigned char *repl, int n_repl) {
    DWORD old_prot;
    int span = n_expect > n_repl ? n_expect : n_repl;
    int patched = 0;
    VirtualProtect(addr, span, PAGE_EXECUTE_READWRITE, &old_prot);
    if (memcmp(addr, expect, n_expect) == 0) {
        memcpy(addr, repl, n_repl);
        patched = 1;
    }
    VirtualProtect(addr, span, old_prot, &old_prot);
    return patched;
}
