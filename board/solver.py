from board.board import Board
from tango_types import SIGN, SYMBOL
from game.game_config import config


class Solver:
    @staticmethod
    def _solve(board: Board, depth: int) -> bool:
        # grid is completely filled
        if depth >= (config.grid_size ** 2):
            return board.is_solved()

        current_posn = (depth // config.grid_size, depth % config.grid_size)

        if board.get_symbol_at_posn(current_posn) != SYMBOL.NONE:
            if not board.is_valid():
                return False
            
            return Solver._solve(board, depth + 1)

        # try putting sun in posn
        board.set_symbol_at_posn(current_posn, SYMBOL.SUN)

        if board.is_valid() and Solver._solve(board, depth + 1):
            return True
        
        
        # try setting moon
        board.set_symbol_at_posn(current_posn, SYMBOL.MOON)
        if board.is_valid() and Solver._solve(board, depth + 1):
            return True
        

        # reset board
        board.set_symbol_at_posn(current_posn, SYMBOL.NONE)

        return False

    @staticmethod
    def solve(board: Board) -> bool:
        return Solver._solve(board, 0)
    
    @staticmethod
    def _get_num_solutions(board: Board, depth: int) -> int:
        # grid is completely filled
        if depth >= (config.grid_size ** 2):
            return board.is_solved()

        current_posn = (depth // config.grid_size, depth % config.grid_size)

        if board.get_symbol_at_posn(current_posn) != SYMBOL.NONE:
            if not board.is_valid():
                return 0
            
            return Solver._get_num_solutions(board, depth + 1)

        num_solutions = 0

        # try putting sun in posn
        board.set_symbol_at_posn(current_posn, SYMBOL.SUN)

        if board.is_valid():
            num_solutions += Solver._get_num_solutions(board, depth + 1)
        
        # try setting moon
        board.set_symbol_at_posn(current_posn, SYMBOL.MOON)
        if board.is_valid():
            num_solutions += Solver._get_num_solutions(board, depth + 1)
        
        # reset board
        board.set_symbol_at_posn(current_posn, SYMBOL.NONE)

        return num_solutions
    
    @staticmethod
    def get_num_solutions(board: Board) -> int:
        return Solver._get_num_solutions(board, 0)
    
    @staticmethod
    def is_intuitively_solvable(board: Board) -> bool:
        """
        Checks whether a board is "intuitively" solvable. A symbol can be placed at an empty posn
        "intuitively" if placing the complement would make the board invalid (e.g. we have to 
        place a moon at (1, 2) because placing a sun would violate some rule).

        Checking whether a board is "intuitively" solvable is done with the following iterative 
        algorithm:
        1. If all tiles on a board are filled, the board is solvable if it is correctly solved
        2. If the board is invalid, it can never be solved intuitively since placing symbols on 
        an invalid board just makes another invalid board
        3. For each empty tile, check if placing either SUN/MOON results in an invalid board. If so,
        the complement can intuitively be placed
        4. If no tiles were placed, the board can't be intuitively solved
        5. Recursively check if the remainder of the board is intuitively solvable
        6. Remove any placed tiles before returning the result
        """
        if board.is_filled():
            return board.is_solved()
        elif not board.is_valid():
            return False
        
        placed_symbols = []
        for i in range(config.grid_size):
            for j in range(config.grid_size):
                if board.get_symbol_at_posn((i, j)) != SYMBOL.NONE:
                    continue

                board.set_symbol_at_posn((i, j), SYMBOL.SUN)
                if not board.is_valid():
                    # we know that the moon MUST be here
                    board.set_symbol_at_posn((i, j), SYMBOL.MOON)
                    placed_symbols.append((i, j))
                    continue

                board.set_symbol_at_posn((i, j), SYMBOL.MOON)
                if not board.is_valid():
                    # we know that the sun MUST be here
                    board.set_symbol_at_posn((i, j), SYMBOL.SUN)
                    placed_symbols.append((i, j))
                    continue

                board.set_symbol_at_posn((i, j), SYMBOL.NONE)

        if not placed_symbols:
            return False

        res = Solver.is_intuitively_solvable(board)

        # empty any symbols we've placed
        for posn in placed_symbols:
            board.set_symbol_at_posn(posn, SYMBOL.NONE)

        return res