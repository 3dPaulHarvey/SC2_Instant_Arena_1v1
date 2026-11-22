# Instant Arena

A StarCraft II custom arena for instant unit spawning and continuous combat.

The active build is **v0.1.7: battle-ready armies**. Every side receives **1-1
weapons and armor, +1 Protoss shields, and all current unit research**. New units
start at full health, shields, and energy; carriers start with a full interceptor
complement. Batches form two mirrored files facing the opponent, with normal
collision placement. Each player has three
favorite unit slots with **10**, **5**, and **1** spawn buttons. The unit dropdown
adds units to those slots in FIFO order. Players 1 and 2 spawn their own armies
and command them normally against each other. Player 1 controls the match speed.
Without a second active human, solo enemy-spawning controls remain available.

The previous map was successfully published and played online. This increment
still needs its interactive solo and two-client play checks before its online behavior is
confirmed. It provides shared sandbox combat; rounds, scoring, victory screens,
rematches, and disconnect handling are future work.

## Open and test

1. Exit the previous test game and close the old map in the Editor.
2. Double-click **Open Arena.cmd** in this project.
3. The launcher opens `src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`.
4. Press **Ctrl+F9** to run the local test.
5. The favorites start with **Marine**, **Void Ray**, and **Queen**, top to bottom.
   Choose a race, then a unit in **Add unit to favorites...**. The oldest top
   favorite drops out, the other two move up, and the chosen unit fills the bottom.
   The dropdown returns to its placeholder so the same unit can be added again.
6. Use the stacked **10**, **5**, or **1** buttons beside a favorite to spawn that
   many units. In solo mode, **Spawn Enemy [Unit]** spawns one enemy of the last
   selected unit; **Clear My Army** and **Reset Arena** remain available.
7. Drag the **Game speed** slider at the bottom of the panel. It snaps to
   **Slower, Slow, Normal, Fast, Faster**, from left to right.

In solo mode, enemy combat units attack-move toward your spawn area; support units
move there. In a two-human game, each player spawns on their own side and commands
their own units manually. Each player has independent race and unit selections;
**Clear My Army** only removes that player's army. Players 1 and 2 are hostile.
Losing all units does not end the session. Each side can have up to 100 living
spawned units.

| Race | Unit submenu |
| --- | --- |
| Terran (17) | Marine, Marauder, Reaper, Ghost, Hellion, Hellbat, Widow Mine, Cyclone, Siege Tank, Thor, Viking, Medivac, Liberator, Banshee, Raven, Battlecruiser, SCV |
| Protoss (18) | Zealot, Stalker, Sentry, Adept, High Templar, Dark Templar, Archon, Immortal, Colossus, Disruptor, Observer, Warp Prism, Phoenix, Void Ray, Oracle, Tempest, Carrier, Probe |
| Zerg (17) | Zergling, Baneling, Roach, Ravager, Hydralisk, Lurker, Infestor, Swarm Host, Ultralisk, Queen, Overlord, Overseer, Mutalisk, Corruptor, Brood Lord, Viper, Drone |

The 52 entries use **Void Multi (Mod)**, SC2's Legacy of the Void multiplayer
dependency. Units spawn in their normal mobile form. Use their own command cards
for Stim, Blink, Charge, Storm, siege, burrow, transport, and other abilities.
Special research includes Zergling movement/attack speed, Baneling speed, Roach
speed/tunneling, Hydralisk and Lurker upgrades, cloak, range and support upgrades.
The map reads the current multiplayer research command cards so unused legacy
upgrades are not granted. Ground and air weapons/armor stay at level 1; Terran
combined plating is applied once, and Protoss shields also receive level 1.
Hellion/Hellbat transformation works without an Armory. Carrier replacement
interceptors cost no minerals in this economy-free arena and retain their normal
build time. Health and energy refill only at spawn; normal ability costs,
cooldowns, target restrictions, and terrain requirements still apply. Solo enemy units
receive a basic attack-move or move order; their spells and mode changes need
separate AI.
The roster contains standard combat, support, and worker units. Buildings, campaign
heroes, summoned-unit menu entries, and the unique Mothership are omitted.

Changing race updates the available unit list without changing favorites; in solo
mode it selects that race's first unit for **Spawn Enemy [Unit]**. Choosing a unit
adds a favorite without spawning anything. Favorites may mix races and contain
duplicates. Spawn batches stop at the existing 100 living-unit limit, so a batch
may spawn fewer units when near the cap.
In solo mode, Reset Arena clears both armies and keeps the favorites and selections.
Two-human mode provides each player with their own spawn and clear controls.
The match starts at **Normal** speed. The slider changes SC2's live game speed;
its label displays the engine's actual preset. Reset Arena keeps your chosen speed.
Player 1 controls speed for the whole match; both players see its current label.
Online speed synchronization still needs a two-client test.
See [COMBAT_SETUP_TEST.md](docs/COMBAT_SETUP_TEST.md) for the new combat checks,
[NEXT_1V1_TEST.md](docs/NEXT_1V1_TEST.md) for this increment's staged test,
[NEXT_SOLO_TEST.md](docs/NEXT_SOLO_TEST.md) for the solo fallback and roster checklist,
and [SOLO_TEST.md](docs/SOLO_TEST.md) for the original recovery test.
See [ROOT_CAUSE.md](docs/ROOT_CAUSE.md) for the compiler failure and repair.

## Project files

| Path | Purpose |
| --- | --- |
| `src/Arena.galaxy` | Arena source, per-player menus and armies, solo fallback, and live speed control |
| `src/InstantArena_Basic.SC2Map/` | The active editable map, including terrain and triggers |
| `tools/build_map.py` | Checks syntax before updating the map's script and triggers |
| `tools/validate_galaxy.py` | Runs the bundled Galaxy syntax parser |
| `tools/configure_players.py` | Configures the editable v34 map's two human lobby slots while preserving other metadata |
| `tests/test_recovery.py` | Regression checks for the failure and restored scripts |
| `tests/test_multiplayer.py` | Ownership and per-player control regression checks |
| `tests/test_favorites.py` | Favorites ordering, batch spawning, and per-player isolation checks |
| `tests/test_combat_setup.py` | Research traversal, exact upgrade levels, spawn readiness, and mirrored formations |
| `tests/test_mapinfo.py` | Lobby metadata preservation and validation checks |
| `backups/v0.1-marine-only/` | The original working source and trigger files |
| `experiments/race-menu-v0.2/` | The inactive menu attempt, retained for diagnosis |
| `maps/` | Destination for a packed map file saved from the Editor |

`InstantArena_Basic.SC2Map` is a component folder. Open its
`ComponentList.SC2Components` file in the Editor. To make a single packed map,
choose **File > Save As > StarCraft II Map Files (.SC2Map)** and save into `maps/`.
A current packed build is also included at `maps/InstantArena-v0.1.7.SC2Map`.
Older packed files still contain their earlier builds.

These files can stay in the project directory. Publishing is needed for normal
internet hosting with a friend, but not for local solo testing.

## Update the existing published map

Yes: you can publish an update to the same map. After the local checks pass, open
the rebuilt component map with the launcher, save a current packed copy into
`maps/`, and use **File > Publish**. Existing packed maps are stale until saved
again from the rebuilt component map. Use the original publishing account and region,
keep the **same Published Name**, and choose a **Minor revision** for this increment.
The publishing system increments the published version automatically when you
reuse that name; the project version `0.1.7` is a separate source version.
See [Blizzard's publishing tutorial](https://s2editor-guides.readthedocs.io/Classic_Tutorials/04_Misc/publishing/).

Keep the existing release setting if you want the same availability. A **Private**
release lets the author create a game and invite friends for testing; a **Public**
release lets other players host it too.
[Publishing release settings](https://s2editor-guides.readthedocs.io/Classic_Tutorials/04_Misc/publishing/).

After upload, create a fresh lobby and follow the two-client checklist. Saving a
local file alone does not update the online map.

## Build and validate

Close the active map before editing its files externally. Edit `src/Arena.galaxy`,
then run:

~~~powershell
python tools/build_map.py
python -m unittest discover -s tests -v
~~~

Reopen the Basic map and test in SC2. The builder updates only code, trigger data,
and trigger names; it preserves terrain and map settings.
`MapScript.galaxy` and `Triggers` are generated files. Make logic changes in
`src/Arena.galaxy` and rebuild so the Editor and source stay consistent.

The syntax checker uses installed Node.js, or VS Code's bundled Node runtime when
Node is not on PATH. It needs no npm installation or network access. Opening and
testing the saved map does not require this build tooling.

The parser checks Galaxy grammar. It does not resolve game dependencies or replace
the Editor's native type checking and gameplay tests. Invalid syntax causes a build
failure before the playable map is overwritten.

## Current test scope

The v0.1.7 build passes Galaxy syntax and all **37 regression checks**, including
exact level-1 upgrades, research traversal, player isolation, full starting
vitals, interceptor capacity, and mirrored formations. A native SC2 5.0.17 run
passed **648 checks**, covering all 52 roster entries for owners 1, 2 and 15,
full vitals and carrier magazines, key ability availability, Stim health costs,
Hellbat transformation, and spawning. All three owners had the same **56 upgrades
at level 1**, with no level-2/3 upgrades. Interactive combat and two-client
validation remain in [COMBAT_SETUP_TEST.md](docs/COMBAT_SETUP_TEST.md).

The previous v0.1.6 build passed Galaxy syntax and **30 regression checks**, covering
favorites ordering, repeated selections, batch spawning, limits, per-player
isolation, and the component map's two human lobby slots. An isolated native SC2
run passed **40 checks**, including actual dropdown selection events, repeated
picks, batch counts, the exact 100-unit cap, and a simulated second player.
The final button layout produced no new script or text errors. Visual review
remains pending because window capture timed out; two-client play is also pending.
The smoke harness is confined to a separate test copy.

The user confirmed the earlier live speed control and online publication worked.
First check the defaults, FIFO ordering, repeated selections, mixed-race favorites,
batch counts, and partial batches at the cap in solo mode. Then test independent
favorites and armies with two human clients, along with combat, clear isolation,
and shared speed. Interactive play checks remain required for this prototype.

Keep the next increment small and choose it after these results. Match rules and
disconnect behavior are not implemented in this sandbox iteration.

## References

Terrain is adapted from Blizzard's SC2 Editor tutorial
[021_Units_Layer.SC2Map](https://github.com/SC2Mapster/blizzard-tutorials/blob/master/docs/New_Tutorials/02_Terrain_Editor/maps/021_Units_Layer.SC2Map),
preserved by SC2Mapster. Its placed units were removed and its triggers replaced.

- [Blizzard's Trigger Module tutorial and local Test Document](https://s2editor-guides.readthedocs.io/Classic_Tutorials/02_Trigger_Module/1/)
- [Component-folder export](https://s2editor-guides.readthedocs.io/New_Tutorials/07_Lessons/083_Export_Game_Assets/)
- [Bundled parser provenance and MIT license](tools/galaxy_parser/README.md)
- [Blizzard's shipped native speed API and cinematic speed changes](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/core.sc2mod/base.sc2data/TriggerLibs/NativeLib.galaxy)
- [Blizzard's standard Void multiplayer unit definitions](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/voidmulti.sc2mod/base.sc2data/GameData/UnitData.xml)
