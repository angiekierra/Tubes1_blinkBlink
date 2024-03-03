from typing import Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction,position_equals

class NewBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def calculate_distance(self, point1: Position, point2: Position):
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)
    
    
    def get_teleporter_position(self,board:Board):
        teleporter = []
        for item in board.game_objects:
            if (item.type == "TeleportGameObject"):
                teleporter.append(item.position)
        return teleporter
    
    def base(self, board_bot : GameObject, nearest_teleport : Position, next_teleport : Position):
        base_position = board_bot.properties.base

        distance_no_teleport = self.calculate_distance(board_bot.position,base_position)
        distance_with_teleport = self.calculate_distance(board_bot.position,nearest_teleport) + self.calculate_distance(next_teleport,base_position)

        return base_position if (distance_no_teleport <= distance_with_teleport) else nearest_teleport  
    

    def best_diamond_ratio(self, board_bot: GameObject, board: Board, nearest_teleport : Position, next_teleport : Position):
        best_diamond_position = None
        min_ratio = float('inf')
        teleport = False

        props = board_bot.properties

        for diamond in board.diamonds:
            points = diamond.properties.points
            if (props.diamonds == 4 and points == 2):
                continue
            distance_no_teleport = self.calculate_distance(board_bot.position, diamond.position)
            distance_with_teleport = self.calculate_distance(board_bot.position,nearest_teleport) + self.calculate_distance(next_teleport,diamond.position)

            teleport = True if distance_with_teleport < distance_no_teleport else False
            real_distance = distance_with_teleport if teleport else distance_no_teleport

            ratio = real_distance/points

            if (ratio < min_ratio):
                min_ratio = ratio
                best_diamond_position = diamond.position
        return nearest_teleport if (teleport and not(position_equals(board_bot.position,nearest_teleport))) else best_diamond_position

    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        timeleft = board_bot.properties.milliseconds_left
        base = board_bot.properties.base
        distance_base = self.calculate_distance(board_bot.position,base)
        teleporters = self.get_teleporter_position(board)

        nearest_teleporter = teleporters[0] if (self.calculate_distance(board_bot.position,teleporters[0]) < self.calculate_distance(board_bot.position,teleporters[1])) else teleporters[1]
        next_teleporter = teleporters[0] if (self.calculate_distance(board_bot.position,teleporters[0]) >= self.calculate_distance(board_bot.position,teleporters[1])) else teleporters[1]        
        

        
        if timeleft < (distance_base*1000+1):
            # Move to base
            self.goal_position = self.base(board_bot,nearest_teleporter,next_teleporter)
        else:
            if props.diamonds == 5:
                self.goal_position = self.base(board_bot,nearest_teleporter,next_teleporter)
            else:
                if(props.diamonds == 4):
                    best_diamond = self.best_diamond_ratio(board_bot,board,nearest_teleporter,next_teleporter)
                    distance_diamond = self.calculate_distance(board_bot.position,best_diamond)
                    if (distance_base < distance_diamond):
                        self.goal_position = self.base(board_bot,nearest_teleporter,next_teleporter)
                    else:
                        self.goal_position = best_diamond
                else:
                    best_diamond = self.best_diamond_ratio(board_bot,board,nearest_teleporter,next_teleporter)
                    self.goal_position = best_diamond



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