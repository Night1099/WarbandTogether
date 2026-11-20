/* exe_personality -- which coop role a process plays, from its exe.
 *
 * The plugin belongs only in dedicated exes: dedicated_campaign is the
 * campaign server (COOP_HOST), any other dedicated exe a battle server.
 * Only the file name counts; the folders above it never decide (a client
 * installed under a folder called "dedicated" stays a client).
 * The winmm loader and the plugin both decide with these functions, so a
 * process the loader refuses is one the plugin would also stay inert in.
 */

#ifndef EXE_PERSONALITY_H
#define EXE_PERSONALITY_H

typedef enum { COOP_HOST, COOP_BATTLE } coop_mode_t;

int         coop_is_dedicated_exe(const char *exe_path);
coop_mode_t coop_mode_from_exe(const char *exe_path);

#endif
