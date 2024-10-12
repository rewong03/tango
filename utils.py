import random
from game.game_config import config
from tango_types import DIRECTION, SYMBOL, Posn

def is_posn_in_bounds(posn) -> bool:
    i, j = posn
    return not (i < 0 or i > config.grid_size or j < 0 or j > config.grid_size)

def add_posns(posn_1: Posn, posn_2: Posn) -> Posn:
    i_1, j_1 = posn_1
    i_2, j_2 = posn_2

    return (i_1 + i_2, j_1 + j_2)

def subtract_posns(posn_1: Posn, posn_2: Posn) -> Posn:
    i_1, j_1 = posn_1
    i_2, j_2 = posn_2

    return (i_1 - i_2, j_1 - j_2)

def direction_to_posn(dir: DIRECTION) -> Posn:
    match dir:
        case DIRECTION.UP:
            return (-1, 0)
        case DIRECTION.DOWN:
            return (1, 0)
        case DIRECTION.LEFT:
            return (0, -1)
        case DIRECTION.RIGHT:
            return (0, 1)
        
    raise ValueError(f"Invalid direction {dir}")   

def posns_to_direction(from_posn: Posn, to_posn: Posn) -> DIRECTION:
    diff_posn = subtract_posns(to_posn, from_posn)

    match diff_posn:
        case (-1, 0):
            return DIRECTION.UP
        case (1, 0):
            return DIRECTION.DOWN
        case (0, -1):
            return DIRECTION.LEFT
        case (0, 1):
            return DIRECTION.RIGHT
        
    raise ValueError(f"Expected posns to have a difference of magnitude 1, got {diff_posn} instead")

def grid_to_screen(grid_posn):
    i, j = grid_posn

    tile_screen_width = config._grid_pixel_width / config.grid_size
    tile_screen_height = config._grid_pixel_height / config.grid_size

    return (
        round(j * tile_screen_height + (tile_screen_height / 2)),
        round(i * tile_screen_width + (tile_screen_width / 2)),
    )


def screen_to_grid(screen_posn):
    i, j = screen_posn

    tile_screen_width = config._grid_pixel_width // config.grid_size
    tile_screen_height = config._grid_pixel_height // config.grid_size

    return j // tile_screen_height, i // (tile_screen_width)

def generate_random_posn() -> Posn:
    return (
        random.randint(0, config.grid_size - 1),
        random.randint(0, config.grid_size - 1)
    )

def generate_random_symbol() -> SYMBOL:
    return random.choice([SYMBOL.SUN, SYMBOL.MOON])