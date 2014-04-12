import random
from actions import Move, Shot, Scan
import pyglet
from vec2d import Vec2d

SCAN_DISTANCE = 5
_SCAN_DISTANCE_SQ = SCAN_DISTANCE ** 2


class Universe:
    def __init__(self, size, contender_classes):
        self.size = size
        r = random.randint
        self.ships = []
        for shiptype in contender_classes:
            self.ships += [shiptype(Vec2d(r(0, size-1), r(0, size-1)))
                           for _ in range(10)]

    def update(self):
        for ship in self.ships:
            ship.requested_action = ship.action()
        # direction change requests first!
        for ship in [s for s in self.ships if s.requested_action in Move]:
            ship.direction = ship.requested_action
        # move all ships
        for ship in self.ships:
            self.move_ship(ship)
        # shots
        self.shots = []
        for ship in (s for s in self.ships
                     if isinstance(s.requested_action, Shot)):
            shot = ship.requested_action
            # check that shot is within range
            if self.in_range(shot.owner.position, shot.position):
                self.shots.append(shot)
        # remove all dead ships (only sort of efficiently)
        self.explosions = []  # cause it'll look cool
        for i, ship in enumerate(self.ships):
            for ship2 in self.ships[i+1:] + self.shots:
                if ship.position == ship2.position:
                    ship.dead = True
                    ship2.dead = True
                    self.explosions.append(ship.position)
        [self.ships.remove(ship) for ship in self.ships if ship.dead]
        # scan only if we're not dead
        self.scan_bubbles = []
        for ship in (s for s in self.ships if s.requested_action in Scan):
            ship.received_scan(self.perform_scan(ship))

    def render(self):
        #ship_batch = pyglet.batch.Batch()

        #tiles = [["."] * self.size for _ in range(self.size)]

        #def set_tile(position, char):
        #    x, y = position
        #    x %= self.size
        #    y %= self.size
        #    tiles[y][x] = char

        for ship in self.ships:
            ship.sprite.position = tuple(ship.position * 8)
            ship.sprite.draw()
            #set_tile(ship.position, ship.letter())
        for explosion in self.explosions:
            pass #set_tile(explosion, "*")
        for shot in self.shots:
            pass #set_tile(shot.position, "|")
        #print('_' * 100)
        #print("\n".join(["".join(_) for _ in reversed(tiles)]))

    def in_range(self, a, b):
        # The points wrap around the universe
        # TODO: Yeah, we need a 2D vector class. This is just ugly.
        if a.x - b.x > self.size / 2:
            b += Vec2d(self.size, 0)
        if a.x - b.x < -self.size / 2:
            b -= Vec2d(self.size, 0)
        if a.y - b.y > self.size / 2:
            b += Vec2d(0, self.size)
        if a.y - b.y < -self.size / 2:
            b -= Vec2d(0, self.size)
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= _SCAN_DISTANCE_SQ

    def move_ship(self, ship):
        if ship.direction == Move.UP:
            ship.position += Vec2d(0, 1)
        elif ship.direction == Move.DOWN:
            ship.position -= Vec2d(0, 1)
        elif ship.direction == Move.RIGHT:
            ship.position += Vec2d(1, 0)
        elif ship.direction == Move.LEFT:
            ship.position -= Vec2d(1, 0)
        ship.position %= self.size

    def perform_scan(self, ship):
        """Return the position and broadcast data of all ships in range."""
        scan_data = []
        for s in self.ships:
            if self.in_range(s.position, ship.position) and not s is ship:
                scan_data.append((s.position, s.broadcast()))

        # If we want to render the scanners, we'll need to render them
        centers = [
            ship.position,
            ship.position + Vec2d(self.size, 0),
            ship.position + Vec2d(0, self.size),
            ship.position + Vec2d(self.size, self.size),
            ship.position + Vec2d(-self.size, 0),
            ship.position + Vec2d(0, -self.size),
            ship.position + Vec2d(-self.size, -self.size),
        ]
        self.scan_bubbles.extend(centers)

        return scan_data