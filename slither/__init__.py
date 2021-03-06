# SLITHER FOR PYTHON 2 AND 3
# Hi there, code divers!
# There's a lot of cool stuff here that has comments so you can understand what I'm doing.
# You can even mess around with it yourself :)
# If you think your messing around might help, go to:
# https://github.com/Tymewalk/Slither
# and make a pull request!

import pygame
import sys, os
# import time # For future timer

sprites = [] # List of all sprites
clock = pygame.time.Clock() # Used to control framerate
eventnames = ['QUIT', 'ACTIVEEVENT', 'KEYDOWN', 'KEYUP', 'MOUSEMOTION', 'MOUSEBUTTONUP', 'MOUSEBUTTONDOWN',
              'JOYAXISMOTION', 'JOYBALLMOTION', 'JOYHATMOTION', 'JOYBUTTONUP', 'JOYBUTTONDOWN',
              'VIDEORESIZE', 'VIDEOEXPOSE', 'USEREVENT']
eventCallbacks = {
                    getattr(pygame, name): lambda e=None: True
                    for name in eventnames
                } # Create a dict of callbacks that do nothing
globalscreen = None

scriptdir = os.path.dirname(os.path.realpath(__import__("__main__").__file__))

# Convienience functions
# Taken from http://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
# This function is broken, issue #9 remains
def rotateCenter(image, angle):
    """rotate a Surface, maintaining position."""
    loc = image.get_rect().center  #rot_image is not defined
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite

# Stage class
class Stage():
    def __init__(self):
        self.snakey = pygame.image.load(os.path.join(os.path.dirname(__file__), "snakey.png"))
        self.costumes = {"costume0" : self.snakey}
        self.costumeNumber = 0
        self.costumeName = "costume0"
        self.currentCostume = None
        self.bgColor = (255, 255, 255)

    # Stage-specific functions
    def setColor(self, r, g, b):
        '''Set the stage's color. Only works on the stage, not sprites.'''
        self.bgColor = (r, g, b)

    # Functions shared by sprites
    def addCostume(self, costumePath, costumeName):
        '''Add a costume based on a given path and name.'''
        costume = pygame.image.load(os.path.join(scriptdir, costumePath))
        self.costumes[costumeName] = costume

    def deleteCostumeByName(self, name):
        '''Delete a costume by name.'''
        self.costumes.pop(name, None)
        setCostumeByName(self.costumeName) # Make sure we recalculate the costume number!

    def deleteCostumeByNumber(self, number):
        '''Delete a costume by number.'''
        if number < len(self.costumes.keys()):
            costumeName = self.costumes.keys()[number]
            self.deleteCostumeByName(costumeName)

    def setCostumeByName(self, name):
        '''Set a costume by its name.'''
        if name in self.costumes:
            self.currentCostume = self.costumes[name]
            self.costumeName = name
            self.costumeNumber = list(self.costumes.keys()).index(name)

    def setCostumeByNumber(self, number):
        '''Set a costume by its number.'''
        if number < len(self.costumes.keys()):
            costumeName = list(self.costumes.keys())[number]
            self.setCostumeByName(costumeName)

    def getCostumeNumber(self):
        '''Get the costume number of the sprite.'''
        return self.costumeNumber

    def getCostumeName(self):
        '''Get the costume name of the sprite.'''
        return self.costumeName


slitherStage = Stage()

# The Sprite inherits things such as the costumes from the stage so everything can be kept in one place.
class Sprite(Stage):
    def __init__(self):
        Stage.__init__(self) # Get all the stuff from the stage, too
        self.currentCostume = self.snakey # By default we should be set to Snakey
        self.xpos = 0 # X Position
        self.ypos = 0 # Y Position
        self.direction = 0 # Direction is how much to change the direction, hence why it starts at 0 and not 90
        self.showing = True
        self.scale = 1 # How much to multiply it by in the scale
        self.zIndex = 0 # How high up are we in the "z" axis?
        sprites.append(self) # Add this sprite to the global list of sprites
        
    def show(self):
        '''Show the sprite.'''
        self.showing = True

    def hide(self):
        '''Hide the sprite.'''
        self.showing = False

    def changeXBy(self, amount):
        '''Change the sprite's X Position by (amount).'''
        self.xpos += amount

    def changeYBy(self, amount):
        '''Change the sprite's Y Position by (amount).'''
        self.ypos += amount

    def goTo(self, xpos, ypos):
        '''Go to xpos, ypos.'''
        self.xpos = xpos
        self.ypos = ypos

    def setXTo(self, xpos):
        '''Set the sprite's X Position to (amount).'''
        self.xpos = xpos

    def setYTo(self, ypos):
        '''Set the sprite's Y Position to (amount).'''
        self.ypos = ypos

    def changeScaleBy(self, amount):
        '''Change the sprite's scale by (amount).'''
        self.scale += amount

    def setScaleTo(self, scale):
        '''Set the sprite's scale to (amount).'''
        self.scale = scale

    def getScale(self):
        '''Get the sprite's current scale.'''
        return self.scale

    def setDirection(self, direction):
        self.direction = direction

    def changeDirectionBy(self, amount):
        self.direction += amount

    def getDirection(self):
        return self.direction
    
    def changeZIndexBy(self, amount):
        '''Change the sprite's z-index by (amount).'''
        self.zIndex += amount
        reorderSprites()

    def setZIndexTo(self, zIndex):
        '''Set the sprite's z-index to (amount).'''
        self.zIndex = zIndex
        reorderSprites()

    def getZIndex(self):
        '''Get the sprite's current z-index.'''
        return self.zIndex

    def isVisible(self):
        '''Check if the object is visible, not just showing.'''
        return self.showing and self.scale > 0

    def delete(self):
        '''Remove the sprite from the global sprites list, causing it not to be drawn.'''
        sprites.remove(self)

class Sound():
    # Based on pygame examples
    def loadSound(self, name):
        '''Load a sound. Set this function to a variable then call variable.play()'''
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = name
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error as e:
            print ('Cannot load sound: %s' % fullname)
            raise e
        return sound

slitherSound = Sound()

def setup(caption=sys.argv[0]):
    '''Sets up PyGame and returns a screen object that can be used with blit().'''
    global globalscreen
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    caption = pygame.display.set_caption(caption)
    globalscreen = screen
    return screen

projectFPS = 60 # 60 is the default
def setFPS(fps):
    '''Set the FPS of the project. Default is 60, and Scratch runs at 30.'''
    global projectFPS
    projectFPS = fps # projectFPS is the FPS that the main loop uses

def reorderSprites():
    global sprites
    sprites = sorted(sprites, key=(lambda s: s.zIndex))

def blit(screen):
    '''Takes a screen as an argument and draws objects to the screen. THIS MUST BE CALLED FOR SLITHER TO DISPAY OBJECTS.'''
    if screen:
        screen.fill(slitherStage.bgColor)

        if slitherStage.currentCostume:
            screen.blit(pygame.transform.scale(slitherStage.currentCostume, (800,600)), (0, 0))

        for obj in sprites:
            if obj.isVisible(): # Check if the object is showing before we do anything
                image = obj.currentCostume # So we can modify it and blit the modified version easily
                # These next few blocks of code check if the object has the defaults before doing anything.
                if not obj.scale == 1:
                    imageSize = image.get_size()
                    image = pygame.transform.scale(image, (int(imageSize[0] * obj.scale), int(imageSize[1] * obj.scale)))
                if not obj.direction == 0:
                    image = rotateCenter(image, obj.direction)
                screen.blit(image, (obj.xpos, obj.ypos))

    pygame.display.flip()

def registerCallback(eventname, func=None):
    "Register the function func to handle the event eventname"
    if func:
        # Direct call (registerCallback(pygame.QUIT, func))
        eventCallbacks[eventname] = func
    else:
        # Decorator call (@registerCallback(pygame.QUIT)
        #                 def f(): pass
        def f(func):
            eventCallbacks[eventname] = func
        return f

def runQuitCallback():
    return eventCallbacks[pygame.QUIT]()

def runMainLoop(frameFunc):
    while True:
        blit(globalscreen)
        frameFunc()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if runQuitCallback():
                    # runQuitCallback would run the function
                    # given to setQuitCallback, and return its result
                    pygame.quit()
                    sys.exit()
            else:
                eventCallbacks[event.type](event)
                # eventCallbacks would be a dictionary mapping
                # event types to handler functions.
        clock.tick(projectFPS) # Run at however many FPS the user specifies
