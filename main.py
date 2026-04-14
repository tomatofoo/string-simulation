import math
import time
from numbers import Real
from typing import Self

import pygame as pg


def normalize_angle(angle: Real) -> Real:
    return (angle + 180) % 360 - 180


class Particle(object):
    def __init__(self: Self,
                 mass: Real,
                 pos: pg.Vector2,
                 velocity: pg.Vector2=(0, 0),
                 net_force: pg.Vector2=(0, 0),
                 friction: Real=1) -> None:

        self._mass = mass
        self._pos = pg.Vector2(pos)
        self._prev = self._pos.copy()
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
    _TIMESTEP = 1 / 240

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
        pg.display.set_caption('String Simulation')
        self._running = 0

        # RENDERING
        self._RADIUS = 4
        self._THICKNESS = 4
        self._COLORS = {
            'fill': (0, 0, 0),
            'arm': (255, 0, 0),
            'bob': (255, 255, 255),
            'obstruction': (0, 255, 255),
            'pivot': (0, 255, 0),
            'text': (255, 255, 255),
        }

        # PHYSICS
        self._MOVEMENT = 100 # multiplier of mouse cursor movement
        self._FRICTION = 0.2 # friction multiplier
        self._GRAVITY = pg.Vector2(0, 1000)
        self._AMOUNT = 24 # amount of pendulums
        self._LENGTH = 100 / self._AMOUNT # length of each pendulum
        self._MASS = 0.5
        self._K = 2000
        self._OBSTRUCTION_RADIUS = 20
        
        # Misc.
        self._pivot = Particle(1, pg.Vector2(self._SCREEN_SIZE) / 2)
        self._movement = pg.Vector2(0, 0)
        self._reset()

        self._font = pg.font.SysFont('Arial', 16)
        self._info = self._font.render(
            '<r> to reset the rope\n'
            '<s> to show / hide spring bobs\n'
            '<o> to enable / disable obstruction\n'
            'drag pivot with mouse cursor',
            1,
            self._COLORS['text'],
        )

        self._show_bobs = 0 # not on purpose i swear
        self._obstruction = 0

    def _reset(self: Self) -> None:
        vector = pg.Vector2(self._LENGTH, 0)
        self._bobs = []
        for i in range(self._AMOUNT):
            bob = Particle(
                mass=self._MASS,
                pos=self._pivot.pos + (i + 1) * vector,
                friction=self._FRICTION,
            )
            self._bobs.append(bob)
        # positions; for interpolation
        self._last = [bob.pos.copy() for bob in self._bobs]

    def _update_bobs(self: Self,
                     rel_game_speed: Real,
                     mouse_pos: pg.Vector2) -> None:

        # https://www.youtube.com/watch?v=0WaDxYuD9S8
        antirestoring = pg.Vector2(0, 0)
        for i in range(self._AMOUNT - 1, -1, -1):
            bob = self._bobs[i]
            next = self._bobs[i - 1] if i else self._pivot
            spring = bob.pos - next.pos
            restoring = ( # F = -kx
                -self._K
                * (spring.magnitude() - self._LENGTH)
                * spring.normalize()
            )
            bob.net_force = (
                self._movement
                + self._GRAVITY * bob.mass
                + restoring
                + antirestoring
            )
            antirestoring = -restoring

            if (self._obstruction
                and bob.pos.distance_to(mouse_pos) < self._OBSTRUCTION_RADIUS):
                vector = bob.pos - mouse_pos
                # make sure that force is against ball using vector angle
                if abs(normalize_angle(bob.net_force.angle_to(vector))) > 90:
                    vector.scale_to_length(self._OBSTRUCTION_RADIUS)
                    bob.pos = mouse_pos + vector
                    # normal force
                    bob.net_force += -bob.net_force.project(vector)

            bob.update(rel_game_speed)
        
    def _render(self: Self, accumulator: Real, mouse_pos: pg.Vector2) -> None:
        t = accumulator / self._TIMESTEP

        self._screen.fill(self._COLORS['fill'])
        if self._obstruction:
            pg.draw.circle(
                self._screen,
                self._COLORS['obstruction'],
                pg.mouse.get_pos(),
                self._OBSTRUCTION_RADIUS,
            )
        prev = self._pivot.pos
        for dex, bob in enumerate(self._bobs):
            # Interpolation
            pos = self._last[dex].lerp(bob.pos, t)
            pg.draw.line(
                self._screen,
                self._COLORS['arm'],
                prev,
                pos,
                self._THICKNESS,
            )
            if self._show_bobs:
                pg.draw.circle(
                    self._screen,
                    self._COLORS['bob'],
                    pos,
                    self._RADIUS,
                )
            prev = pos
        pg.draw.circle(
            self._screen,
            self._COLORS['pivot'],
            self._pivot.pos,
            self._RADIUS,
        )
        self._screen.blit(self._info, (0, 0))

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()
        accumulator = 0 # https://www.gafferongames.com/post/fix_your_timestep/
        self._update_bobs(self._TIMESTEP, pg.mouse.get_pos())
        # ^ so simulation is one step ahead; accounts for interpolation

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
                    elif event.key == pg.K_s:
                        self._show_bobs = not self._show_bobs
                    elif event.key == pg.K_o:
                        self._obstruction = not self._obstruction
                elif (
                    event.type == pg.MOUSEBUTTONDOWN
                    and self._pivot.pos.distance_to(event.pos) < self._RADIUS
                ):
                    clicking = 1
                elif event.type == pg.MOUSEBUTTONUP:
                    clicking = 0
            
            # UPDATE
            mouse_pos = pg.Vector2(pg.mouse.get_pos())
            mouse_rel = pg.Vector2(pg.mouse.get_rel())
            if clicking: # not using pg.MOUSEMOTION on purpose
                self._pivot.pos += mouse_rel
                for bob in self._bobs:
                    bob.pos += (0, 0)
                self._movement.update(mouse_rel * self._MOVEMENT)
            else:
                self._movement.update(0, 0)
            
            accumulator += rel_game_speed
            while accumulator >= self._TIMESTEP:
                rel_game_speed = self._TIMESTEP
                accumulator -= rel_game_speed
                self._last = [bob.pos.copy() for bob in self._bobs]
                self._update_bobs(rel_game_speed, mouse_pos)

            # RENDER
            self._render(accumulator, mouse_pos)
            pg.display.update()

        pg.quit()

if __name__ == '__main__':
    Game().run()

