#include <string.h>
#include "browser_row.h"
#include "asi_rglstring.h"
#include "steam_tunnel.h"

extern void coop_log(const char *fmt, ...);

int browser_row_exists(const char *first, const char *last, const char *ip, int port) {
    const char *row;
    if (!first) return 0;
    for (row = first; row < last; row += BROWSER_ROW_SIZE) {
        const char *row_ip = *(const char *const *)(row + 0x04);   /* m_ip rglString data */
        if (*(const int *)(row + 0x44) == port && row_ip && strcmp(row_ip, ip) == 0)
            return 1;
    }
    return 0;
}

void browser_row_fill(char *row, const char *ip, int port, const char *module, int passworded) {
    rglstring_init(row + 0x000, ip);                   /* m_ip */
    *(int *)(row + 0x040) = 1;                         /* m_ping */
    *(int *)(row + 0x044) = port;                      /* m_port */
    *(int *)(row + 0x048) = -1;                        /* m_siteNo (-1 = campaign, no active mission) */
    *(int *)(row + 0x04C) = -1;                        /* m_missionTemplateNo (-1 = campaign) */
    rglstring_init(row + 0x050, BROWSER_ROW_NAME);     /* m_name */
    rglstring_init(row + 0x090, module);               /* m_moduleName - must match g_moduleName (dir name) */
    rglstring_init(row + 0x0D0, "");                   /* m_siteName */
    rglstring_init(row + 0x110, "");                   /* m_gameTypeName */
    *(int *)(row + 0x150) = 0;                         /* m_numPlayers */
    *(int *)(row + 0x154) = 10;                        /* m_maxNumPlayers */
    *(int *)(row + 0x158) = passworded ? 1 : 0;        /* m_passworded */
    *(int *)(row + 0x15C) = 1;                         /* m_dedicated */
    *(int *)(row + 0x160) = 1170;                      /* m_gameVersion */
    *(int *)(row + 0x164) = 0;                         /* m_moduleVersion */
    *(int *)(row + 0x17C) = 1145;                      /* m_extendedVersion (0x479) */
}

int browser_inject_step(browser_inject *st, int game_type, int searching,
                        int (*cli_state)(void), const void *table) {
    if (game_type != st->last_mode) {
        coop_log("browser: gameType=%d (was %d)\n", game_type, st->last_mode);
        st->last_mode = game_type;
    }

    if (game_type != 4) return 0;

    /* Every scan wipes the engine's server list, taking our row with it --
       re-arm injection whenever a new scan starts so the row comes back
       after each refresh/join instead of once per process. */
    if (searching) {
        if (!st->searching_prev)
            coop_log("browser: scan started (injection re-armed)\n");
        st->searching_prev = 1;
        st->scan_was_active = 1;
        st->injected = 0;
        return 0;
    }
    st->searching_prev = 0;

    if (st->injected) return 0;

    /* Inject after LAN scan finishes (list is stable) */
    if (!st->scan_was_active) return 0;

    /* Injection is one-shot and the row is never corrected, so it must not
       fire while the Steam client verdict is still open -- a LAN address
       latched here would be unroutable for the rest of the session. */
    if (cli_state() == STEAM_CLI_PENDING) {
        if (!st->pending_logged) {
            coop_log("browser: injection held -- Steam client verdict PENDING\n");
            st->pending_logged = 1;
        }
        return 0;
    }
    st->pending_logged = 0;

    if (!table) {
        if (!st->null_table_logged) {
            coop_log("browser: injection waiting -- table widget null\n");
            st->null_table_logged = 1;
        }
        return 0;
    }
    st->null_table_logged = 0;

    coop_log("LAN scan done, injecting server entry\n");
    st->injected = 1;
    return 1;
}
