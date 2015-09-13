import random
from collections import deque

from actions import Move, Shot
from ship import Ship
from vec2d import Vec2d


class Bomber(Ship):
    have_moved = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        shots = []
        for i in range(30):
            x, y = Vec2d(0, 9).rotated(12 * i)
            shots.append(Vec2d(int(x), int(y)))
        self.shots = deque(shots)
        self.shots.rotate(random.randint(-12, 12))

    def action(self):
        if not self.have_moved:
            self.have_moved = True
            return random.choice(list(Move))
        shot = self.shots.pop()
        self.shots.appendleft(shot)
        return Shot(self.position + shot, self)

    def received_scan(self, discovered_objects):
        pass

    def broadcast(self):
        return "BOMBER"
