import copy
import logging
import pygame

import modules.block


class Board:

    ENUM2DIR = {
        pygame.K_UP: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_RIGHT: (0, 1),
        pygame.K_LEFT: (0, -1),
    }
    ENUM2CHAR = {
        pygame.K_UP: 'U',
        pygame.K_DOWN: 'D',
        pygame.K_RIGHT: 'R',
        pygame.K_LEFT: 'L',
    }
    CHAR2ENUM = {
        'U': pygame.K_UP,
        'D': pygame.K_DOWN,
        'R': pygame.K_RIGHT,
        'L': pygame.K_LEFT,
    }

    def __init__(self, board: list, block_types: list, goal: dict, tile_size: tuple, block_colors: list, surface: pygame.Surface, drawing_top_left: tuple, block_gap: int, corner_radius: int, moving_speed: int = 1):
        self.__init_board = copy.deepcopy(board)
        self.__board = board
        self.__goal_block = int(list(goal.keys())[0])
        self.__goal_coords = list(goal.values())[0]

        self.__block_num = max([max(idxs) for idxs in board]) + 1
        self.__blocks = [modules.block.Block() for _ in range(self.__block_num)]

        self.__tile_size = tile_size
        self.__gap = int(block_gap * tile_size[0] / 32)
        self.__radius = corner_radius
        self.__bg_color = block_colors[-1]

        self.__top_left = drawing_top_left
        self.__width = len(board[0]) * tile_size[0]
        self.__height = len(board) * tile_size[1]

        self.__is_moving = False
        self.__moving_direction = [None, None]
        self.__moving_block_idx = None
        self.__speed = moving_speed * tile_size[0] / 32

        self.__step, self.__process = None, None
        self.__curr_answer_step = -1

        for i in range(self.__block_num):
            self.__blocks[i].color = block_colors[i]
            self.__blocks[i].shape = block_types[i]

        self.reset(surface)

    def play_answer(self, surface: pygame.Surface, dirty_rects: list):
        if self.__curr_answer_step == -1:
            prev_board = copy.deepcopy(self.__board)
            self.__step, self.__process = self.__solve()
            self.__board = copy.deepcopy(prev_board)
            self.__curr_answer_step = 0
        if self.__step is None or self.__process is None:
            return
        if self.__curr_answer_step >= self.__step:
            return

        step = self.__curr_answer_step * 2
        block_idx = int(self.__process[step])
        key = self.CHAR2ENUM[self.__process[step + 1]]

        self.__swap(block_idx, key)
        self.__curr_answer_step += 1

    def __solve(self):
        import collections

        que = collections.deque()
        que.append((copy.deepcopy(self.__board), 0, ''))
        is_saw = set()
        is_saw.add(''.join([''.join(['x' if i == -1 else str(self.__blocks[i].shape) for i in row]) for row in self.__board]))
        logging.debug(f'{"".join(["".join(["x" if i == -1 else str(self.__blocks[i].shape) for i in row]) for row in self.__board])}')

        while len(que) > 0:
            board, step, process = que.popleft()
            logging.debug('board')
            [logging.debug(row) for row in board]
            logging.debug(f'step: {step}')
            logging.debug(f'process: {process}')

            spaces = []
            for i in range(len(board)):
                for j in range(len(board[i])):
                    if board[i][j] == -1:
                        spaces.append((i, j))

            search_block_idxs = []
            for space in spaces:
                for value in self.ENUM2DIR.values():
                    if space[0] + value[0] < 0 or space[0] + value[0] >= len(board):
                        continue
                    if space[1] + value[1] < 0 or space[1] + value[1] >= len(board[0]):
                        continue
                    if board[space[0] + value[0]][space[1] + value[1]] == -1:
                        continue
                    if board[space[0] + value[0]][space[1] + value[1]] in search_block_idxs:
                        continue
                    search_block_idxs.append(board[space[0] + value[0]][space[1] + value[1]])

            for block_idx in search_block_idxs:
                for dir, is_movable in self.__is_movable(block_idx, board).items():
                    if not is_movable:
                        continue
                    next_board = copy.deepcopy(board)
                    block_coords = list()
                    for i in range(len(next_board)):
                        for j in range(len(next_board[i])):
                            if next_board[i][j] == block_idx:
                                block_coords.append((i, j))
                    for coord in block_coords:
                        next_board[coord[0]][coord[1]] = -1
                    for coord in block_coords:
                        next_board[coord[0] + self.ENUM2DIR[dir][0]][coord[1] + self.ENUM2DIR[dir][1]] = block_idx

                    next_board_str = ''.join([''.join(['x' if i == -1 else str(self.__blocks[i].shape) for i in row]) for row in next_board])
                    if next_board_str in is_saw:
                        continue
                    is_saw.add(next_board_str)
                    que.append((next_board, step + 1, process + f'{block_idx}{self.ENUM2CHAR[dir]}'))

                    is_goal = True
                    for goal_coord in self.__goal_coords:
                        if next_board[goal_coord[0]][goal_coord[1]] != self.__goal_block:
                            is_goal = False
                    if is_goal:
                        return (step + 1, process + f'{block_idx}{self.ENUM2CHAR[dir]}')

            logging.debug(f'queue size: {len(que)}')

        return (None, None)

    def reset(self, surface: pygame.Surface, dirty_rects: list = []):
        logging.debug('board is reset.')
        self.__curr_answer_step = -1
        board_rect = pygame.Rect(self.__top_left[1], self.__top_left[0], self.__width, self.__height)
        dirty_rects.append(board_rect)
        pygame.draw.rect(surface, self.__bg_color, board_rect, border_radius=3)

        self.__board = copy.deepcopy(self.__init_board)
        for block in self.__blocks:
            block.reset()

        for i in range(len(self.__init_board)):
            for j in range(len(self.__init_board[i])):

                block_idx = self.__init_board[i][j]
                if block_idx == -1:
                    continue

                self.__blocks[block_idx].coords.append((i, j))

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
            self.__swap(block_idx, key)
            self.__curr_answer_step = -1

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

    def __get_rect(self, coord: tuple, is_connected: dict) -> pygame.Rect:
        i, j = coord
        top = self.__top_left[1] + i * self.__tile_size[1] + (0 if is_connected[pygame.K_UP] else self.__gap)
        left = self.__top_left[0] + j * self.__tile_size[0] + (0 if is_connected[pygame.K_LEFT] else self.__gap)
        width = self.__tile_size[0] - (0 if is_connected[pygame.K_LEFT] else self.__gap) - (0 if is_connected[pygame.K_RIGHT] else self.__gap)
        height = self.__tile_size[1] - (0 if is_connected[pygame.K_UP] else self.__gap) - (0 if is_connected[pygame.K_DOWN] else self.__gap)
        return pygame.Rect(left, top, width, height)

    def __swap(self, block_idx: int, key: int):
        logging.debug(f'block {block_idx} is swaiped to {self.ENUM2CHAR[key]}.')
        block = self.__blocks[block_idx]

        if logging.root.level == logging.DEBUG:
            [logging.debug(f'block {block_idx} [{coord}] is swapped to {self.ENUM2CHAR[key]}.') for coord in block.coords]

        for coord in block.coords:
            self.__board[coord[0]][coord[1]] = -1
        for coord in block.coords:
            self.__board[coord[0] + self.ENUM2DIR[key][0]][coord[1] + self.ENUM2DIR[key][1]] = block_idx
        block.coords = [(coord[0] + self.ENUM2DIR[key][0], coord[1] + self.ENUM2DIR[key][1]) for coord in block.coords]

        for coord in block.coords:
            is_connected = self.__is_connected(coord)
            rect = self.__get_rect(coord, is_connected)
            if not is_connected[pygame.K_UP] and not is_connected[pygame.K_LEFT]:
                self.__blocks[block_idx].next_top_left = [rect.top, rect.left]
            if not is_connected[pygame.K_DOWN] and not is_connected[pygame.K_RIGHT]:
                self.__blocks[block_idx].next_bottom_right = [rect.top + rect.height, rect.left + rect.width]
            logging.debug(f'block {block_idx} [{coord}] will be moved to {self.__blocks[block_idx].next_top_left}.')

        self.__is_moving = True
        self.__moving_block_idx = block_idx
        self.__moving_direction = self.ENUM2DIR[key]

    def __get_block_idx(self, cursor: list) -> int:
        if cursor is None:
            return None
        for i in range(self.__block_num):
            if cursor[0] < self.__blocks[i].curr_top_left[0] or cursor[0] > self.__blocks[i].curr_bottom_right[0]:
                continue
            if cursor[1] < self.__blocks[i].curr_top_left[1] or cursor[1] > self.__blocks[i].curr_bottom_right[1]:
                continue
            return i

    def __is_connected(self, coord: tuple, board: list = None) -> dict:
        if board is None:
            board = self.__board
        is_connected = dict()
        for key, value in self.ENUM2DIR.items():
            i, j = coord
            is_connected[key] = False
            if board[i][j] == -1:
                continue
            next_i = i + value[0]
            next_j = j + value[1]
            if next_j < 0 or next_j >= len(board[i]) or next_i < 0 or next_i >= len(board):
                continue
            if board[i][j] != board[next_i][next_j]:
                continue
            is_connected[key] = True
        return is_connected

    def __is_movable(self, block_idx, board: list = None):
        if board is None:
            board = self.__board
        is_movable = {pygame.K_UP: True, pygame.K_DOWN: True, pygame.K_RIGHT: True, pygame.K_LEFT: True}
        block_coords = list()
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == block_idx:
                    block_coords.append((i, j))
        is_connected = {coord: self.__is_connected(coord, board) for coord in block_coords}

        for coord, is_connected in is_connected.items():
            for key, value in is_movable.items():

                if is_connected[key]:
                    continue

                first = coord[0] + self.ENUM2DIR[key][0]
                second = coord[1] + self.ENUM2DIR[key][1]
                if first < 0 or first >= len(board):
                    is_movable[key] = False
                    continue
                if second < 0 or second >= len(board[0]):
                    is_movable[key] = False
                    continue

                is_movable[key] = value and board[first][second] == -1

        if logging.root.level == logging.DEBUG:
            [logging.debug(f'block {block_idx} is movable to {self.ENUM2DIR[key]}.') for key, value in is_movable.items() if value]
        if not any(is_movable.values()):
            logging.debug(f'block {block_idx} is not movable.')

        return is_movable
