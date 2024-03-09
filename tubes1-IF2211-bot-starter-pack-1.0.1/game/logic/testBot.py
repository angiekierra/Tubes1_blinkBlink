from typing import Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction,position_equals


class TestBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    

    def calculate_distance(self, point1: Position, point2: Position) -> Optional[int]:
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)
    
    def get_teleporter_position(self,board:Board):
        teleporter = []
        for item in board.game_objects:
            if (item.type == "TeleportGameObject"):
                teleporter.append(item.position)
        return teleporter
    
    def find_nearest_diamond (self, board_bot: GameObject, board: Board, nearest_teleporter : Position, next_teleporter : Position):
        nearest_diamond = None  
        min_distance = float('inf')
        teleport = False

        for diamond in board.diamonds: 
            distance_no_teleport = self.calculate_distance(board_bot.position, diamond.position)
            distance_with_teleport = self.calculate_distance(board_bot.position,nearest_teleporter) + self.calculate_distance(next_teleporter,diamond.position)

            teleport = True if distance_with_teleport < distance_no_teleport else False
            real_distance = distance_with_teleport if teleport else distance_no_teleport

            if real_distance < min_distance :
                min_distance = real_distance
                nearest_diamond = diamond.position
        return nearest_teleporter if (teleport and not(position_equals(board_bot.position,nearest_teleporter))) else nearest_diamond
    
    def find_nearest_diamond_blue (self, board_bot: GameObject, board: Board, nearest_teleporter : Position, next_teleporter : Position):
        nearest_blue = None
        min_distance = float('inf')
        teleport = False

        for diamond in board.diamonds:
            if (diamond.properties.points == 1):
                distance_no_teleport = self.calculate_distance(board_bot.position, diamond.position)
                distance_with_teleport = self.calculate_distance(board_bot.position,nearest_teleporter) + self.calculate_distance(next_teleporter,diamond.position)

                teleport = True if distance_with_teleport < distance_no_teleport else False
                real_distance = distance_with_teleport if teleport else distance_no_teleport

                if real_distance < min_distance :
                    min_distance = real_distance
                    nearest_blue = diamond.position

        return nearest_teleporter if (teleport and not(position_equals(board_bot.position,nearest_teleporter))) else nearest_blue
    
    def base(self, board_bot : GameObject, nearest_teleport : Position, next_teleport : Position):
        base_position = board_bot.properties.base

        distance_no_teleport = self.calculate_distance(board_bot.position,base_position)
        distance_with_teleport = self.calculate_distance(board_bot.position,nearest_teleport) + self.calculate_distance(next_teleport,base_position)

        return base_position if (distance_no_teleport <= distance_with_teleport) else nearest_teleport
    
    def red_button(self,board_bot : GameObject, board : Board, nearest_teleporter : Position, next_teleporter : Position):
        red_button = None
        teleport = False
        for item in board.game_objects:
            if item.type == "DiamondButtonGameObject":
                red_button = item.position
                break
        distance_teleport = self.calculate_distance(board_bot.position,nearest_teleporter) + self.calculate_distance(next_teleporter,red_button)
        distance_no_teleport = self.calculate_distance(board_bot.position,red_button)

        teleport = True if (distance_teleport < distance_no_teleport) else False
        return nearest_teleporter if (teleport and not(position_equals(board_bot.position,nearest_teleporter))) else red_button

    def dodge(self, board : Board, delta_x,delta_y,current_position : Position):
        if (delta_x != 0):
            delta_x = 0
            if (board.is_valid_move(current_position,delta_x,1)):
                delta_y = 1
            else :
                delta_y = -1
        else :
            delta_y = 0
            if (board.is_valid_move(current_position,1,delta_y)):
                delta_x = 1
            else :
                delta_x = -1
        return delta_x,delta_y

    def teleporter_obstacle(self,position: Position, board: Board):
        teleporters = self.get_teleporter_position(board)
        return (position_equals(teleporters[0], position) or position_equals(teleporters[1], position))
    
    def get_red_button_pos(self, board: Board):
        red_button = None
        for item in board.game_objects:
            if item.type == "DiamondButtonGameObject":
                red_button = item.position
                break  
        return red_button
    
    def red_button_obstacle(self,position : Position, board:Board):
        red_button = self.get_red_button_pos(board)
        return (position_equals(red_button, position))      

    # def nearest_bot(self,board_bot:GameObject,board : Board):
    #     bots = [bot for bot in board.bots if bot.id != board_bot.id]
    #     min_distance = float('inf')
    #     nearest_bot = None
    #     for bot in bots:
    #         if self.calculate_distance(board_bot.position,bot.position) < min_distance:
    #             min_distance = self.calculate_distance(board_bot.position,bot.position)
    #             nearest_bot = bot
    #     return nearest_bot

    # def bot_obstacle(self,pos1 : Position, pos2 : Position):
    #     return (position_equals(pos1,pos2))

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        time_left = props.milliseconds_left
        base = board_bot.properties.base
        distance_base = self.calculate_distance(board_bot.position,base)
        red_button = self.get_red_button_pos(board)
        teleporters = self.get_teleporter_position(board)
        nearest_teleporter = teleporters[0] if (self.calculate_distance(board_bot.position,teleporters[0]) < self.calculate_distance(board_bot.position,teleporters[1])) else teleporters[1]
        next_teleporter = teleporters[0] if (self.calculate_distance(board_bot.position,teleporters[0]) >= self.calculate_distance(board_bot.position,teleporters[1])) else teleporters[1]

        if time_left < (distance_base*1000+30):
            # Move to base
            self.goal_position = base
        else:
            if props.diamonds == 5:
                self.goal_position = base
            else:
                if (props.diamonds == 4):
                    # only look for blue diamonds
                    nearest_diamond = self.find_nearest_diamond_blue(board_bot,board,nearest_teleporter,next_teleporter)
                    distance_diamond = self.calculate_distance(board_bot.position,nearest_diamond)
                    if (distance_base < distance_diamond):
                        self.goal_position = base
                    else:
                        self.goal_position = nearest_diamond
                else :
                    nearest_diamond = self.find_nearest_diamond(board_bot,board,nearest_teleporter,next_teleporter)
                    to_red_button = self.red_button(board_bot,board,nearest_teleporter,next_teleporter)

                    distance_red_button = self.calculate_distance(board_bot.position,to_red_button)
                    distance_diamond = self.calculate_distance(board_bot.position,nearest_diamond)

                    self.goal_position = to_red_button if (distance_red_button < distance_diamond) else nearest_diamond




        current_position = board_bot.position
        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )

            next_position = Position(x=(current_position.x + delta_x), y=(current_position.y + delta_y))
            
            # Dodge teleporter
            if (self.teleporter_obstacle(next_position, board) and not(position_equals(self.goal_position, nearest_teleporter))):
                delta_x, delta_y = self.dodge(board, delta_x, delta_y)

            # Dodge red button
            if (self.red_button_obstacle(next_position, board) and not(position_equals(self.goal_position, red_button))):
                delta_x, delta_y = self.dodge(board, delta_x, delta_y)

            


        return delta_x, delta_y