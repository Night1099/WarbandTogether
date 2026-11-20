/* coop_config -- the plugin's startup settings and game-directory paths.
 *
 * Personality comes from the exe (exe_personality.h). A battle
 * server's pool slot comes from COOP_BATTLE_SLOT; the campaign server's
 * debug reveal from COOP_DEBUG_REVEAL (debug launcher only).
 */

#ifndef COOP_CONFIG_H
#define COOP_CONFIG_H

#include "coop_campaign.h"

/* value: the environment variable's text, NULL when it is not set. */
int coop_battle_slot_from_env(const char *value);
int coop_debug_reveal_from_env(const char *value);

/* <exe dir>\Modules\<module>\variables.txt */
void coop_variables_path(char *out, int out_size, const char *exe_path, const char *module);
/* <exe dir>\WSE\<module>\ -- where the engine's dict_* operations read and write */
void coop_wse_dict_dir(char *out, int out_size, const char *exe_path, const char *module);

/* Write this personality's server config dict into dict_dir (which ends in
 * a backslash). One file per personality: every server in a pool writes its
 * own environment (debug reveal is campaign-only), so a shared file would let
 * the last writer decide another process's setting. File name and keys are
 * spelled the way the engine resolves the module's quick strings: every '_'
 * in an "@name" string becomes ' ' when quick_strings.txt is loaded, so
 * coop_apply_server_cfg opens "coop server cfg campaign" and reads
 * "server password". Returns 0 on success, -1 on failure. */
int coop_write_server_cfg(const char *dict_dir, coop_mode_t mode,
                          const char *password, int debug_reveal);

#endif
