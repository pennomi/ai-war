from actions import Move
import pyglet
from vec2d import Vec2d


class Ship:
    def __init__(self, position: Vec2d):
        self.position = position
        self.last_hit = 0
        self.requested_action = None
        self.direction = Move.UP
        self.dead = False

        # rendering stuff
        image = pyglet.image.load('images/{}.png'.format(
            self.__class__.__name__))
        self.sprite = pyglet.sprite.Sprite(
            image, x=self.position.x, y=self.position.y)

    def action(self):
        raise NotImplementedError("Please implement `action`")

    def received_scan(self, discovered_objects):
        raise NotImplementedError("Please implement `received_scan`")

    def broadcast(self):
        raise NotImplementedError("Please implement `broadcast`")