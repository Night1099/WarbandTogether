#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>
#include "steam_flat.h"

void coop_log(const char *fmt, ...);   /* host DLL's logger */

steam_flat_t SF;

typedef void *(__cdecl *sf_accessor_fn)(void);

static FARPROC sf_bind(HMODULE m, const char *name, int *ok) {
    FARPROC p = GetProcAddress(m, name);
    if (!p) { coop_log("[steam] missing export: %s\n", name); *ok = 0; }
    return p;
}

int steam_flat_resolve(void) {
    HMODULE m;
    int ok = 1;
    sf_accessor_fn acc_sockets, acc_utils;

    memset(&SF, 0, sizeof(SF));

    m = GetModuleHandleA("steam_api_wse2.dll");
    if (!m) {
        coop_log("[steam] steam_api_wse2.dll not loaded -- Steam path unavailable\n");
        return 0;
    }

    acc_sockets = (sf_accessor_fn)sf_bind(m, "SteamAPI_SteamNetworkingSockets_SteamAPI_v012", &ok);
    acc_utils   = (sf_accessor_fn)sf_bind(m, "SteamAPI_SteamNetworkingUtils_SteamAPI_v004", &ok);

    #define BIND(field, name) SF.field = (void *)sf_bind(m, name, &ok)
    BIND(CreateListenSocketP2P,      "SteamAPI_ISteamNetworkingSockets_CreateListenSocketP2P");
    BIND(ConnectP2P,                 "SteamAPI_ISteamNetworkingSockets_ConnectP2P");
    BIND(AcceptConnection,           "SteamAPI_ISteamNetworkingSockets_AcceptConnection");
    BIND(CloseConnection,            "SteamAPI_ISteamNetworkingSockets_CloseConnection");
    BIND(CloseListenSocket,          "SteamAPI_ISteamNetworkingSockets_CloseListenSocket");
    BIND(SendMessageToConnection,    "SteamAPI_ISteamNetworkingSockets_SendMessageToConnection");
    BIND(CreatePollGroup,            "SteamAPI_ISteamNetworkingSockets_CreatePollGroup");
    BIND(DestroyPollGroup,           "SteamAPI_ISteamNetworkingSockets_DestroyPollGroup");
    BIND(SetConnectionPollGroup,     "SteamAPI_ISteamNetworkingSockets_SetConnectionPollGroup");
    BIND(ReceiveMessagesOnPollGroup, "SteamAPI_ISteamNetworkingSockets_ReceiveMessagesOnPollGroup");
    BIND(RunCallbacks,               "SteamAPI_ISteamNetworkingSockets_RunCallbacks");
    BIND(GetConnectionRealTimeStatus,"SteamAPI_ISteamNetworkingSockets_GetConnectionRealTimeStatus");
    BIND(InitRelayNetworkAccess,     "SteamAPI_ISteamNetworkingUtils_InitRelayNetworkAccess");
    BIND(SetGlobalConfigValueInt32,  "SteamAPI_ISteamNetworkingUtils_SetGlobalConfigValueInt32");
    BIND(RunSteamCallbacks,          "SteamAPI_RunCallbacks");
    #undef BIND

    /* optional -- MTU telemetry only, absence is not a failure */
    SF.GetConfigValue = (void *)GetProcAddress(m, "SteamAPI_ISteamNetworkingUtils_GetConfigValue");
    if (!SF.GetConfigValue)
        coop_log("[steam] GetConfigValue export absent -- MTU log disabled (non-fatal)\n");

    /* optional -- relay-status diagnostics only */
    SF.GetRelayNetworkStatus = (void *)GetProcAddress(m, "SteamAPI_ISteamNetworkingUtils_GetRelayNetworkStatus");
    if (!SF.GetRelayNetworkStatus)
        coop_log("[steam] GetRelayNetworkStatus export absent -- relay-status log disabled (non-fatal)\n");
    SF.SetDebugOutputFunction = (void *)GetProcAddress(m, "SteamAPI_ISteamNetworkingUtils_SetDebugOutputFunction");
    if (!SF.SetDebugOutputFunction)
        coop_log("[steam] SetDebugOutputFunction export absent -- GNS debug log disabled (non-fatal)\n");

    /* optional -- invites only; absence disables Join Game, never the tunnel */
    {
        sf_accessor_fn acc_friends =
            (sf_accessor_fn)GetProcAddress(m, "SteamAPI_SteamFriends_v017");
        sf_accessor_fn acc_user =
            (sf_accessor_fn)GetProcAddress(m, "SteamAPI_SteamUser_v023");
        SF.SetRichPresence    = (void *)GetProcAddress(m, "SteamAPI_ISteamFriends_SetRichPresence");
        SF.ClearRichPresence  = (void *)GetProcAddress(m, "SteamAPI_ISteamFriends_ClearRichPresence");
        SF.RegisterCallback   = (void *)GetProcAddress(m, "SteamAPI_RegisterCallback");
        SF.UnregisterCallback = (void *)GetProcAddress(m, "SteamAPI_UnregisterCallback");
        SF.GetSteamID         = (void *)GetProcAddress(m, "SteamAPI_ISteamUser_GetSteamID");
        if (acc_friends && acc_user && SF.SetRichPresence && SF.ClearRichPresence &&
            SF.RegisterCallback && SF.UnregisterCallback && SF.GetSteamID) {
            SF.friends = acc_friends();
            SF.user = acc_user();
        }
        if (!SF.friends || !SF.user) {
            SF.friends = NULL; SF.user = NULL;
            SF.SetRichPresence = NULL; SF.ClearRichPresence = NULL;
            SF.RegisterCallback = NULL; SF.UnregisterCallback = NULL;
            SF.GetSteamID = NULL;
            coop_log("[steam] Friends/SteamUser/RegisterCallback exports incomplete -- invites disabled (non-fatal)\n");
        }
    }

    if (!ok) { memset(&SF, 0, sizeof(SF)); return 0; }

    SF.sockets = acc_sockets();
    SF.utils   = acc_utils();
    if (!SF.sockets || !SF.utils) {
        coop_log("[steam] accessor returned NULL (sockets=%p utils=%p)\n",
                 SF.sockets, SF.utils);
        memset(&SF, 0, sizeof(SF));
        return 0;
    }
    coop_log("[steam] flat API resolved (sockets=%p utils=%p)\n",
             SF.sockets, SF.utils);
    return 1;
}
