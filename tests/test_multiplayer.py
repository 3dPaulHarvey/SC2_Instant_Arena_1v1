"""Source regression checks for the first two-human iteration.

These check the ownership and control boundaries in the authored Galaxy code.
They do not simulate SC2 UI events, network synchronization, or gameplay; those
still need the Editor and the two-client checklist in docs/NEXT_1V1_TEST.md.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def without_comments(source):
    # Keep quoted strings intact, including braces in displayed messages.
    tokens = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/'
    return re.sub(tokens, lambda match: match[0] if match[0].startswith('"') else "", source)


def block_after(source, pattern):
    match = re.search(pattern + r"\s*\{", source)
    if match is None:
        raise AssertionError("Galaxy block not found: " + pattern)
    start = match.end()
    depth = 1
    for token in re.finditer(r'"(?:\\.|[^"\\])*"|[{}]', source[start:]):
        if token[0] == "{":
            depth += 1
        elif token[0] == "}":
            depth -= 1
        if depth == 0:
            return source[start:start + token.start()]
    raise AssertionError("Unclosed Galaxy block: " + pattern)


def condition_value(expression, **variables):
    """Evaluate only a Galaxy boolean/integer expression, with supplied names.

    This is used for guard truth tables; it is not a Galaxy/SC2 interpreter.
    The token restriction excludes strings, attributes, indexing and statements.
    """
    if not re.fullmatch(r"[A-Za-z_0-9\s()!<>=&|+\-]+", expression):
        raise AssertionError("Unsupported guard expression: " + expression)
    expression = expression.replace("&&", " and ").replace("||", " or ")
    expression = re.sub(r"!(?!=)", " not ", expression).strip()
    return eval(expression, {"__builtins__": {}}, variables)


class MultiplayerSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = without_comments((ROOT / "src/Arena.galaxy").read_text(encoding="utf-8"))

    def body(self, name):
        return block_after(self.source, r"\b" + name + r"\s*\([^)]*\)")

    def compact(self, text):
        return re.sub(r"\s+", "", text)

    def test_match_detection_requires_active_second_human(self):
        init = self.compact(self.body("ArenaInit"))
        self.assertIn("arenaHumanMatch=PlayerType(ARENA_PLAYER_TWO)==c_playerTypeUser&&PlayerStatus(ARENA_PLAYER_TWO)==c_playerStatusActive;", init)
        self.assertIn("player=ARENA_PLAYER;while(player<=ARENA_PLAYER_TWO)", init)
        panels = block_after(self.body("ArenaInit"), r"if\s*\(ArenaIsHumanPlayer\(player\)\)")
        self.assertIn("ArenaCreatePanel(player);", self.compact(panels))
        human = block_after(self.body("ArenaInit"), r"if\s*\(arenaHumanMatch\)")
        self.assertRegex(human, r"SetAlliance\([^;]*ARENA_PLAYER_TWO[^;]*libNtve_ge_AllianceSetting_Enemy")

    def test_opponent_and_human_slots_are_limited(self):
        allowed = re.search(r"return\s+([^;]+);", self.body("ArenaIsHumanPlayer"))[1]
        for human_match in (False, True):
            for player in range(17):
                with self.subTest(human_match=human_match, player=player):
                    self.assertEqual(condition_value(allowed, player=player, arenaHumanMatch=human_match,
                        ARENA_PLAYER=1, ARENA_PLAYER_TWO=2), player in ({1, 2} if human_match else {1}))
        opponent = self.body("ArenaOpponent")
        human = block_after(opponent, r"if\s*\(arenaHumanMatch\)")
        self.assertIn("return3-player;", self.compact(human))
        self.assertIn("returnARENA_ENEMY;", self.compact(opponent))
        self.assertIn("constintARENA_PLAYER=1;", self.compact(self.source))
        self.assertIn("constintARENA_PLAYER_TWO=2;", self.compact(self.source))
        self.assertIn("constintARENA_ENEMY=15;", self.compact(self.source))

    def test_selections_and_events_are_bound_to_the_acting_player(self):
        selected = self.compact(self.body("ArenaSelectedUnitType"))
        self.assertIn("DialogControlGetSelectedItem(arenaRaceMenu[player],player)", selected)
        self.assertIn("DialogControlGetSelectedItem(arenaUnitMenu[player],player)", selected)
        for name in ("ArenaButtonClicked", "ArenaMenuChanged"):
            with self.subTest(callback=name):
                callback = self.compact(self.body(name))
                self.assertIn("player=EventPlayer();", callback)
                self.assertIn("!ArenaIsHumanPlayer(player)", callback)
        buttons = self.compact(self.body("ArenaButtonClicked"))
        self.assertIn("control==arenaSpawnButton[player]", buttons)
        self.assertIn("ArenaSpawn(player,player);", buttons)
        menus = self.compact(self.body("ArenaMenuChanged"))
        self.assertIn("arenaRaceMenu[player]", menus)
        self.assertIn("arenaUnitMenu[player]", menus)
        self.assertIn("ArenaFillUnitMenu(player);", menus)
        self.assertIn("ArenaRefreshSelection(player);", menus)

    def test_clear_my_army_cannot_clear_opponent(self):
        callback = self.body("ArenaButtonClicked")
        clear = block_after(callback, r"(?:else\s+)?if\s*\(control\s*==\s*arenaClearButton\[player\]\)")
        self.assertEqual(re.findall(r"ArenaClearGroup\(([^)]*)\)", clear), ["arenaArmy[player]"])

    def test_spawn_ownership_and_cap_are_checked_before_creation(self):
        spawn = self.compact(self.body("ArenaSpawn"))
        created_at = spawn.index("UnitCreate(")
        guarded = spawn[:created_at]
        self.assertIn("!ArenaIsHumanPlayer(player)", guarded)
        self.assertIn("owner!=player", guarded)
        self.assertIn("arenaHumanMatch", guarded)
        self.assertIn("owner!=ARENA_ENEMY", guarded)
        self.assertIn("ArenaSelectedUnitType(player)", guarded)
        self.assertIn("army=arenaArmy[owner];", guarded)
        self.assertIn("spawn=arenaSpawnPoint[owner];", guarded)
        self.assertIn("UnitGroupCount(army,c_unitCountAlive)>=ARENA_LIMIT", guarded)
        self.assertIn("constintARENA_LIMIT=100;", self.compact(self.source))
        self.assertIn("UnitCreate(1,unitType,0,owner,spawn,facing)", spawn)

    def test_spawn_guards_allow_only_each_human_or_the_solo_enemy(self):
        human_expression = re.search(r"return\s+([^;]+);", self.body("ArenaIsHumanPlayer"))[1]
        guards = re.findall(r"if\s*\((.*?)\)\s*\{\s*return\s*;",
            self.body("ArenaSpawn").split("unitType =", 1)[0], re.DOTALL)
        self.assertEqual(len(guards), 2)
        allowed = {(False, 1, 1), (False, 1, 15), (True, 1, 1), (True, 2, 2)}
        for human_match in (False, True):
            for player in range(17):
                for owner in range(17):
                    variables = dict(player=player, owner=owner, arenaHumanMatch=human_match,
                        ARENA_PLAYER=1, ARENA_PLAYER_TWO=2, ARENA_ENEMY=15)
                    variables["ArenaIsHumanPlayer"] = lambda candidate: condition_value(
                        human_expression, **dict(variables, player=candidate))
                    rejected = any(condition_value(guard, **variables) for guard in guards)
                    with self.subTest(human_match=human_match, player=player, owner=owner):
                        self.assertEqual(not rejected, (human_match, player, owner) in allowed)

    def test_only_solo_enemy_units_receive_automatic_orders(self):
        spawn = self.body("ArenaSpawn")
        automatic = block_after(spawn, r"if\s*\(!arenaHumanMatch\s*&&\s*owner\s*==\s*ARENA_ENEMY\)")
        self.assertGreater(spawn.count("UnitIssueOrder("), 0)
        self.assertEqual(spawn.count("UnitIssueOrder("), automatic.count("UnitIssueOrder("))
        self.assertEqual(self.source.count("UnitIssueOrder("), spawn.count("UnitIssueOrder("))

    def test_sandbox_enemy_and_reset_are_guarded_in_human_mode(self):
        buttons = self.compact(self.body("ArenaButtonClicked"))
        self.assertIn("!arenaHumanMatch&&control==arenaEnemyButton[player]", buttons)
        self.assertIn("!arenaHumanMatch&&control==arenaResetButton[player]", buttons)
        self.assertIn("ArenaSpawn(player,ARENA_ENEMY);", buttons)
    def test_speed_control_is_host_only_and_labels_sync_for_both_humans(self):
        speed = self.compact(self.body("ArenaSpeedChanged"))
        self.assertIn("EventPlayer()!=ARENA_PLAYER", speed)
        refresh = self.body("ArenaRefreshSpeed")
        human = block_after(refresh, r"if\s*\(arenaHumanMatch\)")
        self.assertIn("arenaSpeedLabel[ARENA_PLAYER_TWO]", human)
        self.assertIn("PlayerGroupSingle(ARENA_PLAYER_TWO)", human)
        host = block_after(self.body("ArenaCreatePanel"), r"if\s*\(player\s*==\s*ARENA_PLAYER\)")
        self.assertIn("arenaSpeedSlider = DialogControlCreate", host)
        self.assertEqual(self.source.count("arenaSpeedSlider = DialogControlCreate"), 1)

    def test_each_panel_registers_its_own_button_and_menu_events(self):
        panel = self.compact(self.body("ArenaCreatePanel"))
        self.assertIn("DialogSetVisible(arenaDialog[player],PlayerGroupSingle(player),true)", panel)
        self.assertIn("TriggerAddEventDialogControl(buttonTrigger,player,", panel)
        self.assertIn("TriggerAddEventDialogControl(menuTrigger,player,arenaRaceMenu[player],", panel)
        self.assertIn("TriggerAddEventDialogControl(menuTrigger,player,arenaUnitMenu[player],", panel)

    def test_status_reads_both_armies_and_updates_only_its_panel(self):
        status = self.compact(self.body("ArenaRefreshStatusForPlayer"))
        self.assertIn("UnitGroupCount(arenaArmy[player],c_unitCountAlive)", status)
        self.assertIn("ArenaOpponent(player)", status)
        self.assertIn("arenaStatusLabel[player]", status)
        self.assertIn("PlayerGroupSingle(player)", status)


if __name__ == "__main__":
    unittest.main()
