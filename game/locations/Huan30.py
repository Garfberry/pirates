
from game import location
import game.config as config
import game.display as display
from game.events import *
import game.items as items
import game.combat as combat
import game.event as event
import game.items as item
import random
from game.items import Item 
from game.combat import Monster

class GiantSpider(Monster):

    # Giant spider can bite or slash. Both do the same damage, it's just a flavor difference.
    # 100-110 speed. 64-96 health.
    def __init__ (self):
        attacks = {}
        attacks["bite"] = ["bites",random.randrange(60,80), (5,15)]
        attacks["slash"] = ["slashes",random.randrange(60,80), (5,15)]
        super().__init__("Giant Spider", random.randint(64,96), attacks, 100 + random.randint(0, 10))
        self.type_name = "Giant Spider"

class DoubleHoe(Item):

    # Less damage than a cutlass, but lets you pick up to two targets per fight.
    def __init__(self):
        super().__init__("double-hoe", 10)
        self.damage = (8,50)
        self.skill = "swords"
        self.verb = "slam"
        self.verb2 = "slams"
        self.NUMBER_OF_ATTACKS = 2 # Number of attacks to be made in pickTargets


class GiantSpiderEvent (event.Event):

    def __init__ (self):
        self.name = " giant spider attack."

    def process (self, world):
        result = {}
        spider = GiantSpider()
        display.announce("A giant spider leaps from the ceiling and attacks your crew!")
        combat.Combat([spider]).combat()
        display.announce("The giant spider goes limp.")
        # Set newevents to an empty list. If I added 'self' to the list, the event would be readded upon completing, effectively making the spider respawn every turn you are in here.
        result["newevents"] = []
        # Set the result message to an empty string, as we are printing our own strings at the right time.
        result["message"] = ""

        display.announce("In the shed, you find a double-headed hoe. It looks like it'd make a decent weapon.")
        config.the_player.add_to_inventory([DoubleHoe()])

        return result

class Macaque(combat.Monster):
    def __init__ (self, name):
        attacks = {}
        attacks["bite"] = ["bites",random.randrange(70,101), (10,20)]
        #7 to 19 hp, bite attack, 160 to 200 speed (100 is "normal")
        super().__init__(name, random.randrange(7,20), attacks, 180 + random.randrange(-20,21))
        self.type_name = "Man-eating Macacque"

class ManEatingMonkeys (event.Event):
    '''
    A combat encounter with a troop of man eating monkies.
    When the event is drawn, creates a combat encounter with 4 to 8 monkies, kicks control over to the combat code to resolve the fight.
    The monkies are "edible", which is modeled by increasing the ship's food by 5 per monkey appearing and adding an apropriate message to the result.
        Since food is good, the event only has a 50% chance to add itself to the result.
    '''

    def __init__ (self):
        self.name = " monkey attack"

    def process (self, world):
        result = {}
        result["message"] = "the macaques are defeated! ...Those look pretty tasty!"
        monsters = []
        n_appearing = random.randrange(4,8)
        n = 1
        while n <= n_appearing:
            monsters.append(Macaque("Man-eating Macaque "+str(n)))
            n += 1
        display.announce ("The crew is attacked by a troop of man-eating macaques!")
        combat.Combat(monsters).combat()
        if random.randrange(2) == 0:
            result["newevents"] = [ self ]
        else:
            result["newevents"] = [ ]
        config.the_player.ship.food += n_appearing*5

        return result

class Maroonee(combat.Monster):
    def __init__ (self, name):
        attacks = {}
        attacks["bite"] = ["bites",random.randrange(35,51), (5,15)]
        attacks["punch 1"] = ["punches",random.randrange(35,51), (1,10)]
        attacks["punch 2"] = ["punches",random.randrange(35,51), (1,10)]
        #7 to 19 hp, bite attack, 65 to 85 speed (100 is "normal")
        super().__init__(name, random.randrange(7,20), attacks, 75 + random.randrange(-10,11))
        self.type_name = "Mummified Maroonee"

class JeweledCutlass(item.Item):
    def __init__(self):
        super().__init__("jeweled-sword", 185) #Note: price is in shillings (a silver coin, 20 per pound)
        self.damage = (10,60)
        self.skill = "swords"
        self.verb = "cut"
        self.verb2 = "cuts"

class ShorePirates (event.Event):
    petemade = False
    '''
    A combat encounter with a crew of marooned pirate zombies.
    When the event is drawn, creates a combat encounter with 2 to 6 marooned pirates, kicks control over to the combat code to resolve the fight, then adds itself and a simple success message to the result
    '''

    def __init__ (self):
        self.name = " marooned pirate attack"

    def process (self, world):
        '''Process the event. Populates a combat with Maroonee monsters. The first Maroonee may be modified into a "Pirate captain" by buffing its speed and health.'''
        result = {}
        result["message"] = "the marooned pirates are defeated!"
        monsters = []
        min = 2
        uplim = 6
        if not ShorePirates.petemade:
            ShorePirates.petemade = True
            min = 1
            uplim = 5
            monsters.append(Maroonee("Partially-eaten Pete"))
            self.type_name = "Partially-eaten Pete"
            monsters[0].health = 3*monsters[0].health
        elif random.randrange(2) == 0:
            min = 1
            uplim = 5
            monsters.append(Maroonee("Pirate captain"))
            self.type_name = "Marooned Pirate Captain"
            monsters[0].speed = 1.2*monsters[0].speed
            monsters[0].health = 2*monsters[0].health
        n_appearing = random.randrange(min, uplim)
        n = 1
        while n <= n_appearing:
            monsters.append(Maroonee("Mumified maroonee "+str(n)))
            n += 1
        display.announce ("You are attacked by a crew of marooned pirates!")
        combat.Combat(monsters).combat()
        result["newevents"] = [ self ]
        return result



class Island (location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "island"
        self.symbol = 'I'
        self.visitable = True
        self.locations = {}
        self.locations["beach"] = Beach_with_ship(self)

        self.starting_location = self.locations["beach"]

    def enter (self, ship):
        display.announce ("arrived at an island", pause=False)


class Beach_with_ship (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "beach"
        self.verbs['south'] = self

    def enter (self):
        display.announce ("arrive at the beach. Your ship is at anchor in a small bay to the south.")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.")
            self.main_location.end_visit()

class Trees (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "trees"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        # Include a couple of items and the ability to pick them up, for demo purposes
        self.verbs['take'] = self
        self.item_in_tree = JeweledCutlass() #Treasure from this island
        self.item_in_clothes = items.Flintlock() #Flintlock from the general item list

        self.event_chance = 50
        self.events.append(ManEatingMonkeys())
        self.events.append(ShorePirates())

class Shed (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "shed"
        self.verbs['exit'] = self
        self.verbs['leave'] = self

        self.event_chance = 100
        self.events.append(GiantSpiderEvent())

    def enter (self):
        description = "Rotted wood lines the walls of the musty shed."
        display.announce(description)

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "exit" or verb == "leave"):
            config.the_player.next_loc = self.main_location.locations["northBeach"]
            config.the_player.go = True


class MazeStart(location.SubLocation):
    def __init__(self):
        self.starting_segment = None


class MazeEnd(location.SubLocation):
    def __init__(self):
        self.ending_segment = None


class MazeSegment (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "Maze"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.north_loc = None
        self.south_loc = None
        self.east_loc = None
        self.west_loc = None
        self.remaining = ["north", "south", "west", "east"]
        self.depth = 0

frontier = []
start = MazeStart()
end = MazeEnd()
current_segment = MazeSegment()
frontier.append(current_segment)
start.starting_segment = current_segment
current_segment["down"] = start
current_segment.remaining.remove("down")
end_placed = False
while len(frontier) > 0:
    current_segment = random.choice(frontier)
    if end_placed and random.random() < .9:
        next_segment = None
    elif not end_placed and current_segment.depth > 2 and random.random() < .5:
        next_segment = MazeEnd()
    else:
        next_segment = MazeSegment()
        next_segment.depth = current_segment.depth + 1
    connection = random.choice(current_segment.remaining)
    current_segment[connection] = next_segment
    if next_segment == None:
        pass #deadend
    elif type(next_segment) == MazeEnd:
        next_segment.ending_segment = current_segment
    else: #normal maze segment
        if connection == "up":
            back_connection = "down"
        elif connection == "down":
            back_connection = "up"
        elif connection == "left":
            back_connection = "right"
        else:
            back_connection = "left"
        next_segment[back_connection] = current_segment
        next_segment.remaining.removing(back_connection)
    current_segment.remaining.remove(connection)
    if len(current_segment.remaining) < 1:


    def enter (self):
        description = "Oh, looks like you got yourself into a maze. Use your own intution to find the way out"#Something about a maze segment?
        if self.north_loc != None:
            description += "The maze continues north here."
        if self.south_loc != None:
            description += "The maze continues south here"
        if self.east_loc != None:
            description += "The maze branches and turns to the east"
        if self.west_loc != None:
            description += "The maze branches and turns to the west"
        #backward loc always true.
        #if right loc "the maze branches or the maze turns right"
        #if left loc "ditto"

    def process_verb (self, verb, cmd_list, nouns):
        if verb == "forward":
            if(self.forward_loc != None):
                config.the_player.next_loc = self.forward_loc
            else:
                display.announce("You see a wall.")