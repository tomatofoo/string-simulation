import math
import time
from numbers import Real
from typing import Self

import pygame as pg


class Particle(object):
    def __init__(self: Self,
                 mass: Real=1,
                 pos: pg.Vector2=(0, 0),
                 velocity: pg.Vector2=(0, 0),
                 net_force: pg.Vector2=(0, 0)) -> None:
        self._mass = mass
        self._pos = pg.Vector2(pos)
        self._velocity = pg.Vector2(velocity)
        self._net_force = pg.Vector2(net_force)
        self._accel = self._net_force / self._mass

    @property
    def mass(self: Self) -> Real:
        return self._mass

    @mass.setter
    def mass(self: Self, value: Real) -> None:
        self._mass = value

    @property
    def pos(self: Self) -> pg.Vector2:
        return self._pos

    @pos.setter
    def pos(self: Self, value: pg.Vector2) -> None:
        self._pos = pg.Vector2(value)

    @property
    def x(self: Self) -> Real:
        return self._pos[0]

    @x.setter
    def x(self: Self, value: Real) -> None:
        self._pos[0] = value

    @property
    def y(self: Self) -> Real:
        return self._pos[1]

    @y.setter
    def y(self: Self, value: Real) -> None:
        self._pos[1] = value

    @property
    def velocity(self: Self) -> pg.Vector2:
        return self._velocity

    @velocity.setter
    def velocity(self: Self, value: pg.Vector2) -> None:
        self._velocity = pg.Vector2(value)

    @property
    def net_force(self: Self) -> pg.Vector2:
        return self._net_force

    @net_force.setter
    def net_force(self: Self, value: pg.Vector2) -> None:
        self._net_force = pg.Vector2(value)

    def update(self: Self, rel_game_speed: Real) -> None:
        # Velocity verlet
        self._velocity += 0.5 * self._accel * rel_game_speed
        self._pos += self._velocity * rel_game_speed
        self._accel = self._net_force / self._mass
        self._velocity += 0.5 * self._accel * rel_game_speed


class Game(object):

    _SCREEN_SIZE = (640, 480)
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 1

    def __init__(self: Self) -> None:
        pg.init()

        self._settings = {
            'vsync': 0,
        }
        self._screen = pg.display.set_mode(
            self._SCREEN_SIZE,
            flags=self._SCREEN_FLAGS,
            vsync=self._settings['vsync']
        )
        self._running = 0
        
        # RENDERING
        self._SCALE = 32
        self._RADIUS = 4
        self._COLORS = {
            'arm': (255, 0, 0),
            'bob': (255, 255, 255),
            'pivot': (0, 255, 0),
        }
        
        # PHYSICS
        self._GRAVITY = 9.8067
        self._AMOUNT = 1 # amount of pendulums
        self._LENGTH = 2
        
        # Misc.
        self._pivot = pg.Vector2(self._SCREEN_SIZE) / 2 / self._SCALE
        self._bobs = []
        for i in range(1, self._AMOUNT + 1):
            self._bobs.append(Particle(
                pos=self._pivot + pg.Vector2(0, self._LENGTH * i).rotate(45),
            ))

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
            self._screen.fill((0, 0, 0))

            # Update
            pos = self._pivot.copy()
            for bob in self._bobs:
                gravity = pg.Vector2(0, self._GRAVITY * bob.mass)
                tension = -gravity.project(bob.pos - pos)
                bob.net_force = gravity + tension
                bob.update(rel_game_speed)

                # Constraints
                pos += (bob.pos - pos).normalize() * self._LENGTH
                bob.pos = pos

            # Render
            pos = self._pivot
            for bob in self._bobs:
                pg.draw.line(
                    self._screen,
                    self._COLORS['arm'],
                    pos * self._SCALE,
                    bob.pos * self._SCALE,
                )
                """
                pg.draw.circle(
                    self._screen,
                    self._COLORS['bob'],
                    bob.pos * self._SCALE,
                    self._RADIUS,
                )
                """
                pos = bob.pos
            pg.draw.circle(
                self._screen,
                self._COLORS['pivot'],
                self._pivot * self._SCALE,
                self._RADIUS,
            )
            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

