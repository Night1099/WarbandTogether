/* asi_publish -- the values the client ASI's 500 ms thread publishes.
 *
 * The thread re-aims the campaign address at the Steam tunnel, republishes
 * the Steam account id into a module global (the engine wipes module
 * globals on every connect), and arms the post-battle return hop once per
 * "battle over" signal.
 */

#ifndef COOP_ASI_PUBLISH_H
#define COOP_ASI_PUBLISH_H

#define ASI_LOOPBACK_IP "127.0.0.1"

/* Swaps ip to loopback when the Steam client proxy comes up and back to
   lan when it goes down; *reaimed holds the state last applied. Returns 1
   when ip was rewritten, 0 when up already matched (nothing written). */
int host_ip_reaim(int *reaimed, int up, char *ip, int size, const char *lan);

/* $g_coop_my_steam_acctid: the account id zero-extended to 64 bits, or -1
   while Steam has none, which lets the module identify by username at
   once. */
__int64 acctid_global_value(unsigned int acctid);

/* $g_coop_return_to_campaign stays 1 until the engine wipes it on the
   reconnect the return hop causes. Returns 1 (arm the hop) on the first
   tick it reads 1; a tick that reads anything else re-arms the latch. */
int return_latch_step(int *latched, int value);

#endif
