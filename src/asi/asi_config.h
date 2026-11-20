/* asi_config -- the client ASI's coop.ini (the one next to the ASI).
 *
 * [Coop] HostIP/Port/BattlePort/Module/Password and the [Steam] keys that
 * pick the tunnel role. The password is never logged and never enters the
 * tunnel; only its presence does.
 */

#ifndef COOP_ASI_CONFIG_H
#define COOP_ASI_CONFIG_H

#include "steam_tunnel.h"

typedef struct asi_config {
    char host_ip[64];       /* the campaign server the browser row and s59 publish;
                               the Steam client proxy re-aims it at loopback */
    char host_ip_lan[64];   /* the HostIP= value, restored when the tunnel dies */
    int  port;
    int  battle_port;
    char module_name[64];   /* must equal the module's directory name */
    char password[64];      /* [Coop] Password= */
    steam_cfg_t steam;
} asi_config;

/* Reads ini (an absolute path); keys that are missing take their defaults
   (127.0.0.1, 7240, 7241, NativeCoop, no password, Steam role off). */
void asi_config_read(asi_config *c, const char *ini);

/* The game directory: exe's path without its last component. */
void asi_game_dir(const char *exe, char *out, int size);

#endif
