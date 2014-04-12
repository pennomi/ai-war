import random
from actions import Move, Shot, Scan
from ship import Ship
from vec2d import Vec2d


class FooFighter(Ship):
    next_target = None

    def action(self):
        if self.next_target:
            # intensify forward firepower
            possible = [
                self.next_target + Vec2d(1, 0),
                self.next_target + Vec2d(-1, 0),
                self.next_target + Vec2d(0, 1),
                self.next_target + Vec2d(0, -1)]
            # TODO: expose in_range for later use
            #possible = [p for p in possible if in_range(p, self.position)]
            self.next_target = None  # we always want to check if we killed
            if not possible:
                return random.choice(list(Move))
            return Shot(random.choice(possible), self)

        # No targets? Mill about randomly and look for them
        should_scan = random.uniform(0, 1) >= .25
        if should_scan:
            return Scan.SCAN
        else:
            return random.choice(list(Move))

    def received_scan(self, discovered_objects):
        self.next_target = None
        for position, data in discovered_objects:
            if data != "FOO FIGHTER":  # Don't want to shoot my own ships!
                self.next_target = position

    def broadcast(self):
        return "FOO FIGHTER"