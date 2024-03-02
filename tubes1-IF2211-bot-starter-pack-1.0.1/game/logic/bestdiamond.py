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

def best_diamond_position(board_bot: GameObject, board: Board):
    diamonds = board.diamonds
    props = board_bot.properties

    best_diamond = diamonds[0]
    min_distance_points_ratio = 10000
    
    for diamond in diamonds:
        if (props.diamonds == 4 and diamond.properties.points == 2):
            continue

        total_distance = distance(board_bot.position, diamond.position)

        if ((total_distance / diamond.properties.points) < min_distance_points_ratio):
            min_distance_points_ratio = (total_distance / diamond.properties.points)
            best_diamond = diamond

    return best_diamond.position

def best_diamond_position_tp(board_bot: GameObject, board: Board):
    diamonds = board.diamonds
    props = board_bot.properties

    teleporters = teleporter_positions(board)
    close_tp = teleporters[0] if (distance(board_bot.position, teleporters[0]) < distance(board_bot.position, teleporters[1])) else teleporters[1]
    far_tp = teleporters[1] if (position_equals(close_tp, teleporters[0])) else teleporters[0]

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

def tackle_nearest_enemy(board_bot: GameObject, board: Board):
    enemies = [bot for bot in board.bots if bot.properties.name != board_bot.properties.name]

    nearest_enemy_distance = 10000000
    nearest_enemy = enemies[0]
    for enemy in enemies:
        if (distance(enemy.position, board_bot.position) < nearest_enemy_distance):
            nearest_enemy_distance = distance(enemy.position, board_bot.position)
            nearest_enemy = enemy
    
    return nearest_enemy.position

def to_base(board_bot: GameObject, board: Board):
    base = board_bot.properties.base

    teleporters = teleporter_positions(board)
    close_tp = teleporters[0] if (distance(board_bot.position, teleporters[0]) < distance(board_bot.position, teleporters[1])) else teleporters[1]
    far_tp = teleporters[1] if (position_equals(close_tp, teleporters[0])) else teleporters[0]

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

        distance_to_board = abs(current_position.x - base.x) + abs(current_position.y - base.y)

        if (props.diamonds == 5):
            self.goal_position = to_base(board_bot, board)
        elif (len(board.bots) == 2):
            self.goal_position = tackle_nearest_enemy(board_bot, board)
        else:
            self.goal_position = best_diamond_position_tp(board_bot, board)

        if ((props.milliseconds_left / 1000) - 1 <= distance_to_board):
            self.goal_position = to_base(board_bot, board)

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