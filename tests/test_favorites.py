"""Exercise authored favorites and batch-spawn logic with SC2 API substitutes.

This executes a deliberately small subset of Galaxy statements from the real
function bodies. Engine calls are substituted; UI rendering, event delivery,
and SC2 placement still require the in-game checklist.
"""

from pathlib import Path
import re
import unittest

from test_multiplayer import block_after, without_comments


ROOT = Path(__file__).resolve().parents[1]
SOURCE = without_comments((ROOT / "src/Arena.galaxy").read_text(encoding="utf-8"))


def expression(source):
    # Rewrite operators only outside string literals.
    tokens = re.split(r'("(?:\\.|[^"\\])*")', source)
    for index in range(0, len(tokens), 2):
        value = tokens[index].replace("&&", " and ").replace("||", " or ")
        value = re.sub(r"!(?!=)", " not ", value)
        for original, replacement in (("true", "True"), ("false", "False"), ("null", "None")):
            value = re.sub(r"\b" + original + r"\b", replacement, value)
        tokens[index] = value
    return "".join(tokens).strip()


class GalaxyBody:
    """Translate only the statement forms used by these small authored handlers.

    Unsupported control flow fails the test instead of silently approximating
    gameplay. We run the production assignments and conditions, not a Python
    reimplementation of the favorites or spawn algorithm.
    """

    def __init__(self, scope):
        constants = {name: int(value) for name, value in re.findall(r"const\s+int\s+(\w+)\s*=\s*(\d+)\s*;", SOURCE)}
        self.scope = {"__builtins__": {}, **constants, **scope}

    def load(self, name):
        signature = re.search(r"\b(?:void|bool|int|string|point)\s+" + name + r"\s*\(([^)]*)\)", SOURCE)
        if signature is None:
            raise AssertionError("Galaxy function not found: " + name)
        parameters = [part.strip().split()[-1] for part in signature[1].split(",") if part.strip()]
        body = block_after(SOURCE, r"\b" + name + r"\s*\([^)]*\)")
        lines = ["def " + name + "(" + ", ".join(parameters) + "):"]
        indent = 1
        pending = ""

        def emit(statement, block=False):
            statement = statement.strip()
            if not statement:
                return
            if block:
                match = re.fullmatch(r"(if|while|else\s+if)\s*\(([\s\S]*)\)", statement)
                if match:
                    keyword = "elif" if match[1].startswith("else") else match[1]
                    statement = keyword + " (" + expression(match[2]) + "):"
                elif statement == "else":
                    statement = "else:"
                else:
                    raise AssertionError("Unsupported Galaxy block: " + statement)
            else:
                declaration = re.fullmatch(r"(?:int|bool|string|fixed|unitgroup|unit|point|text|trigger|abilcmd)\s+(\w+)(?:\s*=\s*([\s\S]*))?", statement)
                if declaration:
                    statement = declaration[1] + " = " + (expression(declaration[2]) if declaration[2] else "None")
                else:
                    statement = expression(statement)
            lines.append("    " * indent + statement)

        for token in re.findall(r'"(?:\\.|[^"\\])*"|[^"{};]+|[{};]', body):
            if token == "{":
                emit(pending, block=True)
                pending = ""
                indent += 1
            elif token == "}":
                if pending.strip():
                    raise AssertionError("Unterminated Galaxy statement: " + pending)
                pending = ""
                indent -= 1
            elif token == ";":
                emit(pending)
                pending = ""
            else:
                pending += token
        if pending.strip() or indent != 1:
            raise AssertionError("Unbalanced Galaxy body: " + name)
        exec("\n".join(lines), self.scope)
        return self.scope[name]


class FavoritesTests(unittest.TestCase):
    def setUp(self):
        self.favorites = [["Marine", "VoidRay", "Queen"] for _ in range(3)]
        self.selected = ["Marine"] * 3
        self.race_menu = [100, 101, 102]
        self.unit_menu = [200, 201, 202]
        self.selection = {101: 1, 102: 1, 201: 1, 202: 1}
        self.items = {}
        self.text = {}
        self.event_player = 1
        self.event_control = 201
        self.spawns = []
        self.buttons = [[[1000 * player + 10 * slot + button for button in range(3)]
                         for slot in range(3)] for player in range(3)]
        self.galaxy = GalaxyBody({
            "arenaHumanMatch": True,
            "arenaFavoriteUnit": self.favorites,
            "arenaSelectedUnit": self.selected,
            "arenaFavoriteButton": self.buttons,
            "arenaFavoriteLabel": [[600 + 10 * player + slot for slot in range(3)] for player in range(3)],
            "arenaRaceMenu": self.race_menu,
            "arenaUnitMenu": self.unit_menu,
            "arenaEnemyButton": [300, 301, 302],
            "arenaClearButton": [400, 401, 402],
            "arenaResetButton": [500, 501, 502],
            "EventPlayer": lambda: self.event_player,
            "EventDialogControl": lambda: self.event_control,
            "PlayerGroupSingle": lambda player: player,
            "StringToText": lambda value: value,
            "UnitTypeGetName": lambda value: value,
            "IntToString": str,
            "libNtve_gf_SetDialogItemText": lambda control, text, player: self.text.__setitem__(control, text),
            "c_triggerControlPropertyTooltip": 1,
            "DialogControlSetPropertyAsText": lambda *args: None,
            "DialogControlGetSelectedItem": lambda control, player: self.selection[control],
            "DialogControlSelectItem": lambda control, player, index: self.selection.__setitem__(control, index),
            "DialogControlRemoveAllItems": lambda control, player: self.items.__setitem__(control, []),
            "DialogControlAddItem": lambda control, player, item: self.items.setdefault(control, []).append(item),
            "ArenaRefreshStatus": lambda: None,
            "ArenaSpawn": lambda *args: self.spawns.append(args),
        })
        for name in ("ArenaIsHumanPlayer", "ArenaUnitType", "ArenaUnitCount", "ArenaSelectedUnitType",
                     "ArenaRefreshSelection", "ArenaFavoriteQuantity", "ArenaRefreshFavorites", "ArenaAddFavorite", "ArenaFillUnitMenu",
                     "ArenaMenuChanged", "ArenaButtonClicked"):
            self.galaxy.load(name)

    def test_each_player_starts_with_three_populated_slots_and_nine_buttons(self):
        compact = re.sub(r"\s+", "", SOURCE)
        self.assertIn("string[3][3]arenaFavoriteUnit;", compact)
        self.assertIn("int[3][3]arenaFavoriteLabel;", compact)
        self.assertIn("int[3][3][3]arenaFavoriteButton;", compact)
        panel = block_after(SOURCE, r"\bArenaCreatePanel\s*\([^)]*\)")
        for slot, unit in enumerate(("Marine", "VoidRay", "Queen")):
            self.assertRegex(panel, rf'arenaFavoriteUnit\[player\]\[{slot}\]\s*=\s*"{unit}"')

    def test_dropdown_adds_fifo_without_changing_the_other_players_slots(self):
        add = self.galaxy.scope["ArenaAddFavorite"]
        add(1, "Marauder")
        self.assertEqual(self.favorites[1], ["VoidRay", "Queen", "Marauder"])
        self.assertEqual([self.text[610 + slot] for slot in range(3)], self.favorites[1])
        self.assertEqual(self.favorites[2], ["Marine", "VoidRay", "Queen"])
        add(1, "Stalker")
        add(1, "Zergling")
        add(1, "Queen")
        self.assertEqual(self.favorites[1], ["Stalker", "Zergling", "Queen"])

    def test_selecting_a_unit_can_add_the_same_unit_again_and_placeholder_is_ignored(self):
        changed = self.galaxy.scope["ArenaMenuChanged"]
        self.event_player, self.event_control = 2, 202
        self.selection[102] = 3
        for expected in (["VoidRay", "Queen", "Zergling"], ["Queen", "Zergling", "Zergling"]):
            self.selection[202] = 2  # First real unit follows the placeholder.
            changed(False, True)
            self.assertEqual(self.favorites[2], expected)
            self.assertEqual(self.selected[2], "Zergling")
            self.assertEqual(self.selection[202], 1)
        changed(False, True)
        self.assertEqual(self.favorites[2], ["Queen", "Zergling", "Zergling"])
        self.assertEqual(self.spawns, [])

    def test_race_change_refills_dropdown_without_inserting_a_favorite(self):
        self.event_control = 101
        self.selection[101] = 3
        self.galaxy.scope["ArenaMenuChanged"](False, True)
        self.assertEqual(self.favorites[1], ["Marine", "VoidRay", "Queen"])
        self.assertEqual(self.selected[1], "Zergling")
        self.assertEqual(self.selection[201], 1)
        self.assertEqual(len(self.items[201]), 18)  # Placeholder plus 17 Zerg units.
        self.assertIn("favorites", self.items[201][0].lower())
        self.assertEqual(self.spawns, [])

    def test_each_of_the_nine_buttons_uses_its_own_players_stored_slot(self):
        clicked = self.galaxy.scope["ArenaButtonClicked"]
        for player in (1, 2):
            self.event_player = player
            self.selected[player] = "SCV"  # Current dropdown choice must not affect a favorite.
            for slot, unit in enumerate(self.favorites[player]):
                for button, quantity in enumerate((10, 5, 1)):
                    with self.subTest(player=player, slot=slot, quantity=quantity):
                        self.event_control = self.buttons[player][slot][button]
                        before = len(self.spawns)
                        clicked(False, True)
                        self.assertEqual(self.spawns[before:], [(player, player, unit, quantity)])
        self.event_player, self.event_control = 2, self.buttons[1][0][0]
        before = len(self.spawns)
        clicked(False, True)
        self.assertEqual(len(self.spawns), before)

    def test_inactive_actions_and_nonhuman_events_cannot_mutate_favorites_or_spawn(self):
        for name in ("ArenaButtonClicked", "ArenaMenuChanged"):
            for player, run_actions in ((1, False), (0, True), (15, True)):
                with self.subTest(callback=name, player=player, run_actions=run_actions):
                    self.event_player = player
                    self.event_control = self.buttons[1][0][0] if name == "ArenaButtonClicked" else 201
                    self.galaxy.scope[name](False, run_actions)
        self.assertEqual(self.spawns, [])
        self.assertEqual(self.favorites[1:], [["Marine", "VoidRay", "Queen"]] * 2)

    def test_solo_enemy_still_spawns_one_of_the_last_selected_unit(self):
        self.galaxy.scope["arenaHumanMatch"] = False
        self.selected[1] = "Thor"
        self.event_control = 301
        self.galaxy.scope["ArenaButtonClicked"](False, True)
        self.assertEqual(self.spawns, [(1, 15, "Thor", 1)])


class BatchSpawnTests(unittest.TestCase):
    def make_spawn(self, living, fail_at=None, human_match=True):
        armies = [[] for _ in range(16)]
        armies[1] = list(range(living))
        attempts = []
        refreshes = []

        def create(quantity, unit_type, style, owner, location, facing):
            attempts.append((quantity, unit_type, owner, location))
            if fail_at is not None and len(attempts) == fail_at:
                return []
            return [object()]

        galaxy = GalaxyBody({
            "arenaHumanMatch": human_match,
            "arenaArmy": armies, "arenaSpawnPoint": list(range(16)),
            "c_unitCountAlive": 1, "c_messageAreaSubtitle": 1,
            "c_orderQueueReplace": 1,
            "UnitGroupCount": lambda group, kind: len(group),
            "UnitCreate": create,
            "UnitGroupUnit": lambda group, index: group[index - 1] if len(group) >= index else None,
            "UnitGroupAdd": lambda group, unit: group.append(unit),
            "UnitAbilityExists": lambda *args: False,
            "UnitIssueOrder": lambda *args: None,
            "UIDisplayMessage": lambda *args: None,
            "PlayerGroupSingle": lambda player: player,
            "StringToText": lambda value: value,
            "IntToString": str,
            "ArenaRefreshStatus": lambda: refreshes.append(True),
            "ArenaFormationPoint": lambda owner, index, quantity: owner,
            "ArenaPrepareUnit": lambda unit: None,
        })
        galaxy.load("ArenaIsHumanPlayer")
        spawn = galaxy.load("ArenaSpawn")
        return spawn, armies, attempts, refreshes

    def test_batches_spawn_requested_type_and_stop_at_living_cap(self):
        for living in (0, 90, 95, 98, 99, 100):
            for quantity in (10, 5, 1):
                with self.subTest(living=living, quantity=quantity):
                    spawn, armies, attempts, _ = self.make_spawn(living)
                    spawn(1, 1, "VoidRay", quantity)
                    expected = min(quantity, 100 - living)
                    self.assertEqual(len(armies[1]), living + expected)
                    self.assertEqual(attempts, [(1, "VoidRay", 1, 1)] * expected)
                    self.assertEqual(armies[2], [])

    def test_failed_placement_stops_batch_and_retains_successful_units(self):
        spawn, armies, attempts, refreshes = self.make_spawn(0, fail_at=3)
        spawn(1, 1, "Marine", 10)
        self.assertEqual(len(attempts), 3)
        self.assertEqual(len(armies[1]), 2)
        self.assertTrue(refreshes)

    def test_invalid_requests_cannot_create_units(self):
        for player, owner, unit, quantity in ((1, 2, "Marine", 10), (2, 1, "Marine", 10),
                                             (15, 15, "Marine", 10), (1, 1, "", 10),
                                             (1, 1, "Marine", 0), (1, 1, "Marine", -1),
                                             (1, 1, "Marine", 11)):
            with self.subTest(player=player, owner=owner, unit=unit, quantity=quantity):
                spawn, _, attempts, _ = self.make_spawn(0)
                spawn(player, owner, unit, quantity)
                self.assertEqual(attempts, [])


if __name__ == "__main__":
    unittest.main()
