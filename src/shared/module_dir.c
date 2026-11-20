#include <string.h>

#include "module_dir.h"

void module_dir(char *path) {
    char *slash = strrchr(path, '\\');
    if (slash) slash[1] = '\0';
    else path[0] = '\0';
}
