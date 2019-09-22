"""
CSSE1001 2019s2a1 Support Code
"""

# Level constants
MONSTER = "@"
COIN = "$"
PLAYER = "*"
WALL = "#"
CHECKPOINT = "^"
GOAL = "I"
AIR = " "

# Movement constants
RIGHT = 'r'
LEFT = 'l'
UP = 'u'
DOWN = 'd'

DIRECTIONS = {
    'r': (1, 0),
    'l': (-1, 0),
    'u': (0, 1),
    'd': (0, -1)
}

HELP_TEXT = """? - Help.
r - Move right.
l - Move left.
a - Attack a monster immediately left or right of the player
n - Reset to the last checkpoint.
q - Quit."""


def load_level(filename):
    """Load a level file into a string and returns that string.

    Pads the string so that each line has the same amount of characters.

    Parameters:
        filename (str): The name of the level file to load.
    """
    with open(filename, 'r') as file:
        file_contents = file.readlines()

    # get the length of the longest line
    max_width = len(max(file_contents))

    level = []
    for line in file_contents:
        # find how many characters are missing from the current line
        fill = max_width - len(line)
        # pad the current line
        level.append(line.rstrip() + (" " * fill))

    return "\n".join(level)


def position_to_index(position, size):
    """Convert the row, column coordinate in a level to the level strings index.

    Parameters:
        position (tuple<int, int>): The row, column position of a tile.
        size (tuple<int, int>): The rows, columns dimensions of the level.
                                (see level_size)

    Returns:
        (int): The index of the tile in the level string.
    """
    row, column = position
    return row + (size[1] + 1) * (size[0] - column - 1)


def level_size(level):
    """Calculate the rows, columns dimensions of a level from the level string.

    Parameters:
        level (str): The level string.

    Returns:
        (tuple<int, int>): rows, columns dimensions of the given level.
    """
    return level.count('\n') + 1, level.find('\n')
