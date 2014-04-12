import random
from actions import Move
from ship import Ship


class Asteroid(Ship):
    def action(self):
        try:
            return self.preferred_direction
        except AttributeError:
            self.preferred_direction = random.choice(list(Move))
            return self.preferred_direction

    def broadcast(self):
        return None