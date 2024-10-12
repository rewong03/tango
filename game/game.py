import time
import pygame
import pygame.freetype
from board.generator import Generator
from board.solver import Solver
from constants import LINE_THICKNESS
from game.button import BUTTON, Button
from game.game_config import config
from tango_types import DIRECTION, SIGN, SYMBOL
from utils import generate_random_posn, grid_to_screen, screen_to_grid


class Game:
    def __init__(self, debug=False):
        self._board = None
        self._board_copy = None
        self._solved_board = None
        self._is_board_solved = False

        # initialize game
        pygame.init()
        pygame.font.init()

        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode([config._screen_width, config._screen_height])
        self._start_time = time.time()
        self._elapsed_time = 0

        self._large_font = pygame.freetype.SysFont("Comic Sans MS", 60)
        self._small_font = pygame.freetype.SysFont("Comic Sans MS", 20)
        self._text_panel_color = (0, 0, 0)

        # set up buttons
        new_game_button = Button("New Game", (200, 50), self._small_font)
        new_game_button.set_position((config._grid_pixel_width + (config._side_panel_width // 2), 150))

        clear_board_button = Button("Clear Board", (200, 50), self._small_font)
        clear_board_button.set_position((config._grid_pixel_width + (config._side_panel_width // 2), 250))

        get_hint_button = Button("Get a Hint!", (200, 50), self._small_font)
        get_hint_button.set_position((config._grid_pixel_width + (config._side_panel_width // 2), 350))

        give_up_button = Button("Give Up :(", (200, 50), self._small_font)
        give_up_button.set_position((config._grid_pixel_width + (config._side_panel_width // 2), 450))

        debug_button = Button("Debug", (200, 50), self._small_font)
        debug_button.set_position((config._grid_pixel_width + (config._side_panel_width // 2), 550))

        self._buttons = {
            BUTTON.NEW_GAME: new_game_button,
            BUTTON.GET_HINT: get_hint_button,
            BUTTON.GIVE_UP: give_up_button,
            BUTTON.CLEAR_BOARD: clear_board_button
        }

        self._button_handlers = {
            BUTTON.NEW_GAME: self._reset_game,
            BUTTON.GET_HINT: self._get_hint,
            BUTTON.GIVE_UP: self._give_up,
            BUTTON.CLEAR_BOARD: self._clear_board
        }

        if debug:
            self._buttons[BUTTON.DEBUG] = debug_button
            self._button_handlers[BUTTON.DEBUG] = lambda x: print(self._board)

        self._should_exit = False
        self._is_loading = False

        self._new_game()

    def _new_game(self):
        self._board = Generator.generate()
        self._board_copy = self._board.copy()
        self._solved_board = self._board.copy()
        Solver.solve(self._solved_board)

        self._start_time = time.time()
        self._elapsed_time = 0
        self._is_board_solved = False
        self._text_panel_color = (0, 0, 0)

    def _give_up(self):
        if self._is_board_solved:
            return
        
        self._board = self._solved_board
        self._is_board_solved = True
        self._text_panel_color = (255, 0, 0)

    def _get_hint(self):
        if self._is_board_solved:
            return
        
        while True:
            posn = generate_random_posn()
            symbol = self._board.get_symbol_at_posn(posn)
            hint = self._solved_board.get_symbol_at_posn(posn)
            if symbol != hint:
                self._board.set_symbol_at_posn(posn, hint)
                self._is_board_solved = self._board.is_solved()
                break

    def _reset_game(self):
        self._is_loading = True
        self.on_draw()
        self._new_game()
        self._is_loading = False

    def _clear_board(self):
        self._board = self._board_copy
        self._board_copy = self._board.copy()

    def _draw_board_background(self):
        # draw vertical lines
        for i in range(config.grid_size + 1):
            r = pygame.Rect(0, 0, LINE_THICKNESS, config._grid_pixel_height)
            r.centerx = i * config._grid_pixel_width // config.grid_size

            pygame.draw.rect(
                self._screen, (200, 200, 200), r
            )

        # draw horizontal lines
        for i in range(config.grid_size + 1):
            r = pygame.Rect(0, 0, config._grid_pixel_width, LINE_THICKNESS)
            r.centery = i * config._grid_pixel_height // config.grid_size

            pygame.draw.rect(
                self._screen, (200, 200, 200), r
            )

    def _draw_board(self):
        for i in range(config.grid_size):
            for j in range(config.grid_size):
                symbol = self._board.get_symbol_at_posn((i, j))
                tile_center = grid_to_screen((i, j))

                # add colors
                r = pygame.Rect(
                    (0, 0),
                    (
                        config._grid_pixel_width // config.grid_size,
                        config._grid_pixel_height // config.grid_size,
                    ),
                )
                r.center = tile_center
                pygame.draw.rect(self._screen, (255, 255, 255), r)

                # draw symbols
                match symbol:
                    case SYMBOL.SUN:
                        img = pygame.image.load("assets/my_queen.png").convert_alpha()
                        img = pygame.transform.scale_by(img, 0.10)
                        img_rect = img.get_rect()
                        img_rect.center = tile_center
                        self._screen.blit(img, img_rect.topleft)
                    case SYMBOL.MOON:
                        img = pygame.image.load("assets/moon.png").convert_alpha()
                        img = pygame.transform.scale_by(img, 0.10)
                        img_rect = img.get_rect()
                        img_rect.center = tile_center
                        self._screen.blit(img, img_rect.topleft)
                    case SYMBOL.SUN_GUESS:
                        img = pygame.image.load("assets/my_queen.png").convert_alpha()
                        img.set_alpha(50)
                        img = pygame.transform.scale_by(img, 0.10)
                        img_rect = img.get_rect()
                        img_rect.center = tile_center
                        self._screen.blit(img, img_rect.topleft)

                        text_rect = self._large_font.get_rect("?")
                        text_rect.center = tile_center
                        self._large_font.render_to(self._screen, text_rect.topleft, "?", (0, 0, 0))
                    case SYMBOL.MOON_GUESS:
                        img = pygame.image.load("assets/moon.png").convert_alpha()
                        img.set_alpha(50)
                        img = pygame.transform.scale_by(img, 0.10)
                        img_rect = img.get_rect()
                        img_rect.center = tile_center
                        self._screen.blit(img, img_rect.topleft)

                        text_rect = self._large_font.get_rect("?")
                        text_rect.center = tile_center
                        self._large_font.render_to(self._screen, text_rect.topleft, "?", (0, 0, 0))

    def _draw_signs(self):
        # draw signs
        for from_posn, sign_set in self._board.get_all_signs().items():
            tile_center = grid_to_screen(from_posn)

            # dummy rectangle to get the correct positioning
            r = pygame.Rect(
                    (0, 0),
                    (
                        config._grid_pixel_width // config.grid_size,
                        config._grid_pixel_height // config.grid_size,
                    ),
                )
            r.center = tile_center

            for direction, sign in sign_set:
                sign_str = None
                match sign:
                    case SIGN.EQUAL:
                        sign_str = "="
                    case SIGN.TIMES:
                        sign_str = "x"

                sign_center = None
                horiz_scale = 1
                vert_scale = 1
                match direction:
                    case DIRECTION.UP:
                        sign_center = r.midtop
                        horiz_scale = 2
                    case DIRECTION.DOWN:
                        sign_center = r.midbottom
                        horiz_scale = 2
                    case DIRECTION.LEFT:
                        sign_center = r.midleft
                        vert_scale = 2
                    case DIRECTION.RIGHT:
                        sign_center = r.midright
                        vert_scale = 2

                assert sign_str is not None and sign_center is not None

                text_rect_background = self._large_font.get_rect(sign_str)
                text_rect_background.w *= horiz_scale
                text_rect_background.h *= vert_scale
                text_rect_background.center = sign_center
                pygame.draw.rect(self._screen, (255, 255, 255), text_rect_background)

                text_rect = self._large_font.get_rect(sign_str)
                text_rect.center = sign_center
                self._large_font.render_to(self._screen, text_rect.topleft, sign_str, (0, 0, 0))

    def _draw_text_panel(self, text_str: str):
        text_rect = self._large_font.get_rect(text_str)
        text_rect.center = (config._grid_pixel_width + (config._side_panel_width // 2), text_rect.height)
        self._large_font.render_to(self._screen, text_rect.topleft, text_str, self._text_panel_color)

    def _calculate_time_str(self):
        elapsed_minutes = self._elapsed_time // 60
        elapsed_seconds = self._elapsed_time % 60

        if elapsed_minutes < 10:
            elapsed_minutes = f"0{elapsed_minutes}"
        else:
            elapsed_minutes = str(elapsed_minutes)

        if elapsed_seconds < 10:
            elapsed_seconds = f"0{elapsed_seconds}"
        else:
            elapsed_seconds = str(elapsed_seconds)

        return f"{elapsed_minutes}:{elapsed_seconds}"

    def on_draw(self):
        self._screen.fill((255, 255, 255))
        self._draw_board()
        self._draw_board_background()
        self._draw_signs()

        text_panel_str = None
        if self._is_loading:
            text_panel_str = "Loading..."
        else:
            text_panel_str = self._calculate_time_str()
        
        self._draw_text_panel(text_panel_str)

        for button in self._buttons.values():
            button.draw(self._screen)

        pygame.display.flip()

    def _on_grid_click(self, screen_posn, mouse_button):
        if self._is_board_solved:
            return

        i, j = screen_posn

        if i >= 0 and i < config._grid_pixel_width and j >= 0 and j < config._grid_pixel_height:
            tile_i, tile_j = screen_to_grid(screen_posn)
            symbol = self._board.get_symbol_at_posn((tile_i, tile_j))

            match (mouse_button, symbol):
                case (3, SYMBOL.SUN):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN_GUESS)
                case (3, SYMBOL.MOON):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN_GUESS)
                case (3, SYMBOL.NONE):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN_GUESS)
                case (3, SYMBOL.SUN_GUESS):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.MOON_GUESS)
                case (3, SYMBOL.MOON_GUESS):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.NONE)
                case (1, SYMBOL.NONE):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN)
                case (1, SYMBOL.SUN):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.MOON)
                case (1, SYMBOL.MOON):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.NONE)
                case (1, SYMBOL.SUN_GUESS):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN)
                case (1, SYMBOL.MOON_GUESS):
                    self._board.set_symbol_at_posn((tile_i, tile_j), SYMBOL.SUN)
                case _:
                    raise ValueError(f"Invalid mouse click")
                
            self._is_board_solved = self._board.is_solved()
            if self._is_board_solved:
                self._text_panel_color = (0, 255, 0)

    def on_click(self, posn, mouse_button):
        for button_type, button in self._buttons.items():
            if button.is_in_bounds(posn):
                self._button_handlers[button_type]()
                return
            
        self._on_grid_click(posn, mouse_button)
            
    def on_event(self, event):
        match event.type:
            case pygame.QUIT:
                self._should_exit = True
            case pygame.MOUSEBUTTONUP:
                self.on_click(pygame.mouse.get_pos(), event.button)

    def on_tick(self):
        for event in pygame.event.get():
            self.on_event(event)

        if not self._is_board_solved:
            self._elapsed_time = int(time.time() - self._start_time)

        self.on_draw()
        self._clock.tick(60)

    def run(self):
        while not self._should_exit:
            self.on_tick()

        pygame.quit()
