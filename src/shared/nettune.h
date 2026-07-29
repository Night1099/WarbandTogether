/* Runtime engine-constant patcher (TRAFFIC_OPTIMIZATION R2-R4).
 * Table-driven: each site names one 32-bit engine value (imm operand or
 * data dword). Writes happen only when the current value matches the
 * documented stock value -- a mismatch means the binary drifted from the
 * 1145 pin, so the site is skipped and logged, never corrupted. */
#ifndef NETTUNE_H
#define NETTUNE_H

typedef struct nettune_site {
    const char *name;   /* log label */
    void       *addr;   /* byte address of the 32-bit value */
    unsigned    stock;  /* expected current bits (imm32, or float bits) */
    unsigned    tuned;  /* bits to write; tuned==stock means leave stock */
} nettune_site;

/* Verify-and-write each site. Returns the number of sites written. */
int nettune_apply_table(nettune_site *sites, int count);

/* Clamp an ini knob to [lo, hi], logging when it fires. Negative ini
 * values wrap to huge unsigneds and land on hi. */
unsigned nettune_clamp(const char *name, unsigned v, unsigned lo, unsigned hi);

/* Production entry: read [NetTuning] from ini_path, build the per-mode
 * site table, apply it. is_battle selects the battle-exe address set. */
void nettune_apply(int is_battle, const char *ini_path);

#endif
