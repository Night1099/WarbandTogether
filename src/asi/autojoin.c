#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include "autojoin.h"
#include "steam_tunnel.h"
#include "warband_addrs_wse2.h"

extern void coop_log(const char *fmt, ...);

static void autojoin_clear_engine_flags(const autojoin_env *env) {
    /* m_connectToServer must be cleared by us in BOTH exits: the initial
       menu's native clear is our own 7-NOP "opcode 3415 fix", so a stale 1
       bounces the player into the browser on every main-menu visit; and a
       stale m_switchingModule auto-connects on their next manual browser
       visit (row-0 mismatch never clears it). */
    *env->switching_module      = 0;
    *env->switching_to_campaign = 0;
    *env->connect_to_server     = 0;
}

static void autojoin_abandon(autojoin *st, const autojoin_env *env) {
    autojoin_clear_engine_flags(env);
    steam_tunnel_autojoin_clear();
    st->active = 0;
}

static void autojoin_arm(autojoin *st, const autojoin_env *env, int kind) {
    /* Replicate opcode 3415's stores (RE Q5). Address = the s59 thread's
       re-aimed host IP (loopback while the tunnel is up) with the explicit
       port -- the type-4 direct search would default a bare IP to
       rglConfig's iServerPort, which is user-editable (RE round 2).
       Password = our own [Coop] Password= (empty for open servers; the
       pw-without-local-password case never arms -- verdict 0).
       m_switchingToCampaign makes the starting/map/tactical native arms
       pick loading mode 6, whose doStep writes m_gameType = 4 -- with any
       other gameType the engine DROPS the campaign server's ping reply and
       the row table stays empty. rglString::operator= is safe here: this
       IS the render thread. */
    char host_addr[80];
    _snprintf(host_addr, sizeof(host_addr), "%s:%d", env->host_ip, env->port);
    host_addr[sizeof(host_addr) - 1] = '\0';
    env->rgl_copy(env->stored_address, host_addr);
    env->rgl_copy(env->stored_password, env->password);
    /* m_connectToServer is deliberately NOT set here: it is a pure
       navigation trigger, and the same-frame window dispatch would let the
       main menu's native arm consume it first -- that arm hardcodes loading
       mode 4, whose frameMove writes m_gameType=1, under which the engine
       drops the campaign server's ping reply (runtime-proven). All
       menu-screen navigation is ours (mode 6); the flag is set just-in-time
       for the WAIT_NATIVE contexts below, whose map/tactical arms are the
       ones that need it. */
    *env->switching_module      = 1;
    *env->switching_to_campaign = 1;
    st->arm_tick = env->now;
    st->active = kind;
    st->navs = 0;
    coop_log("[autojoin] engine flags set -- address=%s (%s)\n", host_addr,
             kind == STEAM_AUTOJOIN_LOCAL ? "own server, LAN" : "tunnel");
}

void autojoin_step(autojoin *st, const autojoin_env *env) {
    int action;

    if (!st->active) {
        int kind = steam_tunnel_autojoin_armed();
        if (!kind) return;
        if (kind == STEAM_AUTOJOIN_TUNNEL && !env->tunnel_up) {
            steam_tunnel_autojoin_clear();   /* tunnel died between arm and fire */
            return;
        }
        autojoin_arm(st, env, kind);
        return;
    }

    /* The engine clears m_switchingModule on connect and on every connect()
       rejection -- either way the arm is spent. */
    if (*env->switching_module == 0) {
        autojoin_abandon(st, env);
        coop_log("[autojoin] consumed by engine -- flags cleared\n");
        return;
    }

    if (env->now - st->arm_tick > AUTOJOIN_TIMEOUT_MS ||
        (st->active == STEAM_AUTOJOIN_TUNNEL && !env->tunnel_up)) {
        autojoin_abandon(st, env);
        coop_log("[autojoin] timed out or tunnel down -- flags cleared; COOP Direct row remains in the browser\n");
        return;
    }

    /* Dead-zone screens: the flag-consuming windows self-navigate (SELF)
       and a live mission / buried campaign map must not be yanked (WAIT) --
       force navigation only from screens nothing else covers. Recipe lifted
       from mbStartingWindow::frameMove (mode 6 skips the m_switchingModule
       requirement in the loading window's MP arm). */
    if (!env->open_windows || env->n_open_windows <= 0) return;
    action = steam_autojoin_window_action(env->open_windows, env->n_open_windows);
    if (action == STEAM_AJ_WAIT_NATIVE) {
        /* Map / live mission: the native arms own the transition (the map
           joins the network thread; tactical waits for mission end). Both
           pick loading mode 6 via m_switchingToCampaign. Idempotent re-set;
           the consuming arm clears it. */
        *env->connect_to_server = 1;
        return;
    }
    if (action != STEAM_AJ_NAVIGATE) return;
    if (!env->loading_window) return;
    /* No MP profile makes loading mode 6 fall through to the profiles
       window, which we would re-navigate forever -- cap the loop and leave
       the player where the engine put them. */
    if (st->navs >= AUTOJOIN_MAX_NAVS) {
        autojoin_abandon(st, env);
        coop_log("[autojoin] navigation not sticking (no MP profile?) -- flags cleared\n");
        return;
    }
    st->navs++;
    *(int *)(env->loading_window + LOADING_WINDOW_SOURCE_OFF) = 4;   /* back target: main menu */
    *(int *)(env->loading_window + LOADING_WINDOW_MODE_OFF)   = 6;
    *(int *)(env->loading_window + LOADING_WINDOW_STEP_OFF)   = 0;
    env->set_window(3);
    coop_log("[autojoin] navigating to MP browser (loading mode 6, attempt %d)\n", st->navs);
}
