"""AI Challenge: Space Dogfight!

In this challenge, players compete to build fleets of spaceships that hunt down
and destroy their enemies.

Each player subclasses `Ship` and implements the `action`, `received_scan` and
`broadcast` methods. Players can also *add* extra code as necessary, but any
attributes starting with `_` are off-limits! (Yes, that means "dunder"-methods
are no fair!) No static/global/module-level variables are allowed; use the
`broadcast` and `received_scan` methods for inter-ship communication.

The universe step first readies all the player's actions, then executes them in
the following priority:
 * Move:  Begin moving in this direction. This is space, so choosing something
          other than move will leave you moving in that direction! Crashing
          into anything will destroy both objects.
 * (All ships move at this point.)
 * Shoot: Attack the specified location.
 * Scan:  Reveals the `broadcast` data of all objects within 5 squares. Things
          like asteroids will return `None` as broadcast data but will be
          discovered.

Raising an exception anywhere in your code means the ship tears itself apart
in a dramatic explosive decompression! (You're dead.)

########################
# COOL STUFF!
########################
Player must also submit a tiny 8x8 pixel sprite of their ship. For the cool
rendering, of course!
"""

import pyglet
from universe import Universe
import asyncio

# Get all the ships
from contenders.asteroid import Asteroid
from contenders.foo_fighter import FooFighter
from contenders.ufo import UFO
CONTENDERS = [Asteroid, FooFighter, UFO]


def run_pyglet(loop):
    """Use asyncio as the main event loop for pyglet."""
    pyglet.clock.tick()
    for w in pyglet.app.windows:
        w.switch_to()
        w.dispatch_events()
        w.flip()
        if w.has_exit:
            loop.stop()
    loop.call_later(1/30., run_pyglet, loop)


TICK_SPEED = 1/60


def universe_tick(universe, loop, window):
    universe.update()
    window.clear()
    universe.render()
    loop.call_later(TICK_SPEED, universe_tick, universe, loop, window)


def main():
    size = 100

    # HEADS UP! Enabling vsync on Linux will cause the app to freeze.
    window = pyglet.window.Window(width=size * 8, height=size * 8, vsync=False)

    universe = Universe(size, CONTENDERS)
    event_loop = asyncio.get_event_loop()
    event_loop.call_soon(run_pyglet, event_loop)
    event_loop.call_soon(universe_tick, universe, event_loop, window)
    event_loop.run_forever()
    event_loop.close()

if __name__ == "__main__":
    main()
