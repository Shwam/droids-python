#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import random
import copy
import collections
from sets import Set

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "FreakBot"

  @staticmethod
  def password():
    return "password"

  CLAW, ARCHER, REPAIRER, HACKER, TURRET, WALL, TERMINATOR, HANGAR = range(8)
  mobileVariants = [0, 1, 2, 3, 6]
  aggressiveVariants = [0, 1, 4, 6]
  spawnVariants = [0, 1, 6]
  units = [None] * 800
  ends = collections.deque() 
  spawnable = []
  defend = False
  num_mine = 0
  num_theirs = 0
  my_health = 0
  their_health = 0

  def init(self):
    self.update_tiles()
    pass

  def distance(self, tuple1, tuple2):
    return abs(tuple2[0] - tuple1[0]) + abs(tuple2[1] - tuple1[1])

  def forward(self):
    return 1 + self.playerID * -2

  def mySide(self):
    if self.playerID == 0:
      return 0
    return self.mapWidth - 1

  def unit(self, x, y):
    z = x * self.mapHeight + y
    if z > 799 or z < 0:
      print("{}, {} -> {}".format(x,y,z))
    return self.units[z]

  def empty(self, x, y):
    return self.unit(x,y) is None

  def walkable(self, x, y):
    return self.empty(x, y) or self.unit(x, y).variant in self.mobileVariants or self.unit(x, y).controller is not self.playerID
  
  def path(self, x, y, startx, starty):
    return (self.empty(startx, starty) or self.unit(startx, starty).variant in self.mobileVariants) and (self.empty(x, y) or self.unit(x,y).controller is not self.playerID)

  def possiblePath(self, x, y, startx, starty):
    return (self.empty(startx, starty) or self.unit(startx, starty).variant in self.mobileVariants) and self.walkable(x, y)

  def update_tiles(self):
    for i in range(self.mapWidth*self.mapHeight):
      self.units[i] = None
    self.num_mine = self.num_theirs = 0
    for droid in self.droids:
      self.units[droid.x * self.mapHeight + droid.y] = droid
      if droid.owner is self.playerID:
        self.num_mine = self.num_mine + 1
        if droid.variant is self.HANGAR:
          self.my_health += droid.healthLeft
      else:
        self.num_theirs = self.num_theirs + 1
        if droid.variant is self.HANGAR:
          self.their_health += droid.healthLeft

    pass

  def update_tile(self, newloc, droid):
    self.units[droid.x * self.mapHeight + droid.y] = None
    self.units[newloc[0] * self.mapHeight + newloc[1]] = droid
    pass

  def setStarts(self): # just 1 for now
    starts = collections.deque()

    for droid in self.droids:
      if droid.controller is self.playerID and droid.variant < 4:
        starts.appendleft((droid.x, droid.y))
        return starts
    return starts

  def setEnds(self):
    ends = collections.deque()
    for droid in self.droids:
      if droid.controller is self.playerID^1:
        ends.appendleft((droid.x, droid.y))
    return ends


  def pathFind(self, starts, ends):
    Open = collections.deque(starts)
    Closed = Set(starts)
    parentMap = dict()
    path = []
    while Open:
      current = Open.pop()
      if current in ends:
        while current not in starts:
          path.append(current)
          current = parentMap[current]
        return path
      for neighbor in self.neighbors(current): 
        if neighbor not in Closed:
          parentMap[neighbor] = current
          Closed.add((neighbor))
          Open.appendleft((neighbor))
    pass

  def possiblePathFind(self, starts, ends):
    Open = collections.deque(starts)
    Closed = Set(starts)
    parentMap = dict()
    path = []
    while Open:
      current = Open.pop()
      if current in ends:
        while current not in starts:
          path.append(current)
          current = parentMap[current]
        return path
      for neighbor in self.neighbors_unrestricted(current): 
        if neighbor not in Closed:
          parentMap[neighbor] = current
          Closed.add((neighbor))
          Open.appendleft((neighbor))
    pass

  def neighbors(self, droid):
    n = []
    if droid[1] - 1 >= 0 and self.path(droid[0], droid[1] - 1, droid[0], droid[1]):
      n.append((droid[0], droid[1] - 1))
    if droid[1] + 1 < self.mapHeight and self.path(droid[0], droid[1] + 1, droid[0], droid[1]):
      n.append((droid[0], droid[1] + 1))
    if droid[0] - 1 >= 0 and self.path(droid[0] - 1, droid[1], droid[0], droid[1]):
      n.append((droid[0] - 1, droid[1]))
    if droid[0] + 1 < self.mapWidth and self.path(droid[0] + 1, droid[1], droid[0], droid[1]):
      n.append((droid[0] + 1, droid[1]))
    return n
  
  def neighbors_unrestricted(self, droid):
    n = []
    if droid[1] - 1 >= 0 and self.possiblePath(droid[0], droid[1] - 1, droid[0], droid[1]):
      n.append((droid[0], droid[1] - 1))
    if droid[1] + 1 < self.mapHeight and self.possiblePath(droid[0], droid[1] + 1, droid[0], droid[1]):
      n.append((droid[0], droid[1] + 1))
    if droid[0] - 1 >= 0 and self.possiblePath(droid[0] - 1, droid[1], droid[0], droid[1]):
      n.append((droid[0] - 1, droid[1]))
    if droid[0] + 1 < self.mapWidth and self.possiblePath(droid[0] + 1, droid[1], droid[0], droid[1]):
      n.append((droid[0] + 1, droid[1]))
    return n

  def setSpawnable(self):
    spawnable = []
    print("Setting spawns...")
    x = self.mySide()
    while not spawnable or len(spawnable) < self.mapHeight:
      for y in range(self.mapHeight):
        start = [(x, y)]
        if self.possiblePathFind(start, self.ends):
          spawnable.append((x, y))
      if not spawnable:
        print("No spawnable locations! Increasing x...")
      x = x + self.forward()
    self.spawnable = spawnable
    pass

  def spawn(self):
    for droid in self.droids:
      if self.players[self.playerID].scrapAmount >= self.modelVariants[self.CLAW].cost and droid.owner is not self.playerID and droid.variant is self.TURRET and self.tiles[droid.x * self.mapHeight + droid.y].turnsUntilAssembled <= 0:
        self.players[self.playerID].orbitalDrop(droid.x, droid.y, self.CLAW)

    variant = random.choice(self.spawnVariants)
    #if random.randint(0,8) > 6:
    #  variant = self.TERMINATOR
    spawnable = []
    for spawn in self.spawnable:
      if self.tiles[spawn[0]* self.mapHeight + spawn[1]].turnsUntilAssembled is 0:
        if spawn[0] is not self.mySide() or self.empty(spawn[0], spawn[1]) or self.unit(spawn[0], spawn[1]).controller is not self.playerID:
          spawnable.append(spawn)
    if not spawnable:
      print "Error: no valid spawn points"
    while spawnable and self.players[self.playerID].scrapAmount >= self.modelVariants[variant].cost:
        spawn = random.choice(spawnable)
        spawnable.remove(spawn)
        self.players[self.playerID].orbitalDrop(spawn[0], spawn[1], variant)

    return 1
  def smart_move(self):
    s = self.setStarts()
    for droid in self.droids:
      if droid.variant in self.mobileVariants and droid.controller is self.playerID:
        s.clear()
        s.append((droid.x, droid.y))
        if s and self.ends:
          path = self.pathFind(s, self.ends)
          if not path:
            path = self.possiblePathFind(s, self.ends)
          while path and droid.movementLeft:
            new = path.pop()
            if self.empty(new[0], new[1]) and (self.tiles[new[0] * self.mapHeight + new[1]].turnsUntilAssembled is not 1 or droid.movementLeft > 1):
              self.update_tile((new[0], new[1]), droid)
              droid.move(new[0], new[1])
            else:
              path = []

  def radius(self, droid):
    r = []
    for i in range(1,droid.range+1):
      directions = [(droid.x, droid.y + i), (droid.x, droid.y - i), (droid.x - i, droid.y), (droid.x + i, droid.y)]
      for x, y in directions:
        if x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight and self.empty(x, y) is False:
          r.append((x, y))
    return r


  def attack(self):
    for droid in self.droids:
      if droid.controller is self.playerID and droid.variant in self.aggressiveVariants:
        directions = self.radius(droid)
        for x, y in directions:
          if droid.attacksLeft > 0 and x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight and self.empty(x, y) is False and self.unit(x,y).controller is not self.playerID:
            droid.operate(x, y)
              
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.ends = self.setEnds()
    self.update_tiles()
    self.defend = (self.num_mine < self.num_theirs and self.my_health < self.their_health) or self.my_health < self.their_health / 2
    if self.turnNumber%100 < 2 and (not self.spawnable or abs(self.mySide() - self.spawnable[0][0]) > 4):
      self.setSpawnable()
    self.spawn()

    self.smart_move()
    self.attack()
    if self.players[self.playerID].scrapAmount > 100:
      self.spawn()

    #for i in range(800):
    #  if self.units[i] is not None:
    #    print("{}, {} is {}".format((i)/self.mapHeight, (i)%self.mapHeight, self.units[i]))


    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)
