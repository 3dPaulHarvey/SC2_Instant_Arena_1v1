# Battle-ready armies and two-human sandbox test: v0.1.7

This increment adds full unit research, 1-1 upgrades, full starting vitals and
mirrored formations. Complete [COMBAT_SETUP_TEST.md](COMBAT_SETUP_TEST.md) on both
clients. It retains three FIFO favorite slots per player, each with stacked
**10**, **5**, and **1** spawn buttons. It preserves independent human armies
and the solo fallback when Player 2 is not an active human. It does not add rounds,
scoring, victory screens, rematches, or disconnect handling. Treat the steps
below as pending until they are run; code and syntax checks do not establish
online play results.

The historical v0.1.6 build passed Galaxy syntax and all **30 regression checks**, including
favorites ordering, repeated selections, batch counts, limits, and isolation.
An isolated native SC2 run passed **40 checks** on the final layout, including
dropdown selection events, repeated picks, FIFO, batch counts, the exact cap,
ownership, speed preservation, and a simulated second player. No new script or
text errors appeared. Visual review remains pending because window capture timed
out; physical clicks and two-client synchronization still need the checklist.

The v0.1.5 baseline passed Galaxy syntax, 20 source/metadata regression checks,
and 22 native SC2 smoke checks. That native smoke exercised actual solo startup
and explicitly simulated two-player panels, menus, ownership, clearing, and limits
within one client. All five speeds passed. No new script or text-error log appeared.
The production map contains no smoke harness. Two-client synchronization, friend
play, and visual UI review remain pending. Those baseline results do not validate
the new favorites behavior or layout in v0.1.6.

Code review on **October 13, 2026** found no blocker in the basic two-human flow.
The actual component map has User slots 1 and 2, with separate menus, spawn/clear
controls, army ownership, spawn points, and enemy alliances. The regression suite
now checks those slots in the actual playable metadata, in addition to testing
the metadata conversion. The saved native result contains 22 passing checks, but
Player 2 was simulated; real joining, button events, and network synchronization
remain unverified. Player 1's speed permission follows the player slot, not the
identity of the lobby host.

The army counters and 100-unit limits track units created by the spawn buttons.
Ability-created units, such as Swarm Host locusts, are not added to those groups;
**Clear My Army** does not explicitly remove them. Test those abilities separately
if they are part of your match. This limitation does not prevent a basic 1v1.

## 1. Local solo check

1. Close the previous game and Editor map before rebuilding or reopening.
2. Run `python tools/build_map.py`, then
   `python -m unittest discover -s tests -v`.
3. Open **Open Arena.cmd** and press **Ctrl+F9**. Check the version is **0.1.7**.
4. With only Player 1 present, confirm **Spawn Enemy [Unit]** and **Reset Arena**
   are available. Confirm the favorites are **Marine**, **Void Ray**, and **Queen**
   from top to bottom, each with **10**, **5**, and **1** buttons on the right.
   Use Marine's **1** button and **Spawn Enemy Marine**. Friendly units should
   belong to Player 1; solo enemies should use hostile Player 15 and advance
   toward your spawn area.
5. Test **Clear My Army**, then **Reset Arena**. Clearing your army should leave
   enemies; reset should remove both. Favorites, the selected race/unit, and speed
   should remain in place.
6. Complete [NEXT_SOLO_TEST.md](NEXT_SOLO_TEST.md), including the roster, speed,
   unit limit, and surviving army-loss checks. Resolve Editor errors and fallback
   failures before the online test.

## 2. Update the published map

1. Open the rebuilt component map through the launcher. In **Map > Player
   Properties**, verify Players 1 and 2 are **User** slots. In **Map > Game
   Variants**, inspect the variant used for publishing and ensure it permits two
   human participants. This project has no explicit custom variant or lobby team
   setup; confirm the default lobby exposes both slots. Gameplay sets the two
   players as enemies itself. See [Blizzard's game variants tutorial](https://s2editor-guides.readthedocs.io/New_Tutorials/01_Introduction/012_Game_Variants/).
2. Save a current packed
   `.SC2Map` copy into `maps/` so an older packed file is not uploaded by mistake.
   Existing packed maps are stale until saved from the rebuilt component folder.
3. Use **File > Publish**, sign in with the original publishing account, and use
   the same region and **Published Name** as the existing online map.
4. Choose **Minor revision**. Reusing the published name updates that map and
   increments its online revision automatically. `0.1.7` is the source version,
   separate from Battle.net's revision number.
5. Keep the existing release setting, or use **Private** for author-hosted friend
   testing. A Private map permits the author to create games and invite others.
   See [Blizzard's publishing tutorial](https://s2editor-guides.readthedocs.io/Classic_Tutorials/04_Misc/publishing/).
6. Wait for the upload to complete. Create a **fresh lobby** from the updated
   online map; saving locally does not update Battle.net.
7. Keep the lobby private, invite your friend, and put yourself in **Player 1**
   and your friend in **Player 2** before starting. Both accounts must use the
   publishing region. A Private publication controls who can host the map; the
   lobby's privacy controls who can join that particular game.

## 3. Two-client human check

Use two StarCraft II clients and two accounts in the publishing region. The host
should occupy **Player 1** and the friend **Player 2**, both as human players.
Do not substitute a computer player or observer for the second human.

1. **Lobby and version:** confirm both human slots can be joined. Start together
   and check both clients show **0.1.7**. If only the solo controls appear, record
   the lobby slots and stop to investigate Player 2 detection.
2. **Favorites and menu isolation:** both players start with Marine, Void Ray,
   and Queen. Player 1 adds Terran / Marauder; only Player 1 should now show
   Void Ray, Queen, Marauder. Player 2 adds Protoss / Zealot; only Player 2 should
   show Void Ray, Queen, Zealot. Repeat a unit selection to check duplicates and
   FIFO ordering. Changing only the race must leave all three favorites intact.
   The other player's dropdowns and favorites must stay unchanged.
3. **Ownership, counts, and placement:** use favorite **1**, **5**, and **10**
   buttons on each client and confirm the matching count increases. Each unit
   should appear on its owner's side, and each client should be able to select and
   command its own unit. Both army counters should show the expected counts.
   Neither player's favorite buttons should create a unit owned by the other player
   or by the solo enemy slot.
4. **Human combat:** spawn a small ground army each, issue movement and attack
   orders manually, and meet in the arena. The armies should be hostile and able
   to damage each other. Spawned human armies should not receive the solo
   enemy's automatic attack-move orders.
5. **Clear isolation:** while both armies are alive, Player 1 uses **Clear My Army**.
   Only Player 1's units and counter should clear. Spawn again, then repeat with
   Player 2. Both players' favorites, the other army, menu selections, and game
   speed should remain.
6. **Shared speed:** Player 1 changes speed from Normal to Slower and Faster.
   Both clients should show the same current speed label and run at the same
   speed. Player 2 should have no speed-changing control. Return to Normal.
7. **Army limit:** at a quiet moment, clear both armies and spawn **95** units on
   one side, moving units away from the spawn area as needed. Click **10**: only
   five more should spawn. Further favorite buttons must not create a 101st
   living unit.
   The other player should still be able to spawn their own units. Clear the
   first army and verify it can spawn again; repeat for the other side.
8. **Army loss:** allow one player's army to die. Both clients should remain in
   the game, with no round-end or victory screen; that player should be able to
   spawn again. Repeat with the other player.
9. **Broader smoke check:** try one air unit and one support unit per player.
   Check manual movement, ordinary target restrictions, and counters after
   deaths. Use abilities from each unit's normal command card. If using Swarm
   Hosts, test creating locusts and clearing the parent army; record whether the
   locusts remain until their normal expiry.

## Record the result

Record the published revision, lobby slot assignments, both displayed versions,
and pass/fail for each stage. Include the exact action and which client observed
any failure. Keep Editor errors or SC2 script/text errors if any appear.

| Stage | Result |
| --- | --- |
| v0.1.5 baseline: syntax, 20 source/metadata checks, 22 native single-client checks | Passed (historical) |
| v0.1.6 Galaxy syntax and 30 regression checks | Passed |
| v0.1.6 native compilation and 40 single-client smoke checks | Passed (Player 2 simulated) |
| v0.1.7 syntax and 37 regression checks | Passed |
| v0.1.7 native compilation and 648 combat setup checks | Passed (one client; owners 1, 2 and 15) |
| Interactive favorites defaults, FIFO, repeated and mixed-race selections | Pending |
| Favorite 1/5/10 counts, partial batches, and solo UI review | Pending |
| Same-map publishing update | Pending |
| Two-human lobby and menu isolation | Pending |
| Ownership, placement, manual combat | Pending |
| Clear isolation and shared speed | Pending |
| Per-side limit and army-loss continuation | Pending |

Choose the next small increment after this checklist passes. Disconnects and
rejoins are outside this iteration's supported flow.
