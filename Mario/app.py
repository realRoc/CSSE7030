"""
Simple 2d world where the player can interact with the items in the world.
"""
import os
import sys
import time
from tkinter import messagebox, simpledialog

from game.util import get_collision_direction

__author__ = "Yupeng Wu"
__id__ = "45960600"
__date__ = "2019/10/21"
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk

from typing import Tuple, List

import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World

from level import load_world, WorldBuilder
from player import Player

from PIL import Image

BLOCK_SIZE = 2 ** 4
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}

PLAYERS = {
    "mario": "mario",
    "luigi": "luigi"
}

BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube',
    'b': 'bounce_block',
    'I': 'flag',
    '=': 'tunnel',
    'S': 'switch'
}

ITEMS = {
    'C': 'coin',
    '*': 'star'
}

MOBS = {
    '&': "cloud",
    '@': "mushroom"
}


class BounceBlock(Block):
    """A Bounce Block will bounce the player when a player hit the top of this block.

        When this block is activated, it will show up an animation.
    """
    _id = "bounce"

    def __init__(self):
        """
        Construct a new bounce block.
        """
        super().__init__()
        self._active = False
        # Counter, used in the animation
        self._time = 0
        # Store the current image id, initially it's 'default'
        self._image = 'default'

    def on_hit(self, event, data):
        """
        Callback collision with player event handler.

        Parameters:
            event (pymunk.Arbiter): Data about a collision
            data (world, player): The world and the player that were involved in the collision
        """
        world, player = data
        # Ensure the top of the bounce block is being hit
        if get_collision_direction(player, self) == "A":
            self._active = True
            player.set_velocity((0, -3*player.get_max_velocity()))  # bounce the player
            player.set_jumping(False)  # player can't jump while bounced
            player.set_bounced(True)

    def is_active(self) -> bool:
        """(bool): Returns true if the block has been hit on the top."""
        return self._active

    def step(self, time_delta: float, game_data):
        """Animation process.

        Parameters:
            time_delta (float): The amount of time that has passed since the last step, in seconds
            game_data (tuple<World, Player>): Arbitrary data supplied by the app class
        """
        if self.is_active():  # start animation only when it's active
            self._time += time_delta  # count how many time has passed since active
            # control the order of the image id, it's 1-2-3-2-1
            if self._time <= 0.2 or 0.8 < self._time <= 1:
                self._image = '1'
            elif 0.2 < self._time <= 0.4 or 0.6 < self._time <= 0.8:
                self._image = '2'
            elif 0.4 < self._time <= 0.6:
                self._image = '3'
            else:
                self._time = 0  # the animation will stop after 0.8 seconds
                self._active = False  # set the block to not active
                self._image = 'default'  # set the image to 'default'

    def image(self):
        """(str): Returns the image id of this block."""
        return self._image


class Flagpole(Block):
    """A Flagpole Block is a portal to change the level to the current goal level.

        When player hits the top of this block, the player's health will heal for 1 point.
        But the health won't be greater than the max health.
        When the player hits other side of this block, it change the level.

        The portal access is handle in def _handle_player_collide_block in MarioApp
    """
    _id = "flag"

    def __init__(self):
        """
            Construct a new flagpole block.
        """
        super().__init__()

    def on_hit(self, event, data):
        """
        Callback collision with player event handler.

        Parameters:
            event (pymunk.Arbiter): Data about a collision
            data (world, player): The world and the player that were involved in the collision
        """
        world, player = data
        # Ensure the top of the flag block is being hit
        # and ensure player hadn't been healed before in this level
        if get_collision_direction(player, self) == "A" and not player.get_bonus_health():
            player.change_health(1)
            player.set_bonus_health(True)  # player won't get heal twice in a single level


class Tunnel(Block):
    """A Tunnel Block is a portal to change the level to the current tunnel level.

        When player hits the top of this block, and then duck, it change the level.

        The portal access is handle in def _handle_player_collide_block in MarioApp
    """
    _id = "tunnel"

    def __init__(self):
        """
            Construct a new flagpole block.
        """
        super().__init__()

    def on_hit(self, event, data):
        """
        Callback collision with player event handler.

        Parameters:
            event (pymunk.Arbiter): Data about a collision
            data (world, player): The world and the player that were involved in the collision
        """
        world, player = data
        # Ensure the top of the tunnel block is being hit
        if get_collision_direction(player, self) == "A":
            player.set_on_tunnel(True)  # set the 'on tunnel' status to player
        else:
            player.set_on_tunnel(False)


class Switch(Block):
    """A Block which will destroy all bricks within a close radius of the switch when
    a player hits the top of the block.

    Then remain pressed for 10s. During this time, the player is unable to collide with this block.

    After this time, the switch should revert to its original state and all invisible bricks become visible again.
    """
    _id = "switch"

    def __init__(self):
        """
            Construct a new switch block.
        """
        super().__init__()
        self._time = 0  # storage the press time, initially is 0
        self._block_around = []  # storage the block around
        self._pressed = False  # pressed status

    def on_hit(self, event, data):
        """
        Callback collision with player event handler.

        Parameters:
            event (pymunk.Arbiter): Data about a collision
            data (world, player): The world and the player that were involved in the collision
        """
        world, player = data

        # Ensure the top of the switch block is being hit
        if get_collision_direction(player, self) == "A" and not self._pressed:
            self._time = time.time()  # save the hit time
            self._pressed = True  # set the pressed status to True
            if not self._block_around:  # ensure the block storage is empty
                x, y = self.get_position()  # get the switch position
                self._block_around = world.get_things_in_range(x, y, 20)  # put block around into storage
                for block in self._block_around:  # remove block in the storage
                    if not isinstance(block, Switch) and isinstance(block, Block):
                        world.remove_block(block)

    def step(self, time_delta: float, game_data):
        """Animation process

        Parameters:
            time_delta (float): The amount of time that has passed since the last step, in seconds
            game_data (tuple<World, Player>): Arbitrary data supplied by the app class
        """
        world, player = game_data
        # when time past 10 seconds, bring blocks back
        if time.time() - self._time > 10:
            self._pressed = False  # set pressed status to False
            for block in self._block_around:  # every block in the storage
                if not isinstance(block, Switch) and isinstance(block, Block):
                    x, y = block.get_position()
                    world.add_block(block, x, y)  # add them back
            self._block_around = []  # after done, clear the storage

    def get_pressed(self):
        """(bool): Return the switch block's pressed status"""
        return self._pressed

    def set_pressed(self):
        """Set the switch block's pressed status to True"""
        self._pressed = True


class Star(DroppedItem):
    """A type of item that makes the player invincible for 10 seconds.

    When player is invincible, the health color is yellow and will destroy all the
    collide mod without having any damage.

    Handle the timing in player.py.

    Handle the color in StatusDisplay.
    """
    _id = "star"

    def __init__(self):
        """Construct a star item."""
        super().__init__()

    def collect(self, player: Player):
        """Collect the star and set the player invincible status to True.

        Parameters:
            player (Player): The player which collided with the dropped item.
        """
        player.set_invincible(True)


class MushroomMob(Mob):
    """A moving entity which looks like a mushroom, and walk in a slow rate.

    Will damage player when collide this mod unless the player is jumped on its top,
    it will be destroyed and let the player bounce.
    """
    _id = "mushroom"

    def __init__(self):
        super().__init__(self._id, size=(16, 16), weight=40, tempo=-30)
        """
            Construct a mushroom mob.
            
            With a size of (16, 16), weight is 40 and tempo is -30.
            
            The tempo controls that the mushroom initially movement direction.
            Negative means from right to left.
        """
        self._pressed = False  # record the status of pressed or not
        self._pressed_time = 0  # record when self is pressed
        self._world = None  # record the world, used in remove method
        self._image = '1'  # storage the current image id, default = 1
        self._time = time.time()  # record the time

    def on_hit(self, event: pymunk.Arbiter, data):
        """
        Callback collision with player event handler.

        Parameters:
            event (pymunk.Arbiter): Data about a collision
            data (world, player): The world and the player that were involved in the collision
        """
        world, player = data
        self._world = world  # record the current world
        repelled_velocity = 2*player.get_max_velocity()  # set the repelled velocity
        # if collide the side of mushroom, damage & repelled
        # collide left or right have different repelled direction
        if get_collision_direction(player, self) == "L":
            player.change_health(-1)  # health -1
            player.set_velocity((-repelled_velocity, 0))  # repelled to left
        elif get_collision_direction(player, self) == "R":
            player.change_health(-1)  # health -1
            player.set_velocity((repelled_velocity, 0))  # repelled to right
        elif get_collision_direction(player, self) == "A":
            # if jumped on mushroom, start animation and player being bounced
            player.set_velocity((0, -3*player.get_max_velocity()))  # bounce
            player.set_jumping(False)  # player can't jump while bounced
            player.set_bounced(True)
            self.set_pressed(True)  # start pressed animation

    def step(self, time_delta: float, game_data):
        """Animation process.

        Parameters:
            time_delta (float): The amount of time that has passed since the last step, in seconds
            game_data (tuple<World, Player>): Arbitrary data supplied by the app class
        """
        super().step(time_delta, game_data)
        diff = time.time() - self._time  # create a counter
        # handle walk animation, change image per 0.2 second, order: 1-2-1-2-...
        if diff <= 0.2:
            self._image = '1'
        elif 0.2 < diff <= 0.4:
            self._image = '2'
        else:
            self._time = time.time()  # reset the cycle

    def image(self):
        """(str): Return the current image id."""
        return self._image

    def get_pressed_time(self):
        """(float): Return the recorded pressed time."""
        return self._pressed_time

    def get_pressed(self):
        """(bool): Return the status of pressed or not. Pressed is True."""
        return self._pressed

    def set_pressed(self, status: bool):
        """Set the status of pressed and storage the pressed time.

        status(bool): The statue that you wish. Pressed is True
        """
        self._pressed = status
        self._pressed_time = time.time()

    def remove(self):
        """Remove this mob from its world.

        Couldn't write in the step because we need show squished.
        """
        self._world.remove_mob(self)


def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id == "bounce_block":
        block = BounceBlock()
    elif block_id == "flag":
        block = Flagpole()
    elif block_id == "tunnel":
        block = Tunnel()
    elif block_id == "switch":
        block = Switch()
    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()
    elif item_id == "star":
        item = Star()
    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id == "mushroom":
        mob = MushroomMob()
    else:
        mob = Mob(mob_id, size=(1, 1))
    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))


BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube",
    "bounce_block": "bounce_block",
    "flag": "flag",
    "tunnel": "tunnel",
    "switch": "switch"
}

ITEM_IMAGES = {
    "coin": "coin_item",
    "star": "star"
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    "mushroom": "mushroom"
}


# This is a nest dictionary which stores information about those pictures we need
# in postgraduate task.
# Note: MUST named in a valid way!
# TODO: add this in config
SPRITES = {
    "mario_right_stand": {'position': (80, 34, 95, 49), 'id': "characters"},
    "mario_right_walk_1": {'position': (97, 34, 112, 49), 'id': "characters"},
    "mario_right_walk_2": {'position': (114, 34, 129, 49), 'id': "characters"},
    "mario_right_walk_3": {'position': (131, 34, 146, 49), 'id': "characters"},
    "mario_right_jump": {'position': (233, 34, 248, 49), 'id': "characters"},
    "mario_right_fall": {'position': (216, 34, 231, 49), 'id': "characters"},
    "mario_bounced": {'position': (182, 34, 197, 49), 'id': "characters"},
    "luigi_right_stand": {'position': (80, 99, 95, 114), 'id': "characters"},
    "luigi_right_walk_1": {'position': (97, 99, 112, 114), 'id': "characters"},
    "luigi_right_walk_2": {'position': (114, 99, 129, 114), 'id': "characters"},
    "luigi_right_walk_3": {'position': (131, 99, 146, 114), 'id': "characters"},
    "luigi_right_jump": {'position': (233, 99, 248, 114), 'id': "characters"},
    "luigi_right_fall": {'position': (216, 99, 231, 114), 'id': "characters"},
    "luigi_bounced": {'position': (182, 99, 197, 114), 'id': "characters"},
    "mushroom_walk_1": {'position': (0, 15, 16, 32), 'id': "enemies"},
    "mushroom_walk_2": {'position': (16, 15, 32, 32), 'id': "enemies"},
    "mushroom_squished": {'position': (32, 23, 48, 32), 'id': "enemies"},
    "coin_flip_1": {'position': (19, 113, 28, 126), 'id': "items"},
    "coin_flip_2": {'position': (5, 113, 10, 126), 'id': "items"},
    "bounce_used_1": {'position': (112, 113, 127, 127), 'id': "items"},
    "bounce_used_2": {'position': (96, 105, 111, 127), 'id': "items"},
    "bounce_used_3": {'position': (80, 97, 95, 127), 'id': "items"}
}


class SpriteSheetLoader:
    """This class able to load image from a given path with given info."""
    def __init__(self, path, position: (int, int, int, int), name_id):
        """Construct a sprite sheet loader.

        path(str): The file path of the sprite sheet.
        position(4 dimension tuple, (int, int, int, int)):
                The sub-rectangle position in the sheet, the 1st and 2nd int is the
            x-y co-ordinate of the upper-left. 3rd and 4th int is the x-y co-ordinate
            of the bottom-right.
        name_id(str): The id of sprite in the dictionary.
        """
        self._path = path
        self._position = position
        self._name = name_id

    def load_image(self):
        """Try to open the file with the path and return image.

        Will pop error if path is wrong.

        (PIL.Image.Image): Return a image with the given path.
        """
        try:
            return Image.open(self._path, 'r')
        except IOError:
            messagebox.showerror("Error", "Wrong sprite file path!")

    def load_sprite(self, need_reverse: bool):
        """Crop needed image with given order of 'reverse'. Then save it

        If 'reverse' is True, crop the image and then transpose it with a flip.

        Parameter:
            need_reverse(bool): If this image need reverse, it's 'True'.
        Return:
            save_name(str): An abspath of the cropped image.
        """
        im = self.load_image()  # load the sheet picture
        if need_reverse:  # judge whether reverse or not
            region = im.crop(self._position).transpose(Image.FLIP_LEFT_RIGHT)
        else:
            region = im.crop(self._position)
        # save the cropped image to 'sprite' folder
        path = os.path.abspath(os.path.dirname(sys.argv[0])) + '\\sprite\\' # set the path
        save_name = path + self._name + '.png'  # set the image's name
        if not os.path.exists(path):  # if we don't have a 'sprite' folder
            os.makedirs(path)  # then create it
        region.save(save_name)  # save it in the 'sprite' folder
        return save_name


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    def __init__(self, block_images, item_images, mob_images):
        super().__init__(block_images, item_images, mob_images)
        """Construct MarioViewRouter with appropriate entity id to image file mappings.

        Parameters:
             block_images (dict<str: str>): A mapping of block ids to their respective images
             item_images (dict<str: str>): A mapping of item ids to their respective images
             mob_images (dict<str: str>): A mapping of mob ids to their respective images
        """
        self._coin_time = time.time()  # coin animation counter
        # prepare the images of all sprites in the SPRITES dictionary
        for sprite in SPRITES:
            position = SPRITES[sprite]["position"]  # get the sprite's position
            file_name = SPRITES[sprite]["id"] + ".png"  # get the sprite's sprite sheet
            # abspath for the sprite sheet
            path = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\spritesheets\\" + file_name
            # use SpriteSheetLoader to crop the sprite image we need
            image_path = SpriteSheetLoader(path, position, sprite).load_sprite(False)
            self._images[sprite] = tk.PhotoImage(file=image_path)  # put the image in the self._images
            # characters only have right image in the sheet
            # so we need to have another reversed image for 'left'
            if '_right_' in sprite:
                sprite_reversal = sprite.replace('_right_', '_left_')
                image_path = SpriteSheetLoader(path, position, sprite_reversal).load_sprite(True)
                self._images[sprite_reversal] = tk.PhotoImage(file=image_path)

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for Player.

        Parameters:
            instance (Entity): The player to draw
            shape (pymunk.Shape): The player shape in the world
            view (tk.Canvas): The canvas on which to draw the player
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        # 'default' is a status where player has no action and buff
        if instance.image() != 'default':
            if shape.body.velocity.x > 0:  # if player is horizontally moving right
                if shape.body.velocity.y > 0:  # if player is vertically moving down
                    image = self.load_image(instance.get_name() + "_right_fall")  # it's falling
                elif shape.body.velocity.y < 0 and not instance.is_jumping():
                    # if player is vertically moving up with a horizontally velocity
                    # and it's not jumping, means it's flying
                    image = self.load_image(instance.get_name() + "_right_jump")
                else:
                    # if player has no vertically velocity, it's walking
                    image = self.load_image(instance.get_name() + "_right_walk_" + instance.image())
                return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                          image=image, tags="player")]
            elif shape.body.velocity.x < 0:  # if player is horizontally moving left
                if shape.body.velocity.y > 0:  # if player is vertically moving down
                    image = self.load_image(instance.get_name() + "_left_fall")  # it's falling
                elif shape.body.velocity.y < 0 and not instance.is_jumping():
                    # if player is vertically moving up with a horizontally velocity
                    # and it's not jumping, means it's flying
                    image = self.load_image(instance.get_name() + "_left_jump")
                else:
                    # if player has no vertically velocity, it's walking
                    image = self.load_image(instance.get_name() + "_left_walk_" + instance.image())
                return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                          image=image, tags="player")]
        elif shape.body.velocity.y < 0 and instance.is_bounced():  # if player is bounced
            # I regard 'bounced' is a important status that we must show this first
            # if you bounced then move horizontally, it's left/right flying
            image = self.load_image(instance.get_name() + "_bounced")  # it's bounced
            return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="player")]
        else:  # which means player is doing nothing
            image = self.load_image(instance.get_name() + "_right")  # it's 'default'
            return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="player")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for MysteryBlock.

        Parameters:
            instance (Entity): The MysteryBlock to draw
            shape (pymunk.Shape): The MysteryBlock shape in the world
            view (tk.Canvas): The canvas on which to draw the MysteryBlock
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        if instance.is_active():  # if MysteryBlock is active
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(BounceBlock)
    def _draw_bounce_block(self, instance: BounceBlock, shape: pymunk.Shape,
                           view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for BounceBlock.

        Parameters:
            instance (Entity): The BounceBlock to draw
            shape (pymunk.Shape): The BounceBlock shape in the world
            view (tk.Canvas): The canvas on which to draw the BounceBlock
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        # 'default' is a status where BounceBlock has not been triggered
        if instance.image() != 'default':  # if triggered this block
            # the animation rate and image order is handled in BounceBlock
            image = self.load_image("bounce_used_" + instance.image())  # changed image for animation
            return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="block")]
        else:
            image = self.load_image("bounce_block")  # it's 'default'
            return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="block")]

    @ViewRenderer.draw.register(Switch)
    def _draw_switch(self, instance: Switch, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for Switch.

        Parameters:
            instance (Entity): The Switch to draw
            shape (pymunk.Shape): The Switch shape in the world
            view (tk.Canvas): The canvas on which to draw the Switch
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        if instance.get_pressed():  # if switch is pressed
            image = self.load_image("switch_pressed")
        else:
            image = self.load_image("switch")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(MushroomMob)
    def _draw_mushroom(self, instance: MushroomMob, shape: pymunk.Shape,
                       view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for MushroomMob.

        Parameters:
            instance (Entity): The MushroomMob to draw
            shape (pymunk.Shape): The MushroomMob shape in the world
            view (tk.Canvas): The canvas on which to draw the MushroomMob
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        if instance.get_pressed():  # if mushroom is pressed
            image = self.load_image("mushroom_squished")  # change image for 'squished'
            if time.time() - instance.get_pressed_time() > 0.5:  # if time past for 0.5 second
                instance.remove()  # remove the squished mushroom from the world
        else:  # if mushroom not be pressed
            # the walking animation rate is handled in MushroomMob
            image = self.load_image("mushroom_walk_"+instance.image())  # walking
        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Coin)
    def _draw_coin_flip(self, instance: Coin, shape: pymunk.Shape,
                        view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Method to draw the canvas elements for Coin.

        Parameters:
            instance (Entity): The Coin to draw
            shape (pymunk.Shape): The Coin shape in the world
            view (tk.Canvas): The canvas on which to draw the Coin
            offset (tuple<int, int>): The offset of the logical view from the canvas.
        """
        diff = time.time() - self._coin_time  # time counter
        # handle the animation, image order: default-2-1-2-default-...
        # changed per 0.1 second
        if diff <= 0.1 or 0.2 < diff <= 0.3:
            image = self.load_image("coin_flip_2")
        elif 0.1 < diff <= 0.2:
            image = self.load_image("coin_flip_1")
        elif 0.3 < diff <= 0.4:
            image = self.load_image("coin_item")
        else:
            self._coin_time = time.time()  # reset the cycle
            image = self.load_image("coin_item")
        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]


class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    _world: World

    def __init__(self, master: tk.Tk):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """
        self._master = master
        master.title("Mario")  # set title
        self._config = {}  # set config nest dictionary
        self._level_dic = {}  # set level nest dictionary
        self._config_status = True  # status for successfully read config or not
        self._pause = False  # if True, game will pause, if False, game continue

        if self.config_input():  # read config info from file. If can't read, get False
            for key in self._config.keys():  # seeking for some basic info
                if key == 'World':  # from heading: 'World'
                    if all(k in self._config[key] for k in ('gravity', 'start')):
                        try:  # get gravity from 'World', then turns it into 'int'
                            self._gravity = int(self.get_config(key, 'gravity'))
                        except ValueError:  # if failed
                            messagebox.showerror("Invalid value in World", "Invalid value in gravity!")
                            self.config_exit()
                        try:  # get start level. Try to open it
                            self._start_level = self.get_config(key, 'start')
                            open(self._start_level)
                        except IOError:  # if failed
                            messagebox.showerror("Invalid value in World",
                                                 "Don't have this " + self._start_level + " file!")
                            self.config_exit()
                    else:  # if 'World' don't have gravity and start_level
                        messagebox.showerror("Missing attribute", "Missing attributes in World!")
                        self.config_exit()
                elif key == 'Player':  # from heading: 'Player'
                    if all(k in self._config[key] for k in
                           ('character', 'x', 'y', 'mass', 'health', 'max_velocity')):
                        try:  # try get all those stuff below, and change their type
                            self._x = float(self.get_config(key, 'x'))  # get x co-ordinate
                            self._y = float(self.get_config(key, 'y'))  # get y co-ordinate
                            self._mass = int(self.get_config(key, 'mass'))  # get mass
                            self._max_health = int(self.get_config(key, 'health'))  # get max_health
                            self._max_velocity = int(self.get_config(key, 'max_velocity'))  # get max_velocity
                        except ValueError:  # if failed => invalid value
                            messagebox.showerror("Invalid value in Player", "Invalid value in Player attributes!")
                            self.config_exit()
                        self._character = self.get_config(key, 'character')  # get character
                        if self._character not in PLAYERS:  # check character
                            messagebox.showerror("Invalid value in Player",
                                                 "Don't have this '" + self._character + "' character!")
                            self.config_exit()
                    else:  # must missing some of the attribute
                        messagebox.showerror("Missing attribute", "Missing attributes in Player!")
                        self.config_exit()
                else:  # from heading which is not 'World' and 'Player' => 'Level'
                    try:  # check the level existence
                        open(key)
                        if self.get_config(key, 'goal') is not None:  # level must have a goal
                            self._this_level = {}  # create a new dic for this level
                            self._this_level.update(goal=self.get_config(key, 'goal'))  # store the goal
                        else:  # warn that must have a goal
                            messagebox.showerror("Missing attribute", "'" + key +
                                                 "' level must have a goal!")
                            self.config_exit()
                        # if has tunnel, update; if don't, update with None
                        self._this_level.update(tunnel=self.get_config(key, 'tunnel'))
                        self._this_level.update(record=(self._max_health, 0))  # set record(health, score)
                        # update this level to the general level dic
                        self._level_dic.update(dict([(key, self._this_level)]))
                    except IOError:  # if this level don't exist
                        messagebox.showerror("Invalid heading", "Don't have this '" + key + "' level")
                        self.config_exit()
        else:  # if fail in read progress
            self.config_exit()

        if self._config_status:  # only build the world with success config settings
            # build the world with config settings
            world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, self._gravity), fallback=create_unknown)
            world_builder.register_builders(BLOCKS.keys(), create_block)
            world_builder.register_builders(ITEMS.keys(), create_item)
            world_builder.register_builders(MOBS.keys(), create_mob)
            self._builder = world_builder

            self._player = Player(self._character, max_health=self._max_health)
            # set max_velocity to player to avoid hard-coding
            self._player.set_max_velocity(self._max_velocity)
            self._filename = self._start_level  # set current level
            self._goal = self._level_dic[self._filename]['goal']  # get current level's goal
            self._tunnel = self._level_dic[self._filename]['tunnel']  # get current level's tunnel
            self.reset_world(self._filename)  # load the start level
            # View entities on canvas
            self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)
            size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
            self._view = GameView(master, size, self._renderer)
            self._view.pack()

            self._press = False  # status for whether player press the switch
            self.bind()  # bind the keyboard

            # Status Display
            self._percentage = 1  # player health percentage
            self._score = self._player.get_score()  # player's score
            self._statue = StatueDisplay(master, size[0], size[1])  # build statue display
            self._statue.pack(side=tk.BOTTOM, fill=tk.X)  # pack it in the bottom

            # Wait for window to update before continuing
            master.update_idletasks()
            self.step()

            # File menu
            menubar = tk.Menu(self._master)
            # Tell master what is this menu
            self._master.config(menu=menubar)
            file_menu = tk.Menu(menubar)  # build a menu
            menubar.add_cascade(label="File", menu=file_menu)  # File
            file_menu.add_command(label="Load Level", command=self.load_map)  # Load Level
            file_menu.add_command(label="Reset Level", command=self.reset_map)  # Reset Level
            file_menu.add_command(label="High Score", command=self.show_score)  # show High Score
            file_menu.add_command(label="Exit", command=self.exit)  # Exit the game
            menubar.add_cascade(label="Pause/Begin", command=self.pause)  # pause switch

    def config_input(self):
        """Pop a str input message box at the beginning. Please input either abspath or
        a file name (which must be in the same folder with this file) of the config file

        Return:lev
            (bool): If 'True' means valid config path with 'World' and 'Player'
        """
        answer = simpledialog.askstring("Input", "Please input the path of the config file.",
                                        parent=self._master)  # ask for a string
        if answer is not None:
            try:
                self.read_config(answer)  # read the config
                if all(k in self._config for k in ('World', 'Player')):
                    # check whether have a 'World' and 'Player'
                    return True
                else:  # if don't have 'World' or 'Player'
                    messagebox.showerror("Missing necessary heading", "Missing World or Player")
                    return False
            except IOError:
                messagebox.showerror("Invalid path",
                                     "'" + answer + "' is not a valid path!")
                return False

    def read_config(self, filename):
        """Read a config.txt file line by line

        Parameter:
            filename(str): The path of the config file
        Return:
            (dic): A dictionary which contains all information in config.txt
        """
        heading = None
        with open(filename) as fin:  # open the file
            for line in fin:
                line = line.strip()  # cut the tail
                if line.startswith('==') and line.endswith('=='):  # detect headings
                    heading = line[2:-2]  # heading
                    self._config[heading] = {}  # create a dictionary for the heading
                elif line.count(':') == 1 and heading is not None:  # detect attribute
                    attr, _, value = line.partition(':')  # get attribute and their value
                    self._config[heading][attr[:-1]] = value[1:]  # update into dic
                elif line == "":  # if line is empty, skip
                    continue
                else:  # bad line
                    messagebox.showerror("Error", "Bad config file, I can't read it!")
        return self._config

    def get_config(self, heading, attribute):
        """Get value of the attribute in a heading

        Parameter:
            heading(str): The key in config dictionary
            attribute(str): The key in heading dictionary in config dictionary
        Return:
            (str): The value of the attribute.
                   If heading don't have the attribute, return None.
        """
        if attribute in self._config[heading]:
            return self._config[heading][attribute]
        else:
            return None

    def config_exit(self):
        """A command. Exit the app if there's an error during the reading config progress"""
        self._master.destroy()
        self._config_status = False  # ensure the world wouldn't be built

    def get_high_score(self, level):
        """Get the high scored player and their score according to the given level.

        Parameter:
            level(str): The given level name.
        Return:
            (list): A sorted list in descending order by score.
                   Eg: [('Player1', 'Score1'), ('Player2', 'Score2')]
                   The 'Player(s)' and 'Score(s)' are string.
        """
        score_board = {}  # a dic used to store info
        heading = None
        path = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\HighScores\\"
        if not os.path.exists(path):  # check whether there's a 'HighScores' folder
            os.makedirs(path)  # if not, create and return nothing
            return
        # check whether this level has a high score storage
        elif not os.path.exists(path + level):
            return  # if don't have, return nothing
        else:  # if do have a storage
            with open(path + level) as fin:  # open the file
                for line in fin:
                    line = line.strip()  # cut the tail
                    if line.startswith('==') and line.endswith('=='):  # detect headings
                        heading = line[2:-2]  # heading line
                    elif line.count(':') == 1 and heading == level:  # detect attribute
                        name, _, score = line.partition(':')  # get attribute value
                        # this storage have all the records, for a player find the highest score
                        if name in score_board.keys():  # if already has this player in dic
                            if int(score) > int(score_board[name]):  # compare score
                                score_board[name] = score  # if bigger, update
                        else:
                            score_board[name] = score  # new player, update
            # sort the list and take the top 10
            return sorted(score_board.items(), key=lambda x: x[1], reverse=True)[:10]

    def set_high_score(self):
        """Set the high score of a player. Triggered when a flag is collided."""
        # pop a window for player's name
        answer = simpledialog.askstring("Cheers", "What's your name?",
                                        parent=self._master)
        if answer is not None:
            # set the player's record(str)
            record = '==' + self._filename + '==\n' \
                     + answer + ':' + str(self._player.get_score()) + '\n'
        else:  # if didn't have the name
            messagebox.showinfo("Notice", "Not gonna take this on the score board.")
            return False  # skip the method
        # save the record
        path = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\HighScores\\" + self._filename
        if not os.path.exists(path):  # check whether have the file
            open(path, 'w')  # if not, create
        with open(path, 'r+') as fin:  # write record into the file
            fin.read()
            fin.write(record)
            fin.close()

    def show_score(self):
        """Show the score board with a Toplevel."""
        self._pause = True  # pause the game when you check the score
        score_list = self.get_high_score(self._filename)  # get the record
        top = tk.Toplevel()  # create a Toplevel
        top.title('Score Board')
        # create a text label for notification
        title = tk.Label(top, text='High Scored Player in This Level', width=70)
        title.pack(side=tk.TOP, ipady=1)
        if score_list is None:  # check whether the record is empty
            tk.Label(top, text='No record in this level yet!', width=70).pack(side=tk.TOP, ipady=1)
        else:  # if not empty
            for record in score_list:  # shows up all the detail
                tk.Label(top, text=record[0] + ' : ' + record[1]).pack(side=tk.TOP, ipady=1)

    def pause(self):
        """A switch for pause and restart the game."""
        if self._pause:
            self._pause = False
        else:
            self._pause = True
        self.step()  # trigger the next step

    def load_map(self):
        """A method to load a new level"""
        # ask for a new level(str)
        answer = simpledialog.askstring("Input", "Please input a level",
                                        parent=self._master)
        if answer is not None:
            if answer in self._level_dic.keys():  # ensure the level exist
                self.reset_world(answer)  # load that level
                # if you load a new level, player's health will remain but score will be clear
                self._player.change_score(-self._player.get_score())  # a personal setting
            else:
                messagebox.showerror("Invalid filename",
                                     "'" + answer + "' is not a filename!")

    def reset_map(self):
        """A method to reset the current level"""
        self.reset_world(self._filename)

    def exit(self):
        """A method to exit the game

        Return:
            (bool): If exit, return True. Else, return False
        """
        ans = messagebox.askokcancel('Verify exit', 'Really quit?')
        if ans:
            self._master.destroy()
            return True
        else:
            return False

    def reset_world(self, new_level):
        """A method to change the level

        Parameter:
            new_level(str): The level which you wish to be changed to
        """
        if new_level == self._start_level:  # if restart
            self._player.change_health(self._max_health)  # set player with max_health
            self._player.change_score(-self._player.get_score())  # set player score 0
        elif self._filename == new_level:  # if reset current level
            # set the player's health and score by previous record
            record_health, record_score = self._level_dic[new_level]['record']  # get health & score
            self._player.change_health(record_health - self._player.get_health())
            self._player.change_score(record_score - self._player.get_score())

        self._filename = new_level  # change the current level name
        self._goal = self._level_dic[self._filename]['goal']  # change the current goal
        self._tunnel = self._level_dic[self._filename]['tunnel']  # change the current tunnel
        self._player.set_bonus_health(False)  # player can have bonus health again
        self._player.set_jumping(False)  # player can't jump until land
        self._player.set_invincible(False)  # buff won't be brought to another level
        # create world, add player, setup collision handlers
        self._world = load_world(self._builder, self._filename)
        self._world.add_player(self._player, self._x, self._y, self._mass)
        self._builder.clear()
        self._setup_collision_handlers()

    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        # jump
        self._master.bind('<w>', lambda jump: self._jump())
        self._master.bind('<space>', lambda jump: self._jump())
        self._master.bind('<Up>', lambda jump: self._jump())
        # move left
        self._master.bind('<a>', lambda move_left: self._move(-self._max_velocity, self._player.get_velocity()[1]))
        self._master.bind('<Left>', lambda move_left: self._move(-self._max_velocity, self._player.get_velocity()[1]))
        # duck
        self._master.bind('<s>', lambda duck: self._duck())
        self._master.bind('<Down>', lambda duck: self._duck())
        # move right
        self._master.bind('<d>', lambda move_right: self._move(self._max_velocity, self._player.get_velocity()[1]))
        self._master.bind('<Right>', lambda move_right: self._move(self._max_velocity, self._player.get_velocity()[1]))

    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)
        self._view.draw_entities(self._world.get_all_things())
        # calculate the health and score in every step
        max_hp = self._player.get_max_health()
        current_hp = self._player.get_health()
        # if player is invincible, don't change health
        self._statue.set_health(current_hp / max_hp, self._player.get_invincible())
        self._statue.set_score(self._player.get_score())

    def scroll(self):
        """Scroll the view along with the player in the center unless
        they are near the left or right boundaries
        """
        x_position = self._player.get_position()[0]
        half_screen = self._master.winfo_width() / 2
        world_size = self._world.get_pixel_size()[0] - half_screen

        # Left side
        if x_position <= half_screen:
            self._view.set_offset((0, 0))

        # Between left and right sides
        elif half_screen <= x_position <= world_size:
            self._view.set_offset((half_screen - x_position, 0))

        # Right side
        elif x_position >= world_size:
            self._view.set_offset((half_screen - world_size, 0))

    def step(self):
        """Step the world physics and redraw the canvas."""

        data = (self._world, self._player)
        self._world.step(data)

        self.scroll()
        self.redraw()
        # check whether dead
        if self._player.get_health() == 0:  # if died
            answer = messagebox.askyesno("GAME OVER", "Would you like to restart?")
            if answer:  # have a choice to reset the current level
                self.reset_world(self._filename)
            else:  # or quit the game
                self.exit()
        # control the pause/restart
        if self._pause:  # if is paused
            return  # step will stop its process
        else:  # not paused
            self._master.after(10, self.step)  # go! next step

    def _move(self, dx, dy):
        """A method which gives player a velocity to move"""
        # horizontal velocity is dx, vertical velocity is dy
        self._player.set_velocity((dx, dy))

    def _jump(self):
        """A method which enable player to jump"""
        # can't jump while jump
        if self._player.is_jumping():
            # no hard-code, set jump with 2*max_velocity
            self._player.set_velocity((0, -2*self._max_velocity))
            self._player.set_jumping(False)  # means can't jump

    def _duck(self):
        """A method which trigger tunnel while player is on a tunnel"""
        if self._player.get_on_tunnel():  # if it's on tunnel
            if self._tunnel is None:  # if current level didn't a tunnel goal in config
                messagebox.showerror("Missing settings",
                                     "Please check the config file to set this tunnel!")
            else:
                # check with tunnel level to load
                self._level_dic[self._tunnel]['record'] = (self._player.get_health(), self._player.get_score())
                self.reset_world(self._tunnel)  # load the tunnel level

    def _setup_collision_handlers(self):
        """A method which handle all the collision."""
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)
        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block)
        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)

    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the mob collide block
        
        Parameters:
            mob (Mob): The mob that was involved in the collision
            block (Block): The block that the mob collided with
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
             bool: True. Don't ignore this type of collision
        """
        if mob.get_id() == "fireball":  # fireball will destroy block
            if block.get_id() == "brick":
                self._world.remove_block(block)
            self._world.remove_mob(mob)
        elif mob.get_id() == "mushroom":  # mushroom will change their move direction after collide
            # collide on either left or right side
            if get_collision_direction(mob, block) == "L" or get_collision_direction(mob, block) == "R":
                mob.set_tempo(-mob.get_tempo())  # change direction(tempo)
        return True

    def _handle_mob_collide_item(self, mob: Mob, dropped_item: DroppedItem, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the mob collide item

        Parameters:
            mob (Mob): The mob that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the mob collided with
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
            bool: False. Ignore this type of collision
        """
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the mob collide mob

        Parameters:
            mob1 (Mob): The mob that was involved in the collision
            mob2 (Mob): The mob that was involved in the collision
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
            bool: False. Ignore this type of collision
        """
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        return False

    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """

        dropped_item.collect(self._player)
        self._world.remove_item(dropped_item)
        return False

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the player collide block

        Parameters:
            player (Player): The player that was involved in the collision
            block (Block): The block that was involved in the collision
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
            bool: False. Ignore this type of collision
        """
        if get_collision_direction(player, block) == 'A':  # if player land on a block
            self._player.set_jumping(True)  # player can jump
            self._player.set_bounced(False)  # player isn't bounced
        block.on_hit(arbiter, (self._world, player))
        if block.get_id() == "flag":  # if player collide a flag
            if get_collision_direction(player, block) != "A":  # not hit the top of the flag
                self.set_high_score()  # record the score
                if self._goal == 'END':  # if this flag is the END
                    messagebox.showinfo("Congratulation", "GAME OVER!")  # game over
                    self._pause = True  # game pause
                    leave = self.exit()  # ask whether quit or not
                    if not leave:
                        self.reset_world(self._start_level)  # game restart
                        self._pause = False  # game stop pause
                # record the player's current status
                self._level_dic[self._goal]['record'] = (self._player.get_health(), self._player.get_score())
                self.reset_world(self._goal)  # change to the goal level
        elif block.get_id() == "switch":  # if collide with a switch
            if block.get_pressed():  # check if block get pressed
                self._pressed = True  # if yes, player is in 'press mode'
                return False  # which will not collide the 'pressed switch'
        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the player collide mob

        Parameters:
            player (Player): The player that was involved in the collision
            mob (Mob): The mob that was involved in the collision
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
            bool: True. Don't ignore this type of collision
        """
        if player.get_invincible():  # if player has in invincible buff
            self._world.remove_mob(mob)  # destroy the mob
            return True
        mob.on_hit(arbiter, (self._world, player))
        if mob.get_id() == "mushroom":  # if player collide with mushroom
            mob.set_tempo(-mob.get_tempo())  # change mushroom move direction
        return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        """A method which handle all the player separate block

        Parameters:
            player (Player): The player that was involved in the collision
            block (Block): The block that was involved in the collision
            data (dict): data that was added with this collision handler
            arbiter (pymunk.Arbiter): Data about a collision
        Return:
            bool: True. Don't ignore this type of collision
        """
        # player no collide with block
        return not self._handle_player_collide_block(player, block, data, arbiter)


class StatueDisplay(tk.Frame):
    """A frame shows the player's status.

    Update the player's current health and score per step.
    """
    def __init__(self, master, width, height):
        """Construct a StatueDisplay frame

        Parameter:
            master (tk.Tk): The parent frame of the StatueDisplay.
            width (int): The frame's width
            height (int): The frame's height
        """
        super().__init__(master)
        self._width = width
        self._height = height
        # build a black background frame in master
        self._background = tk.Frame(master, bg='black', width=width, height=height)
        self._background.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        # build a score bar in background frame
        self._score_bar = tk.Label(self._background)
        self._score_bar.pack(side=tk.BOTTOM, fill=tk.X)
        # build a health canvas in background frame
        self._health_bar = tk.Canvas(self._background, height=20, bd=0)
        self._health_bar.pack(side=tk.BOTTOM, anchor=tk.W)

    def set_score(self, score):
        """A method of set the score bar using config"""
        self._score_bar.config(text="Score: " + format(score))

    def set_health(self, percentage, invincible: bool):
        """A method of set the health bar using config

        Parameter:
            percentage (float): The percentage of player's health
            invincible (bool): Whether player is in invincible buff
        """
        if invincible:
            # when invincible the health color is yellow
            self._health_bar.config(bg="yellow", width=int(percentage * self._width))
        else:  # when not invincible
            # health bar's color will change due to different percentage of health
            if percentage >= 0.5:
                self._health_bar.config(bg="green", width=int(percentage * self._width))
            elif percentage >= 0.25:
                self._health_bar.config(bg="orange", width=int(percentage * self._width))
            else:
                self._health_bar.config(bg="red", width=int(percentage * self._width))


if __name__ == '__main__':
    root = tk.Tk()
    app = MarioApp(root)
    root.mainloop()
