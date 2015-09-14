import random
from actions import Move, Shot, Scan
import pyglet
from pyglet import gl
from vec2d import Vec2d

SCAN_DISTANCE = 5
_SCAN_DISTANCE_SQ = SCAN_DISTANCE ** 2


def _velocity_and_direction(ship):
    if ship.direction == Move.UP:
        return Vec2d(0, 1), 0
    elif ship.direction == Move.DOWN:
        return Vec2d(0, -1), 180
    elif ship.direction == Move.RIGHT:
        return Vec2d(1, 0), 90
    elif ship.direction == Move.LEFT:
        return Vec2d(-1, 0), -90


def normalize(v):
    v = Vec2d(v)
    if v.x < 0:
        v.x += 100
    elif v.x >= 100:
        v.x -= 100
    if v.y < 0:
        v.y += 100
    elif v.x >= 100:
        v.y -= 100
    return v


def continuous_laser(start, end):
    start = normalize(start)
    end = normalize(end)
    dv = end - start
    seen = {(start.x, start.y)}
    hit_tiles = list()
    for i in range(1, 100):
        dv.length = i * .1
        if dv.length > (end - start).length:
            break
        v = start + dv
        t = (int(v.x), int(v.y))
        hit_tiles.append(t)
    seen_add = seen.add
    return [Vec2d(*x) for x in hit_tiles if not (x in seen or seen_add(x))]


# noinspection PyBroadException
class Universe:
    shots = []
    explosions = []
    scans = []

    def __init__(self, size, contender_classes):
        self.size = size
        r = random.randint
        self.ships = []
        for shiptype in contender_classes:
            self.ships += [shiptype(self, Vec2d(r(0, size - 1), r(0, size - 1)))
                           for _ in range(10)]

        # Make something we can draw for the scanner
        self.scanner_model = []
        for i in range(30):
            self.scanner_model.append(Vec2d(0, SCAN_DISTANCE).rotated(12 * i))

    def update(self):
        # get all the orders
        for ship in self.ships:
            ship.requested_action = ship.action()

        # direction change requests first!
        for ship in self.ships:
            if ship.requested_action in Move:
                ship.direction = ship.requested_action

        # move all ships
        for ship in self.ships:
            self.move_ship(ship)

        # shots
        self.shots.clear()
        for ship in self.ships:
            if not isinstance(ship.requested_action, Shot):
                continue
            shot = ship.requested_action
            # check that shot is within range
            if self.in_range(shot.owner.position, shot.position, laser=True):
                shots = [Shot(p, shot.owner) for p in continuous_laser(shot.owner.position, shot.position)]
                self.shots.extend(shots)

        # remove all dead ships (only sort of efficiently)
        self.explosions.clear()
        for i, ship in enumerate(self.ships):
            # Iterate over ships AND shots to see if they overlap
            for ship2 in self.ships[i + 1:] + self.shots:
                if ship.position == ship2.position:
                    ship.dead = True
                    ship2.dead = True
                    self.explosions.append(ship.position)
        [self.ships.remove(ship) for ship in self.ships if ship.dead]

        # scan only if we're not dead
        self.scans.clear()
        for ship in self.ships:
            if ship.requested_action not in Scan:
                continue
            try:
                ship.received_scan(self.perform_scan(ship))
                self.scans.append(ship.position)
            except Exception:
                ship.dead = True

    def render(self):
        # draw scans
        gl.glColor3f(0, 0.2, 0.2)
        for scan in self.scans:
            vertices = [
                ((scan.x + p.x) * 8 + 4, (scan.y + p.y) * 8 + 4) for p in self.scanner_model
            ]
            vertices = tuple(item for sublist in vertices for item in sublist)
            pyglet.graphics.draw(
                int(len(vertices) / 2), pyglet.gl.GL_LINES,
                ('v2f', vertices)
            )

        # draw ships
        for ship in self.ships:
            ship.sprite.position = ship.position * 8 + Vec2d(4, 4)
            ship.sprite.draw()
        gl.glColor3f(1, 1, 0)
        # draw explosions
        for explosion in self.explosions:
            gl.glPointSize(8.0)
            pyglet.graphics.draw(
                1, pyglet.gl.GL_POINTS,
                ('v2i', (explosion.x * 8 + 4, explosion.y * 8 + 4))
            )
        # draw laser lines
        for shot in self.shots:
            lasers = continuous_laser(shot.owner.position, shot.position)
            vertices = [
                (p.x * 8 + 4, p.y * 8 + 4) for p in lasers
            ]
            vertices = tuple(item for sublist in vertices for item in sublist)

            gl.glColor3f(1, 0, 0)
            pyglet.graphics.draw(
                int(len(vertices) / 2), pyglet.gl.GL_LINE_LOOP,
                ('v2i', vertices)
            )

    def in_range(self, a, b, laser=False):
        distance = (SCAN_DISTANCE * 2) ** 2 if laser else _SCAN_DISTANCE_SQ
        a, b = Vec2d(a), Vec2d(b)  # copy
        # The points wrap around the universe
        if a.x - b.x > self.size / 2:
            b += Vec2d(self.size, 0)
        if a.x - b.x < -self.size / 2:
            b -= Vec2d(self.size, 0)
        if a.y - b.y > self.size / 2:
            b += Vec2d(0, self.size)
        if a.y - b.y < -self.size / 2:
            b -= Vec2d(0, self.size)
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= distance

    def move_ship(self, ship):
        velocity, direction = _velocity_and_direction(ship)
        ship.position += velocity
        ship.sprite.rotation = direction
        ship.position %= self.size

    def perform_scan(self, ship):
        """Return the position and broadcast data of all ships in range."""
        scan_data = []
        for s in self.ships:
            if self.in_range(s.position, ship.position) and s is not ship:
                scan_data.append((s.position, s.broadcast()))
        return scan_data
