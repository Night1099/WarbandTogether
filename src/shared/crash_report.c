#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <psapi.h>
#include <string.h>
#include "crash_report.h"

/* ------------------------------------------------------------------ */
/*  Ring buffer                                                        */
/* ------------------------------------------------------------------ */

#define RING_SIZE      128
#define RING_ENTRY_LEN 256

static char          g_ring[RING_SIZE][RING_ENTRY_LEN];
static volatile LONG g_ring_head = 0;

void crash_ring_write(const char *msg) {
    LONG slot = InterlockedIncrement(&g_ring_head) - 1;
    char *dst = g_ring[slot & (RING_SIZE - 1)];
    lstrcpynA(dst, msg, RING_ENTRY_LEN);
}

/* ------------------------------------------------------------------ */
/*  State                                                              */
/* ------------------------------------------------------------------ */

static PVOID      g_veh_handle = NULL;
static HINSTANCE  g_dll_instance = NULL;
static coop_mode_t g_mode = COOP_HOST;
static volatile LONG g_crash_handling = 0;

/* Watchdog state */
static volatile LONG g_heartbeat = 0;
static HANDLE g_main_thread = NULL;
static HANDLE g_watchdog_thread = NULL;
static volatile LONG g_watchdog_running = 0;
#define WATCHDOG_INTERVAL_MS 5000
#define WATCHDOG_TIMEOUT_MS  10000

static LONG CALLBACK crash_veh_handler(PEXCEPTION_POINTERS pExInfo);
static void make_crash_path(char *buf, int buf_size, const char *ext);
static void write_minidump(PEXCEPTION_POINTERS pExInfo, const char *path);
static void write_text_report(PEXCEPTION_POINTERS pExInfo, const char *path,
                              const char *dmp_path);

/* ------------------------------------------------------------------ */
/*  Init / Shutdown                                                    */
/* ------------------------------------------------------------------ */

void crash_heartbeat(void) {
    InterlockedIncrement(&g_heartbeat);
}

static DWORD WINAPI watchdog_thread(LPVOID param) {
    LONG last_beat = 0;
    DWORD stale_ms = 0;
    (void)param;

    while (g_watchdog_running) {
        Sleep(WATCHDOG_INTERVAL_MS);
        if (!g_watchdog_running) break;

        if (g_heartbeat == 0) continue;

        if (g_heartbeat == last_beat) {
            stale_ms += WATCHDOG_INTERVAL_MS;
            if (stale_ms >= WATCHDOG_TIMEOUT_MS && g_main_thread) {
                char dmp_path[MAX_PATH];
                char txt_path[MAX_PATH];
                CONTEXT ctx;

                if (InterlockedCompareExchange(&g_crash_handling, 1, 0) != 0)
                    break;

                SuspendThread(g_main_thread);
                ctx.ContextFlags = CONTEXT_FULL;
                GetThreadContext(g_main_thread, &ctx);

                {
                    EXCEPTION_RECORD rec;
                    EXCEPTION_POINTERS ep;
                    memset(&rec, 0, sizeof(rec));
                    rec.ExceptionCode = 0xDEAD0001;
                    rec.ExceptionAddress = (PVOID)(DWORD_PTR)ctx.Eip;
                    ep.ExceptionRecord = &rec;
                    ep.ContextRecord = &ctx;

                    make_crash_path(dmp_path, MAX_PATH, ".dmp");
                    make_crash_path(txt_path, MAX_PATH, ".txt");
                    write_minidump(&ep, dmp_path);
                    write_text_report(&ep, txt_path, dmp_path);
                }
                { extern void coop_flush_log(void); coop_flush_log(); }

                ResumeThread(g_main_thread);
                g_crash_handling = 0;
                stale_ms = 0;
                last_beat = g_heartbeat;
            }
        } else {
            stale_ms = 0;
            last_beat = g_heartbeat;
        }
    }
    return 0;
}

void crash_init(HINSTANCE dll_instance, coop_mode_t mode) {
    ULONG stack_size = 32768;
    g_dll_instance = dll_instance;
    g_mode = mode;
    SetThreadStackGuarantee(&stack_size);
    g_veh_handle = AddVectoredExceptionHandler(1, crash_veh_handler);

    DuplicateHandle(GetCurrentProcess(), GetCurrentThread(),
                    GetCurrentProcess(), &g_main_thread,
                    THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT, FALSE, 0);
    g_watchdog_running = 1;
    g_watchdog_thread = CreateThread(NULL, 0, watchdog_thread, NULL, 0, NULL);
}

void crash_shutdown(void) {
    g_watchdog_running = 0;
    if (g_watchdog_thread) {
        WaitForSingleObject(g_watchdog_thread, WATCHDOG_INTERVAL_MS + 1000);
        CloseHandle(g_watchdog_thread);
        g_watchdog_thread = NULL;
    }
    if (g_main_thread) {
        CloseHandle(g_main_thread);
        g_main_thread = NULL;
    }
    if (g_veh_handle) {
        RemoveVectoredExceptionHandler(g_veh_handle);
        g_veh_handle = NULL;
    }
}

/* ------------------------------------------------------------------ */
/*  Output path helper                                                 */
/* ------------------------------------------------------------------ */

static void get_output_dir(char *buf, int buf_size) {
    char *slash;
    GetModuleFileNameA(g_dll_instance, buf, buf_size);
    slash = strrchr(buf, '\\');
    if (slash) slash[1] = '\0';
    else buf[0] = '\0';
}

static void make_crash_path(char *buf, int buf_size, const char *ext) {
    SYSTEMTIME st;
    char dir[MAX_PATH];
    GetLocalTime(&st);
    get_output_dir(dir, MAX_PATH);
    wsprintfA(buf, "%swarband_coop_crash_%04d%02d%02d_%02d%02d%02d%s",
              dir, st.wYear, st.wMonth, st.wDay,
              st.wHour, st.wMinute, st.wSecond, ext);
}

/* ------------------------------------------------------------------ */
/*  Minidump writer                                                    */
/* ------------------------------------------------------------------ */

typedef BOOL (WINAPI *MiniDumpWriteDump_t)(
    HANDLE hProcess, DWORD ProcessId, HANDLE hFile,
    DWORD DumpType, PVOID ExceptionParam,
    PVOID UserStreamParam, PVOID CallbackParam);

#pragma pack(push, 4)
typedef struct {
    DWORD  ThreadId;
    PEXCEPTION_POINTERS ExceptionPointers;
    BOOL   ClientPointers;
} MINI_EXCEPTION_INFO;
#pragma pack(pop)

#define MINI_WITH_DATA_SEGS   0x00000001
#define MINI_WITH_THREAD_INFO 0x00001000

static void write_minidump(PEXCEPTION_POINTERS pExInfo, const char *path) {
    HMODULE hDbgHelp;
    MiniDumpWriteDump_t pMiniDumpWriteDump;
    HANDLE hFile;
    MINI_EXCEPTION_INFO mei;

    hDbgHelp = LoadLibraryA("dbghelp.dll");
    if (!hDbgHelp) return;

    pMiniDumpWriteDump = (MiniDumpWriteDump_t)GetProcAddress(hDbgHelp, "MiniDumpWriteDump");
    if (!pMiniDumpWriteDump) { FreeLibrary(hDbgHelp); return; }

    hFile = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) { FreeLibrary(hDbgHelp); return; }

    mei.ThreadId = GetCurrentThreadId();
    mei.ExceptionPointers = pExInfo;
    mei.ClientPointers = FALSE;  /* in-process handler, not a debugger */

    pMiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(), hFile,
                       MINI_WITH_DATA_SEGS | MINI_WITH_THREAD_INFO,
                       &mei, NULL, NULL);

    CloseHandle(hFile);
    FreeLibrary(hDbgHelp);
}

/* ------------------------------------------------------------------ */
/*  Text crash report                                                  */
/* ------------------------------------------------------------------ */

static int safe_readable(const void *addr) {
    MEMORY_BASIC_INFORMATION mbi;
    if (!VirtualQuery(addr, &mbi, sizeof(mbi))) return 0;
    if (mbi.State != MEM_COMMIT) return 0;
    if (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)) return 0;
    return 1;
}

static void write_text_report(PEXCEPTION_POINTERS pExInfo, const char *path,
                              const char *dmp_path) {
    HANDLE hFile;
    char line[1024];
    int len;
    DWORD written;
    CONTEXT *ctx = pExInfo->ContextRecord;
    EXCEPTION_RECORD *rec = pExInfo->ExceptionRecord;
    SYSTEMTIME st;
    HMODULE mods[256];
    DWORD mod_bytes;
    int i, count, start;

    hFile = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                        FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) return;

#define EMIT(fmt, ...) do { \
    len = wsprintfA(line, fmt, __VA_ARGS__); \
    if (len > 0) WriteFile(hFile, line, len, &written, NULL); \
} while(0)
#define EMITS(s) WriteFile(hFile, s, lstrlenA(s), &written, NULL)

    /* Header */
    GetLocalTime(&st);
    EMIT("=== WARBAND CO-OP CRASH REPORT ===\r\nTimestamp: %04d-%02d-%02d %02d:%02d:%02d\r\n",
         st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
    EMIT("Mode: %s\r\n\r\n", g_mode == COOP_HOST ? "host" : "battle");

    /* Exception */
    EMITS("--- Exception ---\r\n");
    EMIT("Code: 0x%08X\r\nAddress: 0x%08X\r\n",
         rec->ExceptionCode, (DWORD)rec->ExceptionAddress);
    if (rec->ExceptionCode == EXCEPTION_ACCESS_VIOLATION &&
        rec->NumberParameters >= 2) {
        const char *op = rec->ExceptionInformation[0] == 0 ? "READ" :
                         rec->ExceptionInformation[0] == 1 ? "WRITE" : "DEP";
        EMIT("%s of 0x%08X\r\n", op, (DWORD)rec->ExceptionInformation[1]);
    }

    /* Registers */
    EMITS("\r\n--- Registers ---\r\n");
    EMIT("EAX=%08X EBX=%08X ECX=%08X EDX=%08X\r\n", ctx->Eax, ctx->Ebx, ctx->Ecx, ctx->Edx);
    EMIT("ESI=%08X EDI=%08X EBP=%08X ESP=%08X\r\n", ctx->Esi, ctx->Edi, ctx->Ebp, ctx->Esp);
    EMIT("EIP=%08X EFLAGS=%08X\r\n", ctx->Eip, ctx->EFlags);

    /* Stack */
    EMITS("\r\n--- Stack (top 64 dwords) ---\r\n");
    if (safe_readable((void *)ctx->Esp)) {
        DWORD *sp = (DWORD *)ctx->Esp;
        for (i = 0; i < 64; i += 4) {
            EMIT("%08X: %08X %08X %08X %08X\r\n",
                 (DWORD)(sp + i), sp[i], sp[i+1], sp[i+2], sp[i+3]);
        }
    } else {
        EMITS("(stack not readable)\r\n");
    }

    /* Modules */
    EMITS("\r\n--- Modules ---\r\n");
    if (K32EnumProcessModules(GetCurrentProcess(), mods, sizeof(mods), &mod_bytes)) {
        int nmod = mod_bytes / sizeof(HMODULE);
        for (i = 0; i < nmod && i < 256; i++) {
            MODULEINFO mi;
            char name[MAX_PATH];
            if (K32GetModuleInformation(GetCurrentProcess(), mods[i], &mi, sizeof(mi)) &&
                GetModuleFileNameExA(GetCurrentProcess(), mods[i], name, MAX_PATH)) {
                char *slash = strrchr(name, '\\');
                EMIT("%-30s base=%08X size=%08X\r\n",
                     slash ? slash + 1 : name, (DWORD)mi.lpBaseOfDll, mi.SizeOfImage);
            }
        }
    }

    /* Ring buffer */
    EMITS("\r\n--- Recent Log (oldest first) ---\r\n");
    count = g_ring_head < RING_SIZE ? g_ring_head : RING_SIZE;
    start = g_ring_head - count;
    for (i = 0; i < count; i++) {
        char *entry = g_ring[(start + i) & (RING_SIZE - 1)];
        if (entry[0]) {
            EMIT("[%3d] %s", i + 1, entry);
        }
    }

    /* Dump path */
    EMIT("\r\n--- Dump File ---\r\n%s\r\n", dmp_path);

#undef EMIT
#undef EMITS

    CloseHandle(hFile);
}

/* ------------------------------------------------------------------ */
/*  VEH Handler                                                        */
/* ------------------------------------------------------------------ */

static int is_fatal(DWORD code) {
    switch (code) {
    case EXCEPTION_ACCESS_VIOLATION:
    case EXCEPTION_STACK_OVERFLOW:
    case EXCEPTION_INT_DIVIDE_BY_ZERO:
    case EXCEPTION_ILLEGAL_INSTRUCTION:
    case EXCEPTION_ARRAY_BOUNDS_EXCEEDED:
    case EXCEPTION_FLT_DENORMAL_OPERAND:
    case EXCEPTION_FLT_DIVIDE_BY_ZERO:
    case EXCEPTION_FLT_INVALID_OPERATION:
    case EXCEPTION_FLT_OVERFLOW:
    case EXCEPTION_FLT_UNDERFLOW:
        return 1;
    default:
        return 0;
    }
}

static LONG CALLBACK crash_veh_handler(PEXCEPTION_POINTERS pExInfo) {
    if (!is_fatal(pExInfo->ExceptionRecord->ExceptionCode))
        return EXCEPTION_CONTINUE_SEARCH;

    if (InterlockedCompareExchange(&g_crash_handling, 1, 0) != 0)
        return EXCEPTION_CONTINUE_SEARCH;

    {
        char dmp_path[MAX_PATH];
        char txt_path[MAX_PATH];
        make_crash_path(dmp_path, MAX_PATH, ".dmp");
        make_crash_path(txt_path, MAX_PATH, ".txt");
        write_minidump(pExInfo, dmp_path);
        write_text_report(pExInfo, txt_path, dmp_path);
    }
    { extern void coop_flush_log(void); coop_flush_log(); }

    return EXCEPTION_CONTINUE_SEARCH;
}
