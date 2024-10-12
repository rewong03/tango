from enum import Enum

Posn = tuple[int, int]

class SYMBOL(Enum):
    SUN = 1
    MOON = 2
    SUN_GUESS = 3
    MOON_GUESS = 4
    NONE = 5


class SIGN(Enum):
    EQUAL = 0
    TIMES = 1

class DIRECTION(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3