import random
from actions import Move, Shot, Scan
from ship import Ship
from vec2d import Vec2d


class UFO(Ship):
    next_target = None
    diameter = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movement_queue = [Move.DOWN, Move.LEFT, Move.UP, Move.RIGHT]
        if random.randint(0, 1):
            self.movement_queue = list(reversed(self.movement_queue))
        self.move_counter = random.randint(0, self.diameter)

    def action(self):
        self.move_counter += 1

        if self.next_target:
            # intensify forward firepower
            possible = [
                self.next_target + Vec2d(1, 0),
                self.next_target + Vec2d(-1, 0),
                self.next_target + Vec2d(0, 1),
                self.next_target + Vec2d(0, -1)]
            # TODO: expose in_range for later use
            possible = [p for p in possible if self.in_range(p)]
            self.next_target = None  # we always want to check if we killed
            if not possible:
                return random.choice(list(Move))
            return Shot(random.choice(possible), self)

        # No targets? Scan for them. And spin in circles.
        if self.move_counter < self.diameter:
            return Scan.SCAN
        else:
            self.move_counter = 0
            d = self.movement_queue[0]
            self.movement_queue.remove(d)
            self.movement_queue.append(d)
            return d

    def received_scan(self, discovered_objects):
        self.next_target = None
        for position, data in discovered_objects:
            if data != "UFO":
                self.next_target = position

    def broadcast(self):
        return "UFO"