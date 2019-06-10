#!/usr/bin/python




    
try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    import xml.dom.minidom
    import pygame.mixer 

    #import graphic & interface functions 
    from interface import *
    from graphic import *

    
    from socket import *
    from pygame.locals import *
except ImportError:
    print ("couldnt load module")
    sys.exit(2)


 


###########################
#       Settings 
###########################
rockets_max=15
bombs_max = 10
machineguns_max = 20

#--------------------------

game_moneyPayTake = {
                 "startingNewGameMoney" :11000,
                 "bombPrice" : 150,
                 "machineGunPrice" :40,
                 #"repairPrice" : 50,
                 "captiveGet" : 500,
                 "enemyKilled" : 200,                 
                 "captiveKilled" : 600,
                 "enemyFireIntensity" : 75,  # > more fire
                 "changeMovingWay" : 50
                 }
# -------------------------
game_pickedUp = 0
game_screen_x = 680
game_screen_y = 480
game_captiveCount = 0
game_rockedSpeed =  4
game_mode = 0 #Main Menu, Play Game
game_money = game_moneyPayTake['startingNewGameMoney']
sound = {
        "bomb" : None,
        "sas" : None
        }
# ---- Global Objects -----
png_mountain = None
ChopperObj = None
InstrumentsPanel = None
MainMenu = None
###########################
chopperXMLName = None
chopperBombs = 0
chopperMachineguns = 0
choperHealth = 0
map_ofset=0
x_desired_speed = 0
x_speed=0
y_desired_speed = 0
y_speed = 0
MapObject = []
Captive = []
Rockets = []




############################
#       Sound
############################

def load_sound(name):
    class No_sound:
            def play(self):
                    pass

    if not pygame.mixer or not pygame.mixer.get_init():
            return No_sound()

    fullname = os.path.join('Sounds', name)
    if os.path.exists(fullname) == False:
            sound = pygame.mixer.Sound(fullname)
    else:
            print ("load_sound() Error:")
            return No_sound
    return sound






############################
#       CHOPPER
############################

class TBombs(TGrObj):
    
    def __init__(self,y, orientation_prefix, bombType):
            screen = pygame.display.get_surface()
            x = screen.get_rect()[2] /2 - 10
            self.x = x - map_ofset
            self.active = 1
            self.destroy_anim = 0
            self.anim = 0
            self.img_fire_a = None
            self.img_fire_b = None
            self.BombType = bombType            
            if orientation_prefix == "_l":
                    self.orientation = 1
                    self.img = TGrObj("bomb.png")                    
            else:
                    self.orientation = -1
                    self.img = TGrObj("bombL.png")                    
            self.img.drawAt(x,y)            
            
            self.x2 = 0
            self.xAxelerate = 3


    def update(self):
            global sound
            if self.anim == 0:
                if self.BombType == 0:
                    self.img.y += 2
                else:
                    self.x2 += (self.xAxelerate * self.orientation)                                
                    if self.xAxelerate < 20:
                        self.xAxelerate += 0.5
                        self.img.y += 4 - self.xAxelerate/4

            self.img.x = self.x + map_ofset + self.x2
                
            if self.destroy_anim != 0:
                    self.__destroy__()
                    return
            # Collision with Mountain Detect
            my = mauntainHeightAtPos(self.x + self.img.rect[2]/2, self.img.y)
            if self.img.y+self.img.rect[3] > my or abs(self.x2)>800:
                    self.__destroy__()
                    return
                
            #self.img.y += 2                
            # Enemy Hit Detect
            co=0
            for EN in MapObject:
                    if EN.active == 1:
                            if self.img.x+EN.GR.rect[2] > EN.GR.x and self.img.x < EN.GR.x + EN.GR.rect[2]:
                                    if self.img.y + self.img.rect[3] > EN.GR.y: 
                                            sound['bomb'].play()
                                            EN.collision(5)
                                            self.__destroy__()
                                            
            self.img.draw()

    def __destroy__(self):                
            if self.anim == 0:
                    self.img_fire_a = TGrObj("bomb_fire_a.png")
                    self.img_fire_b = TGrObj("bomb_fire_b.png")
            elif self.anim == 1:
                    self.img.image = self.img_fire_a.image
            elif self.anim == 5:
                    self.img.image = self.img_fire_b.image
            elif self.anim == 10:                        
                    self.anim = 0
            self.img.draw()                        
            self.anim += 1
            # Finaly destroy object         
            self.destroy_anim += 1
            if self.destroy_anim > 30:
                    self.active = 0
                    self = None
             


  
class TMachinegun(TGrObj):

    def __init__(self, y, orientation_prefix, angle):
            self.screen = pygame.display.get_surface()
            x = self.screen.get_rect()[2] /2 - 10
            self.x = x - map_ofset
            self.pos_x = 0
            self.y = y+8
            self.active = 1
            if orientation_prefix == "_r":
                    self.orientation = -22
            else:
                    self.orientation = 22                      
            self.angle = angle
            self.destroy_anim = 0
            self.anim = 0
            


    def update(self):
            global game_screen_y
            global game_screen_x
            self.x += self.orientation
            self.pos_x = self.x + map_ofset
            self.y += abs(self.angle)/3
            # EOF SCREEN
            if self.y > game_screen_y or self.pos_x < 0 or self.pos_x > game_screen_x:
                    self.__destroy__()
                    return
            # Collision with Mountain Detect
            my = mauntainHeightAtPos(self.pos_x, self.y)
            if self.y > my:
                    self.__destroy__()
                    return                
            # Enemy Hit Detect
            co=0
            for EN in MapObject:
                    if EN.active == 1:
                            if self.pos_x+EN.GR.rect[2] > EN.GR.x and self.pos_x < EN.GR.x + EN.GR.rect[2]:
                                    if self.y > EN.GR.y and self.y < EN.GR.y + EN.GR.rect[3]: 
                                            EN.collision(1)
                                            self.__destroy__()

            pygame.draw.line(self.screen, (255,0,0), (self.pos_x, self.y), (self.pos_x+3, self.y))
            pygame.draw.line(self.screen, (255,255,255), (self.pos_x, self.y+1), (self.pos_x+3, self.y+1))            

    def __destroy__(self):
            self.active = 0









############################
#       CHOPPER
############################
ChopperObj

class TChopper(TGrObj):
    
    def __init__(self, imageA, imageB, acceleration, speed, climb, strength, bombs, machinegunCount, cost, bombType):
            #  Chopper behaviour
            self.acceleration = acceleration
            self.speed = speed
            self.climb = climb
            self.strength = strength
            self.bombCount = bombs
            self.bombType = bombType
            
            self.machinegunCount = machinegunCount

            self.maxBombs = bombs
            self.maxMachineguns = machinegunCount
            self.cost = cost
            # --- Sys Vars -----
            self.angle = 0
            self.updateAngle = 0
            self.flip = 0
            self.tmpImage = 0
            self.anim=1
            self.orientation_prefix = "_r"
            global bombs_max
            global machineguns_max
            # --- Weapons  -----
            self.bombs =[]
            for q in range(bombs_max):
                    self.bombs.append(0)
                    self.bombs[q] = None

            self.machinegun =[]
            for q in range(machineguns_max):
                    self.machinegun.append(0)
                    self.machinegun[q] = None                
            # ------------------
            #self.orientation = 0
            self.img = TGrObj(imageA)
            self.img_b = TGrObj(imageB)                
            # Prepare Flipped Chopper Images
            self.img_l = self.img.image
            self.img_l_b = self.img_b.image                
            
            self.img_r = pygame.transform.flip(self.img.image, True, False)
            self.img_r_b = pygame.transform.flip(self.img_b.image, True, False)
            # ---
            self.rotatedImageA = self.img.image
            self.rotatedImageB = self.img_b.image                

         

    def drawAt(self, x,y):
            #self.orientation = orientation
            self.img.drawAt(x,y)

    def draw(self, x_speed):                
            if self.angle > x_speed * 2:
                    self.angle = self.angle - self.acceleration * 2
                    self.updateAngle = 1
            elif self.angle < x_speed * 2:
                    self.angle = self.angle + self.acceleration * 2
                    self.updateAngle = 1                        

            if x_speed > self.acceleration:
                    self.orientation_prefix = "_r"
            elif x_speed < -self.acceleration:
                    self.orientation_prefix = "_l"
            else:  # Set speed to 0 prevent very slow movement
                    x_speed = 0

            
            print (">>>>>>>>>>>>>> !!!!!!!!!>>> ", self.orientation_prefix);
            if self.anim == 1:
                    s = 'chopperIMG = self.img'+self.orientation_prefix
                    if self.orientation_prefix == '_r':
                    	chopperIMG = self.img_r
                    else:
                    	chopperIMG = self.img_l
                    #exec(s) 
                    self.anim = 2
            else:
                    #s = 'chopperIMG = self.img'+self.orientation_prefix+"_b"
                    #chopperIMG = self.img_r
                    #exec(s) 
                    if self.orientation_prefix == '_r':
                    	chopperIMG = self.img_r_b
                    else:
                    	chopperIMG = self.img_l_b                    
                    
                    self.anim = 1

            finalImage = pygame.transform.rotate(chopperIMG, self.angle)
            self.updateAngle = 0
            self.img.drawImage(finalImage)
            # ------ Draw Life --------
            #drawLife(self.img.screen, self.strength, self.img)
            InstrumentsPanel.PbLife.setCurrentVal(self.strength)
            # UPDATE BOMBS
            for q in range(bombs_max):
                    if self.bombs[q] != None:
                            self.bombs[q].update()
                            if self.bombs[q].active == 0:
                                    self.bombs[q] = None
            # Update Machineguns
            for q in range(machineguns_max):
                    if self.machinegun[q] != None:
                            self.machinegun[q].update()
                            if self.machinegun[q].active == 0:
                                    self.machinegun[q] = None
            
            

    def fireBomb(self):
        if self.bombCount <= 0:
            return
        global InstrumentsPanel
        for q in range(bombs_max):
            if self.bombs[q] == None:
                self.bombCount -= 1
                self.bombs[q] = TBombs(self.img.y + self.img.rect[3], self.orientation_prefix, self.bombType)
                InstrumentsPanel.PbBombs.setCurrentVal(self.bombCount)
                break


    def fireMachineGun(self):
        if self.machinegunCount <= 0:
            return
        for q in range(machineguns_max):
            if self.machinegun[q] == None:
                    self.machinegunCount -= 1
                    self.machinegun[q] = TMachinegun(self.img.y + self.img.rect[3], self.orientation_prefix, self.angle)
                    InstrumentsPanel.PbMgun.setCurrentVal(self.machinegunCount)
                    break



############################
#       ENEMY
############################
            
class TMapObjectsRockets(TGrObj):
    global sound
    def __init__(self, x,y, ChopperObj):
            self.active = 1
            self.ChopperObj = 0
            self.anim = 0
            self.destroy_anim = 0
            #self.img = TGrObj("bomb.png")
            self.img_fire_a = None
            self.img_fire_b = None                 
            self.x = x - map_ofset
            self.xx = x - map_ofset
            self.y = y
            self.ChopperObj = ChopperObj
            screen = pygame.display.get_surface()
            self.speed = 1;
            rand = random.randint(0,3) 
            if rand == 0:
                self.superRocket = 1
                srImage = "2"
            else:
                self.superRocket = 0
                srImage = ""
                
            if x < screen.get_rect()[2] /2:
                    self.orientation = 1
                    self.img = TGrObj("bomb"+srImage+".png")                        
            else:
                    self.orientation = -1
                    self.img = TGrObj("bomb"+srImage+"L.png")                        

            rand = random.randint(0,2)
            # --- Calculate Rocket launching angle ----
            tmp = game_screen_y/2
            if x > tmp:
                a = x - tmp
            else:
                a = tmp - x    
            o = y - self.ChopperObj.img.y
            self.angle = (math.atan(o/a)*180/3.14*100)/100
            rand = random.randint(0,10)
            self.angle = self.angle - 5 + rand
            if self.angle < 0:
                self.angle = 1





    def update(self):
            global game_rockedSpeed
            angle = self.angle
            speed = game_rockedSpeed
            if self.superRocket==0:
                self.y = self.y - (speed * math.sin(angle* (3.14 /180)))
                self.speed += 1
            else:
                tmp = game_screen_y/2                
                if ChopperObj.img.x > tmp:
                    a = ChopperObj.img.x - tmp
                else:
                    a = tmp - ChopperObj.img.x                 
                o = self.y - self.ChopperObj.img.y                
                self.angle = (math.atan(o/a)*180/3.14*100)/100
                rand = random.randint(0,10)
                self.angle = self.angle - 5 + rand
                angle = self.angle

            

            self.y = self.y - (speed * math.sin(angle* (3.14 /180)))
            self.speed += 0.5
            self.xx += (speed * math.cos(angle* (3.14 /180))) * self.orientation
            self.x = self.xx + map_ofset
            if self.destroy_anim != 0:
                    self.__destroy__()
                    return                
            if self.x < - 15 or self.x > 680 or self.y<-3:
                    self.active = 0
                    return
            # Draw Rocket
            self.img.x = self.x
            self.img.y = self.y                
            self.img.draw()
            # Check for Collision
            if self.x+10 > self.ChopperObj.img.x and self.x < self.ChopperObj.img.x+self.ChopperObj.img.rect[2]:
                    if self.ChopperObj.img.y+self.ChopperObj.img.rect[3] > self.y and self.ChopperObj.img.y < self.y:
                            self.__destroy__()
                            crash("Rocket")

    def __destroy__(self):
            if self.anim == 0:
                    self.img_fire_a = TGrObj("bomb_fire_a.png")
                    self.img_fire_b = TGrObj("bomb_fire_b.png")
                    sound['bomb'].play()                    
            elif self.anim == 1:
                    self.img.image = self.img_fire_a.image
            elif self.anim == 5:
                    self.img.image = self.img_fire_b.image
            elif self.anim == 10:                        
                    self.anim = 0
            self.img.draw()                        
            self.anim += 1
            # Finaly destroy object         
            self.destroy_anim += 1
            if self.destroy_anim > 30:
                    self.active = 0
            




class TMapObjects(TGrObj):
    global map_ofset
    global rockets_max
    global Rockets
    global game_pickedUp
    global game_screen_y

    def __init__(self, obj_type,img_name, sx, ex, strength):
            self.sx = int(sx)
            self.ex = int(ex)
            self.vector = 1
            self.x = int(sx)
            self.strength = int(strength)
            self.active = 1
            self.obj_type = obj_type
            self.captive_view = 50
            #---------------
            self.GR = TGrObj(img_name)
            self.GR.y = 0


    def update(self, mountain, ChopperObj):
            # Check if Enemy is death
            if self.strength < 0:
                    self.active = 0
                    return                
            # Check if out of the screen 
            if self.x + map_ofset < -80 or self.x + map_ofset > game_screen_x + 100:
                    return
            
            if self.obj_type != "building":
                    # X position
                    self.x = self.x + self.vector 
                    self.GR.x = self.x + map_ofset
                    # Y position (claim the mountain)
                    q = mauntainHeightAtPos((self.GR.x+self.GR.rect[2]/2)-map_ofset, self.GR.y)
                    q = q + 5
                    self.GR.y = q - self.GR.rect[3] 
                    # ----- moving vector  -----
                    if self.obj_type == "captive":
                            if self.GR.x+self.GR.rect[2]+self.captive_view > ChopperObj.img.x and self.GR.x-self.captive_view < ChopperObj.img.x+ChopperObj.img.rect[2]:
                                    if ChopperObj.img.y+ChopperObj.img.rect[3]+self.captive_view > self.GR.y:
                                            if self.GR.x < ChopperObj.img.x+ChopperObj.img.rect[2]/2:
                                                    self.vector = 1
                                            else:
                                                    self.vector = -1
                                            
                                                                            
                    else:
                            rand = random.randint(0,game_moneyPayTake['changeMovingWay'])
                            if rand == 0:
                                self.vector = -1
                            if rand == 1:
                                self.vecton = 1
                            if self.GR.x - map_ofset > self.ex:                        
                                    self.vector = -1
                            if self.GR.x - map_ofset < self.sx:
                                    self.vector = 1
            else:
                    self.GR.x = self.x + map_ofset
                    if self.GR.y == 0:
                            q = mauntainHeightAtPos((self.GR.x+self.GR.rect[2]/2)-map_ofset, self.GR.y)
                            self.GR.y = q - self.GR.rect[3] + 10 

                            
                    
            # -- Check For Collision --
            
            if self.GR.x+self.GR.rect[2] > ChopperObj.img.x and self.GR.x < ChopperObj.img.x+ChopperObj.img.rect[2]:
                    if ChopperObj.img.y+ChopperObj.img.rect[3] > self.GR.y:
                            if self.obj_type == "captive":
                                    self.pickUp()
                            else:
                                    crash(self.obj_type)
                                    
                                    
            self.GR.draw()
            # ------ Draw Life --------
            drawLife(self.GR.screen, self.strength, self.GR)
            # ======  FIRE ============
            if self.obj_type == "tank":
                    rand = random.randint(0,game_moneyPayTake['enemyFireIntensity'])
                    if rand == 0:
                            Rockets.append(TMapObjectsRockets(self.GR.x, self.GR.y, ChopperObj))


    def pickUp(self):
            global game_pickedUp
            global game_money
            game_pickedUp = game_pickedUp + 1
            InstrumentsPanel.PbCaptive.setCurrentVal(game_pickedUp)
            game_money += game_moneyPayTake['captiveGet'];
            self.active = 0
            

    def collision(self, force):
            self.strength = self.strength - force
            if self.strength <0:
                    self.active = 0
            


            

############################
#    HELPER FUNCTIONS
############################               

def showAlertWin(txt, waittime, fontSize=48):
    screen = pygame.display.get_surface()
    l = 500
    label = TLabel(screen, txt, 48, 100, 200, l, 150, (255,255,255))
    label.draw()
    pygame.display.flip()
    pygame.time.delay(waittime)     
    



def crash(into_obj):
    global y_speed
    global y_desired_speed
    global ChopperObj
    global game_mode
    global map_ofset
    global MainMenu
    global x_desired_speed
    global y_desired_speed
    global x_speed
    global y_speed
    global MainMenu
    global sound
    global game_captiveCount

    if game_mode == 4:
        return
    if into_obj == "mountain":       
            if game_mode == 3: # GAME OVER
                sound['bomb'].play()                
                showAlertWin("             GAME OVER", 1500)
                MainMenu.BtnStart.txt = "New Game"
                MainMenu.showContinue = False                
                game_mode = 4
                x_desired_speed = 0
                y_desired_speed = 0
                x_speed = 0
                y_speed = 0                 
                print ("END GAME")                
                return        
            if y_speed < 1.1 and abs(x_speed) < 1.1: # Land on the ground
                    y_speed = 0
                    y_desired_speed=0
                    ChopperObj.img.y -= 2
                    if map_ofset > - 10: # Return To Base
                        baseImg, baseRect = load_png("base.png")
                        screen = pygame.display.get_surface()
                        screen.blit(baseImg, (0,0))
                        MainMenu.BtnStart.txt = "Change"
                        MainMenu.showContinue = True                        
                        MainMenu.BackGr = screen.copy()                         
                        game_mode = 4
                        x_desired_speed = 0
                        y_desired_speed = 0
                        x_speed = 0
                        y_speed = 0
                        if game_pickedUp == game_captiveCount:
                            showAlertWin("Well Done!", 1500)
                    return
                

    ChopperObj.strength -= 1
    if ChopperObj.strength <= 0:
        game_mode = 3






def mauntainHeightAtPos(x, selfY=0):
    global png_mountain
    if selfY == 0:
        s = 0
    else:
        s = 400 - selfY
    for q in range(0,395,2):
            absolute_x = int(x)
            color = png_mountain.image.get_at((absolute_x, 395-q))
            color = color[0] +color[1] + color[2] + color[3]
            if color == 0:
                    break
    return 395-q



def drawLife(surface, life, imgObj):
    tmp = life * 4
    if tmp > 5: life_color = Color("green")
    else: life_color = Color("red")
    x_pos = imgObj.x + imgObj.rect[2]/2
    y_pos = imgObj.y + imgObj.rect[3] + 15
    life = tmp
    pygame.draw.rect(surface, life_color, (x_pos, y_pos, life, 2))

            







def InitializeGame(mapXML, chopperXML, chopperBombs, chopperMachineguns):
    global png_backgr
    global png_mountain
    global game_captiveCount
    global game_moneyPayTake
    game_captiveCount = 0
    # ============== Load Map ==================
    mapStr = "Maps/"+mapXML
    doc = xml.dom.minidom.parse(mapStr)
    # --------- Initialize Backgrounds ---------
    bg_far = doc.getElementsByTagName("far_background")[0].firstChild.data
    bg_close = doc.getElementsByTagName("close_background")[0].firstChild.data

    png_backgr = TGrObj(bg_far)        
    png_backgr.drawAt(0, 0)
    png_mountain = TGrObj(bg_close)
    png_mountain.drawAt(0, 0)
    # --------- Initialise ENEMY ---------------
    for obj in doc.getElementsByTagName("object"):
            MapObject.append(TMapObjects(obj.getElementsByTagName("type")[0].firstChild.data,
                                       obj.getElementsByTagName("img")[0].firstChild.data,
                                       obj.getAttribute("sx"),
                                       obj.getAttribute("ex"),
                                       obj.getAttribute("strength")
                                       ))
            if obj.getElementsByTagName("type")[0].firstChild.data == "captive":
                game_captiveCount += 1
    # Map Settings
    game_moneyPayTake['enemyFireIntensity'] = int(doc.getElementsByTagName("enemyFireIntensity")[0].firstChild.data)
    # ========== Load Chopper ==================
    chopperStr = "Choppers/"+chopperXML
    doc = xml.dom.minidom.parse(chopperStr)        
    # --------- Initialise Chopper -------------
    img_a = doc.getElementsByTagName("image_a")[0].firstChild.data
    img_b = doc.getElementsByTagName("image_b")[0].firstChild.data
    settings = doc.getElementsByTagName("chopper")[0]
    ChopperObj = TChopper(img_a, img_b,
                          float(settings.getAttribute("acceleration")),
                          float(settings.getAttribute("speed")),
                          float(settings.getAttribute("climb")),
                          float(settings.getAttribute("strength")),
                          #float(settings.getAttribute("bombs")),
                          float(chopperBombs),
                          float(chopperMachineguns),                          
                          #float(settings.getAttribute("machinegun")),
                          float(settings.getAttribute("cost")),
                          float(settings.getAttribute("bombType")),
                          )

    ChopperObj.img.x =  game_screen_x/2 - ChopperObj.img.rect[2]/2
    ChopperObj.img.y = game_screen_y /3

    screen = pygame.display.get_surface()
    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render("Test", 1, (255, 255, 255))
    screen.blit(text, (200,420))        
    # DRAW PANEL
    Tlen = 10+ ((ChopperObj.climb * 2) * 5)/2
    pygame.draw.line(screen, (255,0,0), (Tlen,424),(Tlen,425))
    ChopperObj.img.y = mauntainHeightAtPos(ChopperObj.img.x +(ChopperObj.img.rect[2]/2) )  - ChopperObj.img.rect[3]  - 20
    #
    return ChopperObj, MapObject








############################
#  Screen and Instruments
############################

    
chopperInstruments_old_dx1 = 0
chopperInstruments_old_dy1 = 0

chopperInstruments_old_dx2 = 0
chopperInstruments_old_dy2 = 0

def chopperInstruments(ChopperObj):
    #global chopperInstruments_old_dx
    global chopperInstruments_old_dx1
    global chopperInstruments_old_dy1
    global chopperInstruments_old_dx2
    global chopperInstruments_old_dy2    
    screen = pygame.display.get_surface()

    dx = abs((x_desired_speed)*8) - 45
    dx = (20 * math.sin(dx* (3.14 /180)))
    dy = (20 * math.cos(dx*4* (3.14 /180))) 
    
    pygame.draw.line(screen, (0,0,0), (chopperInstruments_old_dx1+250, 470-chopperInstruments_old_dy1), (250,470))    
    pygame.draw.line(screen, (255,0,0), (dx+250, 470-dy), (250,470))

    chopperInstruments_old_dx1 = dx
    chopperInstruments_old_dy1 = dy
    # Climbing
    print (y_desired_speed)
    dx = abs((5 - y_desired_speed)*10) - 45
    dx = (20 * math.sin(dx* (3.14 /180)))
    dy = (20 * math.cos(dx*4* (3.14 /180))) 
    
    pygame.draw.line(screen, (0,0,0), (chopperInstruments_old_dx2+300, 470-chopperInstruments_old_dy2), (300,470))    
    pygame.draw.line(screen, (255,0,0), (dx+300, 470-dy), (300,470))

    chopperInstruments_old_dx2 = dx
    chopperInstruments_old_dy2 = dy
    



            






class TMMenuChopperInfo(TProgressBar):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ProgressBar0 = TProgressBar((x+90, y, 60,12), 25, 0, (255,0,0),0)
        self.ProgressBar1 = TProgressBar((x+90, y+18, 60,12), 1.2, 0, (255,0,0))
        self.ProgressBar2 = TProgressBar((x+90, y+18*2, 60,12), 19, 0, (255,0,0))
        self.ProgressBar3 = TProgressBar((x+90, y+18*3, 60,12), 12, 0, (255,0,0))        
        self.ProgressBar4 = TProgressBar((x+90, y+18*5, 60,12), 30, 0, (255,0,0))        
        self.ProgressBar5 = TProgressBar((x+90, y+18*6, 60,12), 122, 0, (255,0,0))
        self.ChopperPrice = "0"
        self.WeaponPrice = "0"
        self.maxBombs = 0
        self.maxMachineguns = 0
        self.curBombs = 0
        self.curMachineguns = 0
        self.maxLife = 0


    def draw(self):
        blit_text("Strength" ,self.x+3, self.y, 16)
        blit_text("Acselerate" ,self.x+3, self.y+18, 16)
        blit_text("Speed" ,self.x+3, self.y+18*2, 16)
        blit_text("Climb" ,self.x+3, self.y+18*3, 16)
        blit_text("Max Bombs" ,self.x+3, self.y+18*5, 16)
        blit_text("Max Machinegun" ,self.x+3, self.y+18*6, 16)
        blit_text("Price" ,self.x+3, self.y+18*4-2, 20)
        blit_text("$ " + self.ChopperPrice  ,self.x+90, self.y+18*4-2, 20)                
        #blit_text("Price" ,self.x+3, self.y+18*7-2, 20)
        #blit_text("$ " + self.WeaponPrice  ,self.x+90, self.y+18*7-2, 20)                            
        self.ProgressBar0.draw()                   
        self.ProgressBar1.draw()
        self.ProgressBar2.draw()
        self.ProgressBar3.draw()
        self.ProgressBar4.draw()
        self.ProgressBar5.draw()

        
    def setIt(self, chopperXML):
        global ChopperObj        
        # ========== Load Chopper ==================
        chopperStr = "Choppers/"+chopperXML
        doc = xml.dom.minidom.parse(chopperStr)    
        settings = doc.getElementsByTagName("chopper")[0]

        self.maxLife = float(settings.getAttribute("strength"))
        self.ProgressBar0.setCurrentVal(self.maxLife)
        self.ProgressBar1.setCurrentVal(float(settings.getAttribute("acceleration")))
        self.ProgressBar2.setCurrentVal(float(settings.getAttribute("speed")))
        self.ProgressBar3.setCurrentVal(float(settings.getAttribute("climb")))
        self.maxBombs = float(settings.getAttribute("bombs"))
        self.ProgressBar4.setCurrentVal(self.maxBombs)
        self.maxMachineguns = float(settings.getAttribute("machinegun"))
        self.ProgressBar5.setCurrentVal(self.maxMachineguns)
        self.ChopperPrice = str(settings.getAttribute("cost"))
        self.WeaponPrice = str(settings.getAttribute("cost"))
      

    def setCurrentChopperInfo(self, life, bombs, mGuns):
        self.ProgressBar0.setExtraVal(life)
        self.ProgressBar4.setExtraVal(bombs)
        self.ProgressBar5.setExtraVal(mGuns)            
       

    def clear(self):
        for q in range(4):
            exec("self.ProgressBar"+str(q)+".currentVal=0")
            exec("self.ProgressBar"+str(q)+".extraVal=0")
            self.ChopperPrice = "0"
            self.WeaponPrice = "0"
            self.maxBombs = 0
            self.maxMachineguns = 0
            self.curBombs = 0
            self.curMachineguns = 0
            self.maxLife = 0            
        

class TMainMenu():
    global game_screen_x
    global game_screen_y
    def __init__(self):            
            self.screen = pygame.display.get_surface()
            self.BackGr = self.screen.copy()
            self.image, self.rect = load_png("Win.png")

            self.width = game_screen_x - 40
            self.height = game_screen_y - 60
            
            self.x = (game_screen_x - self.width) /2
            self.y = (game_screen_y - self.height) /2                        

            self.barImg = pygame.transform.scale(self.image, (14, 120))
            self.image.set_alpha(200)                
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.image.set_alpha(220)
            self.showContinue = False
            # Maps List
            self.mapsListDir = TListDir('Maps/', self.x+25, self.y+50, 150, 100, 16)
            # Choppers List
            self.choppersListDir = TListDir('Choppers/', self.x+25, self.y+185, 150, 130,16)
            # Labels
            self.LabelMap = TLabel(self.screen, self.mapsListDir.ListData[0][0], 16, self.x+175, self.y+50)
            self.LabelChopper = TLabel(self.screen, self.choppersListDir.ListData[0][0], 16, self.x+175, self.y+185,85)
            self.LabelCurrentChopper = TLabel(self.screen, "", 16, self.x+466, self.y+185, 85)            
            # Start Button
            self.BtnStart = TBitButton(self.screen,  "btn1.png", "win2.png", 120, 390, "  Start ", 28, (0,0,0), 100)
            self.BtnContinue = TBitButton(self.screen,  "btn1.png", "win2.png", 280, 390, "Continue ", 28, (255,255,255), 100)            
            self.BtnExit = TBitButton(self.screen,  "btn1.png", "win2.png", 440, 390, "   Exit", 28, (150,0,0), 100)                
            # Buy Sell Buttons
            self.BtnBuy = TBitButton(self.screen,  "btn1.png", "win2.png", self.x+335, self.y+200, "Buy >", 35, (255,255,255), 100)
            self.BtnBuyWeapons = TBitButton(self.screen,  "btn1.png", "win2.png", self.x+335, self.y+290, "Buy >", 35, (255,255,255), 100)            
            # ChopperInfo
            self.MMenuChopperInfo = TMMenuChopperInfo(self.x+175, self.y+205)
            self.MMenuCurrentChopperInfo = TMMenuChopperInfo(self.x+465, self.y+205)
            self.CurrentChopperInfoSet = 0
            

                    
    def draw(self):
            global game_mode
            self.screen.blit(self.BackGr, (0,0))
            self.screen.blit(self.image, (self.x, self.y))

            if self.BtnStart.txt != "New Game": 
                self.mapsListDir.draw()
                self.choppersListDir.draw()
                self.LabelMap.draw()
                self.LabelChopper.draw()
                blit_text("Map" ,self.x+25, self.y+25)
                blit_text("Available Helicopters" ,self.x+25, self.y+160)
                self.MMenuChopperInfo.draw()
                # Buy Sell Buttons
                self.BtnBuy.draw()
                self.BtnBuyWeapons.draw()                
            self.LabelCurrentChopper.draw()
            #Buttons
            self.BtnStart.draw()
            if self.showContinue==True:
                self.BtnContinue.draw()                
            self.BtnExit.draw()

            #Texts
            blit_text("Current Helicopter" ,self.x+465, self.y+160)
            # Money
            blit_text("$ "+str(game_money),self.x+450, self.y+20, 33)
            # Choppers Info
            if self.CurrentChopperInfoSet == 0:
                #self.MMenuCurrentChopperInfo.setCurrentChopperInfo(0,0,0)
                setCurrentChopperInfo = 1


            """
            maxLife = float(self.MMenuCurrentChopperInfo.maxLife)
            cost = float(self.MMenuCurrentChopperInfo.ChopperPrice)
            print (">PPPP >", cost)
            if cost > 0:
                repairPricePerPoint = cost / maxLife
                health, price = self.calculateAmoPrice(maxLife, choperHealth, repairPricePerPoint)
                self.MMenuCurrentChopperInfo.ChopperPrice = str(price)
            """
            
            self.MMenuCurrentChopperInfo.draw()                


            
    
    def mouseClick(self, mouseEvent):
            global game_mode
            global InstrumentsPanel
            global game_money
            global chopperXMLName
            global chopperBombs
            global chopperMachineguns
            global game_moneyPayTake
            global choperHealth
            global ChopperObj
            self.LabelMap.Text(self.mapsListDir.checkEvent(mouseEvent))
            chopperName = self.choppersListDir.checkEvent(self.LabelChopper.txt)
            if chopperName != None:
                self.LabelChopper.Text(chopperName)
                self.MMenuChopperInfo.setIt(chopperName)
           
            # ---- Buy Chopper -----
            if self.BtnBuy.onClick(mouseEvent) == 1 and mouseEvent == MOUSEBUTTONUP and self.LabelChopper.txt != "":
                print ("AAAAA>>>>", self.LabelChopper.txt)
                chopperXMLName = self.LabelChopper.txt
                chopperName = chopperXMLName
                if ChopperObj != None:
                    maxLife = float(self.MMenuCurrentChopperInfo.ProgressBar0.currentVal)
                    Health = self.MMenuCurrentChopperInfo.ProgressBar0.extraVal                
                    cost = float(self.MMenuCurrentChopperInfo.ChopperPrice)
                    repairPricePerPoint = cost / maxLife
                    health, price = self.calculateAmoPrice(maxLife, Health, repairPricePerPoint)
                    print ("maxLife:", maxLife, " choperHealth:",choperHealth, " repairPricePerPoint:",repairPricePerPoint)
                    print (">>>> HEALTH:", health, " PRICE:", price)
                    choperHealth = self.MMenuChopperInfo.ProgressBar0.currentVal
                    game_money += (float(self.MMenuCurrentChopperInfo.ChopperPrice)- price)
                    game_money -= float(self.MMenuChopperInfo.ChopperPrice)
                    
                else:
                    health = 0
                    choperHealth = self.MMenuChopperInfo.ProgressBar0.currentVal
                    price = float(self.MMenuChopperInfo.ChopperPrice)
                    game_money = game_money + float(self.MMenuCurrentChopperInfo.ChopperPrice)
                    choperHealth += health
                    game_money -=price
                    


                curPrice = float(self.MMenuCurrentChopperInfo.ChopperPrice) 
                newPrice = float(self.MMenuChopperInfo.ChopperPrice)
                #if (game_money + curPrice - newPrice) < 0:
                #    showAlertWin("Insufficient Balance", 1500)
                #    return

                self.LabelCurrentChopper.txt = self.LabelChopper.txt                
                self.MMenuCurrentChopperInfo.setIt(self.LabelChopper.txt)




            # ---- Buy Weapons -----
            if self.BtnBuyWeapons.onClick(mouseEvent) == 1 and mouseEvent == MOUSEBUTTONUP:
                if chopperXMLName == None:
                    showAlertWin("Buy Helicopter First.", 1000)
                    return
                moreMachineguns,price = self.calculateAmoPrice(self.MMenuCurrentChopperInfo.maxMachineguns,
                                       self.MMenuCurrentChopperInfo.ProgressBar5.extraVal,
                                       game_moneyPayTake['machineGunPrice'],1)
                chopperMachineguns += moreMachineguns
                game_money -=price

                moreChopperBombs,price = self.calculateAmoPrice(self.MMenuCurrentChopperInfo.maxBombs,
                                       self.MMenuCurrentChopperInfo.ProgressBar4.extraVal,
                                       game_moneyPayTake['bombPrice'])
                chopperBombs += moreChopperBombs
                game_money -=price


            self.MMenuCurrentChopperInfo.setCurrentChopperInfo(choperHealth, chopperBombs, chopperMachineguns)
            if ChopperObj != None: # Refresh instruments panel
                ChopperObj.strength = choperHealth
                ChopperObj.bombCount = chopperBombs            
                ChopperObj.machinegunCount = chopperMachineguns
            if InstrumentsPanel:
                InstrumentsPanel.PbBombs.setCurrentVal(chopperBombs)
                InstrumentsPanel.PbMgun.setCurrentVal(chopperMachineguns)                

                
          
            # -- Start New Game ----
            if self.BtnStart.onClick(mouseEvent) == 1:
                if self.BtnStart.txt == "New Game":
                    game_money = game_moneyPayTake['startingNewGameMoney']
                    self.BtnStart.txt = " Start "
                    self.showContinue = False;
                    self.MMenuCurrentChopperInfo.clear()
                    chopperXMLName = None
                    ChopperObj = None
                    return
                if chopperXMLName == None:
                    showAlertWin("Buy helicopter first!", 1500)                    
                    return
                #game_money = game_moneyPayTake['startingNewGameMoney']                
                game_mode = 5 # Restart Game
            # ------- Quit ---------
            if self.BtnExit.onClick(mouseEvent) == 1: 
                print ("QUIT by user request.")
                game_mode = 10
            # ----- Continue -------
            if self.showContinue==True and self.BtnContinue.onClick(mouseEvent) == 1: 
                InstrumentsPanel.draw()
                game_mode = 2



    def calculateAmoPrice(self, maxAmo, curAmo, AmoCost, HalfBalance=0):
        global game_money
        #print "maxAmo:",maxAmo," curAmo:",curAmo," AmoCost:",AmoCost, " game_money:", game_money        
        if HalfBalance == 1:
            game_money1 = game_money / 2
        else:
            game_money1 = game_money
        price = (maxAmo- curAmo) * AmoCost
        if price >= game_money1: # Insufficiant Balance
            weaponsCanBy =  game_money1 / AmoCost
            #print "weaponsCanBuy:", weaponsCanBy
            if weaponsCanBy <= 0:
                return 0, 0                
            price = weaponsCanBy * AmoCost
        else:                    # Buy maximum amount
            weaponsCanBy = maxAmo - curAmo
        return weaponsCanBy, price




class TInstrumentBar(TProgressBar, TLabel):
    def __init__(self, rectArea, maxVal, currentVal, LabelTxt, SelColor=(255,0,0)):
        self.screen = pygame.display.get_surface()        
        self.ProgressBar = TProgressBar(rectArea, maxVal, currentVal, SelColor)
        self.Label = TLabel(self.screen, LabelTxt, 12, rectArea[0]-52, rectArea[1], 50, 255, (0,0,0) )

    def draw(self):
        self.ProgressBar.draw()
        self.Label.draw()

    def setCurrentVal(self, val):
        self.ProgressBar.setCurrentVal(val)
        
        


class TInstrumentsPanel():
    global game_screen_x
    global game_screen_y
    global ChopperObj
    global game_captiveCount
    global MainMenu
    def __init__(self):
            self.screen = pygame.display.get_surface()
            self.image, self.rect = load_png("instruments_panel1.png")

            self.width = game_screen_x
            self.height = game_screen_y - (game_screen_y - 80)                
            self.x = 2
            self.y = game_screen_y - 81
            # MainMenu Button
            self.BtnMenu = TBitButton(self.screen,  "btn1.png", "win2.png", 580, 455, "Main Memu", 18, (0,0,0), 150)                
            # Bombs
            maxBombs = MainMenu.MMenuCurrentChopperInfo.maxBombs            
            self.PbBombs = TInstrumentBar((636, 410, 40,14),maxBombs,ChopperObj.bombCount, "Bombs")
            # MachineGun
            maxMachineguns = MainMenu.MMenuCurrentChopperInfo.maxMachineguns
            self.PbMgun = TInstrumentBar((636, 430, 40,14),maxMachineguns,ChopperObj.machinegunCount, "Gun")
            # Life
            self.PbLife = TInstrumentBar((535, 410, 40,14),ChopperObj.strength,ChopperObj.strength, "Life")            
            # Captives
            self.PbCaptive = TInstrumentBar((535, 430, 40,14),game_captiveCount, 0, "Captive", (0,255,0))                        
            # Money
            #self.MoneyLabelA = TLabel(self.screen, "Money" , 14, 482, 450, 53, 255, (0,0,0))
            #self.MoneyLabelB = TLabel(self.screen, "$"+str(game_money) , 14, 537, 450, 38, 255, (0,0,0))            

    def draw(self):
            self.screen.blit(self.image, (self.x, self.y))
            self.BtnMenu.draw()
            #Instruments
            self.PbBombs.draw()
            self.PbMgun.draw()
            self.PbLife.draw()
            self.PbCaptive.draw()
            #self.MoneyLabelA.draw()
            #self.MoneyLabelB.draw()









############################
#           MAIN
############################




def main():
    global map_ofset
    global rockets_max
    global Rockets
    global png_mountain
    global MapObject
    global game_pickedUp
    global game_screen_x
    global game_screen_y
    global ChopperObj
    global x_desired_speed 
    global x_speed
    global y_desired_speed 
    global y_speed
    global game_mode
    global InstrumentsPanel
    global MainMenu
    global chopperXMLName
    global choperHealth
    global chopperBombs
    global chopperMachineguns
    global game_money
    global sound
    global instrumentsSubsurface

    game_fallAfterHit = 1  
    key_event = 0
    # ---------------------
    #       SOUNDS
    # ---------------------    
    pygame.mixer.init()
    sound['bomb'] = pygame.mixer.Sound("Sounds/bomb-03.wav") 

    # --------- Initialize screen --------------
    pygame.init()
    #screen = pygame.display.set_mode((game_screen_x, game_screen_y),pygame.FULLSCREEN) 
    screen = pygame.display.set_mode((game_screen_x, game_screen_y) , pygame.DOUBLEBUF)
    
    pygame.display.set_caption('Rescue 1')
    # ------- Initialize Main Menu -------------
    BackGr, BackRect = load_png("startup.png")
    screen.blit(BackGr, (0,0))
    pygame.display.flip()
    
    MainMenu = TMainMenu()
    MainMenu.MMenuChopperInfo.setIt(MainMenu.LabelChopper.txt)
    


    pygame.display.flip()




    

    # Event loop
    key_event = 1
    key_event_left = 0
    key_event_right = 0
    key_event_up = 0
    key_event_down = 0        
    while 1:
            if game_mode==10: # QUIT
                    break; 
            pygame.time.delay(28)            
            for event in pygame.event.get():
                    if event.type == QUIT:
                            return

                    if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                            if game_mode == 0 or game_mode==4 or game_mode==4.5:
                                    MainMenu.mouseClick(event.type)
                            elif game_mode == 2:
                                    if InstrumentsPanel.BtnMenu.onClick(event.type) == 1:
                                            print ("Pause Game")
                                            MainMenu.BtnStart.txt = "New Game"

                                            MainMenu.showContinue = True
                                            MainMenu.BackGr = screen.copy()                                        
                                            game_mode = 4 # Pause Game
                                    InstrumentsPanel.draw()


                    if event.type == KEYDOWN:
                            if event.key == K_RIGHT:
                                    key_event_right = 1
                            elif event.key == K_LEFT:
                                    key_event_left = 1
                            elif event.key == K_UP:
                                    key_event_up = 1
                            elif event.key == K_DOWN:
                                    key_event_down = 1
                            # Throw Bomb        
                            elif event.key == K_z:
                                    ChopperObj.fireBomb()
                                    print ("BOMB!")
                            # Fire Machine Gun                                    
                            elif event.key == K_SPACE:
                                    ChopperObj.fireMachineGun()                                        

                    if event.type == KEYUP:
                            if event.key == K_RIGHT:
                                    key_event_right = 0
                            elif event.key == K_LEFT:
                                    key_event_left = 0
                            elif event.key == K_UP:
                                    key_event_up = 0
                            elif event.key == K_DOWN:
                                    key_event_down = 0

            if game_mode == 0:
                ChopperObj = None
                MapObject = []
                MainMenu.draw()


            elif game_mode == 1:
                # ====== Prepare Game Scene ======
                print (">>>>>",chopperBombs)
                ChopperObj,MapObject = InitializeGame(MainMenu.LabelMap.txt, chopperXMLName, chopperBombs, chopperMachineguns)
                InstrumentsPanel = TInstrumentsPanel()                
                InstrumentsPanel.draw()
                pygame.display.flip()

                game_mode = 2

            elif game_mode == 4: # PAUSE GAME
                print ("end game 2")                
                choperHealth = float(ChopperObj.strength)
                chopperBombs = int(ChopperObj.bombCount)
                chopperMachineguns = int(ChopperObj.machinegunCount)
                MainMenu.MMenuCurrentChopperInfo.setCurrentChopperInfo(choperHealth, chopperBombs, chopperMachineguns)
                game_mode = 4.5


            elif game_mode == 4.5:
                MainMenu.draw()
                
            elif game_mode == 5: # Reset All Parameters and atart new game
                ChopperObj = None
                MapObject = []
                game_mode = 1
                                
                    
            elif game_mode == 2 or game_mode == 3:
                # ========= GAME LOOP ============
                if game_mode==2 and (key_event_right==1 or key_event_left==1 or key_event_up==1 or key_event_down==1):
                        if key_event_right == 1 and x_desired_speed > -ChopperObj.speed:
                                x_desired_speed -= 1
                        if key_event_left == 1 and x_desired_speed < ChopperObj.speed:
                                x_desired_speed += 1
                        if key_event_up == 1 and y_desired_speed > -ChopperObj.climb:
                                y_desired_speed -= 1
                        if key_event_down == 1 and y_desired_speed < ChopperObj.climb:
                                y_desired_speed += 1
                else:
                        if x_desired_speed >0:
                                x_desired_speed -= 1
                        if x_desired_speed <0:
                                x_desired_speed += 1

                        if y_desired_speed > 0:
                                y_desired_speed -= 1
                        if y_desired_speed < 0:
                                y_desired_speed += 1

                        if ChopperObj.strength > choperHealth/2:
                            if abs(x_speed) <0.05:
                                x_desired_speed = 0.0
                                x_speed = 0
                        else:
                            dmg = int(choperHealth - ChopperObj.strength)
                            dmg1 = random.randint(-dmg,dmg) / 10.0
                            
                            x_desired_speed += dmg1
                            y_desired_speed += dmg1


                if game_mode == 3: # Hit and fall
                    y_desired_speed = y_desired_speed + game_fallAfterHit

                                     

                if x_speed < x_desired_speed:
                        x_speed += ChopperObj.acceleration
                if x_speed > x_desired_speed:
                        x_speed -= ChopperObj.acceleration
                if y_speed < y_desired_speed:
                        y_speed += ChopperObj.acceleration *0.2
                if y_speed > y_desired_speed:
                        y_speed -= ChopperObj.acceleration * 0.15


                chopperInstruments(ChopperObj)
                     
                # Calculate Background Position
                png_backgr.x = png_backgr.x + x_speed / 4
                map_ofset = png_backgr.x
                png_backgr.draw()

                # Limit To The End Of The Map
                if png_mountain.x > 10:
                        x_speed = -1
                if png_mountain.x < -(png_mountain.rect[2] - game_screen_x):
                        x_speed = 1
                # Draw Background                
                png_mountain.x = png_mountain.x + x_speed 
                map_ofset = png_mountain.x
                png_mountain.draw()                
                # Draw Chopper
                if ChopperObj.img.y <0:
                        y_speed = 0
                        ChopperObj.img.y += 1
                ChopperObj.img.y = ChopperObj.img.y + y_speed
                ChopperObj.draw(x_speed)
                # Collision With Mountain Detect
                x1 = int(-map_ofset+(ChopperObj.img.x)+6)
                x2 = int(-map_ofset+((ChopperObj.img.x+ChopperObj.img.rect[2])-6))
                y = int(ChopperObj.img.y + ChopperObj.img.rect[3])-2
                colorA = png_mountain.image.get_at((x1,y))
                colorA = colorA[0]+colorA[1]+colorA[2]+colorA[3]
                colorB = png_mountain.image.get_at((x2,y))
                colorB = colorB[0]+colorB[1]+colorB[2]+colorB[3]

              

                if colorA != 0 or colorB !=0:
                        crash('mountain')
                        

                # ------- Update Enemies -----------
                q = 0
                for MapObj in MapObject:
                        if MapObj.active == 1:
                                MapObj.update(png_mountain, ChopperObj)
                        else:
                                game_money += game_moneyPayTake['captiveKilled']
                                MapObject.pop(q)
                        q += 1                                        
                # -------- Update Rockets -----------
                q=0
                for Rocket in Rockets:
                        if Rocket.active == 1:
                                Rocket.update()
                        else:
                                Rockets.pop(q)
                        q +=1
                # =========================================


           
            pygame.display.flip()            



if __name__ == '__main__': main()
pygame.quit()
