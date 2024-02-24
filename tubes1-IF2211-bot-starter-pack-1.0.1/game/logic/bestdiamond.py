import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

def get_best_diamond_position(board_bot: GameObject, board: Board):
    diamonds = board.diamonds
    props = board_bot.properties    

    best_diamond = diamonds[0]
    min_distance_points_ratio = 10000
    for diamond in diamonds:
        if (props.diamonds == 4 and diamond.properties.points == 2):
            continue

        x_distance = abs(board_bot.position.x - diamond.position.x)
        y_distance = abs(board_bot.position.y - diamond.position.y)
        total_distance = x_distance + y_distance

        if ((total_distance / diamond.properties.points) < min_distance_points_ratio):
            min_distance_points_ratio = (total_distance / diamond.properties.points)
            best_diamond = diamond

    return best_diamond.position

class BestDiamondLogic(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        base = board_bot.properties.base

        distance_to_board = abs(current_position.x - base.x) + abs(current_position.y - base.y)

        if (props.diamonds == 5):
            self.goal_position = base
        else:
            self.goal_position = get_best_diamond_position(board_bot, board)

        if ((props.milliseconds_left / 1000) - 1 <= distance_to_board):
            self.goal_position = base

        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        else:
            # Roam around
            delta = self.directions[self.current_direction]
            delta_x = delta[0]
            delta_y = delta[1]
            if random.random() > 0.6:
                self.current_direction = (self.current_direction + 1) % len(
                    self.directions
                )
        return delta_x, delta_y