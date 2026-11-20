#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "loader_path.h"
#include "module_dir.h"

void loader_plugin_path(char *exe_path) {
    module_dir(exe_path);
    lstrcatA(exe_path, "CoopWSEPlugin.dll");
}
