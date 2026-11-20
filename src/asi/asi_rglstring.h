/* asi_rglstring -- writes into the client engine's rglString objects.
 *
 * Layout (0x40 bytes): {cursor @0x00, buf @0x04, cap @0x08, len @0x0C,
 * SSO @0x10 (48 bytes)}. A string that grows past its SSO slot moves to a
 * heap buffer and never returns to the slot, so buf alone says whether the
 * engine has constructed the object.
 */

#ifndef COOP_ASI_RGLSTRING_H
#define COOP_ASI_RGLSTRING_H

#define RGLSTRING_SIZE    0x40
#define RGLSTRING_SSO_MAX 47   /* SSO capacity 48 minus the NUL */

/* Builds an SSO string in zeroed-out memory the caller owns (a browser row
   field). Values past 47 chars are cut to 47. */
void rglstring_init(char *rs, const char *value);

/* Rewrites an engine string register in place through its SSO slot, cut to
   47 chars. Re-points buf at the SSO slot even when the register had grown
   onto the heap. */
void rglstring_set_sso(char *rs, const char *value);

/* Copies value into the string's existing buffer when its capacity holds
   value plus the NUL, and sets len; buf is never re-pointed. Returns 1 when
   written, 0 (string untouched) when it does not fit. */
int rglstring_assign_in_place(char *rs, const char *value);

/* 1 once the engine's constructor has run (buf set, SSO or heap), 0 for
   static storage still zero. */
int rglstring_is_constructed(const char *rs);

#endif
