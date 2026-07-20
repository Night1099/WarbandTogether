#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <string.h>
#include "wse_plugin.h"

extern "C" {
#include "coop_campaign.h"
#include "crash_report.h"
}

static HMODULE g_module = NULL;
static WSEEnvironment *g_env = NULL;
static char g_dll_dir[MAX_PATH];

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        g_module = hModule;
        DisableThreadLibraryCalls(hModule);

        /* Resolve DLL directory for INI loading */
        GetModuleFileNameA(hModule, g_dll_dir, MAX_PATH);
        char *slash = strrchr(g_dll_dir, '\\');
        if (slash) slash[1] = '\0';
        else g_dll_dir[0] = '\0';

        /* WSE2 1.1.4.5 dropped C++ plugin events, so we init via ASI loader.
           Hooks are installed here (just memory patching — safe in DllMain).
           ENet/Winsock init is deferred to first framemove (WSAStartup
           is unreliable under loader lock). */
        campaign_init_from_ini(g_dll_dir);
        crash_init((HINSTANCE)hModule, campaign_get_mode());
    }
    else if (reason == DLL_PROCESS_DETACH) {
        campaign_shutdown();
        crash_shutdown();
    }
    return TRUE;
}

static void plugin_load(void)
{
    OutputDebugStringA("[CoopWSE] plugin_load");
}

static void plugin_unload(void)
{
    OutputDebugStringA("[CoopWSE] plugin_unload");
}

static void plugin_event(void *context, WSEEvent event)
{
    (void)context;
    switch (event) {
    case WSE_EVENT_MODULE_LOAD:
        OutputDebugStringA("[CoopWSE] event: MODULE_LOAD");
        campaign_init_from_ini(g_dll_dir);
        crash_init((HINSTANCE)g_module, campaign_get_mode());
        break;

    case WSE_EVENT_GAME_LOAD:
        OutputDebugStringA("[CoopWSE] event: GAME_LOAD");
        break;

    case WSE_EVENT_FORCE_UNLOAD:
        OutputDebugStringA("[CoopWSE] event: FORCE_UNLOAD");
        campaign_shutdown();
        crash_shutdown();
        break;

    case WSE_EVENT_LOAD_OPERATIONS:
        OutputDebugStringA("[CoopWSE] event: LOAD_OPERATIONS");
        break;
    }
}

extern "C" __declspec(dllexport) int WSEPluginInit(int api_version, WSEPluginInfo *info, WSEEnvironment *env)
{
    if (api_version != WSE_PLUGIN_API_VERSION)
        return 0;

    memset(info, 0, sizeof(*info));
    strncpy(info->m_name,   "Coop Campaign & Battle Sync", sizeof(info->m_name) - 1);
    strncpy(info->m_author, "Ben",                          sizeof(info->m_author) - 1);
    info->m_wse_debug         = 0;
    info->m_wse_type          = 1;         /* 1 = Steam build */
    info->m_wse_version_major = 1;
    info->m_wse_version_minor = 1;
    info->m_version_major     = 2;
    info->m_version_minor     = 0;
    info->m_load_func         = plugin_load;
    info->m_unload_func       = plugin_unload;
    info->m_event_func        = plugin_event;

    g_env = env;
    return 1;
}
