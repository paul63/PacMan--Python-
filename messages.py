"""
Author Paul Brace March 2025
PacMan game developed using arcade
Disappearing messages
"""

import arcade
from constants import *

class Message():
    """ A disappearing message class
        will remain on screen for time and then fly up to top of screen """
    def __init__(self, text, pos, color, size, time, center):
        if center:
            self.message = arcade.Text(text, pos[0], pos[1],
                                       color, size, WINDOW_WIDTH, align="center")
        else:
            self.message = arcade.Text(text, pos[0], pos[1],
                                       color, size, WINDOW_WIDTH)
        self.time = time
        self.done = False
        self.remove = False

    def draw(self):
        self.time -= 1
        if self.time < 1:
            self.remove = True
        if self.remove:
            self.message.y += 10
        if self.message.y > WINDOW_HEIGHT:
            self.done = True
        self.message.draw()
