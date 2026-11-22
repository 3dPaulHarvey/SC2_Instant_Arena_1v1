# Battle-ready armies: v0.1.7

All three arena owners (Players 1, 2 and solo enemy 15) receive the same profile
before the menus are created. The profile includes all three races, independent
of lobby race and favorite selection. General weapons/armor are exactly level 1,
including air upgrades, Zerg melee and missile upgrades, and Protoss shields.
Terran vehicle/ship plating is granted once through the combined upgrade.

Special upgrades are resolved from the current multiplayer research buttons on
20 unit-specialist structures. This covers Stim, Combat Shields, Concussive Shells,
cloak, Infernal Pre-Igniter, Drill Claws, Smart Servos, Cyclone research, Banshee
speed, Raven/Medivac research, Liberator research, Yamato, Charge, Blink, Glaives,
Storm, Shadow Stride, Colossus range, Observer/Prism speed, Phoenix range, Void Ray
speed, Tempest research, Burrow, Zergling speed/attack speed, Baneling speed,
Roach speed/tunneling, Hydralisk research, Lurker research, Neural Parasite,
Ultralisk plating/speed, and Overlord speed as offered by the installed mod.
Research that a balance patch makes innate does not need a separate grant.

New units receive full health, shields and energy once. Carriers fill to the
current magazine capacity and rebuild lost interceptors for free at their normal
build rate. Hellion/Hellbat transformation has its Armory prerequisite removed.
Units appear in mirrored files at their side's spawn point, facing inward; the
engine adjusts occupied ground positions. Human players activate spells and
mode changes themselves. Solo enemies retain basic attack-move/move orders.
No spell AI, permanent Stim, unlimited energy, or cooldown reset is added.
Ghost nukes still require ammunition; morphs, repair, creep and valid spell
targets retain their normal requirements except for the stated arena changes.

## Automated validation

Run `python tools/build_map.py` and `python -m unittest discover -s tests -v`.
Galaxy syntax and **37 regression checks** pass. The new checks execute authored
logic against substitutes for the engine APIs; they do not prove native catalog
access or command-card usability.

An isolated packed-map run in **SC2 5.0.17.98745** passed **648 native checks**:
creation and full vitals for all 52 unit types for each of owners 1, 2 and 15,
full carrier magazines, availability of 13 key abilities, Marine health and
armor, Stim's health cost, actual Hellion-to-Hellbat transformation, a ten-unit
spawn batch, and solo enemy preparation. Bank output confirmed the same **56
level-1 upgrades** for all three owners, with no level-2/3 upgrades. Player 2
units were created directly in this single-client test; this is not a second
connected human or an interactive UI test. The harness ran only in a disposable
map copy, never in the playable component map.

## Interactive checks

1. Reopen the component map using `Open Arena.cmd`, then Ctrl+F9. Confirm **0.1.7**
   and the **1-1 + shields | All unit research** label. Test 1, 5 and 10 batches
   and the partial batch at 95 living units. The cap must stay at 100.
2. Spawn Marines and Marauders. Check level-1 weapon/armor icons, Marine Combat
   Shields health, Stim availability and health cost, and Marauder slowing attacks.
3. Spawn Zerglings, Banelings, Roaches, Hydralisks and Lurkers. Check their speed,
   range and burrow research. Test Zergling attack speed, Roach burrowed movement,
   Hydralisk's current researched ability, and Lurker burrowing/range.
4. Spawn Zealots, Stalkers, Adepts, High Templars and Dark Templars. Check Charge,
   Blink, Glaives, Storm and Shadow Stride. High Templars should start with full
   energy and spend it when casting. Protoss shield armor should show level 1.
5. Check Ghost/Banshee cloak, Raven abilities, Medivac healing/boost, Battlecruiser
   Yamato, Liberator targeting, and Hellion/Hellbat transformation without buildings.
   Siege a Tank, burrow a Lurker, and transform a Viking/Thor; their level-1
   weapons/armor must persist and must not become level 2.
6. Spawn Carriers: check full interceptors immediately, their level-1 weapons,
   and free replacement after losses. Check ground and air damage/armor upgrades
   on one unit from each race, including both forms of morphing units.
7. Use abilities, clear/reset, and respawn. Fresh units should have full vitals
   and the same upgrades; surviving units should not continuously refill.
8. Repeat with both real human clients. Both sides must have the same profile,
   own their units, retain independent favorites and manual control, and show
   mirrored starting files. Also verify equivalent upgrades on solo enemies.

The existing favorites and online checklists still apply. Their historical native
results do not validate this increment. Save a fresh packed map before publishing.

## Data references

The implementation uses Blizzard's shipped data, mirrored by SC2Mapster:
[multiplayer unit command cards](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/voidmulti.sc2mod/base.sc2data/GameData/UnitData.xml),
[research abilities](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/voidmulti.sc2mod/base.sc2data/GameData/AbilData.xml),
and [Galaxy native functions](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/core.sc2mod/base.sc2data/TriggerLibs/natives.galaxy).
