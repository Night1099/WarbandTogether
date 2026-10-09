# v0.0.82

Release notes for WarbandTogether v0.0.82: everything committed on the
Workbench `main` since the v0.0.8 sync (`b620aea`). Everything under
Fixed and Added has been runtime-verified by the maintainer. Code listed
under **Future release** ships in this build too, but it is not verified
yet; treat it as a preview that may not work.

## Read this first: the campaign world is saved now

The campaign server keeps its world between runs (see Added). It loads
`sg00.sav` from
`Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames\` every time it
starts, and a missing file starts a fresh world. **If that file was
written by an older build, delete or move it before you launch this
one**: a world saved by an older module may not load correctly. Before
you close the campaign server window, type `campaign_save` in it, or wait
for `[WORLD SAVE] finished` after the last player has left. Otherwise
everything since the last save is lost. The install guide (Step 3)
covers this.

## Fixed

- **Merchants had no gold, so you could not sell to them** (`a3f8250`;
  verified 2026-10-04). A weaponsmith, armorer, horse or goods merchant
  opened from the town's marketplace showed 0 gold, so nothing could be
  sold. The server now sends each merchant's real gold with their stock,
  moves it the opposite way to yours when you trade, and caps a sale at
  what the merchant can pay. The merchants you walk up to in a town
  visit trade with their real gold too.
- **A rejoin could hand you the previous player's character** (`9986705`;
  verified 2026-10-09 with two players rejoining in the opposite order:
  each got their own name, stats, equipment and gold back). Player
  characters are bound to a player slot, and loading a saved character
  only raised stats and filled item slots, so whoever joined into a slot
  another player had used could keep that player's higher stats and
  items.

## Added

- **The campaign world is saved and loaded** (verified 2026-10-09). The
  world (date, parties, towns, the merchants' stock and gold) is saved
  every 20 real minutes while a player is online, when the last player
  leaves, and whenever the host types `campaign_save` in the campaign
  server window (`[WORLD SAVE] requested` / `finished, slot 0` on the
  console). The next start continues it: you rejoin where you were, the
  date is the saved one, and a battle that was on the map can be fought
  again. Saving does not interrupt a running dedicated battle. The
  debug launcher keeps its own world in `sg01.sav` and saves it every
  5 real minutes, so testing never touches the real one.
- **Weekly wages** (verified 2026-10-03/04/09). Every player pays their
  own party once a week from their own purse, at native's per-troop rates
  (mounted, mercenaries and companions cost more; leadership lowers
  it). The client prints native's payday line, and the "View weekly
  budget report" lists your party. A payday you cannot afford is paid as
  far as your gold goes, and the rest becomes debt that the next payday
  settles. Waiting inside a town halves that day's wages, as in
  singleplayer. Only time you are online counts: a week is about 11 real
  minutes of play, and nothing is charged for the time you are away.
- **Enemy towns and castles turn you away** (verified 2026-10-03/09).
  Riding into a town or castle of a kingdom at war with the players gives
  native's "The town guards are on the lookout for intruders" menu with
  Lay siege, Lead the assault yourself (local) and Leave. No
  marketplace, no walk-around. Villages and friendly centers open as
  before, and the refusal still applies after a rejoin. A siege request
  now needs you to actually be at that center.
- **Debug launcher: Ctrl + V declares war.** With
  `coop_launch_all_debug.bat`, pressing Ctrl + V on the map makes the
  Kingdom of Vaegirs declare war on the players, so the enemy-town
  refusal can be tested without a long campaign.

## Changed

- The `[Coop] ModuleLabel` key is gone from `coop.ini`; it never did
  anything. An old `coop.ini` that still has it keeps working.
- A dedicated siege request is only accepted while your party is at
  that center (not yet exercised in a test).
- The night-bandit infestation messages are back to singleplayer's
  cheat-mode only, and the campaign server console prints a line when a
  siege starts.

## Future release

In this build but not verified yet. Expect these to change; report what
you see.

- **Players inside a besieged castle keep their troops** (`0598d3b`; not
  yet verified). The engine resolves AI battles on the map by itself and
  could take casualties from a player party sitting inside a castle that
  was being assaulted, with no menu. A simulated battle now waits while a
  player is in either side. This is a stopgap until defending a
  besieged center is ported.
- **A loaded character matches its save exactly** (`9986705`; not yet
  verified beyond the two-player rejoin above). A load now lowers stats
  that are higher than the save and empties item slots the save has
  empty; experience and level after a lowered stat follow the saved
  experience.
- Everything listed under "Future release" in the v0.0.8 notes is still
  unverified: the campaign-server crash on join, encounters arriving
  while a screen is open, bought items keeping their drop slot, center
  immunity, per-player relations, companion recruiting, books and
  ransoms, and the unverified quests. "Wait here for some time." was
  used through several game days in the wages test (2026-10-03) and
  works.

## Known issues

### Joining a dedicated battle on a passworded server

With `Password=` set in `coop.ini`, a joining player can enter the
campaign server, but the hop to a dedicated battle drops them to the
multiplayer server list. The host's own hop into the battle works, but
the host's automatic return to the campaign server afterwards may time
out (rejoin from the server list). Until this is fixed, leave
`Password=` empty if other players will fight dedicated battles.

### Village elders' gold

A village elder starts with 0 gold, as in a new singleplayer game, but
selling to an elder does not raise his gold yet.

### Mayors keep offering the caravan escort

Unchanged from v0.0.8: every mayor quest you finish or drop is not
offered again for 20-30 game days (30-50 minutes of play), except the
caravan escort, so once you have done the rest every mayor offers the
caravan until their waits run out.

### Joiners with the default HostIP

A client whose `coop.ini` still has `HostIP=127.0.0.1` can see the
campaign server and the battle list, but the battle click drops to the
multiplayer main menu because the battle connect targets its own
machine. Set `HostIP` to the host's LAN address.

### Enemy towns look neutral on the map

Faction relations are not sent to clients yet, so after a war starts the
map tooltip still shows that kingdom's towns as neutral. The towns still
refuse you.
