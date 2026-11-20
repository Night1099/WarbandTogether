/* local_result -- carries a local battle's result from the debrief menu to
 * the next campaign join.
 *
 * The debrief menu sets $g_coop_result_* (casualties packed troop * 1000 +
 * killed, at most 10) and $g_coop_result_ready = 1; flush writes them to
 * <game dir>/coop_local_result.ini. Module globals do not survive a server
 * join, so after the rejoin load copies the file into $g_coop_pending_* and
 * sets $g_coop_pending_local_result = 1; the module sends the result and
 * sets it to 2.
 */

#ifndef COOP_LOCAL_RESULT_H
#define COOP_LOCAL_RESULT_H

#define LOCAL_RESULT_FILENAME "coop_local_result.ini"
#define LOCAL_RESULT_MAX_CAS  10

/* variables.txt indices, -1 = unresolved. */
typedef struct local_result_src {
    int ready;        /* $g_coop_result_ready */
    int win_loss;
    int xp;
    int cas_count;
    int cas[LOCAL_RESULT_MAX_CAS];   /* $g_coop_result_cas_<i>, packed */
} local_result_src;

typedef struct local_result_dst {
    int pending;      /* $g_coop_pending_local_result: 0 none, 1 loaded, 2 sent */
    int win_loss;
    int xp;
    int cas_count;
    int cas_tid[LOCAL_RESULT_MAX_CAS];
    int cas_killed[LOCAL_RESULT_MAX_CAS];
} local_result_dst;

/* One-shot: when ready is 1, clears it and writes the result file. */
void local_result_flush(const local_result_src *gv, const char *game_dir);

/* While pending is 0 and the file holds a result, copies it into the
   pending globals, sets pending to 1 and deletes the file. */
void local_result_load(const local_result_dst *gv, const char *game_dir);

#endif
