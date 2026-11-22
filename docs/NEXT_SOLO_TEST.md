# Next solo test

Version **0.1.7** adds full unit research, 1-1 upgrades, full starting vitals and
mirrored spawn formations. Run [COMBAT_SETUP_TEST.md](COMBAT_SETUP_TEST.md) as well
as the existing favorites and solo fallback checks below.
Run this checklist with **only Player 1 present** before the two-client test in
[NEXT_1V1_TEST.md](NEXT_1V1_TEST.md). Player 2 must be an active human for two-human
mode; an empty second slot should keep the original enemy-spawning controls.

The v0.1.7 build passes Galaxy syntax and all **37 regression checks**.
Interactive combat and favorites UI review remain pending.

The user confirmed that the earlier live speed test worked. The **52 standard
multiplayer units** and **Void Multi (Mod)** dependency introduced in v0.1.4 remain
in this increment.

The historical v0.1.6 build passed Galaxy syntax, all **30 regression checks**, and **40
native SC2 smoke checks** in a separate map copy. Native checks covered dropdown
events, repeated picks, FIFO ordering, batch counts, caps, ownership, and a
simulated second player. The final layout produced no new script or text errors.
Visual review remains pending because window capture timed out; complete the
interactive steps below and the two-client check separately.

Test the favorites and roster:

1. Close the previous test game and reopen the map with **Open Arena.cmd**, then
   press **Ctrl+F9**. Check that the displayed version is **0.1.7** and that
   **Spawn Enemy [Unit]** and **Reset Arena** are available in solo mode.
2. Confirm favorites start with **Marine**, **Void Ray**, and **Queen**, top to
   bottom. Each row should have **10**, **5**, and **1** buttons stacked on its
   right. Click Marine's **10**, **5**, and **1**; the friendly counter should
   rise by exactly 10, 5, and 1. Clear your army.
3. Check the race and unit dropdowns. In addition to **Add unit to favorites...**,
   Terran should have **17** unit entries, Protoss **18**, and Zerg **17**. Scroll
   within the unit list if necessary. Adding Marauder should produce **Void Ray,
   Queen, Marauder**. Add Marauder again: expect **Queen, Marauder, Marauder**.
   The menu should return to its placeholder after each addition, and no units
   should spawn merely from choosing one.
4. Change the race without choosing a unit. Favorites must stay unchanged, and
   **Spawn Enemy [Unit]** should update to Marine, Zealot, or Zergling for that
   race. Add one unit from another race and spawn from both its row and an older
   row to verify favorites retain their own unit types across race changes.
5. Choose Terran and try **Hellbat, Widow Mine, Cyclone, Siege Tank, Liberator,
   Medivac, Raven, Battlecruiser**, and the final entry **SCV**. Add each unit to
   the bottom favorite, use its **1** button and **Spawn Enemy [Unit]**,
   and check that each counter rises by one with the correct unit type.
6. Choose Protoss and try **Adept, High Templar, Dark Templar, Colossus, Disruptor,
   Observer, Warp Prism, Oracle, Tempest, Carrier**, and the final entry **Probe**.
7. Choose Zerg and try **Baneling, Ravager, Lurker, Swarm Host, Queen, Overlord,
   Overseer, Mutalisk, Brood Lord, Viper**, and the final entry **Drone**.
8. Switch between races several times. Each switch should replace the unit list
   and retain the **Add unit to favorites...** placeholder. Captions should use
   readable unit names, such as Hellbat, Siege Tank, and Swarm Host.
9. Try ordinary ground and air combat. Normal targeting rules apply: for example,
   Vikings in fighter mode and Corruptors target air, while Zealots target ground.
10. Select your Siege Tank, Widow Mine, Lurker, or Liberator and use its command card
    to change mode or burrow. These entries spawn in their normal mobile forms.
    Use spell and transport abilities manually on your own units as needed.
11. Drag the speed slider between Slower and Faster during a fight. It should keep
    working with the roster. Test **Clear My Army** and **Reset Arena**; favorites,
    selected enemy unit, and speed should stay in place while counters clear.
12. With no fighting, spawn **95** friendly units, then click a favorite's **10**.
    Only five more should spawn, reaching **100 living spawned units**. Further
    **10**, **5**, or **1** clicks must not exceed the cap. Clearing should allow
    spawning again. Check the solo enemy's independent 100-unit limit too.
13. Let your army die, then spawn more units. The session should continue without
    a victory screen.

The complete roster is listed in [README.md](../README.md). It includes standard
combat, support, detector, transport, and worker units. Buildings, campaign heroes,
summoned-unit menu entries, and the unique Mothership are omitted from this increment.

Unit research is pre-granted and units start with full energy. Normal spell
costs, cooldowns and targeting still apply; see the combat checklist for details.
The solo enemy side receives a basic attack-move or move order; it does not get new
spellcasting or mode-changing AI in this increment.

Publishing is unnecessary for solo testing. The active map is
`src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`; use the launcher even
if an old map path is still shown in an IDE tab.

For the previous v0.1.4 build, Galaxy syntax and all four recovery checks passed.
An isolated SC2 runtime test passed all 52 roster entries: 104 friendly/hostile
units had the expected types, owners, and counts. Race menu sizes and
reset-to-first behavior also passed, and
the original game speed was restored. No script or text-error log was produced.
Those results are the roster baseline, not proof that v0.1.6 works in SC2.
For v0.1.5, 20 source/metadata checks and 22 isolated native smoke checks passed.
The native smoke confirms solo startup and simulated two-player panels, selections,
ownership, clearing, limits, and all five speeds within one client. Real two-client
play remains pending. Those historical results do not validate the new favorites.
Interactive dropdown scrolling, FIFO ordering, repeated and mixed-race selections,
batch counts, combat abilities, and behavior at both speed extremes are part of
this play check. The earlier automatic harness is
only in a separate test copy of the map.

For the original Marine recovery checklist, see [SOLO_TEST.md](SOLO_TEST.md).
For the cause of the earlier compile failures, see [ROOT_CAUSE.md](ROOT_CAUSE.md).
