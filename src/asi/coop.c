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

#define MB_GAME_PLAYER_TROOP_NO    0x3A8    /* offset into mbGame */

/* ------------------------------------------------------------------ */
/*  rglString helpers (0x40 bytes, 48-byte SSO)                       */
/* ------------------------------------------------------------------ */

static void rglstring_init(char *rs, const char *value) {
    int len = (int)strlen(value);
    memset(rs, 0, 0x40);
    if (len > 47) len = 47;
    *(int *)(rs + 0x00)   = 0;
    *(char **)(rs + 0x04) = rs + 0x10;
    *(int *)(rs + 0x08)   = 48;
    *(int *)(rs + 0x0C)   = len;
    memcpy(rs + 0x10, value, len);
    rs[0x10 + len] = '\0';
}

static void write_string_register(int index, const char *value) {
    char *sr = (char *)(STRING_REG_BASE + index * STRING_REG_STRIDE);
    int len = (int)strlen(value);
    if (len > 47) len = 47;
    memcpy(sr + 0x10, value, len);
    sr[0x10 + len] = '\0';
    *(char **)(sr + 0x04) = sr + 0x10;
    *(int *)(sr + 0x08)   = 48;
    *(int *)(sr + 0x0C)   = len;
    *(int *)(sr + 0x00)   = 0;
}

/* ------------------------------------------------------------------ */
/*  Config                                                            */
/* ------------------------------------------------------------------ */

static char g_host_ip[64]       = "127.0.0.1";
static int  g_port              = 7240;
static int  g_battle_port       = 7241;
static char g_module_name[64]   = "NativeCoop";
static char g_module_label[64]  = "Calradia";  /* module_name from module.ini, used for server list filter */
static char g_game_dir[MAX_PATH] = "";          /* game directory (dirname of exe), set at DLL load */

/* Resolved at DLL load from variables.txt; index into g_basicGame.m_globalVariables int64 vector */
static int  g_encountered_party_idx = -1;
static int  g_asi_local_battle_idx  = -1;  /* $g_coop_asi_local_battle: set to 1 by module before local fight */

static void read_config(HINSTANCE hinstDLL) {
    char dll_path[MAX_PATH], ini_path[MAX_PATH];
    char *slash;
    GetModuleFileNameA(hinstDLL, dll_path, MAX_PATH);
    slash = strrchr(dll_path, '\\');
    if (slash) slash[1] = '\0'; else dll_path[0] = '\0';
    lstrcpynA(ini_path, dll_path, MAX_PATH);
    lstrcatA(ini_path, "coop.ini");
    GetPrivateProfileStringA("Coop", "HostIP",  "127.0.0.1",  g_host_ip,     sizeof(g_host_ip),    ini_path);
    GetPrivateProfileStringA("Coop", "Module",  "NativeCoop",  g_module_name,  sizeof(g_module_name),  ini_path);
    GetPrivateProfileStringA("Coop", "ModuleLabel", "Calradia", g_module_label, sizeof(g_module_label), ini_path);
    g_port        = GetPrivateProfileIntA("Coop", "Port",       7240, ini_path);
    g_battle_port = GetPrivateProfileIntA("Coop", "BattlePort", 7241, ini_path);
    coop_log("config: host=%s port=%d battle=%d module=%s label=%s\n",
             g_host_ip, g_port, g_battle_port, g_module_name, g_module_label);
}

/* Forward declarations for cross-referenced functions */
static void flush_result_string_to_file(void);

/* ------------------------------------------------------------------ */
/*  s59 writer thread (writes battle server IP to string register)    */
/* ------------------------------------------------------------------ */

static DWORD WINAPI s59_writer_thread(LPVOID param) {
    int written = 0;
    (void)param;
    while (1) {
        Sleep(500);
        flush_result_string_to_file();
        { /* Check s0 initialized */
            char *s0 = (char *)STRING_REG_BASE;
            if (*(char **)(s0 + 0x04) != s0 + 0x10) continue;
        }
        write_string_register(59, g_host_ip);
        if (!written) { coop_log("s59=%s\n", g_host_ip); written = 1; }
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Server injection: add our server to the browser's list            */
/*  Called from the browser's frameMove hook (main thread)            */
/* ------------------------------------------------------------------ */

typedef void (__fastcall *fn_thiscall_void)(void *ecx, void *edx);
typedef void (__fastcall *fn_thiscall_ptr)(void *ecx, void *edx, void *arg);

static int g_server_injected = 0;

static void inject_server(void *browser_window) {
    /* mbnetServer is 0x180 bytes */
    char server[0x180];
    fn_thiscall_void server_ctor = (fn_thiscall_void)ADDR_SERVER_CTOR;
    fn_thiscall_void server_dtor = (fn_thiscall_void)ADDR_SERVER_DTOR;
    fn_thiscall_ptr  vec_push    = (fn_thiscall_ptr)ADDR_VEC_PUSH_BACK;
    fn_thiscall_void fill_list   = (fn_thiscall_void)ADDR_FILL_SERVER_LIST;

    /* Construct default mbnetServer */
    server_ctor((void *)server, NULL);

    /* Fill fields */
    rglstring_init(server + 0x000, g_host_ip);         /* m_ip */
    *(int *)(server + 0x040) = 1;                      /* m_ping */
    *(int *)(server + 0x044) = g_port;                 /* m_port */
    *(int *)(server + 0x048) = -1;                     /* m_siteNo (-1 = campaign, no active mission) */
    *(int *)(server + 0x04C) = -1;                     /* m_missionTemplateNo (-1 = campaign) */
    rglstring_init(server + 0x050, "COOP Direct");     /* m_name */
    rglstring_init(server + 0x090, g_module_name);      /* m_moduleName - must match g_moduleName (dir name) */
    rglstring_init(server + 0x0D0, "");                /* m_siteName */
    rglstring_init(server + 0x110, "");                /* m_gameTypeName */
    *(int *)(server + 0x150) = 0;                      /* m_numPlayers */
    *(int *)(server + 0x154) = 10;                     /* m_maxNumPlayers */
    *(int *)(server + 0x158) = 0;                      /* m_passworded */
    *(int *)(server + 0x15C) = 1;                      /* m_dedicated */
    *(int *)(server + 0x160) = 1170;                   /* m_gameVersion */
    *(int *)(server + 0x164) = 0;                      /* m_moduleVersion */
    *(int *)(server + 0x17C) = 1145;                   /* m_extendedVersion (0x479) */

    /* Push to g_multiplayerData.m_serverList */
    vec_push((void *)ADDR_SERVER_LIST, NULL, (void *)server);

    /* Refresh table display */
    fill_list(browser_window, NULL);

    coop_log("server injected: %s:%d name='COOP Direct' module=%s\n",
             g_host_ip, g_port, g_module_label);

    /* Cleanup local (vector made a copy) */
    server_dtor((void *)server, NULL);

    g_server_injected = 1;
}

/* ------------------------------------------------------------------ */
/*  Server browser frameMove hook                                     */
/*  Injects our server on first frame, then passes through            */
/* ------------------------------------------------------------------ */

static BYTE  g_fm_saved[8];
static DWORD g_fm_trampoline = 0;

static int g_scan_was_active = 0;

static int g_result_ready_idx = -1;
static int g_result_win_loss_idx = -1;
static int g_result_xp_idx = -1;
static int g_result_cas_count_idx = -1;
static int g_result_cas_idx[10] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};
static void check_pending_local_result(void);
#define LOCAL_RESULT_FILENAME "coop_local_result.ini"

/* Read result data from module globals, write to .ini.
   The debrief writes: $g_coop_result_win_loss, $g_coop_result_xp,
   $g_coop_result_cas_count, and trp_temp_array_c slots 100+i / 120+i. */
static void flush_result_string_to_file(void) {
    char path[MAX_PATH];
    FILE *f;
    int win, xp, cas_count, i, tid, killed;

    if (g_result_ready_idx < 0) return;
    if (modglobals_get_int(g_result_ready_idx, 0) != 1) return;
    modglobals_set(g_result_ready_idx, 0);

    win = modglobals_get_int(g_result_win_loss_idx, 0);
    xp  = modglobals_get_int(g_result_xp_idx, 0);
    cas_count = modglobals_get_int(g_result_cas_count_idx, 0);
    if (cas_count > 10) cas_count = 10;

    coop_log("flush_result: win=%d xp=%d cas=%d (from globals)\n", win, xp, cas_count);

    _snprintf(path, sizeof(path), "%s\\%s", g_game_dir, LOCAL_RESULT_FILENAME);
    path[MAX_PATH-1] = 0;
    f = fopen(path, "w");
    if (!f) { coop_log("flush_result: cannot write %s\n", path); return; }

    fprintf(f, "[Result]\n");
    fprintf(f, "valid=1\n");
    fprintf(f, "win_loss=%d\n", win);
    fprintf(f, "xp_after=%d\n", xp);

    for (i = 0; i < cas_count; i++) {
        int packed = modglobals_get_int(g_result_cas_idx[i], 0);
        tid    = packed / 1000;
        killed = packed % 1000;
        fprintf(f, "cas_%d_troop=%d\n", i, tid);
        fprintf(f, "cas_%d_killed=%d\n", i, killed);
        coop_log("flush_result: cas[%d] packed=%d troop=%d killed=%d\n", i, packed, tid, killed);
    }
    fprintf(f, "cas_count=%d\n", cas_count);
    fclose(f);
    coop_log("flush_result: written to %s\n", path);
}

static void __cdecl browser_framemove_pre(void *this_ptr) {
    int searching;

    if (*(int *)ADDR_MAP_INTERACTION_MODE == 4) {
        flush_result_string_to_file();
        check_pending_local_result();
    }

    if (g_server_injected) return;
    if (*(int *)ADDR_MAP_INTERACTION_MODE != 4) return;

    searching = *(BYTE *)ADDR_SEARCHING_SERVERS;

    /* Track when LAN scan starts */
    if (searching) {
        g_scan_was_active = 1;
        return;
    }

    /* Inject after LAN scan finishes (list is stable) */
    if (!g_scan_was_active) return;

    {
        void *table = *(void **)((char *)this_ptr + 0x88);
        if (!table) return;
    }

    coop_log("LAN scan done, injecting server entry\n");
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
/*  mbMission::createAgent detour — player attach on gameType=4       */
/* ------------------------------------------------------------------ */

static DWORD g_ca_trampoline = 0;
static BYTE  g_ca_saved[16]   = {0};

/* Called from the naked detour with a pointer to the stack-argument area
   (address of param 2 on the stack, i.e. ESP+4 at the callee entry).
   Mutates playerNo in place when all match conditions hold. */
static void __cdecl create_agent_pre(DWORD *args) {
    int gameType = *(int *)ADDR_MAP_INTERACTION_MODE;
    if (gameType != 4) return;

    /* args[0] = transform, args[1] = entryPointNo, args[2] = troopNo, ...,
       args[13] = playerNo. Indices are (param# - 2) since `this` is in ECX. */
    int troopNo  = (int)args[2];
    int playerNo = (int)args[13];
    if (playerNo != -1) return;

    /* g_mbGame is a pointer at 0xA4F6A4; m_playerTroopNo at +0x3A8. */
    void *mbGame = *(void **)ADDR_CUR_GAME;
    if (!mbGame) return;
    int playerTroopNo = *(int *)((BYTE *)mbGame + MB_GAME_PLAYER_TROOP_NO);
    if (troopNo != playerTroopNo) return;

    int myPlayerNo = *(int *)ADDR_LOCAL_PLAYER_IDX;
    if (myPlayerNo < 0) return;  /* no MP player object -> do nothing */

    args[13] = (DWORD)myPlayerNo;
    coop_log("createAgent detour: playerNo -1 -> %d for troopNo=%d\n",
             myPlayerNo, troopNo);
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
/*  Option C — metaMission populate for coop local battle             */
/*  See patches/Warband/findings_encounters.md "Option C Impl RE"    */
/* ------------------------------------------------------------------ */

static DWORD g_sp_trampoline = 0;
static BYTE  g_sp_saved[16]  = {0};

/* Set by fixup_meta_mission_for_coop when a coop local battle starts.
   The mission_framemove_detour restores gameType on the first frame. */
static volatile int g_in_coop_local_battle = 0;

static void __cdecl fixup_meta_mission_for_coop(void) {
    volatile int *meta;
    int party_no;
    int flag;

    if (*(int *)ADDR_MAP_INTERACTION_MODE != 4) return;

    /* Only fire if the module explicitly set $g_coop_asi_local_battle = 1
       right before change_screen_mission in the encounter menu. */
    flag = modglobals_get_int(g_asi_local_battle_idx, 0);
    if (flag != 1) return;

    meta = (volatile int *)ADDR_META_MISSION;
    if (meta[0] != -1) return;  /* already populated */

    party_no = modglobals_get_int(g_encountered_party_idx, -1);
    if (party_no < 0) return;

    /* Clear the flag so this only fires once */
    modglobals_set(g_asi_local_battle_idx, 0);

    meta[0] = party_no;                                 /* +0x00 encounteredParties[0] */
    meta[1] = -1;                                       /* +0x04 encounteredParties[1] */
    *(int *)((BYTE *)meta + 0x0C) = 0;                  /* m_type (0 = field)          */
    *(int *)((BYTE *)meta + 0x18) = 0;                  /* m_mainPartySide             */
    *(int *)((BYTE *)meta + 0x24) = 1;                  /* m_enemySide (1=opposing team) */
    *(int *)((BYTE *)meta + 0x30) = 1;                  /* m_inEvent                   */
    *(int *)((BYTE *)meta + 0x44) = 1;                  /* m_enemiesPresent            */

    coop_log("metaMission fixup: encountered_party=%d written to 0x%X\n",
             party_no, ADDR_META_MISSION);

    /* Set the flag.  gameType is NOT changed here — it stays at 4 so
       network listen/send in mbCoreGame::frameMove keep working.
       gameType=0 is set in the setParams prologue detour (which runs
       inside the window dispatch, after network listen) and restored
       in the frameMove cleanup (before network send). */
    g_in_coop_local_battle = 1;
    coop_log("local battle flag set (gameType stays 4 until window dispatch)\n");
}

/* ------------------------------------------------------------------ */
/*  Drain the client's outbound event queue while gameType is still 4. */
/*                                                                     */
/*  multiplayer_send_int_to_server only enqueues into slot-0 m_events; */
/*  the per-frame pump (mbCoreGame::frameMove) only services the queue */
/*  while gameType is a client type (1/4). Forcing gameType=0 below    */
/*  silences that pump for the whole local battle, so any event the    */
/*  encounter menu queued (e.g. start_local_fight) would be stranded   */
/*  and never reach the campaign server. Transmit it now, before the   */
/*  flip, via the narrow client send (no inbound work, no gameType     */
/*  check). The per-player rate throttle is bypassed by zeroing        */
/*  m_packetSendTime so the queued event leaves on this call.          */
#define OFF_PLAYER_OBJECT      0x000      /* *(int*)(slot0+0): player object ptr */
#define OFF_PACKET_SEND_TIME   0x300      /* double m_packetSendTime */

static void coop_flush_client_events(void) {
    void *host  = *(void **)ADDR_ENET_HOST_PTR;
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
    g_in_coop_local_battle = 0;
    fixup_meta_mission_for_coop();
    if (g_in_coop_local_battle) {
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
/*  mission_frameMove — per-frame gameType flip for coop local battles */
/*  Sets gameType=0 during frameMove so all SP subsystems work, then  */
/*  restores to 4 on return so network listen/send (which run outside */
/*  frameMove in mbCoreGame::frameMove) see gameType=4.               */
/* ------------------------------------------------------------------ */

static DWORD g_mfm_trampoline = 0;
static BYTE  g_mfm_saved[16]  = {0};
static DWORD g_mfm_saved_retaddr = 0;

static void __cdecl mfm_pre(void) {
    if (*(int *)ADDR_MAP_INTERACTION_MODE == 4 && !g_in_coop_local_battle) {
        flush_result_string_to_file();
        check_pending_local_result();
    }
    if (g_in_coop_local_battle) {
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

        cmp dword ptr [g_in_coop_local_battle], 0
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

/* Pending local battle result -- saved to file by ASI, loaded on next launch.
   The result file lives at <game_dir>/coop_local_result.ini so the ASI can
   read/write it without WSE2 dict restrictions. */



/* Check for pending result file on launch, write values to module globals
   so the simple trigger can send them to the server. */
static int g_pending_result_idx = -1;
static int g_pending_win_loss_idx = -1;

/* Troop slot write — sets slot `slot_no` on troop `troop_idx` to `value`.
   Troop slots are stored as a heap-allocated int array at troop+0x148.
   troop_idx is the 0-based troop index. */
static void write_troop_slot(int troop_idx, int slot_no, int value) {
    DWORD troops_first = *(DWORD *)ADDR_TROOPS_VEC;
    int *slots;
    if (!troops_first) return;
    slots = *(int **)((BYTE *)troops_first + troop_idx * TROOP_SIZE + TROOP_SLOTS_OFF);
    if (!slots) return;
    slots[slot_no] = value;
}

static int g_pending_xp_idx = -1;
static int g_pending_cas_count_idx = -1;
static int g_pending_cas_tid_idx[10]    = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};
static int g_pending_cas_killed_idx[10] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};

static void check_pending_local_result(void) {
    char path[MAX_PATH], key[32];
    int valid, win_loss, xp, cas_count, i, tid, killed;

    if (g_pending_result_idx < 0 || g_pending_win_loss_idx < 0) return;
    if (modglobals_get_int(g_pending_result_idx, 0) != 0) return;

    _snprintf(path, sizeof(path), "%s\\%s", g_game_dir, LOCAL_RESULT_FILENAME);
    path[MAX_PATH-1] = 0;
    valid = GetPrivateProfileIntA("Result", "valid", 0, path);
    coop_log("check_pending: path=%s valid=%d\n", path, valid);
    if (!valid) return;

    win_loss  = GetPrivateProfileIntA("Result", "win_loss", 0, path);
    xp        = GetPrivateProfileIntA("Result", "xp_after", 0, path);
    cas_count = GetPrivateProfileIntA("Result", "cas_count", 0, path);
    if (cas_count > 10) cas_count = 10;

    modglobals_set(g_pending_result_idx, 1);
    modglobals_set(g_pending_win_loss_idx, win_loss);
    if (g_pending_xp_idx >= 0) modglobals_set(g_pending_xp_idx, xp);
    if (g_pending_cas_count_idx >= 0) modglobals_set(g_pending_cas_count_idx, cas_count);

    for (i = 0; i < cas_count; i++) {
        _snprintf(key, sizeof(key), "cas_%d_troop", i);
        tid = GetPrivateProfileIntA("Result", key, 0, path);
        _snprintf(key, sizeof(key), "cas_%d_killed", i);
        killed = GetPrivateProfileIntA("Result", key, 0, path);
        if (g_pending_cas_tid_idx[i] >= 0)
            modglobals_set(g_pending_cas_tid_idx[i], tid);
        if (g_pending_cas_killed_idx[i] >= 0)
            modglobals_set(g_pending_cas_killed_idx[i], killed);
        coop_log("check_pending: cas[%d] troop=%d killed=%d\n", i, tid, killed);
    }

    coop_log("check_pending: win=%d xp=%d cas=%d\n", win_loss, xp, cas_count);
    DeleteFileA(path);
}

static void __cdecl mission_end_restore_gametype(void) {
    if (!g_in_coop_local_battle) return;
    g_in_coop_local_battle = 0;
    *(int *)ADDR_MAP_INTERACTION_MODE = 4;
    coop_log("mission-end transition: gameType restored to 4\n");
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

/* ------------------------------------------------------------------ */
/*  DllMain                                                           */
/* ------------------------------------------------------------------ */

BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;
    if (fdwReason == DLL_PROCESS_ATTACH) {
        char exe_path[MAX_PATH];
        char *last_slash;
        DisableThreadLibraryCalls(hinstDLL);
        GetModuleFileNameA(NULL, exe_path, MAX_PATH);
        if (!strstr(exe_path, "mb_warband_wse2.exe")) return TRUE;

        /* Derive game dir (dirname of exe) for later use by variables.txt lookup */
        lstrcpynA(g_game_dir, exe_path, MAX_PATH);
        last_slash = strrchr(g_game_dir, '\\');
        if (last_slash) *last_slash = '\0';

        g_log = fopen("warband_coop.log", "w");
        coop_log("warband_coop.asi loaded\n");
        read_config(hinstDLL);

        /* Module global access: client vector addresses are raw literals
           (ASLR disabled via binary patch). Resolve all setParams-fixup +
           result-reporting IDs in one variables.txt pass. */
        {
            enum { N_FIXED = 10, N_ALL = N_FIXED + 30 };
            char vars_path[MAX_PATH];
            char cas_names[30][40];
            const char *names[N_ALL];
            int *dest[N_ALL];
            int idxs[N_ALL];
            int n = 0, ci;
            modglobals_desc d;

            g_addrs = &g_addrs_client;
            d.vec_first_addr = g_addrs->global_vars_vec;
            d.vec_last_addr  = g_addrs->global_vars_end;
            modglobals_init(&d);

            _snprintf(vars_path, sizeof(vars_path), "%s\\Modules\\%s\\variables.txt",
                      g_game_dir, g_module_name);
            vars_path[MAX_PATH-1] = 0;

            names[n] = "g_encountered_party";          dest[n] = &g_encountered_party_idx; n++;
            names[n] = "g_coop_asi_local_battle";      dest[n] = &g_asi_local_battle_idx;  n++;
            names[n] = "g_coop_pending_local_result";  dest[n] = &g_pending_result_idx;    n++;
            names[n] = "$g_coop_pending_win_loss";     dest[n] = &g_pending_win_loss_idx;  n++;
            names[n] = "$g_coop_pending_xp";           dest[n] = &g_pending_xp_idx;        n++;
            names[n] = "$g_coop_pending_cas_count";    dest[n] = &g_pending_cas_count_idx; n++;
            names[n] = "g_coop_result_ready";          dest[n] = &g_result_ready_idx;      n++;
            names[n] = "g_coop_result_win_loss";       dest[n] = &g_result_win_loss_idx;   n++;
            names[n] = "g_coop_result_xp";             dest[n] = &g_result_xp_idx;         n++;
            names[n] = "g_coop_result_cas_count";      dest[n] = &g_result_cas_count_idx;  n++;
            for (ci = 0; ci < 10; ci++) {
                _snprintf(cas_names[3*ci], sizeof(cas_names[0]),
                          "$g_coop_pending_cas_tid_%d", ci);
                names[n] = cas_names[3*ci];   dest[n] = &g_pending_cas_tid_idx[ci];    n++;
                _snprintf(cas_names[3*ci+1], sizeof(cas_names[0]),
                          "$g_coop_pending_cas_killed_%d", ci);
                names[n] = cas_names[3*ci+1]; dest[n] = &g_pending_cas_killed_idx[ci]; n++;
                _snprintf(cas_names[3*ci+2], sizeof(cas_names[0]),
                          "g_coop_result_cas_%d", ci);
                names[n] = cas_names[3*ci+2]; dest[n] = &g_result_cas_idx[ci];         n++;
            }

            modglobals_resolve(vars_path, names, idxs, n);
            for (ci = 0; ci < n; ci++) *dest[ci] = idxs[ci];
            coop_log("modglobals: resolved %d ids (encountered_party=%d result_ready=%d)\n",
                     n, g_encountered_party_idx, g_result_ready_idx);
        }

        /* Background thread for s59 */
        CreateThread(NULL, 0, s59_writer_thread, NULL, 0, NULL);

        /* Hook server browser's frameMove to inject server entry */
        hook_install(ADDR_BROWSER_FRAMEMOVE, browser_framemove_detour,
                     BROWSER_PROLOGUE_SIZE, g_fm_saved, &g_fm_trampoline);
        coop_log("browser frameMove hooked at 0x%X\n", ADDR_BROWSER_FRAMEMOVE);

        /* Patch addExperienceToTroop to allow negative XP (Fix H).
           Engine clamps xp_amount < 0 to 0 at 0x4B84A9 (8 bytes:
           test ebx,ebx / jns / xor ebx,ebx / jmp).  NOP the clamp so
           char_sync_xp can correct client XP downward.  The upper clamp
           (cap at 29999) at 0x4B84B1 is preserved. */
        {
            DWORD old_prot;
            BYTE *addr = (BYTE *)0x4B84A9;
            VirtualProtect(addr, 8, PAGE_EXECUTE_READWRITE, &old_prot);
            /* Verify original bytes before patching */
            if (addr[0] == 0x85 && addr[1] == 0xDB && addr[2] == 0x79) {
                memset(addr, 0x90, 8);
                coop_log("addExperienceToTroop negative-clamp patched (8 NOPs at 0x4B84A9)\n");
            } else {
                coop_log("addExperienceToTroop: unexpected bytes at 0x4B84A9 (0x%02X 0x%02X), skipping patch\n",
                         addr[0], addr[1]);
            }
            VirtualProtect(addr, 8, old_prot, &old_prot);
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
            DWORD old_prot;
            /* Gate 1: entry point initialization */
            BYTE *g1a = (BYTE *)0x4F713E;
            BYTE *g1b = (BYTE *)0x4F7147;
            VirtualProtect(g1a, 6 + (g1b - g1a) + 6, PAGE_EXECUTE_READWRITE, &old_prot);
            if (g1a[0] == 0x0F && g1a[1] == 0x84) {
                memset(g1a, 0x90, 6);
                coop_log("mbMission::start gate1a patched (6 NOPs at 0x4F713E)\n");
            } else {
                coop_log("mbMission::start gate1a: unexpected bytes 0x%02X 0x%02X, skipping\n", g1a[0], g1a[1]);
            }
            if (g1b[0] == 0x0F && g1b[1] == 0x84) {
                memset(g1b, 0x90, 6);
                coop_log("mbMission::start gate1b patched (6 NOPs at 0x4F7147)\n");
            } else {
                coop_log("mbMission::start gate1b: unexpected bytes 0x%02X 0x%02X, skipping\n", g1b[0], g1b[1]);
            }
            VirtualProtect(g1a, 6 + (g1b - g1a) + 6, old_prot, &old_prot);

            /* Gate 2: reinforceEntryGroup + spawnEntryGroups */
            BYTE *g2a = (BYTE *)0x4F8B7A;
            BYTE *g2b = (BYTE *)0x4F8B83;
            VirtualProtect(g2a, 6 + (g2b - g2a) + 6, PAGE_EXECUTE_READWRITE, &old_prot);
            if (g2a[0] == 0x0F && g2a[1] == 0x84) {
                memset(g2a, 0x90, 6);
                coop_log("mbMission::start gate2a patched (6 NOPs at 0x4F8B7A)\n");
            } else {
                coop_log("mbMission::start gate2a: unexpected bytes 0x%02X 0x%02X, skipping\n", g2a[0], g2a[1]);
            }
            if (g2b[0] == 0x0F && g2b[1] == 0x84) {
                memset(g2b, 0x90, 6);
                coop_log("mbMission::start gate2b patched (6 NOPs at 0x4F8B83)\n");
            } else {
                coop_log("mbMission::start gate2b: unexpected bytes 0x%02X 0x%02X, skipping\n", g2b[0], g2b[1]);
            }
            VirtualProtect(g2a, 6 + (g2b - g2a) + 6, old_prot, &old_prot);

            /* Gate 3: MP visitor troopNos wipe loop @ 0x4F57FE-0x4F581C.
               After setParams runs, mbMission::start has a loop gated on
               gameType != 0 that iterates all 128 visitors and clears
               m_troopNos (m_end = m_begin). This wipes the troops we
               pushed via add_visitors_to_current_scene before
               spawnEntryGroups can read them. Patch the je at 0x4F5805
               (74 16) to jmp (EB 16) to always skip the wipe loop. */
            BYTE *g3 = (BYTE *)0x4F5805;
            VirtualProtect(g3, 2, PAGE_EXECUTE_READWRITE, &old_prot);
            if (g3[0] == 0x74 && g3[1] == 0x16) {
                g3[0] = 0xEB;
                coop_log("mbMission::start gate3 patched (je->jmp at 0x4F5805)\n");
            } else {
                coop_log("mbMission::start gate3: unexpected bytes 0x%02X 0x%02X, skipping\n", g3[0], g3[1]);
            }
            VirtualProtect(g3, 2, old_prot, &old_prot);
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
                DWORD old_prot;
                VirtualProtect(ai_gates[i].addr, ai_gates[i].len, PAGE_EXECUTE_READWRITE, &old_prot);
                if (ai_gates[i].addr[0] == ai_gates[i].op0 && ai_gates[i].addr[1] == ai_gates[i].op1) {
                    memset(ai_gates[i].addr, 0x90, ai_gates[i].len);
                    coop_log("agent AI gate %d patched (%d NOPs at 0x%X): %s\n",
                             i, ai_gates[i].len, (DWORD)ai_gates[i].addr, ai_gates[i].name);
                } else {
                    coop_log("agent AI gate %d: unexpected bytes 0x%02X 0x%02X at 0x%X, skipping (%s)\n",
                             i, ai_gates[i].addr[0], ai_gates[i].addr[1],
                             (DWORD)ai_gates[i].addr, ai_gates[i].name);
                }
                VirtualProtect(ai_gates[i].addr, ai_gates[i].len, old_prot, &old_prot);
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

        /* mission_frameMove: per-frame gameType flip for local battles.
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
