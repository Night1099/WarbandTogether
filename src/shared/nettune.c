#include <windows.h>
#include <string.h>
#include "nettune.h"
#include "warband_addrs_wse2.h"

void coop_log(const char *fmt, ...); /* host DLL logger (stubbed in tests) */

int nettune_apply_table(nettune_site *sites, int count) {
    int i, applied = 0;
    for (i = 0; i < count; i++) {
        nettune_site *s = &sites[i];
        unsigned cur;
        DWORD old;
        memcpy(&cur, s->addr, 4);
        if (cur != s->stock) {
            coop_log("[nettune] SKIP %s: expected 0x%08X found 0x%08X\n",
                     s->name, s->stock, cur);
            continue;
        }
        if (s->tuned == s->stock) {
            coop_log("[nettune] %s: stock 0x%08X (no write)\n", s->name, s->stock);
            continue;
        }
        /* EXECUTE_READWRITE, not READWRITE: engine threads keep executing
         * this .text page during the write window (DEP would fault them). */
        if (!VirtualProtect(s->addr, 4, PAGE_EXECUTE_READWRITE, &old)) {
            coop_log("[nettune] SKIP %s: VirtualProtect failed\n", s->name);
            continue;
        }
        memcpy(s->addr, &s->tuned, 4);
        VirtualProtect(s->addr, 4, old, &old);
        FlushInstructionCache(GetCurrentProcess(), s->addr, 4);
        coop_log("[nettune] %s: 0x%08X -> 0x%08X\n", s->name, s->stock, s->tuned);
        applied++;
    }
    return applied;
}

unsigned nettune_clamp(const char *name, unsigned v, unsigned lo, unsigned hi) {
    unsigned c = v;
    if (c < lo) c = lo;
    if (c > hi) c = hi;
    if (c != v)
        coop_log("[nettune] CLAMP %s: %u -> %u\n", name, v, c);
    return c;
}

static unsigned float_bits(float f) {
    unsigned u;
    memcpy(&u, &f, 4);
    return u;
}

void nettune_apply(int is_battle, const char *ini_path) {
    unsigned floor_v = GetPrivateProfileIntA("NetTuning", "AimdFloor", 16000, ini_path);
    unsigned step_v  = GetPrivateProfileIntA("NetTuning", "AimdStep",   8000, ini_path);
    unsigned pmax_v  = GetPrivateProfileIntA("NetTuning", "PacketMaxSize", 1350, ini_path);
    unsigned hz_v    = GetPrivateProfileIntA("NetTuning", "SendRateHz", 30, ini_path);
    /* SendRateHz needs no clamp: it only selects between two known-good
       bit patterns below, so no ini value can write out-of-range bits. */
    floor_v = nettune_clamp("AimdFloor", floor_v, 3000, 128000);
    step_v  = nettune_clamp("AimdStep",  step_v,  1000, 32000);
    pmax_v  = nettune_clamp("PacketMaxSize", pmax_v, 576, 1450);
    nettune_site sites[4];
    int n = 0;

    /* Site addresses are preferred-base VAs (see warband_addrs_wse2.h) --
       rebase by the same g_aslr_slide the plugin's own hooks use, or every
       verify-read below hits unrelated memory and SKIPs. */
    if (is_battle) {
        sites[n].name = "aimd_step";  sites[n].addr = (void *)REBASE(DED_NT_AIMD_STEP);
        sites[n].stock = 1000;  sites[n].tuned = step_v;  n++;
        sites[n].name = "aimd_floor"; sites[n].addr = (void *)REBASE(DED_NT_AIMD_FLOOR);
        sites[n].stock = 3000;  sites[n].tuned = floor_v; n++;
        sites[n].name = "pkt_max";    sites[n].addr = (void *)REBASE(DED_NT_PKT_MAX);
        sites[n].stock = 1350;  sites[n].tuned = pmax_v;  n++;
    } else {
        sites[n].name = "aimd_step";  sites[n].addr = (void *)REBASE(CAMP_NT_AIMD_STEP);
        sites[n].stock = 1000;  sites[n].tuned = step_v;  n++;
        sites[n].name = "aimd_floor"; sites[n].addr = (void *)REBASE(CAMP_NT_AIMD_FLOOR);
        sites[n].stock = 3000;  sites[n].tuned = floor_v; n++;
        sites[n].name = "pkt_max";    sites[n].addr = (void *)REBASE(CAMP_NT_PKT_MAX);
        sites[n].stock = 1350;  sites[n].tuned = pmax_v;  n++;
        /* The exe's .rdata dword is 0x3D088888 (Task 1 findings, "nettune
           patch sites (2026-07-25)": stock bytes "88 88 08 3D" @0x887BC0).
           The 0.033333335f literal rounds to 0x3D088889 under MSVC -- one
           ULP off -- so the stock check must use the raw bit pattern, not
           float_bits() on the source literal, or verify always mismatches
           and the SendRateHz knob can never apply. */
        sites[n].name = "send_period"; sites[n].addr = (void *)REBASE(CAMP_NT_SEND_PERIOD);
        sites[n].stock = 0x3D088888u;
        sites[n].tuned = (hz_v >= 62) ? float_bits(0.016f) : 0x3D088888u;
        n++;
    }
    nettune_apply_table(sites, n);
}
