#include <string.h>

#include "exe_personality.h"

static const char *exe_name(const char *exe_path) {
    const char *name = exe_path, *p;
    for (p = exe_path; *p; p++)
        if (*p == '\\' || *p == '/') name = p + 1;
    return name;
}

int coop_is_dedicated_exe(const char *exe_path) {
    return strstr(exe_name(exe_path), "dedicated") != NULL;
}

coop_mode_t coop_mode_from_exe(const char *exe_path) {
    return strstr(exe_name(exe_path), "dedicated_campaign") ? COOP_HOST : COOP_BATTLE;
}
