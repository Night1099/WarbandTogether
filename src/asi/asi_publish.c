#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "asi_publish.h"

int host_ip_reaim(int *reaimed, int up, char *ip, int size, const char *lan) {
    if (up == *reaimed) return 0;
    *reaimed = up;
    lstrcpynA(ip, up ? ASI_LOOPBACK_IP : lan, size);
    return 1;
}

__int64 acctid_global_value(unsigned int acctid) {
    return acctid ? (__int64)acctid : -1;
}

int return_latch_step(int *latched, int value) {
    if (value == 1) {
        if (*latched) return 0;
        *latched = 1;
        return 1;
    }
    *latched = 0;
    return 0;
}
