#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>
#include "asi_config.h"

extern void coop_log(const char *fmt, ...);

static void read_steam(asi_config *c, const char *ini) {
    char steamid_str[32], allowlist_str[512];
    memset(&c->steam, 0, sizeof(c->steam));
    c->steam.host  = GetPrivateProfileIntA("Steam", "SteamHost", 0, ini);
    c->steam.debug = GetPrivateProfileIntA("Steam", "Debug", 0, ini);
    c->steam.has_password = (c->password[0] != '\0');
    GetPrivateProfileStringA("Steam", "HostSteamID64", "", steamid_str,
                             sizeof(steamid_str), ini);
    GetPrivateProfileStringA("Steam", "AllowedSteamIDs", "", allowlist_str,
                             sizeof(allowlist_str), ini);
    steam_cfg_finalize(&c->steam, steamid_str, allowlist_str);
    if (c->steam.role != STEAM_ROLE_OFF)
        coop_log("config: [Steam] role=%s\n",
                 c->steam.role == STEAM_ROLE_HOST ? "host" : "client");
}

void asi_config_read(asi_config *c, const char *ini) {
    GetPrivateProfileStringA("Coop", "HostIP",  "127.0.0.1",  c->host_ip,     sizeof(c->host_ip),    ini);
    lstrcpynA(c->host_ip_lan, c->host_ip, sizeof(c->host_ip_lan));
    GetPrivateProfileStringA("Coop", "Module",  "NativeCoop",  c->module_name,  sizeof(c->module_name),  ini);
    c->port        = GetPrivateProfileIntA("Coop", "Port",       7240, ini);
    c->battle_port = GetPrivateProfileIntA("Coop", "BattlePort", 7241, ini);
    GetPrivateProfileStringA("Coop", "Password", "", c->password, sizeof(c->password), ini);
    coop_log("config: host=%s port=%d battle=%d module=%s password=%s\n",
             c->host_ip, c->port, c->battle_port, c->module_name,
             c->password[0] != '\0' ? "set" : "none");
    /* rglstring_set_sso clamps to 47 chars (s57's rglString SSO); a longer
       password works for the campaign join but silently truncates on every
       battle-server hop. */
    if (strlen(c->password) > 47)
        coop_log("[coop] Password longer than 47 chars -- battle-server hop will truncate; shorten it\n");

    read_steam(c, ini);
}

void asi_game_dir(const char *exe, char *out, int size) {
    char *last_slash;
    lstrcpynA(out, exe, size);
    last_slash = strrchr(out, '\\');
    if (last_slash) *last_slash = '\0';
}
