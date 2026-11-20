/*
 * steam_tunnel.h - Steam P2P tunnel beneath mbnet (client ASI only).
 *
 * Pure core (this header's first half) is unit-tested in tests/c.
 * The tunnel thread itself (steam_tunnel_start) owns every Steam call.
 * Design: docs/superpowers/specs/2026-07-26-steam-networking-design.md.
 */
#ifndef STEAM_TUNNEL_H
#define STEAM_TUNNEL_H

#include "steam_flat.h"

#define STEAM_NUM_VPORTS   5     /* vport 0 = campaign, 1..4 = battle slots */
#define STEAM_MAX_ALLOWED  16
#define STEAM_MAX_RELAYS   40    /* host: one per (remote client x vport) */
#define STEAM_INVITE_MAX   64    /* max length of invite connect string */

#define STEAM_ROLE_OFF     0
#define STEAM_ROLE_HOST    1
#define STEAM_ROLE_CLIENT  2

/* Client-role verdict, published by the tunnel thread. PENDING exists so
   one-shot consumers (the browser injection) can wait for a settled
   address instead of latching the wrong one. */
#define STEAM_CLI_DOWN     0   /* no client role, or the ladder fell to LAN */
#define STEAM_CLI_PENDING  1   /* client role configured, verdict not in yet */
#define STEAM_CLI_UP       2   /* proxy live -- loopback re-aim is in effect */

/* port <-> vport: 7240 <-> 0, 7241+2s <-> 1+s (s = 0..3); -1 = not a coop port */
int steam_port_to_vport(int port);
int steam_vport_to_port(int vport);

typedef struct {
    int  host;                          /* [Steam] SteamHost */
    int  debug;                         /* [Steam] Debug: GNS verbose narration */
    unsigned __int64 host_steamid;      /* parsed HostSteamID64 (client role) */
    unsigned __int64 allowed[STEAM_MAX_ALLOWED];
    int  allowed_count;
    int  role;                          /* STEAM_ROLE_* -- set by finalize */
    char err[160];                      /* non-empty on config error */
    int  has_password;                  /* [Coop] Password non-empty -- presence only, value never enters the tunnel */
} steam_cfg_t;

/* Validates raw ini strings into cfg. Returns 1 on success (role set,
   possibly OFF when no key present), 0 on any config error (role OFF,
   err set -- caller falls back to LAN). */
int steam_cfg_finalize(steam_cfg_t *c, const char *steamid_str,
                       const char *allowlist_str);

/* "coop:<id64>" or "coop:<id64>:pw". build returns len (>0) or 0 if out_size too small. */
int steam_invite_build(char *out, int out_size, unsigned __int64 host_id, int pw);

/* 1 = ok (*host_id nonzero, *pw 0/1); 0 = malformed (outputs untouched). */
int steam_invite_parse(const char *s, unsigned __int64 *host_id, int *pw);

/* Auto-join on invite landing (pure core; the engine-side fire lives in
   coop.c's FrameMove hook). verdict: 1 = arm auto-join at tunnel-UP,
   0 = keep the notify-only landing (passworded host, no local password
   to supply). window_action classifies the engine's open-window stack
   (bottom..top, `count` entries): SELF = a mode-6-safe window is active
   and proceeds on m_switchingModule alone; WAIT = a modal dialog (or
   boot) blocks everything, do nothing; WAIT_NATIVE = a live mission /
   the campaign map is in the stack -- set m_connectToServer and let the
   map/tactical native arms consume it; NAVIGATE = dead zone, force the
   loading-window mode-6 route. */
#define STEAM_AJ_NAVIGATE    0
#define STEAM_AJ_SELF        1
#define STEAM_AJ_WAIT        2
#define STEAM_AJ_WAIT_NATIVE 3
int steam_autojoin_verdict(int invite_pw, int has_local_password);
int steam_autojoin_window_action(const int *stack, int count);

/* Poll-style Steamworks call-result wrapper. init is pure (harness-tested);
   arming/cancelling live in steam_tunnel.c and run on the tunnel thread
   only. Steam completes it through the vtable's 3-arg RunIO slot; the
   caller polls .done from the same thread that pumps callbacks, then reads
   .io_failure and the result buffer. */
typedef struct {
    sf_cbase_t base;            /* MUST stay first: Steam sees a CCallbackBase* */
    volatile long done;
    unsigned char io_failure;
    int cap;                    /* result buffer size == expected payload size */
    void *result;               /* caller-owned */
    int armed;                  /* RegisterCallResult outstanding */
    unsigned __int64 hcall;     /* handle it was armed against */
} steam_callresult_t;

void steam_callresult_init(steam_callresult_t *cr, void *result_buf, int cap,
                           int iCallback);

/* Host-side relay bookkeeping: one entry per accepted Steam connection
   (= one remote client on one vport), holding its loopback UDP socket.
   conn == 0 marks a free slot. */
typedef struct {
    unsigned int conn;    /* HSteamNetConnection */
    int          vport;
    unsigned int sock;    /* SOCKET (x86: fits an unsigned int) */
    unsigned __int64 steamid;   /* remote peer, for telemetry lines */
} steam_relay_t;

void           steam_relay_init(steam_relay_t *t, int cap);
steam_relay_t *steam_relay_add(steam_relay_t *t, int cap,
                               unsigned int conn, int vport, unsigned int sock);
steam_relay_t *steam_relay_by_conn(steam_relay_t *t, int cap, unsigned int conn);
int            steam_relay_remove(steam_relay_t *t, int cap, unsigned int conn);

/* Starts the tunnel thread, which owns every Steam call -- always, even for
   role OFF (an empty [Steam] section): the thread idles in invite standby so
   a later Join Game invite can promote it to CLIENT. OFF opens no sockets
   and publishes no client verdict, so pure-LAN play is unaffected. Only a
   config error (cfg->err set) skips the thread. The cfg snapshot is taken
   by value. */
void steam_tunnel_start(const steam_cfg_t *cfg);

/* 1 while the client proxy is fully live (all listeners bound, relay loop
   running); drops back to 0 if the tunnel dies. coop.c polls this to swap
   g_cfg.host_ip between 127.0.0.1 and the configured LAN address. */
int steam_tunnel_client_is_up(void);

/* STEAM_CLI_* -- the same verdict as a tri-state, so a consumer that can
   only act once can wait out PENDING. */
int steam_tunnel_client_state(void);

/* 1 if the most recently accepted Join Game invite carried ":pw" -- Task 10
   variant B reads this to auto-fill the password on the promoted client. */
int steam_tunnel_invite_pw(void);

/* Auto-join arm handshake: the tunnel thread sets armed for a qualifying
   invite landing; coop.c's FrameMove hook -- the sole engine-memory
   writer -- consumes it and clears on completion, refusal, or timeout.
   armed() returns the kind: TUNNEL = promoted joiner, fire only while the
   client proxy is UP (address is the loopback re-aim); LOCAL = the host
   machine joining its own server over LAN (no tunnel involvement). */
#define STEAM_AUTOJOIN_TUNNEL 1
#define STEAM_AUTOJOIN_LOCAL  2
int  steam_tunnel_autojoin_armed(void);
void steam_tunnel_autojoin_clear(void);
/* External arm (post-battle campaign return hop in coop.c). */
void steam_tunnel_autojoin_arm(int kind);

/* Low dword of the local SteamID64, published by the tunnel thread as soon
   as Steam is usable -- for every role, including OFF standby. 0 if Steam
   is unavailable or not yet up. */
unsigned int steam_tunnel_local_acctid(void);

/* 1 once a Steam-needing role (host/client) has waited out the self-init
   grace and Steam still isn't running; 0 while Steam is up or the role is
   OFF. coop.c republishes this to $g_coop_steam_missing so the module can
   show the host an in-game "Steam not running" warning. */
int steam_tunnel_steam_missing(void);

#endif /* STEAM_TUNNEL_H */
