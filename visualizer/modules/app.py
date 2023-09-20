import json
# import logging
from pathlib import Path
import pygame
import re
import sys

import modules.board
import modules.gradator


class App:

    CONFIG_FILEPATH = str(Path(__file__).resolve().parents[1] / 'config' / 'config.json')

    def __init__(self):
        # init pygame
        pygame.init()
        pygame.display.set_caption('Visualizer')

        # load config
        with open(self.CONFIG_FILEPATH, 'r') as f:
            text = f.read()
        config = json.loads(re.sub(r'/\*[\s\S]*?\*/|//.*', '', text))
        self.__fps = config['fps']
        self.__tile_size = tuple(config['tile_size'].values())
        self.__padding = (int(self.__tile_size[0] / 2), int(self.__tile_size[1] / 2))

        # load board
        color_gradator = modules.gradator.Gradator(tuple(config['color']['block'][0]), tuple(config['color']['block'][1]))
        block_colors = color_gradator.get_colors(max([max(idxs) for idxs in config['board']]) + 1)
        block_colors.append(config['color']['space'])

        # init surface & dirty rects
        screen_width = len(config['board'][0]) * self.__tile_size[0] + self.__padding[0] * 2
        screen_height = len(config['board']) * self.__tile_size[1] + self.__padding[1] * 2
        self.__surface = pygame.display.set_mode((screen_width, screen_height))
        self.__surface.fill(config['color']['bg'])
        self.__dirty_rects = list()

        self.__cursor = {  # [y, x]
            pygame.MOUSEMOTION: [-1, -1],
            pygame.MOUSEBUTTONDOWN: [-1, -1],
            pygame.MOUSEBUTTONUP: [-1, -1],
        }
        self.__swapping_keys = (
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_RIGHT,
            pygame.K_LEFT,
            pygame.K_w,
            pygame.K_s,
            pygame.K_d,
            pygame.K_a,
        )

        pygame.draw.rect(
            self.__surface,
            block_colors[-1],
            pygame.Rect(
                self.__padding[0],
                self.__padding[1],
                screen_width - self.__padding[0] * 2,
                screen_height - self.__padding[1] * 2
            ),
            border_radius=config['radius'],
        )
        self.__board = modules.board.Board(
            config['board'],
            config['block_types'],
            config['goal'],
            self.__tile_size,
            block_colors,
            self.__surface,
            self.__padding,
            block_gap=config['gap'],
            corner_radius=config['radius'],
            moving_speed=config['speed']
        )

        self.__clock = pygame.time.Clock()
        print('game starts.')
        pygame.display.update()

    def run(self):
        while (True):
            self.__mainloop()

    def __mainloop(self):
        pygame.display.update(self.__dirty_rects)
        self.__dirty_rects.clear()

        cursor, event_type, key = None, None, None
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                self.__cursor[pygame.MOUSEMOTION][0], self.__cursor[pygame.MOUSEMOTION][1] = event.pos[1], event.pos[0]
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.__cursor[pygame.MOUSEBUTTONDOWN][0], self.__cursor[pygame.MOUSEBUTTONDOWN][1] = event.pos[1], event.pos[0]
            if event.type == pygame.MOUSEBUTTONUP:
                self.__cursor[pygame.MOUSEBUTTONUP][0], self.__cursor[pygame.MOUSEBUTTONUP][1] = event.pos[1], event.pos[0]

            if event.type == pygame.KEYDOWN and event.key in self.__swapping_keys:
                cursor, event_type, key = self.__cursor[pygame.MOUSEMOTION], event.type, self.__get_direction(event.key)
            elif event.type == pygame.MOUSEBUTTONUP:
                cursor, event_type, key = self.__cursor[pygame.MOUSEBUTTONDOWN], event.type, self.__get_direction()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__board.reset(self.__surface, self.__dirty_rects)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                self.__board.play_answer()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.__quit()
            if event.type == pygame.QUIT:
                self.__quit()

        self.__board.update(self.__surface, self.__dirty_rects, cursor, event_type, key)
        # logging.debug(f'fps: {self.__clock.get_fps():.2f}')
        self.__clock.tick(self.__fps)

    def __quit(self):
        pygame.quit()
        sys.exit()

    def __get_direction(self, key: int = None) -> int:
        if key in (pygame.K_UP, pygame.K_w):
            return pygame.K_UP
        if key in (pygame.K_DOWN, pygame.K_s):
            return pygame.K_DOWN
        if key in (pygame.K_RIGHT, pygame.K_d):
            return pygame.K_RIGHT
        if key in (pygame.K_LEFT, pygame.K_a):
            return pygame.K_LEFT

        dist = [
            self.__cursor[pygame.MOUSEBUTTONUP][0] - self.__cursor[pygame.MOUSEBUTTONDOWN][0],
            self.__cursor[pygame.MOUSEBUTTONUP][1] - self.__cursor[pygame.MOUSEBUTTONDOWN][1]
        ]
        if abs(dist[0]) > abs(dist[1]):
            return pygame.K_DOWN if dist[0] > 0 else pygame.K_UP
        elif abs(dist[0]) < abs(dist[1]):
            return pygame.K_RIGHT if dist[1] > 0 else pygame.K_LEFT
        else:
            return None
