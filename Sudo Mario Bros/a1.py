"""
CSSE1001 2019s2a1
"""

from a1_support import *


# Write the expected functions here

# Implement Functions
def get_position_in_direction(position, direction):
    """This function is used to return the position that would result from moving
    from given position in the given direction.

    Parameters:
        position (tuple<int, int>): The row, column position of a tile.
        direction (str): According to the action. "r", "l", "u" or "d".

    Returns:
        new_position (tuple<int, int>).
    """
    x, y = position
    if direction == "r":
        x += 1
    elif direction == "l":
        x -= 1
    elif direction == "u":
        y += 1
    elif direction == "d":
        y -= 1
    else:
        print("Illegal direction order")
    new_position = (x, y)
    return new_position


def get_tile_at_position(level, position):
    """This function is used to return the character representing the tile at the
    given position in a level string.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.

    Returns:
        (str): The tile you want in the level.
    """
    this_size = level_size(level)
    num = position_to_index(position, this_size)
    list_level = list(level)
    return list_level[num]


def get_tile_in_direction(level, position, direction):
    """This function determine the new position which results from moving the given
    position in the given direction, and return the character representing the tile
    found at this new position.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.
        direction (str): According to the action you have input.

    Returns:
        (str): The tile you want after moving.
    """
    new_position = get_position_in_direction(position, direction)
    return get_tile_at_position(level, new_position)


def remove_from_level(level, position):
    """This function return a level string exactly the same as the one given, but
    with the given position replaced by an air tile.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.

    Returns:
        level (str): A new level string after replacement.
    """
    this_size = level_size(level)
    remove_num = position_to_index(position, this_size)
    list_level = list(level)
    list_level[remove_num] = ' '
    level = ''.join(list_level)
    return level


def move(level, position, direction):
    """This function return the updated position that results from moving the
    character from the given position in the given direction.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.
        direction (str): According to the action you have input.

    Returns:
        next_position (tuple<int, int>): The position after moving, and this will
        be in an air tile and falling onto symbol.
    """
    next_tile = get_tile_in_direction(level, position, direction)
    next_position = get_position_in_direction(position, direction)
    if next_tile == "#":
        up_tile = get_tile_in_direction(level, position, "u")
        if up_tile == "#":
            return position
        else:
            while next_tile != " ":
                next_tile = get_tile_in_direction(level, next_position, "u")
                next_position = get_position_in_direction(next_position, "u")
            if next_tile == " ":
                return next_position
    elif next_tile == " ":
        while next_tile == " ":
            next_tile = get_tile_in_direction(level, next_position, "d")
            next_position = get_position_in_direction(next_position, "d")
        next_position = get_position_in_direction(next_position, "u")
        return next_position
    elif next_tile == "$" or next_tile == "@" or next_tile == "I" or next_tile == "^":
        return next_position


def print_level(level, position):
    """This function print the level with the tile of the given replaced by the
    player tile.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.

    Returns:
        level (str): A new level string after replacement.


        This is another way to achieve the goal, but will fail in the test. I just
    mark these code down for extra learning.

    list_level = list(level)
    list_level[player] = '*'
    level = ''.join(list_level)
    """
    this_size = level_size(level)
    player = position_to_index(position, this_size)
    level = level[:player] + '*' + level[player + 1:]
    return print(level)


def attack(level, position):
    """This function will check whether there is a monster near you. If so, you
    can attack the monster and the monster will be removed from the level.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.

    Returns:
        level (str): A new level string after replacement.
    """
    left_position = get_position_in_direction(position, "l")
    left_til = get_tile_at_position(level, left_position)
    right_position = get_position_in_direction(position, "r")
    right_til = get_tile_at_position(level, right_position)
    if left_til == "@":
        print("Attacking the monster on your left!")
        return remove_from_level(level, left_position)
    elif right_til == "@":
        print("Attacking the monster on your right!")
        return remove_from_level(level, right_position)
    else:
        print("No monsters to attack!")
        return level


def tile_status(level, position):
    """This function checks the tile at the position and gives different output
    due to the different tile.

    Parameters:
        level (str): The level string.
        position (tuple<int, int>): The row, column position of a tile.

    Returns:
        record (tuple<str, str>): A tuple contains the tile and level according
        to the parameters.
    """
    status = get_tile_at_position(level, position)
    if status == "I":
        print("Congratulations! You finished the level")
    elif status == "@":
        print("Hit a monster!")
    elif status == "$" or status == "^":
        level = remove_from_level(level, position)
    record = (status, level)
    return record


def main():
    """This is the main function handles the main interaction with the user.

        When the game starts, it will ask user for a file to load.

        Once the user enters a legal name of the level file, it will load that level
    from the file and print the current score with a loaded level with the player at
    the starting point (position = (0, 1)).

        It will repeatedly ask the user to enter an order and reflect to those actions
    until game is over.
    """
    input_level = input("Please enter the name of the level file (e.g. level1.txt): ")
    level = load_level(input_level)
    score = 0
    print("Score: " + str(score))
    position = (0, 1)
    print_level(level, position)
    action = input("Please enter an action (enter '?' for help): ")
    save = 0
    while action != "q":
        if action == "?":
            print(HELP_TEXT)
        elif action == "r" or action == "l":
            level = remove_from_level(level, position)
            position = move(level, position, action)
            status, level = tile_status(level, position)
            if status == "I":
                break
            elif status == "$":
                score += 1
            elif status == "^":
                save_score = score
                save_level = level
                save_position = position
                save += 1
            elif status == "@":
                if save == 0:
                    break
                else:
                    score = save_score
                    level = save_level
                    position = save_position
        elif action == "n":
            score = save_score
            level = save_level
            position = save_position
        elif action == "a":
            level = attack(level, position)
        else:
            print("Wrong order!")
        print("Score: " + str(score))
        print_level(level, position)
        action = input("Please enter an action (enter '?' for help): ")
    # print("!!! GAME OVER !!!")


if __name__ == "__main__":
    main()