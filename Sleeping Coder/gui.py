"""
CSSE1001 Semester 2, 2019
Sleeping Coders GUI Support Code
Version 1.0.1
"""

import tkinter as tk
from tkinter import messagebox

from enum import Enum
from a2 import Player, Deck
from a2 import Card, NumberCard, TutorCard, CoderCard, AllNighterCard, KeyboardKidnapperCard
from a2_support import FULL_DECK, CODERS, build_deck, CodersGame, generate_name

__author__ = "Brae Webb"
__version__ = "1.0.0"


CARD_HEIGHT = 100
CARD_WIDTH = 76
CARD_SPACE = 15


class Actions(Enum):
    NO_ACTION = "NO_ACTION"
    PICKUP_CODER = "PICKUP_CODER"
    STEAL_CODER = "STEAL_CODER"
    SLEEP_CODER = "SLEEP_CODER"


class CardView:
    """
    A class to manage the drawing of a card on a canvas.
    """

    def __init__(self, canvas, left_side, top_side=0):
        """
        Construct a new card to be drawn on the given canvas at the left_position.

        Parameters:
            canvas (tk.Canvas): The canvas to draw the card onto.
            left_side (int): The amount of pixels in the canvas to draw the card.
            top_side (int): The amount of pixels in the canvas to draw the card
                            from the top.
        """
        self._canvas = canvas

        self.left_side = left_side
        self.top_side = top_side
        self.right_side = left_side + CARD_WIDTH

        self._images = []

        self._back_image = None

        self.draw()

    def draw(self):
        """Draw the backface of the card to the canvas."""
        self._back_image = self.draw_image("images/tutor")

    def redraw(self, card):
        """Redraw the card view with the properties of the given card.

        Parameters:
            card (Card): The card to draw to the canvas. If None, draw the
                         backface of the card.
        """
        if card is not None:
            # draw the card with details from the card parameter
            self._canvas.itemconfig(self._back_image, state="hidden")
        else:
            # draw the backface of the card
            self._canvas.itemconfig(self._back_image, state="normal")

    def draw_image(self, image):
        """Draw an image in the middle of the card.

        Parameters:
            image (str): The filepath of the image to display.
        """
        try:
            self._images.append(tk.PhotoImage(file=image + ".png"))
        except tk.TclError:
            self._images.append(tk.PhotoImage(file=image + ".gif"))
        return self._canvas.create_image(self.left_side + (CARD_WIDTH // 2),
                                         self.top_side + (CARD_HEIGHT // 2),
                                         image=self._images[-1])


class IconCardView(CardView):
    """
    A card that has an image associated with it.
    """

    def draw(self):
        """Draw the backface of the card to the canvas."""
        super().draw()
        self._file_name = None
        self._image_view = None

    def get_file_name(self, card):
        return ""

    def redraw(self, card):
        """Redraw the card view with an icon.

        Parameters:
            card (Card): The card to draw to the canvas. If None, draw the
                         backface of the card.
        """
        super().redraw(card)

        if card is not None:
            # show the image
            self._canvas.itemconfig(self._image_view, state="normal")
        else:
            # hide the image
            self._canvas.itemconfig(self._image_view, state="hidden")
            return

        image = self.get_file_name(card)
        if self._image_view is None or self._file_name != image:
            self._file_name = image
            self._canvas.itemconfig(self._image_view, state="hidden")
            self._image_view = self.draw_image(image)


class TutorCardView(IconCardView):
    """Card view for rendering the coder or tutor cards by looking for coder
    names in the images/cards folder.
    """
    def get_file_name(self, card):
        return f"images/cards/{card.get_name()}"


class CoderCardView(TutorCardView):
    """Card view for rendering the coder card by displaying the custom back
    for coder cards.
    """
    def draw(self):
        super().draw()
        self._back_image = self.draw_image("images/coder")


class NumberCardView(IconCardView):
    """Card view for rendering the number cards by looking for the number in the
    images/numbers folder.
    """
    def get_file_name(self, card):
        return f"images/numbers/{card.get_number()}"


# Dictionary used by the ActionCardView to lookup the appropriate filename for
# the different special card types.
ACTION_ICONS = {
    AllNighterCard: "all_nighter",
    KeyboardKidnapperCard: "keyboard_kidnapper",
}


class ActionCardView(IconCardView):
    """Card view for rendering special action cards such as all-nighter and
    keyboard kidnappers."""
    def get_file_name(self, card):
        image = ACTION_ICONS.get(card.__class__)
        return f"images/{image}"


class BlankCardView(CardView):
    def redraw(self, card):
        self._canvas.itemconfig(self._back_image, state="hidden")


# Card view router used to work out which view to use to render
CARD_VIEW_ROUTER = {
    NumberCard: NumberCardView,
    CoderCard: CoderCardView,
    TutorCard: TutorCardView,
    AllNighterCard: ActionCardView,
    KeyboardKidnapperCard: ActionCardView,
    Card: BlankCardView
}


class DeckView(tk.Canvas):
    """
    A Canvas that displays a deck of cards on a board.
    """

    def __init__(self, master, pick_card=None, border_colour="#e6e6e6",
                 active_border="red", cards_width=None, width_offset=CARD_WIDTH,
                 height_offset=CARD_HEIGHT, *args, **kwargs):
        """
        Construct a deck view.

        Parameters:
            master (tk.Tk|tk.Frame): The parent of this canvas.
            pick_card (callable): The callback when card in this deck is clicked.
                                  Takes an int representing the cards index.
            border_colour (tk.Color): The colour of the decks border.
            offset (int): The offset between cards in the deck.
        """
        super().__init__(master, *args, **kwargs, bg=border_colour,
                         highlightthickness=2, highlightbackground=border_colour)

        self._active = False
        self._playing = False

        self.width = cards_width
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.pick_card = pick_card
        self.cards = {}

        self._border_colour = border_colour
        self._active_border = active_border

        self.bind("<Button-1>", self._handle_click)

    def toggle_active(self, active=None):
        """Toggle whether the deck should be clickable.

        Parameters:
            active (bool): Whether to activate the deck.
        """
        if active is None:
            self._active = not self._active
        else:
            self._active = active

    def toggle_playing(self, playing=None):
        """Toggle whether the deck is the deck being played.

        Parameters:
            playing (bool): Whether this deck is being played.
        """
        if playing is None:
            self._playing = not self._active
        else:
            self._playing = playing

    def _handle_click(self, event):
        """Handles when the player clicks the deck."""
        # the index of the card in the deck
        slot = event.x // CARD_WIDTH
        if self.width is not None:
            row = event.y // CARD_HEIGHT
            column = event.x // CARD_WIDTH
            slot = column + (row * self.width)

        if self.pick_card is not None and self._active:
            self.pick_card(slot)

    def get_card_view(self, card):
        """Determines the view class for a card.

        Parameters:
            card (Card): The card that requires a view.

        Returns:
            (CardView): The view for the given card.
        """
        return CARD_VIEW_ROUTER.get(card.__class__, CardView)

    def draw_card(self, card, slot):
        """
        Draw a card in the given slot on the deck.

        Parameters:
            card (Card): The card to draw to the deck.
            slot (int): The position in the deck to draw the card.

        Returns:
            (CardView): The card view drawn at the slot for a given card.
        """
        left_side = slot * self.width_offset
        top_side = 0

        if self.width is not None:
            left_side = (slot % self.width) * self.width_offset
            top_side = (slot // self.width) * self.height_offset

        view = self.get_card_view(card)
        self.cards[slot] = view(self, left_side + 2, top_side=top_side + 2)

        return self.cards[slot]

    def draw(self, deck, show=True):
        """
        Draw the deck based of the data in a given deck instance.

        Parameter:
            deck (Deck): The deck to draw in this canvas.
            show (bool): Whether the cards should be displayed or not.
        """
        # resize the canvas to fit all the cards in the deck
        self.resize(deck.get_amount())

        # highlight border
        if self._playing:
            self.config(highlightbackground=self._active_border)
        else:
            self.config(highlightbackground=self._border_colour)

        for i, card in enumerate(deck.get_cards()):
            # retrieve the CardView class for this card
            view = self.cards.get(i, None)

            # draw the CardView if it doesn't exist already
            if view is None:
                view = self.draw_card(card, i)

            # if the type of card has changed, redraw the CardView
            if type(view) != self.get_card_view(card):
                view = self.draw_card(card, i)

            # update details in the CardView
            view.redraw(card if show else None)

    def resize(self, size):
        """
        Calculate the dimensions required to fit 'size' cards in this canvas
        and update the canvas size.

        Parameters:
            size (int): The amount of cards that should be displayed in this deck.
        """
        # ensure that the deck is at least one card wide
        if self.width_offset < CARD_WIDTH:
            width = (self.width_offset * size) + CARD_WIDTH
        else:
            width = (self.width_offset * size)

        if self.width is not None:
            width = (self.width_offset * self.width)

        height = CARD_HEIGHT
        if self.width is not None:
            height *= (size // self.width) + 1

        self.config(width=width + 1, height=height + 1)


class PlayerBoard(tk.Frame):
    """Construct the playing board for an individual player.

    This should display the cards in the players hand, collected coder cards
    and display the players name beneath.
    """

    def __init__(self, master, player, background_colour="#e6e6e6",
                 playable_callback=None, coder_callback=None,
                 *args, **kwargs):
        """
        Construct a players board.

        Parameters:
            master (tk.Tk|tk.Frame): The parent of this frame.
            player (Player): The player who owns this board.
            playable_callback (callable(Player, Card)): The function to call
                when a playable card is clicked in the deck.
            coder_callback (callable(Player, Card)): The function to call
                when a coder card is clicked in the deck.
        """
        super().__init__(master, bg=background_colour, *args, **kwargs)

        self.background_colour = background_colour

        cards = tk.Frame(self, bg=background_colour)
        cards.pack(side=tk.TOP)

        # players deck of playable cards
        callback = lambda card: playable_callback(player, card)
        self.hand = hand = DeckView(cards, pick_card=callback)
        hand.pack(side=tk.LEFT)
        hand.draw(player.get_hand())

        # players deck of collected coder cards
        callback = lambda card: coder_callback(player, card)
        self.coders = coders = DeckView(cards, pick_card=callback)
        coders.pack(side=tk.RIGHT)
        coders.draw(player.get_coders())

        self.draw_title(self, player.get_name())

    def selecting_coder(self, selecting):
        """Activate/deactive whether the collected coder cards can be picked."""
        self.coders.toggle_playing(selecting)
        self.coders.toggle_active(selecting)

    def draw(self, player, clickable=False, playing=False):
        """Redraw the players cards."""
        self.hand.toggle_active(active=clickable)
        self.hand.toggle_playing(playing=playing)
        self.hand.draw(player.get_hand(), show=clickable)
        self.coders.draw(player.get_coders(), show=True)

    def draw_title(self, parent, player):
        """Draw a deck label for a player to the board.

        Parameters:
            parent (tk.*): Parent tkinter object to draw the title within.
            player (str): The name of the player.
        """
        label = tk.Label(parent, text=player,
                         font=('arial', '24', ''),
                         fg="black",
                         bg=self.background_colour)
        label.pack(side=tk.TOP)
        return label


class CoderApp:
    """A graphical Sleeping Coders application"""

    def __init__(self, master, game, board_colour="white",
                 deck_colour="#e6e6e6"):
        """Create a new Coder application based on a given CodersGame.

        Parameters:
            master (tk.Tk): The root window for the Uno application.
            game (CodersGame): The game to display in this application.
            board_colour (tk.Color): The background colour of the board.
            deck_colour (tk.Color): The background colour of the decks on the board.
        """
        self._master = master
        self.game = game
        self.board_colour = board_colour
        self.deck_colour = deck_colour

        # define all the class variables
        self._board = self.decks = self._putdown_pile = self._top_deck =\
            self._bottom_deck = self._action_bar = None

        self.render_decks()

        self.add_menu()

    def render_decks(self):
        # remove old frame, if it exists
        if self._board is not None:
            self._board.pack_forget()

        # create a board frame
        self._board = board = tk.Frame(self._master, padx=20, pady=20,
                                       bg=self.board_colour,
                                       borderwidth=2, relief="groove")
        board.pack(expand=True, fill=tk.BOTH)

        self.decks = decks = {}

        # split the board evenly
        split = len(self.game.players) // 2

        # draw the first decks of players
        for i, player in enumerate(self.game.players[:split]):
            decks[player] = self.draw_deck(player, show=False)

        # draw the middle row of piles
        self._putdown_pile, self._top_deck, self._bottom_deck = self.draw_board()

        # draw the second decks of players
        for i, player in enumerate(self.game.players[split:]):
            decks[player] = self.draw_deck(player, show=False)

        # draw the action bar
        self._action_bar = self.draw_action_bar()

    def update(self):
        """Redraw all the decks in the game."""
        # draw all player decks
        for player in self.game.players:
            playing = player == self.game.current_player() \
                      and self.game.get_action() != Actions.PICKUP_CODER.value

            selecting_coders = self.game.get_action() in (Actions.STEAL_CODER.value,
                                                          Actions.SLEEP_CODER.value)
            selecting_coders = selecting_coders and player.get_coders().get_amount() > 0
            self.decks[player].selecting_coder(selecting_coders)

            self.decks[player].draw(player, clickable=playing,
                                    playing=playing)

        # draw the pile decks
        self._putdown_pile.draw(self.game.putdown_pile)

        # redraw coder cards
        coders = self.game.get_sleeping_coders()
        half_coders = len(coders) // 2
        active = self.game.get_action() == Actions.PICKUP_CODER.value
        self._top_deck.toggle_active(active=active)
        self._top_deck.toggle_playing(playing=active)
        self._bottom_deck.toggle_active(active=active)
        self._bottom_deck.toggle_playing(playing=active)
        self._top_deck.draw(self.build_deck(coders[:half_coders]), show=False)
        self._bottom_deck.draw(self.build_deck(coders[half_coders:]), show=False)

        # update the action bar
        self._action_bar.config(text=self.game.get_action())

    def build_deck(self, cards):
        deck = Deck()
        for card in cards:
            if card is None:
                card = Card()
            deck.add_card(card)
        return deck

    def new_game(self):
        """Start a new game"""
        # clone the old players
        players = []
        for player in self.game.players:
            players.append(player.__class__(player.get_name()))

        # generate a new deck
        pickup_pile = Deck(build_deck(FULL_DECK))
        pickup_pile.shuffle()

        # make players pickup cards
        for player in players:
            cards = pickup_pile.pick(7)
            player.get_hand().add_cards(cards)

        # re-generate the coder list
        coders = CODERS[:]

        self.game = CodersGame(pickup_pile, coders, players)
        self.render_decks()
        self.update()

    def add_menu(self):
        """Create a menu for the application"""
        menu = tk.Menu(self._master)

        # file menu with new game and exit
        file = tk.Menu(menu)
        file.add_command(label="New Game", command=self.new_game)
        file.add_command(label="Exit", command=self._master.destroy)

        # add file menu to menu
        menu.add_cascade(label="File", menu=file)
        self._master.config(menu=menu)

    def pick_card(self, player, slot):
        """Called when a given playable player selects a slot.

        Parameters:
            player (Player): The selecting player.
            slot (int): The card index they selected to play.
        """
        # get the selected card
        card = player.get_hand().get_cards()[slot]

        # pick the card
        self.game.select_card(player, card)

        # wait for next move
        self.step()

    def draw_card(self, _):
        """Pick up a card from the deck for the current player."""
        if not self.game.current_player().is_playable():
            return

        # select card from deck
        next_card = self.game.get_pickup_pile().pick()
        # add card to players deck
        self.game.current_player().get_hand().add_cards(next_card)

        # wait for next move
        self.step()

    def draw_board(self):
        """Draw the middle row of card piles to the board.

        Returns:
            tuple<DeckView, DeckView, DeckView>: The putdown pile and the top
                                                 and bottom decks of coder cards.
        """
        board = tk.Frame(self._board, bg=self.deck_colour)
        board.pack(side=tk.TOP, fill=tk.X, expand=True)

        # top row of coder cards
        half_coders = len(self.game.get_sleeping_coders()) // 2
        top_deck = DeckView(board, pick_card=self.pickup_coder)
        top_deck.toggle_active(active=True)
        top_deck.pack(side=tk.TOP, expand=True)

        board_center = tk.Frame(board, bg=self.deck_colour)
        board_center.pack(side=tk.TOP, fill=tk.X, expand=True)

        # right putdown card pile view
        putdown_pile = DeckView(board_center, width_offset=2)
        putdown_pile.draw(self.game.putdown_pile)
        putdown_pile.pack(side=tk.TOP, padx=50)

        # bottom row of coder cards
        bottom_deck = DeckView(board,
                                    pick_card=lambda slot: self.pickup_coder(half_coders + slot))
        bottom_deck.toggle_active(active=True)
        bottom_deck.pack(side=tk.TOP, expand=True)

        return putdown_pile, top_deck, bottom_deck

    def pickup_coder(self, slot):
        """Called when the player clicks an active sleeping coder card.

        Parameters:
            slot (int): The slot of the coder card.
        """
        self.perform_action(self.game.current_player(), slot)

    def perform_action(self, player, slot):
        """Called when an action is performed.

        Actions may be sleeping a queen, picking up a queen or stealing a queen.

        Parameter:
            player (Player): The player relevant to the action.
            slot (int): The slot of the selected card within it's deck.
        """
        self.game.get_last_card().action(player, self.game, slot)

        self.game.set_action(Actions.NO_ACTION.value)
        self.step()

    def draw_deck(self, player, show=True):
        """Draw a players deck to the board

        Parameters:
            player (Player): The player whose deck should be drawn.
            show (bool): Whether or not to display the players deck.

        Returns:
            DeckView: The deck view for the player.
        """
        board = PlayerBoard(self._board, player,
                            playable_callback=self.pick_card,
                            coder_callback=self.perform_action)
        board.pack(side=tk.TOP)
        return board

    def draw_action_bar(self):
        """Draw a bar at the bottom of the screen to display the current action.
        """
        label = tk.Label(self._board, text="Action",
                         font=('Times', '24', 'bold italic'),
                         foreground="white",
                         background="black")
        label.pack(side=tk.TOP, expand=True, fill=tk.X)
        return label

    def step(self):
        """Perform actions to advance the game a turn."""
        # end the game if a player has won
        if self.game.is_over():
            name = "No one"
            if self.game.winner is not None:
                name = self.game.winner.get_name()
            messagebox.showinfo("Game Over",
                                f"{name} has won!")
            self._master.destroy()
            return

        self.update()

    def play(self):
        """Start the game running"""
        self.game.next_player()
        self.step()


def main():
    # create window for coders
    root = tk.Tk()
    root.title("Sleeping Coders")

    # build a list of players for the game
    players = [Player(generate_name()), Player(generate_name())]

    # build a pickup pile
    pickup_pile = Deck(build_deck(FULL_DECK))
    for i in range(5):
        pickup_pile.copy(pickup_pile)
    pickup_pile.shuffle()

    # deal players cards from the pickup pile
    for player in players:
        cards = pickup_pile.pick(5)
        player.get_hand().add_cards(cards)

    # build a list of sleeping coder cards
    coders = CODERS[:]

    # create and play the game
    game = CodersGame(pickup_pile, coders, players)
    app = CoderApp(root, game)
    app.play()

    # update window dimensions
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()


if __name__ == "__main__":
    main()
