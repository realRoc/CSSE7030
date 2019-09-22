#!/usr/bin/env python3

import inspect
from pathlib import Path

from testrunner import (AttributeGuesser, OrderedTestCase, TestMaster,
                        RedirectStdIO, skipIfFailed)


class TestA1(OrderedTestCase):
    a1: ...


class TestDesign(TestA1):
    def test_clean_import(self):
        """ test no prints on import """
        self.assertIsCleanImport(self.a1, msg="You should not be printing on import for a1.py")

    def test_functions_defined(self):
        """ test all specified functions defined """
        a1 = AttributeGuesser(self.a1, fail=False)

        self.aggregate(self.assertIsNotNone, a1.get_position_in_direction, tag='get_position_in_direction')
        self.aggregate(self.assertIsNotNone, a1.get_tile_at_position, tag='get_tile_at_position')
        self.aggregate(self.assertIsNotNone, a1.get_tile_in_direction, tag='get_tile_in_direction')
        self.aggregate(self.assertIsNotNone, a1.remove_from_level, tag='remove_from_level')
        self.aggregate(self.assertIsNotNone, a1.move, tag='move')
        self.aggregate(self.assertIsNotNone, a1.print_level, tag='print_level')
        self.aggregate(self.assertIsNotNone, a1.attack, tag='attack')
        self.aggregate(self.assertIsNotNone, a1.tile_status, tag='tile_status')
        self.aggregate(self.assertIsNotNone, a1.get_position_in_direction, tag='main')

        self.aggregate_tests()

    def test_functions_defined_correctly(self):
        """ test all specified functions defined correctly """
        a1 = AttributeGuesser.get_wrapped_object(self.a1)

        self.aggregate(self.assertFunctionDefined, a1, 'get_position_in_direction', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'get_tile_at_position', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'get_tile_in_direction', 3)
        self.aggregate(self.assertFunctionDefined, a1, 'remove_from_level', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'move', 3)
        self.aggregate(self.assertFunctionDefined, a1, 'print_level', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'attack', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'tile_status', 2)
        self.aggregate(self.assertFunctionDefined, a1, 'main', 0)

        self.aggregate_tests()

    def test_doc_strings(self):
        """ test all functions have documentation strings """
        a1 = AttributeGuesser.get_wrapped_object(self.a1)
        for attr_name, attr in inspect.getmembers(a1, predicate=inspect.isfunction):
            self.aggregate(self.assertDocString, a1, attr_name)

        self.aggregate_tests()


class TestFunctionality(TestA1):
    level = (
        " $ \n"
        "@^I\n"
        "###"
    )


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'get_position_in_direction')
class TestGetPositionInDirection(TestFunctionality):
    def test_right(self):
        """ test 'r' direction """
        result = self.a1.get_position_in_direction((0, 0), 'r')
        self.assertEqual(result, (1, 0))
        result = self.a1.get_position_in_direction((100, 100), 'r')
        self.assertEqual(result, (101, 100))

    def test_left(self):
        """ test 'l' direction """
        result = self.a1.get_position_in_direction((0, 0), 'l')
        self.assertEqual(result, (-1, 0))
        result = self.a1.get_position_in_direction((100, 100), 'l')
        self.assertEqual(result, (99, 100))

    def test_up(self):
        """ test 'u' direction """
        result = self.a1.get_position_in_direction((0, 0), 'u')
        self.assertEqual(result, (0, 1))

        result = self.a1.get_position_in_direction((100, 100), 'u')
        self.assertEqual(result, (100, 101))

    def test_down(self):
        """ test 'd' direction """
        result = self.a1.get_position_in_direction((0, 0), 'd')
        self.assertEqual(result, (0, -1))
        result = self.a1.get_position_in_direction((100, 100), 'd')
        self.assertEqual(result, (100, 99))


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'get_tile_at_position')
class TestGetTileAtPosition(TestFunctionality):
    def test_get_tile_at_position(self):
        """ test getting a tile for all symbols """
        self.assertEqual(self.a1.get_tile_at_position(self.level, (0, 2)), ' ')
        self.assertEqual(self.a1.get_tile_at_position(self.level, (1, 1)), '^')
        self.assertEqual(self.a1.get_tile_at_position(self.level, (2, 0)), '#')
        self.assertEqual(self.a1.get_tile_at_position(self.level, (1, 2)), '$')
        self.assertEqual(self.a1.get_tile_at_position(self.level, (0, 1)), '@')
        self.assertEqual(self.a1.get_tile_at_position(self.level, (2, 1)), 'I')


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'get_tile_in_direction')
class TestGetTileInDirection(TestFunctionality):
    def test_right(self):
        """ test 'r' direction """
        result = self.a1.get_tile_in_direction(self.level, (1, 1), 'r')
        self.assertEqual(result, 'I')

    def test_left(self):
        """ test 'l' direction """
        result = self.a1.get_tile_in_direction(self.level, (1, 1), 'l')
        self.assertEqual(result, '@')

    def test_up(self):
        """ test 'u' direction """
        result = self.a1.get_tile_in_direction(self.level, (1, 1), 'u')
        self.assertEqual(result, '$')

    def test_down(self):
        """ test 'd' direction """
        result = self.a1.get_tile_in_direction(self.level, (1, 1), 'd')
        self.assertEqual(result, '#')


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'remove_from_level')
class TestRemoveFromLevel(TestFunctionality):
    def test_remove_symbol(self):
        """ test removes symbol """
        expected = (
            " $ \n"
            "@ I\n"
            "###"
        )
        result = self.a1.remove_from_level(self.level, (1, 1))
        self.assertEqual(result, expected)

    def test_remove_air(self):
        """ test no change """
        result = self.a1.remove_from_level(self.level, (0, 2))
        self.assertEqual(result, self.level)


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'move')
class TestMove(TestFunctionality):
    level = (
        "           \n"
        "         # \n"
        "    #    # \n"
        "   # # $ # \n"
        "###########"
    )

    def test_move_right(self):
        """ test move right """
        pos = (1, 1)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (2, 1))

    def test_move_left(self):
        """ test move left """
        pos = (1, 1)
        result = self.a1.move(self.level, pos, 'l')
        self.assertEqual(result, (0, 1))

    def test_move_up(self):
        """ test move up (fall back) """
        pos = (1, 1)
        result = self.a1.move(self.level, pos, 'u')
        self.assertEqual(result, (1, 1))

    def test_move_down(self):
        """ test move down (no move) """
        pos = (1, 1)
        result = self.a1.move(self.level, pos, 'd')
        self.assertEqual(result, (1, 1))

    def test_move_up_wall_r(self):
        """ test move up wall (right) """
        pos = (2, 1)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (3, 2))

    def test_move_up_wall_l(self):
        """ test move up wall (left) """
        pos = (6, 1)
        result = self.a1.move(self.level, pos, 'l')
        self.assertEqual(result, (5, 2))

    def test_move_down_wall_r(self):
        """ test move down wall (right) """
        pos = (5, 2)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (6, 1))

    def test_move_down_wall_l(self):
        """ test move down wall (left) """
        pos = (3, 2)
        result = self.a1.move(self.level, pos, 'l')
        self.assertEqual(result, (2, 1))

    def test_move_up_multi_wall_r(self):
        """ test move up multiple walls (right) """
        pos = (8, 1)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (9, 4))

    def test_move_up_multi_wall_l(self):
        """ test move up multiple walls (left) """
        pos = (10, 1)
        result = self.a1.move(self.level, pos, 'l')
        self.assertEqual(result, (9, 4))

    def test_move_down_multi_wall_r(self):
        """ test move down multiple walls (right) """
        pos = (9, 4)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (10, 1))

    def test_move_down_multi_wall_l(self):
        """ test move down multiple walls (left) """
        pos = (9, 4)
        result = self.a1.move(self.level, pos, 'l')
        self.assertEqual(result, (8, 1))

    def test_move_up_multi(self):
        """ test move up multi """
        level = (
            "   \n" +
            " # \n" * 20 +
            "###"
        )

        pos = (0, 1)
        result = self.a1.move(level, pos, 'r')
        self.assertEqual(result, (1, 21))

    def test_move_onto_symbol(self):
        """ test move onto symbol """
        pos = (6, 1)
        result = self.a1.move(self.level, pos, 'r')
        self.assertEqual(result, (7, 1))

    def test_check_order(self):
        """ test wall check before air """
        level = (
            "   \n"
            " # \n"
            "   \n"
            "###"
        )
        pos = (0, 2)
        result = self.a1.move(level, pos, 'r')
        self.assertEqual(result, (1, 3))

    def test_fall_up(self):
        """ test falling after moving up """
        pos = (2, 3)
        result = self.a1.move(self.level, pos, 'u')
        self.assertEqual(result, (2, 1))

    def test_fall_down(self):
        """ test falling after moving down """
        pos = (2, 4)
        result = self.a1.move(self.level, pos, 'd')
        self.assertEqual(result, (2, 1))

    def test_fall_onto_symbol(self):
        """ test falling onto symbol """
        level = (
            "  \n"
            "# \n"
            "#$\n"
            "# \n"
            "##"
        )
        pos = (0, 4)
        result = self.a1.move(level, pos, 'r')
        self.assertEqual(result, (1, 3))

    @skipIfFailed(test_name=test_move_up_multi_wall_r.__name__)
    def test_move_not_recursive(self):
        """ test move is not recursive """
        self.assertIsNotRecursive(self.a1.move, self.level, (8, 1), 'r')


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'print_level')
class TestPrintLevel(TestFunctionality):
    def test_print_level_1(self):
        """ test print level 1"""
        level_1 = self.a1_support.load_level('level1.txt')

        expected = (
            "                                     \n"
            "                             $       \n"
            "           @               ####      \n"
            "          ###             ######     \n"
            "*       #######  $    $  ########   I\n"
            "#####################################\n"
        )

        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.print_level(level_1, (0, 1))

        self.assertEqual(stdio.stdout, expected)
        self.assertIsNone(result)

    def test_print_level_start(self):
        """ test print level (start) """
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.print_level(self.level, (0, 2))

        self.assertEqual(stdio.stdout, "*$ \n@^I\n###\n")
        self.assertIsNone(result)

    def test_print_level_middle(self):
        """ test print level (middle) """
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.print_level(self.level, (1, 1))

        self.assertEqual(stdio.stdout, " $ \n@*I\n###\n")
        self.assertIsNone(result)

    def test_print_level_last(self):
        """ test print level (last) """
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.print_level(self.level, (2, 0))

        self.assertEqual(stdio.stdout, " $ \n@^I\n##*\n")
        self.assertIsNone(result)


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'tile_status')
class TestTileStatus(TestFunctionality):
    level = (
        " @$*^I\n"
        "######"
    )

    def test_goal(self):
        """ test goal """
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.tile_status(self.level, (5, 1))

        self.assertEqual(result, ('I', self.level))
        self.assertEqual(stdio.stdout, "Congratulations! You finished the level\n")

    def test_monster(self):
        """ test monster """
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.tile_status(self.level, (1, 1))

        self.assertEqual(result, ('@', self.level))
        self.assertEqual(stdio.stdout, "Hit a monster!\n")

    def test_coin(self):
        """ test coin """
        result = self.a1.tile_status(self.level, (2, 1))
        self.assertEqual(result, ('$', " @ *^I\n######"))

    def test_checkpoint(self):
        """ test checkpoint """
        result = self.a1.tile_status(self.level, (4, 1))
        self.assertEqual(result, ('^', " @$* I\n######"))

    def test_air(self):
        """ test air """
        result = self.a1.tile_status(self.level, (0, 1))
        self.assertEqual(result, (' ', self.level))

    def test_wall(self):
        """ test wall """
        result = self.a1.tile_status(self.level, (0, 0))
        self.assertEqual(result, ('#', self.level))


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'attack')
class TestAttack(TestFunctionality):
    def test_attack_left(self):
        """ test attack on left """
        level = (
            "@ \n"
            "##"
        )
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.attack(level, (1, 1))

        self.assertEqual(result, "  \n##")
        self.assertEqual(stdio.stdout, "Attacking the monster on your left!\n")

    def test_attack_right(self):
        """ test attack on right"""
        level = (
            " @\n"
            "##"
        )
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.attack(level, (0, 1))

        self.assertEqual(result, "  \n##")
        self.assertEqual(stdio.stdout, "Attacking the monster on your right!\n")

    def test_attack_empty(self):
        """ test attack empty """
        level = (
            "  \n"
            "##"
        )
        with RedirectStdIO(stdout=True) as stdio:
            result = self.a1.attack(level, (0, 1))

        self.assertEqual(result, "  \n##")
        self.assertEqual(stdio.stdout, "No monsters to attack!\n")

    def test_attack_both(self):
        """ test attack both """
        level = (
            "@ @\n"
            "###"
        )

        output = (
            "Attacking the monster on your left!\n"
            "Attacking the monster on your right!\n"
        )

        with RedirectStdIO(stdout=True) as stdio:
            updated_level = self.a1.attack(level, (1, 1))
            final_level = self.a1.attack(updated_level, (1, 1))

        self.assertEqual(updated_level, "  @\n###")
        self.assertEqual(final_level, "   \n###")
        self.assertEqual(stdio.stdout, output)


@skipIfFailed(TestDesign, TestDesign.test_functions_defined.__name__, 'main')
class TestMain(TestA1):
    PATH = Path(__file__).parent / 'test_data'

    def _run_main(self, in_filename, out_filename):
        with open(self.PATH / in_filename) as in_file, \
                open(self.PATH / out_filename) as out_file:
            inputs = in_file.read()
            output = out_file.read()

        error = None
        with RedirectStdIO(stdinout=True) as stdio:
            stdio.stdin = inputs
            try:
                self.a1.main()
            except EOFError as err:
                error = err

        if error is not None:
            raise AssertionError(
                f'Your program is asking for too much input\nEOFError: {error}\n\n{stdio.stdinout}'
            ).with_traceback(error.__traceback__)

        return output, stdio

    def assertMain(self, in_filename, out_filename):
        output, stdio = self._run_main(in_filename, out_filename)
        self.assertMultiLineEqual(stdio.stdinout, output)
        if stdio.stdin != '':
            self.fail(msg="Not all input was read")

    def generate_out_file(self, in_filename, out_filename):
        p = self.PATH / out_filename
        open(p, 'w').close()

        _, stdio = self._run_main(in_filename, out_filename)

        with open(p, 'w') as f:
            f.write(stdio.stdinout)

    def test_run_level_1(self):
        """ test can run level 1 """
        self.assertMain('level1.in', 'level1.out')

    def test_reach_goal(self):
        """ test can reach goal single move """
        self.assertMain('goal.in', 'goal.out')

    def test_can_quit(self):
        """ test can quit """
        self.assertMain('quit.in', 'quit.out')

    def test_output_help(self):
        """ test can output help """
        self.assertMain('help.in', 'help.out')

    def test_multiple_move(self):
        """ test multiple moves """
        self.assertMain('flat.in', 'flat.out')

    def test_score_update_once(self):
        """ test collect coin and score updates """
        self.assertMain('coins_single.in', 'coins_single.out')

    def test_score_updates(self):
        """ test collect coin and score updates """
        self.assertMain('coins_multi.in', 'coins_multi.out')

    def test_death(self):
        """ test death on monster """
        self.assertMain('game_over.in', 'game_over.out')

    def test_reset_to_checkpoint(self):
        """ test resets to checkpoint with 'n' """
        self.assertMain('checkpoint_single.in', 'checkpoint_single.out')

    def test_resets_to_last_checkpoint(self):
        """ test resets to last checkpoint """
        self.assertMain('checkpoint_last.in', 'checkpoint_last.out')

    def test_reset_to_checkpoint_on_death(self):
        """ test resets to checkpoint on death """
        self.assertMain('checkpoint_death.in', 'checkpoint_death.out')

    @skipIfFailed(test_name=test_reach_goal.__name__)
    def test_main_not_recursive(self):
        """ test the main function is not recursive """
        self.assertIsNotRecursive(self.assertMain, 'flat.in', 'flat.out')


def main():
    test_cases = [
        TestDesign,
        TestGetPositionInDirection,
        TestGetTileAtPosition,
        TestGetTileInDirection,
        TestRemoveFromLevel,
        TestMove,
        TestPrintLevel,
        TestAttack,
        TestTileStatus,
        TestMain
    ]

    master = TestMaster(max_diff=None,  # set to None to see full output
                        # suppress_stdout=False,
                        # ignore_import_fails=True,
                        timeout=1,
                        include_no_print=True,
                        scripts=[
                            ('a1', 'a1.py'),
                            ('a1_support', 'a1_support.py')
                        ])
    master.run(test_cases)


if __name__ == '__main__':
    main()
