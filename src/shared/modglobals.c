#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>
#include "modglobals.h"

extern void coop_log(const char *fmt, ...);

static modglobals_desc g_desc;

void modglobals_init(const modglobals_desc *desc) {
    g_desc = *desc;
}

static __int64 *elem_ptr(int idx) {
    unsigned int first, last, byte_off;
    if (idx < 0 || !g_desc.vec_first_addr) return 0;
    first = *(unsigned int *)g_desc.vec_first_addr;
    last  = *(unsigned int *)g_desc.vec_last_addr;
    if (!first || last <= first) return 0;
    byte_off = (unsigned int)idx * 8;
    if (byte_off + 8 > last - first) return 0;
    return (__int64 *)(first + byte_off);
}

int modglobals_get(int idx, __int64 *out) {
    __int64 *p = elem_ptr(idx);
    if (!p) return 0;
    *out = *p;
    return 1;
}

int modglobals_set(int idx, __int64 val) {
    __int64 *p = elem_ptr(idx);
    if (!p) return 0;
    *p = val;
    return 1;
}

int modglobals_get_int(int idx, int fallback) {
    __int64 v;
    return modglobals_get(idx, &v) ? (int)v : fallback;
}

void modglobals_resolve(const char *vars_path,
                        const char *const names[], int idx_out[], int n) {
    char line[256];
    int i, idx = 0;
    FILE *f;

    for (i = 0; i < n; i++) idx_out[i] = -1;

    f = fopen(vars_path, "r");
    if (!f) {
        coop_log("modglobals: variables.txt open failed: %s\n", vars_path);
        return;
    }
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r' ||
                       line[len-1] == ' '  || line[len-1] == '\t'))
            line[--len] = 0;
        for (i = 0; i < n; i++)
            if (idx_out[i] < 0 && strcmp(line, names[i]) == 0)
                idx_out[i] = idx;
        idx++;
    }
    fclose(f);

    for (i = 0; i < n; i++)
        if (idx_out[i] < 0)
            coop_log("modglobals: %s not found in %s (%d lines scanned)\n",
                     names[i], vars_path, idx);
}
