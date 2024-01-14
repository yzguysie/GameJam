import pygame
import math
pygame.init()

class button:
    def __init__(self, x, y, width, height, text, onclick=None, image_file=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (64, 64, 64)
        self.border_color = (128, 128, 128)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = (255, 255, 255)
        self.text_size = round(width/len(text)*2.5)
        self.font = pygame.font.SysFont('Cascadia Code', self.text_size)
        self.being_clicked = False
        self.enabled = True
        self.disp_text = self.font.render(self.text, True, self.text_color)
        self.moving = False
        self.fancy = True
        self.onclick = onclick
        self.image_file = image_file
        self.image = None
        if self.image_file:

            self.update_image()

    def update_image(self):
        self.image = pygame.transform.smoothscale(self.image_file, (round(self.width), round(self.height)))
        
    def draw(self, surface):
        if self.enabled:
            if self.image:
                surface.blit(self.image, (self.x, self.y))
                return
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, self.border_color, self.rect, round(min(self.width, self.height)/25))
            surface.blit(self.disp_text, (self.rect[0], self.rect[1]))
            
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[2] and self.mouse_over():
            if self.moving:
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
            else:
                self.moving = True
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
                
        else:
            if self.moving and pygame.mouse.get_pressed()[2]:
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
            else:
                self.moving = False
        self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()

    def get_clicked(self):
        self.update()
        if pygame.mouse.get_pressed()[0] and self.mouse_over() and self.enabled:
            if not self.being_clicked:
                self.being_clicked = True
                self.rect = pygame.Rect(self.x+min(self.width, self.height)/20, self.y+min(self.width, self.height)/20, self.width-min(self.width, self.height)/10, self.height-min(self.width, self.height)/10)
                self.text_size = int(self.width/len(self.text)*1.2)
                self.disp_text = self.font.render(self.text, False, self.text_color)
                return False
        else:
            if self.being_clicked == True:
                self.being_clicked = False
                self.update()
                self.text_size = int(self.width/len(self.text)*1.5)
                self.disp_text = self.font.render(self.text, False, self.text_color)
                is_clicked = self.mouse_over()
                if self.onclick:
                    self.onclick()
                return is_clicked
            
            return False


    def mouse_over(self):
        x, y = pygame.mouse.get_pos()
        if x >= self.x and x <= self.x+self.width and self.enabled:
            return y >= self.y and y <= self.y+self.height
        return False

    def set_theme(self, theme):

        if theme == "blue":
            self.color = (32, 42, 98)
            self.border_color = (48, 64, 164)
            self.text_color = (96, 96, 255)

        if theme == "red":
            self.color = (128, 32, 32)
            self.border_color = (196, 48, 48)
            self.text_color = (255, 64, 64)

class text_box:
    def __init__(self, surface, x, y, width, height):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ''
        self.active_color = (64, 64, 64)
        self.inactive_color = (32, 32, 32)
        self.border_color = (128, 128, 128)
        self.text_color = (192, 192, 192)
        self.color = self.inactive_color
        self.active = False
        self.events = None
        self.text_size = 25
        self.font = pygame.font.SysFont('Cascadia Code', self.text_size)
        self.disp_text = self.font.render(self.text, True, self.text_color)

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.surface, self.color, self.rect)
        pygame.draw.rect(self.surface, self.border_color, self.rect, round(min(self.width, self.height)/25))
        self.surface.blit(self.disp_text, (self.rect[0], self.rect[1]))
        
        
    def tick(self):
        self.draw()
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.active = not self.active
                else:
                    self.active = False
                self.color = self.active_color if self.active else self.inactive_color
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.text = ''
                        self.disp_text = self.font.render(self.text, True, self.text_color)
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.disp_text = self.font.render(self.text, True, self.text_color)
                    else:
                        self.text += event.unicode
                        self.disp_text = self.font.render(self.text, True, self.text_color)
        

class menu:
    def __init__(self, x, y, width, height, columns, rows):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.buttons = []
        self.color = (128, 128, 128)
        self.enabled = True
        
    def add_button(self, button):
        if len(self.buttons) > self.columns*self.rows:
            return
        button.width = self.width/self.columns *.9
        button.height = self.height/self.rows *.9
        button_column = len(self.buttons)%self.columns
        button_row = len(self.buttons)//self.columns
        button.x = self.x + self.width*(button_column/self.columns) + button.width/10
        button.y = self.y + self.height*(button_row/self.rows) + button.height/10
        
        button.rect = pygame.Rect(button.x, button.y, button.width, button.height)
        
        button.text_size = round(button.width/len(button.text)*2.5)
        button.font = pygame.font.SysFont('Cascadia Code', button.text_size)
        button.disp_text = button.font.render(button.text, True, button.text_color)
        button.update_image()
        self.buttons.append(button)

    def draw(self, surface):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, self.rect)
        for button in self.buttons:
            button.draw(surface)

    def tick(self):
        # if self.enabled:
        #     self.draw()
        for button in self.buttons:
            button.get_clicked()
    
class slider:
    def __init__(self, surface, x, y, width, height, minimum, maximum, step_amount, text, slider_pos, color, border_color, text_color, slider_color, slide_color, slide_color_dark, onclick=None):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.minimum = minimum
        self.maximum = maximum
        self.step_amount = step_amount
        self.text = text
        self.slider_pos = self.width*((slider_pos-minimum)/(maximum-minimum))
        self.color = color
        self.border_color = border_color
        self.text_color = text_color
        self.slider_color = slider_color
        self.slide_color = slide_color
        self.slide_color_dark = slide_color_dark
        self.enabled = True
        self.rect = pygame.Rect(x, y, width, height)
        self.being_clicked = False
        self.text_size = int(self.height/3)
        self.font = pygame.font.SysFont('Times New Roman', self.text_size)
        self.text2 = str(self.get_value())
        self.slider_size = min(self.width, self.height)/5
        self.moving = False
        self.disp_text = self.font.render(self.text, False, self.text_color)
        self.disp_text2 = self.font.render(self.text2, False, self.text_color)
        self.fancy = False
        self.shine_color = (255, 255, 255)
        self.slider_outline_color = (32, 32, 32)
        self.onclick = onclick

        
    def draw(self):
        if self.enabled:
            pygame.draw.rect(self.surface, self.color, self.rect)
            pygame.draw.rect(self.surface, self.border_color, self.rect, int(min(self.width, self.height)/25))
            pygame.draw.line(self.surface, self.slide_color, (self.x,self.y+self.height/2), (self.x+self.slider_pos,self.y+self.height/2), width = round(min(self.width, self.height)/10))
            pygame.draw.line(self.surface, self.slide_color_dark, (self.x+self.slider_pos,self.y+self.height/2), (self.x+self.width,self.y+self.height/2), width = round(min(self.width, self.height)/10))
            self.surface.blit(self.disp_text, (self.x, self.y))
            self.surface.blit(self.disp_text2, (self.x, self.y+self.height/3*2))
            steps = int(abs((self.maximum-self.minimum)/self.step_amount))
            if steps < self.width/3:
                for i in range(steps):

                    pygame.draw.line(self.surface, self.slide_color, (self.x+self.width/steps*i, self.y+self.height/2.5), (self.x+self.width/steps*i, self.y+self.height-self.height/2.5))
            if self.fancy:
                pygame.gfxdraw.filled_circle(self.surface, round(self.x+self.slider_pos), round(self.y+self.height/2), round(self.slider_size), self.slider_color)
                pygame.gfxdraw.aacircle(self.surface, round(self.x+self.slider_pos), round(self.y+self.height/2), round(self.slider_size), self.slider_outline_color)
                pygame.draw.circle(self.surface, self.shine_color, (round(self.x+self.slider_pos), round(self.y+self.height/2)), round(self.slider_size*0.8), round(self.slider_size/5), draw_top_right=True)

            else:
                pygame.draw.circle(self.surface, self.slider_color, (self.x+self.slider_pos, self.y+self.height/2), self.slider_size)
            

    def mouse_over(self):
        x, y = pygame.mouse.get_pos()
        if x >= self.x and x <= self.x+self.width and self.enabled:
            return y >= self.y and y <= self.y+self.height
        return False

    def mouse_on_slide(self):
        x, y = pygame.mouse.get_pos()
        if x >= self.x+self.width/10 and x <= self.x+self.width-self.width/10 and self.enabled:
            return y >= self.y and y <= self.y+self.height
        return False

    def get_pos_of_nearest_step(self, steps):
        return self.slider_pos+(self.width/steps/2)-((self.slider_pos+(self.width/steps/2))%(self.width/steps))

    def set_fancy(self, fancy):
        self.text2 = str(self.get_value())
        self.fancy = True
        self.update_fancy()
            
    def update_fancy(self):
        if self.fancy:
            self.disp_text = self.font.render(self.text, True, self.text_color)
            self.disp_text2 = self.font.render(self.text2, True, self.text_color)
        else:
            self.disp_text = self.font.render(self.text, False, self.text_color)
            self.disp_text2 = self.font.render(self.text2, False, self.text_color)

    def set_theme(self, theme):

        if theme == "blue":
            self.slider_color = (32, 42, 98)
            self.slider_outline_color = (48, 64, 164)
            self.color = (32, 42, 98)
            self.border_color = (48, 64, 164)
            self.slide_color = (64, 84, 196)
            self.slide_color_dark = (64, 86, 164)
            self.text_color = (96, 96, 255)

        if theme == "red":
            self.slider_color = (196, 48, 48)
            self.slider_outline_color = (164, 28, 28)
            self.color = (128, 32, 32)
            self.border_color = (196, 48, 48)
            self.slide_color = (225, 64, 64)
            self.slide_color_dark = (196, 64, 64)
            self.shine_color = (255, 225, 225)
            self.text_color = (255, 64, 64)

    def get_clicked(self):
        self.update()
        if pygame.mouse.get_pressed()[0] and self.mouse_over() and self.enabled:
            self.being_clicked = True
            self.slider_pos = pygame.mouse.get_pos()[0]-self.x

            steps = int(abs((self.maximum-self.minimum)/self.step_amount))
            self.slider_pos = self.get_pos_of_nearest_step(steps)
            self.slider_size = min(self.width, self.height)/6
            if self.onclick:
                self.onclick()
            return True
        
        else:

            self.slider_size = min(self.width, self.height)/5
            if self.being_clicked == True:
                self.being_clicked = False
                return self.mouse_over()
            #self.update()
        return False
    
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.text2 != str(self.get_value()):
            self.text2 = str(self.get_value())
            self.disp_text2 = self.font.render(self.text2, False, self.text_color)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[2] and self.mouse_over():
            if self.moving:
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
            else:
                self.moving = True
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
                
        else:
            if self.moving and pygame.mouse.get_pressed()[2]:
                self.x += mouse_x-self.last_mouse_x
                self.y += mouse_y-self.last_mouse_y
            else:
                self.moving = False
        self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
                
            

    def get_value(self):
        val = self.minimum+(self.slider_pos/self.width)*(self.maximum-self.minimum)

        if val == int(val):
            return int(val)
        
        return val

    def set_value(self, value):
        self.slider_pos = self.width*(value-self.minimum)/(self.maximum-self.minimum)
        

    
        
