from math import ceil

class GameConfig:
    def __init__(self, grid_size=6):
        self._grid_size = grid_size
        
        self._grid_pixel_width = 9 * ceil(600 / 9)
        self._grid_pixel_height = self._grid_pixel_width
        self._side_panel_width = 300
        self._side_panel_height = self._grid_pixel_height
        self._screen_width = self._grid_pixel_width + self._side_panel_width
        self._screen_height = self._grid_pixel_height

    @property
    def grid_size(self):
        return self._grid_size
    
    @grid_size.setter
    def grid_size(self, value):
        self._grid_size = value

        self._grid_pixel_width = 9 * ceil(600 / 9)
        self._grid_pixel_height = self._grid_pixel_width
        self._side_panel_width = 300
        self._side_panel_height = self._grid_pixel_height
        self._screen_width = self._grid_pixel_width + self._grid_pixel_height
        self._screen_height = self._grid_pixel_height

config = GameConfig()
    