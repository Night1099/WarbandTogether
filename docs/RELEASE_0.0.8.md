# v0.0.8

Release notes for WarbandTogether v0.0.8: everything committed on the
Workbench `main` since the v0.0.71 sync (`8784a7a`). Everything under
Fixed and Added has been runtime-verified by the maintainer. Code listed
under **Future release** ships in this build too, but it is not verified
yet, or not finished; treat it as a preview that may not work.

## Fixed

- **The server password and the debug map reveal never applied.** The
  host plugin wrote its config dict as `coop_server_cfg_campaign.wsedict`
  with the keys `server_password` and `debug_reveal`, but the engine
  turns every underscore in a module string into a space when it loads
  the module, so the campaign server looked for `coop server cfg
  campaign.wsedict` and never found it. `[Coop] Password=` was silently
  ignored on both server personalities, and `coop_launch_all_debug.bat`
  left fog of war on. The plugin now writes the names the module reads.
  If you had `Password=` set, your server is passworded from this
  release on. Verified 2026-09-24 (debug launcher: the campaign server
  reads `debug reveal 1` with a player connected, and the map is
  revealed).
- **Rejoining after a conversation loaded a different character.** After
  talking to anyone in a lord's hall (or any scene), the next reconnect
  to the campaign server could hydrate a fresh username-keyed character
  at a different map spot instead of your Steam-keyed one, and everything
  you did afterwards (relations, XP, saves) landed on that stray
  character. The client add-on's 500 ms publisher, which hands your Steam
  account id to the module for the identify message, waited for string
  register 0 to be "initialised" by checking that it still used its
  inline buffer; the first 48+ character string a script stored there
  moved it to the heap for good, and from then on every publish was
  skipped for the rest of the process. The server never received a
  Steam id and fell back to username keying. The publisher now only
  waits for the register table to exist. The server log also gains
  `[IDENT] player N acctid=X` and `[HYDRATE] player N via timeout` lines
  so a wrong-key hydrate is visible at once. Verified 2026-09-22 (lord
  conversation, exit, rejoin identified with the real account id and
  loaded the Steam-keyed character).
- **Castles reported "another player is already visiting"** and left
  the party stuck on the castle, while towns and villages worked. The
  quest-offer push added with quest sync treated a center without a
  mayor or elder as a failure, and in the module system a failing step
  inside the server's enter branch falls through into the locked branch,
  so the server locked the castle for you and then told you it was
  taken. The locked reply is now only sent when the lock check itself
  says so, and the offer push is a no-op for castles. Verified
  2026-09-21.
- **Stuck in a battle with no popup after a rejoin** (`92f54ec`;
  verified 2026-09-23). On a rejoin the server put your party back on
  the map where it had last been parked, a moment before it moved it to
  your saved position. Anything hostile nearby could attack it in that
  moment; the battle message reached a client that was not ready for
  it, so no menu opened, and the party stayed stuck in that battle after
  moving back. The party now appears on the map only once your
  character has loaded, already at its saved position.
- **Client crash inside a town visit** (`6f5d3f0`). A client could crash
  during a "Walk around the town" visit, in the engine's party
  replication receive path: a position update for a party the client
  had never been told about was applied to a bad pointer. The client
  add-on now skips such an update and logs `replication row N for
  missing party M skipped` in `warband_coop.log`. Verified 2026-09-23:
  no crash in visits and lord battles.
- **Vestigial `set_steam_port` removed from battle-server configs**
  (`e0ac858`). The dedicated engine never recognised it. The firewall
  range in the install docs narrows to the ports actually used,
  7240-7247.
- Inventory sync: bag-capacity clamp, async-push mirror guard, fast-reopen
  flush, equip slot 9 persistence, `inv_change` item validation
  (diagnosed by Sirparabaran in WarbandTogether PR #1; hand-ported;
  `de99f67`, `adef0f9`, `0ec78f0`, `332ecfb`, `872353d`, `7f7e6e8`,
  `636da0d`, `6368c97`; runtime-verified 2026-09-18).
- Build: `build_module.bat` now stops at the first failing step; pytest
  checks network send arity and payload width (`fb92baf`, `5494437`,
  `dd6a68c`, `f5ea26b`; verified in-session: injected build error stops
  the chain, both tests failed red on real bugs before their fixes).
- **Walking around a town, village, or castle no longer freezes you in a
  T-pose** (`294824b`, verified 2026-09-19). The three visit entries started
  the scene without asking the client ASI to run it as a single-player
  mission, so the engine treated your agent as a remote player waiting
  for a server that never came: no controls, no animation, no NPC AI.
  The visit entries now make the same request the local fight does, and
  the ASI fills in the encounter record for a peaceful visit instead of
  a battle. Root cause matches what Sirparabaran found in WarbandTogether
  PR #1; the fix was re-derived against the engine here. The center's
  people arrive with the visit roster push (see Added).
- **Leaving a visit rejoins the campaign server automatically**
  (`4676755`, verified 2026-09-19). Ending any mission on a campaign client drops the
  connection and lands you in the server browser. Visits now arm the same
  auto-return the dedicated battles use, so you are back on the map
  without clicking the server row.
- **Quest fixes found on the first gate run** (`18b8381`, `cbcf5b5`;
  verified 2026-09-20/21). The coop center menu no longer reports
  `Invalid Player ID: -1` when it opens mid-rejoin, and a client whose
  quest is already active advances it in place instead of rebuilding it,
  so the engine prints its own quest transition messages.
- **Build leaves the `ID_*.py` tables alone** (`d46c0c3`). The module
  build wrote them in text mode, so every build on Windows turned their
  LF endings into CRLF and left 23 files "modified" with no content
  change. Guarded by a schema test.

## Added

- **Taverns have people in them again** (verified 2026-09-22/23: the
  tavern fills, and hiring the mercenary company works end to end). A
  coop tavern held nobody but the tavernkeeper, because everything that
  decides who drinks where -- the mercenary company looking for a master,
  the companions passing through, the ransom broker, the travelling
  informant, the minstrel, the bookseller, the odd brawler -- lives in
  state the campaign server never sent to anyone. The server now sends it
  when you walk into a town, and the tavern fills up in the order the
  singleplayer game uses.
  - **Hiring the mercenary company works**: you agree the price in the
    tavern, and once you are back on the map the server charges your
    purse, puts the men in your party, and empties that town's company so
    the next player through finds nobody for hire. The count is re-priced
    and clamped by the server against your gold and your party's room for
    men, so nothing is minted by a client.
  - **A long tavern visit no longer loses the deal** (verified
    2026-09-22). The world keeps moving while you sit in a tavern, and
    every few days it swaps each
    town's mercenary company and moves the companions around. A hire or
    recruit you agreed to just before a swap used to be refused silently
    when you got back to the map. The server now remembers the company and
    towns from before the most recent swap and honours what you saw. Each
    company can still only be hired once.
- **Town and village visits show the center's people, and towns and
  castles offer the lord's hall** (verified 2026-09-19: town NPCs, mayor
  conversation, village elder, hall with the lords the campaign map
  showed inside). The server
  sends the visiting player the center's armorer, weaponsmith, mayor or
  elder, horse merchant, and for the hall its guards, lords and ladies, so
  the scene is populated even though center data never reaches clients.
  Design from Sirparabaran's WarbandTogether PR #1, rebuilt on our sync.
- **Trading with the merchants you walk up to** (`158ef9a`, `1b3b3f4`;
  verified 2026-09-19: town weaponsmith and horse merchant, village
  elder). The weaponsmith, armorer, and horse merchant in a town scene
  and the elder in a village show their real stock at that center's
  prices. What you buy and sell is queued on your machine and applied by
  the server after the visit ends and you are back on the map, so the
  goods and the gold match once the rejoin completes. Opening a
  merchant's screen without trading changes nothing. The goods merchant
  does not stand in the town scene, so goods trade stays in the center
  menu's marketplace. The inventory screen is not available inside a
  visit scene (`cfef13a`); use it from the map or the center menu.
- **Town and village quests** (Plan 4 of the PR #1 port; verified end to
  end 2026-09-20/21 for the caravan escort and the cattle herd: offer,
  accept, escort, arrival, claim at the giving mayor; wine delivered to
  the target town's tavernkeeper and paid on the rejoin 2026-09-23). The
  server rolls the offer with the game's own rules, spawns and drives the
  herd or caravan, watches arrivals and deadlines, and pays the reward,
  experience, renown and standing into your character. Your quest log
  shows your quests and survives rejoins; another player never sees
  them. The caravan pays out on arrival at its town without a
  conversation. Wine is turned in to the tavernkeeper through the tavern
  visit below. Design from Sirparabaran's WarbandTogether PR #1, rebuilt
  so the server owns every step.
- More mayor quests (verified 2026-09-27/29): deal with looters (40
  denars a band, a bonus when the last band falls; local-fight kills
  credited, progress and final report at the guildmaster, quest completed
  on the rejoin), rescue the kidnapped girl by paying the ransom from the
  encounter menu and bringing her home, and deal with night bandits
  (clear your town's ambush). Mayors no longer fall back to the caravan
  escort every time.
- Night ambushes: walking an infested town's streets at night can now
  spring native's bandit trap; win for XP and a purse (town win verified
  2026-09-29).
- **Towns offer "Visit the tavern."** (verified 2026-09-23). The
  center menu opens the town's tavern scene with the tavernkeeper in
  his place, so wine deliveries can be claimed and his other lines
  work; who else is in the tavern is covered above. Leaving the tavern
  rejoins the campaign server like every other visit.
- **Debug launcher with the map revealed** (`562482c`, verified
  2026-09-21). `coop_launch_all_debug.bat [N]` starts the same set as
  `coop_launch_all.bat` but sets `COOP_DEBUG_REVEAL=1` for the campaign
  server, which marks every party map-visible. The normal launcher keeps
  native fog of war.
- **Joining lands on your own party** (`14d2214`, `cf609f3`, `36d5cb0`;
  verified 2026-09-23). The client follows its own party from the first map frame
  instead of waiting for a server camera event, snaps once the own
  party's position has landed, and caches the last known map position
  on the client so the next join opens on it.
- **`[NetTuning] BacklogPeriodMs`** (`226e956`; the patch is verified to
  apply on both dedicated exes). A player whose last packet overflowed
  (join burst, character and inventory hydrate) was pinned to 10 Hz by
  the engine's backlog send period. The knob re-points that ceiling at a
  plugin-owned value; default 33 ms, 100 = stock. Its effect on join
  drain time is not measured yet.
- **Straight to spawn on battle join** (`ebd4f64`, shipped after v0.0.71
  was cut; verified for a field battle, initiator and B-key joiner, with
  the kill-XP message). Joining a dedicated battle no longer walks
  through the welcome, faction, and character choosers. You spawn as
  your own campaign character on the ally side once the battle is
  running. The in-battle Esc menu keeps "Show Game Rules" and "Choose
  Troops" and loses the two choosers.
- **Public roadmap.** `ROADMAP.md` and `roadmap.json` at the root of this
  repo list every singleplayer feature, which milestone it belongs to,
  and whether it works in coop yet. A block view of the same data lives
  at https://github.com/Night1099/warband-together-site.

## Future release

In this build but not verified yet, or not finished. Expect these to
change; report what you see.

- **Campaign server crash when a client joins** (`7afc290`; fixed, not
  yet verified). The host plugin serviced its battle-server IPC link
  from two threads at once (the IPC thread and the per-frame engine
  hook) with no locking, so ENet double-freed acknowledgement blocks and
  the campaign server died with heap corruption. The same crash
  signature was present in three crash dumps going back to Aug 29. The
  IPC thread is now the sole owner of the link. The plugin's crash
  handler also treats heap corruption as fatal, so it writes its own
  dump and report next time instead of leaving only the Windows Error
  Reporting dump.
- **Encounter arriving while a screen is open** (`f7f7280`; fixed, not
  yet verified). If an AI party reached you while you were in the
  character, inventory, party, or trade screen, the encounter menu was
  silently dropped and your party sat frozen in the encounter with no
  way out. The server-pushed menu jump is now deferred to the game loop,
  and an open screen is closed so the encounter takes over immediately.
  Town and village encounter menus went through the same path and are
  fixed the same way.
- **Bought items stay where you drop them** (`0f2855d`; not yet
  verified). A purchase dragged to a specific bag slot jumped to the
  first free slot on the next inventory open, because the server placed
  it with `troop_add_item` and then overwrote the client. The trade
  close now reports the drop slot and the server honours it when the
  slot is empty.
- **Campaign server: bandit-lair reveal is singleplayer-only**
  (`b6b295b`; built, not yet run with players). The vanilla 0.1-interval
  trigger that reveals bandit lairs near the player's party ran on the
  dedicated campaign server, where every `party_set_flags` call is a
  network broadcast to every client.
- The campaign server's `iMaxFrameRate` drops from 240 to 100
  (`197f230`; not yet run with players).
- **Immune inside a town, castle, or village** (`b85b5e9`; not yet
  verified). Entering a center attaches your party to it, the same
  mechanism the game uses for a lord inside a town. AI parties cannot
  target, chase, or encounter you until you leave, at which point your
  party reappears at the center. No siege exception exists yet because
  nothing launches a siege against a player-held center.
- **"Wait here for some time."** in the center menu (`79ec266`; not yet
  verified). Drops you back to the map view while you stay inside the
  center and immune. The world keeps running, the hotkey screens work,
  and Space brings the center menu back.
- **Your standing with lords, ladies, merchants and towns is your own**
  (Plan 3 of the PR #1 port; not yet runtime-verified). The server keeps
  each player's relations and "have we met" flags with their character,
  sends them to you when you join, and applies every change your own
  conversations and menus make, whether you made it in a lord's hall,
  a village, or on the map. The relation lines in notes and greetings
  show your values, not another player's, and they survive rejoins.
  Lord and lady personalities now match the server's, so a quarrelsome
  lord is quarrelsome for everyone. Design from Sirparabaran's
  WarbandTogether PR #1, rebuilt so the server owns the values.
- **Tavern: recruiting a companion binds them to one player** (not yet
  verified). A companion is a single person in the world: once one of
  you hires Borcha, he is gone from everyone else's taverns. Companions
  also move around between towns every few days again, which this fork
  had disabled -- they used to stand in the same tavern forever.
- **Tavern: buying books and ransoming a captured companion** from the
  broker both go through the server the same way as a hire (ransom not
  yet verified; books fixed in `cb20566`, not yet re-verified). A book
  bought in the tavern used to cost you the price on the rejoin but
  never arrive: the server did not accept the bookseller as a merchant,
  dropped the purchase, and charged the gold anyway. It now accepts him,
  and a trade the server rejects no longer moves any gold.
- Tavern, not ported yet: selling prisoners to the broker (the engine's
  prisoner screen is wired to a party a coop client does not own) and
  the tavern brawls (the drunk and the hired assassin are placed, but
  the fight triggers are not ported yet).
- Quests not yet verified: troublesome bandits, the village elder's
  grain, a partial wine delivery, rejoining mid-quest, a second player
  on the same mayor, and quest expiry.
- Quest expiry costs the native relation penalty (-1 for most mayor
  quests, -4 looters, -6 grain), not the harsher one coop charged before
  (not yet verified).
- Kidnapped girl: beating the kidnappers instead of paying, and credit
  for a dedicated battle against them (not yet verified).
- Night ambushes: losing (you lose some gold) and the village ambush
  (not yet verified).
- Persuade lords to make peace: bribe, befriend or out-argue two
  warmongering lords in their halls, or capture them; the claim ends the
  war for everyone on the server (not yet verified).
- Straight to spawn: the siege assault variant, the Esc menu contents,
  and the pre-spawn free-camera wait (not yet verified).

## Docs

- Full accuracy audit of every living doc and flow dossier (`1e59bc2`):
  line anchors re-pointed, stale commit references and facts corrected,
  install disclaimer rewritten to say what actually persists.
- Deferred ledger: center immunity siege exception.
- New flow dossier `docs/flows/campaign-server-tick.md` (`8a703fc`):
  frame loop, simple-trigger clock, party replication and per-client
  send pacing on the dedicated campaign server.

## Known issues

### Mayors keep offering the caravan escort

Eight of the singleplayer game's mayor quests are ported now:
troublesome bandits, moving a cattle herd, escorting a caravan,
delivering wine, rescuing a kidnapped girl, dealing with looters,
dealing with night bandits, and persuading lords to make peace. Each one
you finish or drop is not offered again for 20-30 game days, and the
campaign clock runs about a game hour every 4 seconds, so that is 30-50
minutes of play. The caravan escort has no such wait, so once you have
done the rest, every mayor offers the caravan until their waits run out.
Deal with night bandits keeps its target town's streets infested with
the ambush every night for as long as that quest is active, and only one
persuade-lords-to-make-peace quest can be active on the whole server at
a time.

### Joiners with the default HostIP

A client whose `coop.ini` still has `HostIP=127.0.0.1` can see the
campaign server and the battle list but the battle click drops to the
multiplayer main menu and nothing happens, because the battle connect
targets its own machine. Set `HostIP` to the host's LAN address. The
install guide's troubleshooting table covers this.
