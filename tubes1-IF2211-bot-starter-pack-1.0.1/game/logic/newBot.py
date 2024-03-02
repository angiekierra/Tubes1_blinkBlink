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
    
    def find_nearest_teleporter(self, board_bot: GameObject, teleporters):
        nearest_teleporter = None
        min_distance = float('inf')

        for teleport in teleporters:
            distance = (abs(board_bot.position.x - teleport.position.x)) + (abs(board_bot.position.y - teleport.position.y))
            if (distance < min_distance):
                min_distance = distance
                nearest_teleporter = teleport
        return nearest_teleporter
    
    def get_nearest_diamond(self,board_bot: GameObject, board : Board) :
        nearest_diamond = None  
        min_distance = float('inf')

        for diamond in board.diamonds: 
            distance = (abs(board_bot.position.x - diamond.position.x)) + (abs(board_bot.position.y - diamond.position.y))
            if distance < min_distance :
                min_distance = distance
                nearest_diamond = diamond
        return nearest_diamond
    

    # def teleport_ratio()
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
                if(props.diamonds == 4):
                    best_diamond = self.best_diamond_ratio(board_bot,board)
                    distance_diamond = self.calculate_distance(board_bot.position,best_diamond)
                    if (distance_base < distance_diamond[0]):
                        self.goal_position = base
                    else:
                        self.goal_position = best_diamond[0]
                else:
                    best_diamond = self.best_diamond_ratio(board_bot,board)
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