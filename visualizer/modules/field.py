import copy
import logging
import pygame

import modules.block


class Field:

    DIRECTIONS = {
        pygame.K_UP: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_RIGHT: (0, 1),
        pygame.K_LEFT: (0, -1),
    }

    def __init__(self, field: list, tile_size: tuple, block_colors: list, surface: pygame.Surface, drawing_top_left: tuple, block_gap: int, corner_radius: int, moving_speed: int = 1):
        self.__init_field = copy.deepcopy(field)
        self.__field = field

        self.__block_num = max([max(idxs) for idxs in field]) + 1
        self.__blocks = [modules.block.Block() for _ in range(self.__block_num)]

        self.__tile_size = tile_size
        self.__gap = block_gap
        self.__radius = corner_radius
        self.__bg_color = block_colors[-1]

        self.__top_left = drawing_top_left
        self.__width = len(field[0]) * tile_size[0]
        self.__height = len(field) * tile_size[1]

        self.__is_moving = False
        self.__moving_direction = [None, None]
        self.__moving_block_idx = None
        self.__speed = moving_speed

        for i in range(self.__block_num):
            self.__blocks[i].color = block_colors[i]

        self.reset(surface)

    def reset(self, surface: pygame.Surface, dirty_rects: list = []):
        logging.debug('field is reset.')
        field_rect = pygame.Rect(self.__top_left[1], self.__top_left[0], self.__width, self.__height)
        dirty_rects.append(field_rect)
        pygame.draw.rect(surface, self.__bg_color, field_rect, border_radius=3)

        self.__field = copy.deepcopy(self.__init_field)
        for block in self.__blocks:
            block.reset()

        for i in range(len(self.__init_field)):
            for j in range(len(self.__init_field[i])):

                block_idx = self.__init_field[i][j]
                if block_idx == -1:
                    continue

                self.__blocks[block_idx].field_idxs.append((i, j))

                is_connected = self.__is_connected((i, j))
                rect = self.__get_rect((i, j), is_connected)

                if not is_connected[pygame.K_UP] and not is_connected[pygame.K_LEFT]:
                    self.__blocks[block_idx].curr_top_left = [rect.top, rect.left]
                if not is_connected[pygame.K_DOWN] and not is_connected[pygame.K_RIGHT]:
                    self.__blocks[block_idx].curr_bottom_right = [rect.top + rect.height, rect.left + rect.width]

                pygame.draw.rect(
                    surface, self.__blocks[block_idx].color, rect,
                    border_top_left_radius=0 if is_connected[pygame.K_UP] or is_connected[pygame.K_LEFT] else self.__radius,
                    border_top_right_radius=0 if is_connected[pygame.K_UP] or is_connected[pygame.K_RIGHT] else self.__radius,
                    border_bottom_left_radius=0 if is_connected[pygame.K_DOWN] or is_connected[pygame.K_LEFT] else self.__radius,
                    border_bottom_right_radius=0 if is_connected[pygame.K_DOWN] or is_connected[pygame.K_RIGHT] else self.__radius,
                )

    def update(self, surface: pygame.Surface, dirty_rects: list, cursor: list, event_type: int, key: int):
        block_idx = self.__get_block_idx(cursor)

        is_movable = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_RIGHT: False, pygame.K_LEFT: False}
        if block_idx is not None and event_type in (pygame.KEYDOWN, pygame.MOUSEBUTTONUP):
            is_movable = self.__is_movable(block_idx)
        if event_type == pygame.MOUSEBUTTONUP and list(is_movable.values()).count(True) == 1:
            key = [key for key, value in is_movable.items() if value][0]

        if any(is_movable.values()) and key is not None and is_movable[key] and not self.__is_moving:
            self.__swap(block_idx, key, surface, dirty_rects)
        if self.__is_moving:
            self.__draw_moving_block(surface, dirty_rects)

    def __draw_moving_block(self, surface: pygame.Surface, dirty_rects: list):
        # draw background
        block = self.__blocks[self.__moving_block_idx]
        rect = pygame.Rect(
            block.curr_top_left[1],
            block.curr_top_left[0],
            block.curr_bottom_right[1] - block.curr_top_left[1],
            block.curr_bottom_right[0] - block.curr_top_left[0],
        )
        dirty_rects.append(rect)
        pygame.draw.rect(surface, self.__bg_color, rect)

        # update coord
        block.curr_top_left[0] += self.__moving_direction[0] * self.__speed
        block.curr_top_left[1] += self.__moving_direction[1] * self.__speed
        block.curr_bottom_right[0] += self.__moving_direction[0] * self.__speed
        block.curr_bottom_right[1] += self.__moving_direction[1] * self.__speed
        diff = [
            (block.next_top_left[0] - block.curr_top_left[0]) * self.__moving_direction[0],
            (block.next_top_left[1] - block.curr_top_left[1]) * self.__moving_direction[1]
        ]
        if diff[0] < 0 or diff[1] < 0:
            block.curr_top_left = block.next_top_left.copy()
            block.curr_bottom_right = block.next_bottom_right.copy()
            self.__is_moving = False
            logging.debug(f'block {self.__moving_block_idx} is stopped.')

        # draw block
        rect = pygame.Rect(
            block.curr_top_left[1],
            block.curr_top_left[0],
            block.curr_bottom_right[1] - block.curr_top_left[1],
            block.curr_bottom_right[0] - block.curr_top_left[0],
        )
        dirty_rects.append(rect)
        pygame.draw.rect(surface, block.color, rect, border_radius=self.__radius)

    def __get_rect(self, field_idx: tuple, is_connected: dict) -> pygame.Rect:
        i, j = field_idx
        top = self.__top_left[1] + i * self.__tile_size[1] + (0 if is_connected[pygame.K_UP] else self.__gap)
        left = self.__top_left[0] + j * self.__tile_size[0] + (0 if is_connected[pygame.K_LEFT] else self.__gap)
        width = self.__tile_size[0] - (0 if is_connected[pygame.K_LEFT] else self.__gap) - (0 if is_connected[pygame.K_RIGHT] else self.__gap)
        height = self.__tile_size[1] - (0 if is_connected[pygame.K_UP] else self.__gap) - (0 if is_connected[pygame.K_DOWN] else self.__gap)
        return pygame.Rect(left, top, width, height)

    def __swap(self, block_idx: int, key: int, surface: pygame.Surface, dirty_rects: list):
        logging.debug(f'block {block_idx} is swaiped to {self.DIRECTIONS[key]}.')
        block = self.__blocks[block_idx]

        if logging.root.level == logging.DEBUG:
            [logging.debug(f'block {block_idx} [{field_idx}] is swapped to {self.DIRECTIONS[key]}.') for field_idx in block.field_idxs]

        is_swapped = [False] * len(block.field_idxs)
        i = 0
        while not all(is_swapped):
            if is_swapped[i]:
                i = (i + 1) % len(block.field_idxs)
                continue

            block_field_idx = block.field_idxs[i]
            space_field_idx = (
                block_field_idx[0] + self.DIRECTIONS[key][0],
                block_field_idx[1] + self.DIRECTIONS[key][1]
            )
            if space_field_idx in block.field_idxs:
                i = (i + 1) % len(block.field_idxs)
                continue

            logging.debug(f'block {block_idx} [{block_field_idx}] is swapped to {space_field_idx}.')
            self.__field[space_field_idx[0]][space_field_idx[1]] = block_idx
            self.__field[block_field_idx[0]][block_field_idx[1]] = -1

            block.field_idxs.remove(block_field_idx)
            block.field_idxs.insert(i, space_field_idx)
            is_swapped[i] = True

        for field_idx in block.field_idxs:
            is_connected = self.__is_connected(field_idx)
            rect = self.__get_rect(field_idx, is_connected)
            if not is_connected[pygame.K_UP] and not is_connected[pygame.K_LEFT]:
                self.__blocks[block_idx].next_top_left = [rect.top, rect.left]
            if not is_connected[pygame.K_DOWN] and not is_connected[pygame.K_RIGHT]:
                self.__blocks[block_idx].next_bottom_right = [rect.top + rect.height, rect.left + rect.width]
            logging.debug(f'block {block_idx} [{field_idx}] will be moved to {self.__blocks[block_idx].next_top_left}.')

        self.__is_moving = True
        self.__moving_block_idx = block_idx
        self.__moving_direction = self.DIRECTIONS[key]

    def __get_block_idx(self, cursor: list) -> int:
        if cursor is None:
            return None
        for i in range(self.__block_num):
            if cursor[0] < self.__blocks[i].curr_top_left[0] or cursor[0] > self.__blocks[i].curr_bottom_right[0]:
                continue
            if cursor[1] < self.__blocks[i].curr_top_left[1] or cursor[1] > self.__blocks[i].curr_bottom_right[1]:
                continue
            return i

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

    def __is_movable(self, block_idx):
        is_movable = {pygame.K_UP: True, pygame.K_DOWN: True, pygame.K_RIGHT: True, pygame.K_LEFT: True}
        block = self.__blocks[block_idx]
        is_connected = {field_idx: self.__is_connected(field_idx) for field_idx in block.field_idxs}

        for field_idx, is_connected in is_connected.items():
            for key, value in is_movable.items():

                if is_connected[key]:
                    continue

                first = field_idx[0] + self.DIRECTIONS[key][0]
                second = field_idx[1] + self.DIRECTIONS[key][1]
                if first < 0 or first >= len(self.__field):
                    is_movable[key] = False
                    continue
                if second < 0 or second >= len(self.__field[0]):
                    is_movable[key] = False
                    continue

                is_movable[key] = value and self.__field[first][second] == -1

        if logging.root.level == logging.DEBUG:
            [logging.debug(f'block {block_idx} is movable to {self.DIRECTIONS[key]}.') for key, value in is_movable.items() if value]
        if not any(is_movable.values()):
            logging.debug(f'block {block_idx} is not movable.')

        return is_movable
