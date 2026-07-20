#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>

#include "warband_addrs_wse2.h"
#include "hook.h"
#include "crash_report.h"
#include "coop_campaign.h"
#include "battle_net.h"
#include "battle_ipc.h"
#include "wsedict.h"
#include "modglobals.h"
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

/* ------------------------------------------------------------------ */
/*  Module global variable indices -- resolved from variables.txt      */
/* ------------------------------------------------------------------ */

static int g_gvar_round_ended = -1;
static int g_gvar_battle_started = -1;
static int g_gvar_battle_slot  = -1;                     /* battle server: own slot id */
static int g_gvar_slots_online = -1;                     /* campaign: online bitmask   */
static int g_gvar_battle_ended_slot[IPC_MAX_BATTLE_SLOTS] = {-1, -1, -1, -1};
static int g_gvar_in_progress_slot[IPC_MAX_BATTLE_SLOTS] = {-1, -1, -1, -1};
static int g_gvar_mp_winner = -1;
static int g_gvar_set_xp_go = -1;
static int g_gvar_set_xp_troop = -1;
static int g_gvar_set_xp_value = -1;

/* ------------------------------------------------------------------ */
/*  Battle slot state                                                  */
/* ------------------------------------------------------------------ */

static int   g_battle_slot = 0;                          /* COOP_BATTLE: pool slot from env */
static void *g_ipc_peer_slot[IPC_MAX_BATTLE_SLOTS];      /* COOP_HOST: ENet peer per slot   */

/* ------------------------------------------------------------------ */
/*  Hook state                                                        */
/* ------------------------------------------------------------------ */

static DWORD g_fm_trampoline = 0;
static BYTE  g_fm_saved[FRAMEMOVE_PROLOGUE_SIZE];

/* recalc_path_roster recursion guard */
static BYTE  g_rpr_saved[16];
static DWORD g_rpr_trampoline;
static int   g_rpr_depth = 0;

static DWORD g_mask_refresh_tick = 0;   /* IPC-thread mask republish cadence */

/* ------------------------------------------------------------------ */
/*  Forward declarations                                              */
/* ------------------------------------------------------------------ */

static void coop_on_frame(void);
static void coop_post_frame(void);
static void coop_on_ipc_packet(void *peer, const uint8_t *data, int len);
static void coop_on_ipc_event(void *peer, int connected);
static void update_slots_online_mask(void);

/* ------------------------------------------------------------------ */
/*  FrameMove detour                                                  */
/* ------------------------------------------------------------------ */

__declspec(naked) void framemove_detour(void) {
    __asm {
        /* === PRE-TICK: network polling === */
        sub  esp, 64
        movdqu [esp],      xmm0
        movdqu [esp + 16], xmm1
        movdqu [esp + 32], xmm2
        movdqu [esp + 48], xmm3
        pushad
        sub  esp, 112
        fsave [esp]
        call coop_on_frame
        frstor [esp]
        add  esp, 112
        popad
        movdqu xmm0, [esp]
        movdqu xmm1, [esp + 16]
        movdqu xmm2, [esp + 32]
        movdqu xmm3, [esp + 48]
        add  esp, 64

        /* === RUN ORIGINAL mbGame::frameMove via trampoline === */
        call dword ptr [g_fm_trampoline]

        /* === POST-TICK: process deferred commands (set_xp, etc) === */
        sub  esp, 64
        movdqu [esp],      xmm0
        movdqu [esp + 16], xmm1
        movdqu [esp + 32], xmm2
        movdqu [esp + 48], xmm3
        pushad
        sub  esp, 112
        fsave [esp]
        call coop_post_frame
        frstor [esp]
        add  esp, 112
        popad
        movdqu xmm0, [esp]
        movdqu xmm1, [esp + 16]
        movdqu xmm2, [esp + 32]
        movdqu xmm3, [esp + 48]
        add  esp, 64
        ret
    }
}

/* ------------------------------------------------------------------ */
/*  coop_on_frame                                                     */
/* ------------------------------------------------------------------ */

/* ASLR slide — computed once, used by REBASE() macro in warband_addrs_wse2.h */
DWORD g_aslr_slide = 0;

/* --- IPC thread: hosts the battle-server ENet listener and republishes
   the slots-online mask. The framemove hook also polls IPC, but this
   thread guarantees liveness even when frames stall (loading screens). --- */
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
            update_slots_online_mask();
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
    bnet_poll();
    crash_heartbeat();
}

/* ------------------------------------------------------------------ */
/*  coop_post_frame — runs AFTER mbGame::frameMove (scripts done)      */
/*  Processes deferred commands that scripts signalled via globals.     */
/* ------------------------------------------------------------------ */

static void coop_post_frame(void) {
    /* --- troop_set_xp: authoritative XP write (Fix H) ---
       Module script sets $g_coop_set_xp_go = 1 to request a direct
       write to mbTroop.m_experience.  We run after frameMove so the
       script's global-variable writes are already visible, and any
       subsequent troop_get_xp in the *next* frame sees the correct
       value.  coop_save_character also runs in the same frame as the
       script that sets the flag — but we moved the XP set here
       (post-tick), so the save still reads the old XP.

       To handle this, the module script defers its save to the next
       frame via a "set_xp_pending" gate: it sets the flag, skips the
       save, and lets the next frame's pre-tick pick up the save.

       Actually — simpler: the script already logs the dict_xp for
       diagnostics.  We process the command here (post-frame), and the
       only reader of troop XP after this point is coop_save_character,
       which runs during the SAME frameMove call (earlier in this frame,
       before the script set the flag).  The NEXT frame will see the
       corrected XP.  The save that matters is the Phase 2 save or the
       autosave, both of which run in future frames.

       Wait — coop_load_character AND coop_save_character both run in
       the same player_joined handler, within the same frameMove call.
       The save at :51931 reads troop_get_xp AFTER the script sets the
       flag but BEFORE we get to coop_post_frame.  So the save still
       captures the wrong XP.

       Fix: skip the save in the script when set_xp was used, and have
       coop_post_frame trigger the save after writing XP.  But the DLL
       can't call module scripts.

       Alternative fix: don't defer — instead, have the DLL write XP
       BEFORE frameMove, by reading the flag in coop_on_frame.  But the
       flag hasn't been set yet (it's set during frameMove).

       REAL fix: use a TWO-FRAME protocol.
       Frame N: script sets go=1.  Script marks "xp_deferred" so it
       skips the immediate save.
       Frame N+1: DLL coop_on_frame sees go=1, writes XP, clears go.
       Script's next trigger/joined continues and saves with correct XP.
       But player_joined is a one-shot — it doesn't span two frames.

       SIMPLEST FIX: write XP inline from the module script using a
       big positive add_xp_to_troop to reach the target.  If current >
       target, we're stuck.  For current < target, add the delta.  For
       current > target, we need the DLL.

       Let's do this: post_frame writes XP.  The save in player_joined
       captures the STALE xp, but that save's only purpose is to persist
       Phase 2 XP.  When set_xp is active, Phase 2 hasn't run yet (the
       set_xp is for the base load, not Phase 2).  So the Phase 2 save
       path is separate and correct.

       Actually, re-reading the code: coop_save_character at :51931
       only runs when phase2_applied==1.  And when set_xp_go is set,
       it's from coop_load_character (base XP).  Phase 2 adds positive
       XP on top.  The save at :51931 captures troop_get_xp which is
       (stale_base + phase2_delta).  The stale_base is wrong, but after
       post_frame writes the correct base, the NEXT save (autosave or
       exit) will capture the right total.

       This is acceptable for now — the Phase 2 save will be slightly
       off by the base delta, but the next autosave (300s) corrects it.

       TODO: if this drift is unacceptable, restructure player_joined
       to split across two frames.
    */
    if (g_coop_mode != COOP_HOST) return;
    if (g_gvar_set_xp_go < 0) return;

    __try {
        int go = modglobals_get_int(g_gvar_set_xp_go, 0);
        if (go == 1) {
            int troop_id = modglobals_get_int(g_gvar_set_xp_troop, 0);
            int xp_value = modglobals_get_int(g_gvar_set_xp_value, 0);
            void *game = wb_cur_game();
            if (game) {
                /* Troop array: game + CAMP_OFF_TROOP_ARRAY -> troop_array_ptr.
                   Each troop struct is TROOP_STRIDE bytes.
                   m_experience at +0x164, m_level at +0x178 (same as client). */
                char *troop_arr = *(char **)((char *)game + CAMP_OFF_TROOP_ARRAY);
                if (troop_arr) {
                    char *troop = troop_arr + (unsigned)troop_id * CAMP_TROOP_STRIDE;
                    int old_xp = *(int *)(troop + 0x164);
                    *(int *)(troop + 0x164) = xp_value;

                    /* Recompute m_level from XP.
                       g_levelTable thresholds — hardcoded from RE of
                       addExperienceToTroop (engine values, fLevelBoundaryMultiplier=1.0). */
                    {
                        static const int xp_table[] = {
                            0, 0, 600, 1360, 2296, 3426, 4768, 6345,
                            8179, 10297, 13010, 16161, 19806, 24007, 28832, 34362,
                            40682, 47892, 56103, 65441, 77233, 90809, 106425, 124371,
                            144981, 168636, 195769, 226879, 262533, 303381, 350164, 412091,
                            484440, 568947, 667638, 782877, 917424, 1074494, 1257843, 1471851,
                            1721626, 2070551, 2489361, 2992033, 3595340, 4319408, 5188389, 6231267
                        };
                        int level = 0;
                        int max_lvl = (sizeof(xp_table)/sizeof(xp_table[0])) - 1;
                        while (level < max_lvl && xp_value >= xp_table[level + 1])
                            level++;
                        *(int *)(troop + 0x178) = level;
                    }
                    coop_log("[set_xp] troop=%d old_xp=%d new_xp=%d level=%d\n",
                             troop_id, old_xp, xp_value,
                             *(int *)(troop + 0x178));
                }
            }
            modglobals_set(g_gvar_set_xp_go, 0);
        }
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        /* Access violation during global/troop read — vector may be reallocating */
    }
}

/* ------------------------------------------------------------------ */
/*  INI parsing                                                       */
/* ------------------------------------------------------------------ */

static void coop_load_ini(const char *dll_dir) {
    char ini_path[MAX_PATH];

    lstrcpynA(ini_path, dll_dir, MAX_PATH);
    lstrcatA(ini_path, "coop.ini");

    /* Mode comes from the exe name alone; the winmm loader only loads this
       plugin into dedicated servers (coop_loader.c). */
    {
        char exe_name[MAX_PATH];
        GetModuleFileNameA(NULL, exe_name, MAX_PATH);
        if (strstr(exe_name, "dedicated_campaign"))
            g_coop_mode = COOP_HOST;
        else
            g_coop_mode = COOP_BATTLE;
    }

    g_port = GetPrivateProfileIntA("Coop", "Port", 7240, ini_path);
    GetPrivateProfileStringA("Coop", "HostIP", "127.0.0.1", g_host_ip, sizeof(g_host_ip), ini_path);
    GetPrivateProfileStringA("Coop", "Module", "NativeCoop", g_module_name, sizeof(g_module_name), ini_path);

    if (g_coop_mode == COOP_BATTLE) {
        char slot_str[8];
        if (GetEnvironmentVariableA("COOP_BATTLE_SLOT", slot_str, sizeof(slot_str)) > 0)
            g_battle_slot = atoi(slot_str);
        if (g_battle_slot < 0 || g_battle_slot >= IPC_MAX_BATTLE_SLOTS)
            g_battle_slot = 0;
        coop_log("battle slot: %d (COOP_BATTLE_SLOT env)\n", g_battle_slot);
    }

    coop_log("config: mode=%s port=%d host=%s module=%s\n",
             g_coop_mode == COOP_HOST ? "host" : "battle",
             g_port, g_host_ip, g_module_name);
}

/* ------------------------------------------------------------------ */
/*  recalc_path_roster recursion guard                                 */
/* ------------------------------------------------------------------ */

__declspec(naked) void recalc_path_roster_detour(void) {
    __asm {
        inc  dword ptr [g_rpr_depth]
        cmp  dword ptr [g_rpr_depth], MAX_ROSTER_RECURSION_DEPTH
        jg   bail_out

        push dword ptr [esp + 8]
        push dword ptr [esp + 8]
        call dword ptr [g_rpr_trampoline]
        dec  dword ptr [g_rpr_depth]
        ret  8

    bail_out:
        dec  dword ptr [g_rpr_depth]
        xor  eax, eax
        ret  8
    }
}

/* ------------------------------------------------------------------ */
/*  Global variable resolver (from variables.txt)                      */
/* ------------------------------------------------------------------ */

static void resolve_battle_global_indices(void) {
    enum { N_FIXED = 8, N_ALL = N_FIXED + 2 * IPC_MAX_BATTLE_SLOTS };
    char path[MAX_PATH];
    char slot_names[2 * IPC_MAX_BATTLE_SLOTS][40];
    const char *names[N_ALL];
    int *dest[N_ALL];
    int idx[N_ALL];
    int n = 0, i;

    GetModuleFileNameA(NULL, path, MAX_PATH);
    { char *s = strrchr(path, '\\'); if (s) s[1] = '\0'; }
    lstrcatA(path, "Modules\\");
    lstrcatA(path, g_module_name);
    lstrcatA(path, "\\variables.txt");

    names[n] = "g_round_ended";              dest[n] = &g_gvar_round_ended;    n++;
    names[n] = "coop_battle_started";        dest[n] = &g_gvar_battle_started; n++;
    names[n] = "coop_battle_slot";           dest[n] = &g_gvar_battle_slot;    n++;
    names[n] = "g_coop_battle_slots_online"; dest[n] = &g_gvar_slots_online;   n++;
    names[n] = "coop_winner_team";           dest[n] = &g_gvar_mp_winner;      n++;
    names[n] = "g_coop_set_xp_go";           dest[n] = &g_gvar_set_xp_go;      n++;
    names[n] = "g_coop_set_xp_troop";        dest[n] = &g_gvar_set_xp_troop;   n++;
    names[n] = "g_coop_set_xp_value";        dest[n] = &g_gvar_set_xp_value;   n++;
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++) {
        _snprintf(slot_names[2*i], sizeof(slot_names[0]),
                  "g_coop_battle_ended_%d", i);
        names[n] = slot_names[2*i];   dest[n] = &g_gvar_battle_ended_slot[i]; n++;
        _snprintf(slot_names[2*i+1], sizeof(slot_names[0]),
                  "g_coop_battle_in_progress_%d", i);
        names[n] = slot_names[2*i+1]; dest[n] = &g_gvar_in_progress_slot[i];  n++;
    }

    modglobals_resolve(path, names, idx, n);
    for (i = 0; i < n; i++) *dest[i] = idx[i];

    coop_log("battle globals: round_ended=%d battle_started=%d mp_winner=%d battle_slot=%d slots_online=%d\n",
             g_gvar_round_ended, g_gvar_battle_started, g_gvar_mp_winner,
             g_gvar_battle_slot, g_gvar_slots_online);
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++)
        coop_log("slot %d: battle_ended=%d in_progress=%d\n",
                 i, g_gvar_battle_ended_slot[i], g_gvar_in_progress_slot[i]);
    coop_log("set_xp globals: go=%d troop=%d value=%d\n",
             g_gvar_set_xp_go, g_gvar_set_xp_troop, g_gvar_set_xp_value);
}

/* ------------------------------------------------------------------ */
/*  WSE dict directory helper                                          */
/* ------------------------------------------------------------------ */

static void get_wse_dict_dir(char *out, int out_size) {
    GetModuleFileNameA(NULL, out, out_size);
    { char *s = strrchr(out, '\\'); if (s) s[1] = '\0'; }
    lstrcatA(out, "WSE\\");
    lstrcatA(out, g_module_name);
    lstrcatA(out, "\\");
}

/* ------------------------------------------------------------------ */
/*  Battle data collection + dict writing + IPC signal (COOP_BATTLE)   */
/* ------------------------------------------------------------------ */

static void battle_collect_and_save(void) {
    int winner;
    int player_count = 0;

    winner = modglobals_get_int(g_gvar_mp_winner, 0);

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
        uint8_t buf[1 + sizeof(battle_end_signal_t)];
        battle_end_signal_t sig;
        int n;
        memset(&sig, 0, sizeof(sig));
        sig.slot = (uint8_t)g_battle_slot;
        sig.winner = (uint8_t)winner;
        sig.player_count = player_count;
        n = pkt_write(buf, PKT_BATTLE_END, &sig, sizeof(sig));
        bnet_send(buf, n);
        coop_log("[battle] sent PKT_BATTLE_END: winner=%d players=%d\n",
                 winner, player_count);
    }
}

/* ------------------------------------------------------------------ */
/*  Battle polling thread (COOP_BATTLE mode only)                      */
/* ------------------------------------------------------------------ */

static HANDLE g_battle_poll_thread = NULL;
static volatile LONG g_battle_poll_running = 0;
static int g_battle_save_done = 0;
static __int64 g_prev_battle_started = 0;

/* Engine function: mbBasicGame::getGlobalVariable(int index) -> __int64
   __thiscall: this in ECX. Use __fastcall(this, edx_unused, index) in C. */
typedef __int64 (__fastcall *getGlobalVar_fn)(void *, void *, int);

static void battle_on_ipc_event(void *peer, int connected) {
    (void)peer;
    if (connected) {
        uint8_t buf[1 + sizeof(battle_hello_t)];
        battle_hello_t hello;
        int n;
        hello.slot = (uint8_t)g_battle_slot;
        n = pkt_write(buf, PKT_BATTLE_HELLO, &hello, sizeof(hello));
        bnet_send(buf, n);
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
            modglobals_set(g_gvar_battle_slot, g_battle_slot);
            modglobals_get(g_gvar_battle_started, &battle_started);
        } __except(EXCEPTION_EXECUTE_HANDLER) {
            Sleep(100);
            continue;
        }

        if (battle_started == 1 && g_prev_battle_started != 1) {
            g_battle_save_done = 0;
            coop_log("[battle] battle_started -> 1\n");
        }

        /* Edge detect: battle_started -> -1 means coop_copy_parties_to_file_mp
           has finished dict_save of @coop_battle. The dict is on disk, so we can
           now collect DLL-side data (per-player char XP) and send PKT_BATTLE_END
           without a race against the module save. */
        if (battle_started == -1 && g_prev_battle_started != -1 && !g_battle_save_done) {
            coop_log("[battle] battle_started -> -1 (module save complete), collecting data...\n");
            battle_collect_and_save();
            g_battle_save_done = 1;
        }

        g_prev_battle_started = battle_started;

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
    /* ISOLATION TEST: hook mbGame::frameMove (campaign_tick) for per-frame polling.
       CD3DApp::FrameMove is WSE2-hooked at runtime — can't use it. */
    hook_install(REBASE(ADDR_CAMPAIGN_TICK), framemove_detour,
                 CAMPAIGN_TICK_PROLOGUE_SIZE, g_fm_saved, &g_fm_trampoline);
    coop_log("framemove hook installed (via campaign_tick 0x%X)\n", REBASE(ADDR_CAMPAIGN_TICK));

    hook_install(REBASE(ADDR_RECALC_PATH_ROSTER), recalc_path_roster_detour,
                 RECALC_PATH_ROSTER_PROLOGUE_SIZE, g_rpr_saved, &g_rpr_trampoline);
    coop_log("recalc_path_roster recursion guard installed (max depth %d)\n",
             MAX_ROSTER_RECURSION_DEPTH);
}

/* ------------------------------------------------------------------ */
/*  Binary patches (encounter skip, edge scroll, AI walk limit,        */
/*  widget null-bypass, destructor guard, duplicate name NOP)          */
/* ------------------------------------------------------------------ */

static void install_patches(void) {
    /* Increase AI path pre-walk limit (WSE2 default is 6, bump to 100) */
    {
        DWORD old_prot;
        BYTE *p = (BYTE *)REBASE(ADDR_AI_PATH_WALK_LIMIT);
        VirtualProtect(p, 1, PAGE_EXECUTE_READWRITE, &old_prot);
        *p = 0x64;
        VirtualProtect(p, 1, old_prot, &old_prot);
        coop_log("AI path walk limit increased to 100\n");
    }

    /* MP screen widget null-bypass — DISABLED for WSE2 (addresses unverified,
       not needed with dedicated battle server architecture) */

    /* Slot-array destructor guard — DISABLED for WSE2 (vanilla address,
       not needed with dedicated battle server architecture) */

    /* Duplicate name check, browse thread cleanup — DISABLED for WSE2
       (vanilla addresses, not needed with dedicated battle server) */

    /* Serial validation, name check, browse cleanup — ALL DISABLED for WSE2.
       These patches use vanilla addresses not yet mapped to WSE2, and are
       not needed with the dedicated battle server architecture. */
}

/* ------------------------------------------------------------------ */
/*  IPC packet handler (campaign receives from battle server)          */
/* ------------------------------------------------------------------ */

static void update_slots_online_mask(void) {
    int i, mask = 0;
    static int s_last_logged_mask = -1;
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++)
        if (g_ipc_peer_slot[i]) mask |= (1 << i);
    modglobals_set(g_gvar_slots_online, mask);
    /* Called ~1/s from the net thread as a republish -- log changes only */
    if (mask != s_last_logged_mask) {
        coop_log("[ipc] slots online mask = 0x%X\n", mask);
        s_last_logged_mask = mask;
    }
}

static void coop_on_ipc_event(void *peer, int connected) {
    int i;
    if (connected) return;   /* slot is learned from HELLO, not CONNECT */
    for (i = 0; i < IPC_MAX_BATTLE_SLOTS; i++) {
        if (g_ipc_peer_slot[i] == peer) {
            g_ipc_peer_slot[i] = NULL;
            coop_log("[ipc] battle slot %d disconnected\n", i);
            if (modglobals_get_int(g_gvar_in_progress_slot[i], 0) == 1) {
                modglobals_set(g_gvar_battle_ended_slot[i], 1);
                coop_log("[ipc] slot %d was in progress -> flagged ended (abort)\n", i);
            }
        }
    }
    update_slots_online_mask();
}

static void coop_on_ipc_packet(void *peer, const uint8_t *data, int len) {
    if (len < 1) return;
    switch (data[0]) {
    case PKT_BATTLE_HELLO: {
        battle_hello_t hello;
        if (pkt_read(data, len, &hello, sizeof(hello)) &&
            hello.slot < IPC_MAX_BATTLE_SLOTS) {
            g_ipc_peer_slot[hello.slot] = peer;
            coop_log("[ipc] HELLO: battle slot %d online\n", hello.slot);
            update_slots_online_mask();
        } else {
            coop_log("[ipc] bad HELLO (len=%d)\n", len);
        }
        break;
    }
    case PKT_BATTLE_END: {
        battle_end_signal_t sig;
        if (pkt_read(data, len, &sig, sizeof(sig)) &&
            sig.slot < IPC_MAX_BATTLE_SLOTS) {
            coop_log("[ipc] PKT_BATTLE_END: slot=%d winner=%d atk_cas=%d def_cas=%d players=%d\n",
                     sig.slot, sig.winner, sig.attacker_casualties,
                     sig.defender_casualties, sig.player_count);
            modglobals_set(g_gvar_battle_ended_slot[sig.slot], 1);
            coop_log("[ipc] set $g_coop_battle_ended_%d = 1\n", sig.slot);
        } else {
            coop_log("[ipc] PKT_BATTLE_END bad/short (%d bytes)\n", len);
        }
        break;
    }
    default:
        coop_log("[ipc] unknown packet type=0x%02X len=%d\n", data[0], len);
        break;
    }
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
        if (!strstr(exe_name, "dedicated")) {
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

    g_log = fopen(g_coop_mode == COOP_HOST ? "warband_coop_host.log"
                                           : "warband_coop_battle.log", "w");
    coop_log("warband_coop loaded (mode=%s) aslr_slide=0x%08X\n",
             g_coop_mode == COOP_HOST ? "host" : "battle",
             g_aslr_slide);

    {
        modglobals_desc d;
        d.vec_first_addr = REBASE(g_addrs->global_vars_vec);
        d.vec_last_addr  = REBASE(g_addrs->global_vars_end);
        modglobals_init(&d);
    }
    resolve_battle_global_indices();

    /* Battle server binary has different function addresses from client/campaign.
       Hooks use client addresses via REBASE() -- installing them on the battle
       server would patch random code and crash. Skip all hooks for COOP_BATTLE;
       battle end detection uses a polling thread instead (no engine hook needed). */
    if (g_coop_mode != COOP_BATTLE)
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

    /* framemove_detour is installed at ADDR_CAMPAIGN_TICK (see install_hooks) */
    hook_remove(REBASE(ADDR_CAMPAIGN_TICK), g_fm_saved, CAMPAIGN_TICK_PROLOGUE_SIZE);
    hook_remove(REBASE(ADDR_RECALC_PATH_ROSTER), g_rpr_saved, RECALC_PATH_ROSTER_PROLOGUE_SIZE);
    if (g_log) {
        coop_log("warband_coop unloaded\n");
        fclose(g_log);
        g_log = NULL;
    }
}

coop_mode_t campaign_get_mode(void) {
    return g_coop_mode;
}

