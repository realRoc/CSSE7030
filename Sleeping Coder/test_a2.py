#!/usr/bin/env python3

__author__ = "Steven Summers"
__version__ = "1.0.0"

import inspect
import itertools
import random

from collections import namedtuple

from testrunner import AttributeGuesser, OrderedTestCase, TestMaster, skipIfFailed

# Would use dataclasses but supporting 3.6
# because that is the default on Lab computers
CodersGameState = namedtuple('CodersGameState', [
    'pickup_pile',
    'putdown_pile',
    'coders',
    'current_player',
    'current_player_hand',
    'current_player_coders',
    'next_player',
    'next_player_hand',
    'next_player_coders',
    'prev_player',
    'prev_player_hand',
    'prev_player_coders',
    'action'
])


class TestA2(OrderedTestCase):
    a2: ...
    a2_support: ...

    def setUp(self):
        if self.a2 is None:
            self.skipTest("Failed to import 'a2.py'")


class TestDesign(TestA2):
    def test_clean_import(self):
        """ test no prints on import """
        self.assertIsCleanImport(self.a2, msg="You should not be printing on import for a1.py")

    def test_classes_defined(self):
        """ test all specified classes defined """
        a2 = AttributeGuesser(self.a2, fail=False)

        if self.aggregate(self.assertIsNotNone, a2.Card, tag='Card'):
            Card = AttributeGuesser(self.a2.Card, fail=False)

            if self.aggregate(self.assertIsNotNone, Card.play, tag='Card.play'):
                self.aggregate(self.assertFunctionDefined, Card, 'play', 3, tag='Card.play')

            if self.aggregate(self.assertIsNotNone, Card.action, tag='Card.action'):
                self.aggregate(self.assertFunctionDefined, Card, 'action', 4, tag='Card.action')

        if self.aggregate(self.assertIsNotNone, a2.NumberCard, tag='NumberCard'):
            NCard = AttributeGuesser(self.a2.NumberCard, fail=False)

            self.aggregate(self.assertFunctionDefined, a2.NumberCard, '__init__', 2, tag='NumberCard.__init__')
            if self.aggregate(self.assertIsNotNone, NCard.get_number, tag='NumberCard.get_number'):
                self.aggregate(self.assertFunctionDefined, NCard, 'get_number', 1, tag='NumberCard.get_number')

            if self.aggregate(self.assertIsNotNone, NCard.play, tag='NumberCard.play'):
                self.aggregate(self.assertFunctionDefined, NCard, 'play', 3, tag='NumberCard.play')

            if self.aggregate(self.assertIsNotNone, NCard.action, tag='NumberCard.action'):
                self.aggregate(self.assertFunctionDefined, NCard, 'action', 4, tag='NumberCard.action')

        if self.aggregate(self.assertIsNotNone, a2.CoderCard, tag='CoderCard'):
            CCard = AttributeGuesser(self.a2.CoderCard, fail=False)

            self.aggregate(self.assertFunctionDefined, a2.CoderCard, '__init__', 2, tag='CoderCard.__init__')
            if self.aggregate(self.assertIsNotNone, CCard.get_name, tag='CoderCard.get_name'):
                self.aggregate(self.assertFunctionDefined, CCard, 'get_name', 1, tag='CoderCard.get_name')

            if self.aggregate(self.assertIsNotNone, CCard.play, tag='CoderCard.play'):
                self.aggregate(self.assertFunctionDefined, CCard, 'play', 3, tag='CoderCard.play')

            if self.aggregate(self.assertIsNotNone, CCard.action, tag='CoderCard.action'):
                self.aggregate(self.assertFunctionDefined, CCard, 'action', 4, tag='CoderCard.action')

        if self.aggregate(self.assertIsNotNone, a2.TutorCard, tag='TutorCard'):
            TCard = AttributeGuesser(self.a2.TutorCard, fail=False)

            self.aggregate(self.assertFunctionDefined, a2.TutorCard, '__init__', 2, tag='TutorCard.__init__')
            if self.aggregate(self.assertIsNotNone, TCard.get_name, tag='TutorCard.get_name'):
                self.aggregate(self.assertFunctionDefined, TCard, 'get_name', 1, tag='TutorCard.get_name')

            if self.aggregate(self.assertIsNotNone, TCard.play, tag='TutorCard.play'):
                self.aggregate(self.assertFunctionDefined, TCard, 'play', 3, tag='TutorCard.play')

            if self.aggregate(self.assertIsNotNone, TCard.action, tag='TutorCard.action'):
                self.aggregate(self.assertFunctionDefined, TCard, 'action', 4, tag='TutorCard.action')

        if self.aggregate(self.assertIsNotNone, a2.KeyboardKidnapperCard, tag='KeyboardKidnapperCard'):
            KCard = AttributeGuesser(self.a2.KeyboardKidnapperCard, fail=False)

            if self.aggregate(self.assertIsNotNone, KCard.play, tag='KeyboardKidnapperCard.play'):
                self.aggregate(self.assertFunctionDefined, KCard, 'play', 3, tag='KeyboardKidnapperCard.play')

            if self.aggregate(self.assertIsNotNone, KCard.action, tag='KeyboardKidnapperCard.action'):
                self.aggregate(self.assertFunctionDefined, KCard, 'action', 4, tag='KeyboardKidnapperCard.action')

        if self.aggregate(self.assertIsNotNone, a2.AllNighterCard, tag='AllNighterCard'):
            ACard = AttributeGuesser(self.a2.AllNighterCard, fail=False)

            if self.aggregate(self.assertIsNotNone, ACard.play, tag='AllNighterCard.play'):
                self.aggregate(self.assertFunctionDefined, ACard, 'play', 3, tag='AllNighterCard.play')

            if self.aggregate(self.assertIsNotNone, ACard.action, tag='AllNighterCard.action'):
                self.aggregate(self.assertFunctionDefined, ACard, 'action', 4, tag='AllNighterCard.action')

        if self.aggregate(self.assertIsNotNone, a2.Deck, tag='Deck'):
            Deck = AttributeGuesser(self.a2.Deck, fail=False)
            if self.aggregate(self.assertFunctionDefined, Deck, '__init__', 2, tag='Deck.__init__'):
                params = inspect.signature(a2.Deck.__init__).parameters
                if self.aggregate(self.assertEqual, 'starting_cards', list(params)[1],
                                  msg="parameter name should be `starting_cards` in Deck.__init__",
                                  tag='Deck.__init__.starting_cards'):
                    self.aggregate(self.assertIsNone, params['starting_cards'].default,
                                   msg="`starting_cards` should default to `None`",
                                   tag='Deck.__init__.starting_cards=None')

            if self.aggregate(self.assertIsNotNone, Deck.get_cards, tag='Deck.get_cards'):
                self.aggregate(self.assertFunctionDefined, Deck, 'get_cards', 1, tag='Deck.get_cards')

            if self.aggregate(self.assertIsNotNone, Deck.get_card, tag='Deck.get_card'):
                self.aggregate(self.assertFunctionDefined, Deck, 'get_card', 2, tag='Deck.get_card')

            if self.aggregate(self.assertIsNotNone, Deck.top, tag='Deck.top'):
                self.aggregate(self.assertFunctionDefined, Deck, 'top', 1, tag='Deck.top')

            if self.aggregate(self.assertIsNotNone, Deck.remove_card, tag='Deck.remove_card'):
                self.aggregate(self.assertFunctionDefined, Deck, 'remove_card', 2, tag='Deck.remove_card')

            if self.aggregate(self.assertIsNotNone, Deck.get_amount, tag='Deck.get_amount'):
                self.aggregate(self.assertFunctionDefined, Deck, 'get_amount', 1, tag='Deck.get_amount')

            if self.aggregate(self.assertIsNotNone, Deck.shuffle, tag='Deck.shuffle'):
                self.aggregate(self.assertFunctionDefined, Deck, 'shuffle', 1, tag='Deck.shuffle')

            if self.aggregate(self.assertIsNotNone, Deck.pick, tag='Deck.pick'):
                if self.aggregate(self.assertFunctionDefined, Deck, 'pick', 2, tag='Deck.pick'):
                    params = inspect.signature(a2.Deck.pick).parameters
                    if self.aggregate(self.assertEqual, 'amount', list(params)[1],
                                      msg="parameter name should be `amount` in Deck.pick",
                                      tag='Deck.pick.amount'):
                        self.aggregate(self.assertEqual, params['amount'].default, 1,
                                       msg="`amount` should default to `1`",
                                       tag='Deck.pick.amount=1')

            if self.aggregate(self.assertIsNotNone, Deck.add_card, tag='Deck.add_card'):
                self.aggregate(self.assertFunctionDefined, Deck, 'add_card', 2, tag='Deck.add_card')

            if self.aggregate(self.assertIsNotNone, Deck.add_cards, tag='Deck.add_cards'):
                self.aggregate(self.assertFunctionDefined, Deck, 'add_cards', 2, tag='Deck.add_cards')

            if self.aggregate(self.assertIsNotNone, Deck.copy, tag='Deck.copy'):
                self.aggregate(self.assertFunctionDefined, Deck, 'copy', 2, tag='Deck.copy')

        if self.aggregate(self.assertIsNotNone, a2.Player, tag='Player'):
            Player = AttributeGuesser(self.a2.Player, fail=False)
            self.aggregate(self.assertFunctionDefined, Player, '__init__', 2, tag='Player.__init__')

            if self.aggregate(self.assertIsNotNone, Player.get_name, tag='Player.get_name'):
                self.aggregate(self.assertFunctionDefined, Player, 'get_name', 1, tag='Player.get_name')

            if self.aggregate(self.assertIsNotNone, Player.get_hand, tag='Player.get_hand'):
                self.aggregate(self.assertFunctionDefined, Player, 'get_hand', 1, tag='Player.get_hand')

            if self.aggregate(self.assertIsNotNone, Player.get_coders, tag='Player.get_coders'):
                self.aggregate(self.assertFunctionDefined, Player, 'get_coders', 1, tag='Player.get_coders')

            if self.aggregate(self.assertIsNotNone, Player.has_won, tag='Player.has_won'):
                self.aggregate(self.assertFunctionDefined, Player, 'has_won', 1, tag='Player.has_won')

        self.aggregate_tests()

    def test_classes_defined_correctly(self):
        """ test all specified classes are defined correctly """
        a2 = AttributeGuesser.get_wrapped_object(self.a2)

        card_defined = self.aggregate(self.assertClassDefined, a2, 'Card', tag='Card')
        if card_defined:
            self.aggregate(self.assertFunctionDefined, a2.Card, 'play', 3, tag='Card.play')
            self.aggregate(self.assertFunctionDefined, a2.Card, 'action', 4, tag='Card.action')
            self.aggregate(self.assertFunctionDefined, a2.Card, '__str__', 1, tag='Card.__str__')
            self.aggregate(self.assertFunctionDefined, a2.Card, '__repr__', 1, tag='Card.__repr__')

        if self.aggregate(self.assertClassDefined, a2, 'NumberCard', tag='NumberCard'):
            self.aggregate(self.assertFunctionDefined, a2.NumberCard, 'get_number', 1, tag='NumberCard.get_number')
            if card_defined:
                self.aggregate(self.assertIsSubclass, a2.NumberCard, a2.Card, tag='NumberCard')

        if self.aggregate(self.assertClassDefined, a2, 'CoderCard', tag='CoderCard'):
            self.aggregate(self.assertFunctionDefined, a2.CoderCard, 'get_name', 1, tag='CoderCard.get_name')
            if card_defined:
                self.aggregate(self.assertIsSubclass, a2.CoderCard, a2.Card, tag='CoderCard')

        if self.aggregate(self.assertClassDefined, a2, 'TutorCard', tag='TutorCard'):
            self.aggregate(self.assertFunctionDefined, a2.TutorCard, 'get_name', 1, tag='TutorCard.get_name')
            if card_defined:
                self.aggregate(self.assertIsSubclass, a2.TutorCard, a2.Card, tag='TutorCard')

        if self.aggregate(self.assertClassDefined, a2, 'KeyboardKidnapperCard', tag='KeyboardKidnapperCard'):
            if card_defined:
                self.aggregate(self.assertIsSubclass, a2.KeyboardKidnapperCard, a2.Card, tag='KeyboardKidnapperCard')

        if self.aggregate(self.assertClassDefined, a2, 'AllNighterCard', tag='AllNighterCard'):
            if card_defined:
                self.aggregate(self.assertIsSubclass, a2.AllNighterCard, a2.Card, tag='AllNighterCard')

        if self.aggregate(self.assertClassDefined, a2, 'Deck', tag='Deck'):
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'get_cards', 1, tag='Deck.get_cards')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'get_card', 2, tag='Deck.get_card')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'top', 1, tag='Deck.top')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'remove_card', 2, tag='Deck.remove_card')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'get_amount', 1, tag='Deck.get_amount')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'shuffle', 1, tag='Deck.shuffle')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'pick', 2, tag='Deck.pick')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'add_card', 2, tag='Deck.add_card')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'add_cards', 2, tag='Deck.add_cards')
            self.aggregate(self.assertFunctionDefined, a2.Deck, 'copy', 2, tag='Deck.copy')
            self.aggregate(self.assertFunctionDefined, a2.Deck, '__str__', 1, tag='Deck.__str__')
            self.aggregate(self.assertFunctionDefined, a2.Deck, '__repr__', 1, tag='Deck.__repr__')

        if self.aggregate(self.assertClassDefined, a2, 'Player', tag='Player'):
            self.aggregate(self.assertFunctionDefined, a2.Player, 'get_name', 1, tag='Player.get_name')
            self.aggregate(self.assertFunctionDefined, a2.Player, 'get_hand', 1, tag='Player.get_hand')
            self.aggregate(self.assertFunctionDefined, a2.Player, 'get_coders', 1, tag='Player.get_coders')
            self.aggregate(self.assertFunctionDefined, a2.Player, 'has_won', 1, tag='Player.has_won')
            self.aggregate(self.assertFunctionDefined, a2.Player, '__str__', 1, tag='Deck.__str__')
            self.aggregate(self.assertFunctionDefined, a2.Player, '__repr__', 1, tag='Deck.__repr__')

        self.aggregate_tests()

    def test_doc_strings(self):
        """ test all classes and functions have documentation strings """
        a2 = AttributeGuesser.get_wrapped_object(self.a2)
        for func_name, func in inspect.getmembers(a2, predicate=inspect.isfunction):
            if func_name != 'main':
                self.aggregate(self.assertDocString, func)

        for cls_name, cls in inspect.getmembers(a2, predicate=inspect.isclass):
            self.aggregate(self.assertDocString, cls)
            for func_name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
                if func_name.startswith('__') and func_name.endswith('__') and func_name != '__init__':
                    continue
                self.aggregate(self.assertDocString, func)

        self.aggregate_tests()


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Card')
class TestCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card = self.a2.Card()

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'Card.__str__')
    def test_str(self):
        """ test Card.__str__ """
        self.assertEqual(str(self._card), "Card()")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'Card.__repr__')
    def test_repr(self):
        """ test Card.__repr__ """
        self.assertEqual(repr(self._card), "Card()")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard.__init__')
class TestNumberCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card1 = self.a2.NumberCard(3)
        self._card2 = self.a2.NumberCard(1001)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard.get_number')
    def test_get_number(self):
        """ test NumberCard.get_number """
        self.assertEqual(self._card1.get_number(), 3)
        self.assertEqual(self._card2.get_number(), 1001)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'NumberCard.__str__')
    def test_str(self):
        """ test NumberCard.__str__ """
        self.assertEqual(str(self._card1), "NumberCard(3)")
        self.assertEqual(str(self._card2), "NumberCard(1001)")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'NumberCard.__repr__')
    def test_repr(self):
        """ test NumberCard.__repr__ """
        self.assertEqual(repr(self._card1), "NumberCard(3)")
        self.assertEqual(repr(self._card2), "NumberCard(1001)")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard.__init__')
class TestCoderCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card1 = self.a2.CoderCard("brae")
        self._card2 = self.a2.CoderCard("steven")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard.get_name')
    def test_get_number(self):
        """ test CoderCard.get_name """
        self.assertEqual(self._card1.get_name(), "brae")
        self.assertEqual(self._card2.get_name(), "steven")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'CoderCard.__str__')
    def test_str(self):
        """ test CoderCard.__str__ """
        self.assertEqual(str(self._card1), "CoderCard(brae)")
        self.assertEqual(str(self._card2), "CoderCard(steven)")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'CoderCard.__repr__')
    def test_repr(self):
        """ test CoderCard.__repr__ """
        self.assertEqual(repr(self._card1), "CoderCard(brae)")
        self.assertEqual(repr(self._card2), "CoderCard(steven)")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard.__init__')
class TestTutorCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card1 = self.a2.TutorCard("hanwei")
        self._card2 = self.a2.TutorCard("luis")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard.get_name')
    def test_get_number(self):
        """ test TutorCard.get_name """
        self.assertEqual(self._card1.get_name(), "hanwei")
        self.assertEqual(self._card2.get_name(), "luis")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'TutorCard.__str__')
    def test_str(self):
        """ test TutorCard.__str__ """
        self.assertEqual(str(self._card1), "TutorCard(hanwei)")
        self.assertEqual(str(self._card2), "TutorCard(luis)")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'TutorCard.__repr__')
    def test_repr(self):
        """ test TutorCard.__repr__ """
        self.assertEqual(repr(self._card1), "TutorCard(hanwei)")
        self.assertEqual(repr(self._card2), "TutorCard(luis)")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'KeyboardKidnapperCard')
class TestKeyboardKidnapperCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card = self.a2.KeyboardKidnapperCard()

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'KeyboardKidnapperCard.__str__')
    def test_str(self):
        """ test KeyboardKidnapperCard.__str__ """
        self.assertEqual(str(self._card), "KeyboardKidnapperCard()")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'KeyboardKidnapperCard.__repr__')
    def test_repr(self):
        """ test KeyboardKidnapperCard.__repr__ """
        self.assertEqual(repr(self._card), "KeyboardKidnapperCard()")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'AllNighterCard')
class TestAllNighterCard(TestA2):
    def setUp(self):
        super().setUp()
        self._card = self.a2.AllNighterCard()

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'AllNighterCard.__str__')
    def test_str(self):
        """ test AllNighterCard.__str__ """
        self.assertEqual(str(self._card), "AllNighterCard()")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined_correctly.__name__, 'AllNighterCard.__repr__')
    def test_repr(self):
        """ test AllNighterCard.__repr__ """
        self.assertEqual(repr(self._card), "AllNighterCard()")


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.__init__')
class TestDeck(TestA2):
    def setUp(self):
        self._cards = [self.a2.Card() for _ in range(5)]
        # self._cards = [self.a2.NumberCard(i) for i in range(5)]

    def test_deck_init(self):
        """ test Deck.__init__ """
        self.a2.Deck()
        self.a2.Deck([])
        self.a2.Deck(None)
        self.a2.Deck(starting_cards=[])

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.get_cards')
    def test_get_cards(self):
        """ test Deck.get_cards """
        deck = self.a2.Deck([])
        cards = deck.get_cards()
        self.assertIsInstance(cards, list)
        self.assertIs(cards, deck.get_cards())

        deck = self.a2.Deck(self._cards[:])
        self.assertEqual(self._cards, deck.get_cards())

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.get_card')
    def test_get_card(self):
        """ test Deck.get_card """
        card = self.a2.Card()
        deck = self.a2.Deck([card])
        self.assertIs(card, deck.get_card(0))

        deck = self.a2.Deck(self._cards[:])
        self.assertIs(deck.get_card(2), self._cards[2])
        self.assertIs(deck.get_card(3), self._cards[3])

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.top')
    def test_top(self):
        """ test Deck.top """
        deck = self.a2.Deck(self._cards[:])
        self.assertIs(deck.top(), self._cards[4])
        self.assertIs(deck.top(), self._cards[4])

    @skipIfFailed(test_name=test_get_cards.__name__)
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.remove_card')
    def test_remove_card(self):
        """ test Deck.remove_card """
        c_remove_next, c2, c_remove, c4, c5 = self._cards
        deck = self.a2.Deck(self._cards[:])

        # Remove first card
        self.assertIsNone(deck.remove_card(2), msg="Deck.remove_card should not return")

        # Check state of cards
        update = deck.get_cards()
        self.assertNotIn(c_remove, update)
        for card in (c_remove_next, c2, c4, c5):
            self.assertIn(card, update)

        # Remove second card
        deck.remove_card(0)

        # Check state of cards
        update = deck.get_cards()
        self.assertNotIn(c_remove_next, update)
        for card in (c2, c4, c5):
            self.assertIn(card, update)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.get_amount')
    def test_get_amount(self):
        """ test Deck.get_amount """
        deck = self.a2.Deck([])
        self.assertEqual(deck.get_amount(), 0)

        deck = self.a2.Deck(self._cards[:])
        self.assertEqual(deck.get_amount(), 5)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.shuffle')
    def test_shuffle(self):
        """ test Deck.shuffle """
        random.seed(1337)
        deck = self.a2.Deck([])
        self.assertIsNone(deck.shuffle(), msg="Deck.shuffle should not return")

        random.seed(1337)
        order = [1, 0, 3, 2, 4]
        shuffled = [self._cards[i] for i in order]
        deck = self.a2.Deck(self._cards[:])
        self.assertIsNone(deck.shuffle(), msg="Deck.shuffle should not return")
        self.assertEqual(deck.get_cards(), shuffled, msg="Don't try do your own shuffling")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.pick')
    @skipIfFailed(test_name=test_get_cards.__name__)
    def test_pick(self):
        """ test Deck.pick """
        deck = self.a2.Deck(self._cards[:])
        self.assertEqual(deck.pick(1), [self._cards[4]])
        self.assertEqual(deck.pick(2), [self._cards[3], self._cards[2]])
        self.assertEqual(deck.pick(), [self._cards[1]])

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.add_card')
    @skipIfFailed(test_name=test_get_cards.__name__)
    def test_add_card(self):
        """ test Deck.add_card """
        deck = self.a2.Deck([])
        card = self.a2.Card()
        self.assertIsNone(deck.add_card(card), msg="Deck.add_card should not return")
        self.assertEqual(deck.get_cards(), [card])

        deck = self.a2.Deck(self._cards[:])
        deck.add_card(card)
        self.assertEqual(deck.get_cards(), self._cards + [card])

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.add_cards')
    @skipIfFailed(test_name=test_get_cards.__name__)
    def test_add_cards(self):
        """ test Deck.add_cards """
        deck = self.a2.Deck([])
        cards = [self.a2.Card() for _ in range(5)]
        self.assertIsNone(deck.add_cards(self._cards[:]), msg="Deck.add_card should not return")
        self.assertEqual(deck.get_cards(), self._cards)

        deck = self.a2.Deck(self._cards[:])
        deck.add_cards(cards[:])
        self.assertEqual(deck.get_cards(), self._cards + cards)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck.copy')
    @skipIfFailed(test_name=test_get_cards.__name__)
    def test_copy(self):
        """ test Deck.copy """
        deck_1 = self.a2.Deck([])
        deck_2 = self.a2.Deck([])
        self.assertIsNone(deck_1.copy(deck_2), msg="Deck.copy should not return")
        self.assertEqual(deck_1.get_cards(), [])
        self.assertEqual(deck_2.get_cards(), [])

        deck_1 = self.a2.Deck(self._cards[:])
        deck_2 = self.a2.Deck([])
        deck_1.copy(deck_2)
        self.assertEqual(deck_1.get_cards(), self._cards)
        self.assertEqual(deck_2.get_cards(), [])

        deck_1 = self.a2.Deck([])
        deck_2 = self.a2.Deck(self._cards[:])
        deck_1.copy(deck_2)
        self.assertEqual(deck_1.get_cards(), self._cards)
        self.assertEqual(deck_2.get_cards(), self._cards)

        deck_1 = self.a2.Deck(self._cards[:])
        deck_2 = self.a2.Deck(self._cards[:])
        deck_1.copy(deck_2)
        self.assertEqual(deck_1.get_cards(), self._cards * 2)
        self.assertEqual(deck_2.get_cards(), self._cards)

    def test_str(self):
        """ test Deck.__str__ """
        deck = self.a2.Deck([])
        self.assertEqual(str(deck), "Deck()")

        deck = self.a2.Deck([self.a2.Card()])
        self.assertEqual(repr(deck), "Deck(Card())")

        deck = self.a2.Deck(self._cards)
        self.assertEqual(str(deck), "Deck(Card(), Card(), Card(), Card(), Card())")

    def test_repr(self):
        """ test Deck.__repr__ """
        deck = self.a2.Deck([])
        self.assertEqual(repr(deck), "Deck()")

        deck = self.a2.Deck([self.a2.Card()])
        self.assertEqual(repr(deck), "Deck(Card())")

        deck = self.a2.Deck(self._cards)
        self.assertEqual(repr(deck), "Deck(Card(), Card(), Card(), Card(), Card())")

    def test_str_with_other_cards(self):
        """ test Deck with other cards """
        deck = self.a2.Deck([
            self.a2.Card(),
            self.a2.NumberCard(1),
            self.a2.CoderCard("steven"),
            self.a2.TutorCard("steven"),
            self.a2.KeyboardKidnapperCard(),
            self.a2.AllNighterCard()
        ])

        self.assertEqual(str(deck), 'Deck(Card(), NumberCard(1), CoderCard(steven), '
                                    'TutorCard(steven), KeyboardKidnapperCard(), AllNighterCard())')


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player.__init__')
class TestPlayer(TestA2):
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player.get_name')
    def test_get_name(self):
        """ test Player.get_name """
        p1 = self.a2.Player("steven")
        p2 = self.a2.Player("sTeVeN")

        self.assertEqual(p1.get_name(), "steven")
        self.assertEqual(p2.get_name(), "sTeVeN")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player.get_hand')
    def test_get_hand(self):
        """ test Player.get_hand """
        p = self.a2.Player("steven")
        hand = p.get_hand()
        self.assertIsInstance(hand, self.a2.Deck)

        hand2 = p.get_hand()
        self.assertIs(hand, hand2)

        p2 = self.a2.Player("brae")
        self.assertIsNot(p2.get_hand(), hand, msg="Player's shouldn't have the same hand")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player.get_coders')
    def test_get_coders(self):
        """ test Player.get_coders """
        p = self.a2.Player("steven")
        coders = p.get_coders()
        self.assertIsInstance(coders, self.a2.Deck)

        coders2 = p.get_coders()
        self.assertIs(coders, coders2)

        p2 = self.a2.Player("brae")
        self.assertIsNot(p2.get_coders(), coders, msg="Player's shouldn't have the same hand")

    @skipIfFailed(test_name=test_get_coders.__name__)
    def test_has_won(self):
        """ test Player.has_won """
        p = self.a2.Player("steven")
        self.assertIs(p.has_won(), False)

        for _ in range(4):
            p.get_coders().add_card(self.a2.Card())
        self.assertIs(p.has_won(), True)

        p.get_coders().add_card(self.a2.Card())
        self.assertIs(p.has_won(), True)

    def test_str(self):
        """ test Player.__str__ """
        p = self.a2.Player("steven")
        self.assertEqual(str(p), 'Player(steven, Deck(), Deck())')

    def test_repr(self):
        """ test Player.__repr__ """
        p = self.a2.Player("steven")
        self.assertEqual(repr(p), 'Player(steven, Deck(), Deck())')

    @skipIfFailed(test_name=test_str.__name__)
    @skipIfFailed(test_name=test_get_hand.__name__)
    @skipIfFailed(test_name=test_get_coders.__name__)
    def test_str_cards(self):
        """ test Player with cards in deck """
        p = self.a2.Player("Steven")
        p.get_hand().add_cards([self.a2.Card(), self.a2.Card()])
        self.assertEqual(str(p), 'Player(Steven, Deck(Card(), Card()), Deck())')

        p.get_coders().add_cards([self.a2.Card(), self.a2.Card()])
        self.assertEqual(str(p), 'Player(Steven, Deck(Card(), Card()), Deck(Card(), Card()))')

    @skipIfFailed(test_name=test_repr.__name__)
    @skipIfFailed(test_name=test_get_hand.__name__)
    @skipIfFailed(test_name=test_get_coders.__name__)
    def test_repr_cards(self):
        """ test Player.__repr__ with cards in deck """
        p = self.a2.Player("Steven")
        p.get_hand().add_cards([self.a2.Card(), self.a2.Card()])
        self.assertEqual(repr(p), 'Player(Steven, Deck(Card(), Card()), Deck())')

        p.get_coders().add_cards([self.a2.Card(), self.a2.Card()])
        self.assertEqual(repr(p), 'Player(Steven, Deck(Card(), Card()), Deck(Card(), Card()))')


@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Player')
@skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Deck')
class TestPlayAndAction(TestA2):
    def setUp(self):
        if self.a2_support is None:
            self.skipTest("Failed to import 'a2_support.py'")

    def init_game(self, card_type, *card_args, size=6, num_players=3, cycle=True):
        players = [self.a2.Player(f'Player {i}') for i in range(1, num_players + 1)]
        num_cards = size * (num_players + 1)
        if cycle:
            args = itertools.cycle(card_args)
            cards = [card_type(next(args)) for _ in range(num_cards)]
        else:
            cards = [card_type(*card_args) for _ in range(num_cards)]

        pickup_pile = self.a2.Deck(cards)

        for player in players:
            player.get_hand().add_cards(pickup_pile.pick(5))

        coders = self.a2_support.CODERS[:]
        self._game = self.a2_support.CodersGame(pickup_pile, coders, players)

    def get_game_state(self) -> CodersGameState:
        current_player = self._game.current_player()
        next_player = self._game.get_turns().peak(1)
        prev_player = self._game.get_turns().peak(-1)

        return CodersGameState(
            pickup_pile=self._game.get_pickup_pile().get_cards()[:],
            putdown_pile=self._game.putdown_pile.get_cards()[:],
            coders=self._game.get_sleeping_coders()[:],
            current_player=current_player,
            current_player_hand=current_player.get_hand().get_cards()[:],
            current_player_coders=current_player.get_coders().get_cards()[:],
            next_player=next_player,
            next_player_hand=next_player.get_hand().get_cards()[:],
            next_player_coders=next_player.get_coders().get_cards()[:],
            prev_player=self._game.get_turns().peak(-1),
            prev_player_hand=prev_player.get_hand().get_cards()[:],
            prev_player_coders=prev_player.get_coders().get_cards()[:],
            action=self._game.get_action()
        )

    def assertGameState(self, initial_state: CodersGameState, new_state: CodersGameState, *ignore):
        new_state_dict = new_state._asdict()
        initial_state = initial_state._asdict()
        for field in set(CodersGameState._fields) - set(ignore):
            self.assertEqual(new_state_dict[field], initial_state[field],
                             msg=f"Unexpected value changed for field '{field}'")

    def _test_play_card_common(self) -> CodersGameState:
        state = self.get_game_state()
        card = state.current_player_hand[0]
        self.assertIsNone(card.play(state.current_player, self._game))
        new_state = self.get_game_state()

        # Removed card
        self.assertNotIn(card, new_state.prev_player.get_hand().get_cards())

        # Ensure new card has been added
        self.assertEqual(new_state.current_player.get_hand().get_amount(), 5)
        # Top Card from pickup pile is in hand
        self.assertIs(new_state.current_player.get_hand().top(), state.pickup_pile[-1])
        # Top Card from pickup pile has been removed
        self.assertNotIn(new_state.current_player.get_hand().top(), new_state.pickup_pile)
        # Check only one top card has been removed from pickup pile
        self.assertEqual(new_state.pickup_pile, state.pickup_pile[:-1])

        self.assertEqual(state.putdown_pile, new_state.putdown_pile,
                         msg="Should not be changing putdown pile yourself")

        # Check untouched
        self.assertEqual(state.coders, new_state.coders)
        return new_state

    def _test_action_card_common(self, card, slot):
        self.init_game(self.a2.Card, cycle=False)

        # Remove Coder from game at `slot` and add it to next player's hand
        coder = self._game.get_sleeping_coders()[slot]
        self._game.get_sleeping_coders()[slot] = None
        self._game.get_turns().peak(1).get_coders().add_card(coder)

        state = self.get_game_state()
        self.assertIsNone(card.action(state.next_player, self._game, 0))
        new_state = self.get_game_state()

        # Check next player's turn
        self.assertIs(state.next_player, new_state.current_player)
        # Check Coder has been removed from player
        self.assertNotIn(coder, new_state.current_player_coders)

        self.assertEqual(new_state.action, "NO_ACTION")

        # Check untouched
        self.assertEqual(state.current_player_hand, new_state.prev_player_hand)
        self.assertEqual(state.next_player_hand, new_state.current_player_hand)

        self.assertEqual(state.putdown_pile, new_state.putdown_pile)
        self.assertEqual(state.pickup_pile, new_state.pickup_pile)

        return coder, state, new_state

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Card.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Card')
    def test_card_play(self):
        """ test Card.play """
        self.init_game(self.a2.Card, cycle=False)
        new_state = self._test_play_card_common()
        self.assertEqual(new_state.action, "NO_ACTION")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Card.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'Card')
    def test_card_action(self):
        """ test Card.action """
        self.init_game(self.a2.Card, cycle=False)

        state = self.get_game_state()
        card = self.a2.Card()
        self.assertIsNone(card.action(state.next_player, self._game, 0))
        new_state = self.get_game_state()

        self.assertEqual(state, new_state)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard')
    def test_number_play(self):
        """ test NumberCard.play """
        self.init_game(self.a2.NumberCard, *range(10))

        state = self.get_game_state()
        card = state.current_player_hand[0]
        self.assertIsNone(card.play(state.current_player, self._game))
        new_state = self.get_game_state()

        # Changed to next player
        self.assertIs(state.next_player, new_state.current_player)

        # Removed card
        self.assertNotIn(card, new_state.prev_player.get_hand().get_cards())

        # Ensure new card has been added
        self.assertEqual(new_state.prev_player.get_hand().get_amount(), 5)

        # Top Card from pickup pile is in hand
        self.assertIs(new_state.prev_player.get_hand().top(), state.pickup_pile[-1])
        # Top Card from pickup pile has been removed
        self.assertNotIn(new_state.prev_player.get_hand().top(), new_state.pickup_pile)

        self.assertEqual(state.putdown_pile, new_state.putdown_pile,
                         msg="Should not be changing putdown pile yourself")

        # Action was changed
        self.assertEqual(new_state.action, "NO_ACTION")

        # Check untouched
        self.assertEqual(state.coders, new_state.coders)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'NumberCard')
    def test_number_action(self):
        """ test NumberCard.action """
        self.init_game(self.a2.Card, cycle=False)

        state = self.get_game_state()
        card = self.a2.NumberCard(0)
        self.assertIsNone(card.action(state.next_player, self._game, 0))
        new_state = self.get_game_state()

        self.assertEqual(state, new_state)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard')
    def test_coder_play(self):
        """ test CoderCard.play """
        self.init_game(self.a2.CoderCard, *(f'Coder {i}' for i in range(10)))

        state = self.get_game_state()
        card = state.current_player_hand[0]
        self.assertIsNone(card.play(state.current_player, self._game))
        new_state = self.get_game_state()

        self.assertEqual(new_state.action, "NO_ACTION")
        # Everything except action should be the same
        self.assertGameState(state, new_state, "action")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'CoderCard')
    def test_coder_action(self):
        """ test CoderCard.action """
        self.init_game(self.a2.Card, cycle=False)

        state = self.get_game_state()
        card = self.a2.CoderCard("Coder")
        self.assertIsNone(card.action(state.next_player, self._game, 0))
        new_state = self.get_game_state()

        self.assertEqual(state, new_state)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard')
    def test_tutor_play(self):
        """ test TutorCard.play """
        self.init_game(self.a2.TutorCard, *(f'Tutor {i}' for i in range(10)))
        new_state = self._test_play_card_common()
        self.assertEqual(new_state.action, "PICKUP_CODER")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'TutorCard')
    def test_tutor_action(self):
        """ test TutorCard.action """
        self.init_game(self.a2.Card, cycle=False)

        slot = 11
        coder = self._game.get_sleeping_coders()[slot]

        card = self.a2.TutorCard("Tutor")
        state = self.get_game_state()
        self.assertIsNone(card.action(state.current_player, self._game, slot))
        new_state = self.get_game_state()

        # Check next player's turn
        self.assertIs(state.next_player, new_state.current_player)
        # Check Coder has been removed
        self.assertIsNone(new_state.coders[slot])
        # Check Coder added to Player
        self.assertIn(coder, new_state.prev_player_coders)
        # Check action set
        self.assertEqual(new_state.action, "NO_ACTION")

        # Check untouched
        self.assertEqual(state.current_player_hand, new_state.prev_player_hand)
        self.assertEqual(state.next_player_hand, new_state.current_player_hand)
        self.assertEqual(state.next_player_coders, new_state.current_player_coders)

        self.assertEqual(state.putdown_pile, new_state.putdown_pile)
        self.assertEqual(state.pickup_pile, new_state.pickup_pile)

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'KeyboardKidnapperCard.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'KeyboardKidnapperCard')
    def test_keyboard_play(self):
        """ test KeyboardKidnapperCard.play """
        self.init_game(self.a2.KeyboardKidnapperCard, cycle=False)
        new_state = self._test_play_card_common()
        self.assertEqual(new_state.action, "STEAL_CODER")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'KeyboardKidnapperCard.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'KeyboardKidnapperCard')
    def test_keyboard_action(self):
        """ test KeyboardKidnapperCard.action """
        card = self.a2.KeyboardKidnapperCard()

        slot = 11
        coder, state, new_state = self._test_action_card_common(card, slot)

        # Check Coder added to current player's (at the time) coders
        self.assertIn(coder, new_state.prev_player_coders)

        # Ensure slot is still empty
        self.assertIsNone(new_state.coders[slot])

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'AllNighterCard.play')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'AllNighterCard')
    def test_all_nighter_play(self):
        """ test AllNighterCard.play """
        self.init_game(self.a2.AllNighterCard, cycle=False)
        new_state = self._test_play_card_common()
        self.assertEqual(new_state.action, "SLEEP_CODER")

    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'AllNighterCard.action')
    @skipIfFailed(TestDesign, TestDesign.test_classes_defined.__name__, 'AllNighterCard')
    def test_all_nighter_action(self):
        """ test AllNighterCard.action """
        card = self.a2.AllNighterCard()

        slot = 11
        coder, state, new_state = self._test_action_card_common(card, slot)

        # Check Coder added to game
        self.assertIs(new_state.coders[slot], coder)

        # Check all other coders are untouched
        self.assertEqual(new_state.coders[:slot] + new_state.coders[slot+1:],
                         state.coders[:slot] + state.coders[slot+1:])

        # Check untouched
        self.assertEqual(state.current_player_coders, new_state.prev_player_coders)


def main():
    test_cases = [
        TestDesign,
        TestCard,
        TestNumberCard,
        TestCoderCard,
        TestTutorCard,
        TestKeyboardKidnapperCard,
        TestAllNighterCard,
        TestDeck,
        TestPlayer,
        TestPlayAndAction
    ]

    master = TestMaster(max_diff=None,
                        # suppress_stdout=False,
                        ignore_import_fails=True,
                        timeout=1,
                        include_no_print=True,
                        scripts=[
                            ('a2', 'a2.py'),
                            ('a2_support', 'a2_support.py')
                        ])
    master.run(test_cases)


if __name__ == '__main__':
    main()
