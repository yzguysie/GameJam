import pygame
from pygame import gfxdraw
from pygame import mixer
from functools import partial

pygame.init()

mixer.init()
import random
import math
import time
import winsound
import ui
import os
#from win32gui import FindWindow, GetWindowRect
    
from configparser import ConfigParser

config = ConfigParser()
player_sprite = True
obstacle_sprite = True
hazard_sprite = True
portal_sprite = False

screen_width, screen_height = 768, 432





#MAKE "BUMP pads" that PUSH you like terracotta in minecraft (Like sideways jump pad or those thingies in edge)
fps = 120
tickrate = 120
width = 1600
height = 900

grid_width = round(width/32)
grid_height = round(height/18)
xscale = screen_width/width
yscale = screen_height/height
xscale = yscale
real_xscale = screen_width/width

autosave = True

window = pygame.display.set_mode([screen_width, screen_height], pygame.RESIZABLE)
pygame.display.set_caption("Game Jam Game")

font = 'arial'
font_width = int(16)
dialogue_font = pygame.font.SysFont(font, font_width)

white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
light_gray = (192, 192, 192)
dark_gray = (64, 64, 64)
red = (255, 0, 0)
blue = (85, 171, 255)
bg_blue = (64, 84, 128)
green = (85, 255, 171)
purple = (255, 64, 255)
yellow = (255,255,0)
blue_black = (6, 8, 32)
light_blue_black = (24, 32, 64)
BACKGROUND_COLOR = bg_blue

clock = pygame.time.Clock()

show_hitboxes = False

autoscroll = False
autoscroll_start_x = round(width/3)
autoscroll_end_x = round(2*width/3)
autoscroll_start_y = round(height-height/3*2)
autoscroll_end_y = round(height-height/3)
autoscroll_smoothness = fps/15
autoscroll_offset_x = 0
autoscroll_offset_y = 0

player_circle = False
world_height_limit = -5000
class Sprite():
    def __init__(self, image, x, y, rotation):
        self.x = x
        self.y = y
        self.ogimage = image
        self.rotation = rotation
        self.last_rotation = rotation
        self.target_rotation = rotation
        self.image = pygame.transform.rotate(self.ogimage, self.rotation)
        self.centered = False

    def draw(self):
        self.image = pygame.transform.rotate(self.ogimage, self.rotation)
        if self.centered:
            window.blit(self.image, (self.x-self.image.get_width()/2, self.y-self.image.get_height()/2))
        else:
            x_offset = (self.image.get_width()-self.ogimage.get_width())/2
            y_offset = (self.image.get_height()-self.ogimage.get_height())/2
            window.blit(self.image, (self.x-x_offset, self.y-y_offset))
        


    def set_centered(self, centered):
        self.centered = centered


class Player():
    def __init__(self):
        self.x = 0  # consider x and y combined with a position struct, self.pos.x, self.pos.y
        self.xspeed = 0 # consider a Velocity struct (vector) with x and y components
        self.yspeed = 0
        # consider nametuple "Dimensions" with width/height for the following 2, then you can have normDimensions, minDimensions, and dimensions
        self.normwidth = 50
        self.normheight = 50
        self.miniwidth = math.sqrt(1)/2.1*self.normwidth
        self.miniheight = math.sqrt(1)/2.1*self.normheight
        self.width = 50
        self.height = 50
        self.y = height-self.height
        self.color = green
        self.jump_height = 17.5
        self.mini_jump_height = math.sqrt(3)/2*self.jump_height
        self.max_speed_x = 10
        self.max_speed_y = 25
        self.on_ground = False
        self.holding_jump = False
        self.mini = False
        self.gravity = gravity
        self.acceleration = .85
        self.fancy = True
        self.rotation = 0
        self.sprite = None
        self.interpolation_offset_x = 0
        self.interpolation_offset_y = 0
        # self.image = sprite()

    def die(self):
        global player_random
        #self.gravity = abs(self.gravity)
        self.x = 0
        self.y = height-self.height
        self.xspeed = 0
        self.yspeed = 0
        self.width = self.normwidth
        self.height = self.normheight
        self.mini = False
        self.on_ground = False
        self.holding_jump = False
        if player_random and False:
            if self in players:
                players.remove(self)
            player = Player()
            player.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            player.width = (random.randint(10, 50))
            player.height = (random.randint(10, 50))
            player.normwidth = player.width
            player.normheight = player.height
            player.miniwidth = player.width/math.sqrt(2)
            player.miniheight = player.height/math.sqrt(2)
            player.jump_height = random.randint(17, 30)
            player.mini_jump_height = player.jump_height/1.2
            player.max_speed_x = random.uniform(5, 20)
            player.max_speed_y = random.uniform(10, 50)
            player.acceleration = random.uniform(.5, 2)
            players.append(player)
        self.gravity = abs(self.gravity)

        # Clean this up - repeated code and loads every time player dies
        self.set_sprite(player_default_image)

    def set_sprite(self, image):
        #Clean this up - does same thing as make_sprite
        sprite_width, sprite_height = round(self.width*xscale), round(self.height*yscale)
        sprite_image = pygame.transform.smoothscale(image, (sprite_width, sprite_height))
        self.sprite = Sprite(sprite_image, self.x*xscale, self.y*yscale, self.rotation)
        self.sprite.set_centered(False)
       
    def draw(self):
        self.do_rotation()
        if player_sprite:
            if (fps > tickrate):
                interpolation_frames = int(fps/tickrate)
                if frames%(interpolation_frames) == 0:
                    self.interpolation_offset_x = 0
                else:
                    self.interpolation_offset_x = self.xspeed*gamespeed * (frames%interpolation_frames)/interpolation_frames
                
                if frames%(interpolation_frames) == 0:
                    self.interpolation_offset_y = 0
                else:
                    self.interpolation_offset_y = self.yspeed*gamespeed * (frames%interpolation_frames)/interpolation_frames
            self.sprite.x = ((self.x+self.interpolation_offset_x)-autoscroll_offset_x)*xscale
            self.sprite.y = ((self.y+self.interpolation_offset_y)-autoscroll_offset_y)*yscale
            self.sprite.width = self.width*xscale
            self.sprite.height = self.height*yscale
            self.sprite.draw()
            return
                
    def on_surface(self):
        if self.gravity >= 0:
            if self.y >= height-(ground_height+self.height):
                #self.y = height-(ground_height+self.height)
                return True
        else:
            if self.y <= world_height_limit:
                #self.y = world_height_limit
                return True

        for obstacle in obstacles:
            if self.is_on(obstacle):
                return True

        return False

    def touching_surface(self):
        if self.on_surface():
            return True
        
        if self.gravity >= 0:
            if self.y >= height-(ground_height+self.height):
                return True
        else:
            if self.y <= world_height_limit:
                return True

        for obstacle in obstacles:
            if self.is_touching_no_generosity(obstacle):
                return True

        return False

    def do_collision(self):
        # Clean this up - fix collision
        hitting = False
        for obstacle in obstacles:
            player_top = self.y
            player_bottom = self.y+self.height
            player_right = self.x+self.width
            player_left = self.x
            box_top = obstacle.y
            box_bottom = obstacle.y+obstacle.height
            box_right = obstacle.x+obstacle.width
            box_left = obstacle.x
            player_x_speed = self.xspeed*gamespeed
            player_y_speed = self.yspeed*gamespeed
            gravity_sign = (self.gravity/abs(self.gravity))
            #If hitting left side stop
            if player_right > box_left and player_right <= box_left + player_x_speed+1:
                if player_bottom-self.height/4 > box_top+player_y_speed*gravity_sign and player_top+player_y_speed*gravity_sign < box_bottom-self.height/4: # -self.height/4 for leeway so if almost on top of block it gives it to you
                    self.x = obstacle.x-self.width
                    self.xspeed = 0

                    
                    hitting = True

            #if hitting right side stop
            if player_left < box_right and player_left-player_x_speed >= box_right + 0:
                if player_bottom-self.height/4 > box_top-(player_y_speed)*gravity_sign and player_top+(player_y_speed)*gravity_sign < box_bottom-self.height/4: #Thought this caused the Catching on right side of column but i dont know
                #if player_bottom-self.height/4 > box_top-abs(player_y_speed)*gravity_sign and player_top+abs(player_y_speed)*gravity_sign < box_bottom-self.height/4: #Thought this is right but i dont think so
                    self.x = box_right
                    self.xspeed = 0

                    hitting = True

            if self.gravity >= 0:
                #if hitting top of block
                #if player_right-player_x_speed > box_left and player_left+player_x_speed < box_right: #Caused player hitting right side of column of blocks to get "Caught" idk if good tho
                if player_right-abs(player_x_speed) > box_left and player_left+abs(player_x_speed) < box_right:# Idk if abs is good
                    if player_bottom > box_top and player_top < box_bottom:
                        hitting = True
                        #if player_top < box_top: (Bad on low fps)
                        if player_top < box_top+player_y_speed:
                            
                            self.y = obstacle.y-self.height
                            self.yspeed = 0

                        #if hitting bottom
                        elif self.yspeed < 0:
                            self.yspeed = 0
                            self.y = obstacle.y+obstacle.height
            else:
               
                #if hitting bottom of block
                if self.x+self.width-self.xspeed*gamespeed > obstacle.x and self.x+self.xspeed*gamespeed < obstacle.x+obstacle.width:
                    if player_bottom > box_top and player_top < box_bottom:
                        hitting = True
                        #if player_bottom > box_bottom: (Bad on low fps)
                        if player_bottom-player_y_speed > box_bottom:
                            self.y = box_bottom
                            self.yspeed = 0
                            

                        #if hitting top   
                        elif self.yspeed > 0:
                            self.yspeed = 0
                            self.y = obstacle.y-self.height

        for hazard in hazards:
            if self.is_touching(hazard):
                self.die()
        return hitting


    def is_touching_no_generosity(self, obstacle):
        if self.x+self.width >= obstacle.x and self.x <= obstacle.x+obstacle.width:
            return self.y+self.height >= obstacle.y and self.y <= obstacle.y+obstacle.height

        return False

    def is_touching(self, obstacle):
        if self.x+self.width-self.width/4 > obstacle.x and self.x+self.width/4 < obstacle.x+obstacle.width:
            return self.y+self.height-self.height/4 >= obstacle.y and self.y+self.height/4 <= obstacle.y+obstacle.height

        return False


    def is_on(self, obstacle):
        player_top = self.y
        player_bottom = self.y+self.height
        player_right = self.x+self.width
        player_left = self.x
        box_top = obstacle.y
        box_bottom = obstacle.y+obstacle.height
        box_right = obstacle.x+obstacle.width
        box_left = obstacle.x
        player_x_speed = self.xspeed*gamespeed
        player_y_speed = self.yspeed*gamespeed
        gravity_sign = (self.gravity/abs(self.gravity))
        rightside_up = self.gravity >= 0
        on_x = player_right-player_x_speed > box_left and player_left-player_x_speed < box_right
        on_y = False

        if on_x:

            if rightside_up:
                on_y = player_bottom >= box_top and player_top <= box_top


            else:
                on_y = player_top <= box_bottom and player_bottom >= box_bottom

        return on_x and on_y
        
        
            
    def do_rotation(self):
        if self.touching_surface():
            if self.sprite.rotation % 90 > 45:
                self.sprite.target_rotation = self.sprite.rotation -self.sprite.rotation % 90 +90
            else:
                self.sprite.target_rotation = self.sprite.rotation -self.sprite.rotation % 90
        else:
            self.apply_friction(flat_friction*air_friction_mult, multiplicative_friction*air_friction_mult)
            self.sprite.target_rotation -= 360/fps*self.xspeed/self.max_speed_x*(self.gravity/abs(self.gravity))
        smoothness = fps/15
        self.sprite.rotation += (self.sprite.target_rotation-self.sprite.rotation)/max(1,smoothness) 
               
           
       
   
    def tick(self):
        global obstacles
        self.apply_gravity()
        if self.touching_surface():
            self.apply_friction(flat_friction, multiplicative_friction)
            
        self.get_instructions()
        self.x += self.xspeed*gamespeed
        self.y += self.yspeed*gamespeed
        self.do_collision()
           
        if self.y < world_height_limit:
            self.y = world_height_limit
            self.yspeed = 0

        if self.y+self.height > height:
            self.y = height-self.height
           
        if self.on_surface():
            self.yspeed = 0

       
        #self.do_collision()


    def apply_friction(self, flat_friction, multiplicative_friction):
        if self.xspeed > flat_friction*gamespeed:
            self.xspeed -= flat_friction*gamespeed
            self.xspeed -= self.xspeed*multiplicative_friction*gamespeed
        elif self.xspeed < -flat_friction*gamespeed:
            self.xspeed += flat_friction*gamespeed
            self.xspeed -= self.xspeed*multiplicative_friction*gamespeed

        else:
            self.xspeed = 0
    def apply_gravity(self):
        if self.mini:
            self.yspeed += self.gravity*gamespeed
        else:
            self.yspeed += self.gravity*gamespeed
        if self.yspeed > self.max_speed_y:
            self.yspeed = self.max_speed_y
        if self.yspeed < -self.max_speed_y:
            self.yspeed = -self.max_speed_y

    def get_instructions(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.xspeed += self.acceleration*gamespeed
            if self.xspeed > self.max_speed_x:
                self.xspeed = self.max_speed_x
               
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.xspeed -= self.acceleration*gamespeed
            if self.xspeed < -player.max_speed_x:
                self.xspeed = -player.max_speed_x
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or (pygame.mouse.get_pressed()[0] and not editing and not mouse_over_anything())) and self.on_surface():
            self.jump()


    def jump(self):
        #dislike_sfx = pygame.mixer.Sound("dislike.mp3")
        #dislike_sfx.play()
        if self.mini:
            self.yspeed = -self.mini_jump_height*(abs(self.gravity)/self.gravity)
        else:
            self.yspeed = -self.jump_height*(abs(self.gravity)/self.gravity)
           
        if self.yspeed < -player.max_speed_y:
            self.yspeed = -player.max_speed_y


    def set_mini(self, mini):
        if mini:
            self.width = self.miniwidth
            self.height = self.miniheight
            self.mini = True
        else:
            self.width = self.normwidth
            self.height = self.normheight
            self.mini = False
        
        self.set_sprite(player_default_image)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = light_gray
        self.outline_color = gray
        self.rotation = 0
        self.costume = 0

    def __repr__(self):
        split_character = "@"
        return str(self.x) + split_character + str(self.y) + split_character + str(self.width) + split_character + str(self.height) + split_character + str(self.rotation) + split_character + str(self.costume) + split_character + str(self.color) + split_character + str(self.outline_color) 

    def draw(self):
        if obstacle_sprite:
            update_sprite(self)
            self.sprite.draw()
            return

        self.x = round(self.x)
        self.y = round(self.y)
        self.width = round(self.width)
        self.height = round(self.height)
        
        self.rect = (self.x*xscale, self.y*yscale, self.width*xscale, self.height*yscale)
        pygame.gfxdraw.box(window, self.rect, self.color)
        pygame.gfxdraw.rectangle(window, self.rect, self.outline_color)

    def tick(self):
        pass
class Hazard:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = red
        self.type = 1
        self.rotation = 0

    def __repr__(self):
        # Clean this up - repeated code and what is f (should put into func)
        f = "@"
        return str(self.x) + f + str(self.y) + f + str(self.width) + f + str(self.height) + f + str(self.rotation) + f + str(self.type) + f + str(self.color)
    
    def draw(self):
        if show_hitboxes:
            pygame.gfxdraw.rectangle(window, (round((self.x+self.width/4-autoscroll_offset_x)*xscale), round((self.y+self.height/4-autoscroll_offset_y)*yscale), round(self.width/2*xscale), round(self.height/2*yscale)), red)

            
        if hazard_sprite:
            update_sprite(self)
            self.sprite.draw()
            return
        if self.type == 1:
            outline = .667
            color = (self.color[0]*outline, self.color[1]*outline, self.color[2]*outline)
            if self.rotation < 180:
                pygame.gfxdraw.filled_trigon(window, round(self.x*xscale), round((self.y+self.height-self.height*(self.rotation/180))*yscale), round((self.x+self.width/2+self.width/2*(self.rotation/180))*xscale), round((self.y+self.height*(self.rotation/180))*yscale), round((self.x+self.width-self.width*(self.rotation/180))*xscale), round((self.y+self.height)*yscale), self.color)
            elif self.rotation == 180:
                pygame.gfxdraw.filled_trigon(window, round(self.x*xscale), round(self.y*yscale), round((self.x+self.width/2)*xscale), round((self.y+self.height)*yscale), round((self.x+self.width)*xscale), round(self.y*yscale), self.color)
            else:
                pass
            
            
        if self.type == 2:
            self.rect = (self.x*xscale, self.y*yscale, self.width*xscale, self.height*yscale)
            pygame.gfxdraw.box(window, self.rect, self.color)

    def tick(self):
        pass
        

class Portal:
    def __init__(self, x, y, width, height, type_):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mode = type_
        self.contacting = False
        self.rotation = 0
        if self.mode == 0:
            self.color = gray

        elif self.mode == 1:
            self.color = yellow
   
        elif self.mode == 2:
            self.color = blue

        elif self.mode == 3:
            self.color = green

        elif self.mode == 4:
            self.color = purple

        elif self.mode == 5:
            self.color = red

        elif self.mode == 6:
            self.color = gray
        
        else:
            self.color = white

    def __repr__(self):
        # Clean this up - unreadable (what is f)
        f = "@"
        return str(self.x) + f + str(self.y) + f + str(self.width) + f + str(self.height) + f + str(self.mode) + f + str(self.rotation)

    def apply(self, player):
        if self.mode == 1:
            if player.gravity > 0:
                player.gravity = -player.gravity
                if player.yspeed > player.max_speed_y/2:
                    player.yspeed = player.max_speed_y/2
        elif self.mode == 2:
            if player.gravity < 0:
                player.gravity = -player.gravity
                if player.yspeed < -player.max_speed_y/2:
                    player.yspeed = -player.max_speed_y/2


        elif self.mode == 3:
            player.mini = False
            player.set_mini(player.mini)

        elif self.mode == 4:
            player.mini = True
            player.set_mini(player.mini)

        elif self.mode == 5:
            player.yspeed = -player.max_speed_y*(abs(player.gravity)/player.gravity)

        elif self.mode == 6:
            global level_num
            global load_new_level
            if self in portals:
                level_num += 1
                load_new_level = True
                portals.remove(self)
            
    def tick(self):
        for player in players:
            if self.check_collision(player):
                self.apply(player)

    def check_collision(self, player):
        if player.x+player.width > self.x and player.x < self.x+self.width:
            if player.y+player.height > self.y and player.y < self.y+self.height:
                return True
        return False

    def draw(self):
        update_sprite(self)
        self.sprite.draw()
        return
        if show_hitboxes:
            pygame.gfxdraw.rectangle(window, (round((self.x-autoscroll_offset_x)*xscale), round((self.y-autoscroll_offset_y)*yscale), round(self.width*xscale), round(self.height*yscale)), red)



        if self.mode == 5:
            rect = pygame.Rect(round((self.x-autoscroll_offset_x)*xscale), round((self.y-autoscroll_offset_y)*yscale), round(self.width*xscale), round(self.height*yscale))
            pygame.gfxdraw.box(window, rect, self.color)
            return 

        lowest = .5
        highest = 1
        pygame.gfxdraw.aaellipse(window, round(((self.x-autoscroll_offset_x))*xscale), round(((self.y-autoscroll_offset_y))*yscale), round((self.width/2)*xscale), round((self.height/2)*yscale), self.color)


class Level():
   
    def __init__(self, data):
        #print("Attempting to load: " + data)
        #try:
            if data == "":
                self.player = Player()
                self.obstacles = []
                self.hazards = []
                self.portals = []
                self.objects = []
                return
            data = data.split("|")
            player_data = data[0].split(" ")
            obstacle_data = data[1].split("/")
            for i in range(len(obstacle_data)):
                obstacle_data[i] = obstacle_data[i].split("@")


            hazard_data = data[2].split("/")
            for i in range(len(hazard_data)):
                hazard_data[i] = hazard_data[i].split("@")

            portal_data = data[3].split("/")
            for i in range(len(portal_data)):
                portal_data[i] = portal_data[i].split("@")
            
            self.player = Player()
            if len(player_data) == 2:
                self.player.x = float(player_data[0])
                self.player.y = float(player_data[1])
            
    
            self.obstacles = []
            for obstacle in obstacle_data:
                if len(obstacle) > 3:
                    new_obstacle = Obstacle(float(obstacle[0]), float(obstacle[1]), float(obstacle[2]), float(obstacle[3]))
                    if len(obstacle) > 4:
                        new_obstacle.rotation = float(obstacle[4])
                    self.obstacles.append(new_obstacle)
                    

            self.hazards = []
            for hazard in hazard_data:
                if len(hazard) > 3:
                    new_hazard = Hazard(float(hazard[0]), float(hazard[1]), float(hazard[2]), float(hazard[3]))
                    if len(hazard) > 4:
                        new_hazard.rotation = float(hazard[4])
                    self.hazards.append(new_hazard)

            self.portals = []
            for portal in portal_data:
                if len(portal) > 4:
                    new_portal = Portal(float(portal[0]), float(portal[1]), float(portal[2]), float(portal[3]), int(portal[4]))
                    if len(portal) > 5:
                        new_portal.rotation = float(portal[5])
                    self.portals.append(new_portal)

            self.objects = []
            self.objects = self.obstacles+self.hazards+self.portals

            #print(str(data) + " loaded.")
        
        #except:
            #print("Could not load level: level data corrupted")

def set_level(level):
    global player
    global obstacles
    global hazards
    global portals
    global objects
    try:
        player = level.player

        obstacles = level.obstacles

        hazards = level.hazards

        portals = level.portals

        objects = level.objects

    except:
        print("Level corrupted")

def save_level():
    #global player
    #global obstacles
    
    data = ""
    data += str(player.x) + " " + str(player.y)
    data += "|"
    strobstacles = []
    for i in range(len(obstacles)):
        strobstacles.append(repr(obstacles[i]))
    data += "/".join(strobstacles)

    data += "|"
    strhazards = []
    for i in range(len(hazards)):
        strhazards.append(repr(hazards[i]))
    data += "/".join(strhazards)

    data += "|"

    strportals = []
    for i in range(len(portals)):
        strportals.append(repr(portals[i]))
    data += "/".join(strportals)
    #print(data)
    return data

menu_button_width = round(screen_width/5)
menu_button_height = round(screen_height/5)
menu_button_x = screen_width/2-menu_button_width/2

menu_buttons = []

menu = True

DELETE = 0
BLOCK = 1
SPIKE = 2
YELLOW_PORTAL = 3
BLUE_PORTAL = 4
MINI_PORTAL = 5
NORMAL_PORTAL = 6
SLAB = 7
MINI_BLOCK = 8
END_PORTAL = 9
JUMP_PAD = 10
SELECT = 11

selected = BLOCK

last_delta = time.time()

def set_selected_object(obj):
    global selected
    print(f"called with: {obj}")
    selected = obj

loading_level = False
loading_level = False

def on_slot_clicked(slot):
    global saving_level
    global loading_level
    
    if saving_level:
        save_level_good(f'slot_{slot}')
        saving_level = False
    elif loading_level:
        load_level(f'slot_{slot}')
        loading_level = False


def set_saving_loading(saving, loading):
    global saving_level
    global loading_level
    saving_level = saving
    loading_level = loading

def reload_buttons():
    global players
    global buttons
    
    global save_button
    global load_button
    global reset_button

    global slot_1_button
    global slot_2_button
    global slot_3_button
    global slot_4_button
    global slot_5_button
    global slot_6_button
    global slot_7_button
    global slot_8_button
    global slot_9_button
    global slot_10_button
    global recover_button


    global menu
    global menu_buttons
    global play_button
    global options_button
    global quit_button
    global editor_button

    global autoscroll_start_x
    global autoscroll_end_x
    global real_xscale
    autoscroll_start_x = round(width/3*((screen_width/screen_height)/16*9))
    autoscroll_end_x = round(2*width/3*((screen_width/screen_height)/16*9))
    
    buttons = []
    button_width = round(screen_width/20)
    button_height = round(screen_height/30)
    menu_button_width = button_width*4
    menu_button_height = button_height*4
    menu_button_x = screen_width/2-menu_button_width/2
    menu_button_y_func = lambda height_factor : screen_height/2-menu_button_height * height_factor
    if True:
        menu_buttons = []

        play_button = ui.button(window, menu_button_x, menu_button_y_func(2), menu_button_width, menu_button_height, "PLAY")
        editor_button = ui.button(window, menu_button_x, menu_button_y_func(1), menu_button_width, menu_button_height, "LEVEL EDITOR")
        options_button = ui.button(window, menu_button_x, menu_button_y_func(0), menu_button_width, menu_button_height, "OPTIONS")
        quit_button = ui.button(window, menu_button_x, menu_button_y_func(-1), menu_button_width, menu_button_height, "QUIT")

        menu_buttons.append(play_button)
        menu_buttons.append(options_button)
        menu_buttons.append(editor_button)
        menu_buttons.append(quit_button)
    if True:
        save_button = ui.button(window, screen_width-button_width*2, 0, button_width, button_height, "save", partial(set_saving_loading, True, False))
        load_button = ui.button(window, screen_width-button_width, 0, button_width, button_height, "load", partial(set_saving_loading, False, True))
        reset_button = ui.button(window, screen_width-button_width*2, button_height, button_width, button_height, "reset", partial(set_level, Level("")))
        delete_button = ui.button(window, 0, (button_height+5), button_width, button_height, "delete", partial(set_selected_object, DELETE))
        block_button = ui.button(window, (button_width+5)*0, (button_height+5)*2, button_width, button_height, "block", partial(set_selected_object, BLOCK))
        slab_button = ui.button(window, (button_width+5)*1, (button_height+5)*2, button_width, button_height, "slab", partial(set_selected_object, SLAB))
        mini_block_button = ui.button(window, (button_width+5)*2, (button_height+5)*2, button_width, button_height, "mini block", partial(set_selected_object, MINI_BLOCK))
        spike_button = ui.button(window, (button_width+5)*3, (button_height+5)*2, button_width, button_height, "spike", partial(set_selected_object, SPIKE))
        yellow_portal_button = ui.button(window, 0, (button_height+5)*3, button_width*2, button_height, "upside down portal", partial(set_selected_object, YELLOW_PORTAL))
        blue_portal_button = ui.button(window, (button_width+5)*2, (button_height+5)*3, button_width*2, button_height, "rightside up portal", partial(set_selected_object, BLUE_PORTAL))
        mini_portal_button = ui.button(window, (button_width+5)*0, (button_height+5)*4, button_width, button_height, "Mini portal", partial(set_selected_object, MINI_PORTAL))
        normal_portal_button = ui.button(window, (button_width+5)*1, (button_height+5)*4, button_width, button_height, "Normal portal", partial(set_selected_object, NORMAL_PORTAL))
        end_portal_button = ui.button(window, (button_width+5)*2, (button_height+5)*4, button_width, button_height, "End portal", partial(set_selected_object, END_PORTAL))
        jump_pad_button = ui.button(window, (button_width+5)*3, (button_height+5)*4, button_width, button_height, "Jump pad", partial(set_selected_object, JUMP_PAD))
        select_button = ui.button(window, (button_width+5)*4, (button_height+5)*4, button_width, button_height, "select", partial(set_selected_object, SELECT))

        slots = 16

        for i in range(1,slots+1):
            
            if (i%2==0):
                new_button_x = screen_width-button_width
            else:
                new_button_x = screen_width-button_width*2
            new_button_y = button_height*((i+3)//2)
            new_button = ui.button(window, new_button_x, new_button_y, button_width, button_height, f"Slot {i}", partial(on_slot_clicked, i))
            if editing:
                buttons.append(new_button)

        recover_button = ui.button(window, screen_width-button_width, button_height, button_width, button_height, "Recover")

        if editing:
            buttons.append(save_button)
            buttons.append(load_button)
            buttons.append(reset_button)
            buttons.append(recover_button)
            buttons.append(delete_button)
            buttons.append(select_button)
            buttons.append(block_button)
            buttons.append(mini_block_button)
            buttons.append(spike_button)
            buttons.append(yellow_portal_button)
            buttons.append(blue_portal_button)
            buttons.append(mini_portal_button)
            buttons.append(normal_portal_button)
            buttons.append(end_portal_button)
            buttons.append(slab_button)
            buttons.append(jump_pad_button)
    # Clean this up - repeated code, loading image for each player
    for player in players:
        player.set_sprite(player_default_image)

level_num = 1
player_count = 1
player_random = False

gravity = 1.15
gamespeed = 60/tickrate
ground_height = 0

flat_friction = .2
multiplicative_friction = .05
air_friction_mult = .333

players = []


for i in range(player_count):
    player = Player()
    if (player_random) and i % 2 == 1:
        player.gravity = -player.gravity
    if player_random:
        player.gravity *= random.uniform(0, 2)
        while player.gravity == 0:
            player.gravity *= random.uniform(0, 2)
        
        player.x += i
        player.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        player.width = (random.randint(10, 50))
        player.height = (random.randint(10, 50))
        player.normwidth = player.width
        player.normheight = player.height
        player.miniwidth = player.width/math.sqrt(2)
        player.miniheight = player.height/math.sqrt(2)
        player.jump_height = random.randint(17, 30)
        player.mini_jump_height = player.jump_height/1.2
        player.max_speed_x = random.uniform(5, 20)
        player.max_speed_y = random.uniform(10, 50)
        player.acceleration = random.uniform(.5, 2)

    players.append(player)

player_default_image = pygame.image.load("resources/images/sebocube.png")
hazard_default_image = pygame.image.load("resources/images/Larimore_icespike.png")
obstacle_default_image = pygame.image.load("resources/images/Larimore_block.png")
background_default_image = pygame.image.load("resources/images/GJ_Background.jpg")
menu_background_default_image = pygame.image.load("resources/images/GJ_Menu_Background.png")
portal_default_image = pygame.image.load("resources/images/blue_portal.png")

for player in players:
    player.set_sprite(player_default_image)


objects = []
obstacles = []
hazards = []
portals = []

objects_editing = []

background = Sprite(pygame.transform.smoothscale(background_default_image, (screen_width, screen_height)), 0, 0, 0)

menu_background = Sprite(pygame.transform.smoothscale(menu_background_default_image, (screen_width, screen_height)), 0, 0, 0)


frames = 0
playing = True
last_time = time.time()-100


editing = True

# Clean this up - delete this
def example_func(i):
    print(i)
    

def mouse_over_anything():
    for button in buttons:
        if button.mouse_over():
            return True
    for slider in sliders:
        if slider.mouse_over():
            return True
        if slider.moving:
            return True
    return False

buttons = []

menus = []

ex_menu = ui.menu(window, 50, 90, 100, 100, 3, 5)
for i in range(ex_menu.rows*ex_menu.columns-1):
    ex_menu.add_button(ui.button(window, 0, 0, 0, 0, f"{i}", partial(example_func, i), player_default_image))

#menus.append(ex_menu)

button_width = round(screen_width/20)
button_height    = round(screen_height/30)


reload_buttons()

sliders = []

text_boxes = []

ex_text_box = ui.text_box(window, 600, 100, 100, 100)

#text_boxes.append(ex_text_box)

def get_grid_pos(pos):
    global grid_width
    global grid_height
    x, y = pos
    return x - x%grid_width, y - y%grid_height
    #y = y - y%grid_height
    #return x, y

def get_special_grid_pos(pos, sp_width, sp_height):
    x, y = pos
    return x - x%sp_width, y - y%sp_height
        

def get_mouse_pos():
    global xscale
    global yscale

    x, y = pygame.mouse.get_pos()
    return x/xscale, y/yscale

def get_objs_touching(objs, pos, amount):
    touching = []
    x, y = pos
    for obj in objs:
        if x > obj.x and x < obj.x+obj.width:
            if y > obj.y and y < obj.y+obj.height:
                if amount == 1:
                    return obj
                touching.append(obj)
                if amount != -1 and len(touching) >= amount:
                    return touching
    if len(touching) != 0:
        return touching
    return None


def delete_touching(pos):
    obj = get_objs_touching(objects, pos, 1)
    if obj:
        if isinstance(obj, Obstacle):
            obstacles.remove(obj)
            objects.remove(obj)
        elif isinstance(obj, Hazard):
            hazards.remove(obj)
            objects.remove(obj)
        elif isinstance(obj, Portal):
            portals.remove(obj)
            objects.remove(obj)

#clean this up - unused func
def rotate_touching(pos):
    obj = get_objs_touching(obstacles, pos, 1)
    if obj:
        obj.rotation += 90
        obj.rotation %= 360
    obj = get_objs_touching(hazards, pos, 1)
    if obj:
        obj.rotation += 90
        obj.rotation %= 360
    
def make_new_object(id_, pos):
    global objects_editing
    x, y = pos
    x = x+autoscroll_offset_x
    y = y+autoscroll_offset_y
    pos = (x,y)
    if id_ == DELETE:
        # Clean this up - repeated code
        delete_touching(pos)

    # Clean this up - repeated code
    if id_ == SELECT:
        obj = get_objs_touching(objects, pos, 1)
        if obj:
            if obj in objects_editing:
                objects_editing.remove(obj)
            else:
                objects_editing.append(obj)
        else:
            objects_editing = []
        
        #CLEAN UP - you NEED to put every object in one list bro (ok i did but kinda in a bad way so fix that now)
    if id_ == BLOCK:
        x, y = get_grid_pos(pos)
        new_obstacle = Obstacle(x ,y, grid_width, grid_height)
        if obstacle_sprite:
            make_sprite(new_obstacle, obstacle_default_image)
        obstacles.append(new_obstacle)
        objects.append(new_obstacle)

    if id_ == SPIKE:
        x, y = get_grid_pos(pos)
        new_spike = Hazard(x, y, grid_width, grid_height)
        if hazard_sprite:
            make_sprite(new_spike, hazard_default_image)
        hazards.append(new_spike)
        objects.append(new_spike)

    if id_ == YELLOW_PORTAL:
        x, y = get_grid_pos(pos)
        new_portal = Portal(x, y, grid_width/2, grid_height*2, 1)
        make_sprite(new_portal, portal_default_image)
        portals.append(new_portal)
        objects.append(new_portal)

    if id_ == BLUE_PORTAL:
        x, y = get_grid_pos(pos)
        new_portal = Portal(x, y, grid_width/2, grid_height*2, 2)
        make_sprite(new_portal, portal_default_image)
        portals.append(new_portal)
        objects.append(new_portal)

    if id_ == NORMAL_PORTAL:
        x, y = get_grid_pos(pos)
        new_portal = Portal(x, y, grid_width/2, grid_height*2, 3)
        make_sprite(new_portal, portal_default_image)
        portals.append(new_portal)
        objects.append(new_portal)

    if id_ == MINI_PORTAL:
        x, y = get_grid_pos(pos)
        new_portal = Portal(x, y, grid_width/2, grid_height*2, 4)
        make_sprite(new_portal, portal_default_image)
        portals.append(new_portal)
        objects.append(new_portal)

    if id_ == SLAB:
        x, y = get_special_grid_pos(pos, grid_width, grid_height/2)
        new_obstacle = Obstacle(x ,y, grid_width, grid_height/2)
        if obstacle_sprite:
            make_sprite(new_obstacle, obstacle_default_image)
        obstacles.append(new_obstacle)
        objects.append(new_obstacle)

    if id_ == MINI_BLOCK:
        x, y = get_special_grid_pos(pos, grid_width/2, grid_height/2)
        new_obstacle = Obstacle(x ,y, grid_width/2, grid_height/2)
        if obstacle_sprite:
            make_sprite(new_obstacle, obstacle_default_image)
        obstacles.append(new_obstacle)
        objects.append(new_obstacle)

    if id_ == JUMP_PAD:
        x, y = get_special_grid_pos(pos, grid_width, grid_height/2)
        new_portal = Portal(x, y, grid_width, grid_height/2, 5)
        portals.append(new_portal)
        objects.append(new_portal)

    if id_ == END_PORTAL:
        x, y = get_grid_pos(pos)
        new_portal = Portal(x, y, grid_width/2, grid_height*2, 6)
        make_sprite(new_portal, portal_default_image)
        portals.append(new_portal)
        objects.append(new_portal)
        


num_levels = 16
def load_level(level_name):
    # Clean this up - idk its just bad
    if level_num > num_levels:
        #return
        print("Trying to load level not declared")
    #try:
    file_name = f'resources/levels/{level_name}.ini'
    config.read(file_name)
    saved_level_data = config.get((level_name), ('level'))
    level = Level(saved_level_data)
    set_level(level)

    # Clean this up - repeated code
    #reload_all_sprites() (clean up this should be used instead because its what youre doing but causes error because func def later)
    for hazard in hazards:
        make_sprite(hazard, hazard_default_image)
        update_sprite(hazard)

        
    for obstacle in obstacles:
        make_sprite(obstacle, obstacle_default_image)

    for portal in portals:
        make_sprite(portal, portal_default_image)
        
    for player in players:
        player.die()

    #except:
    #    print(f"Failed to load level {level_name}")


# def reload_hazard_sprite(hazard):
#         cube_width, cube_height = round(hazard.width*xscale), round(hazard.height*yscale)
#         cube_image = pygame.transform.scale(hazard_default_image, (cube_width, cube_height))
#         cube_rotation = 0
#         hazard.sprite = Sprite(cube_image, hazard.x*xscale, hazard.y*yscale, hazard.rotation)

def update_sprite(self):
            self.sprite.x = (self.x-autoscroll_offset_x)*xscale
            self.sprite.y = (self.y-autoscroll_offset_y)*yscale
            self.sprite.width = self.width*xscale
            self.sprite.height = self.height*yscale
            self.sprite.rotation = self.rotation

def make_sprite(self, image, centered=False):
    image = pygame.transform.smoothscale(image, (round(self.width*xscale), round(self.height*yscale)))
    self.sprite = Sprite(image, self.x*xscale, self.y*yscale, self.rotation)
    self.sprite.set_centered(centered)

def save_level_good(level_name):
    config = ConfigParser()
    saved_level_data = save_level()
    config[level_name] = {}
    config[level_name]['level'] = saved_level_data
    with open(f'resources/levels/{level_name}'+'.ini', 'w') as configfile:
        config.write(configfile)

def save_all_levels(num):
    for i in range(1, num+1):
        load_level(f'slot_{i}')
        save_level_good(f'slot_{i}')

def main_menu():
    global menu
    global playing
    global editing
    window.fill(BACKGROUND_COLOR)
    menu_background.draw()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            menu = False
            playing = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu = False
                playing = False
                break
            
    for button in menu_buttons:
        button.draw()
        if button.get_clicked():
            # Clean this up - use button onclick()
            if button == play_button:
                editing = False
                playing = True
                menu = False
                reload_buttons()
                
            elif button == options_button:
                pass
        
            elif button == editor_button:
                editing = True
                playing = True
                menu = False
                reload_buttons()

            elif button == quit_button:
                menu = False
                playing = False
                break

    pygame.display.flip()
    clock.tick(fps)
load_level(f'slot_{level_num}')
load_new_level = False

def reload_all_sprites():
    global background
    global menu_background
    for player in players:
        player.set_sprite(player_default_image)

    for hazard in hazards:
        make_sprite(hazard, hazard_default_image)


    for obstacle in obstacles:
        make_sprite(obstacle, obstacle_default_image)

    background = Sprite(pygame.transform.smoothscale(background_default_image, (screen_width, screen_height)), 0, 0, 0)
    menu_background = Sprite(pygame.transform.smoothscale(menu_background_default_image, (screen_width, screen_height)), 0, 0, 0)

while playing:
    if screen_width != pygame.display.get_surface().get_width() or screen_height != pygame.display.get_surface().get_height():
        
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        xscale = screen_width/width
        real_xscale = screen_width/width
        yscale = screen_height/height
        xscale = yscale
        reload_buttons()
        reload_all_sprites()
        
    if menu:
        main_menu()
        continue

    if frames % max(int(fps/2), 1) == 0:
        fps_ = int(1/((time.time()-last_time)/(fps/2))+.5)
        last_time = time.time()
    
    window.fill(BACKGROUND_COLOR)
    background.draw()

    if load_new_level:
        load_level(f'slot_{level_num}')
        load_new_level = False
   
    events = pygame.event.get()
    for event in events:
        #global saving_level
        if event.type == pygame.QUIT:
            playing = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu = True
                #playing = False
                break
           

            elif event.key == pygame.K_RETURN:
                save_all_levels(num_levels)

            if editing:
                # if event.key == pygame.K_s:
                #     saving_level = True
                if event.key == pygame.K_w:
                    for obj in objects_editing:
                        obj.y -= grid_height  

                elif event.key == pygame.K_a:
                    for obj in objects_editing:
                        obj.x -= grid_width   

                elif event.key == pygame.K_s:
                    for obj in objects_editing:
                        obj.y += grid_height

                elif event.key == pygame.K_d:
                    for obj in objects_editing:
                        obj.x += grid_width
            
                elif event.key == pygame.K_l:
                    loading_level = True
                    

                elif event.key == pygame.K_c:
                    player_circle = not player_circle
                    
                # Clean this up - put keys and their actions into lists and get indexof key which corresponds to indexof action
                elif event.key == pygame.K_0:
                    make_new_object(DELETE, get_mouse_pos())

                elif event.key == pygame.K_1:
                    make_new_object(BLOCK, get_mouse_pos())                

                elif event.key == pygame.K_2:
                    make_new_object(SPIKE, get_mouse_pos())

                elif event.key == pygame.K_3:
                    make_new_object(BLUE_PORTAL, get_mouse_pos())

                elif event.key == pygame.K_4:
                    make_new_object(YELLOW_PORTAL, get_mouse_pos())

                elif event.key == pygame.K_5:
                    make_new_object(NORMAL_PORTAL, get_mouse_pos())

                elif event.key == pygame.K_6:
                    make_new_object(MINI_PORTAL, get_mouse_pos())

                elif event.key == pygame.K_7:
                    make_new_object(SLAB, get_mouse_pos())

                elif event.key == pygame.K_8:
                    make_new_object(END_PORTAL, get_mouse_pos())

                elif event.key == pygame.K_9:
                    make_new_object(SELECT, get_mouse_pos())
                    
                elif event.key == pygame.K_r:
                    for obj in objects_editing:
                        obj.rotation += 90
                        obj.rotation %= 360

                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not mouse_over_anything() and editing:
                make_new_object(selected, get_mouse_pos())
                    

                
                
                

    if tickrate < fps:
        if frames%(int(fps/tickrate))==0:
            for object in objects:
                object.tick()
            for player in players:  
                player.tick()
    else:
        for i in range(int(tickrate/fps)):
            for object in objects:
                object.tick()
            for player in players:  
                player.tick()

    for object in objects:
        object.draw()
    for player in players:  
        player.draw()
    #Nvm don't Clean up - don't fix this because you already did lol()())()())()()(the obstacles will always be before the others and will always be selected first, so obstacles must be deleted to select hazards/portals on the same grid space
    #objects = obstacles+hazards+portals

    # Clean this up - put into func
        
    pivot_x = players[0].x+players[0].width/2+players[0].interpolation_offset_x-autoscroll_offset_x

    pivot_y = players[0].y+players[0].height/2+players[0].interpolation_offset_y-autoscroll_offset_y

    if pivot_x > autoscroll_end_x:
        autoscroll_offset_x += (pivot_x-autoscroll_end_x)/autoscroll_smoothness

    if pivot_x < autoscroll_start_x:
        autoscroll_offset_x += (pivot_x-autoscroll_start_x)/autoscroll_smoothness

    if pivot_y > autoscroll_end_y:
        autoscroll_offset_y += (pivot_y-autoscroll_end_y)/autoscroll_smoothness

    if pivot_y < autoscroll_start_y:
        autoscroll_offset_y += (pivot_y-autoscroll_start_y)/autoscroll_smoothness

    for menu_ in menus:
        menu_.tick()

    for box in text_boxes:
        box.events = events
        box.tick()
        
    for button in buttons:
        #global saving_level
        #global loading_level
        button.draw()
        button.get_clicked()
    
    dialogue = dialogue_font.render("FPS: " + str(fps_), True, white)
    dialogue_rect = dialogue.get_rect()
    window.blit(dialogue, dialogue_rect)
   

    if (frames+1) % (fps*30) == 0 and editing:
        saved_level_data = save_level()
        config['autosave'] = {}
        config['autosave']['level'] = saved_level_data
        with open('resources/levels/autosave.ini', 'w') as configfile:
            config.write(configfile)
        print("Auto Saved level")
        print(frames+1)


    pygame.display.flip()
    clock.tick(fps)
    frames += 1
    delta_time = (time.time()-last_delta)
    last_delta = time.time()
saved_level_data = save_level()
config['autosave'] = {}
config['autosave']['level'] = saved_level_data
with open('resources/levels/autosave.ini', 'w') as configfile:
    config.write(configfile)
print("Saved level")
pygame.quit()