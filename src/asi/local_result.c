#define WIN32_LEAN_AND_MEAN
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <stdio.h>
#include "local_result.h"
#include "modglobals.h"

void coop_log(const char *fmt, ...);

static void result_path(char *path, const char *game_dir) {
    _snprintf(path, MAX_PATH, "%s\\%s", game_dir, LOCAL_RESULT_FILENAME);
    path[MAX_PATH-1] = 0;
}

void local_result_flush(const local_result_src *gv, const char *game_dir) {
    char path[MAX_PATH];
    FILE *f;
    int win, xp, cas_count, i, tid, killed;

    if (gv->ready < 0) return;
    if (modglobals_get_int(gv->ready, 0) != 1) return;
    modglobals_set(gv->ready, 0);

    win = modglobals_get_int(gv->win_loss, 0);
    xp  = modglobals_get_int(gv->xp, 0);
    cas_count = modglobals_get_int(gv->cas_count, 0);
    if (cas_count > LOCAL_RESULT_MAX_CAS) cas_count = LOCAL_RESULT_MAX_CAS;

    coop_log("flush_result: win=%d xp=%d cas=%d (from globals)\n", win, xp, cas_count);

    result_path(path, game_dir);
    f = fopen(path, "w");
    if (!f) { coop_log("flush_result: cannot write %s\n", path); return; }

    fprintf(f, "[Result]\n");
    fprintf(f, "valid=1\n");
    fprintf(f, "win_loss=%d\n", win);
    fprintf(f, "xp_after=%d\n", xp);

    for (i = 0; i < cas_count; i++) {
        int packed = modglobals_get_int(gv->cas[i], 0);
        tid    = packed / 1000;
        killed = packed % 1000;
        fprintf(f, "cas_%d_troop=%d\n", i, tid);
        fprintf(f, "cas_%d_killed=%d\n", i, killed);
        coop_log("flush_result: cas[%d] packed=%d troop=%d killed=%d\n", i, packed, tid, killed);
    }
    fprintf(f, "cas_count=%d\n", cas_count);
    fclose(f);
    coop_log("flush_result: written to %s\n", path);
}

void local_result_load(const local_result_dst *gv, const char *game_dir) {
    char path[MAX_PATH], key[32];
    int valid, win_loss, xp, cas_count, i, tid, killed;

    if (gv->pending < 0 || gv->win_loss < 0) return;
    if (modglobals_get_int(gv->pending, 0) != 0) return;

    result_path(path, game_dir);
    valid = GetPrivateProfileIntA("Result", "valid", 0, path);
    if (!valid) return;
    coop_log("check_pending: path=%s valid=%d\n", path, valid);

    win_loss  = GetPrivateProfileIntA("Result", "win_loss", 0, path);
    xp        = GetPrivateProfileIntA("Result", "xp_after", 0, path);
    cas_count = GetPrivateProfileIntA("Result", "cas_count", 0, path);
    if (cas_count > LOCAL_RESULT_MAX_CAS) cas_count = LOCAL_RESULT_MAX_CAS;

    modglobals_set(gv->pending, 1);
    modglobals_set(gv->win_loss, win_loss);
    if (gv->xp >= 0) modglobals_set(gv->xp, xp);
    if (gv->cas_count >= 0) modglobals_set(gv->cas_count, cas_count);

    for (i = 0; i < cas_count; i++) {
        _snprintf(key, sizeof(key), "cas_%d_troop", i);
        tid = GetPrivateProfileIntA("Result", key, 0, path);
        _snprintf(key, sizeof(key), "cas_%d_killed", i);
        killed = GetPrivateProfileIntA("Result", key, 0, path);
        if (gv->cas_tid[i] >= 0)
            modglobals_set(gv->cas_tid[i], tid);
        if (gv->cas_killed[i] >= 0)
            modglobals_set(gv->cas_killed[i], killed);
        coop_log("check_pending: cas[%d] troop=%d killed=%d\n", i, tid, killed);
    }

    coop_log("check_pending: win=%d xp=%d cas=%d\n", win_loss, xp, cas_count);
    DeleteFileA(path);
}
