import math
import time
from numbers import Real
from typing import Self

import pygame as pg


class Particle(object):
    def __init__(self: Self,
                 mass: Real,
                 pos: pg.Vector2,
                 velocity: pg.Vector2=(0, 0),
                 net_force: pg.Vector2=(0, 0),
                 friction: Real=1) -> None:

        self._mass = mass
        self._pos = pg.Vector2(pos)
        self._velocity = pg.Vector2(velocity)
        self._net_force = pg.Vector2(net_force)
        self._accel = self._net_force / self._mass
        self._friction = friction

    def __getitem__(self: Self, item: int) -> None:
        return self._pos[item]

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

    @property
    def friction(self: Self) -> Real:
        return self._friction

    @friction.setter
    def friction(self: Self, value: Real) -> None:
        self._friction = value

    def update(self: Self, rel_game_speed: Real) -> None:
        # For some reason Euler integration works best????
        self._accel = self._net_force / self._mass
        self._velocity += self._accel * rel_game_speed
        self._pos += self._velocity * rel_game_speed
        self._velocity *= self._friction**rel_game_speed


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
        self._RADIUS = 4
        self._COLORS = {
            'fill': (0, 0, 0),
            'arm': (255, 0, 0),
            'bob': (255, 255, 255),
            'pivot': (0, 255, 0),
        }
        
        # PHYSICS
        self._GRAVITY = pg.Vector2(0, 1000)
        self._AMOUNT = 10 # amount of pendulums
        self._LENGTH = 100 / self._AMOUNT
        self._MASS = 1
        self._K = 1000
        
        # Misc.
        self._pivot = Particle(1, pg.Vector2(self._SCREEN_SIZE) / 2)
        self._reset()

    def _reset(self: Self) -> None:
        vector = pg.Vector2(self._LENGTH, 0).rotate(45)
        self._bobs = []
        for i in range(self._AMOUNT):
            bob = Particle(
                mass=self._MASS,
                pos=self._pivot.pos + (i + 1) * vector,
                friction=0.8,
            )
            self._bobs.append(bob)

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        clicking = 0

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = delta_time * self._GAME_SPEED
            
            # EVENTS
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self._reset()
                elif event.type == pg.MOUSEMOTION and clicking:
                    self._pivot.pos += event.rel
                elif event.type == pg.MOUSEBUTTONDOWN:
                    clicking = self._pivot.pos.distance_to(event.pos) < self._RADIUS
                elif event.type == pg.MOUSEBUTTONUP:
                    clicking = 0

            pg.display.set_caption(str(1 / delta_time) if delta_time else 'inf')
            
            # UPDATE
            force = pg.Vector2(0, 0)
            for i in range(self._AMOUNT - 1, -1, -1):
                bob = self._bobs[i]
                next = self._bobs[i - 1] if i else self._pivot
                spring = bob.pos - next.pos
                restoring = ( # F = -kx
                    -self._K
                    * (spring.magnitude() - self._LENGTH)
                    * spring.normalize()
                )
                bob.net_force = self._GRAVITY * bob.mass + restoring - force
                force = restoring
                bob.update(rel_game_speed)

            # RENDER
            self._screen.fill(self._COLORS['fill'])
            pg.draw.circle(
                self._screen,
                self._COLORS['pivot'],
                self._pivot.pos,
                self._RADIUS,
            )
            prev = self._pivot
            for bob in self._bobs:
                pg.draw.line(
                    self._screen,
                    self._COLORS['arm'],
                    prev.pos,
                    bob.pos,
                )
                pg.draw.circle(
                    self._screen,
                    self._COLORS['bob'],
                    bob.pos,
                    self._RADIUS,
                )
                prev = bob
            
            pg.display.update()

        pg.quit()

if __name__ == '__main__':
    Game().run()

