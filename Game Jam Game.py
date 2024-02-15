import pygame
from pygame import gfxdraw
from pygame import mixer
from functools import partial
from enum import Enum

pygame.init()

pygame.mixer.init()
import random
import math
import time
import ui
    
from configparser import ConfigParser

config = ConfigParser()
player_sprite = True
obstacle_sprite = True
hazard_sprite = True
portal_sprite = False

screen_width, screen_height = 768, 432

#MAKE "BUMP pads" that PUSH you like terracotta in minecraft (Like sideways jump pad or those thingies in edge)
fps = 60
tickrate = 60
width = 1600
height = 900



grid_width = round(width/32)
grid_height = round(height/18)
xscale = screen_width/width
yscale = screen_height/height
xscale = yscale
real_xscale = screen_width/width

autosave = True

pygame.display.set_caption("Game Jam Game")

font = 'arial'
font_width = int(16)
dialogue_font = pygame.font.SysFont(font, font_width)

class Colors:
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

class ObjectType(Enum):
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

BACKGROUND_COLOR = Colors.bg_blue

show_hitboxes = False

autoscroll = False
autoscroll_start_x = round(width/3)
autoscroll_end_x = round(2*width/3)
autoscroll_start_y = round(height-height/3*2)
autoscroll_end_y = round(height-height/3)
autoscroll_smoothness = fps/15
autoscroll_offset_x = 0
autoscroll_offset_y = 0

world_height_limit = -5000

def example_func(i):
        print(i)

class Sprite:
    def __init__(self, image, x, y, rotation):
        self.x = x
        self.y = y
        self.ogimage = image
        self.rotation = rotation
        self.last_rotation = rotation
        self.target_rotation = rotation
        self.image = pygame.transform.rotate(self.ogimage, self.rotation)
        self.centered = False

    def draw(self, window):
        if self.rotation != self.last_rotation:
            self.image = pygame.transform.rotate(self.ogimage, self.rotation)
            self.last_rotation = self.rotation
        if self.centered:
            window.blit(self.image, (self.x-self.image.get_width()/2, self.y-self.image.get_height()/2))
        else:
            x_offset = (self.image.get_width()-self.ogimage.get_width())/2
            y_offset = (self.image.get_height()-self.ogimage.get_height())/2
            window.blit(self.image, (self.x-x_offset, self.y-y_offset))

    def set_centered(self, centered):
        self.centered = centered



class Drawable:

    def make_sprite(self, image, centered=False):
        image = pygame.transform.smoothscale(image, (round(self.width*xscale), round(self.height*yscale)))
        self.sprite = Sprite(image, self.x*xscale, self.y*yscale, self.rotation)
        self.sprite.set_centered(centered)

    def update_sprite(self):
        self.sprite.x = (self.x-autoscroll_offset_x)*xscale
        self.sprite.y = (self.y-autoscroll_offset_y)*yscale
        self.sprite.width = self.width*xscale
        self.sprite.height = self.height*yscale
        self.sprite.rotation = self.rotation

    def draw(self, window):
        self.update_sprite()
        self.sprite.draw(window)




class Object(Drawable):

    def __init__(self, x, y, width=grid_width, height=grid_height, rotation=0):
        self.id = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.sprite = None


    def is_colliding(self, object):
        if object.x+object.width > self.x and object.x < self.x+self.width:
            if object.y+object.height > self.y and object.y < self.y+self.height:
                return True
        return False
    
    
    def __repr__(self):
        info = [str(self.id), str(self.x), str(self.y), str(self.width), str(self.height), str(self.rotation)]
        return "@".join(info)
    



class Player(Object):

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
        self.color = Colors.green
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
        self.gravity = abs(self.gravity)

        # Clean this up - repeated code and loads every time player dies
        self.make_sprite(player_default_image)

    # def set_sprite(self, image):
    #     #Clean this up - does same thing as make_sprite
    #     sprite_width, sprite_height = round(self.width*xscale), round(self.height*yscale)
    #     sprite_image = pygame.transform.smoothscale(image, (sprite_width, sprite_height))
    #     self.sprite = Sprite(sprite_image, self.x*xscale, self.y*yscale, self.rotation)
    #     self.sprite.set_centered(False)
       
    def draw(self, window):
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
            self.sprite.draw(window)
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
            player_width = self.width
            player_height = self.height
            box_top = obstacle.y
            box_bottom = obstacle.y+obstacle.height
            box_right = obstacle.x+obstacle.width
            box_left = obstacle.x
            player_x_speed = self.xspeed*gamespeed
            player_y_speed = self.yspeed*gamespeed
            player_max_x_speed = self.max_speed_x*gamespeed
            player_max_y_speed = self.max_speed_y*gamespeed
            gravity_sign = (self.gravity/abs(self.gravity))
            #If hitting left side stop
            if gravity_sign == 1:
                on_y = player_bottom >= box_top+player_max_y_speed and player_top < box_bottom


            else:
                on_y = player_top <= box_bottom-player_max_y_speed and player_bottom >= box_bottom
            if player_right > box_left and player_right <= box_left + player_max_x_speed:
                if on_y: # -self.height/4 for leeway so if almost on top of block it gives it to you
                    self.x = obstacle.x-self.width
                    self.xspeed = 0

                    
                    hitting = True

            #if hitting right side stop
            if player_left < box_right and player_left-player_x_speed >= box_right + 0:
                if on_y: #Thought this caused the Catching on right side of column but i dont know
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
        player_max_x_speed = self.max_speed_x*gamespeed
        player_max_y_speed = self.max_speed_y*gamespeed
        gravity_sign = (self.gravity/abs(self.gravity))
        rightside_up = self.gravity >= 0
        on_x = player_right > box_left and player_left < box_right
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
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or (pygame.mouse.get_pressed()[0] and not game.display.is_edit_mode() and not mouse_over_anything())) and self.on_surface():
            self.jump()


    def jump(self):
        jump_sound.play()
        if self.mini:
            self.yspeed = -self.mini_jump_height*(abs(self.gravity)/self.gravity)
        else:
            self.yspeed = -self.jump_height*(abs(self.gravity)/self.gravity)
           
        if self.yspeed < -player.max_speed_y:
            self.yspeed = -player.max_speed_y


    def set_mini(self, mini):
        if mini:
            self.mini = True
            self.width = self.miniwidth
            self.height = self.miniheight
        else:
            self.mini = False
            self.width = self.normwidth
            self.height = self.normheight
        
        self.make_sprite(player_default_image)



class Obstacle(Object):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 1
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.color = Colors.light_gray
        self.outline_color = Colors.gray
        self.rotation = 0
        self.costume = 0

   


    def draw(self, window):
        if obstacle_sprite:
            self.update_sprite()
            self.sprite.draw(window)
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

class Hazard(Object):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 2
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.color = Colors.red
        self.type = 1
        self.rotation = 0


        # f = "@"
        # return str(self.x) + f + str(self.y) + f + str(self.width) + f + str(self.height) + f + str(self.rotation) + f + str(self.type) + f + str(self.color)
    
    # def draw(self, window):
    #     if show_hitboxes:
    #         pygame.gfxdraw.rectangle(window, (round((self.x+self.width/4-autoscroll_offset_x)*xscale), round((self.y+self.height/4-autoscroll_offset_y)*yscale), round(self.width/2*xscale), round(self.height/2*yscale)), Colors.red)

    #     if hazard_sprite:
    #         self.update_sprite()
    #         self.sprite.draw(window)
    #         return
    #     if self.type == 1:
    #         outline = .667
    #         color = (self.color[0]*outline, self.color[1]*outline, self.color[2]*outline)
    #         if self.rotation < 180:
    #             pygame.gfxdraw.filled_trigon(window, round(self.x*xscale), round((self.y+self.height-self.height*(self.rotation/180))*yscale), round((self.x+self.width/2+self.width/2*(self.rotation/180))*xscale), round((self.y+self.height*(self.rotation/180))*yscale), round((self.x+self.width-self.width*(self.rotation/180))*xscale), round((self.y+self.height)*yscale), self.color)
    #         elif self.rotation == 180:
    #             pygame.gfxdraw.filled_trigon(window, round(self.x*xscale), round(self.y*yscale), round((self.x+self.width/2)*xscale), round((self.y+self.height)*yscale), round((self.x+self.width)*xscale), round(self.y*yscale), self.color)
    #         else:
    #             pass
            
    #     if self.type == 2:
    #         self.rect = (self.x*xscale, self.y*yscale, self.width*xscale, self.height*yscale)
    #         pygame.gfxdraw.box(window, self.rect, self.color)

    def tick(self):
        pass
        

class Portal(Object):
    def __init__(self, x, y, width, height, type_, rotation=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mode = type_
        self.rotation = rotation
        self.id = self.mode+2
        self.contacting = False
        self.rotation = 0


    def apply(self, player):
        pass

            
    def tick(self):
        for player in players:
            if self.is_colliding(player):
                self.apply(player)

   

class BluePortal(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 3
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0

    def apply(self, player):
        if player.gravity < 0:
            player.gravity *= -1
            if player.yspeed < -player.max_speed_y/2:
                player.yspeed = -player.max_speed_y/2

class YellowPortal(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 4
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0

    def apply(self, player):
        if player.gravity > 0:
            player.gravity *= -1
            if player.yspeed > player.max_speed_y/2:
                player.yspeed = player.max_speed_y/2

class NormalPortal(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 5
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0

    def apply(self, player):
        player.set_mini(False)

class MiniPortal(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 6
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0
    
    def apply(self, player):
        player.set_mini(True)

class EndLevelPortal(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 7
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0
    
    def apply(self, player):
            global level_num
            global load_new_level
            global portals
            if self in portals:
                level_num += 1
                load_new_level = True
                portals.remove(self)

class BumpPad(Portal):
    def __init__(self, x, y, width, height, rotation=0):
        self.id = 8
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.contacting = False
        self.rotation = 0

    def apply(self, player):
        player.yspeed = -player.max_speed_y*(abs(player.gravity)/player.gravity)

    
class Level():
    def __init__(self):
        self.player = Player()
        
        self.obstacles = []
        self.hazards = []
        self.portals = []


    def load(self, data):
        #try:
            important_list = [Object, Obstacle, Hazard, BluePortal, YellowPortal, NormalPortal, MiniPortal, EndLevelPortal, BumpPad, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal, Portal]

            data = data.split("/")

            self.obstacles = []
            self.hazards = []
            self.portals = []
            
            
            for object in data:
                object_data = object.split("@")
                object_id = int(object_data[0])


                if int(object_id) == 1:
                    self.obstacles.append(Obstacle(float(object_data[1]), float(object_data[2]), float(object_data[3]), float(object_data[4]), float(object_data[5])))
                elif int(object_id) == 2:
                    self.hazards.append(Hazard(float(object_data[1]), float(object_data[2]), float(object_data[3]), float(object_data[4]), float(object_data[5])))
                else:
                    portal_type = important_list[object_id]
                    if portal_type != Portal:
                        new_portal = portal_type(float(object_data[1]), float(object_data[2]), float(object_data[3]), float(object_data[4]), float(object_data[5]))
                    else:
                        new_portal = Portal(float(object_data[1]), float(object_data[2]), float(object_data[3]), float(object_data[4]), int(object_data[0])-2, float(object_data[5]))
                    
                    self.portals.append(new_portal)

def set_level(level):
    global player
    global obstacles
    global hazards
    global portals
    try:
        player = level.player

        obstacles = level.obstacles

        hazards = level.hazards

        portals = level.portals

    except:
        print("Level corrupted")

def save_level():

    object_data = []
    for object in all_objects():
        object_data.append(repr(object))
    return "/".join(object_data)

menu_button_width = round(screen_width/5)
menu_button_height = round(screen_height/5)
menu_button_x = screen_width/2-menu_button_width/2


selected = ObjectType.BLOCK

last_delta = time.time()

def set_selected_object(obj):
    global selected
    print(f"called with: {obj}")
    selected = obj

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

level_num = 1
player_count = 1
#player_random = False

gravity = 1.15
gamespeed = 60/tickrate
ground_height = 0

flat_friction = .2
multiplicative_friction = .05
air_friction_mult = .333

players = []


for i in range(player_count):
    player = Player()

    players.append(player)

player_default_image = pygame.image.load("resources/images/sebocube.png")
hazard_default_image = pygame.image.load("resources/images/Larimore_icespike.png")
obstacle_default_image = pygame.image.load("resources/images/Larimore_block.png")
background_default_image = pygame.image.load("resources/images/GJ_Background.jpg")
menu_background_default_image = pygame.image.load("resources/images/GJ_Menu_Background.png")
ground_default_image = pygame.image.load("resources/images/snowground.png")
ceiling_default_image = pygame.image.load("resources/images/tiles.png")
portal_default_image = pygame.image.load("resources/images/blue_portal.png")
yellow_portal_default_image = pygame.image.load("resources/images/yellow_portal.png")


game_default_music = pygame.mixer.Sound("resources/sounds/ez.mp3")
jump_sound = pygame.mixer.Sound("resources/sounds/smb_jump1.wav")

for player in players:
    player.make_sprite(player_default_image)


obstacles = []
hazards = []
portals = []

def all_objects():
    for o in obstacles:
        yield o
    for h in hazards:
        yield h
    for p in portals:
        yield p

objects_editing = []


frames = 0
last_time = time.time()-100

    

def mouse_over_anything():
    for button in game.display.buttons:
        if button.mouse_over():
            return True
    for slider in sliders:
        if slider.mouse_over():
            return True
        if slider.moving:
            return True
    return False

#buttons = []


sliders = []

text_boxes = []


def get_grid_pos(pos, g_width=grid_width, g_height=grid_height):
    x, y = pos
    return x - x%g_width, y - y%g_height


def get_mouse_pos():

    x, y = pygame.mouse.get_pos()
    return (x/xscale)+autoscroll_offset_x, (y/yscale)+autoscroll_offset_y

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
    obj = get_objs_touching(all_objects(), pos, 1)
    if obj:
        if isinstance(obj, Obstacle):
            obstacles.remove(obj)
        if isinstance(obj, Portal):
            portals.remove(obj)
        if isinstance(obj, Hazard):
            hazards.remove(obj)

    
def make_new_object(id_, pos):
    global objects_editing
    x, y = get_grid_pos(pos)
    if id_ == ObjectType.DELETE:
        # Clean this up - repeated code
        delete_touching(pos)

    # Clean this up - repeated code
    if id_ == ObjectType.SELECT:
        obj = get_objs_touching(all_objects(), pos, 1)
        if obj:
            if obj in objects_editing:
                objects_editing.remove(obj)
            else:
                objects_editing.append(obj)
        else:
            objects_editing = []
        
        #CLEAN UP - you NEED to put every object in one list bro (ok i did but kinda in a bad way so fix that now)
    if id_ == ObjectType.BLOCK:
        new_obstacle = Obstacle(x ,y, grid_width, grid_height)
        if obstacle_sprite:
            new_obstacle.make_sprite(obstacle_default_image)
        obstacles.append(new_obstacle)

    if id_ == ObjectType.SPIKE:
        new_spike = Hazard(x, y, grid_width, grid_height)
        if hazard_sprite:
            new_spike.make_sprite(hazard_default_image)
        hazards.append(new_spike)

    if id_ == ObjectType.YELLOW_PORTAL:
        new_portal = YellowPortal(x, y, grid_width/2, grid_height*2)
        new_portal.make_sprite(yellow_portal_default_image)
        portals.append(new_portal)

    if id_ == ObjectType.BLUE_PORTAL:
        new_portal = BluePortal(x, y, grid_width/2, grid_height*2)
        new_portal.make_sprite(portal_default_image)
        portals.append(new_portal)

    if id_ == ObjectType.NORMAL_PORTAL:
        new_portal = NormalPortal(x, y, grid_width/2, grid_height*2)
        new_portal.make_sprite(portal_default_image)
        portals.append(new_portal)

    if id_ == ObjectType.MINI_PORTAL:
        new_portal = MiniPortal(x, y, grid_width/2, grid_height*2)
        new_portal.make_sprite(portal_default_image)
        portals.append(new_portal)

    if id_ == ObjectType.SLAB:
        x, y = get_grid_pos(pos, grid_width, grid_height/2)
        new_obstacle = Obstacle(x ,y, grid_width, grid_height/2)
        if obstacle_sprite:
            new_obstacle.make_sprite(obstacle_default_image)
        obstacles.append(new_obstacle)

    if id_ == ObjectType.MINI_BLOCK:
        x, y = get_grid_pos(pos, grid_width/2, grid_height/2)
        new_obstacle = Obstacle(x ,y, grid_width/2, grid_height/2)
        if obstacle_sprite:
            new_obstacle.make_sprite(obstacle_default_image)
        obstacles.append(new_obstacle)

    if id_ == ObjectType.JUMP_PAD:
        new_portal = BumpPad(x, y, grid_width, grid_height/2)
        portals.append(new_portal)

    if id_ == ObjectType.END_PORTAL:
        new_portal = EndLevelPortal(x, y, grid_width/2, grid_height*2, 6)
        new_portal.make_sprite(portal_default_image)
        portals.append(new_portal)
        


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
    level = Level()
    level.load(saved_level_data)
    set_level(level)


    important_list2 = [obstacle_default_image, obstacle_default_image, hazard_default_image, portal_default_image, yellow_portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image]

    for object in all_objects():
        object.make_sprite(important_list2[object.id])
        
    for player in players:
        player.die()

    #except:
    #    print(f"Failed to load level {level_name}")





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

load_level(f'slot_{level_num}')
load_new_level = False









class Display:
    def __init__(self):
        self.screen_width, self.screen_height = 768, 432
        self.window = pygame.display.set_mode([self.screen_width, self.screen_height], pygame.RESIZABLE)
        self.menus = []
        self.buttons = []
        self.menu_buttons = []
        self.edit_mode = False
        self.reload_buttons()
        self.background = Sprite(pygame.transform.smoothscale(background_default_image, (self.screen_width, self.screen_height)), 0, 0, 0)
        self.menu_background = Sprite(pygame.transform.smoothscale(menu_background_default_image, (self.screen_width, self.screen_height)), 0, 0, 0)
        self.ground = Sprite(pygame.transform.scale(ground_default_image, (self.screen_width*2, self.screen_width/2)), 0, 0, 0)
        self.ceiling = Sprite(pygame.transform.scale(ceiling_default_image, (self.screen_width*2, self.screen_width/2)), 0, 0, 0)

    def set_edit_mode(self):
        self.edit_mode = True
    
    def set_play_mode(self):
        self.edit_mode = False
    
    def is_edit_mode(self):
        return self.edit_mode

    def check_window_resize(self):
        global xscale, yscale, real_xscale
            
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()
        xscale = self.screen_width/width
        real_xscale = self.screen_width/width
        yscale = self.screen_height/height
        xscale = yscale
        self.reload_buttons()
        self.reload_all_sprites()

    def reload_buttons(self):
        global players
        
        global save_button
        global load_button
        global reset_button

        global recover_button

        global play_button
        global options_button
        global quit_button
        global editor_button

        global autoscroll_start_x
        global autoscroll_end_x
        global real_xscale
        autoscroll_start_x = round(width/3*((self.screen_width/self.screen_height)/16*9))
        autoscroll_end_x = round(2*width/3*((self.screen_width/self.screen_height)/16*9))
        
        self.buttons = []
        button_width = round(self.screen_width/20)
        button_height = round(self.screen_height/30)
        menu_button_width = button_width*4
        menu_button_height = button_height*4
        menu_button_x = self.screen_width/2-menu_button_width/2
        menu_button_y_func = lambda height_factor : self.screen_height/2-menu_button_height * height_factor
        if True:
            self.menu_buttons = []


            self.play_button = ui.button(menu_button_x, menu_button_y_func(2), menu_button_width, menu_button_height, "PLAY")
            self.editor_button = ui.button(menu_button_x, menu_button_y_func(1), menu_button_width, menu_button_height, "LEVEL EDITOR")
            self.options_button = ui.button(menu_button_x, menu_button_y_func(0), menu_button_width, menu_button_height, "OPTIONS")
            self.quit_button = ui.button(menu_button_x, menu_button_y_func(-1), menu_button_width, menu_button_height, "QUIT")

            self.menu_buttons.append(self.play_button)
            self.menu_buttons.append(self.options_button)
            self.menu_buttons.append(self.editor_button)
            self.menu_buttons.append(self.quit_button)
        if True:
            self.save_button = ui.button(self.screen_width-button_width*2, 0, button_width, button_height, "save", partial(set_saving_loading, True, False))
            self.load_button = ui.button(self.screen_width-button_width, 0, button_width, button_height, "load", partial(set_saving_loading, False, True))
            self.reset_button = ui.button(self.screen_width-button_width*2, button_height, button_width, button_height, "reset", partial(set_level, Level()))
            self.delete_button = ui.button(0, (button_height+5), button_width, button_height, "delete", partial(set_selected_object, ObjectType.DELETE))
            self.block_button = ui.button((button_width+5)*0, (button_height+5)*2, button_width, button_height, "block", partial(set_selected_object, ObjectType.BLOCK), obstacle_default_image)
            self.slab_button = ui.button((button_width+5)*1, (button_height+5)*2, button_width, button_height, "slab", partial(set_selected_object, ObjectType.SLAB))
            self.mini_block_button = ui.button((button_width+5)*2, (button_height+5)*2, button_width, button_height, "mini block", partial(set_selected_object, ObjectType.MINI_BLOCK))
            self.spike_button = ui.button((button_width+5)*3, (button_height+5)*2, button_width, button_height, "spike", partial(set_selected_object, ObjectType.SPIKE), hazard_default_image)
            self.yellow_portal_button = ui.button(0, (button_height+5)*3, button_width*2, button_height, "upside down portal", partial(set_selected_object, ObjectType.YELLOW_PORTAL))
            self.blue_portal_button = ui.button((button_width+5)*2, (button_height+5)*3, button_width*2, button_height, "rightside up portal", partial(set_selected_object, ObjectType.BLUE_PORTAL))
            self.mini_portal_button = ui.button((button_width+5)*0, (button_height+5)*4, button_width, button_height, "Mini portal", partial(set_selected_object, ObjectType.MINI_PORTAL))
            self.normal_portal_button = ui.button((button_width+5)*1, (button_height+5)*4, button_width, button_height, "Normal portal", partial(set_selected_object, ObjectType.NORMAL_PORTAL))
            self.end_portal_button = ui.button((button_width+5)*2, (button_height+5)*4, button_width, button_height, "End portal", partial(set_selected_object, ObjectType.END_PORTAL))
            self.jump_pad_button = ui.button((button_width+5)*3, (button_height+5)*4, button_width, button_height, "Jump pad", partial(set_selected_object, ObjectType.JUMP_PAD))
            self.select_button = ui.button((button_width+5)*4, (button_height+5)*4, button_width, button_height, "select", partial(set_selected_object, ObjectType.SELECT))

            slots = 16

            for i in range(1,slots+1):
                if (i%2==0):
                    new_button_x = self.screen_width-button_width
                else:
                    new_button_x = self.screen_width-button_width*2
                new_button_y = button_height*((i+3)//2)
                new_button = ui.button(new_button_x, new_button_y, button_width, button_height, f"Slot {i}", partial(on_slot_clicked, i))
                if self.edit_mode:
                    self.buttons.append(new_button)

            self.recover_button = ui.button(self.screen_width-button_width, button_height, button_width, button_height, "Recover", partial(load_level, 'autosave'))

            if self.edit_mode:
                self.buttons.append(self.save_button)
                self.buttons.append(self.load_button)
                self.buttons.append(self.reset_button)
                self.buttons.append(self.recover_button)
                self.buttons.append(self.delete_button)
                self.buttons.append(self.select_button)
                self.buttons.append(self.block_button)
                self.buttons.append(self.mini_block_button)
                self.buttons.append(self.spike_button)
                self.buttons.append(self.yellow_portal_button)
                self.buttons.append(self.blue_portal_button)
                self.buttons.append(self.mini_portal_button)
                self.buttons.append(self.normal_portal_button)
                self.buttons.append(self.end_portal_button)
                self.buttons.append(self.slab_button)
                self.buttons.append(self.jump_pad_button)

    def reload_all_sprites(self):
        for player in players:
            player.make_sprite(player_default_image)

        important_list2 = [obstacle_default_image, obstacle_default_image, hazard_default_image, portal_default_image, yellow_portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image, portal_default_image]

        for object in all_objects():
            object.make_sprite(important_list2[object.id])
        


        self.background = Sprite(pygame.transform.smoothscale(background_default_image, (self.screen_width, self.screen_height)), 0, 0, 0)
        self.menu_background = Sprite(pygame.transform.smoothscale(menu_background_default_image, (self.screen_width, self.screen_height)), 0, 0, 0)
        self.ground = Sprite(pygame.transform.scale(ground_default_image, (self.screen_width*2, self.screen_height)), 0, 0, 0)
        self.ceiling = Sprite(pygame.transform.scale(ceiling_default_image, (self.screen_width*2, self.screen_height)), 0, 0, 0)
        
class Game:
    def __init__(self):
        self.display = Display()

        self.playing = True
        self.in_menu = True
        self.clock = pygame.time.Clock()
        self.menus = []
        self.level = Level()
        ex_menu = ui.menu(50, 90, 100, 100, 3, 5)
        for i in range(ex_menu.rows*ex_menu.columns):
            ex_menu.add_button(ui.button(0, 0, 0, 0, f"{i}", partial(example_func, i), player_default_image))

        self.menus.append(ex_menu)

    def main_menu(self):
        self.display.window.fill(BACKGROUND_COLOR)
        self.display.menu_background.draw(self.display.window)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.in_menu = False
                self.playing = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = False
                    self.playing = False
                    break
                
            elif event.type == pygame.VIDEORESIZE:
                self.display.check_window_resize()

        for button in self.display.menu_buttons:
            button.draw(self.display.window)
            if button.get_clicked():
                # Clean this up - use button onclick()
                if button == self.display.play_button:
                    self.display.set_play_mode()
                    self.playing = True
                    self.in_menu = False
                    self.display.reload_buttons()
                    
                elif button == self.display.options_button:
                    pass
            
                elif button == self.display.editor_button:
                    self.display.set_edit_mode()
                    self.playing = True
                    self.in_menu = False
                    self.display.reload_buttons()

                elif button == self.display.quit_button:
                    self.in_menu = False
                    self.playing = False
                    break

        pygame.display.flip()
        self.clock.tick(fps)
    
    def handle_events(self, events):
        mouse_pos = get_mouse_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.playing = False
                break

            elif event.type == pygame.VIDEORESIZE:
                self.display.check_window_resize()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    break
            

                elif event.key == pygame.K_RETURN:
                    save_all_levels(num_levels)

                if self.display.is_edit_mode():

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
                

                    elif event.key == pygame.K_0:
                        make_new_object(ObjectType.DELETE, mouse_pos)

                    elif event.key == pygame.K_1:
                        make_new_object(ObjectType.BLOCK, mouse_pos)                

                    elif event.key == pygame.K_2:
                        make_new_object(ObjectType.SPIKE, mouse_pos)

                    elif event.key == pygame.K_3:
                        make_new_object(ObjectType.BLUE_PORTAL, mouse_pos)

                    elif event.key == pygame.K_4:
                        make_new_object(ObjectType.YELLOW_PORTAL, mouse_pos)

                    elif event.key == pygame.K_5:
                        make_new_object(ObjectType.NORMAL_PORTAL, mouse_pos)

                    elif event.key == pygame.K_6:
                        make_new_object(ObjectType.MINI_PORTAL, mouse_pos)

                    elif event.key == pygame.K_7:
                        make_new_object(ObjectType.SLAB, mouse_pos)

                    elif event.key == pygame.K_8:
                        make_new_object(ObjectType.END_PORTAL, mouse_pos)

                    elif event.key == pygame.K_9:
                        make_new_object(ObjectType.SELECT, mouse_pos)
                        
                    elif event.key == pygame.K_r:
                        for obj in objects_editing:
                            obj.rotation += 90
                            obj.rotation %= 360

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.display.is_edit_mode() and not mouse_over_anything():
                    make_new_object(selected, mouse_pos)

    def play(self):
        global xscale, yscale, real_xscale 
        global frames, last_time, load_new_level
        global autoscroll_offset_x, autoscroll_offset_y

        while self.playing:
                
            if self.in_menu:
                self.main_menu()
                continue

            if frames % max(int(fps/2), 1) == 0:
                fps_ = int(1/((time.time()-last_time)/(fps/2))+.5)
                last_time = time.time()
            
            self.display.window.fill(BACKGROUND_COLOR)
            self.display.background.draw(self.display.window)
            self.display.ground.x = -autoscroll_offset_x*yscale
            self.display.ground.y = (self.display.screen_height-autoscroll_offset_y*yscale)
            

            while self.display.ground.x > 0:
                self.display.ground.x -= self.display.ground.image.get_width()/2
            while self.display.ground.x+self.display.ground.image.get_width() < self.display.screen_width:
                self.display.ground.x += self.display.ground.image.get_width()/2
            
            self.display.ceiling.x = -autoscroll_offset_x*yscale

            while self.display.ceiling.x > 0:
                self.display.ceiling.x -= self.display.ceiling.image.get_width()/2
            while self.display.ceiling.x + self.display.ceiling.image.get_width() < self.display.screen_width:
                self.display.ceiling.x += self.display.ceiling.image.get_width()/2


            self.display.ceiling.y = (world_height_limit*yscale-autoscroll_offset_y*yscale-self.display.screen_height)
            

            

            
            self.display.ground.draw(self.display.window)
            self.display.ceiling.draw(self.display.window)




            if load_new_level:
                load_level(f'slot_{level_num}')
                load_new_level = False
        
            events = pygame.event.get()
            self.handle_events(events)
            if tickrate < fps:
                if frames%(int(fps/tickrate))==0:
                    for object in all_objects():
                        object.tick()
                    for player in players:  
                        player.tick()
            else:
                for i in range(int(tickrate/fps)):
                    for object in all_objects():
                        object.tick()
                    for player in players:  
                        player.tick()


            for object in all_objects():
                object.draw(self.display.window)
            for player in players:  
                player.draw(self.display.window)


            # Clean up - Put this into a func
                                
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

            for menu in self.menus:
                menu.tick()
                menu.draw(self.display.window)

            for box in text_boxes:
                box.events = events
                box.tick()
                
            for button in game.display.buttons:
                button.get_clicked()
                button.draw(self.display.window)
            
            dialogue = dialogue_font.render("FPS: " + str(fps_), True, Colors.white)
            dialogue_rect = dialogue.get_rect()
            self.display.window.blit(dialogue, dialogue_rect)
        

            if (frames+1) % (fps*30) == 0 and self.display.is_edit_mode():
                save_level_good('autosave')
                print("Auto Saved level")
                print(frames+1)


            pygame.display.flip()
            self.clock.tick(fps)
            frames += 1
            # delta_time = (time.time()-last_delta)
            # last_delta = time.time()

game = Game()
# game.load_default()
game.play()

save_level_good('autosave')
print("Saved level")
pygame.quit()