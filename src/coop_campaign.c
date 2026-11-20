#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <stdio.h>
#include <stdarg.h>

#include "warband_addrs_wse2.h"
#include "hook.h"
#include "crash_report.h"
#include "coop_campaign.h"
#include "battle_net.h"
#include "battle_ipc.h"
#include "campaign_ipc.h"
#include "battle_end.h"
#include "coop_config.h"
#include "coop_gvars.h"
#include "set_xp.h"
#include "modglobals.h"
#include "nettune.h"
#include <shlobj.h>  /* SHGetFolderPathA */

/* ------------------------------------------------------------------ */
/*  Logging                                                           */
/* ------------------------------------------------------------------ */

static FILE *g_log = NULL;

void coop_log(const char *fmt, ...) {
    if (!g_log) return;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(g_log, fmt, ap);
    va_end(ap);
    fflush(g_log);
    {
        char ring_buf[256];
        va_list ap2;
        va_start(ap2, fmt);
        vsnprintf(ring_buf, sizeof(ring_buf), fmt, ap2);
        va_end(ap2);
        crash_ring_write(ring_buf);
    }
}

void coop_flush_log(void) {
    if (g_log) fflush(g_log);
}

/* ------------------------------------------------------------------ */
/*  Config                                                            */
/* ------------------------------------------------------------------ */

static coop_mode_t g_coop_mode = COOP_HOST;
static int         g_port = 7240;
static char        g_host_ip[64] = "127.0.0.1";
static char        g_module_name[64] = "NativeCoop";
static char        g_server_password[64] = "";
static int         g_debug_reveal = 0;   /* COOP_DEBUG_REVEAL env: campaign server marks every party map-visible */
static char        g_ini_path[MAX_PATH];  /* stashed for nettune_apply, called once g_log is open */

/* ------------------------------------------------------------------ */
/*  Module global variable indices -- resolved from variables.txt      */
/* ------------------------------------------------------------------ */

static coop_gvars g_gv = COOP_GVARS_UNRESOLVED;

/* ------------------------------------------------------------------ */
/*  Battle slot state                                                  */
/* ------------------------------------------------------------------ */

static int   g_battle_slot = 0;                          /* COOP_BATTLE: pool slot from env */
static ipc_slots g_ipc = { {NULL}, &g_gv.ipc, -1 };      /* COOP_HOST: peer per slot */

/* ------------------------------------------------------------------ */
/*  Hook state                                                        */
/* ------------------------------------------------------------------ */

/* Per-personality engine sites the frame hook and the set_xp consumer
   use. The campaign hooks mbGame::frameMove; a battle server runs every
   frame inside mbMission::frameMove. Both are main-thread, between script
   ticks, so a consumer there never races the engine's own troop writes. */
typedef struct personality_sites {
    const char *frame_fn_name;
    DWORD frame_fn;
    int   frame_prologue_size;
    BYTE  frame_prologue[16];
    DWORD level_table;
    DWORD level_boundary_mult;
} personality_sites;

static const personality_sites g_sites_campaign = {
    "campaign mbGame::frameMove", CAMP_ADDR_CAMPAIGN_TICK,
    CAMP_CAMPAIGN_TICK_PROLOGUE_SIZE, CAMP_CAMPAIGN_TICK_PROLOGUE_BYTES,
    CAMP_ADDR_LEVEL_TABLE, CAMP_ADDR_LEVEL_BOUNDARY_MULT,
};
static const personality_sites g_sites_battle = {
    "battle mbMission::frameMove", DED_ADDR_MISSION_FRAMEMOVE,
    DED_MISSION_FRAMEMOVE_PROLOGUE_SIZE, DED_MISSION_FRAMEMOVE_PROLOGUE_BYTES,
    DED_ADDR_LEVEL_TABLE, DED_ADDR_LEVEL_BOUNDARY_MULT,
};
static const personality_sites *g_sites = NULL;   /* pinned once at init */

static DWORD g_fm_trampoline = 0;
static BYTE  g_fm_saved[16];

static DWORD g_mask_refresh_tick = 0;   /* IPC-thread mask republish cadence */

/* ------------------------------------------------------------------ */
/*  Forward declarations                                              */
/* ------------------------------------------------------------------ */

static void coop_on_frame(void);
static void coop_post_frame(void);
static void coop_on_ipc_packet(void *peer, const uint8_t *data, int len);
static void coop_on_ipc_event(void *peer, int connected);

/* ------------------------------------------------------------------ */
/*  FrameMove detour -- installed at the personality's frame function       */
/*  (g_sites->frame_fn). Runs both coop callbacks between ticks, then       */
/*  jmp's into the trampoline so the hooked function's own return goes      */
/*  straight back to the engine caller.                                     */
/* ------------------------------------------------------------------ */

__declspec(naked) void framemove_detour(void) {
    __asm {
        /* Between-ticks coop processing (net poll + deferred commands).
           Must be jmp-style: a call into the trampoline would shift the
           hooked function's argument frame by one slot. */
        sub  esp, 64
        movdqu [esp],      xmm0
        movdqu [esp + 16], xmm1
        movdqu [esp + 32], xmm2
        movdqu [esp + 48], xmm3
        pushad
        sub  esp, 112
        fsave [esp]
        call coop_on_frame
        call coop_post_frame
        frstor [esp]
        add  esp, 112
        popad
        movdqu xmm0, [esp]
        movdqu xmm1, [esp + 16]
        movdqu xmm2, [esp + 32]
        movdqu xmm3, [esp + 48]
        add  esp, 64
        jmp  dword ptr [g_fm_trampoline]
    }
}

/* ------------------------------------------------------------------ */
/*  coop_on_frame                                                     */
/* ------------------------------------------------------------------ */

/* ASLR slide — computed once, used by REBASE() macro in warband_addrs_wse2.h */
DWORD g_aslr_slide = 0;

/* --- IPC thread: hosts the battle-server ENet listener and republishes
   the slots-online mask. It is the SOLE owner of the ENet host: enet_host_service
   mutates peer/ack lists with no internal locking, so polling from the
   framemove hook as well double-frees under load (heap corruption 0xC0000374).
   Running here also guarantees liveness when frames stall (loading screens). --- */
static HANDLE g_poll_thread = NULL;
static volatile LONG g_poll_running = 0;

static DWORD WINAPI ipc_thread_func(LPVOID param) {
    (void)param;
    /* Wait for process to fully initialize (DllMain loader lock) */
    Sleep(1000);

    if (g_coop_mode == COOP_HOST) {
        bnet_init(1 /* listener */, IPC_PORT, IPC_MAX_BATTLE_SLOTS);
        bnet_set_recv_callback(coop_on_ipc_packet);
        bnet_set_event_callback(coop_on_ipc_event);
        coop_log("campaign mode: IPC listener on port %d\n", IPC_PORT);
    }

    while (g_poll_running) {
        bnet_poll();
        /* Republish the battle-slot online mask ~1/s: the module's startup
           script zeroes $g_coop_battle_slots_online after load, and a HELLO
           processed before the globals vector exists would otherwise be
           lost for good (mask writes are event-driven). */
        if (g_coop_mode == COOP_HOST && (++g_mask_refresh_tick & 63) == 0)
            ipc_slots_publish_mask(&g_ipc);
        Sleep(16);  /* ~60Hz */
    }
    return 0;
}

static void start_ipc_thread(void) {
    if (g_poll_thread) return;
    g_poll_running = 1;
    g_poll_thread = CreateThread(NULL, 0, ipc_thread_func, NULL, 0, NULL);
    if (g_poll_thread)
        coop_log("ipc thread started (init in 1s)\n");
}

static void stop_ipc_thread(void) {
    if (!g_poll_thread) return;
    InterlockedExchange(&g_poll_running, 0);
    WaitForSingleObject(g_poll_thread, 3000);
    CloseHandle(g_poll_thread);
    g_poll_thread = NULL;
    coop_log("ipc thread stopped\n");
}

static void coop_on_frame(void) {
    crash_heartbeat();
}

/* ------------------------------------------------------------------ */
/*  coop_post_frame — runs between ticks, just before the next          */
/*  mbGame::frameMove call (jmp-style detour, see framemove_detour).    */
/*  Processes deferred commands the previous tick's scripts signalled   */
/*  via globals.                                                        */
/* ------------------------------------------------------------------ */

static int engine_troops(set_xp_troops *out) {
    void *game = wb_cur_game();
    if (!game) return 0;
    out->arr = *(char **)((char *)game + MBGAME_OFF_TROOP_ARRAY);
    out->count = *(int *)((char *)game + MBGAME_OFF_NUM_TROOPS);
    out->level_table = (const int *)REBASE(g_sites->level_table);
    out->boundary_mult = *(float *)REBASE(g_sites->level_boundary_mult);
    return 1;
}

static void coop_post_frame(void) {
    /* --- troop_set_xp: authoritative XP write (Fix H) ---
       The module script requests a direct mbTroop.m_experience write by
       setting $g_coop_set_xp_go = 1 (+ troop/value globals) during its
       tick; we consume it here, at the entry of the next frame, so the
       script's global writes are already visible and every troop_get_xp
       from that frame on sees the corrected value. Both personalities:
       a battle server's char load queues the same request.

       Known accepted drift: a coop_save_character in the SAME frame as
       the requesting script (the phase-2 save in player_joined) still
       reads the stale base XP — the DLL cannot call module scripts to
       re-trigger the save post-write.  The next save (autosave every 300
       campaign hours, or exit) captures the corrected total, which bounds the drift. */
    __try {
        coop_set_xp_consume(&g_gv, engine_troops);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        /* Access violation during global/troop read — vector may be reallocating */
    }
}

/* ------------------------------------------------------------------ */
/*  INI parsing                                                       */
/* ------------------------------------------------------------------ */

static void coop_load_ini(const char *dll_dir) {
    char *ini_path = g_ini_path;

    lstrcpynA(ini_path, dll_dir, MAX_PATH);
    lstrcatA(ini_path, "coop.ini");

    /* Mode comes from the exe name alone; the winmm loader only loads this
       plugin into dedicated servers (coop_loader.c). */
    {
        char exe_name[MAX_PATH];
        GetModuleFileNameA(NULL, exe_name, MAX_PATH);
        g_coop_mode = coop_mode_from_exe(exe_name);
    }

    g_port = GetPrivateProfileIntA("Coop", "Port", 7240, ini_path);
    GetPrivateProfileStringA("Coop", "HostIP", "127.0.0.1", g_host_ip, sizeof(g_host_ip), ini_path);
    GetPrivateProfileStringA("Coop", "Module", "NativeCoop", g_module_name, sizeof(g_module_name), ini_path);
    GetPrivateProfileStringA("Coop", "Password", "", g_server_password, sizeof(g_server_password), ini_path);

    if (g_coop_mode == COOP_BATTLE) {
        char slot_str[8];
        int set = GetEnvironmentVariableA("COOP_BATTLE_SLOT", slot_str, sizeof(slot_str)) > 0;
        g_battle_slot = coop_battle_slot_from_env(set ? slot_str : NULL);
        coop_log("battle slot: %d (COOP_BATTLE_SLOT env)\n", g_battle_slot);
    }

    if (g_coop_mode == COOP_HOST) {
        char reveal_str[8];
        int set = GetEnvironmentVariableA("COOP_DEBUG_REVEAL", reveal_str, sizeof(reveal_str)) > 0;
        g_debug_reveal = coop_debug_reveal_from_env(set ? reveal_str : NULL);
    }

    coop_log("config: mode=%s port=%d host=%s module=%s password=%s debug_reveal=%d\n",
             g_coop_mode == COOP_HOST ? "host" : "battle",
             g_port, g_host_ip, g_module_name,
             g_server_password[0] ? "set" : "none", g_debug_reveal);
}

/* ------------------------------------------------------------------ */
/*  Global variable resolver (from variables.txt)                      */
/* ------------------------------------------------------------------ */

static void resolve_battle_global_indices(void) {
    char exe[MAX_PATH], path[MAX_PATH];
    GetModuleFileNameA(NULL, exe, MAX_PATH);
    coop_variables_path(path, MAX_PATH, exe, g_module_name);
    coop_gvars_resolve(path, &g_gv);
}

/* ------------------------------------------------------------------ */
/*  Server config dict writing                                        */
/* ------------------------------------------------------------------ */

static void write_server_cfg_dict(void) {
    char exe[MAX_PATH], dir[MAX_PATH];
    GetModuleFileNameA(NULL, exe, MAX_PATH);
    coop_wse_dict_dir(dir, MAX_PATH, exe, g_module_name);
    coop_write_server_cfg(dir, g_coop_mode, g_server_password, g_debug_reveal);
}

/* ------------------------------------------------------------------ */
/*  Battle data collection + dict writing + IPC signal (COOP_BATTLE)   */
/* ------------------------------------------------------------------ */

static void battle_collect_and_save(void) {
    int winner;
    int player_count = 0;

    winner = modglobals_get_int(g_gv.mp_winner, 0);

    coop_log("[battle] round ended: winner=%d\n", winner);

    /* Count active players for IPC packet.
       SP XP parity moved all XP computation to the campaign-side module script;
       the DLL no longer touches char_xp. */
    {
        int max_players = ded_num_players_limit();
        int i;
        for (i = 1; i < max_players && i < 250; i++) {
            char *p = ded_get_player(i);
            int troop_no;
            if (!p || *(int *)(p + PLAYER_OFF_STATUS) == 0) continue;
            troop_no = *(int *)(p + PLAYER_OFF_TROOP_NO);
            if (troop_no < 0) continue;
            player_count++;
        }
    }

    /* Send IPC signal to campaign server */
    {
        uint8_t buf[PKT_HDR_SIZE + sizeof(battle_end_signal_t)];
        bnet_send(buf, battle_end_build(buf, g_battle_slot, winner, player_count));
        coop_log("[battle] sent PKT_BATTLE_END: winner=%d players=%d\n",
                 winner, player_count);
    }
}

/* ------------------------------------------------------------------ */
/*  Battle polling thread (COOP_BATTLE mode only)                      */
/* ------------------------------------------------------------------ */

static HANDLE g_battle_poll_thread = NULL;
static volatile LONG g_battle_poll_running = 0;
static battle_end_edge g_battle_end_edge = {0, 0};

/* Engine function: mbBasicGame::getGlobalVariable(int index) -> __int64
   __thiscall: this in ECX. Use __fastcall(this, edx_unused, index) in C. */
typedef __int64 (__fastcall *getGlobalVar_fn)(void *, void *, int);

static void battle_on_ipc_event(void *peer, int connected) {
    (void)peer;
    if (connected) {
        uint8_t buf[PKT_HDR_SIZE + sizeof(battle_hello_t)];
        bnet_send(buf, battle_hello_build(buf, g_battle_slot));
        coop_log("[battle] IPC up, sent HELLO slot=%d\n", g_battle_slot);
    }
}

static DWORD WINAPI battle_poll_thread_func(LPVOID param) {
    (void)param;
    Sleep(2000);  /* wait for server to fully initialize (loader lock safe) */

    bnet_init(0 /* client */, IPC_PORT, 1);
    bnet_set_event_callback(battle_on_ipc_event);
    coop_log("[battle] IPC client connecting to localhost:%d\n", IPC_PORT);
    coop_log("[battle] poll thread started\n");

    while (g_battle_poll_running) {
        __int64 battle_started = 0;

        /* SEH guard: mission restart deallocates the global variable vector.
           The poll thread may read freed memory during the brief reallocation
           window. Catch the access violation and retry next iteration. */
        __try {
            /* Publish our slot for module dict-name derivation. Idempotent;
               the vector may be reallocated on mission restart (SEH-guarded). */
            modglobals_set(g_gv.battle_slot, g_battle_slot);
            modglobals_get(g_gv.battle_started, &battle_started);
        } __except(EXCEPTION_EXECUTE_HANDLER) {
            Sleep(100);
            continue;
        }

        /* battle_started -> -1: coop_copy_parties_to_file_mp has finished the
           dict_save of @coop_battle, so PKT_BATTLE_END cannot race the module save. */
        if (battle_end_edge_step(&g_battle_end_edge, battle_started))
            battle_collect_and_save();

        bnet_poll();
        {
            static DWORD s_last_reconnect = 0;
            DWORD now = GetTickCount();
            if (!bnet_is_connected() && (now - s_last_reconnect) > 5000) {
                s_last_reconnect = now;
                bnet_reconnect();
            }
        }
        Sleep(16);  /* ~60Hz */
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Hook installation (called from campaign_init_from_ini)             */
/* ------------------------------------------------------------------ */

static void install_hooks(void) {
    /* The personality's PDB-derived frame function (the client VA
       ADDR_CAMPAIGN_TICK is a DIFFERENT binary and must never be
       patched here — see findings "B2 fix addresses"). */
    if (!hook_install_verified(REBASE(g_sites->frame_fn), framemove_detour,
                               g_sites->frame_prologue_size, g_sites->frame_prologue,
                               g_fm_saved, &g_fm_trampoline)) {
        coop_log("framemove hook REFUSED (byte mismatch) at %s — per-frame coop "
                 "processing (set_xp) is OFFLINE\n", g_sites->frame_fn_name);
        return;
    }
    coop_log("framemove hook installed at %s 0x%08X\n",
             g_sites->frame_fn_name, REBASE(g_sites->frame_fn));
}

/* ------------------------------------------------------------------ */
/*  Binary patches (AI walk limit)                                    */
/* ------------------------------------------------------------------ */

static void install_patches(void) {
    /* AI path pre-walk limit 6 -> 100 (campaign-exe site, PDB-derived).
       Verify-before-write: stock imm8 must be 0x06. */
    DWORD old_prot;
    BYTE *p = (BYTE *)REBASE(CAMP_ADDR_AI_PATH_WALK_LIMIT);
    if (*p != 0x06) {
        coop_log("AI walk-limit patch SKIPPED: byte at 0x%08X is 0x%02X, "
                 "expected 0x06\n", (DWORD)p, *p);
        return;
    }
    VirtualProtect(p, 1, PAGE_EXECUTE_READWRITE, &old_prot);
    *p = 0x64;
    VirtualProtect(p, 1, old_prot, &old_prot);
    coop_log("AI path walk limit increased to 100\n");
}

/* ------------------------------------------------------------------ */
/*  IPC packet handler (campaign receives from battle server)          */
/* ------------------------------------------------------------------ */

static void coop_on_ipc_event(void *peer, int connected) {
    ipc_slots_on_event(&g_ipc, peer, connected);
}

static void coop_on_ipc_packet(void *peer, const uint8_t *data, int len) {
    ipc_slots_on_packet(&g_ipc, peer, data, len);
}

/* ------------------------------------------------------------------ */
/*  Public API                                                         */
/* ------------------------------------------------------------------ */

void campaign_init_from_ini(const char *dll_dir) {
    /* Defense in depth: the loader only loads us into dedicated servers,
       but never patch engine memory in any other process. */
    {
        char exe_name[MAX_PATH];
        GetModuleFileNameA(NULL, exe_name, MAX_PATH);
        if (!coop_is_dedicated_exe(exe_name)) {
            OutputDebugStringA("[CoopWSE] non-dedicated process, plugin inert");
            return;
        }
    }

    coop_load_ini(dll_dir);

    /* Compute ASLR slide: runtime base vs preferred base */
    {
        HMODULE exe = GetModuleHandleA(NULL);
        g_aslr_slide = (DWORD)exe - WSE2_PREFERRED_BASE;
    }
    g_addrs = (g_coop_mode == COOP_HOST) ? &g_addrs_campaign : &g_addrs_battle;
    g_sites = (g_coop_mode == COOP_HOST) ? &g_sites_campaign : &g_sites_battle;

    g_log = fopen(g_coop_mode == COOP_HOST ? "warband_coop_host.log"
                                           : "warband_coop_battle.log", "w");
    coop_log("warband_coop loaded (mode=%s) aslr_slide=0x%08X\n",
             g_coop_mode == COOP_HOST ? "host" : "battle",
             g_aslr_slide);

    /* Runs after g_log is open (for visible [nettune] lines) and after
       g_aslr_slide is computed (nettune_apply rebases every site by it). */
    nettune_apply(g_coop_mode == COOP_BATTLE, g_ini_path);

    {
        modglobals_desc d;
        d.vec_first_addr = REBASE(g_addrs->global_vars_vec);
        d.vec_last_addr  = REBASE(g_addrs->global_vars_end);
        modglobals_init(&d);
    }
    resolve_battle_global_indices();

    /* Write server config dict (both campaign and battle personalities) */
    write_server_cfg_dict();

    install_hooks();

    if (g_coop_mode == COOP_HOST) {
        install_patches();
        start_ipc_thread();
    }

    /* IPC channel -- bnet_init calls enet_initialize/WSAStartup which is
       unsafe under DllMain loader lock. Both modes defer it to their
       background thread (ipc_thread_func / battle_poll_thread_func). */
    if (g_coop_mode == COOP_BATTLE) {
        g_battle_poll_running = 1;
        g_battle_poll_thread = CreateThread(NULL, 0, battle_poll_thread_func, NULL, 0, NULL);
        coop_log("battle mode: poll thread started (IPC deferred)\n");
    }

    coop_log("initialization complete\n");
}

void campaign_shutdown(void) {
    stop_ipc_thread();
    bnet_shutdown();

    if (g_fm_trampoline)
        hook_remove(REBASE(g_sites->frame_fn), g_fm_saved, g_sites->frame_prologue_size);

    if (g_coop_mode == COOP_BATTLE) {
        InterlockedExchange(&g_battle_poll_running, 0);
        if (g_battle_poll_thread) {
            WaitForSingleObject(g_battle_poll_thread, 3000);
            CloseHandle(g_battle_poll_thread);
            g_battle_poll_thread = NULL;
        }
        if (g_log) {
            coop_log("warband_coop unloaded (battle)\n");
            fclose(g_log);
            g_log = NULL;
        }
        return;
    }

    if (g_log) {
        coop_log("warband_coop unloaded\n");
        fclose(g_log);
        g_log = NULL;
    }
}

coop_mode_t campaign_get_mode(void) {
    return g_coop_mode;
}

