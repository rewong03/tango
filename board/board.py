from collections import defaultdict

from game.game_config import config
from utils import (add_posns, direction_to_posn, is_posn_in_bounds,
                     posns_to_direction)
from tango_types import DIRECTION, SIGN, SYMBOL, Posn


class Board:
    def __init__(self):
        # 2d-array of symbols
        self._board: list[list[SYMBOL]] = [[SYMBOL.NONE.value for i in range(config.grid_size)] for j in range(config.grid_size)]

        # mapping of (posn) => {(sign, direction)}
        # mapping is directional, we only keep track of going right or down
        self._signs: dict[Posn, set[tuple[SIGN, DIRECTION]]] = defaultdict(set)

    def get_symbol_at_posn(self, posn: Posn) -> SYMBOL:
        i, j = posn

        if not is_posn_in_bounds(posn):
            raise ValueError(
                f"Tried to access board out of bounds (position {posn})"
            )

        return SYMBOL(self._board[i][j])

    def set_symbol_at_posn(self, posn: Posn, symbol: SYMBOL) -> None:
        i, j = posn

        if not is_posn_in_bounds(posn):
            raise ValueError(f"Tried to set board out of bounds (position {posn})")

        self._board[i][j] = symbol.value

    def get_all_signs(self) -> dict[Posn, set[tuple[SIGN, DIRECTION]]]:
        return self._signs

    def get_signs_at_posn(self, posn: Posn) -> set[tuple[SIGN, DIRECTION]]:
        return self._signs[posn]

    def set_sign(self, from_posn: Posn, to_posn: Posn, sign: SIGN) -> None:
        if not is_posn_in_bounds(from_posn) or not is_posn_in_bounds(to_posn):
            raise ValueError("Posn out of bounds")
        
        dir = posns_to_direction(from_posn, to_posn)
        if dir != DIRECTION.RIGHT and dir != DIRECTION.DOWN:
            raise ValueError(f"Sign is going in invalid direction {dir}")
        
        self._signs[from_posn].add((dir, sign))

    def remove_sign(self, from_posn: Posn, dir: DIRECTION) -> None:
        if not is_posn_in_bounds(from_posn):
            raise ValueError("Posn out of bounds")
        
        filtered = set()
        for d, sign in self._signs[from_posn]:
            if d != dir:
                filtered.add((d, sign))

        self._signs[from_posn] = filtered

    def is_filled(self) -> bool:
        for i in range(config.grid_size):
            for j in range(config.grid_size):
                if self._board[i][j] > SYMBOL.MOON.value:
                    return False
                
        return True

    def is_valid(self) -> bool:
        """
        Board is valid if all conditions apply:

        1. Each row has no more than (size / 2) of one symbol
        2. Each col has no more than (size / 2) of one symbol
        3. Tiles connected with a "=" have the same symbol
        4. Tiles connected with a "x" have different symbols
        5. No 3 consecutive tiles in a row/column have the same symbol
        """
        # check condition 1
        for i in range(config.grid_size):
            counter = [0 for _ in range(len(SYMBOL))]
            for j in range(config.grid_size):
                symbol = self._board[i][j]
                counter[symbol - 1] += 1

            if counter[SYMBOL.SUN.value - 1] > config.grid_size / 2 or counter[SYMBOL.MOON.value - 1] > config.grid_size / 2:
                return False
        
        # check condition 2
        for j in range(config.grid_size):
            counter = [0 for _ in range(len(SYMBOL))]
            for i in range(config.grid_size):
                symbol = self._board[i][j]
                counter[symbol - 1] += 1

            if counter[SYMBOL.SUN.value - 1] > config.grid_size / 2 or counter[SYMBOL.MOON.value - 1] > config.grid_size / 2:
                return False
            
        # check no 3 consecutive tiles in row
        for i in range(config.grid_size):
            for j in range(config.grid_size - 2):
                if self._board[i][j] <= SYMBOL.MOON.value and self._board[i][j] == self._board[i][j + 1] and self._board[i][j] == self._board[i][j + 2]:
                    return False
                
        # check no 3 consecutive tiles in column
        for j in range(config.grid_size):
            for i in range(config.grid_size - 2):
                if self._board[i][j] <= SYMBOL.MOON.value and self._board[i][j] == self._board[i + 1][j] and self._board[i][j] == self._board[i + 2][j]:
                    return False
            
        # check sign constraints
        for from_posn, sign_set in self._signs.items():
            for dir, sign in sign_set:
                dir_posn = direction_to_posn(dir)
                to_posn = add_posns(from_posn, dir_posn)

                from_symbol = self.get_symbol_at_posn(from_posn)
                to_symbol = self.get_symbol_at_posn(to_posn)

                if from_symbol.value > SYMBOL.MOON.value or to_symbol.value > SYMBOL.MOON.value:
                    continue

                match sign:
                    case SIGN.EQUAL:
                        # symbols must be equal
                        if from_symbol != to_symbol:

                            return False
                    case SIGN.TIMES:
                        # symbols must be opposite
                        if from_symbol == to_symbol:
                            return False
                        
        return True

    def is_solved(self) -> bool:
        """
        Board is solved if all conditions apply:

        1. Each row has the same number of suns/moons
        2. Each column has the same number of suns/moons
        3. Tiles connected with a "=" have the same symbol
        4. Tiles connected with a "x" have different symbols
        5. No 3 consecutive tiles in a row/column have the same symbol
        6. All board positions are filled
        """
        # SUN = 1 and MOON = 2 so sum of each row should be (3 * grid size) / 2
        if not all(sum(row) == 3 * config.grid_size / 2 for row in self._board):
            return False
        
        # same with column
        for j in range(config.grid_size):
            col_sum = sum(self._board[i][j] for i in range(config.grid_size))
            if col_sum != 3 * config.grid_size / 2:
                return False
            
        # check no 3 consecutive tiles in row
        for i in range(config.grid_size):
            for j in range(config.grid_size - 2):
                if self._board[i][j] == self._board[i][j + 1] and self._board[i][j] == self._board[i][j + 2]:
                    return False
                
        # check no 3 consecutive tiles in column
        for j in range(config.grid_size):
            for i in range(config.grid_size - 2):
                if self._board[i][j] == self._board[i + 1][j] and self._board[i][j] == self._board[i + 2][j]:
                    return False
            
        # check sign constraints
        for from_posn, sign_set in self._signs.items():
            for dir, sign in sign_set:
                dir_posn = direction_to_posn(dir)
                to_posn = add_posns(from_posn, dir_posn)

                match sign:
                    case SIGN.EQUAL:
                        # symbols must be equal
                        if self.get_symbol_at_posn(from_posn) != self.get_symbol_at_posn(to_posn):

                            return False
                    case SIGN.TIMES:
                        # symbols must be opposite
                        if self.get_symbol_at_posn(from_posn) == self.get_symbol_at_posn(to_posn):
                            return False
                        
        return True
    
    def clear_board(self):
        self._board = [[SYMBOL.NONE.value for i in range(config.grid_size)] for j in range(config.grid_size)]
    
    def __repr__(self):
        string = "board = Board()\n"
        for i in range(config.grid_size):
            for j in range(config.grid_size):
                string += (
                    f"board.set_symbol_at_posn(({i}, {j}), {SYMBOL(self._board[i][j])})\n"
                )

        for from_posn, sign_set in self._signs.items():
            for dir, sign in sign_set:
                dir_posn = direction_to_posn(dir)
                to_posn = add_posns(from_posn, dir_posn)
                string += (
                    f"board.set_symbol_at_posn({from_posn}, {to_posn}, {sign})\n"
                )

        return string
    
    def print_board(self) -> None:
        board_str = ""

        for i in range(config.grid_size):
            for j in range(config.grid_size):
                symbol = self.get_symbol_at_posn((i, j))

                symbol_str = None
                match symbol:
                    case SYMBOL.SUN:
                        symbol_str = "S"
                    case SYMBOL.MOON:
                        symbol_str = "M"
                    case SYMBOL.NONE:
                        symbol_str = "+"

                sign_str = None
                if (DIRECTION.RIGHT, SIGN.EQUAL) in self._signs[(i, j)]:
                    sign_str = "="
                elif (DIRECTION.RIGHT, SIGN.TIMES) in self._signs[(i, j)]:
                    sign_str = "x"
                else:
                    sign_str = " "

                board_str += symbol_str + sign_str

            board_str += "\n"

            for j in range(config.grid_size):
                sign_str = None
                if (DIRECTION.DOWN, SIGN.EQUAL) in self._signs[(i, j)]:
                    sign_str = "="
                elif (DIRECTION.DOWN, SIGN.TIMES) in self._signs[(i, j)]:
                    sign_str = "x"
                else:
                    sign_str = " "

                board_str += sign_str + " "

            board_str += "\n"

        print(board_str)

    def copy(self):
        board = Board()

        for i in range(config.grid_size):
            for j in range(config.grid_size):
                board.set_symbol_at_posn((i, j), SYMBOL(self._board[i][j]))

        for from_posn, sign_set in self._signs.items():
            for dir, sign in sign_set:
                dir_posn = direction_to_posn(dir)
                to_posn = add_posns(from_posn, dir_posn)

                board.set_sign(from_posn, to_posn, sign)

        return board

