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

        # Jika sedang membawa diamond dan waktu hampir habis, dan jarak ke base lebih besar dari jarak maksimum yang dapat ditempuh dalam sisa waktu
        if props.diamonds > 0 and props.milliseconds_left <= 17000 and distance_to_base >= props.milliseconds_left/1000:
            # Bot pergi ke base untuk mengamankan diamondnya
            self.goal_position = props.base

        if props.diamonds == 4:     # Jika jumlah diamond di inventory sudah mencapai 4
            closest_low_value_diamond = self.find_closest_low_value_diamond(current_position, board.diamonds)
            if closest_low_value_diamond:
                # Hitung jarak ke diamond bernilai 1
                distance_to_low_value_diamond = abs(current_position.x - closest_low_value_diamond.x) + abs(current_position.y - closest_low_value_diamond.y)
                # Bandingkan dengan jarak ke base
                if distance_to_low_value_diamond < distance_to_base:
                    # Jika jarak ke diamond lebih dekat dari jarak ke base, pergi ambil diamond
                    self.goal_position = closest_low_value_diamond
                else:
                    # Jika jarak ke base lebih dekat, langsung kembali ke base
                    self.goal_position = props.base
            else:
                # Jika tidak ada diamond bernilai 1 di sekitar, langsung kembali ke base
                self.goal_position = props.base
        
        if props.diamonds == 5:
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
                max = 0
                best_diamond = None
                for diamond in board.diamonds:
                    space_left = props.inventory_size - props.diamonds
                    if diamond.properties.points <= space_left:
                        if diamond.properties.points > max:
                            max = diamond.properties.points
                            best_diamond = diamond
                if best_diamond == 2:
                    self.goal_position = best_diamond.position
                else:
                    # Cari diamond dengan jarak terdeket
                    self.goal_position = self.find_closest_diamond(board_bot.position, board.diamonds)
        
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
            # Invalid move
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
                    # Jika langkah valid, update posisi sebelumnya
                self.previous_position = (cur_x, cur_y)
            return delta_x, delta_y
        return 0, 0

    def find_closest_low_value_diamond(self, current_position, diamonds):
        closest_distance = float('inf')
        closest_low_value_diamond_position = None
        for diamond in diamonds:
            if diamond.properties.points == 1:
                distance = abs(diamond.position.x - current_position.x) + abs(diamond.position.y - current_position.y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_low_value_diamond_position = diamond.position
        return closest_low_value_diamond_position
    
    def find_closest_diamond(self, current_position, diamonds):
        closest_distance = float('inf')
        closest_diamond_position = None
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