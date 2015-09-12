from actions import Move
import pyglet
from vec2d import Vec2d

# TODO: Duplicated from universe.py
SCAN_DISTANCE = 5
_SCAN_DISTANCE_SQ = SCAN_DISTANCE ** 2


class Ship:
    def __init__(self, universe, position: Vec2d):
        self.universe_size = universe.size
        self.position = position
        self.last_hit = 0
        self.requested_action = None
        self.direction = Move.UP
        self.dead = False

        # rendering stuff
        image = pyglet.image.load('images/{}.png'.format(
            self.__class__.__name__))
        image.anchor_x, image.anchor_y = 4, 4
        self.sprite = pyglet.sprite.Sprite(
            image, x=self.position.x, y=self.position.y)

    def in_range(self, a):
        a, b = Vec2d(a), Vec2d(self.position)  # copy
        # The points wrap around the universe
        if a.x - b.x > self.universe_size / 2:
            b += Vec2d(self.universe_size, 0)
        if a.x - b.x < -self.universe_size / 2:
            b -= Vec2d(self.universe_size, 0)
        if a.y - b.y > self.universe_size / 2:
            b += Vec2d(0, self.universe_size)
        if a.y - b.y < -self.universe_size / 2:
            b -= Vec2d(0, self.universe_size)
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= _SCAN_DISTANCE_SQ

    def action(self):
        raise NotImplementedError("Please implement `action`")

    def received_scan(self, discovered_objects):
        raise NotImplementedError("Please implement `received_scan`")

    def broadcast(self):
        raise NotImplementedError("Please implement `broadcast`")