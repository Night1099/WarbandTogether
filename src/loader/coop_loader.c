#define WIN32_LEAN_AND_MEAN
#include <windows.h>

/* Minimal winmm.dll proxy — all 180 exports forwarded to winmm_sys.dll
   via linker /EXPORT:name=winmm_sys.name (no runtime LoadLibrary).
   Only job: load CoopWSEPlugin.dll from a background thread. */

static HMODULE g_plugin = NULL;

static DWORD WINAPI loader_thread(LPVOID param) {
    char path[MAX_PATH];
    (void)param;

    /* Load-bearing gate: the plugin is dedicated-server-only (since B8
       it has no client code at all); game clients use warband_coop.asi.
       This check is what keeps CoopWSEPlugin.dll out of every player
       client that ships the same winmm proxy on disk. */
    GetModuleFileNameA(NULL, path, MAX_PATH);
    if (!strstr(path, "dedicated")) return 0;

    Sleep(3000);
    { char *s = strrchr(path, '\\'); if (s) s[1] = '\0'; }
    lstrcatA(path, "CoopWSEPlugin.dll");
    g_plugin = LoadLibraryA(path);
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID reserved) {
    (void)hModule; (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        CreateThread(NULL, 0, loader_thread, NULL, 0, NULL);
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_plugin) FreeLibrary(g_plugin);
    }
    return TRUE;
}
