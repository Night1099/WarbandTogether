#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "steam_tunnel.h"
#include "steam_flat.h"
#include "warband_addrs_wse2.h"

void coop_log(const char *fmt, ...);

/* The backend->Steam direction FD_SETs every live relay in one pass. */
typedef char steam_assert_relays_fit_fdset[(STEAM_MAX_RELAYS < FD_SETSIZE) ? 1 : -1];

int steam_port_to_vport(int port) {
    int s;
    if (port == 7240) return 0;
    for (s = 0; s < 4; s++)
        if (port == 7241 + 2 * s) return 1 + s;
    return -1;
}

int steam_vport_to_port(int vport) {
    if (vport == 0) return 7240;
    if (vport >= 1 && vport < STEAM_NUM_VPORTS) return 7241 + 2 * (vport - 1);
    return -1;
}

/* Strict SteamID64 parse: decimal digits only, non-zero, at most 20 digits
   (uint64 range) so a typo cannot wrap into a plausible-looking other ID.
   Returns 0 on error, and then leaves *endp untouched. */
static unsigned __int64 parse_steamid(const char *s, const char **endp) {
    unsigned __int64 v = 0;
    const char *p = s;
    int digits = 0;
    if (*p < '0' || *p > '9') return 0;
    while (*p >= '0' && *p <= '9') {
        if (++digits > 20) return 0;
        v = v * 10 + (unsigned)(*p - '0');
        p++;
    }
    if (endp) *endp = p;
    return v;
}

/* RE check 5 (Q6) on mbnetNetworkClient::receiveEvent @0x53F690 found the
   ping-reply parser always builds a brand-new mbnetServer row (mov
   [esi+0x158], eax @0x54393F) and never refreshes an existing row's
   m_passworded in place -- see patches/Warband_WSE2/findings.md
   "Phase 4 invites+password RE" Q6. That negative verdict means the
   browser row can go stale, so the rich-presence connect string must
   carry its own ":pw" suffix (Task 10 Variant B's `steam_tunnel_invite_pw`
   is the other consumer). One writer rule: if the engine ever gains an
   in-place refresh, this flips to 0 and the suffix stops shipping. */
#define STEAM_RP_PW_FLAG 1

int steam_invite_build(char *out, int out_size, unsigned __int64 host_id, int pw) {
    int n = _snprintf(out, out_size, pw ? "coop:%I64u:pw" : "coop:%I64u", host_id);
    if (n <= 0 || n >= out_size) { if (out_size > 0) out[0] = '\0'; return 0; }
    return n;
}

int steam_invite_parse(const char *s, unsigned __int64 *host_id, int *pw) {
    unsigned __int64 id;
    const char *p = s, *end = NULL;
    if (strncmp(p, "coop:", 5) != 0) return 0;
    p += 5;
    id = parse_steamid(p, &end);
    if (id == 0) return 0;
    if (*end == '\0')                       { *host_id = id; *pw = 0; return 1; }
    if (strcmp(end, ":pw") == 0)            { *host_id = id; *pw = 1; return 1; }
    return 0;
}

int steam_cfg_finalize(steam_cfg_t *c, const char *steamid_str,
                       const char *allowlist_str) {
    c->role = STEAM_ROLE_OFF;
    c->err[0] = '\0';
    c->allowed_count = 0;
    c->host_steamid = 0;

    if (c->host && steamid_str[0]) {
        _snprintf(c->err, sizeof(c->err),
                  "SteamHost and HostSteamID64 are mutually exclusive");
        return 0;
    }

    if (steamid_str[0]) {
        const char *end = steamid_str;
        c->host_steamid = parse_steamid(steamid_str, &end);
        if (c->host_steamid == 0 || *end != '\0') {
            _snprintf(c->err, sizeof(c->err),
                      "bad HostSteamID64 '%s'", steamid_str);
            return 0;
        }
        c->role = STEAM_ROLE_CLIENT;
        return 1;
    }

    if (c->host) {
        const char *p = allowlist_str;
        while (*p) {
            unsigned __int64 id;
            const char *end;
            while (*p == ' ' || *p == ',') p++;
            if (!*p) break;
            if (c->allowed_count >= STEAM_MAX_ALLOWED) {
                _snprintf(c->err, sizeof(c->err),
                          "AllowedSteamIDs: more than %d entries", STEAM_MAX_ALLOWED);
                c->allowed_count = 0;
                return 0;
            }
            id = parse_steamid(p, &end);
            if (id == 0 || (*end != '\0' && *end != ',' && *end != ' ')) {
                _snprintf(c->err, sizeof(c->err),
                          "AllowedSteamIDs: bad entry near '%.20s'", p);
                c->allowed_count = 0;
                return 0;
            }
            c->allowed[c->allowed_count++] = id;
            p = end;
        }
        c->role = STEAM_ROLE_HOST;
        return 1;
    }

    return 1;  /* no role key: OFF, not an error */
}

void steam_relay_init(steam_relay_t *t, int cap) {
    memset(t, 0, sizeof(*t) * cap);
}

steam_relay_t *steam_relay_add(steam_relay_t *t, int cap,
                               unsigned int conn, int vport, unsigned int sock) {
    int i, free_i = -1;
    if (conn == 0) return NULL;
    for (i = 0; i < cap; i++) {
        if (t[i].conn == conn) return NULL;        /* duplicate */
        if (t[i].conn == 0 && free_i < 0) free_i = i;
    }
    if (free_i < 0) return NULL;                   /* full */
    t[free_i].conn = conn;
    t[free_i].vport = vport;
    t[free_i].sock = sock;
    return &t[free_i];
}

steam_relay_t *steam_relay_by_conn(steam_relay_t *t, int cap, unsigned int conn) {
    int i;
    if (conn == 0) return NULL;
    for (i = 0; i < cap; i++)
        if (t[i].conn == conn) return &t[i];
    return NULL;
}

int steam_relay_remove(steam_relay_t *t, int cap, unsigned int conn) {
    steam_relay_t *r = steam_relay_by_conn(t, cap, conn);
    if (!r) return 0;
    memset(r, 0, sizeof(*r));
    return 1;
}

/* ------------------------------------------------------------------ */
/*  Tunnel state (single instance; tunnel thread owns all Steam calls) */
/* ------------------------------------------------------------------ */

typedef struct {
    steam_cfg_t cfg;
    volatile LONG client_up;              /* client role fully live */
    volatile LONG client_state;           /* STEAM_CLI_* */
    int client_dead;                      /* tunnel thread: unwind the loop */
    /* host role */
    HSteamListenSocket listen[STEAM_NUM_VPORTS];
    HSteamNetPollGroup pollgrp;
    steam_relay_t relays[STEAM_MAX_RELAYS];
    /* client role: one slot per vport */
    struct {
        SOCKET sock;                      /* loopback listener at the real port */
        HSteamNetConnection conn;         /* 0 = not connected */
        struct sockaddr_in engine_addr;   /* engine's source addr for replies */
        int engine_valid;
        int retries;                      /* bounded reconnects */
        DWORD last_attempt_tick;          /* rate-limits ConnectP2P attempts */
    } cv[STEAM_NUM_VPORTS];
} steam_tun_t;

/* cfg.role and cfg.host_steamid are MUTABLE after start: the invite drain
   (tunnel thread) may promote OFF->CLIENT or re-target CLIENT. Sole writer
   is the tunnel thread; steam_steamside_cleanup still never touches cfg. */
static steam_tun_t g_tun;

static DWORD g_start_tick;                /* steam_tunnel_start time */

int steam_tunnel_client_is_up(void) { return g_tun.client_up != 0; }

/* PENDING is meant to be a short pre-verdict window; a hung Steam init call
   would otherwise hold the browser injection forever. After the watchdog
   window the verdict is forced DOWN (LAN) -- reversible: the tunnel thread
   republishes UP if the proxy does come live later. */
#define STEAM_PENDING_WATCHDOG_MS 90000

int steam_tunnel_client_state(void) {
    if (g_tun.client_state == STEAM_CLI_PENDING &&
        GetTickCount() - g_start_tick > STEAM_PENDING_WATCHDOG_MS) {
        InterlockedExchange(&g_tun.client_state, STEAM_CLI_DOWN);
        coop_log("[steam] PENDING watchdog: no verdict after %ds -- LAN unblocked\n",
                 STEAM_PENDING_WATCHDOG_MS / 1000);
    }
    return (int)g_tun.client_state;
}

static void steam_host_run(void);
static void steam_client_run(void);
static void steam_standby_run(void);
static void steam_pump_callbacks(void);
static void steam_drain_events(void);
static void steam_drain_invite(void);

/* ------------------------------------------------------------------ */
/*  Status-changed event queue                                        */
/*                                                                    */
/*  Steam dispatches the config-201 callback from whichever pump runs  */
/*  first -- our per-interface RunCallbacks() or the engine's per-frame */
/*  SteamAPI_RunCallbacks() on the main thread. So the callback is NOT */
/*  thread-confined and must not touch a socket, the relay table or    */
/*  Steam itself: it copies the event here and the tunnel thread does  */
/*  all the work. A lock (not a lock-free SPSC ring) because those two */
/*  dispatchers can produce concurrently.                             */
/* ------------------------------------------------------------------ */

#define STEAM_EVQ_SIZE 32

typedef struct {
    HSteamNetConnection conn;
    HSteamListenSocket  listen;
    unsigned __int64    steamid;
    int                 state;
    int                 end_reason;
} steam_evt_t;

static steam_evt_t      g_evq[STEAM_EVQ_SIZE];
static int              g_evq_head, g_evq_tail, g_evq_count;
static CRITICAL_SECTION g_evq_cs;
static DWORD            g_tunnel_tid;
static volatile LONG    g_foreign_cb_logged;
static DWORD            g_role_start_tick;   /* SteamAPI pump grace anchor */
static DWORD            g_last_pump_tick;
static int              g_pump_started;

static void __cdecl steam_on_status_changed(SteamNetConnectionStatusChangedCallback_t *cb) {
    steam_evt_t e;
    int dropped = 0;

    if (GetCurrentThreadId() != g_tunnel_tid &&
        InterlockedExchange(&g_foreign_cb_logged, 1) == 0)
        coop_log("[steam] status callback dispatched on thread %u, tunnel thread is %u "
                 "-- work deferred to the tunnel thread as designed\n",
                 GetCurrentThreadId(), g_tunnel_tid);

    e.conn       = cb->m_hConn;
    e.listen     = cb->m_info.m_hListenSocket;
    e.steamid    = cb->m_info.m_identityRemote.u.m_steamID64;
    e.state      = cb->m_info.m_eState;
    e.end_reason = cb->m_info.m_eEndReason;

    coop_log("[steam] cb: conn=%u state %d->%d listen=%u id=%I64u reason=%d\n",
             e.conn, cb->m_eOldState, e.state, e.listen, e.steamid, e.end_reason);

    EnterCriticalSection(&g_evq_cs);
    if (g_evq_count < STEAM_EVQ_SIZE) {
        g_evq[g_evq_tail] = e;
        g_evq_tail = (g_evq_tail + 1) % STEAM_EVQ_SIZE;
        g_evq_count++;
    } else {
        dropped = 1;
    }
    LeaveCriticalSection(&g_evq_cs);

    /* Dropping is survivable: the state machine re-syncs on Steam's next
       event for that connection, and a full queue means the tunnel thread
       is wedged anyway. */
    if (dropped)
        coop_log("[steam] event queue full -- dropped state=%d conn=%u\n", e.state, e.conn);
}

static int steam_evq_pop(steam_evt_t *out) {
    int got = 0;
    EnterCriticalSection(&g_evq_cs);
    if (g_evq_count > 0) {
        *out = g_evq[g_evq_head];
        g_evq_head = (g_evq_head + 1) % STEAM_EVQ_SIZE;
        g_evq_count--;
        got = 1;
    }
    LeaveCriticalSection(&g_evq_cs);
    return got;
}

/* GNS debug narration -- fires on Steam's internal threads; log-only. */
static void __cdecl steam_on_debug_output(int nType, const char *pszMsg) {
    coop_log("[gns:%d] %s\n", nType, pszMsg);
}

/* ------------------------------------------------------------------ */
/*  Join Game (rich-presence) invite delivery                         */
/*                                                                    */
/*  Steam's plain-callback dispatch invokes the 1-arg Run slot; the   */
/*  3-arg RunIO exists only so the vtable shape matches CCallbackBase  */
/*  -- both funnel into the same body. Either slot can run on Steam's  */
/*  own dispatch thread (whichever pump gets there first), so, like    */
/*  the status-changed callback above, this must only copy and flag:   */
/*  the tunnel thread does the parse/refuse/accept work in             */
/*  steam_drain_invite. Last-writer-wins on the mailbox is correct --  */
/*  a newer click supersedes an unconsumed one.                        */
/* ------------------------------------------------------------------ */

static CRITICAL_SECTION g_invite_cs;      /* init beside g_evq_cs in steam_tunnel_start */
static char             g_invite_str[STEAM_INVITE_MAX];
static volatile LONG    g_invite_pending;
static volatile LONG    g_invite_pw;      /* set at accept time; steam_tunnel_invite_pw() */
/* Set at accept time alongside g_invite_pw; consumed by Task 7 (not yet
   wired to any reader here). */
static volatile LONG    g_invite_landed_pending;

static void __fastcall steam_cb_rp_run(sf_cbase_t *self, void *edx, void *pvParam) {
    sf_GameRichPresenceJoinRequested_t *p = (sf_GameRichPresenceJoinRequested_t *)pvParam;
    (void)self; (void)edx;
    EnterCriticalSection(&g_invite_cs);
    lstrcpynA(g_invite_str, p->m_rgchConnect, sizeof(g_invite_str));
    LeaveCriticalSection(&g_invite_cs);
    InterlockedExchange(&g_invite_pending, 1);
    coop_log("[steam] Join Game invite from %I64u: '%s'\n",
             p->m_steamIDFriend, p->m_rgchConnect);
}

static void __fastcall steam_cb_rp_runio(sf_cbase_t *self, void *edx, void *pvParam,
                                         unsigned char bIOFailure, unsigned __int64 hCall) {
    (void)bIOFailure; (void)hCall;
    steam_cb_rp_run(self, edx, pvParam);
}

static int __fastcall steam_cb_rp_size(sf_cbase_t *self, void *edx) {
    (void)self; (void)edx;
    return (int)sizeof(sf_GameRichPresenceJoinRequested_t);
}

/* Member order must match sf_cbase_vtbl_t's physical layout: RunIO (3-arg)
   first, then the 1-arg Run Steam's plain-callback dispatch actually
   calls, then GetCallbackSizeBytes -- MSVC reverses same-name virtual
   overloads (see steam_flat.h). */
static const sf_cbase_vtbl_t g_rp_vtbl = { steam_cb_rp_runio, steam_cb_rp_run, steam_cb_rp_size };
static sf_cbase_t g_rp_cb = { &g_rp_vtbl, 0, 0 };
static int g_rp_registered;

/* Q9 verdict (Task 1): connected-to-a-server state is BSS-plain and
   background-thread safe -- m_networkActive nonzero, m_actionCode == 7
   (join sent / session live), and m_gameType == 1 (multiplayer). All
   three read together to avoid false positives from LAN-search or
   chkserial states that also touch these fields. */
static int steam_engine_in_session(void) {
    return *(volatile unsigned char *)ADDR_NET_RUN_FLAG != 0 &&
           *(volatile int *)ADDR_NET_PROGRESS_STATE == 7 &&
           *(volatile int *)ADDR_MAP_INTERACTION_MODE == 1;
}

/* Q10 verdict (Task 1): the engine's displayMessage is unsafe off the
   render thread (touches font drawing, the mesh render queue and a
   std::deque with no locking), so this stays log-only. Kept as a single
   call site in case a safe main-thread path is added later. */
static void steam_notify(const char *msg) {
    coop_log("[steam] %s\n", msg);
}

/* Parses and acts on a pending invite: refuses cross-role/in-session/
   already-tunneled cases, otherwise promotes this session to CLIENT and
   ends any live client loop so the thread epilogue rebuilds against the
   new host. Called at the top of steam_drain_events so every role loop
   (including OFF standby) drains it. */
static void steam_drain_invite(void) {
    char raw[STEAM_INVITE_MAX];
    unsigned __int64 id;
    int pw;

    if (InterlockedExchange(&g_invite_pending, 0) == 0) return;
    EnterCriticalSection(&g_invite_cs);
    lstrcpynA(raw, g_invite_str, sizeof(raw));
    LeaveCriticalSection(&g_invite_cs);

    if (!steam_invite_parse(raw, &id, &pw)) {
        coop_log("[steam] malformed invite '%s' -- ignored\n", raw);
        return;
    }
    if (g_tun.cfg.role == STEAM_ROLE_HOST) {
        coop_log("[steam] invite ignored -- this machine is the host\n");
        return;
    }
    if (steam_engine_in_session()) {
        steam_notify("Join Game: leave the current server first, then click again");
        return;
    }
    if (g_tun.cfg.role == STEAM_ROLE_CLIENT && g_tun.cfg.host_steamid == id &&
        steam_tunnel_client_is_up()) {
        steam_notify("Join Game: tunnel to this host is already up -- join via the MP browser");
        return;
    }

    coop_log("[steam] invite accepted: host=%I64u pw=%d -- rebuilding as client\n", id, pw);
    g_tun.cfg.host_steamid = id;
    g_tun.cfg.role = STEAM_ROLE_CLIENT;
    InterlockedExchange(&g_invite_pw, pw);
    InterlockedExchange(&g_invite_landed_pending, 1);
    g_start_tick = GetTickCount();  /* re-anchor: watchdog measures from THIS PENDING, not process start */
    InterlockedExchange(&g_tun.client_state, STEAM_CLI_PENDING);  /* hold browser inject */
    g_tun.client_dead = 1;      /* ends a live client session; standby returns via role check */
}

int steam_tunnel_invite_pw(void) { return g_invite_pw != 0; }

/* Blocks until Steam is usable for this process. Fresh start: the engine's
   boot-time SteamAPI_Init verdict (ADDR_STEAM_API_INIT) is authoritative;
   this thread starts BEFORE the engine's pre-WinMain init (and before the
   engine has even loaded steam_api_wse2.dll), so both the flag check and
   the export resolution must retry inside the loop. If the flag never
   flips (game launched before Steam -- the engine's init is one-shot), we
   escalate after a grace period and establish the pipe ourselves via
   SteamAPI_Init (harmless to the engine: its own Steam features are dead
   post-boot either way). Recovery (Steam died mid-session): the engine
   flag is stale-1, so only a fresh SteamAPI_Init success counts. */
#define STEAM_SELF_INIT_GRACE_MS 30000

/* Role OFF has nothing to tunnel yet (no invite has promoted it), so it must
   not hold this thread hostage waiting on a Steam client that may never
   launch. timeout_ms == 0 waits forever (configured roles); a nonzero
   timeout gives up and returns 0 so the caller can exit quietly. */
static int steam_wait_steam_ready(int recovering, DWORD timeout_ms) {
    unsigned char (__cdecl *init_fn)(void) = NULL;
    DWORD start = GetTickCount(), last_log = 0;
    for (;;) {
        DWORD now = GetTickCount();
        if (!recovering && *(volatile BYTE *)ADDR_STEAM_API_INIT == 1)
            return 1;
        if (!init_fn) {
            HMODULE m = GetModuleHandleA("steam_api_wse2.dll");
            if (m) init_fn = (unsigned char (__cdecl *)(void))
                                 GetProcAddress(m, "SteamAPI_Init");
        }
        if (init_fn && (recovering || now - start > STEAM_SELF_INIT_GRACE_MS) &&
            init_fn()) {
            coop_log("[steam] SteamAPI_Init succeeded on the tunnel thread%s\n",
                     recovering ? " (recovery)" : " (engine boot-init never flagged)");
            return 1;
        }
        if (timeout_ms != 0 && now - start > timeout_ms) {
            coop_log("[steam] Steam not ready after %us -- invite standby off (LAN unaffected)\n",
                     timeout_ms / 1000);
            return 0;
        }
        if (now - last_log > 60000) {
            last_log = now;
            coop_log("[steam] waiting for Steam (%s)...\n",
                     recovering ? "recovery" : "engine init pending or Steam not running");
        }
        Sleep(recovering ? 5000 : 250);
    }
}

#define STEAM_OFF_READY_TIMEOUT_MS 120000

/* SEH filter: records what actually faulted (code, address, owning
   module) before the handler swallows it -- a bare EXECUTE_HANDLER left
   the tunnel's crash sites undiagnosable from the log. */
/* Which tunnel call was in flight when a fault hit (crash addresses often
   land inside steamclient.dll -- the phase names our call site). */
static volatile const char *g_tun_phase = "idle";
#define TUN_PHASE(p) (g_tun_phase = (p))

static int steam_seh_report(const char *where, EXCEPTION_POINTERS *ep) {
    void *addr = ep->ExceptionRecord->ExceptionAddress;
    HMODULE m = NULL;
    char mod[MAX_PATH] = "?";
    if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                           GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                           (LPCSTR)addr, &m) && m) {
        char *slash;
        GetModuleFileNameA(m, mod, sizeof(mod));
        slash = strrchr(mod, '\\');
        if (slash) memmove(mod, slash + 1, strlen(slash + 1) + 1);
    }
    coop_log("[steam] SEH in %s: code=0x%08X addr=%p (%s+0x%X) phase=%s\n", where,
             ep->ExceptionRecord->ExceptionCode, addr, mod,
             m ? (unsigned)((char *)addr - (char *)m) : 0, g_tun_phase);
    return EXCEPTION_EXECUTE_HANDLER;
}

/* Releases the winsock side and publishes the DOWN verdict, so coop.c
   restores the configured LAN address. Idempotent; runs on the tunnel
   thread only. */
static void steam_client_deactivate(void) {
    int v;
    for (v = 0; v < STEAM_NUM_VPORTS; v++)
        if (g_tun.cv[v].sock) { closesocket(g_tun.cv[v].sock); g_tun.cv[v].sock = 0; }
    InterlockedExchange(&g_tun.client_up, 0);
    InterlockedExchange(&g_tun.client_state, STEAM_CLI_DOWN);
}

/* Releases every Steam-side handle and resets per-session state so a
   recovery attempt starts from scratch. Steam may be mid-shutdown (that is
   how we usually get here), so the Steam calls are SEH-contained; the
   winsock closes and the state reset always run. */
static void steam_steamside_cleanup(void) {
    int i;
    for (i = 0; i < STEAM_MAX_RELAYS; i++)
        if (g_tun.relays[i].conn && g_tun.relays[i].sock)
            closesocket((SOCKET)g_tun.relays[i].sock);
    __try {
        if (SF.ClearRichPresence && SF.friends) {
            SF.ClearRichPresence(SF.friends);
        }
        if (g_rp_registered && SF.UnregisterCallback) {
            SF.UnregisterCallback(&g_rp_cb);
        }
        if (SF.sockets) {
            for (i = 0; i < STEAM_NUM_VPORTS; i++) {
                if (g_tun.cv[i].conn)
                    SF.CloseConnection(SF.sockets, g_tun.cv[i].conn, 0, NULL, 0);
                if (g_tun.listen[i])
                    SF.CloseListenSocket(SF.sockets, g_tun.listen[i]);
            }
            for (i = 0; i < STEAM_MAX_RELAYS; i++)
                if (g_tun.relays[i].conn)
                    SF.CloseConnection(SF.sockets, g_tun.relays[i].conn, 0, NULL, 0);
            if (g_tun.pollgrp)
                SF.DestroyPollGroup(SF.sockets, g_tun.pollgrp);
        }
    } __except (steam_seh_report("steamside_cleanup", GetExceptionInformation())) {
        coop_log("[steam] Steam-side cleanup faulted (Steam already gone?) -- state reset anyway\n");
    }
    g_rp_registered = 0;   /* re-registered on rebuild; Steam may be gone here, hence SEH above */
    steam_relay_init(g_tun.relays, STEAM_MAX_RELAYS);
    for (i = 0; i < STEAM_NUM_VPORTS; i++) {
        g_tun.listen[i] = 0;
        memset(&g_tun.cv[i], 0, sizeof(g_tun.cv[i]));
    }
    g_tun.pollgrp = 0;
    g_tun.client_dead = 0;
    g_pump_started = 0;
    g_last_pump_tick = 0;
    {   /* stale events reference dead connections -- drop them */
        steam_evt_t ev;
        while (steam_evq_pop(&ev)) {}
    }
}

/* Role OFF: keep callbacks flowing so a Join Game invite can arrive.
   Touches no sockets and publishes no client verdict -- pure-LAN players
   must see zero behavior change. Returns when an invite promotes the
   role (Task 5) so the thread epilogue rebuilds as CLIENT. */
static void steam_standby_run(void) {
    for (;;) {
        TUN_PHASE("standby:pump");  steam_pump_callbacks();
        TUN_PHASE("standby:runcb"); SF.RunCallbacks(SF.sockets);
        TUN_PHASE("standby:drain"); steam_drain_events();
        if (g_tun.cfg.role != STEAM_ROLE_OFF) return;   /* invite promoted us */
        Sleep(50);
    }
}

/* One tunnel session: global config + role loop. Returns when the role
   loop ends (setup failure, client retry exhaustion); faults propagate to
   the caller's SEH. */
static void steam_role_session(void) {
    TUN_PHASE("session:setup");
    /* Explicit ICE policy + relay warm-up. The status callback is
       registered per listen socket / connection only (steam_cb_option) --
       one delivery path, and global scope stays untouched. */
    SF.SetGlobalConfigValueInt32(SF.utils, SF_CFG_P2P_TRANSPORT_ICE_ENABLE,
                                 SF_ICE_ENABLE_ALL);
    /* First-ever route negotiation can outlive the 10 s default while
       relay pings are cold; give it room. */
    SF.SetGlobalConfigValueInt32(SF.utils, SF_CFG_TIMEOUT_INITIAL, 30000);
    if (SF.SetDebugOutputFunction) {
        if (g_tun.cfg.debug) {
            SF.SetDebugOutputFunction(SF.utils, SF_DEBUG_VERBOSE, steam_on_debug_output);
            SF.SetGlobalConfigValueInt32(SF.utils, SF_CFG_LOGLEVEL_P2P_RENDEZVOUS,
                                         SF_DEBUG_VERBOSE);
            SF.SetGlobalConfigValueInt32(SF.utils, SF_CFG_LOGLEVEL_SDR_RELAY_PINGS,
                                         SF_DEBUG_VERBOSE);
        } else {
            SF.SetDebugOutputFunction(SF.utils, SF_DEBUG_WARNING, steam_on_debug_output);
        }
    }
    SF.InitRelayNetworkAccess(SF.utils);

    if (!g_rp_registered && SF.RegisterCallback) {
        SF.RegisterCallback(&g_rp_cb, SF_CB_GAME_RICH_PRESENCE_JOIN_REQUESTED);
        g_rp_registered = 1;
        coop_log("[steam] Join Game callback registered\n");
    }

    g_role_start_tick = GetTickCount();

    if (g_tun.cfg.role == STEAM_ROLE_HOST) {
        coop_log("[steam] role=HOST (allowlist: %d entries)\n",
                 g_tun.cfg.allowed_count);
        if (g_tun.cfg.allowed_count == 0)
            coop_log("[steam] *** WARNING: AllowedSteamIDs is empty -- any Steam "
                     "user who learns this SteamID can attempt to join; the "
                     "server password is the only gate. Set one. ***\n");
        steam_host_run();
    } else if (g_tun.cfg.role == STEAM_ROLE_CLIENT) {
        coop_log("[steam] role=CLIENT host=%I64u\n", g_tun.cfg.host_steamid);
        steam_client_run();
    } else {
        coop_log("[steam] role=OFF -- invite standby (no sockets, no re-aim)\n");
        steam_standby_run();
    }
}

/* The thread never gives up while Steam might come back: every session end
   (SEH fault from a dying Steam client, setup failure, retry exhaustion)
   publishes DOWN -- LAN fallback stays usable -- then waits for Steam to be
   healthy again and rebuilds the whole role from scratch. Backoff caps at
   60 s so a Steam that never returns costs one log line a minute. */
static DWORD WINAPI steam_tunnel_thread(LPVOID param) {
    WSADATA wsa;
    int attempt = 0;
    DWORD backoff = 5000;
    (void)param;
    g_tunnel_tid = GetCurrentThreadId();
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        coop_log("[steam] WSAStartup failed -- LAN fallback\n");
        InterlockedExchange(&g_tun.client_state, STEAM_CLI_DOWN);
        return 0;
    }
    for (;;) {
        int fatal = 0;
        __try {
            if (!steam_wait_steam_ready(attempt > 0,
                    g_tun.cfg.role == STEAM_ROLE_OFF ? STEAM_OFF_READY_TIMEOUT_MS : 0)) {
                fatal = 1;   /* OFF standby only: Steam absent, exit quietly */
            } else if (!steam_flat_resolve()) {
                coop_log("[steam] flat-API resolve failed -- LAN fallback\n");
                fatal = 1;
            } else {
                steam_role_session();
            }
        } __except (steam_seh_report("tunnel session", GetExceptionInformation())) {
            coop_log("[steam] tunnel session crashed -- LAN fallback active, will retry\n");
        }
        steam_client_deactivate();
        steam_steamside_cleanup();
        if (fatal) {
            coop_log("[steam] Steam path unavailable for this process -- LAN fallback is final\n");
            return 0;
        }
        attempt++;
        coop_log("[steam] tunnel retry %d in %u ms\n", attempt, backoff);
        Sleep(backoff);
        if (backoff < 60000) backoff *= 2;
    }
}

void steam_tunnel_start(const steam_cfg_t *cfg) {
    HANDLE h;
    if (cfg->err[0]) {
        coop_log("[steam] config error: %s -- LAN fallback\n", cfg->err);
        return;                       /* misconfig stays OFF-and-dead, as today */
    }
    g_tun.cfg = *cfg;
    g_start_tick = GetTickCount();
    InitializeCriticalSection(&g_evq_cs);
    InitializeCriticalSection(&g_invite_cs);
    if (cfg->role == STEAM_ROLE_CLIENT)
        g_tun.client_state = STEAM_CLI_PENDING;
    h = CreateThread(NULL, 0, steam_tunnel_thread, NULL, 0, NULL); /* always: even role OFF needs the thread to pump invite callbacks */
    if (h == NULL) {
        coop_log("[steam] CreateThread failed -- LAN fallback\n");
        g_tun.client_state = STEAM_CLI_DOWN;
        return;
    }
    CloseHandle(h);
    coop_log("[steam] tunnel thread started (role=%s)\n",
             cfg->role == STEAM_ROLE_HOST ? "host" :
             cfg->role == STEAM_ROLE_CLIENT ? "client" : "off/standby");
}

static int steam_id_allowed(unsigned __int64 id) {
    int i;
    if (g_tun.cfg.allowed_count == 0) return 1;
    for (i = 0; i < g_tun.cfg.allowed_count; i++)
        if (g_tun.cfg.allowed[i] == id) return 1;
    return 0;
}

/* host: which vport does a listen socket serve? */
static int steam_vport_of_listen(HSteamListenSocket ls) {
    int v;
    for (v = 0; v < STEAM_NUM_VPORTS; v++)
        if (g_tun.listen[v] == ls) return v;
    return -1;
}

/* Telemetry helpers */
static unsigned int g_oversize_sends;   /* datagrams > 1300 B tunneled */
static DWORD g_last_stat_tick;

static void steam_log_mtu(HSteamNetConnection conn) {
    int mtu = 0, dt = SF_CFGTYPE_INT32;
    unsigned int cb = sizeof(mtu);
    if (!SF.GetConfigValue) return;
    /* OK=1 / OKInherited=2; errors are negative and 0 is not a defined result */
    if (SF.GetConfigValue(SF.utils, SF_CFG_MTU_DATASIZE, SF_SCOPE_CONNECTION,
                          (int)conn, &dt, &mtu, &cb) > 0)
        coop_log("[steam] mtu conn=%u MTU_DataSize=%d (mbnet max 1350 -- oversize fragments)\n",
                 conn, mtu);
}

/* GetConnectionRealTimeStatus exposes no loss counter; connection quality is
   Valve's own loss-derived proxy, and pending-unreliable bytes stand in for
   local drops (a backlog means Steam is shedding datagrams we handed it). */
static void steam_log_status_row(HSteamNetConnection conn, int vport,
                                 unsigned __int64 peer, const char *tag) {
    SteamNetConnectionRealTimeStatus_t st;
    memset(&st, 0, sizeof(st));
    if (SF.GetConnectionRealTimeStatus(SF.sockets, conn, &st, 0, NULL) != SF_RESULT_OK)
        return;
    coop_log("[steam] stat %s vport=%d id=%I64u conn=%u ping=%dms qual=%.2f/%.2f "
             "out=%.0fB/s in=%.0fB/s pend=%dB frag>1300=%u\n",
             tag, vport, peer, conn, st.m_nPing,
             st.m_flConnectionQualityLocal, st.m_flConnectionQualityRemote,
             st.m_flOutBytesPerSec, st.m_flInBytesPerSec,
             st.m_cbPendingUnreliable, g_oversize_sends);
}

/* SteamAPI callback pump. The SDR relay-config fetch (and other Steam
   call-results the tunnel depends on) complete only when someone in the
   process calls SteamAPI_RunCallbacks -- and the engine does not pump it
   after boot. The tunnel thread owns the pump: 20 Hz, starting after a
   grace period so any engine call-results still pending from Workshop
   startup are not dispatched onto this thread while the engine is mid-init.
   Both role loops call this every iteration.
   Considered and rejected: ManualDispatch on our own pipe. It is an
   exclusive process-wide mode switch that must precede all callback use
   and the engine already initialized normally -- flipping it mid-process
   is undefined for the engine's registered callbacks. */
#define STEAM_PUMP_GRACE_MS    10000
#define STEAM_PUMP_INTERVAL_MS 50

static void steam_pump_callbacks(void) {
    DWORD now = GetTickCount();
    if (now - g_role_start_tick < STEAM_PUMP_GRACE_MS) return;
    if (now - g_last_pump_tick < STEAM_PUMP_INTERVAL_MS) return;
    g_last_pump_tick = now;
    if (!g_pump_started) {
        g_pump_started = 1;
        coop_log("[steam] SteamAPI callback pump started (engine does not pump; relay init depends on it)\n");
    }
    SF.RunSteamCallbacks();
}

/* Relay-network availability (100=Current is healthy; see steam_flat.h).
   A stuck non-100 value here means Steam's SDR backend is unreachable and
   no P2P rendezvous can complete regardless of what we do. */
static void steam_log_relay_status(const char *tag) {
    SteamRelayNetworkStatus_t st;
    if (!SF.GetRelayNetworkStatus) return;
    memset(&st, 0, sizeof(st));
    SF.GetRelayNetworkStatus(SF.utils, &st);
    coop_log("[steam] relay status (%s): avail=%d netcfg=%d anyrelay=%d msg='%s'\n",
             tag, st.m_eAvail, st.m_eAvailNetworkConfig, st.m_eAvailAnyRelay,
             st.m_debugMsg);
}

static void steam_periodic_stats(void) {
    DWORD now = GetTickCount();
    int i;
    if (now - g_last_stat_tick < 10000) return;
    g_last_stat_tick = now;
    steam_log_relay_status("10s");
    if (g_tun.cfg.role == STEAM_ROLE_HOST) {
        for (i = 0; i < STEAM_MAX_RELAYS; i++)
            if (g_tun.relays[i].conn != 0)
                steam_log_status_row(g_tun.relays[i].conn, g_tun.relays[i].vport,
                                     g_tun.relays[i].steamid, "host");
    } else {
        for (i = 0; i < STEAM_NUM_VPORTS; i++)
            if (g_tun.cv[i].conn != 0)
                steam_log_status_row(g_tun.cv[i].conn, i,
                                     g_tun.cfg.host_steamid, "cli");
    }
}

static void steam_host_on_event(const steam_evt_t *ev) {
    unsigned __int64 peer = ev->steamid;

    if (ev->state == SF_STATE_CONNECTING) {
        int vport = steam_vport_of_listen(ev->listen);
        SOCKET s;
        struct sockaddr_in bindaddr, backend;
        steam_relay_t *r;

        /* Per-scope callbacks make this unreachable; if it ever fires the
           connection is not ours to touch, so only log it. */
        if (vport < 0) {
            coop_log("[steam] ignoring CONNECTING on unknown listen socket %u (conn=%u)\n",
                     ev->listen, ev->conn);
            return;
        }
        if (!steam_id_allowed(peer)) {
            coop_log("[steam] REJECT %I64u on vport %d (not in AllowedSteamIDs)\n", peer, vport);
            SF.CloseConnection(SF.sockets, ev->conn, 0, "not allowed", 0);
            return;
        }

        /* loopback socket for this (client x vport): its ephemeral source
           port is the mbnet peer separation (audit Q4) */
        s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (s == INVALID_SOCKET) {
            coop_log("[steam] socket() failed for %I64u vport %d (err=%d)\n",
                     peer, vport, WSAGetLastError());
            SF.CloseConnection(SF.sockets, ev->conn, 0, "host socket fail", 0);
            return;
        }
        memset(&bindaddr, 0, sizeof(bindaddr));
        bindaddr.sin_family = AF_INET;
        bindaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        bindaddr.sin_port = 0;  /* ephemeral */
        memset(&backend, 0, sizeof(backend));
        backend.sin_family = AF_INET;
        backend.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        backend.sin_port = htons((unsigned short)steam_vport_to_port(vport));
        if (bind(s, (struct sockaddr *)&bindaddr, sizeof(bindaddr)) != 0 ||
            connect(s, (struct sockaddr *)&backend, sizeof(backend)) != 0) {
            coop_log("[steam] bind/connect failed for %I64u vport %d (err=%d)\n",
                     peer, vport, WSAGetLastError());
            closesocket(s);
            SF.CloseConnection(SF.sockets, ev->conn, 0, "host socket fail", 0);
            return;
        }
        { u_long nb = 1; ioctlsocket(s, FIONBIO, &nb); }  /* recv drain loop needs non-blocking */

        r = steam_relay_add(g_tun.relays, STEAM_MAX_RELAYS, ev->conn, vport,
                            (unsigned int)s);
        if (!r) {
            coop_log("[steam] relay table full -- rejecting %I64u vport %d\n", peer, vport);
            closesocket(s);
            SF.CloseConnection(SF.sockets, ev->conn, 0, "relay table full", 0);
            return;
        }
        r->steamid = peer;
        if (SF.AcceptConnection(SF.sockets, ev->conn) != SF_RESULT_OK) {
            coop_log("[steam] AcceptConnection failed for %I64u vport %d\n", peer, vport);
            closesocket(s);
            steam_relay_remove(g_tun.relays, STEAM_MAX_RELAYS, ev->conn);
            SF.CloseConnection(SF.sockets, ev->conn, 0, "accept failed", 0);
            return;
        }
        SF.SetConnectionPollGroup(SF.sockets, ev->conn, g_tun.pollgrp);
        coop_log("[steam] ACCEPT %I64u on vport %d (conn=%u)\n", peer, vport, ev->conn);
        return;
    }

    if (ev->state == SF_STATE_CONNECTED) {
        coop_log("[steam] connected: %I64u (conn=%u)\n", peer, ev->conn);
        steam_log_mtu(ev->conn);
        return;
    }

    if (ev->state == SF_STATE_CLOSED_BY_PEER ||
        ev->state == SF_STATE_PROBLEM_DETECTED) {
        steam_relay_t *r = steam_relay_by_conn(g_tun.relays, STEAM_MAX_RELAYS, ev->conn);
        coop_log("[steam] closed: %I64u (conn=%u state=%d reason=%d)\n",
                 peer, ev->conn, ev->state, ev->end_reason);
        if (r) {
            closesocket((SOCKET)r->sock);
            steam_relay_remove(g_tun.relays, STEAM_MAX_RELAYS, ev->conn);
        }
        SF.CloseConnection(SF.sockets, ev->conn, 0, NULL, 0);
        /* mbnet times the vanished peer out natively -- nothing else to do */
        return;
    }
}

#define STEAM_CLIENT_MAX_RETRIES 3

static int steam_client_vport_of_conn(HSteamNetConnection conn) {
    int v;
    for (v = 0; v < STEAM_NUM_VPORTS; v++)
        if (g_tun.cv[v].conn == conn) return v;
    return -1;
}

#define STEAM_CLIENT_RETRY_INTERVAL_MS 2000

/* Charges a failure to a vport. Vport 0 is the campaign link: without it the
   proxy has nothing to tunnel, so exhausting its budget takes the whole
   tunnel down and hands the engine back its LAN address. */
static void steam_client_charge_failure(int v) {
    g_tun.cv[v].retries++;
    if (g_tun.cv[v].retries < STEAM_CLIENT_MAX_RETRIES) return;
    coop_log("[steam] vport %d: %d failures -- giving up (engine will show connection lost)\n",
             v, g_tun.cv[v].retries);
    if (v == 0) {
        coop_log("[steam] campaign vport dead -- deactivating tunnel, LAN address restored\n");
        g_tun.client_dead = 1;
    }
}

static void steam_client_on_event(const steam_evt_t *ev) {
    int v = steam_client_vport_of_conn(ev->conn);
    if (v < 0) {
        coop_log("[steam] ignoring state=%d for untracked conn=%u\n", ev->state, ev->conn);
        return;
    }

    if (ev->state == SF_STATE_CONNECTED) {
        coop_log("[steam] vport %d connected to %I64u\n", v, g_tun.cfg.host_steamid);
        g_tun.cv[v].retries = 0;
        steam_log_mtu(ev->conn);
        return;
    }
    if (ev->state == SF_STATE_CLOSED_BY_PEER ||
        ev->state == SF_STATE_PROBLEM_DETECTED) {
        coop_log("[steam] vport %d connection to %I64u lost (state=%d reason=%d)\n",
                 v, g_tun.cfg.host_steamid, ev->state, ev->end_reason);
        SF.CloseConnection(SF.sockets, ev->conn, 0, NULL, 0);
        g_tun.cv[v].conn = 0;   /* next engine datagram triggers a retry */
        steam_client_charge_failure(v);
    }
}

/* Installs our status-changed handler on this scope only (see the queue
   comment): global scope would clobber whatever the engine installed. */
static void steam_cb_option(SteamNetworkingConfigValue_t *o) {
    o->m_eValue    = SF_CFG_CB_CONNECTION_STATUS;
    o->m_eDataType = SF_CFGTYPE_PTR;
    o->m_val.m_ptr = (void *)steam_on_status_changed;
}

static void steam_client_connect_vport(int v) {
    SteamNetworkingIdentity host;
    SteamNetworkingConfigValue_t opt;
    DWORD now = GetTickCount();

    if (g_tun.cv[v].retries >= STEAM_CLIENT_MAX_RETRIES) return;
    /* Bound the retry budget in time as well as in count, so three instant
       failures cannot kill the vport for the session. */
    if (g_tun.cv[v].last_attempt_tick &&
        now - g_tun.cv[v].last_attempt_tick < STEAM_CLIENT_RETRY_INTERVAL_MS)
        return;
    g_tun.cv[v].last_attempt_tick = now;

    memset(&host, 0, sizeof(host));
    host.m_eType  = SF_IDENTITY_TYPE_STEAMID;
    host.m_cbSize = 8;   /* sizeof(steamID64) -- identity equality checks
                            type+size+payload; size 0 makes Steam reject
                            every rendezvous reply as "wrong remote identity" */
    host.u.m_steamID64 = g_tun.cfg.host_steamid;
    steam_cb_option(&opt);
    g_tun.cv[v].conn = SF.ConnectP2P(SF.sockets, &host, v, 1, &opt);
    if (g_tun.cv[v].conn == 0) {
        coop_log("[steam] ConnectP2P(vport %d, %I64u) failed outright\n",
                 v, g_tun.cfg.host_steamid);
        steam_client_charge_failure(v);
        return;
    }
    SF.SetConnectionPollGroup(SF.sockets, g_tun.cv[v].conn, g_tun.pollgrp);
    coop_log("[steam] vport %d connecting to %I64u (conn=%u)\n",
             v, g_tun.cfg.host_steamid, g_tun.cv[v].conn);
}

/* Drains everything the callback queued, on the tunnel thread. */
static void steam_drain_events(void) {
    steam_evt_t ev;
    steam_drain_invite();
    while (steam_evq_pop(&ev)) {
        if (g_tun.cfg.role == STEAM_ROLE_HOST) steam_host_on_event(&ev);
        else if (g_tun.cfg.role == STEAM_ROLE_CLIENT) steam_client_on_event(&ev);
        /* OFF: connection events impossible -- no listens, no connects */
    }
}

#define STEAM_DGRAM_MAX 2048   /* mbnet caps datagrams at 1350; headroom only */
#define STEAM_RECV_BATCH 64

static void steam_host_run(void) {
    int v;
    char buf[STEAM_DGRAM_MAX];
    SteamNetworkingConfigValue_t opt;

    steam_cb_option(&opt);
    for (v = 0; v < STEAM_NUM_VPORTS; v++) {
        g_tun.listen[v] = SF.CreateListenSocketP2P(SF.sockets, v, 1, &opt);
        if (g_tun.listen[v] == 0) {
            coop_log("[steam] CreateListenSocketP2P(vport %d) failed -- LAN fallback\n", v);
            while (--v >= 0) SF.CloseListenSocket(SF.sockets, g_tun.listen[v]);
            return;
        }
    }
    g_tun.pollgrp = SF.CreatePollGroup(SF.sockets);
    if (g_tun.pollgrp == 0) {
        coop_log("[steam] CreatePollGroup failed -- LAN fallback\n");
        for (v = 0; v < STEAM_NUM_VPORTS; v++)
            SF.CloseListenSocket(SF.sockets, g_tun.listen[v]);
        return;
    }
    steam_relay_init(g_tun.relays, STEAM_MAX_RELAYS);
    coop_log("[steam] host bridge up: vports 0-%d listening\n", STEAM_NUM_VPORTS - 1);
    steam_log_relay_status("bridge-up");

    if (SF.SetRichPresence) {
        char cs[STEAM_INVITE_MAX];
        unsigned __int64 self_id = SF.GetSteamID ? SF.GetSteamID(SF.user) : 0;
        if (self_id && steam_invite_build(cs, sizeof(cs), self_id,
                                          g_tun.cfg.has_password ? STEAM_RP_PW_FLAG : 0) > 0) {
            SF.SetRichPresence(SF.friends, "connect", cs);
            coop_log("[steam] rich presence set: %s\n", cs);
        }
    }

    for (;;) {
        SteamNetworkingMessage_t *msgs[STEAM_RECV_BATCH];
        int n, i;
        fd_set rd;
        struct timeval tv;

        TUN_PHASE("host:pump");     steam_pump_callbacks();
        TUN_PHASE("host:runcb");    SF.RunCallbacks(SF.sockets);
        TUN_PHASE("host:drain");    steam_drain_events();
        TUN_PHASE("host:stats");    steam_periodic_stats();

        /* Steam -> backend */
        TUN_PHASE("host:recv");
        n = SF.ReceiveMessagesOnPollGroup(SF.sockets, g_tun.pollgrp, msgs, STEAM_RECV_BATCH);
        for (i = 0; i < n; i++) {
            steam_relay_t *r = steam_relay_by_conn(g_tun.relays, STEAM_MAX_RELAYS,
                                                   msgs[i]->m_conn);
            if (r && msgs[i]->m_cbSize > 0 && msgs[i]->m_cbSize <= STEAM_DGRAM_MAX)
                send((SOCKET)r->sock, (const char *)msgs[i]->m_pData,
                     msgs[i]->m_cbSize, 0);
            msgs[i]->m_pfnRelease(msgs[i]);
        }

        /* backend -> Steam */
        FD_ZERO(&rd);
        {
            int j, any = 0;
            for (j = 0; j < STEAM_MAX_RELAYS; j++)
                if (g_tun.relays[j].conn != 0) {
                    FD_SET((SOCKET)g_tun.relays[j].sock, &rd);
                    any = 1;
                }
            if (!any) { Sleep(1); continue; }
            tv.tv_sec = 0; tv.tv_usec = 1000;   /* 1 ms -- the latency floor */
        }
        TUN_PHASE("host:send");
        if (select(0, &rd, NULL, NULL, &tv) > 0) {
            int j;
            for (j = 0; j < STEAM_MAX_RELAYS; j++) {
                steam_relay_t *r = &g_tun.relays[j];
                if (r->conn == 0 || !FD_ISSET((SOCKET)r->sock, &rd)) continue;
                for (;;) {
                    int len = recv((SOCKET)r->sock, buf, sizeof(buf), 0);
                    if (len <= 0) break;
                    {
                        if (len > 1300) g_oversize_sends++;
                        EResult er = SF.SendMessageToConnection(SF.sockets, r->conn, buf,
                                     (unsigned int)len, SF_SEND_UNRELIABLE_NO_NAGLE, NULL);
                        if (er != SF_RESULT_OK && er != SF_RESULT_LIMITEXCEEDED)
                            coop_log("[steam] send failed vport=%d id=%I64u conn=%u er=%d\n",
                                     r->vport, r->steamid, r->conn, er);
                    }
                }
            }
        }
    }
}

static void steam_client_run(void) {
    int v;
    char buf[STEAM_DGRAM_MAX];

    /* Bind the REAL server ports on loopback (joiners run no dedicated
       processes; a bind failure means this box hosts something -> LAN). */
    for (v = 0; v < STEAM_NUM_VPORTS; v++) {
        struct sockaddr_in a;
        u_long nb = 1;
        SOCKET s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (s == INVALID_SOCKET) {
            coop_log("[steam] socket() failed (err=%d) -- LAN fallback\n", WSAGetLastError());
            return;
        }
        memset(&a, 0, sizeof(a));
        a.sin_family = AF_INET;
        a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);   /* strictly 127.0.0.1 */
        a.sin_port = htons((unsigned short)steam_vport_to_port(v));
        if (bind(s, (struct sockaddr *)&a, sizeof(a)) != 0) {
            coop_log("[steam] cannot bind 127.0.0.1:%d (err=%d; is this machine hosting?) -- LAN fallback\n",
                     steam_vport_to_port(v), WSAGetLastError());
            closesocket(s);
            return;
        }
        ioctlsocket(s, FIONBIO, &nb);
        g_tun.cv[v].sock = s;
    }
    g_tun.pollgrp = SF.CreatePollGroup(SF.sockets);
    if (g_tun.pollgrp == 0) { coop_log("[steam] CreatePollGroup failed -- LAN fallback\n"); return; }

    InterlockedExchange(&g_tun.client_up, 1);
    InterlockedExchange(&g_tun.client_state, STEAM_CLI_UP);
    if (InterlockedExchange(&g_invite_landed_pending, 0)) {
        steam_notify("Join Game: tunnel ready -- COOP Direct is in the MP browser (LAN tab)");
        /* RE Q5: auto-join deferred to a future design; armed-browser-row
           is the committed landing (Task 7 Step 1). See findings Q5. */
    }
    coop_log("[steam] client proxy up: 127.0.0.1 ports 7240/7241/7243/7245/7247 -> %I64u\n",
             g_tun.cfg.host_steamid);
    steam_log_relay_status("proxy-up");

    for (;;) {
        SteamNetworkingMessage_t *msgs[STEAM_RECV_BATCH];
        int n, i;
        fd_set rd;
        struct timeval tv;

        /* Returning hands teardown to the thread epilogue, which closes the
           loopback sockets and republishes the DOWN verdict. */
        if (g_tun.client_dead) return;

        TUN_PHASE("cli:pump");      steam_pump_callbacks();
        TUN_PHASE("cli:runcb");     SF.RunCallbacks(SF.sockets);
        TUN_PHASE("cli:drain");     steam_drain_events();
        TUN_PHASE("cli:stats");     steam_periodic_stats();

        /* Steam -> engine */
        TUN_PHASE("cli:recv");
        n = SF.ReceiveMessagesOnPollGroup(SF.sockets, g_tun.pollgrp, msgs, STEAM_RECV_BATCH);
        for (i = 0; i < n; i++) {
            int mv = steam_client_vport_of_conn(msgs[i]->m_conn);
            if (mv >= 0 && g_tun.cv[mv].engine_valid &&
                msgs[i]->m_cbSize > 0 && msgs[i]->m_cbSize <= STEAM_DGRAM_MAX)
                sendto(g_tun.cv[mv].sock, (const char *)msgs[i]->m_pData,
                       msgs[i]->m_cbSize, 0,
                       (struct sockaddr *)&g_tun.cv[mv].engine_addr,
                       sizeof(g_tun.cv[mv].engine_addr));
            msgs[i]->m_pfnRelease(msgs[i]);
        }

        /* engine -> Steam */
        TUN_PHASE("cli:send");
        FD_ZERO(&rd);
        for (v = 0; v < STEAM_NUM_VPORTS; v++) FD_SET(g_tun.cv[v].sock, &rd);
        tv.tv_sec = 0; tv.tv_usec = 1000;   /* 1 ms */
        if (select(0, &rd, NULL, NULL, &tv) > 0) {
            for (v = 0; v < STEAM_NUM_VPORTS; v++) {
                if (!FD_ISSET(g_tun.cv[v].sock, &rd)) continue;
                for (;;) {
                    struct sockaddr_in from;
                    int fromlen = sizeof(from);
                    int len = recvfrom(g_tun.cv[v].sock, buf, sizeof(buf), 0,
                                       (struct sockaddr *)&from, &fromlen);
                    if (len <= 0) break;
                    g_tun.cv[v].engine_addr = from;
                    g_tun.cv[v].engine_valid = 1;
                    if (g_tun.cv[v].conn == 0) steam_client_connect_vport(v);
                    if (g_tun.cv[v].conn != 0) {
                        if (len > 1300) g_oversize_sends++;
                        EResult er = SF.SendMessageToConnection(SF.sockets,
                                     g_tun.cv[v].conn, buf, (unsigned int)len,
                                     SF_SEND_UNRELIABLE_NO_NAGLE, NULL);
                        if (er != SF_RESULT_OK && er != SF_RESULT_LIMITEXCEEDED)
                            coop_log("[steam] send failed vport=%d id=%I64u conn=%u er=%d\n",
                                     v, g_tun.cfg.host_steamid, g_tun.cv[v].conn, er);
                    }
                }
            }
        }
    }
}
