"""Class for representing a Player entity within the game."""
import time

__version__ = "1.1.0"

from game.entity import DynamicEntity


class Player(DynamicEntity):
    """A player in the game"""
    _type = 3

    def __init__(self, name: str, max_health: float = 20):
        """Construct a new instance of the player.

        Parameters:
            name (str): The player's name
            max_health (float): The player's maximum & starting health
        """
        super().__init__(max_health=max_health)

        self._image = 'default'  # current image for animation
        self._image_time = 0  # counter for animation
        self._name = name  # player's name
        self._score = 0  # player's score
        self._invincible = False  # player's invincible or not
        self._invincible_time = 0  # counter for invincible
        self._is_on_tunnel = False  # whether player is on a tunnel
        self._bonus_health = False  # whether player has bonus a buff
        self._bounced = False  # whether player is bounced
        self._max_velocity = 0  # the max_velocity of the player, controlled by config

    def get_name(self) -> str:
        """(str): Returns the name of the player."""
        return self._name

    def get_score(self) -> int:
        """(int): Get the players current score."""
        return self._score

    def change_score(self, change: float = 1):
        """Increase the players score by the given change value."""
        self._score += change

    def change_health(self, change):
        """Change a player's health with a given change.

        Parameter:
            change (int): Positive for increase. Negative for decrease.
        """
        if change > 0:  # if increase the health
            self._health += change  # increase the health
            # current health won't larger than max
            if self._health > self._max_health:
                self._health = self._max_health
        else:  # if decrease the health
            if not self._invincible:
                self._health += change  # decrease the health
                if self._health < 0:  # current health won't smaller than 0
                    self._health = 0

    def get_invincible(self):
        """Get the status of invincible

        Return:
            (bool): True means is invincible.
        """
        return self._invincible

    def set_invincible(self, status: bool):
        """Set the status of invincible

        Parameter:
            status (bool): The status you wish to give invincible
        """
        self._invincible = status
        if self._invincible:  # if become invincible
            self._invincible_time = time.time()  # record the invincible time

    def step(self, time_delta: float, game_data):
        """Handle all the animation or invincible statue

        Parameter:
            time_delta (float): The diff time between every step
            game_data (world, player): The world and the player.
        """
        if self.get_invincible():  # if become invincible
            if time.time() - self._invincible_time > 10:  # if the time past 10 seconds
                self.set_invincible(False)  # remove the buff

        if self.get_velocity()[0] != 0:  # if moved horizontally
            self._image_time += time_delta  # count time while move
            # set the order of image id while moving, generally it's 3-2-1-2-3-...
            if self._image_time <= 0.1:  # if time past 0.1 second
                self._image = '3'  # set image id to '3'
            elif 0.1 < self._image_time <= 0.2 or 0.3 < self._image_time <= 0.4:
                # if time past 0.2 or 0.4 second
                self._image = '2'  # set image id to '2'
            elif 0.2 < self._image_time <= 0.3:  # if time past 0.3 second
                self._image = '1'  # set image id to '1'
            elif self._image_time > 0.4:  # reset the cycle
                self._image = '3'
                self._image_time = 0
        else:  # if not moving
            self._image = 'default'  # set it with default image

    def get_on_tunnel(self):
        """Get the status of whether the player is on a tunnel

        (bool): Return True means player is on a tunnel
        """
        return self._is_on_tunnel

    def set_on_tunnel(self, status: bool):
        """Set the status of whether the player is on a tunnel

        Parameter:
            status (bool): The status you wish to set for.
        """
        self._is_on_tunnel = status

    def get_bonus_health(self):
        """Get whether the player has been bonus health in this level

        (bool): Return True means player has get the bonus
        """
        return self._bonus_health

    def set_bonus_health(self, status: bool):
        """Set the status of whether the player has been bonus health in this level

        Parameter:
            status (bool): The status you wish to set for.
        """
        self._bonus_health = status

    def set_position(self, x: float, y: float):
        """Set the position of the player. Used by the location in config.txt

        Parameter:
            x (float): The x co-ordinate of the player
            y (float): The y co-ordinate of the player
        """
        self._shape.body.position.x = x
        self._shape.body.position.y = y

    def image(self):
        """Get the player's current image

        (str): Return the image's id. It's a key used to search in a dictionary
               for the image.
        """
        return self._image

    def is_bounced(self):
        """Get the status of whether player is bounced

        (bool): Return True means player is bounced
        """
        return self._bounced

    def set_bounced(self, status: bool):
        """Set the status of whether the player has been bounced

        Parameter:
            status (bool): The status you wish to set for.
        """
        self._bounced = status

    def set_max_velocity(self, velocity):
        """Set the max velocity of the player.

        Parameter:
            velocity (int): The value of the max velocity.
        """
        self._max_velocity = velocity

    def get_max_velocity(self):
        """Get the max velocity of the player.

        (int): Return the max velocity of the player.
        """
        return self._max_velocity

    def __repr__(self):
        return f"Player({self._name!r})"
