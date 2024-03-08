from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Properties, Position
from ..util import get_direction, position_equals

class myBot(BaseLogic):
    def __init__(self):
        self.goal_position = None
        self.previous_position = (None, None)
        self.turn_direction = 1

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        current_position = board_bot.position

        # Cek jarak ke base
        distance_to_base = abs(current_position.x - props.base.x) + abs(current_position.y - props.base.y)

        # Jika sedang membawa diamond dan waktu hampir habis, dan ratio jarak ke base dan sisa waktu lebih dari 1
        if (props.diamonds > 0 and distance_to_base/(props.milliseconds_left/1000) >= 1) or props.diamonds == 5:
            self.goal_position = props.base

        if props.diamonds == 4 or props.diamonds == 3:     # Jika jumlah diamond di inventory sudah mencapai 3/4
            closest_diamond_position = self.find_closest_diamond(current_position, board.diamonds, props)
            if closest_diamond_position:
                distance_to_diamond = abs(current_position.x - closest_diamond_position.x - 1) + abs(current_position.y - closest_diamond_position.y)
                # Bandingkan dengan jarak ke base
                if distance_to_diamond < distance_to_base:
                    # Jika jarak ke diamond lebih dekat dari jarak ke base, pergi ambil diamond
                    self.goal_position = closest_diamond_position
                else:
                    # Jika jarak ke base lebih dekat, langsung kembali ke base
                    self.goal_position = props.base
            else:
                # Jika tidak ada diamond bernilai 1 di sekitar, langsung kembali ke base
                self.goal_position = props.base
        
        elif self.goal_position is None or position_equals(current_position, self.goal_position): 
            # Cari sel dengan jumlah diamond terbanyak di sekitar
            max_diamonds_around = 0
            best_position = None

            for y in range(board.height):
                for x in range(board.width):
                    current_pos = Position(y=y, x=x)
                    diamonds_around = self.count_diamonds_around(current_pos, board)

                    if diamonds_around > max_diamonds_around:
                        max_diamonds_around = diamonds_around
                        best_position = current_pos
                        
            if best_position:
                # Cari posisi diamond dengan point paling gede 
                max_points = 0
                best_diamond = None
                for diamond in board.diamonds:
                    space_left = props.inventory_size - props.diamonds
                    if diamond.properties.points <= space_left:
                        if diamond.properties.points > max_points:
                            max_points = diamond.properties.points
                            best_diamond = diamond
                distance_to_best_diamond = abs(current_position.x - best_diamond.position.x - 1) + abs(current_position.y - best_diamond.position.y)
                if best_diamond.properties.points == 2 and distance_to_best_diamond <= 7:
                    self.goal_position = best_diamond.position
                else:
                    # Cari diamond dengan jarak terdeket
                    self.goal_position = self.find_closest_diamond(board_bot.position, board.diamonds, props)
        
        if self.goal_position:
            current_position = board_bot.position
            cur_x = current_position.x
            cur_y = current_position.y

            # Hitung jarak ke posisi tujuan
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )

            if (cur_x, cur_y) == self.previous_position:
                if delta_x != 0 and delta_y != 0:
                    # Jika bot dapat bergerak dalam semua arah
                    if abs(delta_x) > abs(delta_y):
                        delta_y = 0
                    else:
                        delta_x = 0
                elif delta_x == 0 and delta_y == 0:
                    # Jika bot berada di tempat yang sama
                    delta_x = 0
                    delta_y = 0
            else:
                self.previous_position = (cur_x, cur_y)
            return delta_x, delta_y
        return 0, 0

    def find_closest_diamond(self, current_position, diamonds, props):
        closest_distance = float('inf')
        closest_diamond_position = None
        if props.diamonds == 4:
            for diamond in diamonds:
                if diamond.properties.points == 1:
                    distance = abs(diamond.position.x - current_position.x) + abs(diamond.position.y - current_position.y)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_diamond_position = diamond.position
        else:
            for diamond in diamonds:
                distance = abs(diamond.position.x - current_position.x) + abs(diamond.position.y - current_position.y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_diamond_position = diamond.position
        return closest_diamond_position
    
    def count_diamonds_around(self, position: Position, board: Board) -> int:
        diamonds_count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 <= position.y + dy < board.height and 0 <= position.x + dx < board.width:
                    neighbor_pos = Position(y=position.y + dy, x=position.x + dx)
                    diamonds_count += sum(1 for diamond in board.diamonds if position_equals(diamond.position, neighbor_pos))

        return diamonds_count