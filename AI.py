#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import random
import copy

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "S"

  @staticmethod
  def password():
    return "password"

  CLAW, ARCHER, REPAIRER, HACKER, TURRET, WALL, TERMINATOR, HANGAR = range(8)
  
  units = [None] * 800

  def init(self):
    self.update_tiles()
    pass

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

  def update_tiles(self):
    for i in range(self.mapWidth*self.mapHeight):
      self.units[i] = None

    for droid in self.droids:
      self.units[droid.x * self.mapHeight + droid.y] = droid

    pass
    
  def spawn(self):
    variant = random.randint(0,4)
    if self.players[self.playerID].scrapAmount >= self.modelVariants[variant].cost:
      y = random.randint(0,self.mapHeight - 1)
      self.players[self.playerID].orbitalDrop(self.mySide(), y, variant)

    return 1
  
  def move_units(self):
    for droid in self.droids:
      canMove = True
      while droid.movementLeft > 0 and canMove:
        if droid.controller == self.playerID:
          print("Attempting to move {}...".format(droid.id))
          if droid.forward >= 0 and droid.forward < self.mapWidth and self.empty(droid.forward, droid.y):          
              self.units[droid.forward+self.mapWidth*droid.y] = self.units[droid.x + self.mapWidth * droid.y]
              self.units[droid.x + self.mapWidth * droid.y] = None
              droid.move(droid.forward, droid.y)
              print("Success! Forward -> {}".format(droid.x))

              #print("{} < {} ... {}".format(droid.forward, self.mapWidth, droid.forward < self.mapWidth))
              #print("{}, {} is {}... empty = {}".format(droid.x, droid.y, self.unit(droid.x, droid.y), self.empty(droid.forward, droid.y)))
          else:
            y = droid.y + 1 + 2 * random.randint(-1,0)
            if y >= 0 and y < self.mapHeight and self.empty(droid.x, y):
              self.units[droid.x+self.mapWidth*y] = self.units[droid.x + self.mapWidth * droid.y]
              self.units[droid.x + self.mapWidth * droid.y] = None
              droid.move(droid.x, y)
              print("Success! Up -> {}".format(droid.y))
            else:
              y = -y
              if y >= 0 and y < self.mapHeight and self.empty(droid.x, y):
                self.units[droid.x+self.mapWidth*y] = self.units[droid.x + self.mapWidth * droid.y]
                self.units[droid.x + self.mapWidth * droid.y] = None
                droid.move(droid.x, y)
                print("Success! Up/Down -> {}".format(droid.y))
              else:
                canMove = False
                print("Failed.")
        else:
          canMove = False
          print("Failed.")
          #print("Droid {} trying to move up or down".format(droid.id))
    
    return 1

  def attack(self):
    for droid in self.droids:
      if droid.controller is self.playerID:
        if droid.variant < 6 and droid.attacksLeft > 0 and droid.variant is not self.REPAIRER:
          if droid.forward > 0 and droid.forward < self.mapWidth and self.empty(droid.forward, droid.y) is False:
            if self.unit(droid.forward, droid.y).owner is not self.playerID:
              droid.operate(droid.forward, droid.y)
          elif droid.back > 0 and droid.back < self.mapWidth and self.empty(droid.back, droid.y) is False:
            if self.unit(droid.back, droid.y).owner is not self.playerID:
              droid.operate(droid.back, droid.y)
          elif droid.up > 0 and droid.up < self.mapHeight and self.empty(droid.x, droid.up) is False:
            if self.unit(droid.x, droid.up).owner is not self.playerID:
              droid.operate(droid.x, droid.up)
          elif droid.down > 0 and droid.down < self.mapHeight and self.empty(droid.x, droid.down) is False:
            if self.unit(droid.x, droid.down).owner is not self.playerID:
              droid.operate(droid.x, droid.down)

        #print("Droid {} operating on {}".format(droid.id, self.tile(droid.forward, droid.y)))
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.update_tiles()
    self.spawn()
    self.attack()
    self.move_units()
    self.update_tiles()
    self.attack()

    #for i in range(800):
    #  if self.units[i] is not None:
    #    print("{}, {} is {}".format((i)/self.mapHeight, (i)%self.mapHeight, self.units[i]))


    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)
