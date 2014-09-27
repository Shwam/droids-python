#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import random

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "S"

  @staticmethod
  def password():
    return "password"

  CLAW, ARCHER, REPAIRER, HACKER, TURRET, WALL, TERMINATOR, HANGAR = range(8)
  
  def init(self):
    pass

  def mySide(self):
    if self.playerID == 0:
      return 0
    return self.mapWidth - 1

  def tile(self, x, y):
    return self.tiles[y*self.mapHeight + x]

  def spawn(self):
    y = random.randint(0,self.mapHeight - 1)
    self.players[self.playerID].orbitalDrop(self.mySide(), y, random.randint(0,1))

    return 1
  
  def move_units(self):
    for droid in self.droids:
      if droid.movementLeft > 0 and droid.owner == self.playerID:
        if self.turnNumber % 3 == 0 and self.tile(droid.forward, droid.y).variantToAssemble == -1:
          droid.move(droid.forward, droid.y)
        elif self.turnNumber % 3 == 1:
          droid.move(droid.x, droid.y + random.randint(-1,1))
        if self.turnNumber % 3 == 2 and self.tile(droid.forward, droid.y).variantToAssemble == -1:
          droid.move(droid.forward, droid.y)
    print("WORDS WORDS WORDS WORDS TILE ({}).".format(self.tile(0,0)))
    
    return 1

  def attack(self):
    for droid in self.droids:
      if droid.movementLeft > 0 and droid.owner == self.playerID and self.tile(droid.forward, droid.y).variantToAssemble == -1:
        droid.operate(droid.forward, droid.y)
        print("Droid {} operating on {}".format(droid.id, self.tile(droid.forward, droid.y)))
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.spawn()
    self.move_units()
    self.attack()
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)
