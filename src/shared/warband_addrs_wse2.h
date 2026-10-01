#pragma once
#include <windows.h>

/*
 * WSE2 Address Map -- the single engine address table (client + dedicated).
 *
 * All addresses from WSE2 PDB symbols (mb_warband_wse2.pdb, full symbols).
 * Struct offsets from Ghidra type database with PDB loaded.
 *
 * Key architectural differences from vanilla:
 *   - rglVector: 12 bytes (no self_ptr), VEC_OFF_START=0, VEC_OFF_END=4
 *   - Hash vector items: flat mbParty** array, not chunked deque
 *   - rglString: 64 bytes (48-byte SSO) vs vanilla 144 bytes (128-byte buf)
 *   - Battle fields split: encounter in mbGame, battle in mbMetaMission
 *   - Session params: mbnetData fields, not flat BSS globals
 *   - mbnetNetworkManager: unified object, not split host+data regions
 *   - NETMGR_OFF_ANTICHEAT removed (WSE2 has no Steam VAC field)
 *   - Several int fields changed to bool (1 byte): paused, cameraFollow
 *   - Party size: 0x5718 vs 0x5D28; stack size: 0x1C vs 0x20
 */

/* =================================================================== */
/*  ASLR support                                                        */
/* =================================================================== */

/* WSE2 has ASLR enabled (DllCharacteristics & IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE).
   All ADDR_* defines use the preferred image base 0x400000.
   At runtime, compute the slide and use REBASE() on every address.           */

#define WSE2_PREFERRED_BASE  0x00400000

extern DWORD g_aslr_slide;  /* set once in campaign_init_from_ini */

/* Rebase a static VA to its runtime address */
#define REBASE(va)  ((DWORD)(va) + g_aslr_slide)

/* =================================================================== */
/*  Per-personality address table                                       */
/* =================================================================== */

/* Addresses that differ per binary personality (client, campaign
   dedicated, battle dedicated) are selected ONCE at startup by pinning
   g_addrs to one of the three const tables (warband_addrs_wse2.c);
   consumers read g_addrs->cur_game etc. -- no per-call-site mode tests.
   Values are preferred-base VAs; wrap in REBASE() at use.

   A future WSE2 engine port edits one table per binary.

   Naked-asm detours that branch on [g_coop_mode] (campaign_tick_detour,
   update_ai_detour) keep reading the mode global directly -- asm can't
   chase struct pointers cheaply, and those branches select behavior,
   not addresses. */

typedef struct addr_table {
    DWORD cur_game;         /* mbGame** slot (PDB: g_game) */
    DWORD cur_mission;      /* mbMission** slot (PDB: g_mission) */
    DWORD global_vars_vec;  /* g_basicGame.m_globalVariables._Myfirst slot */
    DWORD global_vars_end;  /* m_globalVariables._Mylast slot */
} addr_table;

extern const addr_table g_addrs_client;    /* mb_warband_wse2.exe */
extern const addr_table g_addrs_campaign;  /* mb_warband_wse2_dedicated_campaign.exe */
extern const addr_table g_addrs_battle;    /* mb_warband_wse2_dedicated.exe */
extern const addr_table *g_addrs;          /* pinned once at init */

/* =================================================================== */
/*  Global pointers                                                     */
/* =================================================================== */

#define ADDR_CUR_GAME        0xA4F6A4  /* mbGame** -> mbGame*   (PDB: g_game) */
#define ADDR_CUR_MISSION     0xA4F6A8  /* mbMission** -> mbMission* (PDB: g_mission) */

/* Dedicated server equivalents. The two dedicated exes have DISTINCT
   .data layouts -- verified per binary from each PDB with code-load
   cross-checks (patches/WarbandDedicated/findings.md, B6 section). */
#define CAMP_ADDR_CUR_GAME    0x8CC4AC  /* mbGame** (PDB: g_game), dedicated_campaign */
#define CAMP_ADDR_CUR_MISSION 0x8CC4B0  /* mbMission** (PDB: g_mission) */
#define DED_ADDR_CUR_GAME     0x901514  /* mbGame** (PDB: g_game), battle dedicated */
#define DED_ADDR_CUR_MISSION  0x901518  /* mbMission** (PDB: g_mission) */

/* Campaign-exe hook/patch sites -- these are PREFERRED-BASE VAs and must be
   passed through REBASE(): the dedicated exes load ASLR-slid. PDB-derived,
   patches/WarbandDedicated findings "B2 fix addresses". The old client-exe
   ADDR_CAMPAIGN_TICK / ADDR_AI_PATH_WALK_LIMIT below are a DIFFERENT binary
   and must never be used to hook/patch the campaign exe. */
#define CAMP_ADDR_CAMPAIGN_TICK           0x466EB0  /* mbGame::frameMove -- __thiscall(game*, float delta) */
#define CAMP_CAMPAIGN_TICK_PROLOGUE_SIZE  6         /* push ebp; mov ebp,esp; sub esp,0x24 */
#define CAMP_CAMPAIGN_TICK_PROLOGUE_BYTES { 0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x24 }
#define CAMP_ADDR_AI_PATH_WALK_LIMIT      0x4ABE57  /* operand byte of cmp eax,6 @0x4ABE55 in mbParty::aiUpdateBehavior 0x4ABAB0 */

/* =================================================================== */
/*  Function addresses                                                  */
/* =================================================================== */

/* Campaign / frame */
#define ADDR_CAMPAIGN_TICK   0x4B2190  /* mbGame::frameMove -- __thiscall(game*, float delta) */
#define ADDR_FRAMEMOVE       0x483340  /* CD3DApplication::FrameMove -- __thiscall(CD3DApp*, float) */

/* Party AI */
#define ADDR_UPDATE_AI_BEHAV         0x56E270  /* mbParty::aiUpdateBehavior -- __thiscall(party*) */
#define ADDR_UPDATE_DEST_FOR_BEHAV   0x56EB80  /* mbParty::aiUpdateMovement -- __thiscall(party*) */

/* Screen / UI */
#define ADDR_PUSH_SCREEN     0x4C7CE0  /* mbGameScreen::openWindow -- __thiscall(g_gameScreen, int window_id) */
#define ADDR_SET_WINDOW      0x4C7C50  /* mbGameScreen::setWindow(int) -- pops the open-window stack (close()
                                          each), then openWindow. __thiscall in the PDB but never reads ECX
                                          (indexes g_gameScreen.m_windows directly) -- callable as stdcall(int).
                                          PDB-verified (findings "Auto-join on invite landing RE"). */
#define ADDR_LOADING_WINDOW_PTR  0xABB95C  /* g_gameScreen.m_windows[3] -- mbLoadingWindow* */
#define ADDR_OPEN_WINDOWS_BEGIN  0xABB9E8  /* g_gameScreen.m_openWindows rglVector<int> begin */
#define ADDR_OPEN_WINDOWS_END    0xABB9EC  /* g_gameScreen.m_openWindows rglVector<int> end; active window
                                              index = *(int*)(end - 4) */
#define LOADING_WINDOW_MODE_OFF   0x04   /* mbLoadingWindow m_mode: 6 = MP route without the
                                            m_switchingModule requirement (mbStartingWindow recipe) */
#define LOADING_WINDOW_SOURCE_OFF 0x14   /* m_sourceWindowNo (back target; 4 = mbInitialWindow) */
#define LOADING_WINDOW_STEP_OFF   0x6C   /* mbLoadingWindow::m_step -- reset to 0 before setWindow(3).
                                            (m_stage is 0x68; 0x148 is m_savegameNo -- the pre-audit
                                            value zeroed the savegame slot, PDB audit B8) */

/* String operations */
#define ADDR_RGL_STRING_COPY 0x679DC0  /* rglString::operator=(char const*) -- __thiscall(rglString*, char*) */

/* Battle system */
#define ADDR_INITIATE_BATTLE     0x4B92F0  /* mbGame::startBattle -- __thiscall(game*, int partyA, int partyB) */
#define ADDR_ENCOUNTER_ACTION    0x4EFCC0  /* mbMetaMission::parseEncounterFlags -- __thiscall(metaMission*) */
#define ADDR_CLEANUP_BATTLE      0x4F00C0  /* mbMetaMission::endEncounter -- __thiscall(metaMission*) */

/* Network */
#define ADDR_SERVER_CREATE           0x54BBC0  /* mbnetNetworkManager::startServer -- __thiscall(netmgr*) */
#define ADDR_CLIENT_CONNECT_DIRECT   0x54BA70  /* mbnetNetworkManager::connectToServer -- __thiscall(netmgr*) */
#define ADDR_RESOLVE_HOSTNAME        0x520720  /* mbnetAddress::mbnetAddress -- constructor does resolution */
#define ADDR_WSA_INIT                0x54B900  /* mbnetNetworkManager::startWinsockIfNeeded */
#define ADDR_RESET_SESSION           0x54B2E0  /* mbnetNetworkManager::stopNetwork -- session reset embedded */
#define ADDR_RESET_PLAYERS           0x53B7F0  /* mbnetData::initialize -- player reset embedded */
#define ADDR_IS_THREAD_RUNNING       0x54B8C0  /* mbnetNetworkManager::isThreadActive */

/* Scene transition -- no single-function equivalent in WSE2.
   mbMetaMission::startMission (0x4EFE40) + mbMission::start (0x4F5490) together
   cover what vanilla ADDR_SCENE_TRANSITION did. */
#define ADDR_SCENE_TRANSITION    0x4F5490  /* mbMission::start -- __thiscall(mission*) */

/* Save system */
#define ADDR_BUILD_SAVE_PATH     0x45DB30  /* mbBasicGame::getMyDocumentsSavegamePath */

/* =================================================================== */
/*  Prologue sizes (verified by WSE2 disassembly -- complete instrs,    */
/*  no relative refs)                                                   */
/* =================================================================== */

#define CAMPAIGN_TICK_PROLOGUE_SIZE   7  /* push ebp; mov ebp,esp; sub esp,0x18; push esi */
#define FRAMEMOVE_PROLOGUE_SIZE       9  /* push ebp; mov ebp,esp; mov eax,fs:[0] (SEH, safe) */
#define UPDATE_AI_PROLOGUE_SIZE       7  /* push ebp; mov ebp,esp; sub esp,0x48; push esi */
#define INITIATE_BATTLE_PROLOGUE_SIZE 9  /* push ebp; mov ebp,esp; sub esp,0x248 */
#define ENCOUNTER_ACTION_PROLOGUE_SIZE 7 /* push ebp; mov ebp,esp; test byte [ebp+8],1; push ebx */
#define CLEANUP_BATTLE_PROLOGUE_SIZE  9  /* push ebp; mov ebp,esp; mov eax,fs:[0] (SEH, safe) */

/* =================================================================== */
/*  Inline patch site addresses                                         */
/* =================================================================== */

/* Time delta: SSE movss xmm0,[0xA44D0C] (8 bytes, was x87 fld in vanilla) */
#define ADDR_TIME_DELTA_LOAD        0x4B2256  /* normal campaign path */
#define TIME_DELTA_LOAD_PROLOGUE_SIZE 8       /* movss xmm0, dword [0xA44D0C] */
/* Alt path at 0x4B2214 (accel mode) loads the same global -- patch both if needed */

/* Edge scroll: SSE ucomiss/lahf/test/jnp pattern (was x87 fnstsw/test/jne in vanilla).
   4 identical sites for up/down/left/right edges. */
#define ADDR_EDGE_SCROLL_PATCH      0x4E86B0  /* lahf; test ah,0x44; jnp (7 bytes) -- 1 of 4 */
/* Additional sites: 0x4E8743, 0x4E87CB, 0x4E8852 */

/* Party tick encounter skip / visual reentry */
#define ADDR_PARTY_TICK_ENCOUNTER   0x56BE88  /* cmp [edi+0x1C0], 4 -- encounter detection (7 bytes) */
#define ADDR_PARTY_TICK_VISUAL      0x56C1E0  /* mov ecx, edi -- visual update reentry (2 bytes) */
#define PARTY_TICK_ENCOUNTER_PATCH_SIZE 7     /* cmp dword [edi+0x1C0], 4 = 7 bytes */

/* AI walk step limit -- WSE2 reduced from 10 to 6 */
#define ADDR_AI_PATH_WALK_LIMIT     0x56E617  /* operand byte of cmp eax, imm8 (value=0x06) */

/* Serial bypass in connect thread */
#define ADDR_SERIAL_BYPASS          0x547D61  /* 6-byte jne -- NOP to bypass serial check */

/* Vanilla-era patch-site cluster removed: every address was mid-instruction
   in unrelated WSE2 code (rglConfig::save, muParser, CD3DEnumeration...) --
   PDB audit B6. */

/* =================================================================== */
/*  Network manager globals                                             */
/* =================================================================== */

/*
 * ARCHITECTURAL CHANGE from vanilla:
 * Vanilla: ADDR_NETMGR_HOST (0x87C2E0) + ADDR_NETMGR_DATA (0xDD9CC0) -- two flat BSS regions.
 * WSE2:    g_networkManager (0xAF76A8, 0xE80 bytes) + g_multiplayerData (0xA80740, 0x1780 bytes).
 *
 * Code that writes to (ADDR_NETMGR_HOST + offset) still works as long as offsets are updated.
 */
#define ADDR_NETMGR_HOST         0xAF76A8  /* g_networkManager -- mbnetNetworkManager (0xE80 bytes) */
#define ADDR_NETMGR_DATA         0xA80740  /* g_multiplayerData -- mbnetData (0x1780 bytes) */
#define ADDR_NETMGR_SESSION      ADDR_NETMGR_HOST  /* session reset is embedded in stopNetwork */
#define ADDR_NETMGR              ADDR_NETMGR_HOST   /* legacy alias */

/* Offsets relative to ADDR_NETMGR_HOST (g_networkManager, 0xAF76A8) */
/* NETMGR_OFF_ANTICHEAT: REMOVED in WSE2 -- no Steam VAC field.
   Code setting this to 0 must be removed or guarded. */
#define NETMGR_OFF_ANTICHEAT     0xFFFF  /* REMOVED -- sentinel value, writes will fault intentionally */
#define NETMGR_OFF_INITIALIZED   0x58    /* bool: m_winsockStarted (same offset as vanilla) */
#define NETMGR_OFF_THREAD_ALIVE  0x59    /* bool: m_networkActive (same offset as vanilla) */
#define NETMGR_OFF_HOST          0x74    /* ptr: m_host (mbnetHost* -- custom UDP/WinSock, not ENet; see NETWORKING_AUDIT §3) -- vanilla was 0x8C */
#define NETMGR_OFF_THREAD        0x88    /* HANDLE: m_networkThread -- vanilla was 0xA0 */
#define NETMGR_OFF_PORT          0x94    /* ushort: m_server.m_address.m_port -- vanilla was 0xAC */

/* Absolute addresses for net fields (base + offset) */
#define ADDR_NET_RUN_FLAG        0xAF7701  /* g_networkManager.m_networkActive (byte: 1=alive) */
#define ADDR_NET_PROGRESS_STATE  0xAF7724  /* g_networkManager.m_actionCode (int: connection progress) */
#define ADDR_MBNET_HOST_PTR      0xAF771C  /* g_networkManager.m_host (ptr: mbnetHost* -- custom UDP/WinSock, not ENet; see NETWORKING_AUDIT §3) */
#define ADDR_STEAM_API_INIT      0xA4F5FB  /* g_isSteamAPIInit (BYTE) -- 1 once the engine's SteamAPI_Init succeeded; gates the Steam tunnel (NETWORKING_AUDIT §4/§7.1) */

/* Bitstream range fields -- changed offsets from vanilla */
#define NETMGR_OFF_BITS_PLAYER   0x2C    /* m_numBitsPlayer -- vanilla was 0x38 */
#define NETMGR_OFF_BITS_TROOP    0x38    /* m_numBitsTroop -- vanilla was 0x40 */

/* =================================================================== */
/*  Session / multiplayer data (g_multiplayerData at 0xA80740)          */
/* =================================================================== */

/*
 * ARCHITECTURAL CHANGE: vanilla had standalone BSS globals for session params.
 * WSE2 stores them as fields within g_multiplayerData (mbnetData, 0x1780 bytes).
 */
#define ADDR_LOCAL_PLAYER_IDX    0xA807AC  /* g_multiplayerData.m_myPlayerNo (int) */
#define ADDR_CLIENT_MODE_FLAG    0xA808C0  /* g_multiplayerData.m_missionStarting (bool, 1 byte!) */
#define ADDR_MP_SCENE_NO         0xA808AC  /* g_multiplayerData.m_nextSiteNo */
#define ADDR_MP_MT_NO            0xA808B4  /* g_multiplayerData.m_nextMissionTemplateNo */
#define ADDR_MP_MODE_PENDING     0xA808C0  /* g_multiplayerData.m_missionStarting (bool, 1 byte!) */

#define BATTLE_MP_PORT           7240      /* default Warband MP port */

/* =================================================================== */
/*  Screen / map globals                                                */
/* =================================================================== */

#define ADDR_SCREEN_MGR_BASE     0xABB950  /* g_gameScreen -- mbGameScreen instance (0xA4 bytes) */
/* In WSE2, g_gameScreen is a struct instance, NOT a pointer-to-pointer like vanilla.
   No standalone "map screen pointer" exists; g_gameScreen is just
   m_windows[38] + m_openWindows (audit (c)). */

/* g_basicGame (0xA84C68) contains game type and direct connect fields */
#define ADDR_BASIC_GAME          0xA84C68  /* mbBasicGame instance (0x35608 bytes) */

/* Game type: 0=SP, 1=client, 2=dedicated, 3=host, 5=campaign_server */
#define ADDR_MAP_INTERACTION_MODE 0xA89524  /* g_basicGame + 0x48BC = m_gameType */

/* Direct connect fields (in g_basicGame) */
#define ADDR_DIRECT_CONNECT_ADDR     0xA89650  /* g_basicGame.m_storedAddress (rglString, 64 bytes) */
#define ADDR_DIRECT_CONNECT_PASS     0xA89690  /* g_basicGame.m_storedPassword (rglString, 64 bytes) */
#define ADDR_SWITCHING_MODULE        0xA8960D  /* g_basicGame.m_switchingModule (bool) */
#define ADDR_SWITCHING_TO_CAMPAIGN   0xA8960E  /* g_basicGame.m_switchingToCampaign (bool) */
#define ADDR_DIRECT_CONNECT_FLAG     0xA8960F  /* g_basicGame.m_connectToServer (bool) */

/* Encounter flags: real encounter flags = game+0x3C8 (mbGame::m_encounterFlags),
   not an mbMetaMission field. ADDR_ENCOUNTER_FLAGS was a duplicate of
   ADDR_META_MISSION + OFF_MM_RESULT_FLAGS under a wrong name (B5), removed. */
#define ADDR_META_MISSION        0xA476D8  /* mbMetaMission instance (0x50 bytes) */

/* =================================================================== */
/*  Additional WSE2 globals                                             */
/* =================================================================== */

#define ADDR_CORE_GAME           0xA73AB0  /* g_coreGame -- mbCoreGame (0x9E8 bytes) */
#define ADDR_NETWORK_MGR         0xAF76A8  /* g_networkManager (alias for ADDR_NETMGR_HOST) */
#define ADDR_D3D_APP             0xAF8AE0  /* g_D3DApp -- CD3DApplication instance */
#define ADDR_GAME_VARIABLES      0xABA270  /* g_gameVariables */
#define ADDR_GLOBAL_VARS_VEC     0xA84E88  /* g_basicGame+0x220: m_globalVariables._Myfirst (CLIENT only) */
#define ADDR_GLOBAL_VARS_END     0xA84E8C  /* g_basicGame+0x220: m_globalVariables._Mylast (CLIENT only) */

/* Campaign dedicated server (mb_warband_wse2_dedicated_campaign.exe):
   g_basicGame at 0x8D27D8 (PDB-verified), m_globalVariables at +0x2B0
   (dedicated binaries carry m_banListStream, shifting members +0x90 vs
   the client's +0x220 -- see patches/WarbandDedicated/findings.md,
   getGlobalVariable at 0x437E40). +0x220 here is m_triggerParams:
   writes through the old 0x8CE9D8 landed in scratch space. */
#define CAMP_ADDR_GLOBAL_VARS_VEC 0x8D2A88
#define CAMP_ADDR_GLOBAL_VARS_END 0x8D2A8C  /* m_globalVariables._Mylast */

/* Troop array in campaign server (Fix H: troop_set_xp).
   RE'd from addExperienceToTroop at 0x46B270 in dedicated_campaign.
   m_experience at +0x164, m_level at +0x178 (same as client). */
#define CAMP_OFF_TROOP_ARRAY     0x13D28    /* game + offset -> troop_array_ptr */
#define CAMP_TROOP_STRIDE        0x978      /* sizeof(mbTroop) = 0x978 in this build (PDB-confirmed; no 0xFC8 variant exists -- audit b1) */
#define CAMP_ADDR_LEVEL_TABLE         0x8C3040  /* g_levelTable -- int[64] (PDB ?g_levelTable@@3PAHA) */
#define CAMP_LEVEL_TABLE_ENTRIES      64
#define CAMP_ADDR_LEVEL_BOUNDARY_MULT 0x8C1AD4  /* rglConfig::Campaign::fLevelBoundaryMultiplier (float) */
#define CAMP_OFF_NUM_TROOPS           0x13D2C   /* mbGame::m_numTroops (right after m_troops @0x13D28) */
#define ADDR_META_MISSION_BASE   0xA476D8  /* g_metaMission -- mbMetaMission (0x50 bytes) */
#define ADDR_TIME_SPEED_MULT     0xA44D0C  /* float: time_speed_multiplier (read-only constant) */
#define ADDR_NUM_PLAYERS_LIMIT   0xA44D68  /* int: rglConfig::Network::iNumPlayersLimit */
#define ADDR_SERVER_PORT         0xA44B40  /* int: rglConfig::Network::iServerPort */
#define ADDR_IS_STEAM_INIT       0xA4F5FB  /* bool: g_isSteamAPIInit */

/* Player identity:
   Vanilla had flat globals at 0x861908 (name), 0x861900 (unique_id), 0x8619B4 (enabled).
   WSE2 stores player name in g_multiplayerData.m_profiles[profileNo].m_name.
   unique_id = (uint)(player.m_sessionId & 0xFFFFFF), computed by mbnetPlayer::getUniqueId.
   These addresses are NOT direct equivalents -- code using them needs rework. */
/* #define ADDR_PLAYER_NAME      -- see profiles vector in g_multiplayerData+0x04 */
/* #define ADDR_UNIQUE_ID        -- computed from session id, no stored global */
/* #define ADDR_UNIQUE_ID_ENABLED -- use ADDR_IS_STEAM_INIT (0xA4F5FB) */

/* =================================================================== */
/*  Game struct offsets (from *ADDR_CUR_GAME)                           */
/* =================================================================== */

#define OFF_TIME_DELTA           0x15A64  /* float: m_frameTime (PDB) -- 0x15C40 was inside m_mainPartyDnas, audit B4 */
#define OFF_GAME_HOUR            0x13EA0  /* m_hour; +4 day, +8 week, +C month, +10 year; m_dateTimer (mbGameTimer) at +0x13E90 -- PDB */
#define OFF_SAVE_SLOT            0x0000   /* int: m_savegameNo (same as vanilla) */
#define OFF_MAIN_PARTY_NO        0x0394   /* int: m_mainPartyNo -- vanilla 0x6CC */
#define OFF_CAMERA_PARTY_NO      0x03A0   /* int: m_cameraPartyNo -- vanilla 0x6D8 */
#define OFF_CAMERA_FOLLOW_ENABLED 0x03A4  /* bool (1 byte!): m_cameraFollowingParty -- vanilla 0x6DC */
#define OFF_PLAYER_TROOP_NO      0x03A8   /* int: m_playerTroopNo -- vanilla 0x6E0 */
#define OFF_PAUSED               0x03B0   /* bool (1 byte!): m_paused -- vanilla 0x6E8 */
#define OFF_PARTIES_HV           0x0444   /* rglHashVector<mbParty>: m_parties -- vanilla 0x7E4 */
#define OFF_FACTIONS_PTR         0x13D7C  /* mbFaction*: m_factions -- vanilla 0x1413C */
#define OFF_NUM_FACTIONS         0x13D80  /* int: m_numFactions -- vanilla 0x14140 */

/* Encounter fields (still in mbGame, not moved to mbMetaMission) */
#define OFF_ENCOUNTER_PARTY      0x13D48  /* int: m_encounteredPartyNo -- vanilla 0x140FC */
#define OFF_ENCOUNTER_TYPE       0x13D4C  /* int: m_encounteredPartyNo2 -- vanilla 0x14100 */
#define OFF_ENCOUNTER_SIDE       0x13D50  /* int: m_encounteredPartyIsAttacker -- vanilla 0x14104 */

/* Battle fields MOVED to mbMetaMission (g_metaMission = 0xA476D8).
   Code reading game+OFF_BATTLE_* must be changed to read from g_metaMission+offset.
   These defines point into the mbMetaMission global so existing read patterns
   (*(int32_t*)((char*)game + OFF_BATTLE_ADVANTAGE)) need to change to
   (*(int32_t*)(ADDR_META_MISSION + OFF_MM_BATTLE_ADVANTAGE)). */
#define OFF_MM_PARTY_A           0x0000   /* m_encounteredParties[0] */
#define OFF_MM_PARTY_B           0x0004   /* m_encounteredParties[1] */
#define OFF_MM_TYPE              0x000C   /* m_type */
#define OFF_MM_BATTLE_ADVANTAGE  0x0010   /* m_battleAdvantage */
#define OFF_MM_MAIN_PARTY_SIDE   0x0018   /* m_mainPartySide */
#define OFF_MM_RESULT_FLAGS      0x001C   /* m_resultFlags */
#define OFF_MM_BATTLE_MT_NO      0x0034   /* m_missionTemplateNo */
#define OFF_MM_BATTLE_SCENE      0x0038   /* m_siteNo */
#define OFF_MM_ENTRY_POINT       0x003C   /* m_entryPointNo */
#define OFF_MM_IN_PARTY_BATTLE   0x004C   /* m_inPartyBattleMode (bool) */

/* Compatibility aliases: battle fields redirected to g_metaMission.
   WARNING: code using (game + OFF_BATTLE_*) is BROKEN. These are offsets from
   ADDR_META_MISSION, not from game. Defined here so code compiles, but callers
   must be updated to read from ADDR_META_MISSION instead. */
#define OFF_BATTLE_ADVANTAGE     OFF_MM_BATTLE_ADVANTAGE  /* read from ADDR_META_MISSION! */
#define OFF_BATTLE_SCENE         OFF_MM_BATTLE_SCENE      /* read from ADDR_META_MISSION! */
#define OFF_BATTLE_PARTY_B       OFF_MM_PARTY_B           /* read from ADDR_META_MISSION! */
#define OFF_BATTLE_MT_NO         OFF_MM_BATTLE_MT_NO      /* read from ADDR_META_MISSION! */

/* =================================================================== */
/*  Mission object fields (from *ADDR_CUR_MISSION)                      */
/* =================================================================== */

#define MISSION_OFF_MT_NO        0x9600   /* int: m_missionTemplateNo -- vanilla 0xB7F8 */
#define MISSION_OFF_SCENE        0x9604   /* int: m_siteNo -- vanilla 0xB7FC */
#define MISSION_OFF_MP_FLAG      0x9B19   /* byte: m_isMultiplayer -- vanilla 0xBD31 */

/* =================================================================== */
/*  Hash vector internals (from HV base at game + OFF_PARTIES_HV)       */
/* =================================================================== */

/*
 * Chunked storage, same as vanilla: m_items is an array of chunk pointers,
 * each chunk holding 16 mbParty (PDB audit B3). `mbGame::getParty` decompiles
 * to (raw & 0xF)*0x5718 + items[raw >> 4]; `rglHashVector<mbParty>::createChunk`
 * @0x4BF210 allocates chunks. For main-thread client code prefer the engine's
 * O(1) `mbGame::getParty` @0x4B5E40 -- the raw walker below exists only for
 * thread-safe reads off the main thread.
 */
#define HV_ITEMS_BEGIN       0x138CC   /* m_items._Myfirst (mbParty** chunk array) */
#define HV_ITEMS_END         0x138D0   /* m_items._Mylast */
#define HV_NUM_CREATED       0x138D8   /* m_numIndices (party count, not raw slot count) */
#define HV_CHUNK_SHIFT       4         /* 16 mbParty per chunk */
#define HV_CHUNK_MASK        0xF

/* =================================================================== */
/*  Party struct offsets (party size = 0x5718)                          */
/* =================================================================== */

#define PARTY_SIZE           0x5718    /* vs vanilla 0x5D28 (-0x610 bytes) */
#define PARTY_OFF_VALID      0x04     /* same as vanilla -- rglStableVectorItem base */
#define PARTY_OFF_NO         0x08     /* same as vanilla -- rglStableVectorItem base */
#define PARTY_OFF_POS        0x0090   /* rglVector4: x at +0x90, y at +0x94 -- vanilla 0x130 */
#define PARTY_OFF_FACTION    0x00F8   /* int: m_factionNo -- vanilla 0x1F0 */
#define PARTY_OFF_TEMPLATE   0x0110   /* int: m_partyTemplateNo -- vanilla 0x210 */
#define PARTY_OFF_TROOPS_VEC 0x0138   /* rglVector<mbPartyStack> (12 bytes) -- vanilla 0x240 */
#define PARTY_OFF_NUM_STACKS 0x0144   /* int: m_numStacks -- vanilla 0x250 */
#define PARTY_OFF_ATTACHED_TO 0x0164  /* int: m_parentPartyNo -- vanilla 0x20C */

/* AI pending fields -- written by aiUpdateBehavior, copied to active each tick */
#define PARTY_OFF_AI_PENDING       0x0184  /* int: m_defaultBehavior -- vanilla 0x294 */
#define PARTY_OFF_AI_PENDING_OBJ   0x0188  /* int: m_defaultBehaviorObject -- vanilla 0x298 */
#define PARTY_OFF_AI_PENDING_X     0x018C  /* float: m_defaultBehaviorPosition.x -- vanilla 0x29C */
#define PARTY_OFF_AI_PENDING_Y     0x0190  /* float: m_defaultBehaviorPosition.y -- vanilla 0x2A0 */

/* AI active fields -- what the movement system reads */
#define PARTY_OFF_AI_BEHAV         0x01C0  /* int: m_behavior -- vanilla 0x2D0 */
#define PARTY_OFF_AI_TARGET_PARTY  0x01C4  /* int: m_behaviorObject -- vanilla 0x2D4 */
#define PARTY_OFF_AI_TARGET_X      0x01C8  /* float: m_behaviorPosition.x -- vanilla 0x2DC */
#define PARTY_OFF_AI_TARGET_Y      0x01CC  /* float: m_behaviorPosition.y -- vanilla 0x2E0 */

#define PARTY_OFF_AI_WAIT_TIMER    0x0180  /* float: m_behaviorSelectTime -- vanilla 0x290 */
#define PARTY_OFF_DEST             0x0210  /* rglVector2: x at +0x210, y at +0x214 -- vanilla 0x320 */
#define PARTY_OFF_PATH_STATUS      0x5228  /* int: m_pathValidity -- vanilla 0x533C */
#define PARTY_OFF_PATH_TARGET      0x522C  /* int: m_targetManifoldFaceNo (navmesh face, NOT a party no) -- vanilla 0x5340 */
#define PARTY_OFF_PATH_NEEDS_UPDATE 0x5230 /* int: m_computePath -- vanilla 0x5344 */
#define PARTY_OFF_MOVE_TARGET_PARTY 0x5250 /* m_moveTargetPartyNo -- the party-valued target (PDB, audit B9) */
#define PARTY_OFF_SLOTS            0x5280  /* mbSlots -> rglVector<__int64> -- vanilla 0x5390 */

/* Party stack struct (WSE2 size = 0x1C vs vanilla 0x20) */
#define PARTY_STACK_SIZE     0x1C
#define STACK_OFF_NUM_TROOPS 0x00     /* same as vanilla */

/* =================================================================== */
/*  WSE2 vector layout (12 bytes, NO self_ptr prefix)                   */
/*  Vanilla: +0=self_ptr, +4=start, +8=end, +C=max (16 bytes)          */
/*  WSE2:    +0=_Myfirst, +4=_Mylast, +8=_Myend (12 bytes)             */
/* =================================================================== */

#define VEC_OFF_START  0   /* _Myfirst -- vanilla was 4 */
#define VEC_OFF_END    4   /* _Mylast  -- vanilla was 8 */

/* =================================================================== */
/*  Co-op slot indices on p_main_party                                  */
/* =================================================================== */

#define SLOT_COOP_SPAWN_REQ      100
#define SLOT_COOP_PARTY_NO       101
#define SLOT_COOP_SETUP_DONE     102
#define SLOT_COOP_LOBBY_STATE    103
#define SLOT_COOP_SAVE_SLOT      104
#define SLOT_COOP_CLIENT_READY   105
#define SLOT_COOP_HOST_IP        106
#define SLOT_COOP_ROLE           107
/* 108-110 free (were SLOT_COOP_BATTLE_WINNER/ATK_CAS/DEF_CAS -- legacy
   in-process battle result delivery, removed; results flow via the
   battle dict + PKT_BATTLE_END IPC) */

/* =================================================================== */
/*  Faction struct (WSE2 size = 0x500, vanilla = 0xCA4)                 */
/* =================================================================== */

#define FACTION_SIZE             0x500
/* ARCHITECTURAL CHANGE: vanilla relations = float[128] at fixed offset.
   WSE2 relations = rglVector<float> (dynamic, 12 bytes) at offset 0x8C.
   Access changes from (faction + 0x12C + target*4) to dereferencing the
   vector's _Myfirst pointer at (faction + 0x8C). */
#define FACTION_RELATIONS_OFF    0x008C  /* rglVector<float> -- NOT float[128]! */

/* =================================================================== */
/*  mbnetPlayer struct (0x348 bytes, heap-allocated via vector)          */
/* =================================================================== */

#define PLAYER_SIZE              0x348
#define PLAYER_OFF_STATUS        0x0000  /* int: connection state */
#define PLAYER_OFF_NAME          0x00BC  /* rglString: m_name (64 bytes) */
#define PLAYER_OFF_AGENT_NO      0x01A0  /* int: m_agentNo */
#define PLAYER_OFF_TEAM_NO       0x01A8  /* int: m_teamNo */
#define PLAYER_OFF_TROOP_NO      0x01AC  /* int: m_troopNo */
#define PLAYER_OFF_READY         0x01B4  /* bool: m_ready */
#define PLAYER_OFF_READY_SPAWN   0x019D  /* bool: m_readyToSpawn */
#define PLAYER_OFF_ITEMS         0x01C0  /* int[10]: m_items */
#define PLAYER_OFF_SLOTS         0x0210  /* mbSlots: m_slots (12 bytes) */
#define PLAYER_OFF_PARTY_NO      0x0344  /* int: m_partyNo (WSE2 extension) */

/* =================================================================== */
/*  Accessor helpers                                                    */
/* =================================================================== */

static __inline void *wb_cur_game(void) {
    return *(void **)REBASE(g_addrs->cur_game);
}

static __inline void *wb_cur_mission(void) {
    return *(void **)REBASE(g_addrs->cur_mission);
}

/* =================================================================== */
/*  Hash vector navigation -- CHUNKED (16 mbParty per chunk, PDB B3)    */
/* =================================================================== */

static __inline int hv_num_items(const void *game) {
    const char *hv = (const char *)game + OFF_PARTIES_HV;
    return *(int *)(hv + HV_NUM_CREATED);
}

/*
 * Chunk-indexed party lookup: m_items is an array of chunk pointers, each
 * chunk holding HV_CHUNK_MASK+1 mbParty slots contiguously. raw_index is a
 * raw slot index (chunk_no = raw_index >> HV_CHUNK_SHIFT, slot within chunk
 * = raw_index & HV_CHUNK_MASK), not a party-count index.
 */
static __inline char *hv_party_ptr(const void *game, int raw_index) {
    const char *hv = (const char *)game + OFF_PARTIES_HV;
    char **chunks     = *(char ***)(hv + HV_ITEMS_BEGIN);
    char **chunks_end = *(char ***)(hv + HV_ITEMS_END);
    int num_chunks, chunk_no;
    if (!chunks || !chunks_end) return NULL;
    num_chunks = (int)(chunks_end - chunks);
    if (raw_index < 0) return NULL;
    chunk_no = raw_index >> HV_CHUNK_SHIFT;
    if (chunk_no >= num_chunks || !chunks[chunk_no]) return NULL;
    return chunks[chunk_no] + (raw_index & HV_CHUNK_MASK) * PARTY_SIZE;
}

/*
 * Scans every raw slot across all chunks (num_chunks << HV_CHUNK_SHIFT),
 * not hv_num_items() -- that count is the live party count, not the raw
 * slot capacity. For main-thread client code prefer the engine's O(1)
 * mbGame::getParty @0x4B5E40; this walker exists for thread-safe reads only.
 */
static __inline char *find_party_by_no(const void *game, int target_no) {
    const char *hv = (const char *)game + OFF_PARTIES_HV;
    char **chunks     = *(char ***)(hv + HV_ITEMS_BEGIN);
    char **chunks_end = *(char ***)(hv + HV_ITEMS_END);
    int total, i;
    if (!chunks || !chunks_end) return NULL;
    total = (int)(chunks_end - chunks) << HV_CHUNK_SHIFT;
    for (i = 0; i < total; i++) {
        char *p = hv_party_ptr(game, i);
        if (!p) continue;
        if (*(int *)(p + PARTY_OFF_VALID) != 1) continue;
        if (*(int *)(p + PARTY_OFF_NO) == target_no)
            return p;
    }
    return NULL;
}

/* =================================================================== */
/*  Party slot access (mbSlots = rglVector<__int64>, 12 bytes)          */
/*  NO self_ptr prefix: VEC_OFF_START=0, VEC_OFF_END=4                  */
/* =================================================================== */

static __inline int party_slot_count(const char *party) {
    __int64 *start = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_START);
    __int64 *end   = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_END);
    if (!start || !end || end <= start) return 0;
    return (int)(end - start);
}

static __inline __int64 party_get_slot(const char *party, int slot) {
    __int64 *start = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_START);
    __int64 *end   = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_END);
    if (!start || !end) return 0;
    if (slot < 0 || slot >= (int)(end - start)) return 0;
    return start[slot];
}

static __inline void party_set_slot(char *party, int slot, __int64 val) {
    __int64 *start = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_START);
    __int64 *end   = *(__int64 **)(party + PARTY_OFF_SLOTS + VEC_OFF_END);
    if (!start || !end) return;
    if (slot < 0 || slot >= (int)(end - start)) return;
    start[slot] = val;
}

/* =================================================================== */
/*  MetaMission battle field accessors (convenience)                    */
/* =================================================================== */

static __inline int mm_battle_advantage(void) {
    return *(int *)(REBASE(ADDR_META_MISSION) + OFF_MM_BATTLE_ADVANTAGE);
}
static __inline int mm_battle_scene(void) {
    return *(int *)(REBASE(ADDR_META_MISSION) + OFF_MM_BATTLE_SCENE);
}
static __inline int mm_battle_mt_no(void) {
    return *(int *)(REBASE(ADDR_META_MISSION) + OFF_MM_BATTLE_MT_NO);
}
static __inline int mm_party_b(void) {
    return *(int *)(REBASE(ADDR_META_MISSION) + OFF_MM_PARTY_B);
}
static __inline int mm_encounter_side(void) {
    return *(int *)(REBASE(ADDR_META_MISSION) + OFF_MM_MAIN_PARTY_SIDE);
}

/* =================================================================== */
/*  Client ASI (mb_warband_wse2.exe)                                    */
/*  Addresses used only by warband_coop.asi: server browser injection,  */
/*  the createAgent player-attach detour, and local co-op battle         */
/*  plumbing (Option C metaMission populate + gameType flip hooks).     */
/*  The client has ASLR disabled via binary patch, so these are used    */
/*  as raw literals -- do NOT wrap in REBASE().                         */
/* =================================================================== */

/* rglString register array (s0, s1, ... string registers) */
#define STRING_REG_BASE         0xA87298
#define STRING_REG_STRIDE       0x40

/* mbMission::createAgent detour — player attach on gameType=4.
   createAgent is __thiscall with 19 args (see kb.h @ 0x500B70). MSVC places
   `this` in ECX; all other args are pushed right-to-left on the stack.
   Argument order at entry (stack slots, [ESP] = return address):
     [ESP+0x04] transform         (param 2)
     [ESP+0x08] entryPointNo      (param 3)
     [ESP+0x0C] troopNo           (param 4)
     ...
     [ESP+0x38] playerNo          (param 15, the -1 we want to replace)
   Stack layout confirmed by subagent RE (findings_encounters.md section
   "Entry playerNo Routing"). */
#define ADDR_CREATE_AGENT          0x500B70
#define CREATE_AGENT_PROLOGUE_SIZE 5     /* push ebp + mov ebp,esp + push -1 = 5 bytes exactly */

/* Server list vector: g_multiplayerData.m_serverList */
#define ADDR_SERVER_LIST        0xA80750  /* rglVector<mbnetServer> */
#define ADDR_SEARCHING_SERVERS  0xA80769  /* uint8 m_searchingServers */
#define ADDR_MP_PROFILE_NO      0xA80740  /* int g_multiplayerData.m_profileNo */
#define ADDR_MP_PROFILES_FIRST  0xA80744  /* mbnetProfile* profiles._Myfirst */
#define MP_PROFILE_STRIDE       0x90
#define MP_PROFILE_TAB_OFF      0x74      /* persisted browser source: 0=Internet 1=LAN 2=Favorites (clamped 0..2 by initialize @0x517CD4) */
#define ADDR_NUM_PLAYERS        0xA807B4

/* g_basicGame stored fields for auto-connect */
#define ADDR_STORED_MODULE      0xA89610

/* Server browser */
#define ADDR_BROWSER_WINDOW     0xABB9B8
#define ADDR_BROWSER_FRAMEMOVE  0x519A20
#define BROWSER_PROLOGUE_SIZE   6

/* Engine functions */
#define ADDR_SERVER_CTOR        0x568C30  /* mbnetServer::mbnetServer() */
#define ADDR_SERVER_DTOR        0x51EE60  /* mbnetServer::~mbnetServer() */
#define ADDR_VEC_PUSH_BACK      0x546BF0  /* vector<mbnetServer>::push_back */
#define ADDR_VEC_CLEAR          0x51E570  /* rglVector<mbnetServer>::clear */
#define ADDR_FILL_SERVER_LIST   0x51CE10  /* fillServerList(this=window) */

/* Troop access (client): mbGame::m_troops at game+0x13D40 (mbTroop*, stride
   0x978), m_numTroops at +0x13D44; troop slots = mbTroop::m_slots (mbSlots)
   at +0x968, elements __int64. Engine accessor: mbGame::getTroop 0x4B5DA0.
   (PDB audit B7 -- the previous ADDR_TROOPS_VEC/TROOP_SIZE/TROOP_SLOTS_OFF
   trio was vanilla-era and entirely wrong.) */

/* Option C — metaMission populate for coop local battle.
   See patches/Warband/findings_encounters.md "Option C Impl RE". */
#define ADDR_SET_PARAMS          0x4F4B10  /* mbMission::setParams */

/* Drain the client's outbound event queue while gameType is still 4
   (see coop_flush_client_events in coop.c for the full rationale). */
#define ADDR_NET_CLIENT_SEND   0x545540   /* mbnetNetworkClient::send(this) */
#define ADDR_NET_CLIENT_THIS   0xAF77C0   /* mbnetNetworkClient (call-site literal) */
#define ADDR_NET_PLAYERS_VEC   0xA80810   /* *(void**) m_players.m_vec begin -> slot0 */

/* mission_frameMove — per-frame gameType flip for coop local battles */
#define ADDR_MISSION_FRAMEMOVE     0x4FC450
#define MISSION_FRAMEMOVE_PROLOGUE 6  /* push ebp/mov ebp,esp/and esp,-8 */

/* Mission-end transition hook inside mbTacticalWindow::frameMove --
   restores gameType=4 before the post-battle menu transition. */
#define ADDR_MISSION_END_TRANSITION  0x5C68BE
#define MISSION_END_TRANSITION_SIZE  7  /* cmp dword ptr [imm32], imm8 */

/* Party replication row apply in mbnetNetworkClient::receiveReplicationData
   (0x544270, m_gameType == 4 branch). The engine turns the result of
   rglHashVector<mbParty>::getRawIndex (0x470700) into a party pointer with
   no miss check; -1 (a party removed by an event earlier in the same
   packet) becomes a low unmapped address and replicatePosition faults.
   Hook lands right after the getRawIndex call with the raw index in eax. */
#define ADDR_REPL_PARTY_ROW_LOOKUP   0x5444BF  /* mov edx,eax ; mov eax,[esi+0x13D10] */
#define REPL_PARTY_ROW_LOOKUP_SIZE   8
#define ADDR_REPL_PARTY_ROW_NEXT     0x54456C  /* per-row continue: reloads esi, advances edi and the row counter */

/* Talk-branch short-circuit -- party-window Talk on an MP campaign client
   starts a map conversation, an SP-only mission path whose entry-group
   source is never populated (spawnEntryGroups derefs null-4), and the
   caller's tail then switches the UI into a conversation window with no
   scene (renderer crash). The whole branch must be skipped: hook the
   5-byte `call startMapConversation` and, in MP, drop the 4 pushed args
   and jump to the branch join point. The join consumes edi (party-window
   this), which stays live across the hook.
   See patches/Warband_WSE2/findings.md "startMapConversation". */
#define ADDR_START_MAP_CONVERSATION  0x4F0360  /* mbMetaMission::startMapConversation (__thiscall, ret 0x10) */
#define ADDR_PARTY_TALK_CALL         0x52E74A  /* call insn in mbPartyWindow::frameMove */
#define ADDR_PARTY_TALK_RESUME       0x52E74F  /* next insn after the call (SP path) */
#define ADDR_PARTY_TALK_JOIN         0x52EA9B  /* Talk-branch join point (MP skip) */

/* In MP the skipped Talk instead opens the clicked member's character
   sheet, mirroring the engine's canonical companion-open sequence.
   0x534DF9 is inside mbPresentationWindow::frameMove, not the party
   window: charWin->m_viewedTroopNo/+0x10 = troop,
   m_sourceWindowNo/+0x14 = return-to window, m_mode/+0x4 = 1, then
   mbGameScreen::setWindow(0xB). setWindow is stdcall(windowId), ret 4,
   no this. Sheet is read-only for troops with zero unspent point pools
   (the + buttons only render when the viewed troop has points). */
#define ADDR_CHAR_WINDOW_PTR         0xABB97C  /* &g_gameScreen.m_windows[0xB] (mbCharacterWindow*) */
#define ADDR_SET_WINDOW              0x4C7C50  /* mbGameScreen::setWindow(windowId) */
#define WINDOW_ID_CHARACTER          0xB
#define WINDOW_ID_PARTY              8

/* =================================================================== */
/*  WSE2 Dedicated Server Address Map                                   */
/*  Binary: mb_warband_wse2_dedicated.exe (full PDB symbols)            */
/*                                                                      */
/*  The dedicated server is a separate build -- ALL global addresses     */
/*  differ from the client. Struct FIELD offsets (e.g. player+0x1AC)    */
/*  are identical since both share the same source.                     */
/*                                                                      */
/*  Key architectural differences from client:                          */
/*    - No CD3DApplication, no mbGame::frameMove, no mbGameScreen       */
/*    - Main loop: mbCoreGame::runDedicatedServer -> ::frameMove        */
/*    - g_basicGame has different field offsets (+0x2B0 vs client +0x220 */
/*      for m_globalVariables) due to conditionally-compiled members     */
/*    - isDedicatedServer/isServer/isMultiplayer all return true         */
/*    - ASLR enabled (same as client)                                   */
/* =================================================================== */

/* =================================================================== */
/*  Runtime-accessible dedicated server addresses for campaign & battle */
/*  CAMP_ prefix for campaign server; DED_ prefix for battle servers    */
/* =================================================================== */

/* Net-tuning patch sites (TRAFFIC_OPTIMIZATION R2-R4). Byte addresses of
   the 32-bit operand/data values, not the instruction start -- see
   patches/WarbandDedicated/findings.md "nettune patch sites (2026-07-25)".
   AIMD cap sites (0x489EF2 campaign / 0x4B4692 battle) are intentionally
   NOT patched -- cap stays 100000. These are PREFERRED-BASE VAs: both
   dedicated exes ARE ASLR-slid at runtime (confirmed live -- observed
   non-zero g_aslr_slide on both host and battle processes), so every
   consumer must wrap these in REBASE(), never use them as raw literals.
   AIMD sites live inside mbnetNetworkManager::frameMove; PKT_MAX sites
   live inside mbnetPlayer::computePacketValues (esi+0x2FC there is
   m_uploadLimit, dedicated d7). SEND_PERIOD is k_minPacketSendPeriod --
   a single xref, no COMDAT collateral (dedicated d7). */
#define CAMP_NT_AIMD_STEP    0x00489EED  /* add ecx,imm32 operand -- stock 1000 */
#define CAMP_NT_AIMD_FLOOR   0x00489ECD  /* mov eax,imm32 operand -- stock 3000 */
#define CAMP_NT_PKT_MAX      0x004A717A  /* mov eax,imm32 operand -- stock 1350 */
#define CAMP_NT_SEND_PERIOD  0x00887BC0  /* .rdata float dword -- stock 0.033333335f, k_minPacketSendPeriod */
#define DED_NT_AIMD_STEP     0x004B468D  /* add ecx,imm32 operand -- stock 1000 */
#define DED_NT_AIMD_FLOOR    0x004B466D  /* mov eax,imm32 operand -- stock 3000 */
#define DED_NT_PKT_MAX       0x004D2A9A  /* mov eax,imm32 operand -- stock 1350 */

/* Backlog send-period ceiling. sendToPlayer picks a player's period with a
   three-way branch; when the previous packet overflowed (mbnetPlayer+0x19C
   set from !fillPacket) it uses max(m_packetSendPeriod, min(0.1f,
   ping_ms / 0.001f * 0.7f)). The ping term is a divss where a mulss was
   meant, so it saturates for any ping >= 1 ms and a backlogged player is
   pinned to 10 Hz. The 0.1f dword is shared by ~40 (campaign) / ~100
   (battle) readers incl. the battle exe's frame-dt clamp, so nettune
   re-points the disp32 of the one movss that loads the ceiling at a
   plugin-owned float instead of rewriting the constant. Both the operand
   and its stock value are image-relative: REBASE() both. */
#define CAMP_NT_BACKLOG_CEIL_DISP   0x00499D8D  /* disp32 of movss xmm1,[0.1f] @0x499D89 in sendToPlayer 0x499D30 */
#define CAMP_NT_BACKLOG_CEIL_RDATA  0x00887BEC  /* stock disp32 target: shared .rdata 0.1f */
#define DED_NT_BACKLOG_CEIL_DISP    0x004C56AD  /* disp32 of movss xmm1,[0.1f] @0x4C56A9 in sendToPlayer 0x4C5650 */
#define DED_NT_BACKLOG_CEIL_RDATA   0x008BB870  /* stock disp32 target: shared .rdata 0.1f */

/* CAMP_/DED_ADDR_CUR_GAME and _CUR_MISSION defined near top (feed the
   campaign/battle addr_table instances in warband_addrs_wse2.c) */
#define DED_ADDR_BASIC_GAME        0x907840
#define DED_ADDR_GLOBAL_VARS_VEC   0x907AF0  /* g_basicGame+0x2B0 */
#define DED_ADDR_GLOBAL_VARS_END   0x907AF4  /* m_globalVariables._Mylast */
#define DED_ADDR_NETMGR_DATA       0x903F88
#define CAMP_ADDR_NETMGR_DATA      0x8CEF20  /* g_multiplayerData (mbnetData) in dedicated_campaign -- PDB (audit d5); previously missing, DED_ twin is a different binary */
#define DED_ADDR_NUM_PLAYERS_LIMIT 0x8F6E48
#define DED_ADDR_AGENT_DIE         0x44B090  /* mbAgent::die, 5-byte hookable prologue */
#define DED_ADDR_TRIGGER_EXECUTE   0x51AB30  /* mbTriggerManager::execute */
#define DED_ADDR_COMMIT_DEATH      0x492D60
#define DED_ADDR_COMMIT_WOUND      0x492E00

/* Agent struct (in mbMission chunked deque) */
#define DED_AGENT_SIZE             0x7250
#define DED_AGENT_CHUNK_BITS       4
#define DED_AGENT_CHUNK_MASK       0xF
#define DED_AGENT_OFF_STATUS       0x2C   /* 1=alive, 3=wounded */
#define DED_AGENT_OFF_PLAYER_NO    0x30   /* -1 = no player */
#define DED_AGENT_OFF_TROOP_NO     0x268
#define DED_AGENT_OFF_TEAM_NO      0x738    /* int: team number (0=enemy, 1=ally) */

/* Mission agent deque offsets */
#define DED_MISSION_OFF_AGENT_CHUNKS  0x18
#define DED_MISSION_OFF_AGENT_CAP     0x08  /* m_agents.m_capacity (allocated) */
#define DED_MISSION_OFF_AGENT_COUNT   0x04  /* m_agents.m_size -- LIVE count; iterate this, not capacity (audit b4) */

/* Dedicated server accessor helpers — only call from COOP_BATTLE code.
   Module global access lives in shared/modglobals (initialized per mode). */
static __inline int ded_num_players_limit(void) {
    return *(int *)REBASE(DED_ADDR_NUM_PLAYERS_LIMIT);
}

static __inline char *ded_get_player(int player_no) {
    char *base = *(char **)(REBASE(DED_ADDR_NETMGR_DATA) + 0xD0);
    if (!base) return NULL;
    return base + player_no * PLAYER_SIZE;
}

static __inline char *ded_get_agent(int agent_id) {
    void *mission = *(void **)REBASE(DED_ADDR_CUR_MISSION);
    char **chunks;
    if (!mission) return NULL;
    chunks = *(char ***)((char *)mission + DED_MISSION_OFF_AGENT_CHUNKS);
    if (!chunks) return NULL;
    return chunks[agent_id >> DED_AGENT_CHUNK_BITS] +
           (agent_id & DED_AGENT_CHUNK_MASK) * DED_AGENT_SIZE;
}
