"""
Author Paul Brace March 2025
PacMan game developed using the arcade library
Music Monkeys Spinning Monkeys by Kevin MacLeod
"""

import arcade
import pyglet
from pyglet.graphics import Batch
from constants import *
# import both as * and by name so can use . notation in match case
import constants
from maze_grids import maze_layouts
from brick import Brick
from dot import *
from ghost import *
from messages import Message
from pac_man import *


# Constants
WINDOW_TITLE = "PacMan"

music = arcade.load_sound("sounds/MazeTune.mp3")
extra_life = arcade.load_sound("sounds/extraLife.wav")
game_over = arcade.load_sound('sounds/GameOver.wav')
level_over = arcade.load_sound('sounds/LevelCompleted.wav')
energiser_eaten = arcade.load_sound('sounds/eatEnergiser.wav')
fruit_eaten = arcade.load_sound('sounds/eatfruit.wav')

class GameView(arcade.Window):
    """
    Main Game Class.
    """

    def __init__(self):

        # Call the parent class to set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Set the background colour
        self.background_color = arcade.csscolor.BLACK

        # Get display width and set screen center
        # set up the screen
        viewport = pyglet.display.get_display().get_default_screen()
        left = viewport.width // 2 - WINDOW_WIDTH // 2
        top = viewport.height // 2 - WINDOW_HEIGHT // 2
        self.set_location(left, top)

        # Create text Batches used to hold and draw text sprites
        self.score_batch = Batch()
        self.instructions = Batch()
        self.game_over = Batch()
        # For temporary messages
        self.messages = []

        # Text sprites
        self.your_score_text = None
        self.high_score_text = None
        self.current_level_text = None
        self.inst = []
        self.game_over_text = []

        # Create sprite lists
        self.scene = arcade.Scene()
        # List of lives left images
        self.scene.add_sprite_list("Lives")
        self.scene.add_sprite_list("Grid", True)
        self.scene.add_sprite_list("Dots")
        self.scene.add_sprite_list("Fruit")
        self.scene.add_sprite_list("Ghosts")
        self.scene.add_sprite_list("Pacman")
        self.fruit_position = (0, 0)
        self.pacman = None
        self.fright_length = 0
        self.level = 0
        self.score = 0
        self.high_score = 0
        self.dots_eaten = 0
        self.lives = 0
        self.new_life_timer = 0    # Time for which new life message appears
        self.chase_timer = 0
        self.scatter_timer = 0
        self.scatter_timer = 0
        self.scatter_count = 0
        self.fright_length = 0
        self.new_life_target = 0
        self.ghosts_eaten = 0
        self.level_cleared = False
        self.end_of_level_timer = 0
        self.current_ghost_mode = 0
        self.mode_timer = 0
        self.fright_counter = 0
        self.game_state = PAUSED
        # Initialise game
        self.load_high_score()
        self.set_up_score_line()
        self.initialise_new_game()
        self.music_playing = None
        self.set_instructions()

    def set_instructions(self):
        """ Create text sprites and add to the Batch"""
        instructions = [
            "Press left, right, up and down arrows to move",
            "Avoid being caught by the ghosts",
            "Ghosts switch between chase and scatter mode",
            "Eat the dots and bonus fruit to score points",
            "Eating an energiser puts ghosts into fright mode",
            "Catch ghosts in fright mode to score points",
            "Clear all dots to move to next level",
            "Scores:",
            "    Small dot = 20 points   Energiser = 50 points",
            "    Ghost from 200 to 1,600 points",
            "    Fruit from 100 to 5,000 points"]

        y = 620
        self.inst.append(arcade.Text("Pac-Man - Instructions",0, y,
            YELLOW, HEADING_FONT_SIZE, bold=True, batch=self.instructions,
            width=WINDOW_WIDTH, align="center"))

        y -= 50
        for line in instructions:
            self.inst.append(arcade.Text(line,40, y, WHITE,
                INST_FONT_SIZE, batch=self.instructions, width=600))
            y -= 40

        self.inst.append(arcade.Text("Press I for more information",
            0, y - 25, AQUA, INST_FONT_SIZE, batch=self.instructions,
            width=WINDOW_WIDTH, align="center"))
        self.inst.append(arcade.Text("Press SPACE to start game without music, M with music",
            0, y - 65, AQUA, INST_FONT_SIZE, batch=self.instructions,
            width=WINDOW_WIDTH, align="center"))

    def set_information(self):
        """ Create text sprites and add to the Batch"""
        instructions = [
            "Further information:",
            "The ghosts alternate between chase mode and scatter mode.",
            "In scatter mode they head for their designated corner",
            "  this happens 3 times a level.",
            "Chase mode initially lasts 20 seconds and scatter 10 seconds.",
            "Chase mode time increases and scatter reduces each level.",
            "In chase mode:",
            "    Blinky (red) will head directly for you.",
            "    Pinky (pink) tries to get ahead of you.",
            "    Inky (blue) tries to get behind you.",
            "    Clyde (orange) just wanders about randomly.",
            "Ghost fright mode initially lasts 10 seconds but reduces each level.",
            "Ghosts start flashing 2 seconds before the end of fright mode.",
            "3 bonus fruits appear for 7 seconds on each level and get more",
            "  valuable in higher levels.",
            "You get an extra life every 10,000 points - max 5 at any time."]

        self.inst.clear()
        y = 620
        self.inst.append(arcade.Text("Pac-Man - Instructions",0, y,
            YELLOW, HEADING_FONT_SIZE, bold=True, batch=self.instructions,
            width=WINDOW_WIDTH, align="center"))

        y -= 50
        for line in instructions:
            self.inst.append(arcade.Text(line,10, y, WHITE,
                INFO_FONT_SIZE, batch=self.instructions, width=600))
            y -= 30

        self.inst.append(arcade.Text("Press SPACE to start game without music, M with music",
            0, y - 40, AQUA, INST_FONT_SIZE, batch=self.instructions,
            width=WINDOW_WIDTH, align="center"))

    def set_for_level(self):
        # reset game - called at launch and at the end of each level
        # Clear existing elements
        # Reset number of scatters invoked for new level
        self.scatter_count = 0
        #  reset in case grid cleared while in fright mode
        self.ghosts_eaten = 0
        # reset dots_eaten counter for new level
        self.dots_eaten = 0
        self.level_cleared = False
        self.create_maze()
        # Stop player movement
        self.pacman.next_direction = HOLD
        self.current_ghost_mode = Ghost.CHASE
        self.mode_timer = CHASE_TIMER
        self.fright_counter = 0
        # set pacman and ghost speed for level slow down for first 5 levels
        if self.level < 6:
            speed_percent = 100 - (6 - self.level) * 5
            self.pacman.set_speed_percent(speed_percent)
            for ghost in self.scene["Ghosts"]:
                ghost.set_speed_percent(speed_percent)
        self.current_level_text.text = f"Level: {self.level}"
        self.set_fruit_line()

    def set_up_score_line(self):
        # Called to initialise the 3 score text items
        self.your_score_text = arcade.Text("Your score: 0",20, WINDOW_HEIGHT - 20,
            WHITE, SCORE_FONT_SIZE, batch=self.score_batch)
        self.high_score_text = arcade.Text(f"High score: {self.high_score}",200,
            WINDOW_HEIGHT - 20, WHITE, SCORE_FONT_SIZE,
            batch=self.score_batch)
        self.current_level_text = arcade.Text("Level: 1",400, WINDOW_HEIGHT - 20,
            WHITE, SCORE_FONT_SIZE, batch=self.score_batch)

    def set_game_over(self):
        """ Create text sprites and add to the Batch"""
        self.game_over = Batch()
        y = 500
        self.game_over_text.append(arcade.Text("GAME OVER", 0, y, YELLOW,
                                               HEADING_FONT_SIZE, align="center", bold=True, batch=self.game_over,
                                               width=WINDOW_WIDTH))

        y -= 75
        self.game_over_text.append(arcade.Text(f"Your score: {self.score}", 0, y,
                                               WHITE, HEADING_FONT_SIZE, align="center",
                                               batch=self.game_over, width=WINDOW_WIDTH))
        y -= 75
        self.game_over_text.append(arcade.Text(f"You reached level: {self.level}", 0, y,
                                               WHITE, HEADING_FONT_SIZE, align="center",
                                               batch=self.game_over, width=WINDOW_WIDTH))
        y -= 75
        if self.score > self.high_score:
            self.game_over_text.append(arcade.Text("Congratulations a new high score!", 0, y,
                                                   GREEN, HEADING_FONT_SIZE, align="center",
                                                   batch=self.game_over, width=WINDOW_WIDTH))
            self.high_score = self.score
            # Save high score
            with open("scores.txt", "w") as file:
                file.write(str(self.score))
        y -= 75
        self.inst.append(arcade.Text(
            "Press SPACE to start game without music, M with music",0, y,
            AQUA, INST_FONT_SIZE, align="center",
            batch=self.game_over, width=WINDOW_WIDTH))

    def load_high_score(self):
        try:
            with open("scores.txt", "r") as file:
                self.high_score = int(file.read())
        except:
            self.high_score = 0

    def initialise_new_game(self):
        # Set defaults for new game
        self.score = 0
        self.level = 1
        self.lives = START_LIVES
        self.set_for_level()
        # reset timers
        self.chase_timer = CHASE_TIMER
        self.scatter_timer = SCATTER_TIMER
        self.fright_length = FRIGHT_TIMER
        self.new_life_target = NEW_LIFE_INTERVAL
        self.set_lives_line()
        self.set_fruit_line()

    def set_lives_line(self):
        self.scene["Lives"].clear()
        # Create icons for lives left
        for i in range(self.lives):
            life = arcade.Sprite("images/pacOpen.png")
            life.center_x = 44 + i * 25
            life.center_y = 20
            self.scene.add_sprite("Lives", life)

    def set_fruit_line(self):
        self.scene["Fruit"].clear()
        # Create icons for fruit line based on level
        for i in range(0, self.level):
            fruit = arcade.Sprite(Dot.fruit_image[i])
            fruit.center_x = WINDOW_WIDTH - i * 25 - 40
            fruit.center_y = 20
            self.scene.add_sprite("Fruit", fruit)

    def add_new_life(self):
        # Adds a new life, called every NEW_LIFE_INTERVAL
        if self.lives < 5:
            self.lives += 1
            self.messages.append(Message("New life", (0, 15), RED,
                                         INST_FONT_SIZE, 100, True))
            self.set_lives_line()
            extra_life.play(volume=0.15)

    def create_maze(self):
        # Clear current board sprites
        self.scene["Grid"].clear()
        self.scene["Dots"].clear()
        self.scene["Ghosts"].clear()
        # Generate the maze elements for the current level and set up for the new maze
        level = (self.level - 1) % len(maze_layouts)
        maze = maze_layouts[level]
        for y, row in enumerate(maze):
            for x, char in enumerate(row):
                match char:
                    case "X":
                        self.scene.add_sprite("Grid", Brick(level, x, y))
                    case "O":
                        self.scene.add_sprite("Grid", Brick(Brick.OPENING, x, y))
                    case "Y":
                        if self.pacman is not None:
                            self.pacman.kill()
                        self.pacman = PacMan(x, y)
                        self.scene.add_sprite("Pacman", self.pacman)
                    case ".":
                        self.scene.add_sprite("Dots", Dot(Dot.DOT, x, y))
                    case "E":
                        self.scene.add_sprite("Dots", Dot(Dot.ENERGISER, x, y))
                    case "F":
                        self.fruit_position = (x, y)
                    case "B":
                        self.scene.add_sprite("Ghosts", Ghost(Ghost.BLINKY, x, y))
                    case "I":
                        self.scene.add_sprite("Ghosts", Ghost(Ghost.INKY, x, y))
                    case "P":
                        self.scene.add_sprite("Ghosts", Ghost(Ghost.PINKY, x, y))
                    case "C":
                        self.scene.add_sprite("Ghosts", Ghost(Ghost.CLYDE, x, y))

    def update_score(self, points):
        self.score += points
        self.your_score_text.text = "Your score: " + str(self.score)
        if self.score >= self.new_life_target:
            self.new_life_target += NEW_LIFE_INTERVAL
            self.add_new_life()

    def snap_to_grid(self, pos, speed):
        # Check the position ( x or y) of the object and if near a grid (20x20) edge
        # reposition grid center - called if object is trying to change direction
        # this is so that object can change direction if required
        ipos = round(pos)
        dist = pos - ipos // 20 * 20
        # check if near forward grid edge
        if dist >= 20 - speed / 1.5:
            # Move to next grid position
            ipos = ipos + 20 - ipos % 20
            return ipos
        elif dist <= speed / 1.5:
            # Move back to last grid position
            ipos = ipos - ipos % 20
            return ipos
        else:
            return pos

    def try_to_move(self, direction, game_object):
        # Try to move in the direction given
        # return Ture if object can move
        x_vel = 0
        y_vel = 0
        if direction != game_object.current_direction:
            # snap to grid so if trying to change direction
            game_object.center_x = self.snap_to_grid(game_object.center_x, game_object.speed)
            game_object.center_y = self.snap_to_grid(game_object.center_y, game_object.speed)
        if direction == RIGHT:
            x_vel = game_object.speed
        elif direction == LEFT:
            x_vel = -game_object.speed
        elif direction == UP:
            y_vel = game_object.speed
        elif direction == DOWN:
            y_vel = -game_object.speed

        game_object.center_x += x_vel
        game_object.center_y += y_vel

        # Check if we can move in direction or if we have hit a wall. If we have hit a brick
        # position next to the brick
        hit_list = arcade.check_for_collision_with_list(
            game_object, self.scene["Grid"])
        if len(hit_list) > 0:
            brick = hit_list[0]
            match direction:
                case constants.LEFT:
                    # move to right edge
                    game_object.center_x = brick.center_x + 20
                case constants.RIGHT:
                    # move to left edge
                    game_object.center_x = brick.center_x - 20
                case constants.UP:
                    # move to bottom edge
                    game_object.center_y = brick.center_y - 20
                case constants.DOWN:
                    # move to top edge
                    game_object.center_y = brick.center_y + 20
            return False
        # We can move so record change of direction if required
        if game_object.current_direction != direction:
            game_object.current_direction = direction
            game_object.change_direction = True
        return True

    def move_pacman(self, next_direction):
        # try and move the packman in the direction provided
        if not self.try_to_move(next_direction, self.pacman):
            self.try_to_move(self.pacman.current_direction, self.pacman)
        # Check if exiting screen left or right
        if self.pacman.center_x < 2:
            self.pacman.center_x = WINDOW_WIDTH - 22
        elif self.pacman.center_x > WINDOW_WIDTH - 22:
            self.pacman.center_x = 2

    def move_ghost(self, ghost, direction):
        # try and move the ghost in the direction provided
        # return True if ghost can move
        if not self.try_to_move(direction, ghost):
            return False
        ghost.set_direction_image(direction)
        if ghost.center_x < 2:
            ghost.center_x = WINDOW_WIDTH - 22
        elif ghost.center_x > WINDOW_WIDTH - 22:
            ghost.center_x = 2
        return True

    def ghost_fright_over(self):
        # fright mode over - return to ghosts default state
        self.ghosts_eaten = 0
        for ghost in self.scene["Ghosts"]:
            ghost.set_default_mode(False)
        self.mode_timer = self.chase_timer

    def change_ghost_mode(self):
        # called when timer expired to change ghost mode
        if self.scatter_count < 3 and self.current_ghost_mode == Ghost.CHASE:
            # Put ghosts in scatter mode
            self.scatter_count += 1
            self.current_ghost_mode = Ghost.SCATTER
            self.mode_timer = self.scatter_timer
            for ghost in self.scene["Ghosts"]:
                ghost.set_scatter_mode()
        else:
            # Put ghosts in chase mode
            self.current_ghost_mode = Ghost.CHASE
            self.mode_timer = self.chase_timer
            for ghost in self.scene["Ghosts"]:
                ghost.set_default_mode(False)

    def on_key_press(self, key: int, modifiers: int):
        """ User pressed a key """
        match key:
            case arcade.key.LEFT | arcade.key.A:
                self.pacman.next_direction = LEFT
            case arcade.key.RIGHT | arcade.key.D:
                self.pacman.next_direction = RIGHT
            case arcade.key.UP | arcade.key.W:
                self.pacman.next_direction = UP
            case arcade.key.DOWN | arcade.key.X:
                self.pacman.next_direction = DOWN
            case arcade.key.SPACE:
                if self.game_state != IN_PLAY:
                    self.initialise_new_game()
                    self.game_state = IN_PLAY
            case arcade.key.M:
                if self.game_state != IN_PLAY:
                    self.initialise_new_game()
                    self.game_state = IN_PLAY
                    self.music_playing = music.play(volume=0.33, loop=True)
            case arcade.key.I:
                if self.game_state == PAUSED:
                    self.set_information()

    def check_if_eaten_dot(self):
        # check if packman has eaten a dot
        hit_list = arcade.check_for_collision_with_list(
            self.pacman, self.scene["Dots"])
        if len(hit_list) > 0:
            dot = hit_list[0]
            self.update_score(dot.score)
            dot.done = True
            self.dots_eaten += 1
            for ghost in self.scene["Ghosts"]:
                # reduce dot delay to release for penned ghosts
                ghost.reduce_delay()
            # Check if just eaten an energiser
            if dot.dtype == Dot.ENERGISER:
                # put ghosts in fright mode
                energiser_eaten.play(volume=0.15)
                for ghost in self.scene["Ghosts"]:
                    ghost.set_frightened_mode()
                Ghost.fright_timer = self.fright_length
            elif dot.dtype == Dot.FRUIT:
                fruit_eaten.play(volume=0.15)
                self.messages.append(Message(f"{dot.score}",
                                             (dot.center_x - 10, dot.center_y - 5),
                                             WHITE,
                                             SCORE_FONT_SIZE, 100, False))
            # check if fruit to be displayed
            if self.dots_eaten == 70 or self.dots_eaten == 170:
                self.scene.add_sprite("Dots",
                                      Dot(Dot.FRUIT, self.fruit_position[0],
                                      self.fruit_position[1], self.level))

    def check_if_ghost_collide(self):
        # Check if player and a ghost have collided
        # If ghost is in fright mode then we have caught it
        # increase score, display catch score and set to return to pen
        # else player has been caught
        hit_list = arcade.check_for_collision_with_list(
            self.pacman, self.scene["Ghosts"])
        if len(hit_list) > 0:
            ghost = hit_list[0]
            if ghost.mode == Ghost.FRIGHTENED:
                if self.ghosts_eaten < 4:
                    self.ghosts_eaten += 1
                self.update_score(ghost_score[self.ghosts_eaten - 1])
                self.messages.append(Message(f"{ghost_score[self.ghosts_eaten - 1]}",
                                             (ghost.center_x - 10, ghost.center_y - 5), WHITE,
                                             SCORE_FONT_SIZE, 100, False))
                ghost.return_to_pen()
            elif ghost.mode != Ghost.CAUGHT:
                # pacman caught
                self.pacman.set_caught()
                self.lives -= 1
                self.set_lives_line()

    def on_update(self, delta_time):
        """Called roughly once every frame update
            check all game logic and create all game animation here"""
        if self.game_state == IN_PLAY:
        # Check for pacman caught
            if self.pacman.done:
                if self.lives < 1:
                    self.set_game_over()
                    self.game_state = GAME_OVER
                    if self.music_playing is not None:
                        arcade.stop_sound(self.music_playing)
                    game_over.play(volume=0.05)
                else:
                    self.pacman.return_to_start()
                    self.pacman.next_direction = HOLD
                    for ghost in self.scene["Ghosts"]:
                        ghost.jump_to_start()
                    self.ghost_fright_over()
                    return

            if not self.level_cleared:
                # Try to move pacman in the next direction selected by player
                # if pacman cannot move then carry on in same direction
                if self.pacman.next_direction != HOLD and not self.pacman.caught():
                    self.move_pacman(self.pacman.next_direction)

            self.check_if_eaten_dot()

            if not self.pacman.caught():
                # clear_done_objects()
                if len(self.scene["Dots"]) == 0:
                    # End of level
                    if not self.level_cleared:
                        # set a delay timer
                        self.level_cleared = True
                        self.end_of_level_timer = END_OF_LEVEL_DELAY
                        level_over.play(volume=0.15)

                    self.end_of_level_timer -= 1
                    if self.end_of_level_timer <= 0:
                        # pause at end of level complete so set for next level
                        self.level += 1
                        self.set_for_level()
                        # increase chase length by 2 seconds
                        self.chase_timer += FRAME_REFRESH * 2
                        # reduce scatter and frightened length
                        if self.scatter_timer > FRIGHT_TIMER * 5:
                            self.scatter_timer -= FRAME_REFRESH / 2
                        if self.fright_length > FRAME_REFRESH * 5:
                            self.fright_length -= FRAME_REFRESH / 2
                    else:
                        return

                self.check_if_ghost_collide()

                # Check if in fright mode and if timer expired
                if Ghost.fright_timer > 0:
                    Ghost.fright_timer -= 1
                    if Ghost.fright_timer <= 0:
                        self.ghost_fright_over()
                else:
                    # tick timer for change of ghost mode
                    self.mode_timer -= 1
                    if self.mode_timer <= 0:
                        self.change_ghost_mode()

                # Try and move the ghost in the calculated direction
                for ghost in self.scene["Ghosts"]:
                    # set movement direction for each ghost
                    direction = ghost.set_direction(self.pacman)
                    # Try and move in that direction
                    if not self.move_ghost(ghost, direction):
                        # try to continue to move in current direction
                        moved = False
                        if not self.move_ghost(ghost, ghost.current_direction):
                            # Cannot move in the selected or current direction so test other directions
                            order = ghost.get_order()
                            for i in range(0, 4):
                                if order[i] == LEFT and ghost.current_direction == RIGHT:
                                    continue
                                if order[i] == RIGHT and ghost.current_direction == LEFT:
                                    continue
                                if order[i] == UP and ghost.current_direction == DOWN:
                                    continue
                                if order[i] == DOWN and ghost.current_direction == UP:
                                    continue
                                moved = self.move_ghost(ghost, order[i])
                                if moved:
                                    break
                            if not moved:
                                # reverse direction if ghost cannot move in any of the tried directions
                                if ghost.current_direction == LEFT:
                                    direction = RIGHT
                                elif ghost.current_direction == RIGHT:
                                    direction = LEFT
                                elif ghost.current_direction == UP:
                                    direction = DOWN
                                elif ghost.current_direction == DOWN:
                                    direction = UP
                                self.move_ghost(ghost, direction)

            self.scene.update(delta_time)

    def on_draw(self):
        """Render the screen."""
        # The clear method should always be called at the start of on_draw.
        # It clears the whole screen to whatever the background color is
        # set to. This ensures that you have a clean slate for drawing each
        # frame of the game.
        self.clear()

        if self.game_state == IN_PLAY:
            self.scene.draw()
            for message in self.messages:
                message.draw()
                if message.done:
                    self.messages.remove(message)

        match self.game_state:
            case constants.IN_PLAY:
                self.score_batch.draw()
            case constants.GAME_OVER:
                self.game_over.draw()
            case constants.PAUSED:
                self.instructions.draw()


def main():
    """Main function"""
    window = GameView()
    arcade.run()


if __name__ == "__main__":
    main()
