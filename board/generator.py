import random
from board.board import Board
from board.solver import Solver
from game.game_config import config
from utils import add_posns, direction_to_posn, generate_random_posn, generate_random_symbol
from tango_types import SIGN, SYMBOL, DIRECTION, Posn


class Generator:
    @staticmethod
    def _generate_board_symbols(board: Board, depth: int) -> bool:
        if depth >= (config.grid_size ** 2):
            return board.is_solved()
        
        current_posn = (depth // config.grid_size, depth % config.grid_size)
        
        choices = [SYMBOL.SUN, SYMBOL.MOON]
        random.shuffle(choices)
        for symbol in choices:
            board.set_symbol_at_posn(current_posn, symbol)

            if board.is_valid() and Generator._generate_board_symbols(board, depth + 1):
                return True
            

        board.set_symbol_at_posn(current_posn, SYMBOL.NONE)
        return False

    @staticmethod
    def generate_board_symbols() -> Board:
        board = Board()
        while not Generator._generate_board_symbols(board, 0):
            print("FAILED TO GENERATE BOARD")
            board = Board()
        
        return board
    
    @staticmethod
    def populate_signs(board: Board):
        # populate going row-wise
        for i in range(config.grid_size):
            for j in range(config.grid_size - 1):
                from_posn = (i, j)
                to_posn = (i, j + 1)

                from_symbol = board.get_symbol_at_posn(from_posn)
                to_symbol = board.get_symbol_at_posn(to_posn)

                if from_symbol == to_symbol:
                    board.set_sign(from_posn, to_posn, SIGN.EQUAL)
                else:
                    board.set_sign(from_posn, to_posn, SIGN.TIMES)

        # populate going column-wise
        for j in range(config.grid_size):
            for i in range(config.grid_size - 1):
                from_posn = (i, j)
                to_posn = (i + 1, j)

                from_symbol = board.get_symbol_at_posn(from_posn)
                to_symbol = board.get_symbol_at_posn(to_posn)

                if from_symbol == to_symbol:
                    board.set_sign(from_posn, to_posn, SIGN.EQUAL)
                else:
                    board.set_sign(from_posn, to_posn, SIGN.TIMES) 
    
    @staticmethod
    def random_remove_symbols(board: Board, num_to_remove) -> None:
        filled_posns = []
        for i in range(config.grid_size):
            for j in range(config.grid_size):
                if board.get_symbol_at_posn((i, j)) != SYMBOL.NONE:
                    filled_posns.append((i, j))

        random.shuffle(filled_posns)

        for i in range(min(len(filled_posns), num_to_remove)):
            board.set_symbol_at_posn(filled_posns[i], SYMBOL.NONE)

    
    @staticmethod
    def reduce_signs(board: Board) -> None:
        num_signs = 2 * (config.grid_size - 1) * config.grid_size

        board_signs = board.get_all_signs()
        remaining_signs = []
        for from_posn, sign_set in board_signs.items():
            for dir, sign in sign_set:
                remaining_signs.append((from_posn, dir, sign))

        while num_signs >= 0:
            random.shuffle(remaining_signs)
            
            to_remove = None
            for from_posn, dir, sign in remaining_signs:
                board.remove_sign(from_posn, dir)

                num_solutions = Solver.get_num_solutions(board)
                if num_solutions == 1:
                    to_remove = (from_posn, dir, sign)
                    break

                # add sign back
                dir_posn = direction_to_posn(dir)
                to_posn = add_posns(from_posn, dir_posn)
                board.set_sign(from_posn, to_posn, sign)

            if to_remove:
                remaining_signs.remove((from_posn, dir, sign))
                num_signs -= 1
            else:
                return
            
    @staticmethod
    def populate_symbols(board: Board) -> None:
        if Solver.is_intuitively_solvable(board):
            return
        
        # solution = board.copy()
        if not Solver.solve(board):
            raise ValueError("Input board must be solvable")
        
        posns = [(i, j) for i in range(config.grid_size) for j in range(config.grid_size)]
        random.shuffle(posns)
        posns = set(posns)
        
        for _ in range(config.grid_size ** 2):
            removed_posn = None

            for posn in posns:
                symbol = board.get_symbol_at_posn(posn)
                if symbol == SYMBOL.NONE:
                    continue

                board.set_symbol_at_posn(posn, SYMBOL.NONE)
                if Solver.is_intuitively_solvable(board):
                    removed_posn = posn
                    break

                board.set_symbol_at_posn(posn, symbol)

            if removed_posn:
                posns.remove(removed_posn)
            else:
                return
        
        # empty_posns = []
        # for i in range(config.grid_size):
        #     for j in range(config.grid_size):
        #         if board.get_symbol_at_posn((i, j)) == SYMBOL.NONE:
        #             empty_posns.append((i, j))

        # random.shuffle(empty_posns)

        # for i in range(len(empty_posns)):
        #     board.set_symbol_at_posn(empty_posns[i], solution.get_symbol_at_posn(empty_posns[i]))
            
        #     if Solver.is_intuitively_solvable(board):
        #         return
            
        raise ValueError("Something went very wrong")

    @staticmethod
    def generate() -> Board:
        board = Generator.generate_board_symbols()
        Generator.populate_signs(board)

        board.clear_board()
        board.set_symbol_at_posn(generate_random_posn(), generate_random_symbol())

        Generator.reduce_signs(board)
        Generator.populate_symbols(board)   

        board.print_board()
        assert Solver.is_intuitively_solvable(board)

        return board