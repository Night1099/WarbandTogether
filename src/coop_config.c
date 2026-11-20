#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

#include "coop_config.h"
#include "battle_ipc.h"
#include "wsedict.h"
#include "module_dir.h"

extern void coop_log(const char *fmt, ...);

int coop_battle_slot_from_env(const char *value) {
    int slot = value ? atoi(value) : 0;
    if (slot < 0 || slot >= IPC_MAX_BATTLE_SLOTS)
        slot = 0;
    return slot;
}

int coop_debug_reveal_from_env(const char *value) {
    return value ? atoi(value) != 0 : 0;
}

static void exe_dir(char *out, int out_size, const char *exe_path) {
    lstrcpynA(out, exe_path, out_size);
    module_dir(out);
}

void coop_variables_path(char *out, int out_size, const char *exe_path, const char *module) {
    exe_dir(out, out_size, exe_path);
    lstrcatA(out, "Modules\\");
    lstrcatA(out, module);
    lstrcatA(out, "\\variables.txt");
}

void coop_wse_dict_dir(char *out, int out_size, const char *exe_path, const char *module) {
    exe_dir(out, out_size, exe_path);
    lstrcatA(out, "WSE\\");
    lstrcatA(out, module);
    lstrcatA(out, "\\");
}

int coop_write_server_cfg(const char *dict_dir, coop_mode_t mode,
                          const char *password, int debug_reveal) {
    char path[MAX_PATH];
    const char *name = mode == COOP_HOST ? "coop server cfg campaign"
                                         : "coop server cfg battle";
    wsedict_t *d;
    int rc;
    _snprintf(path, sizeof(path), "%s%s.wsedict", dict_dir, name);
    d = wsedict_create();
    if (!d) return -1;
    wsedict_set_str(d, "server password", password);
    wsedict_set_int(d, "debug reveal", debug_reveal);
    rc = wsedict_save(d, path);
    if (rc == 0)
        coop_log("server cfg dict written (%s, password=%s, debug_reveal=%d)\n",
                 path, password[0] ? "set" : "none", debug_reveal);
    else
        coop_log("server cfg dict WRITE FAILED (%s)\n", path);
    wsedict_free(d);
    return rc;
}
