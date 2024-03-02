from typing import Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

## Mentingin diamond merah
class NewBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def best_diamond_ratio(self, board_bot: GameObject, board: Board):
        best_diamond_position = None
        max_ratio = float('-inf')

        props = board_bot.properties

        for diamond in board.diamonds:
            points = diamond.properties.points
            if (props.diamonds == 4 and points == 2):
                continue
            distance = (abs(board_bot.position.x - diamond.position.x)) + (abs(board_bot.position.y - diamond.position.y))
            ratio = points/distance

            if (ratio > max_ratio):
                max_ratio = ratio
                best_diamond_position = diamond.position
        return best_diamond_position,max_ratio
    
    def get_teleporters(self,board:Board):
        teleporter = []
        for item in board.game_objects:
            if item.type == "TeleportGameObject":
                teleporter.append(item)
        return teleporter
    
    def find_nearest_teleporter(self, board_bot: GameObject, teleporters : list[GameObject]):
        nearest_teleporter = None
        min_distance = float('inf')

        for teleport in teleporters:
            distance = (abs(board_bot.position.x - teleport.position.x)) + (abs(board_bot.position.y - teleport.position.y))
            if (distance < min_distance):
                min_distance = distance
                nearest_teleporter = teleport
        return nearest_teleporter,min_distance
    
    def get_nearest_diamond(self,teleport: GameObject, board : Board) :
        nearest_diamond = None  
        min_distance = float('inf')

        for diamond in board.diamonds: 
            distance = (abs(teleport.position.x - diamond.position.x)) + (abs(teleport.position.y - diamond.position.y))
            if distance < min_distance :
                min_distance = distance
                nearest_diamond = diamond
        return nearest_diamond,min_distance
    
    def calculate_distance(self, point1: Position, point2: Position) -> Optional[int]:
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)

    def teleport_ratio(self,board_bot: GameObject, board : Board, teleporter : list[GameObject]):
        nearest_teleporter = self.find_nearest_teleporter(board_bot,teleporter)[0]
        nearest_teleporter_position = nearest_teleporter.position
        pair = None
        for teleport in teleporter:
            if teleport.id != nearest_teleporter.id:
                pair = teleport

        nearest_diamond = self.get_nearest_diamond(pair,board)
        distance_to_teleport = self.calculate_distance(board_bot.position,nearest_teleporter.position)
        distance_to_diamond = nearest_diamond[1]
        total_distance = distance_to_teleport+distance_to_diamond
        return (total_distance/nearest_diamond[0].properties.points),nearest_teleporter_position

    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        timeleft = board_bot.properties.milliseconds_left
        base = board_bot.properties.base
        distance_base = self.calculate_distance(board_bot.position,base)
        teleporters = self.get_teleporters(board)

        if timeleft <= (distance_base*1000):
            # Move to base
            self.goal_position = base
        else:
            if props.diamonds == 5:
                self.goal_position = base
            else:
                if(props.diamonds == 4):
                    best_diamond = self.best_diamond_ratio(board_bot,board)
                    distance_diamond = self.calculate_distance(board_bot.position,best_diamond[0])
                    if (distance_base < distance_diamond):
                        self.goal_position = base
                    else:
                        self.goal_position = best_diamond[0]
                else:
                    ratio_teleport = self.teleport_ratio(board_bot,board,teleporters)
                    best_diamond = self.best_diamond_ratio(board_bot,board)
                    if (ratio_teleport[0] > best_diamond[1] ) :
                        self.goal_position = ratio_teleport[1]
                    else:
                        self.goal_position = best_diamond[0]


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