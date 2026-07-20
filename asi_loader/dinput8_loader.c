#define WIN32_LEAN_AND_MEAN
#include <windows.h>

/* Real dinput8.dll handle and function pointer */
static HMODULE g_realDinput8 = NULL;

typedef HRESULT (WINAPI *DirectInput8Create_t)(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf,
    LPVOID *ppvOut, LPVOID punkOuter);

static DirectInput8Create_t g_realDirectInput8Create = NULL;

/* Forwarded export */
__declspec(dllexport) HRESULT WINAPI DirectInput8Create(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf,
    LPVOID *ppvOut, LPVOID punkOuter)
{
    if (!g_realDirectInput8Create) return E_FAIL;
    return g_realDirectInput8Create(hinst, dwVersion, riidltf, ppvOut, punkOuter);
}

static void load_real_dinput8(void) {
    char sysdir[MAX_PATH];
    char path[MAX_PATH];
    GetSystemDirectoryA(sysdir, MAX_PATH);
    wsprintfA(path, "%s\\dinput8.dll", sysdir);
    g_realDinput8 = LoadLibraryA(path);
    if (g_realDinput8) {
        g_realDirectInput8Create = (DirectInput8Create_t)
            GetProcAddress(g_realDinput8, "DirectInput8Create");
    }
}

static void load_asi_plugins(void) {
    WIN32_FIND_DATAA fd;
    HANDLE hFind;
    char fpu_state[512];  /* FXSAVE needs 512 bytes, 16-byte aligned */
    char *fpu_buf;

    hFind = FindFirstFileA("*.asi", &fd);
    if (hFind == INVALID_HANDLE_VALUE) return;

    /* Align buffer to 16 bytes for FXSAVE */
    fpu_buf = (char *)(((DWORD)fpu_state + 15) & ~15);

    do {
        /* Save FULL FPU + SSE state — ASI CRT init corrupts it */
        __asm {
            mov eax, [fpu_buf]
            fxsave [eax]
        }
        LoadLibraryA(fd.cFileName);
        __asm {
            mov eax, [fpu_buf]
            fxrstor [eax]
        }
    } while (FindNextFileA(hFind, &fd));

    FindClose(hFind);
}

BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hinstDLL);
        load_real_dinput8();
        load_asi_plugins();
    }
    else if (fdwReason == DLL_PROCESS_DETACH) {
        if (g_realDinput8) FreeLibrary(g_realDinput8);
    }
    return TRUE;
}
