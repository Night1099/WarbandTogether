/* loader_path -- where the winmm loader finds the plugin. */

#ifndef LOADER_PATH_H
#define LOADER_PATH_H

/* Rewrites exe_path (MAX_PATH buffer) in place into the path of
   CoopWSEPlugin.dll in the exe's own folder. */
void loader_plugin_path(char *exe_path);

#endif
