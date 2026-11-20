/* module_dir -- the folder of a module or exe path.
 *
 * Everything that finds a file beside a module cuts its
 * GetModuleFileName path here: the plugin's coop.ini and crash reports,
 * the loader's plugin, the game's Modules\ and WSE\ folders. The folder
 * keeps its trailing backslash, so a file name appends directly. A path
 * with no backslash has no folder and becomes "".
 */

#ifndef MODULE_DIR_H
#define MODULE_DIR_H

/* Cuts path in place after its last backslash. */
void module_dir(char *path);

#endif
