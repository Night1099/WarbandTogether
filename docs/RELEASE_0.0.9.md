# v0.0.9 — Captivity, Morale & Food

Players can now be taken prisoner when defeated, rescued by friends, feed their troops, and manage party morale.

> **Before you update:**
> - **Back up your characters before testing captivity.** Being captured can cost gold and items, just like in singleplayer. Character files live in the campaign server's `WSE\NativeCoop\` folder (`coop char sid <id>.wsedict` and `coop char bak sid <id>.wsedict`).
> - **Old world saves:** Saves from v0.0.82 haven't been tested with this build. If anything seems off after updating, move `sg00.sav` out of `Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames\` to start a fresh world.
> - **LAN players:** Make sure `HostIP` in your `coop.ini` is set to the host PC's LAN IP (see Known Issues).

## What's New

- **Defeat, Captivity & Rescue**
  - Losing a battle can now make you a prisoner, costing troops, prisoners, some gold, and potentially items.
  - While captive, your party disappears from the map and your camera smoothly follows your captor (clicking the map, opening menus, or rejoining keeps it locked on them).
  - You'll eventually escape on your own. If held in a castle, you get singleplayer's events: prisoner exchange, another night in the cell, or a ransom offer you can pay or refuse.
  - **Co-op rescue:** Another player can defeat your captor (locally or on a battle server) to free you and your party on the spot. Only the captor's own troops fight.
  - Captivity persists across disconnects and rejoins. While captive, you can't enter towns or join battles with `B`.
- **Party Morale**
  - Your party now has singleplayer morale driven by food variety, party size, leadership, and wage debt.
  - Morale persists across rejoins and sets how brave your bots are in dedicated battles.
- **Food & Supplies**
  - Your party eats food from your inventory and meat spoils over time while you're online.
  - Running out of food shows the red *"Party has nothing to eat!"* warning and drains morale.
  - Food quantities persist across rejoins, moving items in your inventory, and dedicated battles.
- **Abandoned Battles Auto-Cancel**
  - If nobody connects to a dedicated battle within ~1 minute of real time (15 game hours), the battle is cancelled automatically — freeing the enemy party and battle server slot and notifying whoever started it. Battles that actually start are never cancelled.
- **Weekly Budget Report on Payday**
  - Payday now opens singleplayer's weekly budget screen showing prior debt, gold before payment, and wages charged.

## Bug Fixes

- **Starting Gear & Background Kit:** New characters now spawn with the correct starting gold and equipped gear for their chosen background — no extra free troops, bonus gold, or duplicate shared starting companions.
- **Clean Character Slots:** Creating a new character in a previously used player slot no longer inherits leftover skills, proficiencies, XP, or renown.
- **Double Volunteer Recruitment:** Recruiting villagers no longer briefly shows twice as many recruits on your client.

## Cleanup

- Removed `coop_client2.bat` (an internal dev script that never worked in release builds), along with an unused Lua reporter and an unused battle server ini file.

## Experimental / Unverified

*Included in this build, but not fully tested yet — let us know if you run into issues.*

- **Enemy Party Stays Put During Combat:** Attacked parties should no longer wander off the map mid-fight (seen working in dedicated battles; local fights untested).
- **Clean Battle Server XP Slots:** Battle servers now wipe leftover XP when reusing a player slot so it can't leak as extra kill XP.
- Unverified items listed under **Experimental** in the v0.0.82 notes are still pending full testing.

## Known Issues

- **LAN Players Must Set `HostIP`:** Dedicated battles connect to the `HostIP` in your own `coop.ini`, not the server you clicked in the browser. If it's blank, wrong, or left at `127.0.0.1`, you can play on the campaign map but joining a dedicated battle kicks you to the multiplayer menu (and may require restarting the game). Set `HostIP` to the host PC's LAN IP (`ipconfig` on the host).
- **Companions Prevent Capture in Dedicated Battles:** Having a companion in your party prevents you from being taken prisoner after losing a dedicated battle (works normally in local fights). Also, only the player who started a dedicated battle can be captured by it.
- **Captives Aren't Shown in the Captor's Party:** Your captor's party tooltip/roster doesn't list you as a prisoner yet.
- **Battle Bots Never Rout:** Dedicated battle troops use party morale for courage, but never flee a losing fight.
- **Passworded Servers & Battle Hops:** If the host sets `Password=` in `coop.ini`, every player must also add that exact password to their own `coop.ini`, or dedicated battle hops will drop them to the server list.
- **Closing Inventory as Meat Spoils:** Closing your inventory at the exact moment meat spoils can undo the spoilage.
- **From Earlier Releases:** Selling to village elders doesn't increase their gold; guild masters keep offering caravan escorts once other quests are on cooldown; enemy towns still show as neutral on the map tooltip after war is declared (though they still refuse entry).
