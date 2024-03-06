import random
from typing import Optional, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import clamp, position_equals

def get_direction(current_x, current_y, dest_x, dest_y, h_priority):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if h_priority:
        if delta_x != 0:
            delta_y = 0
    else:
        if delta_y != 0:
            delta_x = 0
    return (delta_x, delta_y)

def distance(p1: Position, p2: Position):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)

def distance_tp(src: Position, dest: Position, close_tp: Position, far_tp: Position):
    return distance(src, close_tp) + distance(far_tp, dest)

def min_distance(src: Position, dest: Position, close_tp: Position, far_tp: Position):
    return min(distance(src, dest), distance_tp(src, dest, close_tp, far_tp))

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

def within_cluster(p1: Position, p2: Position):
    return (abs(p1.x - p2.x) < 3 and abs(p1.y - p2.y) < 3)

def count_diamond_cluster(diamond: GameObject, diamonds: List[GameObject]):
    sum = diamond.properties.points
    for diamond2 in diamonds:
        if (within_cluster(diamond.position, diamond2.position) and not(position_equals(diamond.position, diamond2.position))):
            sum += diamond2.properties.points
    return sum

def best_cluster(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    diamonds = board.diamonds
    props = board_bot.properties

    best_cluster = diamonds[0]
    min_distance_points_ratio = 10000
    through_tp = False
    chosen_distance = 100000
    max_points = 0

    for diamond in diamonds:
        if (props.diamonds == 4 and diamond.properties.points == 2):
            continue

        total_diamonds = count_diamond_cluster(diamond, diamonds)

        total_distance_normal = distance(board_bot.position, diamond.position)
        total_distance_tp = distance(board_bot.position, close_tp) + distance(far_tp, diamond.position)
        total_distance = min(total_distance_normal, total_distance_tp)

        if ((total_distance / min(total_diamonds, props.inventory_size - props.diamonds)) < min_distance_points_ratio):
            min_distance_points_ratio = (total_distance / min(total_diamonds, props.inventory_size - props.diamonds))
            best_cluster = diamond
            max_points = min(total_diamonds, props.inventory_size - props.diamonds)
            chosen_distance = total_distance
            through_tp = True if (total_distance == total_distance_tp) else False

    print(f"Current position: {board_bot.position.x} {board_bot.position.y}")
    print(f"Best cluster: {best_cluster.position.x} {best_cluster.position.y}")
    print(f"Distance: {chosen_distance}")
    print(f"Points: {max_points}")
    return close_tp if (through_tp and not(position_equals(board_bot.position, close_tp))) else best_cluster.position

def best_cluster_base(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    diamonds = board.diamonds
    props = board_bot.properties

    best_cluster = diamonds[0]
    min_distance_points_ratio = 10000
    through_tp = False
    chosen_distance = 100000
    max_points = 0

    for diamond in diamonds:
        if (props.diamonds == 4 and diamond.properties.points == 2):
            continue

        total_diamonds = count_diamond_cluster(diamond, diamonds)

        d_current_diamond = min_distance(board_bot.position, diamond.position, close_tp, far_tp)
        d_diamond_base = min_distance(diamond.position, board_bot.properties.base, close_tp, far_tp)
        total_distance = d_current_diamond + d_diamond_base

        if ((total_distance / min(total_diamonds, props.inventory_size - props.diamonds)) < min_distance_points_ratio):
            min_distance_points_ratio = (total_distance / min(total_diamonds, props.inventory_size - props.diamonds))
            best_cluster = diamond
            max_points = min(total_diamonds, props.inventory_size - props.diamonds)
            chosen_distance = total_distance
            through_tp = True if (d_current_diamond == distance_tp(board_bot.position, diamond.position, close_tp, far_tp)) else False

    print(f"Current position: {board_bot.position.x} {board_bot.position.y}")
    print(f"Best cluster (returning): {best_cluster.position.x} {best_cluster.position.y}")
    print(f"Distance: {chosen_distance}")
    print(f"Points: {max_points}")
    return close_tp if (through_tp and not(position_equals(board_bot.position, close_tp))) else best_cluster.position

def to_base(board_bot: GameObject, board: Board, close_tp: Position, far_tp: Position):
    base = board_bot.properties.base

    return_distance_normal = distance(board_bot.position, base)
    return_distance_tp = distance(board_bot.position, close_tp) + distance(far_tp, base)
    
    return base if (return_distance_normal < return_distance_tp or position_equals(board_bot.position, close_tp)) else close_tp

class BestClusterLogic(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.h_priority = True
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position
        base = board_bot.properties.base

        print(props.milliseconds_left)
        
        teleporters = teleporter_positions(board)
        close_tp = teleporters[0] if (distance(board_bot.position, teleporters[0]) < distance(board_bot.position, teleporters[1])) else teleporters[1]
        far_tp = teleporters[1] if (position_equals(close_tp, teleporters[0])) else teleporters[0]

        distance_to_base = min(distance(current_position, base), distance_tp(current_position, base, close_tp, far_tp))
        d_red_button = distance(red_button(board_bot, board, close_tp, far_tp), current_position)

        if (props.diamonds == 5):
            self.goal_position = to_base(board_bot, board, close_tp, far_tp)
            print(f"To base chosen (full)")
        elif (props.diamonds >= 3):
            cluster = best_cluster_base(board_bot, board, close_tp, far_tp)
            red = red_button(board_bot, board, close_tp, far_tp)

            d_current_cluster = min_distance(current_position, cluster, close_tp, far_tp)
            d_cluster_base = min_distance(cluster, base, close_tp, far_tp)
            d_red_button_base = min_distance(red, base, close_tp, far_tp)

            if (d_red_button < d_current_cluster and (d_red_button + d_red_button_base) < (distance_to_base + 5) and not(position_equals(red, close_tp))):
                self.goal_position = red
                print(f"Red button chosen")
            elif (d_current_cluster + d_cluster_base) < distance_to_base + 5 and not(position_equals(cluster, close_tp)):
                self.goal_position = cluster
                print(f"Best cluster chosen (returning)")
            else:
                self.goal_position = to_base(board_bot, board, close_tp, far_tp)
                print(f"To base chosen (next item too far)")
        else:
            d_best_cluster = distance(best_cluster(board_bot, board, close_tp, far_tp), current_position)

            if (d_red_button < d_best_cluster and not(position_equals(red_button(board_bot, board, close_tp, far_tp), close_tp))):
                self.goal_position = red_button(board_bot, board, close_tp, far_tp)
                print(f"Red button chosen")
            else:
                self.goal_position = best_cluster(board_bot, board, close_tp, far_tp)
                print(f"Best cluster chosen")

        if ((props.milliseconds_left / 1000) - 1.5 <= distance_to_base):
            self.goal_position = to_base(board_bot, board, close_tp, far_tp)
            print(f"Distance: {distance(current_position, self.goal_position)}")
            print(f"To base chosen (time)")

        if self.goal_position:
            print(f"Goal position {self.goal_position.x} {self.goal_position.y}")
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
                self.h_priority
            )
            
            new_position = Position(x=(current_position.x + delta_x), y=(current_position.y + delta_y))
            # check if destination isnt a teleporter, but blocked by a teleporter
            if (blocked_by_teleporter(new_position, board) and not(position_equals(self.goal_position, close_tp))):
                print(f"Blocked by teleporter")
                if (delta_x != 0): # if initially going vertically, move horizontally
                    delta_x = 0
                    self.h_priority = True
                    if (board.is_valid_move(current_position, delta_x, 1)): 
                        delta_y = 1
                    else:
                        delta_y = -1 # go down if cant go up (at the top of the board)
                else:
                    delta_y = 0
                    self.h_priority = False
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