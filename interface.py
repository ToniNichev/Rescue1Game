import pygame
import os
from pygame.locals import *
from graphic import *







############################
#       Interface
############################    

def blit_text(Txt,x,y,Fsize=22, Fcolor=(255,255,255)):
        screen = pygame.display.get_surface()
        font = pygame.font.Font(None, Fsize)
        font.set_bold(False)
        text = font.render(Txt, 1, Fcolor)
        screen.blit(text, (x,y)) 




class TBitButton():
        def __init__(self,screen, imageName, onclickImageName, x=0, y=0, txt=None, fontSize=14, txtColor=(0,0,0), alpha=255):
                self.txt = txt
                self.txtColor = txtColor
                self.onclickImage = None
                if imageName != None:
                        self.image, self.rect = load_png(imageName)
                        if onclickImageName!=None:
                                self.onclickImage, self.onclickrect = load_png(onclickImageName)
                        if self.txt != None:
                                print (len(txt))
                                w = int(fontSize * 0.460) * len(txt) + 30
                                h = int(fontSize * 1.2)
                                self.image = pygame.transform.scale(self.image, (w, h))
                                self.image.set_alpha(alpha)                                   
                                self.rect[2] = w
                                self.rect[3] = h
                                if self.onclickImage!=None:                        
                                        self.onclickImage = pygame.transform.scale(self.onclickImage, (w, h))                                     
                else:
                        self.image = None

                self.x = x
                self.y = y
                self.screen = screen
                self.fontSize = fontSize
                self.clicked = 0


        def draw(self):
                if self.image != None:
                        if self.clicked == 1 and self.onclickImage!= None:
                                self.screen.blit(self.onclickImage, (self.x, self.y))
                        else:
                                self.screen.blit(self.image, (self.x, self.y))
                if self.txt != None:
                        blit_text(self.txt ,self.x+18, self.y+3, self.fontSize, self.txtColor)                
        

        def onClick(self, mouseEvent):
                if mouseEvent == MOUSEBUTTONUP:                
                        if self.clicked == 1:
                                self.clicked = 0                                
                                return 1
                        self.clicked = 0
                        return 0
                mx,my = pygame.mouse.get_pos()
                if mx > self.x and mx < self.x + self.rect[2]:
                        if my > self.y and my < self.y + self.rect[3]:
                                self.clicked = 1
                                return 0
                return 0
                self.clicked = 0





class TLabel():
        def __init__(self, screen, txt, fontSize, x=0, y=0, w=150, alpha=50, fColor=(255,255,255)):
                self.screen = screen
                self.image, self.rect = load_png("win2.png")
                self.w = w
                self.fontSize = fontSize
                self.h = fontSize+2
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.image.set_alpha(alpha)
                self.x = x
                self.y = y
                self.txt = txt
                self.fColor = fColor
                

        def draw(self):
                self.screen.blit(self.image, (self.x, self.y))
                blit_text(self.txt ,self.x+6, self.y+2, self.fontSize, self.fColor)
                
        def Text(self, text):
                if text == None:
                        return
                self.txt = text
                self.draw()





class TListDir():
    
    def __init__(self, dirName, x, y, w, h, fontSize=14, Alpha=50):   
        self.screen = pygame.display.get_surface()        
        self.image, self.rect = load_png("win2.png")
        self.image = pygame.transform.scale(self.image, (w, h))
        self.image.set_alpha(Alpha)                
        #
        self.screen = pygame.display.get_surface()
        self.page = 0
        self.fontSize = fontSize
        self.dirName = dirName
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.scrollPos = 0
        self.itemsPerView = self.height / (self.fontSize+2)
        self.itemsCount = 0
        self.ListData = []
        for f in os.listdir(self.dirName):            
            self.ListData.append([f, 0])
            self.itemsCount += 1
            # Up Down Buttons
            self.ButtonUp = TBitButton(self.screen, "btn_u.png", "btn_u2.png", self.x + self.width - 22 , self.y+3)
            self.ButtonDown = TBitButton(self.screen, "btn_d.png", "btn_d2.png", self.x + self.width - 22 , self.y+self.height - 22)                    
                
                
    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))                
        y = self.y
        x = self.x
        co = 0                
        for Data in self.ListData:
            if self.scrollPos <= co:
                blit_text(Data[0] ,x+4, y+4, self.fontSize)
                Data[1] = y
                y += (self.fontSize+2)                                                                                
                co += 1
                if co - self.scrollPos  >=  self.itemsPerView:
                    break
                        
        # Up Down Buttons
        self.ButtonUp.draw()
        self.ButtonDown.draw()


                
    def scrollList(self, pos):
        self.scrollPos = self.scrollPos + pos
        self.draw()
                

    def checkEvent(self, mouseEvent):
        # Up Down Buttons                
            if self.ButtonUp.onClick(mouseEvent) == 1 and self.scrollPos > 0:
                    self.scrollList(-1)
            if self.ButtonDown.onClick(mouseEvent) == 1 and self.scrollPos < self.itemsCount - self.itemsPerView-1:
                    self.scrollList(1)
            if mouseEvent == MOUSEBUTTONUP:
                    return                        
            # Click Item
            mx,my = pygame.mouse.get_pos()                
            for Data in self.ListData:
                    if mx >self.x and mx <self.x + self.width-23:
                            if my > Data[1] and my <Data[1] + self.fontSize:
                                    return Data[0]
            return None






class TProgressBar():

    def __init__(self, rectArea, maxVal, currentVal, SelColor=(255,0,0), extraVal=0, externalValColor=(0,100,0)):
        self.screen = pygame.display.get_surface()
        self.color = SelColor
        self.externalValColor = externalValColor
        self.rectArea = rectArea
        self.maxVal = maxVal
        self.currentVal = currentVal
        self.image, self.rect = load_png("win2.png")
        self.image = pygame.transform.scale(self.image, (rectArea[2], rectArea[3]))
        self.extraVal = extraVal


    def draw(self):
        x = self.rectArea[0]+2
        y = self.rectArea[1]+2
        w = (self.currentVal * (self.rectArea[2]-4)  )  / (self.maxVal+0.01)
        h = self.rectArea[3]-4
        self.screen.blit(self.image,  self.rectArea)
        pygame.draw.rect(self.screen, self.color, (x, y, w, h))
        if self.extraVal > 0:
                w1 = (self.extraVal * (self.rectArea[2]-4)  )  / self.maxVal
                pygame.draw.rect(self.screen, self.externalValColor, (x,y,w1,h))


    def setCurrentVal(self, val, ExtraVal=0):
        if val < 0:
            return
        self.currentVal = val
        self.extraVal = ExtraVal
        self.draw()


    def setExtraVal(self, ExtraVal):
        if ExtraVal < 0:
            return
        self.extraVal = ExtraVal
        self.draw()
        


