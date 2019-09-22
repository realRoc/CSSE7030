#!/usr/bin/env python3
"""
Assignment 2 - Sleeping Coders
CSSE1001/7030
Semester 2, 2019
"""

import random

__author__ = "Yupeng Wu ID: 45960600"

# Write your classes here


class Card(object):
    """The basic method for all kinds of cards."""
    def play(self, player, game):
        """
        Called when a player plays a card.
            1. Remove the card from player's hand.
            2. Pickup a new card from the pickup pile.
            3. Set action as NO_ACTION.
        """
        # remove card
        player.get_hand().get_cards().remove(self)
        # player pickup a new card from the pile
        pick_card = game.pick_card()[0]
        player.get_hand().add_card(pick_card)
        # set action
        game.set_action("NO_ACTION")

    def action(self, player, game, slot):
        """
        Will pass if there is no action.
        Will be override if there is an action.
        """
        pass

    def __str__(self):
        return "Card()"

    def __repr__(self):
        return str(self)


class NumberCard(Card):
    """A number card which has an associated number value."""
    def __init__(self, number: int):
        """
        Get to number value for the number card.

        Parameters:
             number (int): The number value.
        """
        self._number = number

    def get_number(self):
        """(Number): Returns the number value of the number card."""
        return self._number

    def play(self, player, game):
        """
        Do the same thing as Card.play.
        Turns to the next player.

        Parameters:
            player: The player who played the card.
            game: The game which is processing.
        """
        super().play(player, game)
        game.skip()

    def __str__(self):
        return "NumberCard({})".format(self._number)

    def __repr__(self):
        return str(self)


class CoderCard(Card):
    """A card which stores the name of a coder card."""
    def __init__(self, coder):
        """
        Get the name of the coder card.

        Parameters:
           coder (str): The coder card's name."""
        self._coder = coder

    def get_name(self):
        """(Card): Returns the CoderCard's name."""
        return self._coder

    def play(self, player, game):
        """
        Don't do anything in Card.play.
        Just set the action as "NO_ACTION"
        """
        game.set_action("NO_ACTION")

    def __str__(self):
        return "CoderCard({})".format(self._coder)

    def __repr__(self):
        return str(self)


class TutorCard(Card):
    """A card which stores the name of a tutor card."""
    def __init__(self, tutor: str):
        """
        Get the name of the tutor card.

        Parameters:
             tutor (str): The name of the tutor card.
        """
        self._tutor = tutor

    def get_name(self):
        """(Card): Returns the TutorCard's name."""
        return self._tutor

    def play(self, player, game):
        """
        Do the same thing as Card.play but set a different action

        Parameters:
            player: The player who played the card.
            game: The game which is processing.
        """
        super().play(player, game)
        game.set_action("PICKUP_CODER")

    def action(self, player, game, slot):
        """
        1. Add the selected card to the player's deck.
        2. Replace the selected card to None in the pile.
        3. Set "NO_ACTION" and move on.

        Parameters:
            player: The player who played the card.
            game: The game which is processing.
            slot: (int) The slot of a sleeping coder in the sleeping coder pile.
        """
        # add card to player's deck
        player.get_coders().add_card(game.get_sleeping_coder(slot))
        # replace the sleeping coder's deck to None
        game.set_sleeping_coder(slot, None)
        game.set_action("NO_ACTION")
        game.skip()

    def __str__(self):
        return "TutorCard({})".format(self._tutor)

    def __repr__(self):
        return str(self)


class KeyboardKidnapperCard(Card):
    """A card allows the player to steal a coder card from another players."""
    def play(self, player, game):
        """
        Do the same thing as Card.play but set a different action

        Parameters:
            player: The target player.
            game: The game which is processing.
        """
        super().play(player, game)
        game.set_action("STEAL_CODER")

    def action(self, player, game, slot):
        """
        1. Add the selected card to the current player's deck.
        2. Remove it from its origin deck.
        3. Set "NO_ACTION" and move on.

        Parameters:
            player: The target player.
            game: The game which is processing.
            slot: (int) The slot of the coder card in target player.
        """
        # add card to current player's deck
        stolen_card = player.get_coders().get_card(slot)
        game.current_player().get_coders().add_card(stolen_card)
        # remove
        player.get_coders().remove_card(slot)
        game.set_action("NO_ACTION")
        game.skip()

    def __str__(self):
        return "KeyboardKidnapperCard()"

    def __repr__(self):
        return str(self)


class AllNighterCard(Card):
    """A card allows player to put a coder card from other's back to sleep"""
    def play(self, player, game):
        """
        Do the same thing as Card.play but set a different action

        Parameters:
            player: The target player.
            game: The game which is processing.
        """
        super().play(player, game)
        game.set_action("SLEEP_CODER")

    def action(self, player, game, slot):
        """
        1. Add the selected card to the first empty slot in the coder's pile.
        2. Remove the card from its origin deck.
        3. Set "NO_ACTION" and move on.

        Parameters:
            player: The target player.
            game: The game which is processing.
            slot: (int) The slot of the coder card in target player.
        """
        # get the first empty slot in coders' pile
        position = -1
        for coder in game.get_sleeping_coders():
            position += 1
            if coder is None:
                break
        # add
        sleep_coder = player.get_coders().get_card(slot)
        game.set_sleeping_coder(position, sleep_coder)
        # remove
        player.get_coders().remove_card(slot)
        game.set_action("NO_ACTION")
        game.skip()

    def __str__(self):
        return "AllNighterCard()"

    def __repr__(self):
        return str(self)


class Deck(object):
    """A collection of ordered cards."""
    def __init__(self, starting_cards=None):
        """
        Get the cards.

        Parameters:
            starting_cards: (Cards) If it's None, create with an empty list.
                            If it's provided, created with that list of cards.
        """
        if starting_cards is None:
            starting_cards = []
        self._cards = starting_cards

    def get_cards(self):
        """
        Return: (List[Card]) The list of cards in the deck.
        """
        return self._cards

    def get_card(self, slot):
        """
        Parameters:
            slot: (int) The specified slot of a card.

        Return: (Card) The card at the slot in the deck.
        """
        return self._cards[slot]

    def top(self):
        """
        Return: (Card) The card on the top of the deck.
                If the deck is empty, return None.
        """
        # judge whether the deck is empty
        if not self._cards:
            return None
        else:
            return self._cards[-1]

    def remove_card(self, slot):
        """
        Remove the card at the given slot.

        Parameters:
             slot: (int) The slot of the card which want to be removed.
        """
        self._cards.pop(slot)

    def get_amount(self):
        """
        Return: (int) The amount of cards in a deck.
        """
        return len(self._cards)

    def shuffle(self):
        """Shuffle the order of the cards in the deck."""
        random.shuffle(self._cards)

    def pick(self, amount: int = 1):
        """
        Take the first amount of cards off the deck.

        Parameters:
             amount: (int) The amount of wanted cards. Initially will be 1.

        Return: (List[Card]) A list of cards off the deck.
        """
        pick_result = []
        for slot in range(0, amount):
            pick_result.append(self._cards.pop(-1))
        return pick_result

    def add_card(self, card: Card):
        """
        Place a card on the top of the deck.

        Parameters:
             card: (Card) The card to be placed.
        """
        self._cards.append(card)

    def add_cards(self, cards):
        """
        Place a list of cards on the top of the deck.

        Parameters:
             cards: (List[Card]) The list of card to be placed.
        """
        # append the card in the card list with a for loop
        for card in cards:
            self._cards.append(card)

    def copy(self, other_deck):
        """
        Copy all of the cards from another deck into current deck.

        Parameters:
             other_deck: (Deck) The target deck to be copied.
        """
        # extend the cards in the Deck with a for loop
        self._cards.extend(other_deck.get_cards())

    def __str__(self):
        return "Deck({})".format(str(self._cards)[1:-1])

    def __repr__(self):
        return str(self)


class Player(object):
    """Represents one of the players in the game."""
    def __init__(self, name):
        """
        Get the player's name. A player has two decks, hand deck and coder deck.

        Parameters:
             name: (str) The name of the player.
        """
        self._name = name
        self._hand_cards = Deck()
        self._coder_cards = Deck()

    def get_name(self):
        """Return: (str) The name of the player."""
        return self._name

    def get_hand(self):
        """Return: (Deck) The player's hand deck."""
        return self._hand_cards

    def get_coders(self):
        """Return: (Deck) The player's coder deck."""
        return self._coder_cards

    def has_won(self):
        """Return True if and only if the player has 4 or more coders."""
        # judge whether the player has 4 or more coders
        if len(self.get_coders().get_cards()) > 3:
            return True
        else:
            return False

    def __str__(self):
        return "Player({0}, {1}, {2})".format(self._name,
                                              self.get_hand(),
                                              self.get_coders())

    def __repr__(self):
        return str(self)


def main():
    print("Please run gui.py instead")


if __name__ == "__main__":
    main()
