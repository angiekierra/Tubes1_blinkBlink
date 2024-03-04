import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction, position_equals

def distance(p1: Position, p2: Position):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)

def teleporter_positions(board: Board):
    teleporters = []
    for game_object in board.game_objects:
        if (game_object.type == "TeleportGameObject"):
            teleporters.append(game_object.position)
    return teleporters

def blocked_by_teleporter(position: Position, board: Board):
    teleporters = teleporter_positions(board)
    return (position_equals(teleporters[0], position) or position_equals(teleporters[1], position))

def red_button(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    for game_object in board.game_objects:
        if (game_object.type == "DiamondButtonGameObject"):
            red_button = game_object.position
            break

    total_distance_normal = distance(board_bot.position, red_button)
    total_distance_tp = distance(board_bot.position, close_tp) + distance(far_tp, red_button)

    return red_button if ((total_distance_normal <= total_distance_tp) or position_equals(board_bot.position, close_tp)) else close_tp 

def best_diamond(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    diamonds = board.diamonds
    props = board_bot.properties

    best_diamond = diamonds[0]
    min_distance_points_ratio = 10000
    through_tp = False

    for diamond in diamonds:
        if (props.diamonds == 4 and diamond.properties.points == 2):
            continue

        total_distance_normal = distance(board_bot.position, diamond.position)
        total_distance_tp = distance(board_bot.position, close_tp) + distance(far_tp, diamond.position)
        total_distance = min(total_distance_normal, total_distance_tp)

        if ((total_distance / diamond.properties.points) < min_distance_points_ratio):
            min_distance_points_ratio = (total_distance / diamond.properties.points)
            best_diamond = diamond
            through_tp = True if (total_distance == total_distance_tp) else False

    return close_tp if (through_tp and not(position_equals(board_bot.position, close_tp))) else best_diamond.position

# def tackle_nearest_enemy(board_bot: GameObject, board: Board):
#     enemies = [bot for bot in board.bots if bot.properties.name != board_bot.properties.name]

#     nearest_enemy_distance = 10000000
#     nearest_enemy = enemies[0]
#     for enemy in enemies:
#         if (distance(enemy.position, board_bot.position) < nearest_enemy_distance):
#             nearest_enemy_distance = distance(enemy.position, board_bot.position)
#             nearest_enemy = enemy
    
#     return nearest_enemy.position

def to_base(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    base = board_bot.properties.base

    return_distance_normal = distance(board_bot.position, base)
    return_distance_tp = distance(board_bot.position, close_tp) + distance(far_tp, base)
    
    return base if (return_distance_normal < return_distance_tp or position_equals(board_bot.position, close_tp)) else close_tp

class BestDiamondLogic(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        base = board_bot.properties.base
        print(props.milliseconds_left)
        print(props.inventory_size)
        
        teleporters = teleporter_positions(board)
        close_tp = teleporters[0] if (distance(board_bot.position, teleporters[0]) < distance(board_bot.position, teleporters[1])) else teleporters[1]
        far_tp = teleporters[1] if (position_equals(close_tp, teleporters[0])) else teleporters[0]

        distance_to_base = distance(current_position, base)

        if (props.diamonds == 5):
            self.goal_position = to_base(board_bot, board, close_tp, far_tp)
        # elif (len(board.bots) == 2):
        #     self.goal_position = tackle_nearest_enemy(board_bot, board)
        else:
            d_red_button = distance(red_button(board_bot, board, close_tp, far_tp), current_position)
            d_best_diamond = distance(best_diamond(board_bot, board, close_tp, far_tp), current_position)

            if (d_red_button < d_best_diamond):
                self.goal_position = red_button(board_bot, board, close_tp, far_tp)
            else:
                self.goal_position = best_diamond(board_bot, board, close_tp, far_tp)

        if ((props.milliseconds_left / 1000) - 1 <= distance_to_base):
            self.goal_position = to_base(board_bot, board, close_tp, far_tp)

        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            
            new_position = Position(x=(current_position.x + delta_x), y=(current_position.y + delta_y))
            # check if destination isnt a teleporter, but blocked by a teleporter
            if (blocked_by_teleporter(new_position, board) and not(position_equals(self.goal_position, close_tp))):
                if (delta_x != 0): # if initially going vertically, move horizontally
                    delta_x = 0
                    if (board.is_valid_move(current_position, delta_x, 1)): 
                        delta_y = 1
                    else:
                        delta_y = -1 # go down if cant go up (at the top of the board)
                else:
                    delta_y = 0
                    if (board.is_valid_move(current_position, 1, delta_y)):
                        delta_x = 1
                    else:
                        delta_x = -1 # go left if cant go right (at the right edge of the board)
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