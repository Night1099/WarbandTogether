#include <windows.h>

extern "C" {
#include "coop_campaign.h"
#include "crash_report.h"
#include "module_dir.h"
}

static char g_dll_dir[MAX_PATH];

/* The winmm loader loads the plugin and WSE2 1.1.4.5 calls no plugin
   entry point, so everything starts and stops here. Hooks are memory
   patches, safe under the loader lock; ENet/Winsock init waits for the
   first framemove (WSAStartup is unreliable under the loader lock). */
BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);

        GetModuleFileNameA(hModule, g_dll_dir, MAX_PATH);
        module_dir(g_dll_dir);

        campaign_init_from_ini(g_dll_dir);
        crash_init((HINSTANCE)hModule, campaign_get_mode());
    }
    else if (reason == DLL_PROCESS_DETACH) {
        campaign_shutdown();
        crash_shutdown();
    }
    return TRUE;
}
