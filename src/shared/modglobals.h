/* modglobals -- the single accessor + resolver for module-system globals.
 *
 * Module globals live in g_basicGame.m_globalVariables, an MSVC
 * std::vector<__int64> at a different address in each binary personality
 * (client, campaign dedicated, battle dedicated). modglobals_init() pins
 * the vector's _Myfirst/_Mylast pointer addresses once at startup -- the
 * caller passes them already ASLR-rebased -- and get/set re-read both
 * pointers on every call because the engine reallocates the vector
 * (mission restart). SEH guarding against the reallocation window stays
 * at hostile-context call sites (poll threads), not here.
 */

#ifndef COOP_MODGLOBALS_H
#define COOP_MODGLOBALS_H

typedef struct modglobals_desc {
    /* Absolute (rebased) addresses of the vector's _Myfirst and _Mylast
       pointer slots -- NOT the element storage itself. */
    unsigned int vec_first_addr;
    unsigned int vec_last_addr;
} modglobals_desc;

void modglobals_init(const modglobals_desc *desc);

/* One pass over variables.txt (one name per line, order == index):
   idx_out[i] = 0-based line number of names[i], or -1 if absent (logged).
   Indices shift on every module rebuild, so callers re-resolve each launch. */
void modglobals_resolve(const char *vars_path,
                        const char *const names[], int idx_out[], int n);

/* Bounds-checked element access. Return 1 on success; 0 when idx is
   unresolved (-1), the vector is down, or idx is past _Mylast. */
int modglobals_get(int idx, __int64 *out);
int modglobals_set(int idx, __int64 val);

/* Sugar over modglobals_get for the common int-with-fallback read. */
int modglobals_get_int(int idx, int fallback);

#endif
