/*
 * warband_coop.asi - Direct Connect for WSE2 COOP campaign.
 *
 * Hooks the server browser's frameMove to inject a server entry from
 * coop.ini into the server list. Combined with m_switchingModule stored
 * fields, the browser auto-connects to the server through the full
 * protocol flow.
 *
 * Also writes server IP into string register s59 for battle connections.
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "hook.h"

/* ------------------------------------------------------------------ */
/*  Logging                                                           */
/* ------------------------------------------------------------------ */

static FILE *g_log = NULL;

void coop_log(const char *fmt, ...) {
    va_list ap;
    if (!g_log) return;
    va_start(ap, fmt);
    vfprintf(g_log, fmt, ap);
    va_end(ap);
    fflush(g_log);
}

/* ------------------------------------------------------------------ */
/*  Engine addresses (WSE2 exe, PDB-verified)                         */
/*  Single address table lives in warband_addrs_wse2.h. ASLR is       */
/*  disabled on this client via binary patch, so these are used as    */
/*  raw literals -- do NOT wrap in REBASE().                          */
/* ------------------------------------------------------------------ */

#include "warband_addrs_wse2.h"
#include "modglobals.h"
#include "steam_tunnel.h"
#include "asi_rglstring.h"
#include "asi_publish.h"
#include "local_result.h"
#include "local_mission.h"
#include "browser_row.h"
#include "autojoin.h"
#include "asi_patch.h"
#include "asi_config.h"
#include "asi_gvars.h"

#define MB_GAME_PLAYER_TROOP_NO    0x3A8    /* offset into mbGame */

/* ------------------------------------------------------------------ */
/*  Config                                                            */
/* ------------------------------------------------------------------ */

/* g_cfg.host_ip is the address the browser row and s59 publish; sole
   writer after DllMain: the s59 thread (see steam_reaim_host_ip). */
static asi_config g_cfg;
static char g_game_dir[MAX_PATH] = "";          /* game directory (dirname of exe), set at DLL load */

/* Resolved in DllMain before the s59 thread starts and the hooks go in. */
static asi_gvars g_gv;

static void read_config(HINSTANCE hinstDLL) {
    char dll_path[MAX_PATH], ini_path[MAX_PATH];
    char *slash;
    GetModuleFileNameA(hinstDLL, dll_path, MAX_PATH);
    slash = strrchr(dll_path, '\\');
    if (slash) slash[1] = '\0'; else dll_path[0] = '\0';
    lstrcpynA(ini_path, dll_path, MAX_PATH);
    lstrcatA(ini_path, "coop.ini");
    asi_config_read(&g_cfg, ini_path);
}

/* ------------------------------------------------------------------ */
/*  s59 writer thread (writes battle server IP to string register)    */
/* ------------------------------------------------------------------ */

/* The one place g_cfg.host_ip changes: swap to loopback while the Steam client
   proxy is live, back to the ini value when it dies. Readers on the main
   thread take a snapshot, and the browser injection additionally waits out
   STEAM_CLI_PENDING, so no reader can observe a half-written address or
   latch a stale one. */
static int g_host_ip_reaimed = 0;   /* s59 thread */
static int g_return_latched   = 0;   /* s59 thread */

static void flush_result_string_to_file(void) { local_result_flush(&g_gv.result, g_game_dir); }
static void check_pending_local_result(void) { local_result_load(&g_gv.pending, g_game_dir); }

static void steam_reaim_host_ip(void) {
    int up = steam_tunnel_client_is_up();
    if (!host_ip_reaim(&g_host_ip_reaimed, up, g_cfg.host_ip, sizeof(g_cfg.host_ip), g_cfg.host_ip_lan)) return;
    coop_log(up ? "[steam] client proxy up -- HostIP re-aimed to %s (s59 + browser inject)\n"
                : "[steam] client proxy down -- HostIP restored to %s (LAN fallback)\n",
             g_cfg.host_ip);
}

/* The MP browser opens on the tab persisted in the active profile
   (mbnetProfile+0x74; the Internet tab hides the injected coop row).
   Force it to LAN once, before the browser window is first constructed --
   initialize @0x516B40 then sets the combo AND auto-starts a LAN scan,
   so the row appears with zero clicks. Engine clamps the value on read. */
static void force_browser_lan_default(void) {
    static int forced = 0;
    char *profiles;
    int profile_no, *tab;
    if (forced) return;
    profiles   = *(char **)ADDR_MP_PROFILES_FIRST;
    profile_no = *(int *)ADDR_MP_PROFILE_NO;
    if (!profiles || profile_no < 0) return;
    tab = (int *)(profiles + profile_no * MP_PROFILE_STRIDE + MP_PROFILE_TAB_OFF);
    if (*tab != 1) {
        *tab = 1;
        coop_log("browser default tab forced to LAN (profile %d)\n", profile_no);
    }
    forced = 1;
}

/* Arm the auto-join driver at the campaign server's address (g_cfg.host_ip:
   g_cfg.port -- loopback while the joiner tunnel is UP). TUNNEL kind when the
   client proxy is up so a mid-wait tunnel death aborts the join; LOCAL
   otherwise. The FrameMove hook consumes the arm on the render thread. */
static void arm_campaign_return(const char *why) {
    steam_tunnel_autojoin_arm(steam_tunnel_client_is_up()
                              ? STEAM_AUTOJOIN_TUNNEL
                              : STEAM_AUTOJOIN_LOCAL);
    coop_log("[autojoin] %s -- returning to campaign server\n", why);
}

static DWORD WINAPI s59_writer_thread(LPVOID param) {
    int written = 0;
    int pw_prefilled = 0;
    (void)param;
    while (1) {
        Sleep(500);
        flush_result_string_to_file();
        force_browser_lan_default();
        { /* Wait for the engine to construct the string registers (static
             storage is zero until the rglString ctor runs). Test the buffer
             pointer for NULL only: s0 moves to a heap buffer the first time a
             script stores a 48+ char string in it and never returns to its
             SSO slot, so an SSO-equality test would park this loop -- and
             every publish below it -- for the rest of the process. */
            if (!rglstring_is_constructed((const char *)STRING_REG_BASE)) continue;
        }
        steam_reaim_host_ip();
        rglstring_set_sso((char *)(STRING_REG_BASE + 59 * STRING_REG_STRIDE), g_cfg.host_ip);
        rglstring_set_sso((char *)(STRING_REG_BASE + 57 * STRING_REG_STRIDE), g_cfg.password);  /* mirror for module_simple_triggers.py's deferred battle connect */
        if (!written) { coop_log("s59=%s\n", g_cfg.host_ip); written = 1; }

        /* Republish the Steam account id every tick: the engine wipes
           module globals on every server connect, and a module-side
           startup zero must never stick (project-state lesson).
           -1 = "Steam not up right now" -- lets the module send its
           username-keying identify immediately instead of burning the
           ~5 s no-report tick budget (which delays new-char creation
           and battle spawn by that long on no-Steam clients). A later
           tick overwrites the sentinel with the real acctid if Steam
           comes up; the module latches identify per connection. */
        if (g_gv.my_steam_acctid >= 0) {
            modglobals_set(g_gv.my_steam_acctid,
                           acctid_global_value(steam_tunnel_local_acctid()));
        }

        /* Publish whether a Steam-needing role has given up finding Steam, so
           the module can warn the host in-game. Republished every tick for the
           same reason as the acctid: the engine wipes module globals on connect. */
        if (g_gv.steam_missing >= 0)
            modglobals_set(g_gv.steam_missing, steam_tunnel_steam_missing());

        /* Post-battle return hop: the battle server's ch127 ev-55 handler
           sets $g_coop_return_to_campaign just before the end-of-battle
           kick. Edge-latched: the global stays 1 until the engine wipes it
           on the reconnect this very arm causes, so without the latch this
           loop would re-arm forever. */
        if (g_gv.return_to_campaign >= 0 &&
            return_latch_step(&g_return_latched, modglobals_get_int(g_gv.return_to_campaign, 0)))
            arm_campaign_return("battle over");

        /* One-shot m_storedPassword prefill: covers the engine's own
           m_switchingModule direct-connect arm only -- a manual browser
           Connect reads the password textbox instead (RE Q7), so this is
           belt-and-braces, not the primary password delivery path. In-place
           write per RE Q8: only safe when the rglString's existing buffer
           capacity (+0x08) exceeds the new length; never re-point +0x04 at
           the SSO slot. */
        if (!pw_prefilled && g_cfg.password[0]) {
            if (rglstring_assign_in_place((char *)ADDR_DIRECT_CONNECT_PASS, g_cfg.password)) {
                coop_log("[steam] stored password prefilled from coop.ini\n");
            } else {
                coop_log("[steam] stored password prefill skipped -- exceeds buffer capacity\n");
            }
            pw_prefilled = 1;
        }
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Server injection: add our server to the browser's list            */
/*  Called from the browser's frameMove hook (main thread)            */
/* ------------------------------------------------------------------ */

typedef void (__fastcall *fn_thiscall_void)(void *ecx, void *edx);
typedef void (__fastcall *fn_thiscall_ptr)(void *ecx, void *edx, void *arg);

static void inject_server(void *browser_window) {
    /* mbnetServer is 0x180 bytes */
    char server[BROWSER_ROW_SIZE];
    char host_ip[64];
    fn_thiscall_void server_ctor = (fn_thiscall_void)ADDR_SERVER_CTOR;
    fn_thiscall_void server_dtor = (fn_thiscall_void)ADDR_SERVER_DTOR;
    fn_thiscall_ptr  vec_push    = (fn_thiscall_ptr)ADDR_VEC_PUSH_BACK;
    fn_thiscall_void fill_list   = (fn_thiscall_void)ADDR_FILL_SERVER_LIST;

    /* One snapshot of the address the s59 thread owns */
    lstrcpynA(host_ip, g_cfg.host_ip, sizeof(host_ip));

    if (browser_row_exists(*(char **)ADDR_SERVER_LIST, *(char **)(ADDR_SERVER_LIST + 4),
                           host_ip, g_cfg.port)) {
        coop_log("server row %s:%d already listed -- push skipped\n", host_ip, g_cfg.port);
        return;
    }

    /* Construct default mbnetServer */
    server_ctor((void *)server, NULL);

    /* One writer for m_passworded: invite :pw flag (Steam path) or local
       Password= (host's own client / prefilled joiner). LAN joiners without
       either degrade to the engine's wrong-password reject. */
    browser_row_fill(server, host_ip, g_cfg.port, g_cfg.module_name,
                     steam_tunnel_invite_pw() || g_cfg.password[0]);

    /* Push to g_multiplayerData.m_serverList */
    vec_push((void *)ADDR_SERVER_LIST, NULL, (void *)server);

    /* Refresh table display */
    fill_list(browser_window, NULL);

    coop_log("server injected: %s:%d name='COOP Direct' module=%s\n",
             host_ip, g_cfg.port, g_cfg.module_name);

    /* Cleanup local (vector made a copy) */
    server_dtor((void *)server, NULL);
}

/* ------------------------------------------------------------------ */
/*  Server browser frameMove hook                                     */
/*  Injects our server on first frame, then passes through            */
/* ------------------------------------------------------------------ */

static BYTE  g_fm_saved[8];
static DWORD g_fm_trampoline = 0;

static browser_inject g_browser_inject = BROWSER_INJECT_INIT;   /* render thread */

static void __cdecl browser_framemove_pre(void *this_ptr) {
    int mode = *(int *)ADDR_MAP_INTERACTION_MODE;

    if (mode == 4) {
        flush_result_string_to_file();
        check_pending_local_result();
    }

    if (browser_inject_step(&g_browser_inject, mode, *(BYTE *)ADDR_SEARCHING_SERVERS,
                            steam_tunnel_client_state, *(void **)((char *)this_ptr + 0x88)))
        inject_server(this_ptr);
}

__declspec(naked) void browser_framemove_detour(void) {
    __asm {
        push ecx
        push ecx
        call browser_framemove_pre
        add  esp, 4
        pop  ecx
        jmp  [g_fm_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  Auto-join on invite landing -- CD3DApplication::FrameMove hook    */
/*  Sole engine-memory writer for the auto-join flags; the tunnel      */
/*  thread only sets the armed bit. RE ground truth: findings          */
/*  "Auto-join on invite landing RE (2026-08-23)".                     */
/* ------------------------------------------------------------------ */

static BYTE  g_aj_saved[16];
static DWORD g_aj_trampoline = 0;

static autojoin g_autojoin = AUTOJOIN_INIT;   /* render thread */

static void engine_rgl_copy(void *rgl_string, const char *value) {
    typedef void (__fastcall *fn_rgl_copy)(void *ecx, void *edx, const char *s);
    ((fn_rgl_copy)ADDR_RGL_STRING_COPY)(rgl_string, NULL, value);
}

static void engine_set_window(int window) {
    ((void (__stdcall *)(int))ADDR_SET_WINDOW)(window);
}

static void __cdecl autojoin_framemove_pre(void) {
    const int *begin = *(const int **)ADDR_OPEN_WINDOWS_BEGIN;
    const int *end   = *(const int **)ADDR_OPEN_WINDOWS_END;
    autojoin_env env;
    env.switching_module      = (volatile unsigned char *)ADDR_SWITCHING_MODULE;
    env.switching_to_campaign = (volatile unsigned char *)ADDR_SWITCHING_TO_CAMPAIGN;
    env.connect_to_server     = (volatile unsigned char *)ADDR_DIRECT_CONNECT_FLAG;
    env.open_windows   = begin;
    env.n_open_windows = (begin && end > begin) ? (int)(end - begin) : 0;
    env.loading_window = *(char **)ADDR_LOADING_WINDOW_PTR;
    env.tunnel_up      = steam_tunnel_client_is_up();
    env.now            = GetTickCount();
    env.host_ip        = g_cfg.host_ip;
    env.port           = g_cfg.port;
    env.password       = g_cfg.password;
    env.stored_address  = (void *)ADDR_DIRECT_CONNECT_ADDR;
    env.stored_password = (void *)ADDR_DIRECT_CONNECT_PASS;
    env.rgl_copy   = engine_rgl_copy;
    env.set_window = engine_set_window;
    autojoin_step(&g_autojoin, &env);
}

__declspec(naked) void autojoin_framemove_detour(void) {
    __asm {
        push ecx
        call autojoin_framemove_pre
        pop  ecx
        jmp  [g_aj_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  mbMission::createAgent detour — player attach on gameType=4       */
/* ------------------------------------------------------------------ */

static DWORD g_ca_trampoline = 0;
static BYTE  g_ca_saved[16]   = {0};

/* Called from the naked detour with a pointer to the stack-argument area
   (address of param 2 on the stack, i.e. ESP+4 at the callee entry).
   Mutates playerNo in place when all match conditions hold. */
static void __cdecl create_agent_pre(DWORD *args) {
    /* args[0] = transform, args[1] = entryPointNo, args[2] = troopNo, ...,
       args[13] = playerNo. Indices are (param# - 2) since `this` is in ECX. */
    int troopNo  = (int)args[2];
    int playerNo = (int)args[13];
    int newPlayerNo;

    /* g_mbGame is a pointer at 0xA4F6A4; m_playerTroopNo at +0x3A8. */
    void *mbGame = *(void **)ADDR_CUR_GAME;
    if (!mbGame) return;
    newPlayerNo = create_agent_player_no(*(int *)ADDR_MAP_INTERACTION_MODE, troopNo, playerNo,
                                         *(int *)((BYTE *)mbGame + MB_GAME_PLAYER_TROOP_NO),
                                         *(int *)ADDR_LOCAL_PLAYER_IDX);
    if (newPlayerNo == playerNo) return;

    args[13] = (DWORD)newPlayerNo;
    coop_log("createAgent detour: playerNo -1 -> %d for troopNo=%d\n",
             newPlayerNo, troopNo);
}

__declspec(naked) void create_agent_detour(void) {
    __asm {
        /* Preserve caller-visible state. ECX = `this` (thiscall). */
        push ecx
        push edx
        /* Pass pointer to arg area. At this point ESP points at saved edx;
           above that: saved ecx, return addr, then param2 (transform) at +12. */
        lea  eax, [esp + 12]
        push eax
        call create_agent_pre
        add  esp, 4
        pop  edx
        pop  ecx
        jmp  [g_ca_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  Option C — metaMission populate for coop local missions           */
/*  See patches/Warband/findings_encounters.md "Option C Impl RE"    */
/* ------------------------------------------------------------------ */

static DWORD g_sp_trampoline = 0;
static BYTE  g_sp_saved[16]  = {0};

/* Nonzero while a module-requested local mission runs: setparams_pre and
   mission_framemove_detour hold gameType at 0 inside the window dispatch,
   mission_end_restore_gametype clears it at the mission-end transition. */
static volatile int g_in_coop_local_mission = 0;
static int g_local_mission_kind = LOCAL_MISSION_NONE;

/* ------------------------------------------------------------------ */
/*  Drain the client's outbound event queue while gameType is still 4. */
/*                                                                     */
/*  multiplayer_send_int_to_server only enqueues into slot-0 m_events; */
/*  the per-frame pump (mbCoreGame::frameMove) only services the queue */
/*  while gameType is a client type (1/4). Forcing gameType=0 below    */
/*  silences that pump for the whole local mission, so any event the   */
/*  encounter menu queued (e.g. start_local_fight) would be stranded   */
/*  and never reach the campaign server. Transmit it now, before the   */
/*  flip, via the narrow client send (no inbound work, no gameType     */
/*  check). The per-player rate throttle is bypassed by zeroing        */
/*  m_packetSendTime so the queued event leaves on this call.          */
#define OFF_PLAYER_OBJECT      0x000      /* *(int*)(slot0+0): player object ptr */
#define OFF_PACKET_SEND_TIME   0x300      /* double m_packetSendTime */

static void coop_flush_client_events(void) {
    void *host  = *(void **)ADDR_MBNET_HOST_PTR;
    void *slot0 = *(void **)ADDR_NET_PLAYERS_VEC;
    fn_thiscall_void client_send;

    if (host == NULL) return;                                   /* not connected */
    if (slot0 == NULL) return;                                  /* player vector unallocated */
    if (*(int *)((BYTE *)slot0 + OFF_PLAYER_OBJECT) == 0) return;  /* slot 0 empty */
    if (*(BYTE *)ADDR_SEARCHING_SERVERS != 0) return;               /* send loop would skip slot 0 */

    *(double *)((BYTE *)slot0 + OFF_PACKET_SEND_TIME) = 0.0;     /* bypass rate throttle this call */

    client_send = (fn_thiscall_void)ADDR_NET_CLIENT_SEND;
    client_send((void *)ADDR_NET_CLIENT_THIS, NULL);
    coop_log("flushed client outbound queue before gameType flip\n");
}

static void __cdecl setparams_pre(void) {
    int kind;
    g_in_coop_local_mission = 0;
    kind = local_mission_fixup((volatile int *)ADDR_META_MISSION, *(int *)ADDR_MAP_INTERACTION_MODE,
                               g_gv.asi_local_mission, g_gv.encountered_party);
    if (kind != LOCAL_MISSION_NONE) {
        /* gameType is NOT changed in the fixup -- it stays at 4 so network
           listen/send in mbCoreGame::frameMove keep working. gameType=0 is
           set here (inside the window dispatch, after network listen) and
           restored in the frameMove cleanup (before network send). */
        g_in_coop_local_mission = 1;
        g_local_mission_kind = kind;
        coop_log("local mission flag set (gameType stays 4 until window dispatch)\n");
        coop_flush_client_events();
        *(int *)ADDR_MAP_INTERACTION_MODE = 0;
    }
}

__declspec(naked) void setparams_prologue_detour(void) {
    __asm {
        push eax
        push ecx
        push edx
        call setparams_pre
        pop  edx
        pop  ecx
        pop  eax
        jmp  [g_sp_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  mission_frameMove — per-frame gameType flip for coop local missions */
/*  Sets gameType=0 during frameMove so all SP subsystems work, then  */
/*  restores to 4 on return so network listen/send (which run outside */
/*  frameMove in mbCoreGame::frameMove) see gameType=4.               */
/* ------------------------------------------------------------------ */

static DWORD g_mfm_trampoline = 0;
static BYTE  g_mfm_saved[16]  = {0};
static DWORD g_mfm_saved_retaddr = 0;

static void __cdecl mfm_pre(void) {
    if (*(int *)ADDR_MAP_INTERACTION_MODE == 4 && !g_in_coop_local_mission) {
        flush_result_string_to_file();
        check_pending_local_result();
    }
    if (g_in_coop_local_mission) {
        *(int *)ADDR_MAP_INTERACTION_MODE = 0;
    }
}

__declspec(naked) void mission_framemove_detour(void) {
    __asm {
        push eax
        push ecx
        push edx
        call mfm_pre
        pop  edx
        pop  ecx
        pop  eax

        cmp dword ptr [g_in_coop_local_mission], 0
        je  mfm_passthrough

        /* Swap return address so we can restore gameType after return */
        pop dword ptr [g_mfm_saved_retaddr]
        push offset mfm_cleanup
        jmp [g_mfm_trampoline]

    mfm_cleanup:
        mov dword ptr ds:[0xA89524], 4  /* = ADDR_MAP_INTERACTION_MODE — keep in sync with warband_addrs_wse2.h */
        jmp dword ptr [g_mfm_saved_retaddr]

    mfm_passthrough:
        jmp [g_mfm_trampoline]
    }
}

#if 0
#elif defined(ADDR_MAP_INTERACTION_MODE)
/* static assert the asm literal above matches the table */
typedef char assert_game_type_addr[(ADDR_MAP_INTERACTION_MODE == 0xA89524) ? 1 : -1];
#endif

/* ------------------------------------------------------------------ */
/*  Mission-end transition hook at 0x5C68BE                           */
/*  This is inside mbTacticalWindow::frameMove, at the point where    */
/*  the engine detects the mission has ended and transitions to the   */
/*  post-battle menu.  The original instruction is:                   */
/*    cmp dword ptr [0xA89524], 0   (7 bytes: 83 3D 24 95 A8 00 00)  */
/*  We hook here to restore gameType=4 before the menu transition     */
/*  so the debrief menu's MP opcodes work correctly.                  */
/* ------------------------------------------------------------------ */

static DWORD g_met_trampoline = 0;
static BYTE  g_met_saved[16]  = {0};

static void __cdecl mission_end_restore_gametype(void) {
    /* The teardown epilogue this hook sits in drops the campaign connection
       for any mission ended at gameType 4, so the client lands in the
       server browser. A visit has no debrief to show; rejoin straight
       away. A local battle keeps its debrief menu and the manual rejoin
       (its result travels by file on the next browser visit). */
    if (local_mission_end(&g_in_coop_local_mission, &g_local_mission_kind,
                          (int *)ADDR_MAP_INTERACTION_MODE))
        arm_campaign_return("visit over");
}

__declspec(naked) void mission_end_transition_detour(void) {
    __asm {
        push eax
        push ecx
        push edx
        call mission_end_restore_gametype
        pop  edx
        pop  ecx
        pop  eax
        /* Execute original cmp + continue */
        jmp  [g_met_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  Replication row guard at ADDR_REPL_PARTY_ROW_LOOKUP               */
/*  receivePacket applies the packet's events (party removal among    */
/*  them) before its replication rows, and the client replication     */
/*  table never drops a removed party's rows. A row for that party    */
/*  then reaches the pointer math with getRawIndex() == -1. Skip the  */
/*  row instead; the continue target only reads ebp locals/edi/ebx.  */
/* ------------------------------------------------------------------ */

static DWORD g_rpl_trampoline = 0;
static BYTE  g_rpl_saved[16]  = {0};
static const BYTE g_rpl_expected[REPL_PARTY_ROW_LOOKUP_SIZE] =
    {0x8B, 0xD0, 0x8B, 0x86, 0x10, 0x3D, 0x01, 0x00};

static void __cdecl replication_row_missing_party(int row_index) {
    coop_log("replication row %d for missing party %d skipped\n",
             row_index, row_index / 4);
}

__declspec(naked) void replication_party_lookup_detour(void) {
    __asm {
        cmp  eax, -1
        jne  rpl_have_party
        push ecx
        push edx
        push dword ptr [ebp-0x10]      /* row index local of receiveReplicationData */
        call replication_row_missing_party
        add  esp, 4
        pop  edx
        pop  ecx
        mov  eax, 0x54456C             /* = ADDR_REPL_PARTY_ROW_NEXT -- keep in sync with warband_addrs_wse2.h */
        jmp  eax
    rpl_have_party:
        jmp  [g_rpl_trampoline]
    }
}

typedef char assert_repl_row_next_addr[(ADDR_REPL_PARTY_ROW_NEXT == 0x54456C) ? 1 : -1];

/* ------------------------------------------------------------------ */
/*  Talk-branch redirect in mbPartyWindow::frameMove                   */
/*  Party-window "Talk" starts a map conversation, an SP-only mission  */
/*  path: on an MP campaign client the mission's entry-group source is */
/*  never populated (null deref in spawnEntryGroups), and the caller's */
/*  tail then flips the UI into a conversation window with no scene    */
/*  (renderer crash) -- so the whole branch must be skipped, not just  */
/*  the callee.  Hooked instruction is the 5-byte call itself.  MP     */
/*  (gameType 4): drop the 4 pushed args (callee was ret 0x10), open   */
/*  the clicked member's character sheet instead (the engine's own     */
/*  companion-open sequence, read-only for zero-point troops), and     */
/*  jump to the branch join point.  SP: re-emit the call with an       */
/*  absolute target (the original relative call cannot run relocated   */
/*  in the trampoline) and resume at the next instruction.  The join   */
/*  point consumes edi (party-window this); the detour must preserve   */
/*  edi/esi/ebx, and does.                                             */
/* ------------------------------------------------------------------ */

static DWORD g_smc_trampoline = 0;  /* unused: relative call can't relocate */
static BYTE  g_smc_saved[16]  = {0};
static DWORD g_talk_resume = ADDR_PARTY_TALK_RESUME;
static DWORD g_talk_join   = ADDR_PARTY_TALK_JOIN;

static int __cdecl smc_block_check(void) {
    if (*(int *)ADDR_MAP_INTERACTION_MODE != 4) return 0;
    coop_log("party Talk: opening character sheet instead of conversation (MP campaign)\n");
    return 1;
}

/* Mirrors the engine's canonical companion-open (0x534DF9): point the
   character window at the troop, remember the party window as the
   return-to screen, switch windows.  Runs on the UI thread (inside
   mbPartyWindow::frameMove), so the engine call is safe. */
static void __cdecl smc_view_character(int troop_no) {
    BYTE *char_win = *(BYTE **)ADDR_CHAR_WINDOW_PTR;
    void (__stdcall *set_window)(int) = (void (__stdcall *)(int))ADDR_SET_WINDOW;
    if (!char_win) return;
    *(int *)(char_win + 0x10) = troop_no;           /* m_viewedTroopNo */
    *(int *)(char_win + 0x14) = WINDOW_ID_PARTY;    /* m_sourceWindowNo */
    *(int *)(char_win + 0x04) = 1;                  /* m_mode (canonical) */
    set_window(WINDOW_ID_CHARACTER);
}

__declspec(naked) void party_talk_call_detour(void) {
    __asm {
        /* ecx = thiscall this for the passthrough; edi stays untouched */
        push ecx
        push edx
        call smc_block_check
        pop  edx
        pop  ecx
        test eax, eax
        jnz  smc_view
        mov  eax, ADDR_START_MAP_CONVERSATION
        call eax                    /* callee cleans the 4 args (ret 0x10) */
        jmp  [g_talk_resume]
      smc_view:
        mov  ecx, [esp]             /* arg1 convTroopNo (pushed last) */
        add  esp, 0x10              /* drop the 4 conversation args */
        push ecx
        call smc_view_character     /* cdecl: preserves edi/esi/ebx */
        add  esp, 4
        jmp  [g_talk_join]
    }
}

/* ------------------------------------------------------------------ */
/*  Window close hooks: vtable patches to set global variable flags   */
/* ------------------------------------------------------------------ */

/* Screen close detection moved to poller-only (simple triggers pause during
   native windows, so open==1 in poller means screen just closed). No vtable
   hooks needed -- wse_window_opened sets the open flag, poller diffs on close. */

static const BYTE k_nops[16] = {
    0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90,
    0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 };

/* ------------------------------------------------------------------ */
/*  DllMain                                                           */
/* ------------------------------------------------------------------ */

BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;
    if (fdwReason == DLL_PROCESS_ATTACH) {
        char exe_path[MAX_PATH];
        DisableThreadLibraryCalls(hinstDLL);
        GetModuleFileNameA(NULL, exe_path, MAX_PATH);
        if (!strstr(exe_path, "mb_warband_wse2.exe")) return TRUE;

        /* Derive game dir (dirname of exe) for later use by variables.txt lookup */
        asi_game_dir(exe_path, g_game_dir, MAX_PATH);

        g_log = fopen("warband_coop.log", "w");
        coop_log("warband_coop.asi loaded\n");
        read_config(hinstDLL);

        /* Module global access: client vector addresses are raw literals
           (ASLR disabled via binary patch). Resolve all setParams-fixup +
           result-reporting IDs in one variables.txt pass. */
        {
            char vars_path[MAX_PATH];
            modglobals_desc d;

            g_addrs = &g_addrs_client;
            d.vec_first_addr = g_addrs->global_vars_vec;
            d.vec_last_addr  = g_addrs->global_vars_end;
            modglobals_init(&d);

            _snprintf(vars_path, sizeof(vars_path), "%s\\Modules\\%s\\variables.txt",
                      g_game_dir, g_cfg.module_name);
            vars_path[MAX_PATH-1] = 0;
            asi_gvars_resolve(&g_gv, vars_path);
        }

        /* Background thread for s59 */
        CreateThread(NULL, 0, s59_writer_thread, NULL, 0, NULL);

        /* Steam P2P tunnel (no-op unless coop.ini [Steam] sets a role) */
        steam_tunnel_start(&g_cfg.steam);

        /* Hook server browser's frameMove to inject server entry */
        hook_install(ADDR_BROWSER_FRAMEMOVE, browser_framemove_detour,
                     BROWSER_PROLOGUE_SIZE, g_fm_saved, &g_fm_trampoline);
        coop_log("browser frameMove hooked at 0x%X\n", ADDR_BROWSER_FRAMEMOVE);

        /* Auto-join on invite landing: per-frame arm/fire/cleanup driver.
           Idles on a single armed-bit read for LAN/no-Steam sessions. */
        hook_install(ADDR_FRAMEMOVE, autojoin_framemove_detour,
                     FRAMEMOVE_PROLOGUE_SIZE, g_aj_saved, &g_aj_trampoline);
        coop_log("app frameMove hooked at 0x%X (auto-join driver)\n", ADDR_FRAMEMOVE);

        /* Patch addExperienceToTroop to allow negative XP (Fix H).
           Engine clamps xp_amount < 0 to 0 at 0x4B84A9 (8 bytes:
           test ebx,ebx / jns / xor ebx,ebx / jmp).  NOP the clamp so
           char_sync_xp can correct client XP downward.  The upper clamp
           (cap at 29999) at 0x4B84B1 is preserved. */
        {
            static const BYTE xp_clamp[] = { 0x85, 0xDB, 0x79 };
            BYTE *addr = (BYTE *)0x4B84A9;
            if (asi_patch_verified(addr, xp_clamp, 3, k_nops, 8)) {
                coop_log("addExperienceToTroop negative-clamp patched (8 NOPs at 0x4B84A9)\n");
            } else {
                coop_log("addExperienceToTroop: unexpected bytes at 0x4B84A9 (0x%02X 0x%02X), skipping patch\n",
                         addr[0], addr[1]);
            }
        }

        /* Patch mbMission::start to allow campaign clients to spawn agents
           locally for SP encounters (Fix I: local mission agent spawn).

           The engine has two gates in mbMission::start (0x4F5490) that skip
           entry point init and agent spawning when gameType == 1 (MP client)
           or gameType == 4 (campaign client):

           Gate 1 @ 0x4F713E: je 0x4F7340 (skip entry point init)
           Gate 1 @ 0x4F7147: je 0x4F7340 (skip for gameType==4)
           Gate 2 @ 0x4F8B7A: je 0x4F8C26 (skip spawnEntryGroups)
           Gate 2 @ 0x4F8B83: je 0x4F8C26 (skip for gameType==4)

           NOP both gates so campaign clients can run local SP missions
           with proper agent spawning. */
        {
            static const BYTE je_near[] = { 0x0F, 0x84 };
            static const struct { DWORD addr; const char *name; } gates[] = {
                { 0x4F713E, "gate1a" },   /* Gate 1: entry point initialization */
                { 0x4F7147, "gate1b" },
                { 0x4F8B7A, "gate2a" },   /* Gate 2: reinforceEntryGroup + spawnEntryGroups */
                { 0x4F8B83, "gate2b" },
            };
            int i;
            for (i = 0; i < 4; i++) {
                BYTE *g = (BYTE *)gates[i].addr;
                if (asi_patch_verified(g, je_near, 2, k_nops, 6)) {
                    coop_log("mbMission::start %s patched (6 NOPs at 0x%X)\n", gates[i].name, gates[i].addr);
                } else {
                    coop_log("mbMission::start %s: unexpected bytes 0x%02X 0x%02X, skipping\n",
                             gates[i].name, g[0], g[1]);
                }
            }
        }

        /* Gate 3: MP visitor troopNos wipe loop @ 0x4F57FE-0x4F581C.
           After setParams runs, mbMission::start has a loop gated on
           gameType != 0 that iterates all 128 visitors and clears
           m_troopNos (m_end = m_begin). This wipes the troops we
           pushed via add_visitors_to_current_scene before
           spawnEntryGroups can read them. Patch the je at 0x4F5805
           (74 16) to jmp (EB 16) to always skip the wipe loop. */
        {
            static const BYTE je_short[] = { 0x74, 0x16 };
            static const BYTE jmp_short[] = { 0xEB };
            BYTE *g3 = (BYTE *)0x4F5805;
            if (asi_patch_verified(g3, je_short, 2, jmp_short, 1)) {
                coop_log("mbMission::start gate3 patched (je->jmp at 0x4F5805)\n");
            } else {
                coop_log("mbMission::start gate3: unexpected bytes 0x%02X 0x%02X, skipping\n", g3[0], g3[1]);
            }
        }

        /* Patch agent_tick + mission_frameMove to enable bot AI, physics,
           and missiles on gameType=4 (coop local battles).

           The engine skips all agent AI processing for gameType 1 (MP client)
           and gameType 4 (campaign client) because it expects the server to
           handle AI. For local battles the client IS the server, so we NOP
           the gameType==4 branches. The gameType==1 branches remain intact
           so normal MP is unaffected.

           Gate layout (all are cmp eax/edi,4 / je or cmp eax,4 / je-near):
             agent_tick (0x424690):
               0x424884 - 9 bytes - agent physics/collision
               0x424C38 - 5 bytes - AI timing checks
               0x424CF0 - 9 bytes - AI decision block (PRIMARY)
               0x42505F - 5 bytes - weapon action processing
             mission_frameMove (0x4FC450):
               0x4FC640 - 5 bytes - bot spawn tick
               0x4FC8F4 - 9 bytes - missile physics */
        {
            struct { BYTE *addr; int len; BYTE op0; BYTE op1; const char *name; } ai_gates[] = {
                /* agent_tick gates */
                { (BYTE*)0x424884, 9, 0x83, 0xF8, "agent physics/collision"    },
                { (BYTE*)0x424C38, 5, 0x83, 0xF8, "AI timing checks"          },
                { (BYTE*)0x424CF0, 9, 0x83, 0xF8, "AI decision block"         },
                { (BYTE*)0x42505F, 5, 0x83, 0xFF, "weapon action processing"  },
                /* mission_frameMove gates */
                { (BYTE*)0x4FC640, 5, 0x83, 0xF8, "bot spawn tick"            },
                { (BYTE*)0x4FC8F4, 9, 0x83, 0xF8, "missile physics"           },
                /* perception orchestrator gates (0x506330) --
                   without these, m_aiPerceptionReady is never set
                   and agent_runAIDecision bails immediately */
                { (BYTE*)0x50763D, 9, 0x83, 0xF8, "perception LOS/visibility" },
                { (BYTE*)0x507B67, 9, 0x83, 0xF8, "perception team/encounter" },
                { (BYTE*)0x507D09, 9, 0x83, 0xF8, "perception inner loop"     },
                { (BYTE*)0x508A99, 5, 0x83, 0xF8, "perception final scan"     },
            };
            for (int i = 0; i < 10; i++) {
                BYTE cmp_op[2];
                cmp_op[0] = ai_gates[i].op0;
                cmp_op[1] = ai_gates[i].op1;
                if (asi_patch_verified(ai_gates[i].addr, cmp_op, 2, k_nops, ai_gates[i].len)) {
                    coop_log("agent AI gate %d patched (%d NOPs at 0x%X): %s\n",
                             i, ai_gates[i].len, (DWORD)ai_gates[i].addr, ai_gates[i].name);
                } else {
                    coop_log("agent AI gate %d: unexpected bytes 0x%02X 0x%02X at 0x%X, skipping (%s)\n",
                             i, ai_gates[i].addr[0], ai_gates[i].addr[1],
                             (DWORD)ai_gates[i].addr, ai_gates[i].name);
                }
            }
        }

        /* createAgent detour -- substitute playerNo for local player on
           gameType=4 so the MP attach branch at LAB_00500C2B fires.
           See design doc: docs/superpowers/specs/2026-04-16-sp-local-encounter-redirect-design.md */
        hook_install(ADDR_CREATE_AGENT, create_agent_detour,
                     CREATE_AGENT_PROLOGUE_SIZE, g_ca_saved, &g_ca_trampoline);
        coop_log("mbMission::createAgent hooked at 0x%X (trampoline=0x%X)\n",
                 ADDR_CREATE_AGENT, g_ca_trampoline);

        /* Option C: prologue detour on mbMission::setParams so every caller
           (including the coop local-fight caller at 0x4ED30A) runs our
           metaMission fixup before setParams reads encounteredParties.
           setParams prologue is 7 bytes (push ebp; mov ebp,esp; push ecx;
           mov eax,[ebp+8]) -- hook_install copies 7 complete bytes. */
        hook_install(ADDR_SET_PARAMS, setparams_prologue_detour,
                     7, g_sp_saved, &g_sp_trampoline);
        coop_log("mbMission::setParams hooked at 0x%X (trampoline=0x%X)\n",
                 ADDR_SET_PARAMS, g_sp_trampoline);

        /* mission_frameMove: per-frame gameType flip for local missions.
           Sets gameType=0 during frameMove (inside window dispatch),
           restores to 4 after (before network send/manager). */
        hook_install(ADDR_MISSION_FRAMEMOVE, mission_framemove_detour,
                     MISSION_FRAMEMOVE_PROLOGUE, g_mfm_saved, &g_mfm_trampoline);
        coop_log("mission_frameMove hooked at 0x%X (trampoline=0x%X)\n",
                 ADDR_MISSION_FRAMEMOVE, g_mfm_trampoline);

        /* Mission-end transition hook at 0x5C68BE (inside
           mbTacticalWindow::frameMove).  Restores gameType=4 right
           before the engine transitions from mission to post-battle
           menu, so the debrief menu's MP opcodes work. */
        hook_install(ADDR_MISSION_END_TRANSITION, mission_end_transition_detour,
                     MISSION_END_TRANSITION_SIZE, g_met_saved, &g_met_trampoline);
        coop_log("mission-end transition hooked at 0x%X (trampoline=0x%X)\n",
                 ADDR_MISSION_END_TRANSITION, g_met_trampoline);

        /* Party replication rows for a party the client no longer has:
           skip instead of dereferencing a raw index of -1. */
        if (hook_install_verified(ADDR_REPL_PARTY_ROW_LOOKUP, replication_party_lookup_detour,
                                  REPL_PARTY_ROW_LOOKUP_SIZE, g_rpl_expected,
                                  g_rpl_saved, &g_rpl_trampoline))
            coop_log("replication party-row lookup guarded at 0x%X (trampoline=0x%X)\n",
                     ADDR_REPL_PARTY_ROW_LOOKUP, g_rpl_trampoline);

        /* Talk-branch short-circuit: party-window Talk crashes MP clients
           (SP-only conversation mission + scene-less window transition).
           Hook covers exactly the 5-byte call; the trampoline hook_install
           builds holds an unrelocatable relative call and is never used --
           the detour re-emits the call with an absolute target. */
        hook_install(ADDR_PARTY_TALK_CALL, party_talk_call_detour,
                     5, g_smc_saved, &g_smc_trampoline);
        coop_log("party-window Talk call hooked at 0x%X\n", ADDR_PARTY_TALK_CALL);

        coop_log("init complete\n");
    }
    else if (fdwReason == DLL_PROCESS_DETACH) {
        if (g_log) { fclose(g_log); g_log = NULL; }
    }
    return TRUE;
}
