import pygame
import os
from pygame.locals import *

############################
#       Graphic
############################


def load_png(name,colorkey=None):
        fullname = os.path.join('Images', name)
        try:                
                image = pygame.image.load(fullname)
                if image.get_alpha() is None:
                        image = image.convert()
                else:
                        image = image.convert_alpha()
        except pygame.error:
                print ("load_png Error !")
                raise SystemExit

        if colorkey is not None:
                if colorkey is -1:
                        colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

        return image, image.get_rect()



class TGrObj(pygame.sprite.Sprite):
        def __init__(self, name):
                self.x = 4.1
                self.y = 0
                pygame.sprite.Sprite.__init__(self)                
                self.image, self.rect = load_png(name)
                self.screen = pygame.display.get_surface()

        def changeImage(self, name):
                self.image, self.rect = load_png(name)

        def drawAt(self, x,y):                
                self.x = x
                self.y = y
                self.screen.blit(self.image, (x,y))

        def draw(self):

                self.screen.blit(self.image, (self.x, self.y))

        def drawImage(self, img):
                self.screen = pygame.display.get_surface()
                self.screen.blit(img, (self.x, self.y))
