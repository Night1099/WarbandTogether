/* autojoin -- drives the engine into a campaign-server join from any screen.
 *
 * The Steam tunnel thread (an accepted invite) or the ASI (battle over,
 * visit over) arms the join with steam_tunnel_autojoin_arm; this driver,
 * run once per frame on the render thread, is the only writer of the
 * engine flags. RE: patches/Warband_WSE2/findings.md "Auto-join on invite
 * landing RE (2026-08-23)".
 */

#ifndef COOP_AUTOJOIN_H
#define COOP_AUTOJOIN_H

/* Generous by design: covers a player parked on a dead-zone screen the
   engine can't navigate away from (a modal dialog, a live SP battle). */
#define AUTOJOIN_TIMEOUT_MS 60000
/* Loading mode 6 falls through to the profiles window when there is no MP
   profile; past this many navigations the join is abandoned. */
#define AUTOJOIN_MAX_NAVS   5

typedef struct autojoin {
    int           active;     /* 0 idle, else the STEAM_AUTOJOIN_* kind */
    unsigned long arm_tick;
    int           navs;
} autojoin;

#define AUTOJOIN_INIT { 0, 0, 0 }

/* One frame's view of the engine. */
typedef struct autojoin_env {
    volatile unsigned char *switching_module;       /* g_basicGame.m_switchingModule */
    volatile unsigned char *switching_to_campaign;  /* m_switchingToCampaign */
    volatile unsigned char *connect_to_server;      /* m_connectToServer */
    const int *open_windows;    /* g_gameScreen.m_openWindows, active window last */
    int        n_open_windows;  /* 0 when the vector is empty or unallocated */
    char      *loading_window;  /* mbLoadingWindow*, NULL before it exists */
    int        tunnel_up;       /* steam_tunnel_client_is_up() */
    unsigned long now;          /* GetTickCount() */
    const char *host_ip;        /* the campaign server, loopback while the tunnel is up */
    int         port;
    const char *password;       /* [Coop] Password=, "" for an open server */
    void *stored_address;       /* g_basicGame.m_storedAddress (rglString) */
    void *stored_password;      /* g_basicGame.m_storedPassword (rglString) */
    void (*rgl_copy)(void *rgl_string, const char *value);   /* rglString::operator= */
    void (*set_window)(int window);                          /* mbGameScreen::setWindow */
} autojoin_env;

/* Arm: takes the pending kind, stores "ip:port" and the password, sets
   m_switchingModule and m_switchingToCampaign (never m_connectToServer).
   Then per frame: the engine clearing m_switchingModule (connect or
   reject), the timeout, or the tunnel dying under a tunnel join clears all
   three flags and the arm; on map/mission screens m_connectToServer is set
   for the native arm; from other dead-zone screens the loading window is
   sent to the MP browser in mode 6. */
void autojoin_step(autojoin *st, const autojoin_env *env);

#endif
