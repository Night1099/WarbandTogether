/* asi_patch -- verify-before-write patches of client engine code.
 *
 * A patch site is written only when its stock bytes are still there: an
 * address that accepts a write proves nothing (project-state Key Lesson
 * "Verify hook prologue bytes").
 */

#ifndef COOP_ASI_PATCH_H
#define COOP_ASI_PATCH_H

/* Makes the larger of the two spans writable, and when addr starts with
   expect[0..n_expect) writes repl[0..n_repl); the page protection is
   restored either way. Returns 1 when patched, 0 when the bytes did not
   match (nothing written). */
int asi_patch_verified(unsigned char *addr, const unsigned char *expect, int n_expect,
                       const unsigned char *repl, int n_repl);

#endif
