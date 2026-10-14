# Instant Arena

A StarCraft II custom arena for instant unit spawning and continuous combat.

The active build is **v0.1.5: first two-human sandbox**. Players 1 and 2 each
choose a race and unit, spawn their own army, and command it normally against the
other player. Player 1 controls the match speed. Without a second active human,
the original solo enemy-spawning controls remain available.

The previous map was successfully published and played online. This increment
still needs its interactive solo and two-client play checks before its online behavior is
confirmed. It adds shared sandbox combat; rounds, scoring, victory screens,
rematches, and disconnect handling are future work.

## Open and test

1. Exit the previous test game and close the old map in the Editor.
2. Double-click **Open Arena.cmd** in this project.
3. The launcher opens `src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`.
4. Press **Ctrl+F9** to run the local test.
5. Choose **Terran**, **Protoss**, or **Zerg** in the top dropdown. The second
   dropdown lists that race's units.
6. In a solo test, use **Spawn My [Unit]**, **Spawn Enemy [Unit]**,
   **Clear My Army**, and **Reset Arena**.
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
for siege, burrow, transport, and spell abilities. Research requirements, energy,
and attack-target restrictions follow the standard game data. Solo enemy units
receive a basic attack-move or move order; their spells and mode changes need
separate AI.
The roster contains standard combat, support, and worker units. Buildings, campaign
heroes, summoned-unit menu entries, and the unique Mothership are omitted.

Changing race selects its first unit. Menu selections do not spawn anything.
In solo mode, Reset Arena clears both armies and leaves the menu selection in place.
Two-human mode provides each player with their own spawn and clear controls.
The match starts at **Normal** speed. The slider changes SC2's live game speed;
its label displays the engine's actual preset. Reset Arena keeps your chosen speed.
Player 1 controls speed for the whole match; both players see its current label.
Online speed synchronization still needs a two-client test.
See [NEXT_1V1_TEST.md](docs/NEXT_1V1_TEST.md) for this increment's staged test,
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
| `tests/test_mapinfo.py` | Lobby metadata preservation and validation checks |
| `backups/v0.1-marine-only/` | The original working source and trigger files |
| `experiments/race-menu-v0.2/` | The inactive menu attempt, retained for diagnosis |
| `maps/` | Destination for a packed map file saved from the Editor |

`InstantArena_Basic.SC2Map` is a component folder. Open its
`ComponentList.SC2Components` file in the Editor. To make a single packed map,
choose **File > Save As > StarCraft II Map Files (.SC2Map)** and save into `maps/`.

These files can stay in the project directory. Publishing is needed for normal
internet hosting with a friend, but not for local solo testing.

## Update the existing published map

Yes: you can publish an update to the same map. After the local checks pass, open
the rebuilt component map with the launcher, save a current packed copy into
`maps/`, and use **File > Publish**. Use the original publishing account and region,
keep the **same Published Name**, and choose a **Minor revision** for this increment.
The publishing system increments the published version automatically when you
reuse that name; the project version `0.1.5` is a separate source version.
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

Galaxy syntax and all 20 source/metadata regression checks pass. The checks include
the actual component map's two human lobby slots. An isolated native
SC2 smoke test passed 22 checks covering actual solo initialization, spawning,
ownership, clearing, limits, all five speeds, and simulated two-player panels and
selections in one client. No new script or text-error log was produced. The smoke
harness is confined to a test copy; it does not establish two-client synchronization
or visual UI results.

The user confirmed the earlier live speed control and online publication worked.
For v0.1.5, first check the solo fallback, then update the published map and test
with two human clients. Check independent menus, army ownership, separate spawn
areas, combat, clear isolation, and shared speed. Editor compilation and these
play checks must confirm the new behavior on both human clients.

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
