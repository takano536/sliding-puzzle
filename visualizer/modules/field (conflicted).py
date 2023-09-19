import logging
import pygame

import modules.block


class Field:

    DIRECTIONS = {
        'U': (-1, 0),
        'D': (1, 0),
        'R': (0, 1),
        'L': (0, -1),
    }

    def __init__(self, field: list, tile_size: tuple, block_colors: list, surface: pygame.Surface, drawing_top_left: tuple, block_gap: int, corner_radius: int) -> None:
        self.__field = field
        self.__block_num = max([max(idxs) for idxs in field]) + 1
        self.__tile_size = tile_size
        self.__blocks = [modules.block.Block() for _ in range(self.__block_num)]
        self.__gap = block_gap
        self.__top_left = drawing_top_left
        self.__width = len(field[0]) * tile_size[0]
        self.__height = len(field) * tile_size[1]
        self.__radius = corner_radius
        self.__bg_color = block_colors[-1]

        for i in range(len(self.__field)):
            for j in range(len(self.__field[i])):

                block_idx = self.__field[i][j]
                if block_idx == -1:
                    continue

                self.__blocks[block_idx].field_idxs.append((i, j))
                self.__blocks[block_idx].color = block_colors[block_idx]

                is_connected = self.__is_connected((i, j))
                rect = self.__get_rect((i, j), is_connected)

                if not is_connected['U'] and not is_connected['L']:
                    self.__blocks[block_idx].top_left = [rect.top, rect.left]
                if not is_connected['D'] and not is_connected['R']:
                    self.__blocks[block_idx].bottom_right = [rect.top + rect.height, rect.left + rect.width]

                pygame.draw.rect(
                    surface, self.__blocks[block_idx].color, rect,
                    border_top_left_radius=0 if is_connected['U'] or is_connected['L'] else self.__radius,
                    border_top_right_radius=0 if is_connected['U'] or is_connected['R'] else self.__radius,
                    border_bottom_left_radius=0 if is_connected['D'] or is_connected['L'] else self.__radius,
                    border_bottom_right_radius=0 if is_connected['D'] or is_connected['R'] else self.__radius,
                )

        for i in range(self.__block_num):
            top, left = self.__blocks[i].top_left
            bottom, right = self.__blocks[i].bottom_right
            width, height = right - left, bottom - top
            self.__blocks[i].center = [top + int(height / 2), left + int(width / 2)]

    def update(self, cursor: list, surface: pygame.Surface, dirty_rects: list):
        block_idx = self.__get_block_idx(cursor)
        if block_idx == -1:
            return

        is_movable = self.__is_movable(block_idx)
        if not any(is_movable.values()):
            return

        directions = self.__get_move_direction(block_idx, cursor)
        if len([value for value in is_movable.values() if value]) == 1:
            directions = ''.join([key for key, value in is_movable.items() if value])
        else:
            directions = ''.join([direction for direction in list(directions) if is_movable[direction]])

        self.__swap(block_idx, directions, surface, dirty_rects)

    def __get_rect(self, field_idx: tuple, is_connected: dict) -> pygame.Rect:
        i, j = field_idx
        top = self.__top_left[1] + i * self.__tile_size[1] + (0 if is_connected['U'] else self.__gap)
        left = self.__top_left[0] + j * self.__tile_size[0] + (0 if is_connected['L'] else self.__gap)
        width = self.__tile_size[0] - (0 if is_connected['L'] else self.__gap) - (0 if is_connected['R'] else self.__gap)
        height = self.__tile_size[1] - (0 if is_connected['U'] else self.__gap) - (0 if is_connected['D'] else self.__gap)
        return pygame.Rect(left, top, width, height)

    def __swap(self, block_idx: int, directions: str, surface: pygame.Surface, dirty_rects: list):
        if len(directions) < 1:
            return

        logging.debug(f'block {block_idx} is swapped to {directions}.')
        direction = directions[0]
        first = self.__blocks[block_idx].field_idxs[0][0] + self.DIRECTIONS[direction][0]
        second = self.__blocks[block_idx].field_idxs[0][1] + self.DIRECTIONS[direction][1]
        space_field_idx = (first, second)

        block = self.__blocks[block_idx]
        is_connected = {field_idx: self.__is_connected(field_idx) for field_idx in block.field_idxs}
        if len(block.field_idxs) == 1:
            swap_field_idx = block.field_idxs[0]
        else:
            swap_field_idx = [field_idx for field_idx in block.field_idxs if is_connected[field_idx][direction]][0]

        # mask
        for field_idx in block.field_idxs:
            rect = self.__get_rect(field_idx, is_connected[field_idx])
            dirty_rects.append(rect)
            pygame.draw.rect(surface, self.__bg_color, rect)

        is_swapped = [False] * len(block.field_idxs)
        i = 0
        while not all(is_swapped):
            block_field_idx = block.field_idxs[i]
            first = self.__blocks[block_idx].field_idxs[i][0] + self.DIRECTIONS[direction][0]
            second = self.__blocks[block_idx].field_idxs[i][1] + self.DIRECTIONS[direction][1]
            space_field_idx = (first, second)

        self.__field[space_field_idx[0]][space_field_idx[1]] = block_idx
        self.__field[swap_field_idx[0]][swap_field_idx[1]] = -1

        block.field_idxs.remove(swap_field_idx)
        block.field_idxs.append(space_field_idx)

        for field_idx in block.field_idxs:
            is_connected = self.__is_connected(field_idx)
            rect = self.__get_rect(field_idx, is_connected)
            if not is_connected['U'] and not is_connected['L']:
                self.__blocks[block_idx].top_left = [rect.top, rect.left]
            if not is_connected['D'] and not is_connected['R']:
                self.__blocks[block_idx].bottom_right = [rect.top + rect.height, rect.left + rect.width]
            dirty_rects.append(rect)
            pygame.draw.rect(
                surface, block.color, rect,
                border_top_left_radius=0 if is_connected['U'] or is_connected['L'] else self.__radius,
                border_top_right_radius=0 if is_connected['U'] or is_connected['R'] else self.__radius,
                border_bottom_left_radius=0 if is_connected['D'] or is_connected['L'] else self.__radius,
                border_bottom_right_radius=0 if is_connected['D'] or is_connected['R'] else self.__radius,
            )

        top, left = block.top_left
        bottom, right = block.bottom_right
        width, height = right - left, bottom - top
        block.center = [top + int(height / 2), left + int(width / 2)]

    def __get_block_idx(self, cursor: list) -> int:
        for i in range(self.__block_num):
            if cursor[0] < self.__blocks[i].top_left[0] or cursor[0] > self.__blocks[i].bottom_right[0]:
                continue
            if cursor[1] < self.__blocks[i].top_left[1] or cursor[1] > self.__blocks[i].bottom_right[1]:
                continue
            logging.debug(f'block {i} is selected.')
            return i
        return -1

    def __get_move_direction(self, block_idx: int, cursor: list):
        if block_idx == -1:
            return None
        block = self.__blocks[block_idx]
        direction = ''
        if cursor[0] < block.center[0]:
            direction += 'U'
        if cursor[0] > block.center[0]:
            direction += 'D'
        if cursor[1] < block.center[1]:
            direction += 'L'
        if cursor[1] > block.center[1]:
            direction += 'R'
        logging.debug(f'block {block_idx} is moved to {direction}.')
        return direction

    def __is_connected(self, field_idx: tuple) -> dict:
        is_connected = dict()
        for key, value in self.DIRECTIONS.items():
            i, j = field_idx
            is_connected[key] = False
            if self.__field[i][j] == -1:
                continue
            next_i = i + value[0]
            next_j = j + value[1]
            if next_j < 0 or next_j >= len(self.__field[i]) or next_i < 0 or next_i >= len(self.__field):
                continue
            if self.__field[i][j] != self.__field[next_i][next_j]:
                continue
            is_connected[key] = True
        return is_connected

    def __is_movable(self, block_idx) -> bool:
        is_moveable = {'U': True, 'D': True, 'R': True, 'L': True}
        block = self.__blocks[block_idx]
        is_connected = {field_idx: self.__is_connected(field_idx) for field_idx in block.field_idxs}

        for field_idx, is_connected in is_connected.items():
            for key, value in is_moveable.items():

                if is_connected[key]:
                    continue

                first = field_idx[0] + self.DIRECTIONS[key][0]
                second = field_idx[1] + self.DIRECTIONS[key][1]
                if first < 0 or first >= len(self.__field):
                    is_moveable[key] = False
                    continue
                if second < 0 or second >= len(self.__field[0]):
                    is_moveable[key] = False
                    continue

                is_moveable[key] = value and self.__field[first][second] == -1

        if logging.root.level == logging.DEBUG:
            [logging.debug(f'block {block_idx} is moveable to {key}.') for key, value in is_moveable.items() if value]
        if not any(is_moveable.values()):
            logging.debug(f'block {block_idx} is not moveable.')

        return is_moveable
