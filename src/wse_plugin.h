#pragma once

/* WSE2 plugin ABI — stable across WSE2 versions, derived from WSE1 (lennyhans/warband-script-enhancer) */

#define WSE_PLUGIN_API_VERSION 2

#ifdef __cplusplus
extern "C" {
#endif

typedef struct WSEEnvironment WSEEnvironment;

typedef enum {
    WSE_EVENT_FORCE_UNLOAD   = 0,
    WSE_EVENT_LOAD_OPERATIONS = 1,
    WSE_EVENT_MODULE_LOAD    = 2,
    WSE_EVENT_GAME_LOAD      = 3,
} WSEEvent;

typedef void (*WSEPluginLoadFunc)(void);
typedef void (*WSEPluginUnloadFunc)(void);
typedef void (*WSEPluginEventFunc)(void *context, WSEEvent event);

typedef struct {
    char m_name[256];
    char m_author[256];
    int m_wse_debug;
    int m_wse_type;
    int m_wse_version_major;
    int m_wse_version_minor;
    int m_version_major;
    int m_version_minor;
    WSEPluginLoadFunc  m_load_func;
    WSEPluginUnloadFunc m_unload_func;
    WSEPluginEventFunc m_event_func;
} WSEPluginInfo;

__declspec(dllexport) int WSEPluginInit(int api_version, WSEPluginInfo *info, WSEEnvironment *env);

#ifdef __cplusplus
}
#endif
