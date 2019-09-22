"""
CSSE1001 Semester 2, 2019
Sleeping Coders Support Code
Version 1.0.1
"""
import random

from a2 import NumberCard, TutorCard, CoderCard, AllNighterCard, KeyboardKidnapperCard
from a2 import Deck

__author__ = "Brae Webb"
__version__ = "1.0.0"

TUTOR_NAMES = ["benjamin", "brad", "brae", "connor", "damien", "hanwei", "justin", "steven"]

FULL_DECK = [
    (TutorCard(None), TUTOR_NAMES),
    (AllNighterCard(), range(0, 4)),
    (KeyboardKidnapperCard(), range(0, 4)),

    (NumberCard(0), range(0, 10)),
    (NumberCard(0), range(0, 10)),
]

CODERS = [
    CoderCard("anna"),

    CoderCard("wilson"),
    CoderCard("ashleigh"),
    CoderCard("harry"),
    CoderCard("hob"),

    CoderCard("henry"),
    CoderCard("mike"),
    CoderCard("anabelle"),
    CoderCard("kt"),
    CoderCard("lochie"),
    CoderCard("luis"),

    CoderCard("jason"),
    CoderCard("raunaq"),
    CoderCard("sanni"),
    CoderCard("tze"),
    CoderCard("kaleb"),
]


class TurnManager:
    """
    A class to manage the order of turns amongst game players.
    """
    def __init__(self, players):
        """
        Construct a new turn manager to based on game players.

        Parameters:
             players (list<T>): An ordered list of players to store.
        """
        self._players = players
        # start in correct direction
        self._direction = True
        self._location = 0
        self._max = len(players)

    def current(self):
        """
        (T) Returns the player whose turn it is.
        """
        return self._players[self._location]

    def next(self):
        """
        (T) Moves onto the next players turn and return that player.
        """
        return self.skip(count=0)

    def peak(self, count=1):
        """
        Look forward or backwards in the current ordering of turns.

        Parameters:
            count (int): The amount of turns to look forward,
                         if negative, looks backwards.

        Returns:
            (T): The player we are peaking at.
        """
        location = self._location
        location += count if self._direction else -count
        location %= self._max
        return self._players[location]

    def reverse(self):
        """
        Reverse the order of turns.
        """
        self._direction = not self._direction

    def skip(self, count=0):
        """
        (T): Moves onto the next player, skipping 'count' amount players.
        """
        count += 1
        self._location += count if self._direction else -count
        self._location %= self._max
        return self._players[self._location]


class CodersGame:
    """
    A game of Sleeping Coders.
    """
    def __init__(self, deck, coders, players):
        """
        Construct a game of Sleeping Coders from a pickup pile, a list of coder
        cards and a list of players.

        Parameters:
            deck (Deck): The pile of cards to pickup from.
            coders (List<Card>): The list of sleeping coder cards.
            players (list<Player>): The players in this game.
        """
        self._pickup_pile = deck
        self._coders = coders
        self.players = players

        self._turns = TurnManager(players)

        self.putdown_pile = Deck()

        self._is_over = False
        self.winner = None

        self._action = None

    def get_pickup_pile(self):
        """(Deck): Returns the pickup file of a game."""
        return self._pickup_pile

    def get_sleeping_coders(self):
        """(List[Card]): Returns the list of coders who are still asleep in the game."""
        return self._coders

    def get_sleeping_coder(self, slot):
        """(Card): Returns the sleeping coder card at the given slot.

        Parameters:
            slot (int): The slot within the sleeping coders collection to get.
        """
        return self._coders[slot]

    def set_sleeping_coder(self, slot, card):
        """Set the coder at the given slot in the sleeping coders collection

        Parameters:
            slot (int): The slot within the sleeping coders collection to set.
            card (Card): The card to place in the given slot.
        """
        self._coders[slot] = card

    def pick_card(self, blocked_classes=()):
        """
        Pick a the first card from the pickup pile that is not an instance of
        any of the classes in the blocked_classes.

        Parameters:
            blocked_classes (tuple<Card>): The classes that the card cannot be
                                           an instance of.

        Returns:
            (List[Card]): The card picked from the top of the pickup pile.
        """
        while True:
            picked_card = self._pickup_pile.pick()

            if not any((isinstance(picked_card, card_class)
                        for card_class in blocked_classes)):
                return picked_card

    def next_player(self):
        """
        Changes to the next player in the game and returns an instance of them.

        Returns:
            (Player): The next player in the game.
        """
        return self._turns.next()

    def current_player(self):
        """
        (Player) Returns the player whose turn it is currently.
        """
        return self._turns.current()

    def skip(self):
        """Prevent the next player from taking their turn."""
        self._turns.skip()

    def reverse(self):
        """Transfer the turn back to the previous player and reverse the order."""
        self._turns.reverse()

    def get_turns(self):
        """(TurnManager) Returns the turn manager for this game."""
        return self._turns

    def is_over(self):
        """
        (bool): True iff the game has been won. Assigns the winner variable.
        """
        if self._pickup_pile.get_amount() == 0:
            return True

        for player in self.players:
            if player.has_won():
                self.winner = player
                self._is_over = True

        return self._is_over

    def select_card(self, player, card):
        """Perform actions for a player selecting a card

        Parameters:
            player (Player): The selecting player.
            card (Card): The card to select.
        """
        card.play(player, self)
        self.putdown_pile.add_card(card)

    def get_action(self):
        """
        Get the current action being performed.
        """
        return self._action

    def set_action(self, action):
        """
        Set the current action being performed to action.

        Possible Actions:
            NO_ACTION: No action is being performed.
            PICKUP_CODER: Tutor card played to pickup a coder.
            STEAL_CODER: Keyboard Kidnapper played to steal another players coder.
            SLEEP_CODER: All-nighter played to put another players coder to sleep.

        Parameters:
            action (str): The current action.
        """
        self._action = action

    def get_last_card(self):
        """
        (Card): Get the last card that was played.
        """
        return self.putdown_pile.top()


def build_deck(structure, range_cards=(NumberCard, TutorCard)):
    """
    Construct a list of cards from a simplified deck structure.

    Example structure:
    [ (PotionCard(), range(0, 6)),
      (NumberCard(0), range(1, 11)) ]

    Creates a deck with 6 potion cards and 10 number cards ranging from 1 to 10.
    This assumes that NumberCard is apart of the range_card tuple or NumberCard
    will be constructed without a number value.

    Parameters:
        structure (list<tuple>): The simplified deck structure.
        range_cards (tuple<Card>): Cards who should have the range value passed
                                   to the constructor when created.

    Returns:
        (List[Card]): The deck of cards as a list of cards.
    """
    deck = []

    for (card, values) in structure:
        for value in values:
            if card.__class__ not in range_cards:
                new_card = card.__class__()
            else:
                new_card = card.__class__(value)
            deck.append(new_card)

    return deck


def generate_name():
    """
    (str): Selects a random name from a list of player names.
    """
    with open("players.txt", "r") as file:
        names = file.readlines()
    return random.choice(names).strip()


def main():
    print("Please run gui.py instead")


if __name__ == "__main__":
    main()
