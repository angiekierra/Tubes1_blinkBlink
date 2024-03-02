from typing import Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

## Mentingin jarak 
class TestBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def find_nearest_diamond (self, board_bot: GameObject, board: Board) -> Optional[Position]:
        nearest_diamond = None  
        min_distance = float('inf')

        for diamond in board.diamonds: 
            distance = (abs(board_bot.position.x - diamond.position.x)) + (abs(board_bot.position.y - diamond.position.y))
            if distance < min_distance :
                min_distance = distance
                nearest_diamond = diamond.position
        return nearest_diamond
    
    def find_nearest_diamond_blue (self, board_bot: GameObject, board: Board) -> Optional[Position]:
        nearest_blue = None
        min_distance = float('inf')

        for diamond in board.diamonds:
            if (diamond.properties.points == 1):
                distance = (abs(board_bot.position.x - diamond.position.x)) + (abs(board_bot.position.y - diamond.position.y))
                if distance < min_distance :
                    min_distance = distance
                    nearest_blue = diamond.position
        return nearest_blue

    def calculate_distance(self, point1: Position, point2: Position) -> Optional[int]:
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        timeleft = board_bot.properties.milliseconds_left
        base = board_bot.properties.base
        distance_base = self.calculate_distance(board_bot.position,base)
        if timeleft <= (distance_base*1000):
            # Move to base
            self.goal_position = base
        else:
            if props.diamonds == 5:
                self.goal_position = base
            else:
                if (props.diamonds == 4):
                    # only look for blue diamonds
                    nearest_diamond = self.find_nearest_diamond_blue(board_bot,board)
                    distance_diamond = self.calculate_distance(board_bot.position,nearest_diamond)
                    if (distance_base < distance_diamond):
                        self.goal_position = base
                    else:
                        self.goal_position = nearest_diamond
                else :
                    nearest_diamond = self.find_nearest_diamond(board_bot,board)
                    self.goal_position = nearest_diamond



        current_position = board_bot.position
        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )

        return delta_x, delta_y