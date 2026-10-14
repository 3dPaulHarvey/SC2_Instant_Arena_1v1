# Next solo test

Version **0.1.5** adds the first two-human sandbox and keeps the solo fallback.
Run this checklist with **only Player 1 present** before the two-client test in
[NEXT_1V1_TEST.md](NEXT_1V1_TEST.md). Player 2 must be an active human for two-human
mode; an empty second slot should keep the original enemy-spawning controls.

The user confirmed that the earlier live speed test worked. The **52 standard
multiplayer units** and **Void Multi (Mod)** dependency introduced in v0.1.4 remain
in this increment.

Test the expanded roster:

1. Close the previous test game and reopen the map with **Open Arena.cmd**, then
   press **Ctrl+F9**. Check that the displayed version is **0.1.5** and that
   **Spawn Enemy [Unit]** and **Reset Arena** are available in solo mode.
2. Check the race and unit dropdowns. Terran should have **17** entries, Protoss
   **18**, and Zerg **17**. Scroll within the unit list if necessary.
3. Choose Terran and try **Hellbat, Widow Mine, Cyclone, Siege Tank, Liberator,
   Medivac, Raven, Battlecruiser**, and the final entry **SCV**. Click each spawn
   button once for the selected unit and check the appropriate counter rises by one.
4. Choose Protoss and try **Adept, High Templar, Dark Templar, Colossus, Disruptor,
   Observer, Warp Prism, Oracle, Tempest, Carrier**, and the final entry **Probe**.
5. Choose Zerg and try **Baneling, Ravager, Lurker, Swarm Host, Queen, Overlord,
   Overseer, Mutalisk, Brood Lord, Viper**, and the final entry **Drone**.
6. Switch between races several times. Each switch should replace the unit list
   and select its first entry: Marine, Zealot, or Zergling. Captions should use the
   readable unit names, such as Hellbat, Siege Tank, and Swarm Host.
7. Try ordinary ground and air combat. Normal targeting rules apply: for example,
   Vikings in fighter mode and Corruptors target air, while Zealots target ground.
8. Select your Siege Tank, Widow Mine, Lurker, or Liberator and use its command card
   to change mode or burrow. These entries spawn in their normal mobile forms.
   Use spell and transport abilities manually on your own units as needed.
9. Drag the speed slider between Slower and Faster during a fight. It should keep
   working with the roster. Test **Clear My Army** and **Reset Arena**; the
   selected unit and speed should stay in place while the army counters clear.
10. Let your army die, then spawn more units. The session should continue without
    a victory screen. Check that each army stops accepting new units at **100
    living spawned units**, and that clearing it allows spawning again.

The complete roster is listed in [README.md](../README.md). It includes standard
combat, support, detector, transport, and worker units. Buildings, campaign heroes,
summoned-unit menu entries, and the unique Mothership are omitted from this increment.

Research requirements, energy, and other unit rules follow the standard game data.
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
Those results are the roster baseline, not proof that v0.1.5 works in SC2.
For v0.1.5, 19 source/metadata checks and 22 isolated native smoke checks passed.
The native smoke confirms solo startup and simulated two-player panels, selections,
ownership, clearing, limits, and all five speeds within one client. Real two-client
play remains pending. Interactive dropdown scrolling, combat abilities, and behavior at both
speed extremes are part of this play check. The earlier automatic harness is
only in a separate test copy of the map.

For the original Marine recovery checklist, see [SOLO_TEST.md](SOLO_TEST.md).
For the cause of the earlier compile failures, see [ROOT_CAUSE.md](ROOT_CAUSE.md).
