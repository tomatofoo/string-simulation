import time
from numbers import Real
from typing import Self

import pygame as pg


class Particle(object):
    def __init__(self: Self,
                 mass: Real,
                 pos: pg.Vector2,
                 velocity: pg.Vector2,
                 accel: pg.Vector2) -> None:
        self._mass = mass
        self._pos = pg.Vector2(pos)
        self._velocity = pg.Vector2(velocity)
        self._accel = pg.Vector2(accel)

    @property
    def mass(self: Self) -> Real:
        return self._mass

    @mass.setter
    def mass(self: Self, value: Real) -> None:
        self._mass = value

    @property
    def pos(self: Self) -> None:
        return self._pos

    @pos.setter
    def pos(self: Self, value: pg.Vector2) -> None:
        self._pos = pg.Vector2(value)

    @property
    def velocity(self: Self) -> None:
        return self._velocity

    @velocity.setter
    def velocity(self: Self, value: pg.Vector2) -> None:
        self._velocity = pg.Vector2(value)

    @property
    def accel(self: Self) -> None:
        return self._accel

    @accel.setter
    def accel(self: Self, value: pg.Vector2) -> None:
        self._accel = pg.Vector2(value)

    def update(self: Self, rel_game_speed: Real) -> None:
        pass


class Game(object):

    _SCREEN_SIZE = (640, 480)
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 1

    def __init__(self: Self) -> None:
        pg.init()

        self._settings = {
            'vsync': 1,
        }
        self._screen = pg.display.set_mode(
            self._SCREEN_SIZE,
            flags=self._SCREEN_FLAGS,
            vsync=self._settings['vsync']
        )
        self._running = 0

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = delta_time * self._GAME_SPEED

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

