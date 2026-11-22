"""Exercise battle preparation using authored Galaxy and catalog/API substitutes.

These validate traversal, upgrade scope, symmetry and spawn readiness. They do
not replace native SC2 checks of catalog field access and ability availability.
"""
import re
import unittest

from test_favorites import GalaxyBody, SOURCE
from test_multiplayer import block_after


class CombatSetupTests(unittest.TestCase):
    def setUp(self):
        self.levels = {}
        self.edits = []
        self.structures = []
        self.galaxy = GalaxyBody({
            "c_gameCatalogUpgrade": "Upgrade", "c_gameCatalogUnit": "Unit",
            "c_gameCatalogAbil": "Abil",
            "CatalogEntryIsValid": lambda catalog, entry: entry != "Missing",
            "libNtve_gf_SetUpgradeLevelForPlayer": lambda player, upgrade, level:
                self.levels.__setitem__((player, upgrade), level),
            "ArenaGrantResearch": lambda player, structure: self.structures.append((player, structure)),
            "CatalogFieldValueSet": lambda *args: self.edits.append(args),
            "IntToString": str,
        })
        self.galaxy.load("ArenaGrantUpgrade")
        self.prepare = self.galaxy.load("ArenaPreparePlayer")

    def test_all_sides_get_exactly_one_of_each_weapon_armor_and_shield_upgrade(self):
        expected = {
            "TerranInfantryWeaponsLevel1", "TerranInfantryArmorsLevel1",
            "TerranVehicleWeaponsLevel1", "TerranShipWeaponsLevel1",
            "TerranVehicleAndShipArmorsLevel1",
            "ProtossGroundWeaponsLevel1", "ProtossGroundArmorsLevel1",
            "ProtossAirWeaponsLevel1", "ProtossAirArmorsLevel1", "ProtossShieldsLevel1",
            "ZergMeleeWeaponsLevel1", "ZergMissileWeaponsLevel1", "ZergGroundArmorsLevel1",
            "ZergFlyerWeaponsLevel1", "ZergFlyerArmorsLevel1",
        }
        for player in (1, 2, 15):
            self.prepare(player)
            self.prepare(player)
            self.assertEqual({name: level for (owner, name), level in self.levels.items()
                              if owner == player}, dict.fromkeys(expected, 1))

    def test_research_buildings_cover_all_races_without_general_upgrade_buildings(self):
        self.prepare(1)
        structures = {structure for player, structure in self.structures}
        self.assertEqual(structures, {
            "BarracksTechLab", "FactoryTechLab", "StarportTechLab", "GhostAcademy", "FusionCore",
            "TwilightCouncil", "TemplarArchive", "DarkShrine", "RoboticsBay", "FleetBeacon",
            "Hatchery", "Lair", "Hive", "SpawningPool", "BanelingNest", "RoachWarren",
            "HydraliskDen", "LurkerDenMP", "InfestationPit", "UltraliskCavern",
        })
        self.assertTrue(structures.isdisjoint({"EngineeringBay", "Armory", "Forge", "CyberneticsCore", "EvolutionChamber", "Spire"}))

    def test_research_follows_live_cards_skipping_passives_cancel_and_obsolete_entries(self):
        fields = {
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[0].Type"): "AbilCmd",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[0].AbilCmd"): "Research,0",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[1].Type"): "Passive",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[2].Type"): "AbilCmd",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[2].AbilCmd"): "Research,30",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[3].Type"): "AbilCmd",
            ("Unit", "TestLab", "CardLayouts[0].LayoutButtons[3].AbilCmd"): "Train,0",
            ("Unit", "TestLab", "CardLayouts[1].LayoutButtons[0].Type"): "AbilCmd",
            ("Unit", "TestLab", "CardLayouts[1].LayoutButtons[0].AbilCmd"): "Research,1",
            ("Unit", "TestLab", "CardLayouts[1].LayoutButtons[1].Type"): "AbilCmd",
            ("Abil", "Research", "InfoArray[0].Upgrade"): "Stimpack",
            ("Abil", "Research", "InfoArray[1].Upgrade"): "ShieldWall",
            ("Abil", "Research", "InfoArray[2].Upgrade"): "ObsoleteResearch",
        }
        counts = {"CardLayouts": 2, "CardLayouts[0].LayoutButtons": 4, "CardLayouts[1].LayoutButtons": 2}
        self.galaxy.scope.update({
            "CatalogFieldValueCount": lambda catalog, entry, path, player: counts[path],
            "CatalogFieldValueGet": lambda catalog, entry, path, player: fields.get((catalog, entry, path), ""),
            "StringToAbilCmd": lambda value: value.split(","),
            "AbilityCommandGetAbility": lambda command: command[0],
            "AbilityCommandGetCommand": lambda command: int(command[1]),
            "CatalogEntryScope": lambda catalog, entry: "CAbilResearch" if entry == "Research" else "CAbilTrain",
        })
        research = self.galaxy.load("ArenaGrantResearch")
        research(2, "TestLab")
        self.assertEqual(self.levels, {(2, "Stimpack"): 1, (2, "ShieldWall"): 1})
        self.galaxy.scope["ArenaGrantUpgrade"](2, "Missing")
        self.assertEqual(len(self.levels), 2)

    def test_sandbox_changes_are_limited_to_hellion_modes_and_interceptor_cost(self):
        self.prepare(15)
        self.assertEqual(self.edits, [
            ("Abil", "MorphToHellion", "CmdButtonArray[Execute].Requirements", 15, ""),
            ("Abil", "MorphToHellionTank", "CmdButtonArray[Execute].Requirements", 15, ""),
            ("Abil", "CarrierHangar", "InfoArray[Ammo1].Resource[Minerals]", 15, "0"),
        ])
        self.assertNotIn("TechTreeRequirementsEnable(", SOURCE)

    def test_setup_runs_before_panels_for_both_humans_and_solo_enemy(self):
        init = block_after(SOURCE, r"void ArenaInit\s*\(\)")
        for player in ("ARENA_PLAYER", "ARENA_PLAYER_TWO", "ARENA_ENEMY"):
            self.assertLess(init.index(f"ArenaPreparePlayer({player});"), init.index("ArenaCreatePanel(player);"))
        spawn = block_after(SOURCE, r"void ArenaSpawn\s*\([^)]*\)")
        self.assertLess(spawn.index("spawned == null"), spawn.index("ArenaPrepareUnit(spawned);"))
        self.assertLess(spawn.index("ArenaPrepareUnit(spawned);"), spawn.index("UnitIssueOrder("))

    def test_new_units_refill_vitals_and_carriers_only_fill_missing_ammo(self):
        for carrier, capacity, current in ((False, 0, 0), (True, 8, 4), (True, 8, 8), (True, 10, 4)):
            with self.subTest(carrier=carrier, capacity=capacity, current=current):
                vitals, ammo = [], []
                self.galaxy.scope.update({
                    "c_unitPropLifePercent": "life", "c_unitPropShieldsPercent": "shields",
                    "c_unitPropEnergyPercent": "energy",
                    "UnitSetPropertyFixed": lambda *args: vitals.append(args),
                    "UnitAbilityExists": lambda unit, ability: carrier,
                    "UnitGetOwner": lambda unit: 2,
                    "CatalogFieldValueGet": lambda *args: str(capacity),
                    "StringToInt": int,
                    "UnitMagazineCount": lambda *args: current,
                    "AbilityCommand": lambda name, index: (name, index),
                    "UnitMagazineArm": lambda *args: ammo.append(args),
                })
                prepare = self.galaxy.load("ArenaPrepareUnit")
                prepare("unit")
                self.assertEqual(vitals, [("unit", vital, 100.0) for vital in ("life", "shields", "energy")])
                self.assertEqual(ammo, [("unit", ("CarrierHangar", 0), capacity - current)] if carrier and current < capacity else [])

    def test_formations_are_mirrored_spaced_and_within_each_spawn_area(self):
        self.galaxy.scope.update({
            "arenaSpawnPoint": {1: (9, 16), 2: (23, 16), 15: (23, 16)},
            "PointGetX": lambda point: point[0], "PointGetY": lambda point: point[1],
            "IntToFixed": float, "Point": lambda x, y: (x, y),
        })
        point = self.galaxy.load("ArenaFormationPoint")
        for quantity in (1, 5, 10):
            left = [point(1, index, quantity) for index in range(quantity)]
            self.assertEqual(len(set(left)), quantity)
            for owner in (2, 15):
                right = [point(owner, index, quantity) for index in range(quantity)]
                self.assertEqual(right, [(32 - x, y) for x, y in left])
            self.assertTrue(all(7 <= x <= 9 and 12 <= y <= 20 for x, y in left))
        self.assertEqual(point(1, 0, 1), (9, 16))


if __name__ == "__main__":
    unittest.main()
