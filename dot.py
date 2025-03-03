"""
Author Paul Brace March 2025
PacMan game developed using arcade
Dot class used to display dots, energisers and fruit
"""

import arcade
from constants import *

class Dot(arcade.Sprite):

    # Dot type constants
    DOT = 0
    ENERGISER = 1
    FRUIT = 2

    # Dot images
    dot_image = arcade.load_texture('images/dot.png')
    energiser_image = arcade.load_texture('images/energiser.png')
    fruit_image = [
        arcade.load_texture('images/Cherry.png'),
        arcade.load_texture('images/Strawberry.png'),
        arcade.load_texture('images/Orange.png'),
        arcade.load_texture('images/Apple.png'),
        arcade.load_texture('images/Melon.png'),
        arcade.load_texture('images/Galaxian.png'),
        arcade.load_texture('images/Bell.png')
    ]

    # Score earned for each type of fruit when eaten
    fruit_score = [100, 300, 500, 700, 1000, 2000, 3000, 5000]

    def __init__(self, dtype, x, y, fruit_number=1):
        self.dtype = dtype
        x = x * 20 + 20
        y = WINDOW_HEIGHT - (y * 20 + 40)
        # Time fruit remains on screen
        self.timer = 0

        image = None
        self.done = False
        match dtype:
            case Dot.DOT:
                image = Dot.dot_image
                self.score = 20
            case Dot.ENERGISER:
                image = Dot.energiser_image
                self.score = 50
            case Dot.FRUIT:
                if fruit_number > 7:
                    fruit_number = 7
                image = Dot.fruit_image[fruit_number - 1]
                self.score = Dot.fruit_score[fruit_number - 1]
                # Time fruit remains on screen
                self.timer = DISPLAY_FRUIT
                # position between 2 bricks
                x = x - 10
        super().__init__(image, 1, x, y)

    def update(self, delta_time):
        if self.dtype == Dot.FRUIT:
            self.timer -= 1
            if self.timer <= 0:
                self.done = True
        if self.done:
            self.kill()
        super().update(delta_time)
