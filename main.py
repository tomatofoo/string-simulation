import math
import time
from numbers import Real
from typing import Self

import pygame as pg


class Bob(object):
    def __init__(self: Self,
                 pivot: pg.Vector2,
                 mass: Real=1,
                 rel: pg.Vector2=(0, 1),
                 velocity: Real=0, # angular * length
                 net_force: Real=0) -> None:
        self._pivot = pivot
        self._mass = mass
        self.rel = pg.Vector2(rel)
        self._velocity = velocity
        self._net_force = net_force
        self._accel = self._net_force / self._mass

    @property
    def pivot(self: Self) -> pg.Vector2:
        return self._pivot

    @pivot.setter
    def pivot(self: Self, value: pg.Vector2) -> None:
        self._pivot = pg.Vector2(value)

    @property
    def mass(self: Self) -> Real:
        return self._mass

    @mass.setter
    def mass(self: Self, value: Real) -> None:
        self._mass = value

    @property
    def rel(self: Self) -> pg.Vector2:
        return self._rel

    @rel.setter
    def rel(self: Self, value: pg.Vector2) -> None:
        self._rel = pg.Vector2(value)
        self._length = self._rel.magnitude()
        self._pos = self._pivot + self._rel

    @property
    def pos(self: Self) -> pg.Vector2:
        return self._pivot + self._rel

    @property
    def angle(self: Self) -> Real:
        return self._rel.angle

    @property
    def angle_rad(self: Self) -> Real:
        return self._rel.angle_rad

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
    def velocity(self: Self) -> Real:
        return self._velocity

    @velocity.setter
    def velocity(self: Self, value: Real) -> None:
        self._velocity = value

    @property
    def net_force(self: Self) -> Real:
        return self._net_force

    @net_force.setter
    def net_force(self: Self, value: Real) -> None:
        self._net_force = value

    def update(self: Self, rel_game_speed: Real) -> None:
        # Velocity verlet
        self._accel = self._net_force / self._mass
        self._velocity += self._accel * rel_game_speed
        self._rel.rotate_rad_ip(self._velocity * self._length * rel_game_speed)


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
        
        # RENDERING
        self._SCALE = 32
        self._RADIUS = 4
        self._COLORS = {
            'arm': (255, 0, 0),
            'bob': (255, 255, 255),
            'pivot': (0, 255, 0),
        }
        
        # PHYSICS
        self._GRAVITY = 9.8
        self._AMOUNT = 32 # amount of pendulums
        self._LENGTH = 8 / self._AMOUNT
        
        # Misc.
        self._pivot = pg.Vector2(self._SCREEN_SIZE) / 2 / self._SCALE
        self._reset()

    def _reset(self: Self) -> None:
        self._bobs = []
        pos = self._pivot.copy()
        for i in range(self._AMOUNT):
            bob = Bob(pivot=pos, rel=pg.Vector2(0, self._LENGTH).rotate(45))
            pos = bob.pos
            self._bobs.append(bob)

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        while self._running:
            delta_time = min(time.time() - start_time, 1 / 15)
            start_time = time.time()

            rel_game_speed = delta_time * self._GAME_SPEED

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self._reset()

            # Update
            pos = self._pivot
            net_force = 0
            for dex, bob in enumerate(self._bobs):
                net_force += self._GRAVITY * bob.mass * math.cos(bob.angle_rad) * 0.5
                bob.net_force = self._GRAVITY * bob.mass * math.cos(bob.angle_rad) + net_force
                bob.rel = (bob.pos - pos).normalize() * self._LENGTH
                bob.pivot = pos
                bob.update(rel_game_speed)
                bob.velocity *= 0.6**rel_game_speed
                pos = bob.pos

            # Render
            self._screen.fill((0, 0, 0))
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
                )"""
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

